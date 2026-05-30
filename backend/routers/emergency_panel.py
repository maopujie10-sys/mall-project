"""急救面板 API — 一键诊断+修复+重启"""
from fastapi import APIRouter, Depends
from tools.logger import get_logger
from auth import verify_token

router = APIRouter(prefix="/agent/emergency", tags=["Emergency"])
logger = get_logger("emergency")

@router.get("/diagnose")
async def emergency_diagnose(_=Depends(verify_token)):
    """一键全系统诊断"""
    import psutil, os, time
    result = {
        "ok": True, "timestamp": time.time(),
        "cpu": {"percent": psutil.cpu_percent(interval=0.5), "cores": psutil.cpu_count()},
        "memory": {"total": psutil.virtual_memory().total>>20, "used": psutil.virtual_memory().used>>20, "percent": psutil.virtual_memory().percent},
        "disk": {"total": psutil.disk_usage("/").total>>30, "used": psutil.disk_usage("/").used>>30, "percent": psutil.disk_usage("/").percent},
        "network": {"connections": len(psutil.net_connections())},
        "processes": len(psutil.pids())
    }
    # 风险评估
    issues = []
    if result["cpu"]["percent"] > 90: issues.append({"level":"critical","msg":"CPU使用率>90%","fix":"检查Docker容器/后台任务"})
    if result["memory"]["percent"] > 90: issues.append({"level":"critical","msg":"内存>90%","fix":"重启高内存进程"})
    if result["disk"]["percent"] > 85: issues.append({"level":"warning","msg":"磁盘>85%","fix":"清理Docker缓存: docker system prune -af"})
    result["issues"] = issues
    result["status"] = "healthy" if not issues else ("critical" if any(i["level"]=="critical" for i in issues) else "warning")
    return result

@router.post("/quick-fix")
async def emergency_quick_fix(action: str = "restart_ai", _=Depends(verify_token)):
    """一键修复"""
    import subprocess
    fixes = {
        "restart_ai": "docker restart mall-ai-agent",
        "restart_nginx": "nginx -s reload",
        "clean_docker": "docker system prune -af",
        "restart_mysql": "docker restart mall-mysql",
        "check_disk": "df -h /",
    }
    if action not in fixes:
        return {"ok":False,"error":"未知操作","available":list(fixes.keys())}
    try:
        r = subprocess.run(fixes[action].split(), capture_output=True, text=True, timeout=60)
        return {"ok":True,"action":action,"stdout":r.stdout[:500],"stderr":r.stderr[:200]}
    except Exception as e:
        return {"ok":False,"error":str(e)}