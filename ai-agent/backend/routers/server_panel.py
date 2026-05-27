"""服务器监控 — CPU/内存/磁盘/端口/进程"""
import os
import psutil
from fastapi import APIRouter, Depends
from main import verify_token

router = APIRouter(prefix="/server", tags=["Server"])


@router.get("/status")
async def server_status(_=Depends(verify_token)):
    """CPU / 内存 / 磁盘 / 负载"""
    cpu = psutil.cpu_percent(interval=0.3)
    cpu_count = psutil.cpu_count()
    mem = psutil.virtual_memory()
    disk = psutil.disk_usage("/")
    load = os.getloadavg()

    return {
        "cpu": round(cpu, 1),
        "cpuCores": cpu_count,
        "memory": round(mem.percent, 1),
        "memUsed": f"{mem.used // (1024**3)} GB",
        "memTotal": f"{mem.total // (1024**3)} GB",
        "disk": round(disk.percent, 1),
        "diskUsed": f"{disk.used // (1024**3)} GB",
        "diskTotal": f"{disk.total // (1024**3)} GB",
        "loadAvg": f"{load[0]:.2f} / {load[1]:.2f} / {load[2]:.2f}",
        "systems": [
            {"name": "Nginx", "icon": "Connection", "online": _proc_running("nginx"), "info": "反向代理"},
            {"name": "Tomcat/Java", "icon": "Service", "online": _proc_running("java"), "info": "商城后端"},
            {"name": "MySQL", "icon": "Coin", "online": _proc_running("mysqld") or _proc_running("mariadb"), "info": ":3306"},
            {"name": "Redis", "icon": "Odometer", "online": _proc_running("redis-server"), "info": ":6379"},
            {"name": "Agent", "icon": "Cpu", "online": True, "info": ":9000"},
        ],
    }


@router.get("/disk")
async def disk_info(_=Depends(verify_token)):
    partitions = []
    for p in psutil.disk_partitions():
        try:
            usage = psutil.disk_usage(p.mountpoint)
            partitions.append({
                "device": p.device,
                "mount": p.mountpoint,
                "fstype": p.fstype,
                "total": f"{usage.total // (1024**3)} GB",
                "used": f"{usage.used // (1024**3)} GB",
                "free": f"{usage.free // (1024**3)} GB",
                "percent": round(usage.percent, 1),
            })
        except PermissionError:
            pass
    return {"partitions": partitions}


@router.get("/ports")
async def port_status(_=Depends(verify_token)):
    ports = [
        {"service": "HTTP", "port": 80, "protocol": "TCP", "listening": _port_listening(80)},
        {"service": "HTTPS", "port": 443, "protocol": "TCP", "listening": _port_listening(443)},
        {"service": "Java Backend", "port": 8080, "protocol": "TCP", "listening": _port_listening(8080)},
        {"service": "Agent", "port": 9000, "protocol": "TCP", "listening": _port_listening(9000)},
        {"service": "MySQL", "port": 3306, "protocol": "TCP", "listening": _port_listening(3306)},
        {"service": "Redis", "port": 6379, "protocol": "TCP", "listening": _port_listening(6379)},
        {"service": "Vite Dev", "port": 5173, "protocol": "TCP", "listening": _port_listening(5173)},
    ]
    return ports


@router.get("/processes")
async def process_list(_=Depends(verify_token)):
    procs = []
    key_names = {"nginx", "java", "mysqld", "mariadb", "redis-server", "python", "uvicorn", "node"}
    for p in psutil.process_iter(["pid", "name", "cpu_percent", "memory_percent", "status"]):
        try:
            info = p.info
            name = info.get("name", "")
            if not name:
                continue
            # Include key processes + top CPU consumers
            is_key = any(k in name.lower() for k in key_names)
            if is_key or info.get("cpu_percent", 0) > 5:
                procs.append({
                    "name": name,
                    "pid": info["pid"],
                    "cpu": round(info.get("cpu_percent", 0), 1),
                    "mem": round(info.get("memory_percent", 0), 1),
                    "status": "running" if info.get("status") == "running" else str(info.get("status", "")),
                })
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue

    procs.sort(key=lambda x: x["cpu"], reverse=True)
    return procs[:30]


def _proc_running(name: str) -> bool:
    for p in psutil.process_iter(["name"]):
        try:
            if name.lower() in (p.info.get("name") or "").lower():
                return True
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    return False


def _port_listening(port: int) -> bool:
    for conn in psutil.net_connections(kind="inet"):
        if conn.status == "LISTEN" and conn.laddr.port == port:
            return True
    return False
