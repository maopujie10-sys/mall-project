"""系统模式管理 + 紧急切断 + 审批中心"""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from main import verify_token
from state import state

router = APIRouter(prefix="/system", tags=["System"])

VALID_MODES = {"ai_control", "readonly", "assist", "human_control"}


class SetModeRequest(BaseModel):
    mode: str


class ApprovalDecideRequest(BaseModel):
    taskId: str
    approved: bool


@router.get("/mode")
async def get_mode(_=Depends(verify_token)):
    return {
        "mode": state.mode,
        "pendingCount": len(state.pending_approvals),
        "validModes": list(VALID_MODES),
    }


@router.post("/mode")
async def set_mode(req: SetModeRequest, _=Depends(verify_token)):
    if req.mode not in VALID_MODES:
        raise HTTPException(status_code=400, detail=f"Invalid mode. Valid: {VALID_MODES}")

    old_mode = state.mode
    state.mode = req.mode
    state.add_emergency(req.mode, f"手动切换到 {req.mode}")
    state.add_task(f"模式切换: {old_mode} → {req.mode}", risk="L3", status="完成")

    return {"mode": state.mode, "previous": old_mode}


@router.post("/emergency-kill")
async def emergency_kill(_=Depends(verify_token)):
    """立即切断AI所有写权限，进入人工接管模式"""
    old_mode = state.mode
    state.mode = "human_control"
    state.add_emergency("human_control", "Kill Switch 触发")
    state.add_task("紧急切断: AI写权限已停止", risk="L3", status="完成")

    return {
        "mode": "human_control",
        "previous": old_mode,
        "message": "AI写权限已切断，所有高危操作已阻止",
    }


@router.get("/emergency-history")
async def emergency_history(_=Depends(verify_token)):
    return state.emergency_history


# ── 审批中心 ──
@router.get("/approvals/pending")
async def pending_approvals(_=Depends(verify_token)):
    return state.pending_approvals


@router.post("/approvals/decide")
async def decide_approval(req: ApprovalDecideRequest, _=Depends(verify_token)):
    result = state.decide_approval(req.taskId, req.approved)
    if result is None:
        raise HTTPException(status_code=404, detail="Approval task not found")
    state.add_task(
        f"审批决定: {'通过' if req.approved else '拒绝'} [{result['risk']}] {result['name']}",
        risk=result.get("risk", "L2"),
        status="完成",
    )
    return {"result": "ok", "detail": result}


@router.get("/approvals/history")
async def approval_history(_=Depends(verify_token)):
    return state.approval_history
