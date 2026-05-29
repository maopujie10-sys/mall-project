锘?""鍏ㄩ摼璺仴搴锋鏌?鈥?MySQL/Redis/Docker/Nginx/Tomcat/纾佺洏/鍐呭瓨"""
import socket, os, subprocess, asyncio
from datetime import datetime
from fastapi import APIRouter

router = APIRouter(prefix="/agent/health", tags=["Health"])

async def _check_tcp(host: str, port: int, timeout: float = 2) -> dict:
    """TCP绔彛杩為€氭€ф鏌?""
    try:
        _, writer = await asyncio.wait_for(
            asyncio.open_connection(host, port), timeout=timeout
        )
        writer.close()
        return {"ok": True, "latency_ms": 0}
    except Exception as e:
        return {"ok": False, "error": str(e)[:80]}

async def _check_mysql() -> dict:
    """MySQL杩炴帴+鏌ヨ妫€鏌?""
    try:
        import pymysql
        from config import DB_CONFIG
        conn = pymysql.connect(
            host=DB_CONFIG["host"], port=DB_CONFIG["port"],
            user=DB_CONFIG["user"], password=DB_CONFIG["password"],
            database=DB_CONFIG["name"], connect_timeout=3
        )
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        cursor.close()
        conn.close()
        return {"ok": True, "host": f"{DB_CONFIG['host']}:{DB_CONFIG['port']}"}
    except Exception as e:
        return {"ok": False, "error": str(e)[:100]}

async def _check_redis() -> dict:
    """Redis杩炴帴妫€鏌?""
    try:
        from config import REDIS_DSN
        import redis
        r = redis.from_url(REDIS_DSN, socket_connect_timeout=3)
        r.ping()
        r.close()
        return {"ok": True}
    except Exception as e:
        return {"ok": False, "error": str(e)[:80]}

async def _check_docker() -> dict:
    """Docker鏈嶅姟+瀹瑰櫒鐘舵€?""
    try:
        result = subprocess.run(["docker", "ps", "--format", "{{.Names}} {{.Status}}"],
            capture_output=True, text=True, timeout=5)
        if result.returncode != 0:
            return {"ok": False, "error": "Docker瀹堟姢杩涚▼寮傚父"}
        containers = []
        for line in result.stdout.strip().split("\n"):
            if line:
                parts = line.split(" ", 1)
                containers.append({"name": parts[0], "status": parts[1] if len(parts) > 1 else ""})
        stopped = [c for c in containers if "Up" not in c["status"]]
        return {"ok": True, "total": len(containers), "running": len(containers) - len(stopped), "stopped": [c["name"] for c in stopped]}
    except FileNotFoundError:
        return {"ok": True, "note": "Docker鏈畨瑁?}
    except Exception as e:
        return {"ok": False, "error": str(e)[:80]}

async def _check_nginx() -> dict:
    """Nginx绔彛妫€鏌?""
    return await _check_tcp("127.0.0.1", 80)

async def _check_tomcat() -> dict:
    """Tomcat绔彛妫€鏌?""
    return await _check_tcp("127.0.0.1", 8080)

async def _check_disk() -> dict:
    """纾佺洏浣跨敤鐜?""
    try:
        import psutil
        disk = psutil.disk_usage("/")
        return {"ok": disk.percent < 90, "used_pct": disk.percent, "free_gb": round(disk.free / (1024**3), 1)}
    except Exception as e:
        return {"ok": False, "error": str(e)[:80]}

async def _check_memory() -> dict:
    """鍐呭瓨浣跨敤鐜?""
    try:
        import psutil
        mem = psutil.virtual_memory()
        return {"ok": mem.percent < 90, "used_pct": mem.percent, "available_gb": round(mem.available / (1024**3), 1)}
    except Exception as e:
        return {"ok": False, "error": str(e)[:80]}

@router.get("")
async def health_check():
    """鍩虹鍋ュ悍妫€鏌?""
    return {"status": "ok", "service": "TikTokMall Agent", "version": "1.0.0", "time": datetime.now().isoformat()}

@router.get("/full")
async def full_health_check():
    """鍏ㄩ摼璺仴搴锋鏌?鈥?鎵€鏈変緷璧栭」"""
    results = await asyncio.gather(
        _check_mysql(), _check_redis(), _check_docker(),
        _check_nginx(), _check_tomcat(), _check_disk(), _check_memory(),
        return_exceptions=True
    )
    
    names = ["mysql", "redis", "docker", "nginx", "tomcat", "disk", "memory"]
    checks = {}
    all_ok = True
    
    for name, result in zip(names, results):
        if isinstance(result, Exception):
            checks[name] = {"ok": False, "error": str(result)[:100]}
            all_ok = False
        else:
            checks[name] = result
            if not result.get("ok", False):
                all_ok = False
    
    return {
        "status": "healthy" if all_ok else "degraded",
        "service": "TikTokMall Agent",
        "time": datetime.now().isoformat(),
        "checks": checks,
        "healthy": all_ok,
    }

@router.get("/simple")
async def simple_health():
    """绠€鍗曞仴搴锋鏌?渚汥ocker healthcheck)"""
    return {"status": "ok"}
