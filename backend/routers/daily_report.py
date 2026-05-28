"""每日运营早报 — 自动生成+多渠道推送"""
from datetime import datetime
from fastapi import APIRouter, Depends
from auth import verify_token
from state import state
from risk import handle_risk

router = APIRouter(prefix="/agent/report", tags=["DailyReport"])

@router.get("/daily")
async def daily_report(_=Depends(verify_token)):
    """生成每日运营早报"""
    await handle_risk("L1", "生成每日早报")
    import psutil
    mem = psutil.virtual_memory()
    disk = psutil.disk_usage("/")
    cpu = psutil.cpu_percent(interval=0.3)
    domains = state._data.get("rotation_domains", [])
    active = sum(1 for d in domains if d.get("active"))
    pending = state._data.get("pending_approvals", [])
    blacklist = state._data.get("ip_blacklist", [])
    score = 100
    if mem.percent > 80: score -= 15
    if disk.percent > 85: score -= 15
    if cpu > 80: score -= 10
    if pending: score -= 5 * min(len(pending), 4)
    score = max(0, score)
    report = {"date": datetime.now().strftime("%Y-%m-%d"), "time": datetime.now().strftime("%H:%M"),
              "health_score": score, "health_level": "优秀" if score>85 else "良好" if score>70 else "需关注" if score>50 else "危险",
              "server": {"cpu":f"{cpu}%","memory":f"{mem.percent}%","disk":f"{disk.percent}%"},
              "domains":{"total":len(domains),"active":active,"offline":len(domains)-active},
              "pending_approvals":len(pending),"blocked_ips":len(blacklist),"suggestions":[]}
    if mem.percent > 80: report["suggestions"].append(f"内存使用{mem.percent}%，建议释放")
    if disk.percent > 85: report["suggestions"].append(f"磁盘使用{disk.percent}%，建议清理")
    if cpu > 80: report["suggestions"].append(f"CPU负载{cpu}%，建议检查")
    if pending: report["suggestions"].append(f"{len(pending)}个审批待处理")
    if not report["suggestions"]: report["suggestions"].append("一切正常")
    state.append_data("daily_reports", report, 365)
    return {"ok": True, **report}

@router.get("/daily/history")
async def daily_history(_=Depends(verify_token)):
    return {"ok": True, "reports": state._data.get("daily_reports", [])[-30:]}
