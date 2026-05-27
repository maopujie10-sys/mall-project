"""域名轮值管理"""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from main import verify_token
from state import state

router = APIRouter(prefix="/rotation", tags=["Rotation"])

DOMAINS = [
    {"domain": "tiktook.eu.cc", "active": True, "health": "ok", "latency": "23ms", "type": "主域名"},
    {"domain": "tiktokmall.shop", "active": True, "health": "ok", "latency": "45ms", "type": "轮值"},
    {"domain": "tiktokmall.store", "active": True, "health": "ok", "latency": "38ms", "type": "轮值"},
    {"domain": "tiktokmall.online", "active": True, "health": "ok", "latency": "52ms", "type": "轮值"},
    {"domain": "tiktokmall.cc", "active": False, "health": "blocked", "latency": "-", "type": "轮值(已停用)"},
    {"domain": "tiktokmall.live", "active": True, "health": "ok", "latency": "31ms", "type": "轮值"},
    {"domain": "tiktokmall.xyz", "active": True, "health": "degraded", "latency": "180ms", "type": "轮值"},
    {"domain": "tiktokmall.top", "active": True, "health": "ok", "latency": "41ms", "type": "轮值"},
    {"domain": "img.tiktook.eu.cc", "active": True, "health": "ok", "latency": "15ms", "type": "CDN图片"},
]


class ToggleRequest(BaseModel):
    domain: str
    active: bool


class CheckRequest(BaseModel):
    domain: str


@router.get("/domains")
async def get_domains(_=Depends(verify_token)):
    return DOMAINS


@router.post("/toggle")
async def toggle_domain(req: ToggleRequest, _=Depends(verify_token)):
    for d in DOMAINS:
        if d["domain"] == req.domain:
            d["active"] = req.active
            if not req.active:
                d["health"] = "disabled"
            else:
                d["health"] = "ok"
            state.add_task(f"域名轮值: {req.domain} {'启用' if req.active else '停用'}", risk="L2")
            return {"domain": req.domain, "active": req.active}
    raise HTTPException(status_code=404, detail="Domain not found")


@router.post("/check")
async def check_domain(req: CheckRequest, _=Depends(verify_token)):
    for d in DOMAINS:
        if d["domain"] == req.domain:
            d["health"] = "ok"
            state.add_task(f"域名检查: {req.domain} → OK", risk="L1")
            return {"domain": req.domain, "health": "ok", "latency": d.get("latency", "?")}
    raise HTTPException(status_code=404, detail="Domain not found")
