"""审计日志 — 全量操作追踪/查询/导出"""
from datetime import datetime
from fastapi import APIRouter, Depends, Query
from auth import verify_token
from risk import handle_risk
from state import state

router = APIRouter(prefix="/audit", tags=["Audit"])

MAX_LOG = 500


def log_action(action: str, target: str, detail: str = "", risk: str = "L1", user: str = "AI") -> dict:
    """记录审计日志（其他模块可调用）"""
    entry = {
        "id": datetime.now().strftime("%Y%m%d%H%M%S%f")[:-3],
        "time": datetime.now().isoformat(),
        "action": action,
        "target": target,
        "detail": detail[:300],
        "risk": risk,
        "user": user,
    }
    logs = state._data.setdefault("audit_logs", [])
    logs.insert(0, entry)
    if len(logs) > MAX_LOG:
        state._data["audit_logs"] = logs[:MAX_LOG]
    state._save()
    return entry


@router.get("")
async def get_audit_logs(
    page: int = Query(1, ge=1),
    size: int = Query(50, ge=1, le=200),
    action: str = "",
    risk: str = "",
    date_from: str = "",
    date_to: str = "",
    _=Depends(verify_token)
):
    """查询审计日志，支持分页和过滤"""
    await handle_risk("L1", "查看审计日志")
    logs = state._data.get("audit_logs", [])
    # 过滤
    if action:
        logs = [l for l in logs if action.lower() in l["action"].lower()]
    if risk:
        logs = [l for l in logs if l["risk"] == risk]
    if date_from:
        logs = [l for l in logs if l["time"] >= date_from]
    if date_to:
        logs = [l for l in logs if l["time"] <= date_to]
    total = len(logs)
    start = (page - 1) * size
    return {
        "ok": True,
        "logs": logs[start:start + size],
        "total": total,
        "page": page,
        "size": size,
        "pages": (total + size - 1) // size,
    }


@router.get("/stats")
async def audit_stats(_=Depends(verify_token)):
    """审计统计"""
    await handle_risk("L1", "查看审计统计")
    logs = state._data.get("audit_logs", [])
    today = datetime.now().strftime("%Y-%m-%d")
    today_logs = [l for l in logs if l["time"].startswith(today)]
    action_count = {}
    risk_count = {}
    for l in logs:
        action_count[l["action"]] = action_count.get(l["action"], 0) + 1
        risk_count[l["risk"]] = risk_count.get(l["risk"], 0) + 1
    return {
        "ok": True,
        "total": len(logs),
        "today": len(today_logs),
        "top_actions": sorted(action_count.items(), key=lambda x: -x[1])[:10],
        "risk_distribution": risk_count,
    }
