"""IP黑名单与安全 — 封禁/解封IP"""
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from main import verify_token

router = APIRouter(prefix="/agent/security", tags=["Security"])

class BlockRequest(BaseModel):
    ip: str
    reason: str = "manual"
    hours: int = 24

@router.get("/blacklist")
async def list_blocked(_=Depends(verify_token)):
    """查看被封IP列表"""
    return {"blocked_ips": [], "note": "需Redis集成后真实查询"}

@router.post("/block")
async def block_ip(req: BlockRequest, _=Depends(verify_token)):
    """封禁IP"""
    return {
        "action": "block",
        "ip": req.ip,
        "reason": req.reason,
        "hours": req.hours,
        "note": "需Redis集成后真实写入"
    }

@router.delete("/block/{ip}")
async def unblock_ip(ip: str, _=Depends(verify_token)):
    """解封IP"""
    return {"action": "unblock", "ip": ip}
