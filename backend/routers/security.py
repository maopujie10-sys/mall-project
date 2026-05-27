"""IP黑名单与安全 — 封禁/解封IP + 审计日志"""
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel
from auth import verify_token, get_audit_logs, get_rate_limit_stats, create_jwt
from state import state
from risk import handle_risk

router = APIRouter(prefix="/agent/security", tags=["Security"])

def _get_blacklist():
    return state._data.setdefault("ip_blacklist", [])

def _clean_expired():
    now = datetime.now()
    state._data["ip_blacklist"] = [
        e for e in _get_blacklist()
        if datetime.fromisoformat(e["expires_at"]) > now
    ]
    state._save()

class BlockRequest(BaseModel):
    ip: str
    reason: str = "manual"
    hours: int = 24

class JWTRequest(BaseModel):
    subject: str = "agent"
    expire_hours: int = 24

@router.get("/blacklist")
async def list_blocked(_=Depends(verify_token)):
    await handle_risk("L1", "查看IP黑名单")
    _clean_expired()
    return {"blacklist": _get_blacklist(), "count": len(_get_blacklist())}

@router.post("/blacklist/block")
async def block_ip(req: BlockRequest, _=Depends(verify_token)):
    await handle_risk("L3", f"封禁IP: {req.ip}", need_confirm=True)
    _clean_expired()
    expires = (datetime.now() + timedelta(hours=req.hours)).isoformat()
    _get_blacklist().append({"ip": req.ip, "reason": req.reason, "blocked_at": datetime.now().isoformat(), "expires_at": expires})
    state._save()
    return {"ok": True, "ip": req.ip, "expires_at": expires}

@router.post("/blacklist/unblock")
async def unblock_ip(req: BlockRequest, _=Depends(verify_token)):
    await handle_risk("L3", f"解封IP: {req.ip}", need_confirm=True)
    _clean_expired()
    state._data["ip_blacklist"] = [e for e in _get_blacklist() if e["ip"] != req.ip]
    state._save()
    return {"ok": True, "ip": req.ip}

# ===== JWT Token 管理 =====
@router.post("/token")
async def generate_token(req: JWTRequest, _=Depends(verify_token)):
    """生成 JWT Token"""
    await handle_risk("L2", f"生成JWT: {req.subject}")
    token = create_jwt({"sub": req.subject}, req.expire_hours)
    return {"ok": True, "token": token, "expires_in_hours": req.expire_hours}

# ===== 审计日志 =====
@router.get("/audit")
async def audit_logs(limit: int = 100, _=Depends(verify_token)):
    """查看审计日志"""
    await handle_risk("L1", "查看审计日志")
    logs = get_audit_logs(limit)
    return {"ok": True, "logs": logs, "count": len(logs)}

# ===== 速率限制状态 =====
@router.get("/rate-limit")
async def rate_limit_status(_=Depends(verify_token)):
    """查看速率限制状态"""
    stats = get_rate_limit_stats()
    return {"ok": True, **stats}