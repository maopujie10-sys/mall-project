"""可观测性 — Prometheus指标导出 + 系统资源实时监控"""
import time, psutil
from datetime import datetime
from fastapi import APIRouter, Depends
from auth import verify_token

router = APIRouter(prefix="/agent/observability", tags=["Observability"])

# 请求统计
_request_count = {"total": 0, "errors": 0, "by_path": {}}
_start_time = time.time()

def record_request(path: str, is_error: bool = False):
    """记录请求"""
    _request_count["total"] += 1
    if is_error:
        _request_count["errors"] += 1
    _request_count["by_path"][path] = _request_count["by_path"].get(path, 0) + 1

@router.get("/metrics")
async def prometheus_metrics():
    """Prometheus格式指标导出"""
    uptime = int(time.time() - _start_time)
    mem = psutil.virtual_memory()
    disk = psutil.disk_usage("/")
    cpu = psutil.cpu_percent(interval=0.1)
    net = psutil.net_io_counters()
    
    metrics = []
    metrics.append("# HELP friday_uptime_seconds Service uptime in seconds")
    metrics.append("# TYPE friday_uptime_seconds gauge")
    metrics.append(f"friday_uptime_seconds {uptime}")
    
    metrics.append("# HELP friday_requests_total Total requests")
    metrics.append("# TYPE friday_requests_total counter")
    metrics.append(f"friday_requests_total {_request_count['total']}")
    
    metrics.append("# HELP friday_errors_total Total errors")
    metrics.append("# TYPE friday_errors_total counter")
    metrics.append(f"friday_errors_total {_request_count['errors']}")
    
    metrics.append("# HELP friday_cpu_percent CPU usage")
    metrics.append("# TYPE friday_cpu_percent gauge")
    metrics.append(f"friday_cpu_percent {cpu}")
    
    metrics.append("# HELP friday_memory_used_bytes Memory used")
    metrics.append("# TYPE friday_memory_used_bytes gauge")
    metrics.append(f"friday_memory_used_bytes {mem.used}")
    
    metrics.append("# HELP friday_memory_total_bytes Memory total")
    metrics.append("# TYPE friday_memory_total_bytes gauge")
    metrics.append(f"friday_memory_total_bytes {mem.total}")
    
    metrics.append("# HELP friday_disk_used_bytes Disk used")
    metrics.append("# TYPE friday_disk_used_bytes gauge")
    metrics.append(f"friday_disk_used_bytes {disk.used}")
    
    metrics.append("# HELP friday_net_bytes_sent Network bytes sent")
    metrics.append("# TYPE friday_net_bytes_sent counter")
    metrics.append(f"friday_net_bytes_sent {net.bytes_sent}")
    
    from fastapi.responses import PlainTextResponse
    return PlainTextResponse("\n".join(metrics) + "\n")

@router.get("/dashboard")
async def system_dashboard(_=Depends(verify_token)):
    """系统实时监控面板数据"""
    mem = psutil.virtual_memory()
    disk = psutil.disk_usage("/")
    cpu_percent = psutil.cpu_percent(interval=0.3)
    load = psutil.getloadavg() if hasattr(psutil, 'getloadavg') else [0,0,0]
    net = psutil.net_io_counters()
    
    # Top 5 高CPU进程
    top_procs = []
    for p in sorted(psutil.process_iter(['pid','name','cpu_percent','memory_percent']), 
                    key=lambda x: x.info.get('cpu_percent', 0) or 0, reverse=True)[:5]:
        try:
            top_procs.append({
                "pid": p.info['pid'],
                "name": p.info['name'],
                "cpu": round(p.info.get('cpu_percent', 0) or 0, 1),
                "mem": round(p.info.get('memory_percent', 0) or 0, 1),
            })
        except Exception:
            pass
    
    return {
        "ok": True,
        "time": datetime.now().isoformat(),
        "uptime_seconds": int(time.time() - _start_time),
        "cpu": {
            "percent": cpu_percent,
            "cores": psutil.cpu_count(),
            "load_1m": round(load[0], 2),
            "load_5m": round(load[1], 2),
            "load_15m": round(load[2], 2),
        },
        "memory": {
            "total_gb": round(mem.total / (1024**3), 1),
            "used_gb": round(mem.used / (1024**3), 1),
            "available_gb": round(mem.available / (1024**3), 1),
            "percent": mem.percent,
        },
        "disk": {
            "total_gb": round(disk.total / (1024**3), 1),
            "used_gb": round(disk.used / (1024**3), 1),
            "free_gb": round(disk.free / (1024**3), 1),
            "percent": disk.percent,
        },
        "network": {
            "sent_mb": round(net.bytes_sent / (1024**2), 1),
            "recv_mb": round(net.bytes_recv / (1024**2), 1),
        },
        "requests": _request_count,
        "top_processes": top_procs,
        "error_rate": round(_request_count["errors"] / max(_request_count["total"], 1) * 100, 2),
    }
