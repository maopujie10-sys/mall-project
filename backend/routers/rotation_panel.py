"""域名轮值管理 — 跳转检测/权重/报告"""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from auth import verify_token
from state import state
from risk import handle_risk

router = APIRouter(prefix="/rotation", tags=["Rotation"])

DEFAULT_DOMAINS = [
    {"domain": "tiktook.eu.cc", "active": True, "health": "ok", "type": "主域名"},
    {"domain": "tiktokmall.shop", "active": True, "health": "ok", "type": "轮值"},
    {"domain": "tiktokmall.store", "active": True, "health": "ok", "type": "轮值"},
    {"domain": "tiktokmall.online", "active": True, "health": "ok", "type": "轮值"},
    {"domain": "tiktokmall.live", "active": True, "health": "ok", "type": "轮值"},
    {"domain": "tiktokmall.xyz", "active": True, "health": "ok", "type": "轮值"},
    {"domain": "tiktokmall.top", "active": True, "health": "ok", "type": "轮值"},
    {"domain": "img.tiktook.eu.cc", "active": True, "health": "ok", "type": "CDN图片"},
]

def _get_domains():
    if "rotation_domains" not in state._data:
        state._data["rotation_domains"] = DEFAULT_DOMAINS
        state._save()
    return state._data["rotation_domains"]

class AddDomainRequest(BaseModel):
    domain: str
    type: str = "轮值"

class ToggleRequest(BaseModel):
    domain: str
    active: bool

class CheckRequest(BaseModel):
    domain: str

@router.get("/domains")
async def get_domains(_=Depends(verify_token)):
    await handle_risk("L1", "查看轮值域名列表")
    return _get_domains()

@router.post("/domains")
async def add_domain(req: AddDomainRequest, _=Depends(verify_token)):
    domains = _get_domains()
    if any(d["domain"] == req.domain for d in domains):
        raise HTTPException(400, "域名已存在")
    domains.append({"domain": req.domain, "active": True, "health": "ok", "type": req.type})
    state._save()
    return {"domain": req.domain, "added": True}

@router.delete("/domains/{domain}")
async def remove_domain(domain: str, _=Depends(verify_token)):
    domains = _get_domains()
    before = len(domains)
    state._data["rotation_domains"] = [d for d in domains if d["domain"] != domain]
    state._save()
    if len(_get_domains()) == before:
        raise HTTPException(404, "域名不存在")
    return {"domain": domain, "removed": True}

@router.post("/toggle")
async def toggle_domain(req: ToggleRequest, _=Depends(verify_token)):
    await handle_risk("L2", f"域名轮值: {req.domain} {'启用' if req.active else '停用'}")
    for d in _get_domains():
        if d["domain"] == req.domain:
            d["active"] = req.active
            d["health"] = "ok" if req.active else "disabled"
            state._save()
            return {"domain": req.domain, "active": req.active}
    raise HTTPException(status_code=404, detail="域名不存在")

@router.post("/check")
async def check_domain(req: CheckRequest, _=Depends(verify_token)):
    await handle_risk("L1", f"域名检测", req.domain)
    for d in _get_domains():
        if d["domain"] == req.domain:
            d["health"] = "ok"
            state._save()
            return {"domain": req.domain, "health": "ok"}
    raise HTTPException(status_code=404, detail="域名不存在")



class WeightRequest(BaseModel):
    domain: str
    weight: int = 1

class BatchToggleRequest(BaseModel):
    active: bool

@router.get("/report")
async def rotation_report(_=Depends(verify_token)):
    """生成轮值报告"""
    await handle_risk("L1", "生成轮值报告")
    domains = _get_domains()
    active = [d for d in domains if d.get("active")]
    inactive = [d for d in domains if not d.get("active")]
    unhealthy = [d for d in domains if d.get("health") != "ok"]
    return {
        "total": len(domains),
        "active": len(active),
        "inactive": len(inactive),
        "unhealthy": len(unhealthy),
        "health_rate": f"{(len(active)-len(unhealthy))/max(len(active),1)*100:.0f}%",
        "unhealthy_domains": [d["domain"] for d in unhealthy],
    }

@router.post("/weight")
async def set_weight(req: WeightRequest, _=Depends(verify_token)):
    """调整域名权重"""
    await handle_risk("L2", "调整域名权重", f"{req.domain}={req.weight}")
    for d in _get_domains():
        if d["domain"] == req.domain:
            d["weight"] = req.weight
            state._save()
            return {"domain": req.domain, "weight": req.weight}
    raise HTTPException(status_code=404, detail="域名不存在")

@router.post("/check-all")
async def check_all_domains(_=Depends(verify_token)):
    """检测所有域名跳转链路"""
    await handle_risk("L2", "全量检测轮值域名")
    import httpx
    domains = _get_domains()
    results = []
    async with httpx.AsyncClient(timeout=10, follow_redirects=True) as c:
        for d in domains:
            if not d.get("active"):
                continue
            url = f"https://{d['domain']}"
            try:
                r = await c.get(url, headers={"User-Agent": "Mozilla/5.0"})
                chain = [str(r.url)] if r.url else []
                history = [str(h.url) for h in r.history] if r.history else []
                d["health"] = "ok" if r.status_code < 400 else "error"
                results.append({
                    "domain": d["domain"],
                    "status": r.status_code,
                    "redirect_chain": history + chain,
                    "ok": d["health"] == "ok",
                })
            except Exception as e:
                d["health"] = "error"
                results.append({"domain": d["domain"], "status": 0, "error": str(e), "ok": False})
    state._save()
    return {"results": results, "total": len(results), "ok": sum(1 for r in results if r["ok"])}
