"""IP黑名单与安全 — 封禁/解封IP"""
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from auth import verify_token
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

@router.get("/blacklist")
async def list_blocked(_=Depends(verify_token)):
    await handle_risk("L1", "查看IP黑名单")
    _clean_expired()
    return {"blocked_ips": _get_blacklist(), "count": len(_get_blacklist())}

@router.post("/block")
async def block_ip(req: BlockRequest, _=Depends(verify_token)):
    _clean_expired()
    for e in _get_blacklist():
        if e["ip"] == req.ip:
            e["reason"] = req.reason
            e["hours"] = req.hours
            e["expires_at"] = (datetime.now() + timedelta(hours=req.hours)).isoformat()
            state._save()
            return {"action": "updated", "ip": req.ip}
    _get_blacklist().append({
        "ip": req.ip, "reason": req.reason, "hours": req.hours,
        "blocked_at": datetime.now().isoformat(),
        "expires_at": (datetime.now() + timedelta(hours=req.hours)).isoformat(),
    })
    state._save()
    return {"action": "block", "ip": req.ip}

@router.delete("/block/{ip}")
async def unblock_ip(ip: str, _=Depends(verify_token)):
    before = len(_get_blacklist())
    state._data["ip_blacklist"] = [e for e in _get_blacklist() if e["ip"] != ip]
    state._save()
    return {"action": "unblock", "ip": ip, "removed": before > len(_get_blacklist())}

