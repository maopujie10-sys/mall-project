''"Docker  -- //''"
import subprocess
from fastapi import APIRouter, Depends, HTTPException
from auth import verify_token
from risk import handle_risk

router = APIRouter(prefix="/agent/docker", tags=["Docker"])

@router.get("/containers")
async def list_containers(_=Depends(verify_token)):
    await handle_risk("L1", "Docker")
    try:
        result = subprocess.run(
            ["docker", "ps", "--format", "{{.ID}}|{{.Names}}|{{.Status}}|{{.Image}}"],
            capture_output=True, text=True, timeout=10
        )
        containers = []
        for line in result.stdout.strip().split("\n"):
            if line:
                parts = line.split("|")
                containers.append({"id": parts[0], "name": parts[1], "status": parts[2], "image": parts[3]})
        return {"containers": containers, "count": len(containers)}
    except Exception as e:
        return {"containers": [], "error": str(e)}

@router.get("/containers/{container_id}/logs")
async def container_logs(container_id: str, _=Depends(verify_token), tail: int = 100):
    await handle_risk("L1", f'', container_id)
    try:
        result = subprocess.run(
            ["docker", "logs", "--tail", str(tail), container_id],
            capture_output=True, text=True, timeout=10
        )
        return {"container_id": container_id, "logs": result.stdout[-2000:]}
    except Exception as e:
        raise HTTPException(500, str(e))
