"""腾讯云 COS 图片存储工具 -- 上传/下载/删除/签名URL"""
import os
import hashlib
import httpx
from datetime import datetime
from urllib.parse import quote
from config import COS_SECRET_ID, COS_SECRET_KEY, COS_BUCKET, COS_REGION, COS_DOMAIN

# COS endpoint
COS_ENDPOINT = f"{COS_BUCKET}.cos.{COS_REGION}.myqcloud.com"
COS_BASE_URL = f"https://{COS_ENDPOINT}"

def _cos_sign(method: str, path: str, headers: dict, expire: int = 3600) -> str:
    """生成 COS 签名 (自实现 HMAC-SHA1)"""
    import hmac, time
    key_time = f"{int(time.time())};{int(time.time())+expire}"
    sign_key = hmac.new(COS_SECRET_KEY.encode(), key_time.encode(), hashlib.sha1).hexdigest()
    http_string = f"{method.lower()}\n{path}\n\nhost={COS_ENDPOINT}\n"
    string_to_sign = f"sha1\n{key_time}\n{hashlib.sha1(http_string.encode()).hexdigest()}\n"
    signature = hmac.new(sign_key.encode(), string_to_sign.encode(), hashlib.sha1).hexdigest()
    auth = (
        f"q-sign-algorithm=sha1"
        f"&q-ak={COS_SECRET_ID}"
        f"&q-sign-time={key_time}"
        f"&q-key-time={key_time}"
        f"&q-header-list=host"
        f"&q-url-param-list="
        f"&q-signature={signature}"
    )
    return auth

async def upload_image(file_path: str, cos_key: str = None, content_type: str = "image/jpeg") -> dict:
    """上传图片到 COS,返回 {"ok": True, "url": "https://..."} 或 {"ok": False, "error": "..."}"""
    if not COS_SECRET_ID or not COS_SECRET_KEY:
        return {"ok": False, "error": "COS 密钥未配置"}

    if not cos_key:
        ext = os.path.splitext(file_path)[1] or ".jpg"
        name = hashlib.md5(open(file_path, "rb").read()).hexdigest()[:12]
        cos_key = f"products/{datetime.now().strftime('%Y%m')}/{name}{ext}"

    url = f"{COS_BASE_URL}/{quote(cos_key, safe='/')}"
    headers = {
        "Host": COS_ENDPOINT,
        "Content-Type": content_type,
    }

    try:
        with open(file_path, "rb") as f:
            data = f.read()
        headers["Content-Length"] = str(len(data))
        headers["Authorization"] = _cos_sign("put", f"/{cos_key}", headers)

        async with httpx.AsyncClient(timeout=60) as cli:
            r = await cli.put(url, content=data, headers=headers)
            if r.status_code in (200, 204):
                return {"ok": True, "url": f"{COS_DOMAIN}/{cos_key}", "key": cos_key, "size": len(data)}
            else:
                return {"ok": False, "error": f"COS 返回 {r.status_code}: {r.text[:200]}"}
    except Exception as e:
        return {"ok": False, "error": str(e)}

async def upload_bytes(data: bytes, cos_key: str, content_type: str = "image/jpeg") -> dict:
    """上传字节数据到 COS"""
    if not COS_SECRET_ID or not COS_SECRET_KEY:
        return {"ok": False, "error": "COS 密钥未配置"}

    url = f"{COS_BASE_URL}/{quote(cos_key, safe='/')}"
    headers = {
        "Host": COS_ENDPOINT,
        "Content-Type": content_type,
        "Content-Length": str(len(data)),
    }
    headers["Authorization"] = _cos_sign("put", f"/{cos_key}", headers)

    try:
        async with httpx.AsyncClient(timeout=60) as cli:
            r = await cli.put(url, content=data, headers=headers)
            if r.status_code in (200, 204):
                return {"ok": True, "url": f"{COS_DOMAIN}/{cos_key}", "key": cos_key, "size": len(data)}
            return {"ok": False, "error": f"COS 返回 {r.status_code}: {r.text[:200]}"}
    except Exception as e:
        return {"ok": False, "error": str(e)}

async def delete_image(cos_key: str) -> dict:
    """删除 COS 中的图片"""
    url = f"{COS_BASE_URL}/{quote(cos_key, safe='/')}"
    headers = {"Host": COS_ENDPOINT}
    headers["Authorization"] = _cos_sign("delete", f"/{cos_key}", headers)
    try:
        async with httpx.AsyncClient(timeout=15) as cli:
            r = await cli.delete(url, headers=headers)
            return {"ok": r.status_code in (200, 204)}
    except Exception as e:
        return {"ok": False, "error": str(e)}

def get_signed_url(cos_key: str, expire: int = 3600) -> str:
    """生成临时签名URL (带有效期)"""
    headers = {"Host": COS_ENDPOINT}
    auth = _cos_sign("get", f"/{cos_key}", headers, expire)
    params = auth.replace("&", "&")
    return f"{COS_DOMAIN}/{cos_key}?{params}"

async def get_cos_status() -> dict:
    """获取COS连接状态"""
    if not COS_SECRET_ID or not COS_SECRET_KEY:
        return {"status": "未配置", "bucket": COS_BUCKET or "N/A", "region": COS_REGION or "N/A", "uploaded": 0, "usage": "0 MB"}
    try:
        async with httpx.AsyncClient(timeout=10) as cli:
            r = await cli.head(f"{COS_BASE_URL}/", headers={"Host": COS_ENDPOINT, "Authorization": _cos_sign("head", "/", {"Host": COS_ENDPOINT})})
            return {"status": "已连接" if r.status_code < 500 else "异常", "bucket": COS_BUCKET, "region": COS_REGION, "uploaded": 0, "usage": "0 MB"}
    except:
        return {"status": "未连接", "bucket": COS_BUCKET or "N/A", "region": COS_REGION or "N/A", "uploaded": 0, "usage": "0 MB"}