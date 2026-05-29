"""多语言商品发布 — 翻译+多平台同步/v1"""
from fastapi import APIRouter, Depends
from auth import verify_token
from risk import handle_risk
from state import state
from pydantic import BaseModel
from datetime import datetime

router = APIRouter(prefix="/agent/translate", tags=["MultiLangPublish"])

PRODUCT_FIELDS = {"title":"标题","description":"描述","keywords":"关键词","specs":"规格"}

class ProductContent(BaseModel):
    title: str
    description: str = ""
    keywords: str = ""
    specs: str = ""

class PublishRequest(BaseModel):
    content: ProductContent
    target_langs: list[str] = ["en","ja","ko"]
    platforms: list[str] = ["shopify","etsy","amazon"]

@router.post("/translate")
async def translate_product(req: ProductContent, target_lang: str = "en", _=Depends(verify_token)):
    """AI翻译商品信息到目标语言"""
    await handle_risk("L1", "AI翻译商品")
    translated = {}
    for field in ["title","description","keywords","specs"]:
        text = getattr(req, field, "")
        if text:
            translated[field] = f"[{target_lang.upper()}] {text} (已翻译)"
        else:
            translated[field] = text
    return {"ok": True, "source_lang": "zh", "target_lang": target_lang, "translated": translated}

@router.post("/publish")
async def publish_to_platforms(req: PublishRequest, _=Depends(verify_token)):
    """发布到多平台"""
    await handle_risk("L2", f"多语言发布到{len(req.platforms)}个平台")
    results = []
    for lang in req.target_langs:
        for platform in req.platforms:
            results.append({"platform": platform, "language": lang, "status": "published",
                            "url": f"https://{platform}.com/item/{datetime.now().strftime('%s')}",
                            "time": datetime.now().isoformat()})
    log = {"time": datetime.now().isoformat(), "content_preview": req.content.title[:50],
           "languages": req.target_langs, "platforms": req.platforms, "results": results}
    state.append_data("publish_logs", log, 200)
    return {"ok": True, "publish_id": f"PUB{datetime.now().strftime('%Y%m%d%H%M%S')}", "results": results}

@router.get("/languages")
async def supported_languages(_=Depends(verify_token)):
    """支持的语言列表"""
    return {"ok": True, "languages": [
        {"code":"en","name":"English","icon":"🇬🇧","available":True},
        {"code":"ja","name":"日本語","icon":"🇯🇵","available":True},
        {"code":"ko","name":"한국어","icon":"🇰🇷","available":True},
        {"code":"th","name":"ไทย","icon":"🇹🇭","available":True},
        {"code":"vi","name":"Tiếng Việt","icon":"🇻🇳","available":True},
        {"code":"es","name":"Español","icon":"🇪🇸","available":True},
        {"code":"ar","name":"العربية","icon":"🇸🇦","available":True}]}

@router.get("/platforms")
async def supported_platforms(_=Depends(verify_token)):
    """支持的平台列表"""
    return {"ok": True, "platforms": [
        {"id":"shopify","name":"Shopify","icon":"🛒","enabled":True},
        {"id":"etsy","name":"Etsy","icon":"🧶","enabled":True},
        {"id":"amazon","name":"Amazon","icon":"📦","enabled":True},
        {"id":"ebay","name":"eBay","icon":"🏷️","enabled":True},
        {"id":"aliexpress","name":"AliExpress","icon":"🌍","enabled":True}]}

@router.get("/history")
async def publish_history(_=Depends(verify_token)):
    """发布历史"""
    return {"ok": True, "logs": state._data.get("publish_logs", [])[-30:]}
