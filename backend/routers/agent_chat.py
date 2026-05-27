"""AI Agent对话 + 任务管理 + 人工接管"""
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from main import verify_token
from state import state

router = APIRouter(prefix="/agent", tags=["Agent"])


class ChatRequest(BaseModel):
    message: str


class ConfirmRequest(BaseModel):
    taskId: str
    approved: bool


class HandoverRequest(BaseModel):
    reason: str = ""


# ── 命令处理器 ──
COMMANDS = {
    "help": "支持命令: status(服务状态), server(服务器), restart <服务名>, mode(系统模式), tasks(任务列表), approvals(待审批), backup(备份), health(健康检查)",
    "status": "report_status",
    "server": "report_status",
    "health": "report_status",
    "restart": "restart_hint",
    "mode": "mode_info",
    "tasks": "tasks_info",
    "approvals": "approvals_info",
    "backup": "backup_hint",
}


@router.post("/chat")
async def chat(req: ChatRequest, _=Depends(verify_token)):
    msg = req.message.strip().lower()
    response_text = ""
    action = None

    cmd = COMMANDS.get(msg, None)
    if msg.startswith("restart"):
        service = msg.replace("restart", "").strip()
        response_text = f"重启 {service} 需要确认。请通过审批中心提交请求，或使用 /agent/restart/{service} 直接操作。"
        action = {"type": "restart_prompt", "service": service}
    elif cmd == "report_status":
        response_text = (
            f"TikTokMall Agent 运行正常。\n"
            f"模式: {state.mode}\n"
            f"待审批: {len(state.pending_approvals)}项\n"
            f"今日任务: {len(state.tasks)}项\n"
            f"商城: MALL_BASE_URL 已配置"
        )
    elif cmd == "mode_info":
        response_text = f"当前模式: {state.mode}。可用模式: ai_control(全自动), readonly(只读), assist(辅助), human_control(人工接管)"
        action = {"type": "switch_mode", "current": state.mode}
    elif cmd == "tasks_info":
        recent = state.tasks[:5]
        lines = [f"- [{t['risk']}] {t['name']} ({t['status']}) {t['time']}" for t in recent]
        response_text = "最近任务:\n" + ("\n".join(lines) if lines else "无任务记录")
    elif cmd == "approvals_info":
        pending = state.pending_approvals
        lines = [f"- [{a['risk']}] {a['name']} (id={a['id']})" for a in pending]
        response_text = "待审批:\n" + ("\n".join(lines) if lines else "无待审批项")
    elif cmd == "backup_hint":
        response_text = "备份操作属于L3级风险，需要人工确认。请通过审批中心提交备份请求。"
    elif cmd is None:
        response_text = f"收到: 「{req.message}」\n\n{COMMANDS['help']}"
    else:
        response_text = cmd

    state.add_task(f"Chat: {req.message[:40]}", risk="L1")
    return {"reply": response_text, "action": action}


@router.get("/tasks")
async def list_tasks(limit: int = 20, _=Depends(verify_token)):
    return state.tasks[:limit]


@router.post("/confirm")
async def confirm_task(req: ConfirmRequest, _=Depends(verify_token)):
    result = state.decide_approval(req.taskId, req.approved)
    if result is None:
        return {"error": "task not found in pending approvals"}
    state.add_task(
        f"审批: {'通过' if req.approved else '拒绝'} [{result['risk']}] {result['name']}",
        risk=result.get("risk", "L2"),
        status="完成",
    )
    return {"result": "ok", "detail": result}


@router.post("/handover")
async def handover(req: HandoverRequest, _=Depends(verify_token)):
    state.mode = "human_control"
    reason = req.reason or "人工请求接管"
    state.add_emergency("human_control", reason)
    state.add_task(f"人工接管: {reason}", risk="L3", status="完成")
    return {"mode": "human_control", "reason": reason}
