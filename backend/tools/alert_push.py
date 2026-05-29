锘?""鏅鸿兘鍛婅鎺ㄩ€?鈥?宸℃寮傚父鑷姩鎺ㄥ井淇?Telegram/閭欢"""
import os, httpx, json
from datetime import datetime
from tools.logger import get_logger

logger = get_logger("alert_push")

# 鎺ㄩ€佹笭閬撻厤缃?
TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "")
WECOM_WEBHOOK = os.getenv("WECOM_WEBHOOK", "")  # 浼佷笟寰俊
DINGTALK_WEBHOOK = os.getenv("DINGTALK_WEBHOOK", "")  # 閽夐拤
SMTP_HOST = os.getenv("SMTP_HOST", "")
SMTP_USER = os.getenv("SMTP_USER", "")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
SMTP_TO = os.getenv("SMTP_TO", "")

async def push_alert(title: str, content: str, level: str = "P2"):
    """澶氭笭閬撴帹閫佸憡璀?""
    results = {}
    emoji = {"P1": "馃敶", "P2": "馃煛", "P3": "馃煝", "P4": "鈿?}.get(level, "馃摙")
    full_msg = f"{emoji} [{level}] {title}\n\n{content}\n\n鈴?{datetime.now().strftime('%m-%d %H:%M')}"

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

    # 2. 浼佷笟寰俊
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

    # 3. 閽夐拤
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

    logger.info(f"鍛婅鎺ㄩ€佸畬鎴? {json.dumps(results)}")
    return results

async def push_weekly_report(report_data: dict):
    """鎺ㄩ€佸懆鎶ュ埌鎵€鏈夋笭閬?""
    summary = report_data.get("summary", "鍛ㄦ姤鐢熸垚涓?..")
    return await push_alert("馃搳 AI杩愯惀鍛ㄦ姤", summary, "P3")
