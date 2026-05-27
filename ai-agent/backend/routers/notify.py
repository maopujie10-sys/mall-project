"""消息通知 — Telegram Bot消息推送"""
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from main import verify_token
from config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID
import httpx

router = APIRouter(prefix="/agent/notify", tags=["Notify"])

class NotifyRequest(BaseModel):
    message: str
    level: str = "info"  # info | warn | error
    channel: str = "telegram"

@router.post("/send")
async def send_notification(req: NotifyRequest, _=Depends(verify_token)):
    """发送Telegram通知"""
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        return {"sent": False, "error": "TELEGRAM_BOT_TOKEN 或 TELEGRAM_CHAT_ID 未配置"}

    emoji = {"info": "ℹ️", "warn": "⚠️", "error": "🚨"}.get(req.level, "ℹ️")
    text = f"{emoji} <b>TikTokMall</b>\n{req.message}"

    try:
        async with httpx.AsyncClient(timeout=10) as c:
            r = await c.post(
                f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage",
                json={"chat_id": TELEGRAM_CHAT_ID, "text": text, "parse_mode": "HTML"}
            )
        return {"sent": r.status_code == 200, "response": r.json() if r.status_code != 200 else "ok"}
    except Exception as e:
        return {"sent": False, "error": str(e)}

@router.get("/config")
async def notify_config(_=Depends(verify_token)):
    """查看通知配置状态"""
    return {
        "telegram": {
            "configured": bool(TELEGRAM_BOT_TOKEN),
            "chat_id_set": bool(TELEGRAM_CHAT_ID),
        }
    }
