"""Self-Healing Agent API -- """
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
    ''''''
    await handle_risk("L1", '')
    return await SelfHealingAgent.run_patrol()

@router.post("/auto-fix")
async def auto_fix(anomaly_id: str = None, _=Depends(verify_token)):
    ''''''
    await handle_risk("L2", '', anomaly_id or '')
    return await SelfHealingAgent.auto_fix(anomaly_id)

@router.get("/history")
async def anomaly_history(days: int = 7, _=Depends(verify_token)):
    ''''''
    await handle_risk("L1", '')
    return await SelfHealingAgent.get_anomaly_history(days)

@router.post("/resolve")
async def resolve_anomaly(req: ResolveRequest, _=Depends(verify_token)):
    ''''''
    await handle_risk("L1", '', req.anomaly_id)
    return await SelfHealingAgent.resolve_anomaly(req.anomaly_id, req.resolution)