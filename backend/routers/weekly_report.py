"""AI -- //Top///"""
import httpx
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends
from auth import verify_token
from state import state
from risk import handle_risk

router = APIRouter(prefix="/report", tags=["WeeklyReport"])

def _get_weekly_reports():
    return state._data.setdefault("weekly_reports", [])

@router.post("/weekly")
async def generate_weekly_report(_=Depends(verify_token)):
    ''''''
    await handle_risk("L2", '')
    today = datetime.now()
    week_start = (today - timedelta(days=today.weekday())).strftime("%Y-%m-%d")
    week_num = today.isocalendar()[1]
    now = today.strftime("%Y-%m-%d %H:%M")

    data = {"week": week_num, "week_start": week_start, "period": f"{week_start} ~ {today.strftime('%Y-%m-%d')}"}

    
    from config import MALL_BASE_URL
    async with httpx.AsyncClient(timeout=10) as c:
        try:
            r = await c.get(f"{MALL_BASE_URL}/api/orders", params={"page":1,"size":1})
            data["orders_total"] = r.json().get("total", 0) if r.status_code == 200 else 0
        except: data["orders_total"] = 0

        try:
            r = await c.get(f"{MALL_BASE_URL}/api/products", params={"page":1,"size":1})
            data["products_total"] = r.json().get("total", 0) if r.status_code == 200 else 0
        except: data["products_total"] = 0

        try:
            r = await c.get(f"{MALL_BASE_URL}/api/users", params={"page":1,"size":1})
            data["users_total"] = r.json().get("total", 0) if r.status_code == 200 else 0
        except: data["users_total"] = 0

    
    import psutil
    data["cpu"] = f"{psutil.cpu_percent(interval=0.3)}%"
    data["memory"] = f"{psutil.virtual_memory().percent}%"
    data["disk"] = f"{psutil.disk_usage('/').percent}%"

    
    alerts = state._data.get("alerts", [])
    week_alerts = [a for a in alerts if a.get("time",'')[:10] >= week_start]
    data["alerts_this_week"] = len(week_alerts)
    data["alerts_p1"] = sum(1 for a in week_alerts if "P1" in str(a.get("level",'')))

    
    msgs = state._data.get("customer_messages", [])
    week_msgs = [m for m in msgs if m.get("time",'')[:10] >= week_start]
    data["customer_messages"] = len(week_msgs)

    
    try:
        with open("memory/anomalies.json", "r") as f:
            import json
            anoms = json.load(f)
            week_anoms = [a for a in anoms if a.get("detected_at",'')[:10] >= week_start]
            data["anomalies"] = len(week_anoms)
            data["anomalies_resolved"] = sum(1 for a in week_anoms if a.get("status") == "resolved")
    except Exception:
        data["anomalies"] = 0
        data["anomalies_resolved"] = 0

    
    scraped = state._data.get("scraped_products", [])
    week_scraped = [s for s in scraped if s.get("crawled_at",'')[:10] >= week_start]
    data["scraped_products"] = len(week_scraped)
    data["scraped_imported"] = sum(1 for s in week_scraped if s.get("status")=="imported")

    
    domains = state._data.get("rotation_domains", [])
    data["active_domains"] = sum(1 for d in domains if d.get("active"))
    data["total_domains"] = len(domains)

    
    daily_reports = state._data.get("daily_reports", [])
    week_dailies = [r for r in daily_reports if r.get("date",'') >= week_start]
    avg_health = sum(r.get("health_score",100) for r in week_dailies) / max(len(week_dailies), 1)
    data["avg_health_score"] = round(avg_health, 1)

    # AI
    summary = (
        f" {week_num} ({data['period']})\n"
        f"\n"
        f" : {data['orders_total']} | : {data['products_total']} | : {data['users_total']}\n"
        f" CPU: {data['cpu']} | : {data['memory']} | : {data['disk']}\n"
        f" : {data['alerts_this_week']} (P1: {data['alerts_p1']})\n"
        f" : {data['anomalies']} | : {data['anomalies_resolved']}\n"
        f" : {data['customer_messages']}\n"
        f" : {data['scraped_products']} | : {data['scraped_imported']}\n"
        f" : {data['active_domains']}/{data['total_domains']}\n"
        f" : {data['avg_health_score']}/100"
    )

    report = {
        "id": f"week-{week_num}",
        "week": week_num,
        "date": week_start,
        "generated_at": now,
        "data": data,
        "summary": summary,
    }

    reports = _get_weekly_reports()
    reports.insert(0, report)
    if len(reports) > 12: reports[:] = reports[:12]
    state._save()

    return {"ok": True, "report": report}

@router.get("/weekly")
async def list_weekly_reports(_=Depends(verify_token)):
    ''''''
    await handle_risk("L1", '')
    return {"reports": _get_weekly_reports()}

@router.get("/weekly/latest")
async def latest_weekly_report(_=Depends(verify_token)):
    ''''''
    reports = _get_weekly_reports()
    return {"report": reports[0] if reports else None}
