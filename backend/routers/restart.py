"""Docker鏈嶅姟閲嶅惎 鈥?閫氳繃docker compose閲嶅惎瀹瑰櫒"""
from fastapi import APIRouter, Depends, HTTPException
from auth import verify_token
from risk import handle_risk
import subprocess

router = APIRouter(prefix="/agent", tags=["Restart"])

ALLOWED_SERVICES = {"mall-app", "mall-nginx", "mall-db", "mall-redis"}

@router.post("/restart/{service}")
async def restart_service(service: str, _=Depends(verify_token)):
    if service not in ALLOWED_SERVICES:
        raise HTTPException(400, f"涓嶅厑璁搁噸鍚? {service}. 鍏佽: {ALLOWED_SERVICES}")

    await handle_risk("L2", f"閲嶅惎鏈嶅姟: {service}")

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
        raise HTTPException(504, "閲嶅惎瓒呮椂")
    except Exception as e:
        raise HTTPException(500, str(e))

