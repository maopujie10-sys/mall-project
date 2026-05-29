"""杩愯惀鏃ユ姤 鈥?鑷姩鐢熸垚姣忔棩杩愯惀鏁版嵁鎶ュ憡"""
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
    """鐢熸垚浠婃棩杩愯惀鏃ユ姤"""
    await handle_risk("L2", "鐢熸垚杩愯惀鏃ユ姤")
    today = datetime.now().strftime("%Y-%m-%d")
    now = datetime.now().strftime("%H:%M:%S")

    # 鏀堕泦鍚勯」鏁版嵁
    data = {}

    # 鍟嗗煄鐘舵€?
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

    # 绯荤粺鐘舵€?
    data["agent_mode"] = state.mode
    data["pending_approvals"] = len(state.pending_approvals)
    data["tasks_today"] = len(state.tasks)
    data["alerts_unresolved"] = len([a for a in state._data.get("alerts", []) if not a.get("resolved")])

    # 瀹㈡湇鏁版嵁
    msgs = state._data.get("customer_messages", [])
    today_msgs = [m for m in msgs if today in m.get("time", "")]
    data["customer_messages_today"] = len(today_msgs)

    # 鍛婅鏁版嵁
    alerts = state._data.get("alerts", [])
    today_alerts = [a for a in alerts if today in a.get("time", "")]
    data["alerts_today"] = len(today_alerts)

    report = {
        "date": today,
        "generated_at": now,
        "data": data,
        "summary": (
            f"馃搳 {today} 杩愯惀鏃ユ姤\n"
            f"馃敡 妯″紡: {data['agent_mode']}\n"
            f"馃摝 璁㈠崟: {data.get('orders_total', 'N/A')} | 鍟嗗搧: {data.get('products_total', 'N/A')}\n"
            f"鈴?寰呭鎵? {data['pending_approvals']} | 浠婃棩鍛婅: {data['alerts_today']}\n"
            f"馃挰 瀹㈡湇娑堟伅: {data['customer_messages_today']}"
        ),
    }

    reports = _get_reports()
    reports.insert(0, report)
    if len(reports) > 30: reports[:] = reports[:30]
    state._save()

    return report

@router.get("/daily")
async def list_reports(_=Depends(verify_token)):
    """鏌ョ湅鍘嗗彶鏃ユ姤"""
    await handle_risk("L1", "鏌ョ湅杩愯惀鏃ユ姤")
    return {"reports": _get_reports()}

@router.get("/trend")
async def trend_analysis(_=Depends(verify_token)):
    """寮傚父瓒嬪娍鍒嗘瀽"""
    await handle_risk("L1", "寮傚父瓒嬪娍鍒嗘瀽")
    reports = _get_reports()
    if len(reports) < 2:
        return {"trend": "鏁版嵁涓嶈冻锛岃嚦灏戦渶瑕?澶╃殑鏃ユ姤鎵嶈兘鍒嗘瀽瓒嬪娍"}
    recent = reports[:7]
    alert_counts = [r["data"].get("alerts_today", 0) for r in recent]
    avg = sum(alert_counts) / len(alert_counts)
    return {
        "days": len(recent),
        "avg_daily_alerts": round(avg, 1),
        "alert_trend": "涓婂崌 猬嗭笍" if alert_counts[0] > alert_counts[-1] else "涓嬮檷 猬囷笍" if alert_counts[0] < alert_counts[-1] else "骞崇ǔ 鉃★笍",
        "latest_alerts": alert_counts[0],
    }
