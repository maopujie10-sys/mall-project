"""网站访问检测 — 域名解析/HTTPS/页面访问/SSL证书"""
import httpx
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from auth import verify_token
from executor import execute
from risk import handle_risk

router = APIRouter(prefix="/site", tags=["Site"])

class CheckRequest(BaseModel):
    url: str

class DomainRequest(BaseModel):
    domain: str

@router.post("/check")
async def site_check(req: CheckRequest, _=Depends(verify_token)):
    await handle_risk("L1", "网站访问检测", req.url)
    url = req.url if req.url.startswith("http") else f"https://{req.url}"
    result = {"url": url, "accessible": False, "status_code": 0, "latency_ms": 0, "error": ""}
    try:
        async with httpx.AsyncClient(timeout=10, follow_redirects=True) as c:
            start = __import__("time").time()
            r = await c.get(url, headers={"User-Agent": "Mozilla/5.0"})
            latency = int((__import__("time").time() - start) * 1000)
            result.update({
                "accessible": r.status_code < 500,
                "status_code": r.status_code,
                "latency_ms": latency,
            })
    except Exception as e:
        result["error"] = str(e)
    return result

@router.post("/dns")
async def dns_check(req: DomainRequest, _=Depends(verify_token)):
    await handle_risk("L1", "DNS检测", req.domain)
    result = await execute(f"dig +short {req.domain}")
    if not result["success"]:
        result = await execute(f"nslookup {req.domain} 2>/dev/null || echo 'nslookup not available'")
    return {"domain": req.domain, "records": result["stdout"][:500]}

@router.post("/ssl")
async def ssl_check(req: DomainRequest, _=Depends(verify_token)):
    await handle_risk("L1", "SSL证书检测", req.domain)
    result = await execute(f"openssl s_client -connect {req.domain}:443 -servername {req.domain} </dev/null 2>/dev/null | openssl x509 -noout -dates -subject 2>/dev/null")
    if not result["success"] or not result["stdout"].strip():
        return {"domain": req.domain, "error": "无法获取SSL证书信息，请确认域名和443端口可访问"}
    lines = [l.strip() for l in result["stdout"].split("\n") if l.strip()]
    info = {}
    for l in lines:
        if "=" in l:
            k, v = l.split("=", 1)
            info[k.strip()] = v.strip()
    return {"domain": req.domain, "cert_info": info}

