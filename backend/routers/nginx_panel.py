"""Nginx 状态检查 — 进程/配置/日志/重载"""
from fastapi import APIRouter, Depends, HTTPException
from auth import verify_token
from executor import execute
from risk import handle_risk

router = APIRouter(prefix="/nginx", tags=["Nginx"])

@router.get("/status")
async def nginx_status(_=Depends(verify_token)):
    await handle_risk("L1", "检查Nginx状态")
    result = await execute("systemctl status nginx")
    if not result["success"]:
        result = await execute("pgrep -a nginx 2>/dev/null || systemctl is-active nginx 2>/dev/null || echo unknown")
    return {
        "running": "active (running)" in result["stdout"] or "nginx" in result["stdout"],
        "detail": result["stdout"][:500],
    }

@router.get("/test")
async def nginx_test(_=Depends(verify_token)):
    await handle_risk("L1", "测试Nginx配置")
    result = await execute("nginx -t")
    return {
        "ok": result["success"],
        "output": (result["stdout"] or result["stderr"])[:500],
    }

@router.get("/logs")
async def nginx_logs(_=Depends(verify_token), lines: int = 50, type: str = "error"):
    await handle_risk("L1", "查看Nginx日志", f"{type}/{lines}行")
    path = "/var/log/nginx/error.log" if type == "error" else "/var/log/nginx/access.log"
    result = await execute(f"tail -n {lines} {path}")
    return {
        "type": type,
        "lines": lines,
        "content": result["stdout"],
        "truncated": len(result["stdout"]) >= 2000,
    }

@router.post("/reload")
async def nginx_reload(_=Depends(verify_token)):
    risk = await handle_risk("L3", "重载Nginx")
    if not risk["allowed"]:
        return risk
    result = await execute("nginx -s reload")
    return {
        "reloaded": result["success"],
        "output": (result["stdout"] or result["stderr"])[:500],
    }


