''" -- L1 / L2+ / L3 / L4''"
import httpx
from datetime import datetime
from config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID
from state import state

RISK_LEVELS = {"L1", "L2", "L3", "L4"}


async def handle_risk(level: str, action_name: str, detail: str = '') -> dict:
    ''"
    .
    - L1: ,
    - L2:  +  +  Telegram 
    - L3: ,
    - L4: ,

    :
      L1/L2: {"allowed": True, "risk": level, "task_id": "..."}
      L3:    {"allowed": False, "risk": "L3", "approval_id": "...", "message": ''}
      L4:    {"allowed": False, "risk": "L4", "message": ","}
    ''"
    if level not in RISK_LEVELS:
        level = "L1"

    if level == "L1":
        print(f"[Risk] L1 | {action_name} | {detail or '-'}")
        return {"allowed": True, "risk": "L1", "task_id": ''}

    if level == "L2":
        task = state.add_task(name=action_name, risk="L2")
        _send_notification(action_name, detail)
        return {"allowed": True, "risk": "L2", "task_id": task["id"]}

    if level == "L3":
        task_id = f"approval_{int(datetime.now().timestamp())}"
        state.add_approval(task_id=task_id, risk="L3", name=action_name, description=detail)
        _send_notification(f" L3 : {action_name}", detail)
        return {
            "allowed": False,
            "risk": "L3",
            "approval_id": task_id,
            "message": ",",
        }

    if level == "L4":
        state.mode = "human_control"
        state.add_emergency("human_control", f"L4: {action_name}")
        state.add_task(name=action_name, risk="L4", status="-")
        _send_notification(f" L4 : {action_name}", f"{detail}\n")
        return {
            "allowed": False,
            "risk": "L4",
            "message": ",",
            "mode": "human_control",
        }


def _send_notification(action_name: str, detail: str):
    ''" Telegram''"
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        return

    import asyncio

    text = (
        f"\u2699\ufe0f <b>TikTokMall Agent</b>\n"
        f"<b></b>: {action_name}\n"
        f"<b></b>: {detail or '-'}\n"
        f"<b></b>: {datetime.now().strftime('%H:%M:%S')}"
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
