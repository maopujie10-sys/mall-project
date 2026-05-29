"""Self-Healing Agent API -- 自动修复入口"""
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from auth import verify_token
from risk import handle_risk
from agents.self_healing_agent import SelfHealingAgent

router = APIRouter(prefix="/heal", tags=["SelfHealing"])

class ResolveRequest(BaseModel):
    anomaly_id: str
    resolution: str = "manual"

@router.post("/patrol")
async def run_patrol(_=Depends(verify_token)):
    """执行全面巡检"""
    await handle_risk("L1", "自动巡检")
    return await SelfHealingAgent.run_patrol()

@router.post("/auto-fix")
async def auto_fix(anomaly_id: str = None, _=Depends(verify_token)):
    """自动修复异常"""
    await handle_risk("L2", "自动修复", anomaly_id or "全部")
    return await SelfHealingAgent.auto_fix(anomaly_id)

@router.get("/history")
async def anomaly_history(days: int = 7, _=Depends(verify_token)):
    """异常历史"""
    await handle_risk("L1", "异常历史")
    return await SelfHealingAgent.get_anomaly_history(days)

@router.post("/resolve")
async def resolve_anomaly(req: ResolveRequest, _=Depends(verify_token)):
    """标记已解决"""
    await handle_risk("L1", "标记解决", req.anomaly_id)
    return await SelfHealingAgent.resolve_anomaly(req.anomaly_id, req.resolution)