""" -- /Docker/Nginx//"""
import httpx
from datetime import datetime
from fastapi import APIRouter, Depends
from auth import verify_token
from risk import handle_risk
from state import state
from config import MALL_BASE_URL

router = APIRouter(prefix="/inspector", tags=["Inspector"])

def _get_tasks():
    return state._data.setdefault("inspection_tasks", [])

def _save():
    state._save()


@router.post("/run")
async def run_inspection(_=Depends(verify_token)):
    ''''''
    await handle_risk("L2", '')

    tasks = _get_tasks()
    now = datetime.now().strftime("%H:%M:%S")
    results = []

    # 1.  mall-app 
    mall_ok = False
    try:
        async with httpx.AsyncClient(timeout=10) as c:
            r = await c.get(f"{MALL_BASE_URL}/agent/health")
            mall_ok = r.status_code == 200
    except Exception:
        pass
    results.append({"name": '', "ok": mall_ok, "detail": '' if mall_ok else ''})

    # 2.  agent 
    results.append({"name": "Agent", "ok": True, "detail": ''})

    # 3. 
    pending = len(state.pending_approvals)
    if pending > 0:
        results.append({"name": '', "ok": True, "detail": f"{pending}"})

    # 4. 
    try:
        from routers.rollback_center import _load_backups
        backup_count = len(_load_backups())
    except Exception:
        backup_count = 0
    results.append({"name": '', "ok": True, "detail": f"{backup_count}"})

    
    report = {
        "time": now,
        "results": results,
        "total": len(results),
        "passed": sum(1 for r in results if r["ok"]),
        "failed": sum(1 for r in results if not r["ok"]),
    }
    tasks.insert(0, report)
    if len(tasks) > 50:
        tasks[:] = tasks[:50]
    _save()

    # ,
    if report["failed"] > 0:
        from routers.alert import _get_alerts, _send_alert_notification
        alerts = _get_alerts()
        failed_items = [r for r in results if not r["ok"]]
        for item in failed_items:
            alert = {
                "id": f"alert_inspect_{int(datetime.now().timestamp())}",
                "level": "P3",
                "level_name": '',
                "title": f": {item['name']}",
                "detail": item["detail"],
                "source": "inspector",
                "time": now,
                "resolved": False,
                "resolved_at": None,
            }
            alerts.insert(0, alert)
        if len(alerts) > 200:
            alerts[:] = alerts[:200]
        state._save()

    return report


@router.get("/history")
async def inspection_history(_=Depends(verify_token)):
    await handle_risk("L1", '')
    return {"history": _get_tasks()[:20]}


@router.post("/schedule")
async def schedule_inspection(_=Depends(verify_token)):
    ''"(APScheduler),''"
    await handle_risk("L2", '')
    return {
        "scheduled": True,
        "note": "APScheduler,",
        "interval": ": 30",
    }

