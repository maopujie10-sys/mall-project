"""仪表盘API — 实时指标采集/历史趋势/系统健康分"""
import os, time
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends
from auth import verify_token
from risk import handle_risk
from tools.cache import cached
from state import state

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@cached('dashboard', ttl=60)
async def collect_metrics() -> dict:
    """采集当前系统指标快照"""
    import psutil
    cpu = psutil.cpu_percent(interval=0.3)
    mem = psutil.virtual_memory()
    disk = psutil.disk_usage("/")
    try:
        load = os.getloadavg()
    except Exception:
        load = [0, 0, 0]
    return {
        "time": datetime.now().isoformat(),
        "cpu": round(cpu, 1),
        "memory_percent": round(mem.percent, 1),
        "memory_used_gb": round(mem.used / (1024**3), 1),
        "memory_total_gb": round(mem.total / (1024**3), 1),
        "disk_percent": round(disk.percent, 1),
        "disk_used_gb": round(disk.used / (1024**3), 1),
        "disk_total_gb": round(disk.total / (1024**3), 1),
        "load_1m": round(load[0], 2),
        "uptime_days": round((time.time() - psutil.boot_time()) / 86400, 1),
    }


@router.get("/metrics")
async def get_current_metrics(_=Depends(verify_token)):
    """获取当前系统指标"""
    return {"ok": True, "metrics": await collect_metrics()}


@router.get("/history")
@cached('dashboard', ttl=60)
async def get_metrics_history(points: int = 60, _=Depends(verify_token)):
    """获取历史指标趋势"""
    history = state._data.get("metrics_history", [])
    return {"ok": True, "history": history[-points:], "total": len(history)}


@router.get("/health-score")
async def get_health_score(_=Depends(verify_token)):
    """计算系统健康分 (0-100)"""
    m = await collect_metrics()
    score = 100
    if m["cpu"] > 80: score -= 20
    elif m["cpu"] > 60: score -= 10
    if m["memory_percent"] > 80: score -= 20
    elif m["memory_percent"] > 60: score -= 10
    if m["disk_percent"] > 80: score -= 20
    elif m["disk_percent"] > 60: score -= 10
    tasks = state._data.get("tasks", [])
    pending = sum(1 for t in tasks if isinstance(t, dict) and t.get("status") == "pending")
    failed = sum(1 for t in tasks if isinstance(t, dict) and t.get("status") == "failed")
    score -= pending * 2
    score -= failed * 5
    mode = getattr(state, "mode", "ai_control")
    if mode in ("human_control", "human-control"):
        score -= 30
    return {
        "ok": True,
        "score": max(0, min(100, score)),
        "level": "excellent" if score >= 80 else "good" if score >= 60 else "warning" if score >= 40 else "critical",
        "metrics": m,
    }


@router.post("/record")
async def record_metrics(_=Depends(verify_token)):
    """手动记录一次指标快照"""
    m = await collect_metrics()
    history = state._data.setdefault("metrics_history", [])
    history.append(m)
    if len(history) > 500:
        state._data["metrics_history"] = history[-500:]
    state._save()
    return {"ok": True, "recorded": m}
