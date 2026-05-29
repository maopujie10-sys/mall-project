"""系统模式管理 + 紧急切换 + 审批中心"""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from auth import verify_token
from state import state
from risk import handle_risk
from diff_utils import generate_diff_preview

router = APIRouter(prefix="/system", tags=["System"])

VALID_MODES = {"ai_control", "readonly", "assist", "human_control"}

class SetModeRequest(BaseModel):
    mode: str

class ApprovalDecideRequest(BaseModel):
    taskId: str
    approved: bool

@router.get("/mode")
async def get_mode(_=Depends(verify_token)):
    await handle_risk("L1", "查看系统模式")
    return {
        "mode": state.mode,
        "pendingCount": len(state.pending_approvals),
        "historyCount": len(state.approval_history),
        "taskCount": len(state.tasks),
    }

@router.post("/mode")
async def set_mode(req: SetModeRequest, _=Depends(verify_token)):
    if req.mode not in VALID_MODES:
        raise HTTPException(400, f"无效模式: {req.mode}. 可选: {VALID_MODES}")
    old = state.mode
    state.mode = req.mode
    state.add_emergency(req.mode, f"用户切换模式: {old} -> {req.mode}")
    return {"mode": state.mode, "previous": old}

@router.post("/emergency")
async def emergency_stop(_=Depends(verify_token)):
    state.mode = "human_control"
    state.add_emergency("human_control", "紧急停止 - 用户触发")
    return {"mode": "human_control", "message": "AI已暂停,所有自动操作已停止"}

@router.get("/approvals")
async def list_approvals(_=Depends(verify_token)):
    await handle_risk("L1", "查看审批列表")
    return {"pending": state.pending_approvals, "history": state.approval_history[-20:]}

@router.post("/approvals/decide")
async def decide_approval(req: ApprovalDecideRequest, _=Depends(verify_token)):
    result = state.decide_approval(req.taskId, req.approved)
    if not result:
        raise HTTPException(404, "审批项不存在")
    return {"result": result["result"], "taskId": req.taskId}

@router.post("/approvals/diff")
async def preview_diff(task_id: str, before: dict, after: dict, action: str = "", _=Depends(verify_token)):
    """生成变更预览 diff"""
    await handle_risk("L1", "生成变更预览", action or task_id)
    result = generate_diff_preview(action or task_id, before, after)
    return result

@router.get("/emergency-history")
async def emergency_history(_=Depends(verify_token)):
    await handle_risk("L1", "查看紧急事件历史")
    return {"history": state.emergency_history}