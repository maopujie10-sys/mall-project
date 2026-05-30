""" API  ++"""
from fastapi import APIRouter, Depends
from tools.logger import get_logger
from auth import verify_token

router = APIRouter(prefix="/agent/emergency", tags=["Emergency"])
logger = get_logger("emergency")

@router.get("/diagnose")
async def emergency_diagnose(_=Depends(verify_token)):
    ''''''
    import psutil, os, time
    result = {
        "ok": True, "timestamp": time.time(),
        "cpu": {"percent": psutil.cpu_percent(interval=0.5), "cores": psutil.cpu_count()},
        "memory": {"total": psutil.virtual_memory().total>>20, "used": psutil.virtual_memory().used>>20, "percent": psutil.virtual_memory().percent},
        "disk": {"total": psutil.disk_usage("/").total>>30, "used": psutil.disk_usage("/").used>>30, "percent": psutil.disk_usage("/").percent},
        "network": {"connections": len(psutil.net_connections())},
        "processes": len(psutil.pids())
    }
    
    issues = []
    if result["cpu"]["percent"] > 90: issues.append({"level":"critical","msg":"CPU>90%","fix":"Docker/"})
    if result["memory"]["percent"] > 90: issues.append({"level":"critical","msg":">90%","fix":''})
    if result["disk"]["percent"] > 85: issues.append({"level":"warning","msg":">85%","fix":"Docker: docker system prune -af"})
    result["issues"] = issues
    result["status"] = "healthy" if not issues else ("critical" if any(i["level"]=="critical" for i in issues) else "warning")
    return result

@router.post("/quick-fix")
async def emergency_quick_fix(action: str = "restart_ai", _=Depends(verify_token)):
    ''''''
    import subprocess
    fixes = {
        "restart_ai": "docker restart mall-ai-agent",
        "restart_nginx": "nginx -s reload",
        "clean_docker": "docker system prune -af",
        "restart_mysql": "docker restart mall-mysql",
        "check_disk": "df -h /",
    }
    if action not in fixes:
        return {"ok":False,"error":'',"available":list(fixes.keys())}
    try:
        r = subprocess.run(fixes[action].split(), capture_output=True, text=True, timeout=60)
        return {"ok":True,"action":action,"stdout":r.stdout[:500],"stderr":r.stderr[:200]}
    except Exception as e:
        return {"ok":False,"error":str(e)}