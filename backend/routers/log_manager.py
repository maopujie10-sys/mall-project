"""日志集中管理 -- Docker/Nginx/应用日志统一查询"""
import os
import subprocess
from datetime import datetime
from fastapi import APIRouter, Depends, Query
from auth import verify_token
from risk import handle_risk

router = APIRouter(prefix="/agent/logs", tags=["LogManager"])

LOG_SOURCES = {
    "docker-ai": {"name": "Docker - AI后端", "type": "docker", "container": "ai-backend"},
    "docker-frontend": {"name": "Docker - AI前端", "type": "docker", "container": "ai-frontend"},
    "docker-mysql": {"name": "Docker - MySQL", "type": "docker", "container": "mysql56"},
    "docker-redis": {"name": "Docker - Redis", "type": "docker", "container": "redis"},
    "nginx-access": {"name": "Nginx - 访问日志", "type": "file", "path": "/usr/local/nginx/logs/access.log"},
    "nginx-error": {"name": "Nginx - 错误日志", "type": "file", "path": "/usr/local/nginx/logs/error.log"},
    "tomcat": {"name": "Tomcat - 应用日志", "type": "file", "path": "/opt/tomcat8/logs/catalina.out"},
    "app": {"name": "AI应用日志", "type": "file", "path": "/home/data/projects/mall/mall-project/mall-app/logs/app.log"},
}

@router.get("/sources")
async def list_sources(_=Depends(verify_token)):
    """列出可用的日志源"""
    sources = []
    for key, info in LOG_SOURCES.items():
        available = True
        size = "N/A"
        if info["type"] == "file":
            path = info["path"]
            if os.path.exists(path):
                size = f"{os.path.getsize(path) / 1024:.1f} KB"
            else:
                available = False
                size = "不可用"
        elif info["type"] == "docker":
            try:
                result = subprocess.run(["docker", "inspect", info["container"]], capture_output=True, timeout=5)
                available = result.returncode == 0
            except Exception:
                available = False
        sources.append({**info, "id": key, "available": available, "size": size})
    return {"ok": True, "sources": sources}

@router.get("/view")
async def view_logs(
    source: str = Query("app"),
    lines: int = Query(100, ge=1, le=500),
    filter_text: str = Query(""),
    level: str = Query(""),  # ERROR/WARN/INFO/DEBUG
    _=Depends(verify_token),
):
    """查看日志"""
    await handle_risk("L1", f"查看日志: {source}")
    
    if source not in LOG_SOURCES:
        return {"ok": False, "error": f"未知日志源: {source}"}
    
    info = LOG_SOURCES[source]
    raw_lines = []
    
    if info["type"] == "docker":
        try:
            cmd = ["docker", "logs", "--tail", str(lines), info["container"]]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
            raw_lines = result.stdout.strip().split("\n") + result.stderr.strip().split("\n")
        except Exception as e:
            return {"ok": False, "error": f"Docker日志读取失败: {str(e)[:100]}"}
    
    elif info["type"] == "file":
        path = info["path"]
        if not os.path.exists(path):
            return {"ok": False, "error": f"日志文件不存在: {path}"}
        try:
            with open(path, "r", encoding="utf-8", errors="ignore") as f:
                all_lines = f.readlines()
                raw_lines = [l.rstrip() for l in all_lines[-lines:]]
        except Exception as e:
            return {"ok": False, "error": f"文件读取失败: {str(e)[:100]}"}
    
    # 过滤
    filtered = []
    for line in raw_lines:
        if not line.strip():
            continue
        if filter_text and filter_text.lower() not in line.lower():
            continue
        if level:
            upper = line.upper()
            if level.upper() == "ERROR" and "ERROR" not in upper and "ERR" not in upper and "FAIL" not in upper and "FATAL" not in upper:
                continue
            if level.upper() == "WARN" and "WARN" not in upper and "WARNING" not in upper:
                continue
        filtered.append(line)
    
    # 分类统计
    stats = {"ERROR": 0, "WARN": 0, "INFO": 0, "DEBUG": 0, "OTHER": 0}
    for line in filtered:
        upper = line.upper()
        if "ERROR" in upper or "FATAL" in upper or "FAIL" in upper:
            stats["ERROR"] += 1
        elif "WARN" in upper:
            stats["WARN"] += 1
        elif "INFO" in upper:
            stats["INFO"] += 1
        elif "DEBUG" in upper:
            stats["DEBUG"] += 1
        else:
            stats["OTHER"] += 1
    
    return {
        "ok": True,
        "source": source,
        "source_name": info["name"],
        "total_raw": len(raw_lines),
        "total_filtered": len(filtered),
        "stats": stats,
        "lines": filtered[-lines:],
    }

@router.post("/search")
async def search_logs(
    source: str = Query("app"),
    keyword: str = Query(...),
    max_lines: int = Query(1000),
    _=Depends(verify_token),
):
    """全文搜索日志"""
    result = await view_logs(source=source, lines=max_lines, filter_text=keyword)
    return result

@router.get("/recent-errors")
async def recent_errors(hours: int = Query(24), _=Depends(verify_token)):
    """获取最近N小时的错误日志汇总"""
    await handle_risk("L1", "查看错误日志")
    all_errors = []
    for key, info in LOG_SOURCES.items():
        try:
            result = await view_logs(source=key, lines=200, level="ERROR")
            if result.get("ok"):
                for line in result.get("lines", []):
                    all_errors.append({"source": info["name"], "line": line})
        except Exception:
            pass
    
    return {
        "ok": True,
        "total_errors": len(all_errors),
        "by_source": {},
        "errors": all_errors[-50:],
    }
