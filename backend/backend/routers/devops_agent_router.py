''"DevOps Agent API -- ''"
from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from typing import Optional
from auth import verify_token
from risk import handle_risk
from agents.devops_agent import DevOpsAgent

router = APIRouter(prefix="/devops", tags=["DevOps"])

class RestartRequest(BaseModel):
    name: str

@router.get("/health")
async def server_health(host: str = "localhost", _=Depends(verify_token)):
    ''''''
    await handle_risk("L1", '', host)
    return await DevOpsAgent.check_server_health(host)

@router.get("/ports")
async def check_ports(_=Depends(verify_token)):
    ''''''
    await handle_risk("L1", '')
    return {"ports": await DevOpsAgent.check_ports()}

@router.get("/processes")
async def top_processes(limit: int = 10, _=Depends(verify_token)):
    ''''''
    await handle_risk("L1", '')
    return {"processes": await DevOpsAgent.check_top_processes(limit)}

@router.get("/docker")
async def docker_status(_=Depends(verify_token)):
    ''"Docker''"
    await handle_risk("L1", "Docker")
    return await DevOpsAgent.check_docker_status()

@router.post("/docker/restart")
async def restart_container(req: RestartRequest, _=Depends(verify_token)):
    ''''''
    await handle_risk("L2", f": {req.name}")
    return await DevOpsAgent.restart_container(req.name)

@router.get("/nginx")
async def nginx_status(_=Depends(verify_token)):
    ''"Nginx''"
    await handle_risk("L1", "Nginx")
    return await DevOpsAgent.check_nginx_status()

@router.get("/nginx/logs")
async def nginx_logs(lines: int = 50, _=Depends(verify_token)):
    ''"Nginx''"
    await handle_risk("L1", "Nginx")
    return await DevOpsAgent.get_nginx_logs(lines)

@router.post("/auto-heal")
async def auto_heal(_=Depends(verify_token)):
    ''''''
    await handle_risk("L2", '')
    return await DevOpsAgent.auto_heal_check()