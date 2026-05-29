"""请求追踪查看API — 实时链路追踪面板"""
from fastapi import APIRouter, Depends, Query
from auth import verify_token, require_role
from tools.trace import get_recent_traces, get_trace_stats

router = APIRouter(prefix="/agent/trace", tags=["Trace"])


@router.get("/recent")
async def trace_recent(limit: int = Query(100, ge=1, le=500), status: str = Query(""), _=Depends(verify_token)):
    """最近请求追踪记录"""
    traces = get_recent_traces(limit, status_filter=status)
    return {"ok": True, "total": len(traces), "traces": traces}


@router.get("/stats")
async def trace_stats(_=Depends(verify_token)):
    """追踪统计 — 错误率/响应时间分布"""
    return {"ok": True, "stats": get_trace_stats()}


@router.get("/slow")
async def trace_slow(limit: int = Query(20), _=Depends(verify_token)):
    """慢请求列表"""
    slow = get_recent_traces(500, status_filter="slow")
    errors = get_recent_traces(500, status_filter="error")
    return {"ok": True, "slow": slow[-limit:], "errors": errors[-limit:]}
