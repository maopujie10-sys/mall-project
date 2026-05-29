锘?""DevOps Agent API 鈥?杩愮淮鎿嶄綔鍏ュ彛"""
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
    """鏈嶅姟鍣ㄥ仴搴锋鏌?""
    await handle_risk("L1", "鏈嶅姟鍣ㄥ仴搴锋鏌?, host)
    return await DevOpsAgent.check_server_health(host)

@router.get("/ports")
async def check_ports(_=Depends(verify_token)):
    """绔彛鐘舵€佹鏌?""
    await handle_risk("L1", "绔彛妫€鏌?)
    return {"ports": await DevOpsAgent.check_ports()}

@router.get("/processes")
async def top_processes(limit: int = 10, _=Depends(verify_token)):
    """楂樺崰鐢ㄨ繘绋?""
    await handle_risk("L1", "杩涚▼妫€鏌?)
    return {"processes": await DevOpsAgent.check_top_processes(limit)}

@router.get("/docker")
async def docker_status(_=Depends(verify_token)):
    """Docker鐘舵€?""
    await handle_risk("L1", "Docker妫€鏌?)
    return await DevOpsAgent.check_docker_status()

@router.post("/docker/restart")
async def restart_container(req: RestartRequest, _=Depends(verify_token)):
    """閲嶅惎瀹瑰櫒"""
    await handle_risk("L2", f"閲嶅惎瀹瑰櫒: {req.name}")
    return await DevOpsAgent.restart_container(req.name)

@router.get("/nginx")
async def nginx_status(_=Depends(verify_token)):
    """Nginx鐘舵€?""
    await handle_risk("L1", "Nginx妫€鏌?)
    return await DevOpsAgent.check_nginx_status()

@router.get("/nginx/logs")
async def nginx_logs(lines: int = 50, _=Depends(verify_token)):
    """Nginx鏃ュ織"""
    await handle_risk("L1", "Nginx鏃ュ織")
    return await DevOpsAgent.get_nginx_logs(lines)

@router.post("/auto-heal")
async def auto_heal(_=Depends(verify_token)):
    """鑷姩淇宸℃"""
    await handle_risk("L2", "鑷姩淇")
    return await DevOpsAgent.auto_heal_check()