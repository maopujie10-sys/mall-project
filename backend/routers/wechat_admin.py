"""  ///"""
import os, json, base64, hashlib, time
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from pydantic import BaseModel
from auth import verify_token
from state import state
from tools.logger import get_logger

logger = get_logger("wechat_admin")
router = APIRouter(prefix="/agent/wechat", tags=["WeChatAdmin"])

WECHAT_CONFIG_FILE = os.path.join(os.path.dirname(__file__), "..", "data", "wechat_config.json")
LICENSE_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "licenses")

# =====  =====
class WechatConfigRequest(BaseModel):
    app_id: str = ''
    app_secret: str = ''
    token: str = ''
    aes_key: str = ''
    account_name: str = ''
    account_type: str = "service"  # service/subscription
    auto_reply_enabled: bool = True
    welcome_message: str = ''
    default_reply: str = ""

class MenuItem(BaseModel):
    name: str
    type: str = "click"  # click/view/miniprogram
    key: str = ''
    url: str = ''
    sub_buttons: list = []

class MenuRequest(BaseModel):
    buttons: list = []

class LicenseInfo(BaseModel):
    company_name: str = ''
    license_number: str = ''
    legal_person: str = ''
    address: str = ''

# =====  =====
def _load_config() -> dict:
    try:
        if os.path.exists(WECHAT_CONFIG_FILE):
            with open(WECHAT_CONFIG_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
    except:
        pass
    return {}

def _save_config(config: dict):
    os.makedirs(os.path.dirname(WECHAT_CONFIG_FILE), exist_ok=True)
    with open(WECHAT_CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(config, f, ensure_ascii=False, indent=2)

# =====  =====
@router.get("/config")
async def get_wechat_config(_=Depends(verify_token)):
    config = _load_config()
    
    safe = {k: v for k, v in config.items() if k not in ("app_secret", "aes_key")}
    safe["app_secret"] = config.get("app_secret", '')[:4] + "****" if config.get("app_secret") else ''
    safe["aes_key"] = config.get("aes_key", '')[:4] + "****" if config.get("aes_key") else ''
    safe["has_license"] = os.path.exists(os.path.join(LICENSE_DIR, "business_license.jpg"))
    return {"ok": True, "config": safe}

# =====  =====
@router.post("/config")
async def save_wechat_config(req: WechatConfigRequest, _=Depends(verify_token)):
    config = _load_config()
    if req.app_id:
        config["app_id"] = req.app_id
    if req.app_secret and req.app_secret != "****":
        config["app_secret"] = req.app_secret
    if req.token:
        config["token"] = req.token
    if req.aes_key and req.aes_key != "****":
        config["aes_key"] = req.aes_key
    config["account_name"] = req.account_name or config.get("account_name", '')
    config["account_type"] = req.account_type
    config["auto_reply_enabled"] = req.auto_reply_enabled
    config["welcome_message"] = req.welcome_message
    config["default_reply"] = req.default_reply
    config["updated_at"] = datetime.now().isoformat()
    _save_config(config)
    logger.info('')
    return {"ok": True, "message": ''}

# =====  =====
@router.post("/license/upload")
async def upload_license(
    file: UploadFile = File(...),
    company_name: str = '',
    license_number: str = '',
    legal_person: str = '',
    address: str = '',
    _=Depends(verify_token)
):
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(400, '')
    
    os.makedirs(LICENSE_DIR, exist_ok=True)
    
    
    content = await file.read()
    ext = file.filename.split(".")[-1] if file.filename else "jpg"
    filepath = os.path.join(LICENSE_DIR, f"business_license.{ext}")
    with open(filepath, "wb") as f:
        f.write(content)
    
    
    info = {
        "company_name": company_name,
        "license_number": license_number,
        "legal_person": legal_person,
        "address": address,
        "filename": file.filename,
        "uploaded_at": datetime.now().isoformat(),
        "verified": False
    }
    with open(os.path.join(LICENSE_DIR, "license_info.json"), "w", encoding="utf-8") as f:
        json.dump(info, f, ensure_ascii=False, indent=2)
    
    logger.info(f": {company_name}")
    return {"ok": True, "message": '', "info": info}

# =====  =====
@router.get("/license")
async def get_license(_=Depends(verify_token)):
    info_path = os.path.join(LICENSE_DIR, "license_info.json")
    if not os.path.exists(info_path):
        return {"ok": True, "has_license": False}
    
    with open(info_path, "r", encoding="utf-8") as f:
        info = json.load(f)
    
    
    img_file = None
    for ext in ("jpg", "jpeg", "png"):
        path = os.path.join(LICENSE_DIR, f"business_license.{ext}")
        if os.path.exists(path):
            img_file = path
            break
    
    return {
        "ok": True,
        "has_license": True,
        "info": info,
        "has_image": img_file is not None
    }

# =====  =====
@router.get("/license/image")
async def get_license_image():
    for ext in ("jpg", "jpeg", "png"):
        path = os.path.join(LICENSE_DIR, f"business_license.{ext}")
        if os.path.exists(path):
            from fastapi.responses import FileResponse
            return FileResponse(path, media_type=f"image/{ext}")
    raise HTTPException(404, '')

# =====  =====
@router.post("/menu")
async def save_menu(req: MenuRequest, _=Depends(verify_token)):
    config = _load_config()
    config["custom_menu"] = [b.dict() for b in req.buttons]
    config["menu_updated_at"] = datetime.now().isoformat()
    _save_config(config)
    
    
    push_result = await _push_menu_to_wechat(config, req.buttons)
    
    return {"ok": True, "message": '', "push_result": push_result}

# =====  =====
@router.get("/menu")
async def get_menu(_=Depends(verify_token)):
    config = _load_config()
    return {"ok": True, "menu": config.get("custom_menu", [])}

# =====  =====
async def _push_menu_to_wechat(config: dict, buttons: list) -> dict:
    ''''''
    app_id = config.get("app_id")
    app_secret = config.get("app_secret")
    if not app_id or not app_secret:
        return {"ok": False, "error": "AppIDAppSecret"}
    
    try:
        import httpx
        # access_token
        async with httpx.AsyncClient(timeout=15) as client:
            token_resp = await client.get(
                "https://api.weixin.qq.com/cgi-bin/token",
                params={"grant_type": "client_credential", "appid": app_id, "secret": app_secret}
            )
            token_data = token_resp.json()
            access_token = token_data.get("access_token")
            if not access_token:
                return {"ok": False, "error": token_data.get("errmsg", "access_token")}
            
            
            menu_data = {"button": _build_menu_structure(buttons)}
            menu_resp = await client.post(
                f"https://api.weixin.qq.com/cgi-bin/menu/create",
                params={"access_token": access_token},
                json=menu_data
            )
            result = menu_resp.json()
            if result.get("errcode") == 0:
                return {"ok": True, "message": ''}
            else:
                return {"ok": False, "error": result.get("errmsg", '')}
    except Exception as e:
        return {"ok": False, "error": str(e)[:200]}

def _build_menu_structure(buttons: list) -> list:
    ''''''
    result = []
    for btn in buttons[:3]:  # 3
        item = {"name": btn.get("name", '')[:8]}  # 8
        if btn.get("sub_buttons"):
            item["sub_button"] = [
                {"type": s.get("type", "click"),
                 "name": s.get("name", '')[:16],
                 "key" if s.get("type") != "view" else "url": s.get("key", '') if s.get("type") != "view" else s.get("url", '')}
                for s in btn["sub_buttons"][:5]  # 5
            ]
        else:
            item["type"] = btn.get("type", "click")
            if btn.get("type") == "view":
                item["url"] = btn.get("url", '')
            else:
                item["key"] = btn.get("key", '')
        result.append(item)
    return result

# =====  =====
@router.get("/stats")
async def wechat_stats(_=Depends(verify_token)):
    stats = state._data.get("wechat_stats", {
        "total_messages": 0,
        "total_users": 0,
        "today_messages": 0,
        "today_users": 0,
        "last_message_at": None
    })
    return {"ok": True, "stats": stats}

# =====  =====
@router.post("/test-connection")
async def test_wechat_connection(_=Depends(verify_token)):
    config = _load_config()
    app_id = config.get("app_id")
    app_secret = config.get("app_secret")
    
    if not app_id or not app_secret:
        return {"ok": False, "error": "AppIDAppSecret"}
    
    try:
        import httpx
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.get(
                "https://api.weixin.qq.com/cgi-bin/token",
                params={"grant_type": "client_credential", "appid": app_id, "secret": app_secret}
            )
            data = resp.json()
            if data.get("access_token"):
                return {"ok": True, "message": '', "expires_in": data.get("expires_in")}
            else:
                return {"ok": False, "error": data.get("errmsg", '')}
    except Exception as e:
        return {"ok": False, "error": str(e)[:200]}
# =====  =====
class WecomConfigRequest(BaseModel):
    corp_id: str = ''
    agent_id: str = ''
    secret: str = ''
    token: str = ''
    aes_key: str = ''

@router.get("/wecom/config")
async def get_wecom_config(_=Depends(verify_token)):
    config = _load_config()
    wecom = config.get("wecom", {})
    safe = {k: v for k, v in wecom.items() if k not in ("secret", "aes_key")}
    safe["secret"] = wecom.get("secret", '')[:4] + "****" if wecom.get("secret") else ''
    safe["aes_key"] = wecom.get("aes_key", '')[:4] + "****" if wecom.get("aes_key") else ''
    return {"ok": True, "config": safe}

@router.post("/wecom/config")
async def save_wecom_config(req: WecomConfigRequest, _=Depends(verify_token)):
    config = _load_config()
    wecom = config.get("wecom", {})
    if req.corp_id: wecom["corp_id"] = req.corp_id
    if req.secret and req.secret != "****": wecom["secret"] = req.secret
    if req.agent_id: wecom["agent_id"] = req.agent_id
    if req.token: wecom["token"] = req.token
    if req.aes_key and req.aes_key != "****": wecom["aes_key"] = req.aes_key
    wecom["updated_at"] = datetime.now().isoformat()
    config["wecom"] = wecom
    _save_config(config)
    return {"ok": True, "message": ''}

@router.post("/wecom/test")
async def test_wecom_connection(_=Depends(verify_token)):
    config = _load_config()
    wecom = config.get("wecom", {})
    corp_id = wecom.get("corp_id")
    secret = wecom.get("secret")
    if not corp_id or not secret:
        return {"ok": False, "error": "IDSecret"}
    try:
        import httpx
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.get(
                "https://qyapi.weixin.qq.com/cgi-bin/gettoken",
                params={"corpid": corp_id, "corpsecret": secret}
            )
            data = resp.json()
            if data.get("access_token"):
                return {"ok": True, "message": '', "expires_in": data.get("expires_in")}
            return {"ok": False, "error": data.get("errmsg", '')}
    except Exception as e:
        return {"ok": False, "error": str(e)[:200]}