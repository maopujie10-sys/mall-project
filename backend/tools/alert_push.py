"""智能告警推送 — 巡检异常自动推微信/Telegram/邮件"""
import os, httpx, json
from datetime import datetime
from tools.logger import get_logger

logger = get_logger("alert_push")

# 推送渠道配置
TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "")
WECOM_WEBHOOK = os.getenv("WECOM_WEBHOOK", "")  # 企业微信
DINGTALK_WEBHOOK = os.getenv("DINGTALK_WEBHOOK", "")  # 钉钉
SMTP_HOST = os.getenv("SMTP_HOST", "")
SMTP_USER = os.getenv("SMTP_USER", "")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
SMTP_TO = os.getenv("SMTP_TO", "")

async def push_alert(title: str, content: str, level: str = "P2"):
    """多渠道推送告警"""
    results = {}
    emoji = {"P1": "🔴", "P2": "🟡", "P3": "🟢", "P4": "⚪"}.get(level, "📢")
    full_msg = f"{emoji} [{level}] {title}\n\n{content}\n\n⏰ {datetime.now().strftime('%m-%d %H:%M')}"

    # 1. Telegram
    if TELEGRAM_TOKEN and TELEGRAM_CHAT_ID:
        try:
            async with httpx.AsyncClient(timeout=10) as c:
                r = await c.post(
                    f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage",
                    json={"chat_id": TELEGRAM_CHAT_ID, "text": full_msg, "parse_mode": "HTML"}
                )
                results["telegram"] = r.status_code == 200
        except Exception as e:
            results["telegram"] = False

    # 2. 企业微信
    if WECOM_WEBHOOK:
        try:
            async with httpx.AsyncClient(timeout=10) as c:
                r = await c.post(WECOM_WEBHOOK, json={
                    "msgtype": "markdown",
                    "markdown": {"content": f"## {emoji} {title}\n{content}\n>{datetime.now().strftime('%m-%d %H:%M')}"}
                })
                results["wecom"] = r.status_code == 200
        except Exception as e:
            results["wecom"] = False

    # 3. 钉钉
    if DINGTALK_WEBHOOK:
        try:
            async with httpx.AsyncClient(timeout=10) as c:
                r = await c.post(DINGTALK_WEBHOOK, json={
                    "msgtype": "markdown",
                    "markdown": {"title": title, "text": full_msg}
                })
                results["dingtalk"] = r.status_code == 200
        except Exception as e:
            results["dingtalk"] = False

    logger.info(f"告警推送完成: {json.dumps(results)}")
    return results

async def push_weekly_report(report_data: dict):
    """推送周报到所有渠道"""
    summary = report_data.get("summary", "周报生成中...")
    return await push_alert("📊 AI运营周报", summary, "P3")
