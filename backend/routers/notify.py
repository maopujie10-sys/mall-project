"""消息通知 -- Telegram / SMTP 邮件 / 钉钉 / 企业微信"""
from datetime import datetime
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from auth import verify_token
from config import (
    TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID,
    SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASSWORD, SMTP_TO,
    DINGTALK_WEBHOOK, WECOM_WEBHOOK,
)
from risk import handle_risk
import httpx

router = APIRouter(prefix="/agent/notify", tags=["Notify"])

class NotifyRequest(BaseModel):
    message: str
    level: str = "info"
    channel: str = "telegram"  # telegram / email / dingtalk / wecom / all

EMOJI = {"info": "??", "warn": "??", "error": "??", "critical": "??"}

async def send_telegram(message: str, level: str) -> dict:
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        return {"sent": False, "error": "Telegram 未配置"}
    emoji = EMOJI.get(level, "??")
    text = f"{emoji} <b>TikTokMall</b>\n{message}"
    try:
        async with httpx.AsyncClient(timeout=10) as c:
            r = await c.post(
                f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage",
                json={"chat_id": TELEGRAM_CHAT_ID, "text": text, "parse_mode": "HTML"}
            )
        return {"sent": r.status_code == 200}
    except Exception as e:
        return {"sent": False, "error": str(e)}

async def send_email(message: str, level: str) -> dict:
    if not SMTP_HOST or not SMTP_TO:
        return {"sent": False, "error": "邮件未配置"}
    import smtplib
    from email.message import EmailMessage
    try:
        msg = EmailMessage()
        msg.set_content(f"[{level}] TikTokMall\n\n{message}\n\n{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        msg["Subject"] = f"[TikTokMall] {level} ֪ͨ"
        msg["From"] = SMTP_USER
        msg["To"] = SMTP_TO
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as s:
            if SMTP_USER and SMTP_PASSWORD:
                s.starttls()
                s.login(SMTP_USER, SMTP_PASSWORD)
            s.send_message(msg)
        return {"sent": True}
    except Exception as e:
        return {"sent": False, "error": str(e)}

async def send_dingtalk(message: str, level: str) -> dict:
    if not DINGTALK_WEBHOOK:
        return {"sent": False, "error": "钉钉未配置"}
    try:
        async with httpx.AsyncClient(timeout=10) as c:
            r = await c.post(DINGTALK_WEBHOOK, json={"msgtype": "text", "text": {"content": f"[{level}] TikTokMall\n{message}"}})
        return {"sent": r.status_code == 200}
    except Exception as e:
        return {"sent": False, "error": str(e)}

async def send_wecom(message: str, level: str) -> dict:
    if not WECOM_WEBHOOK:
        return {"sent": False, "error": "企业微信未配置"}
    try:
        async with httpx.AsyncClient(timeout=10) as c:
            r = await c.post(WECOM_WEBHOOK, json={"msgtype": "text", "text": {"content": f"[{level}] TikTokMall\n{message}"}})
        return {"sent": r.status_code == 200}
    except Exception as e:
        return {"sent": False, "error": str(e)}

CHANNEL_MAP = {
    "telegram": send_telegram,
    "email": send_email,
    "dingtalk": send_dingtalk,
    "wecom": send_wecom,
}

@router.post("/send")
async def send_notification(req: NotifyRequest, _=Depends(verify_token)):
    """消息通知 -- Telegram / SMTP 邮件 / 钉钉 / 企业微信"""
    await handle_risk("L1", f"����֪ͨ ({req.channel})", req.message[:50])

    if req.channel == "all":
        results = {}
        for name, func in CHANNEL_MAP.items():
            results[name] = await func(req.message, req.level)
        return {"sent": any(r["sent"] for r in results.values()), "results": results}

    func = CHANNEL_MAP.get(req.channel)
    if not func:
        return {"sent": False, "error": f"��֧�ֵ�֪ͨ����: {req.channel}����ѡ: {list(CHANNEL_MAP.keys()) + ['all']}"}

    return await func(req.message, req.level)

@router.get("/config")
async def notify_config(_=Depends(verify_token)):
    await handle_risk("L1", "�鿴֪ͨ����")
    return {
        "telegram": {"configured": bool(TELEGRAM_BOT_TOKEN)},
        "email": {"configured": bool(SMTP_HOST)},
        "dingtalk": {"configured": bool(DINGTALK_WEBHOOK)},
        "wecom": {"configured": bool(WECOM_WEBHOOK)},
    }
