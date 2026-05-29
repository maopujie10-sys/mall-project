"""风险等级控制 — L1自动 / L2记录+通知 / L3需审批 / L4强制接管"""
import httpx
from datetime import datetime
from config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID
from state import state

RISK_LEVELS = {"L1", "L2", "L3", "L4"}


async def handle_risk(level: str, action_name: str, detail: str = "") -> dict:
    """
    风险等级拦截器。
    - L1: 自动放行，仅打印日志
    - L2: 放行 + 记录任务 + 推送 Telegram 通知
    - L3: 创建待审批项，等待用户确认后方可执行
    - L4: 强制切换人工接管模式，禁止自动执行

    返回:
      L1/L2: {"allowed": True, "risk": level, "task_id": "..."}
      L3:    {"allowed": False, "risk": "L3", "approval_id": "...", "message": "需审批确认"}
      L4:    {"allowed": False, "risk": "L4", "message": "高风险操作，已强制人工接管"}
    """
    if level not in RISK_LEVELS:
        level = "L1"

    if level == "L1":
        print(f"[Risk] L1 | {action_name} | {detail or '-'}")
        return {"allowed": True, "risk": "L1", "task_id": ""}

    if level == "L2":
        task = state.add_task(name=action_name, risk="L2")
        _send_notification(action_name, detail)
        return {"allowed": True, "risk": "L2", "task_id": task["id"]}

    if level == "L3":
        task_id = f"approval_{int(datetime.now().timestamp())}"
        state.add_approval(task_id=task_id, risk="L3", name=action_name, description=detail)
        _send_notification(f"🟡 L3 需审批: {action_name}", detail)
        return {
            "allowed": False,
            "risk": "L3",
            "approval_id": task_id,
            "message": "此操作需要审批确认，请前往审批中心处理",
        }

    if level == "L4":
        state.mode = "human_control"
        state.add_emergency("human_control", f"L4高风险操作: {action_name}")
        state.add_task(name=action_name, risk="L4", status="已拒绝-人工接管")
        _send_notification(f"🔴 L4 强制接管: {action_name}", f"{detail}\n系统已自动切换为人工接管模式")
        return {
            "allowed": False,
            "risk": "L4",
            "message": "高风险操作，已强制切换为人工接管模式，自动执行已停止",
            "mode": "human_control",
        }


def _send_notification(action_name: str, detail: str):
    """发送通知到 Telegram"""
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        return

    import asyncio

    text = (
        f"\u2699\ufe0f <b>TikTokMall Agent</b>\n"
        f"<b>操作</b>: {action_name}\n"
        f"<b>详情</b>: {detail or '-'}\n"
        f"<b>时间</b>: {datetime.now().strftime('%H:%M:%S')}"
    )

    async def _send():
        try:
            async with httpx.AsyncClient(timeout=5) as c:
                await c.post(
                    f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage",
                    json={"chat_id": TELEGRAM_CHAT_ID, "text": text, "parse_mode": "HTML"}
                )
        except Exception:
            pass

    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            asyncio.ensure_future(_send())
        else:
            loop.run_until_complete(_send())
    except Exception:
        pass
