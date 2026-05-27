"""服务器监控 — CPU/内存/磁盘/端口/进程"""
import os, psutil
import shutil
from fastapi import APIRouter, Depends
from auth import verify_token
from risk import handle_risk

router = APIRouter(prefix="/server", tags=["Server"])

@router.get("/status")
async def server_status(_=Depends(verify_token)):
    await handle_risk("L1", "查看服务器状态")
    cpu = psutil.cpu_percent(interval=0.3)
    mem = psutil.virtual_memory()
    disk = psutil.disk_usage("/")
    try:
        load = os.getloadavg()
    except Exception:
        load = [0, 0, 0]

    return {
        "cpu": round(cpu, 1),
        "cpu_count": psutil.cpu_count(),
        "memory": {
            "total_gb": round(mem.total / (1024**3), 1),
            "used_gb": round(mem.used / (1024**3), 1),
            "percent": mem.percent,
        },
        "disk": {
            "total_gb": round(disk.total / (1024**3), 1),
            "used_gb": round(disk.used / (1024**3), 1),
            "percent": disk.percent,
        },
        "load": {"1min": load[0], "5min": load[1], "15min": load[2]},
    }

@router.get("/ports")
async def server_ports(_=Depends(verify_token)):
    await handle_risk("L1", "查看服务器端口")
    ports = []
    for conn in psutil.net_connections():
        if conn.status == "LISTEN":
            ports.append({"port": conn.laddr.port, "pid": conn.pid})
    return {"listening": ports}

@router.get("/processes")
async def server_processes(_=Depends(verify_token)):
    await handle_risk("L1", "查看服务器进程")
    procs = []
    for p in psutil.process_iter(["pid", "name", "cpu_percent", "memory_percent"]):
        try:
            procs.append(p.info)
        except Exception:
            pass
    top = sorted(procs, key=lambda x: x.get("cpu_percent", 0) or 0, reverse=True)[:10]
    return {"top10": top}

@router.get("/disk")
async def server_disk(_=Depends(verify_token)):
    """查看磁盘使用详情"""
    await handle_risk("L1", "查看磁盘详情")
    disks = []
    for part in psutil.disk_partitions():
        try:
            usage = psutil.disk_usage(part.mountpoint)
            disks.append({
                "device": part.device,
                "mount": part.mountpoint,
                "fstype": part.fstype,
                "total_gb": round(usage.total / (1024**3), 1),
                "used_gb": round(usage.used / (1024**3), 1),
                "free_gb": round(usage.free / (1024**3), 1),
                "percent": usage.percent,
            })
        except Exception:
            pass
    return {"disks": disks}
