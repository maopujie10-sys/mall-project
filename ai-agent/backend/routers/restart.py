"""Docker服务重启 — 通过docker compose重启容器"""
from fastapi import APIRouter, Depends, HTTPException
from main import verify_token
import subprocess

router = APIRouter(prefix="/agent", tags=["Restart"])

ALLOWED_SERVICES = {"mall-app", "mall-nginx", "mall-db", "mall-redis"}

@router.post("/restart/{service}")
async def restart_service(service: str, _=Depends(verify_token)):
    if service not in ALLOWED_SERVICES:
        raise HTTPException(400, f"不允许重启: {service}. 允许: {ALLOWED_SERVICES}")

    try:
        result = subprocess.run(
            ["docker", "compose", "-f", "/home/data/project/new-mall/docker-compose.yml",
             "restart", service],
            capture_output=True, text=True, timeout=120
        )
        return {
            "service": service, "action": "restarted",
            "stdout": result.stdout[-500:], "stderr": result.stderr[-500:]
        }
    except subprocess.TimeoutExpired:
        return {"service": service, "action": "timeout", "error": "重启超时120s"}
    except FileNotFoundError:
        return {"service": service, "action": "failed", "error": "docker compose 未找到"}

@router.get("/restart")
async def list_restartable(_=Depends(verify_token)):
    return {"allowed_services": list(ALLOWED_SERVICES)}
