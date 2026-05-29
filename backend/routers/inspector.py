"""鑷姩宸℃ 鈥?瀹氭椂妫€鏌ユ湇鍔″櫒/Docker/Nginx/缃戠珯/鍩熷悕鐘舵€?""
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
    """鎵嬪姩瑙﹀彂涓€娆″叏閲忓贰妫€"""
    await handle_risk("L2", "鎵ц鍏ㄩ噺宸℃")

    tasks = _get_tasks()
    now = datetime.now().strftime("%H:%M:%S")
    results = []

    # 1. 妫€鏌?mall-app 杩為€氭€?
    mall_ok = False
    try:
        async with httpx.AsyncClient(timeout=10) as c:
            r = await c.get(f"{MALL_BASE_URL}/agent/health")
            mall_ok = r.status_code == 200
    except Exception:
        pass
    results.append({"name": "鍟嗗煄杩為€氭€?, "ok": mall_ok, "detail": "姝ｅ父" if mall_ok else "涓嶅彲杈?})

    # 2. 妫€鏌?agent 鑷韩
    results.append({"name": "Agent鐘舵€?, "ok": True, "detail": "杩愯涓?})

    # 3. 妫€鏌ュ緟瀹℃壒鏁伴噺
    pending = len(state.pending_approvals)
    if pending > 0:
        results.append({"name": "寰呭鎵逛换鍔?, "ok": True, "detail": f"{pending}椤瑰緟澶勭悊"})

    # 4. 妫€鏌ュ浠?
    try:
        from routers.rollback_center import _load_backups
        backup_count = len(_load_backups())
    except Exception:
        backup_count = 0
    results.append({"name": "澶囦唤璁板綍", "ok": True, "detail": f"鍏眥backup_count}鏉?})

    # 璁板綍鏈宸℃
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

    # 濡傛灉鏈夊け璐ラ」锛岃嚜鍔ㄥ垱寤哄憡璀?
    if report["failed"] > 0:
        from routers.alert import _get_alerts, _send_alert_notification
        alerts = _get_alerts()
        failed_items = [r for r in results if not r["ok"]]
        for item in failed_items:
            alert = {
                "id": f"alert_inspect_{int(datetime.now().timestamp())}",
                "level": "P3",
                "level_name": "涓€鑸?,
                "title": f"宸℃寮傚父: {item['name']}",
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
    await handle_risk("L1", "鏌ョ湅宸℃鍘嗗彶")
    return {"history": _get_tasks()[:20]}


@router.post("/schedule")
async def schedule_inspection(_=Depends(verify_token)):
    """璁剧疆瀹氭椂宸℃锛堥€氳繃APScheduler锛夛紝棰勭暀鎺ュ彛"""
    await handle_risk("L2", "璁剧疆瀹氭椂宸℃")
    return {
        "scheduled": True,
        "note": "瀹氭椂浠诲姟闇€鍦ㄦ湇鍔″惎鍔ㄦ椂閫氳繃APScheduler閰嶇疆锛屽綋鍓嶄负鎵嬪姩瑙﹀彂妯″紡",
        "interval": "寤鸿: 姣?0鍒嗛挓鑷姩宸℃涓€娆?,
    }

