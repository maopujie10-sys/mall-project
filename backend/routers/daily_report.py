""" -- """
import httpx
from datetime import datetime
from fastapi import APIRouter, Depends
from auth import verify_token
from state import state
from risk import handle_risk

router = APIRouter(prefix="/report", tags=["Report"])

def _get_reports():
    return state._data.setdefault("daily_reports", [])

@router.post("/daily")
async def generate_daily_report(_=Depends(verify_token)):
    ''''''
    await handle_risk("L2", '')
    today = datetime.now().strftime("%Y-%m-%d")
    now = datetime.now().strftime("%H:%M:%S")

    
    data = {}

    
    from config import MALL_BASE_URL
    async with httpx.AsyncClient(timeout=10) as c:
        try:
            r = await c.get(f"{MALL_BASE_URL}/api/orders", params={"page": 1, "size": 1})
            data["orders_total"] = r.json().get("total", "N/A") if r.status_code == 200 else "N/A"
        except Exception:
            data["orders_total"] = "N/A"

        try:
            r = await c.get(f"{MALL_BASE_URL}/api/products", params={"page": 1, "size": 1})
            data["products_total"] = r.json().get("total", "N/A") if r.status_code == 200 else "N/A"
        except Exception:
            data["products_total"] = "N/A"

    
    data["agent_mode"] = state.mode
    data["pending_approvals"] = len(state.pending_approvals)
    data["tasks_today"] = len(state.tasks)
    data["alerts_unresolved"] = len([a for a in state._data.get("alerts", []) if not a.get("resolved")])

    
    msgs = state._data.get("customer_messages", [])
    today_msgs = [m for m in msgs if today in m.get("time", '')]
    data["customer_messages_today"] = len(today_msgs)

    
    alerts = state._data.get("alerts", [])
    today_alerts = [a for a in alerts if today in a.get("time", '')]
    data["alerts_today"] = len(today_alerts)

    report = {
        "date": today,
        "generated_at": now,
        "data": data,
        "summary": (
            f" {today} \n"
            f" : {data['agent_mode']}\n"
            f" : {data.get('orders_total', 'N/A')} | : {data.get('products_total', 'N/A')}\n"
            f" : {data['pending_approvals']} | : {data['alerts_today']}\n"
            f" : {data['customer_messages_today']}"
        ),
    }

    reports = _get_reports()
    reports.insert(0, report)
    if len(reports) > 30: reports[:] = reports[:30]
    state._save()

    return report

@router.get("/daily")
async def list_reports(_=Depends(verify_token)):
    ''''''
    await handle_risk("L1", '')
    return {"reports": _get_reports()}

@router.get("/trend")
async def trend_analysis(_=Depends(verify_token)):
    ''''''
    await handle_risk("L1", '')
    reports = _get_reports()
    if len(reports) < 2:
        return {"trend": ",2"}
    recent = reports[:7]
    alert_counts = [r["data"].get("alerts_today", 0) for r in recent]
    avg = sum(alert_counts) / len(alert_counts)
    return {
        "days": len(recent),
        "avg_daily_alerts": round(avg, 1),
        "alert_trend": " " if alert_counts[0] > alert_counts[-1] else " " if alert_counts[0] < alert_counts[-1] else " ",
        "latest_alerts": alert_counts[0],
    }
