"""熔断机制 + 防循环 API"""
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from auth import verify_token
from risk import handle_risk
from safety import circuit_breaker, anti_loop

router = APIRouter(prefix="/safety", tags=["Safety"])

@router.get("/circuit")
async def circuit_status(_=Depends(verify_token)):
    await handle_risk("L1", "查看熔断状态")
    return circuit_breaker.status()

@router.post("/circuit/reset")
async def circuit_reset(action: str = "", _=Depends(verify_token)):
    """重置指定操作的熔断器，留空则重置全部"""
    await handle_risk("L1", "重置熔断器", action or "全部")
    from safety import CircuitBreaker
    if action:
        circuit_breaker._failures[action].clear()
        circuit_breaker._states.pop(action, None)
    else:
        circuit_breaker._failures.clear()
        circuit_breaker._states.clear()
    return {"reset": True, "action": action or "all"}

@router.get("/anti-loop")
async def antiloop_status(_=Depends(verify_token)):
    await handle_risk("L1", "查看防循环状态")
    return {"records": dict(anti_loop._records)}

@router.post("/anti-loop/check")
async def antiloop_check(action_key: str, max_count: int = 1, window_min: int = 10, _=Depends(verify_token)):
    allowed = anti_loop.check(action_key, max_count, window_min)
    return {"action_key": action_key, "allowed": allowed}

@router.post("/anti-loop/record")
async def antiloop_record(action_key: str, _=Depends(verify_token)):
    anti_loop.record(action_key)
    return {"action_key": action_key, "recorded": True}

@router.post("/anti-loop/reset")
async def antiloop_reset(action_key: str = "", _=Depends(verify_token)):
    if action_key:
        anti_loop.reset(action_key)
    else:
        anti_loop._records.clear()
    return {"reset": True, "action_key": action_key or "all"}
