"""告警中心 -- P1~P4 告警分级/触发/通知"""
from datetime import datetime
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from auth import verify_token
from state import state
from risk import handle_risk
from config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID
import httpx

router = APIRouter(prefix="/alert", tags=["Alert"])

ALERT_LEVELS = {"P1": "紧急", "P2": "严重", "P3": "一般", "P4": "观察"}

class AlertCreateRequest(BaseModel):
    title: str
    detail: str = ""
    level: str = "P3"
    source: str = "system"

def _get_alerts():
    return state._data.setdefault("alerts", [])

def _send_alert_notification(level: str, title: str, detail: str):
    """发送告警通知到 Telegram"""
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        return
    import asyncio
    emoji = {"P1": "??", "P2": "??", "P3": "??", "P4": "??"}
    text = (
        f"{emoji.get(level, '??')} <b>[{level}] TikTokMall</b>\n"
        f"<b>{title}</b>\n"
        f"{detail or '-'}\n"
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

@router.get("/list")
async def list_alerts(_=Depends(verify_token), level: str = None):
    await handle_risk("L1", "查看告警列表")
    alerts = _get_alerts()
    if level:
        alerts = [a for a in alerts if a["level"] == level]
    return {"alerts": alerts[:100], "count": len(alerts)}

@router.post("/create")
async def create_alert(req: AlertCreateRequest, _=Depends(verify_token)):
    await handle_risk("L1", f"创建告警 [{req.level}]", req.title)
    if req.level not in ALERT_LEVELS:
        return {"error": f"无效等级: {req.level},可选: {list(ALERT_LEVELS.keys())}"}

    alerts = _get_alerts()
    alert = {
        "id": f"alert_{len(alerts)+1}_{int(datetime.now().timestamp())}",
        "level": req.level,
        "level_name": ALERT_LEVELS[req.level],
        "title": req.title,
        "detail": req.detail,
        "source": req.source,
        "time": datetime.now().strftime("%H:%M:%S"),
        "resolved": False,
        "resolved_at": None,
    }
    alerts.insert(0, alert)
    if len(alerts) > 200:
        alerts[:] = alerts[:200]
    state._save()

    # P1/P2 自动发通知
    if req.level in ("P1", "P2"):
        _send_alert_notification(req.level, req.title, req.detail)

    # P1 自动切人工接管
    if req.level == "P1":
        state.mode = "human_control"
        state.add_emergency("human_control", f"P1告警触发: {req.title}")

    return alert

@router.post("/resolve/{alert_id}")
async def resolve_alert(alert_id: str, _=Depends(verify_token)):
    alerts = _get_alerts()
    for a in alerts:
        if a["id"] == alert_id:
            a["resolved"] = True
            a["resolved_at"] = datetime.now().strftime("%H:%M:%S")
            state._save()
            return {"resolved": True, "alert_id": alert_id}
    return {"error": "告警不存在"}

@router.get("/stats")
async def alert_stats(_=Depends(verify_token)):
    alerts = _get_alerts()
    stats = {k: {"name": v, "count": 0, "unresolved": 0} for k, v in ALERT_LEVELS.items()}
    for a in alerts:
        lv = a.get("level", "P3")
        if lv in stats:
            stats[lv]["count"] += 1
            if not a.get("resolved"):
                stats[lv]["unresolved"] += 1
    return {"stats": stats, "total": len(alerts)}


# ===== ???? =====
from tools.alert_closed_loop import AlertClosedLoop

@router.post("/health-check")
async def run_health_check(_=Depends(verify_token)):
    """???????? + ????"""
    return await AlertClosedLoop.run_health_check()

@router.get("/closed-loop-history")
async def get_closed_loop_history(limit: int = 20, _=Depends(verify_token)):
    """????????"""
    return {"ok": True, "history": AlertClosedLoop.get_history(limit)}

@router.post("/auto-fix")
async def trigger_auto_fix(req: AlertCreateRequest, _=Depends(verify_token)):
    """???????????"""
    return await AlertClosedLoop.detect_and_fix(req.title, req.detail, auto_fix=True)
