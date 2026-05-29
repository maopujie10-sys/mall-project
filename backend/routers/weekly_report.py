锘?""AI杩愯惀鍛ㄦ姤 鈥?鑷姩姹囨€绘湰鍛ㄨ鍗?閿€鍞/Top鍟嗗搧/寮傚父/娴侀噺/绔炲搧鍔ㄦ€?""
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
    """鐢熸垚鏈懆杩愯惀鍛ㄦ姤"""
    await handle_risk("L2", "鐢熸垚杩愯惀鍛ㄦ姤")
    today = datetime.now()
    week_start = (today - timedelta(days=today.weekday())).strftime("%Y-%m-%d")
    week_num = today.isocalendar()[1]
    now = today.strftime("%Y-%m-%d %H:%M")

    data = {"week": week_num, "week_start": week_start, "period": f"{week_start} ~ {today.strftime('%Y-%m-%d')}"}

    # 璁㈠崟鏁版嵁
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

    # 绯荤粺鍋ュ悍
    import psutil
    data["cpu"] = f"{psutil.cpu_percent(interval=0.3)}%"
    data["memory"] = f"{psutil.virtual_memory().percent}%"
    data["disk"] = f"{psutil.disk_usage('/').percent}%"

    # 鏈懆鍛婅
    alerts = state._data.get("alerts", [])
    week_alerts = [a for a in alerts if a.get("time","")[:10] >= week_start]
    data["alerts_this_week"] = len(week_alerts)
    data["alerts_p1"] = sum(1 for a in week_alerts if "P1" in str(a.get("level","")))

    # 鏈懆瀹㈡湇娑堟伅
    msgs = state._data.get("customer_messages", [])
    week_msgs = [m for m in msgs if m.get("time","")[:10] >= week_start]
    data["customer_messages"] = len(week_msgs)

    # 寮傚父浜嬩欢
    try:
        with open("memory/anomalies.json", "r") as f:
            import json
            anoms = json.load(f)
            week_anoms = [a for a in anoms if a.get("detected_at","")[:10] >= week_start]
            data["anomalies"] = len(week_anoms)
            data["anomalies_resolved"] = sum(1 for a in week_anoms if a.get("status") == "resolved")
    except Exception:
        data["anomalies"] = 0
        data["anomalies_resolved"] = 0

    # 閲囬泦鍟嗗搧
    scraped = state._data.get("scraped_products", [])
    week_scraped = [s for s in scraped if s.get("crawled_at","")[:10] >= week_start]
    data["scraped_products"] = len(week_scraped)
    data["scraped_imported"] = sum(1 for s in week_scraped if s.get("status")=="imported")

    # 鍩燂拷锟斤拷杞€?
    domains = state._data.get("rotation_domains", [])
    data["active_domains"] = sum(1 for d in domains if d.get("active"))
    data["total_domains"] = len(domains)

    # 姣忔棩鎶ュ憡姹囨€?
    daily_reports = state._data.get("daily_reports", [])
    week_dailies = [r for r in daily_reports if r.get("date","") >= week_start]
    avg_health = sum(r.get("health_score",100) for r in week_dailies) / max(len(week_dailies), 1)
    data["avg_health_score"] = round(avg_health, 1)

    # AI鐢熸垚鎽樿
    summary = (
        f"馃搳 绗瑊week_num}鍛ㄨ繍钀ュ懆鎶?({data['period']})\n"
        f"鈹佲攣鈹佲攣鈹佲攣鈹佲攣鈹佲攣鈹佲攣鈹佲攣鈹佲攣鈹佲攣\n"
        f"馃摝 璁㈠崟: {data['orders_total']} | 鍟嗗搧: {data['products_total']} | 鐢ㄦ埛: {data['users_total']}\n"
        f"馃枼锔?CPU: {data['cpu']} | 鍐呭瓨: {data['memory']} | 纾佺洏: {data['disk']}\n"
        f"鈿狅笍 鏈懆鍛婅: {data['alerts_this_week']} (P1: {data['alerts_p1']})\n"
        f"馃┖ 寮傚父: {data['anomalies']} | 宸茶В鍐? {data['anomalies_resolved']}\n"
        f"馃挰 瀹㈡湇娑堟伅: {data['customer_messages']}\n"
        f"馃暦锔?閲囬泦鍟嗗搧: {data['scraped_products']} | 宸插鍏? {data['scraped_imported']}\n"
        f"馃寪 娲昏穬鍩熷悕: {data['active_domains']}/{data['total_domains']}\n"
        f"鉂わ笍 骞冲潎鍋ュ悍鍒? {data['avg_health_score']}/100"
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
    """鏌ョ湅鍘嗗彶鍛ㄦ姤"""
    await handle_risk("L1", "鏌ョ湅杩愯惀鍛ㄦ姤")
    return {"reports": _get_weekly_reports()}

@router.get("/weekly/latest")
async def latest_weekly_report(_=Depends(verify_token)):
    """鏌ョ湅鏈€鏂板懆鎶?""
    reports = _get_weekly_reports()
    return {"report": reports[0] if reports else None}
