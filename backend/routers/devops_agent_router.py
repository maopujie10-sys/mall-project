"""DevOps Agent API — 运维操作入口"""
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
    """服务器健康检查"""
    await handle_risk("L1", "服务器健康检查", host)
    return await DevOpsAgent.check_server_health(host)

@router.get("/ports")
async def check_ports(_=Depends(verify_token)):
    """端口状态检查"""
    await handle_risk("L1", "端口检查")
    return {"ports": await DevOpsAgent.check_ports()}

@router.get("/processes")
async def top_processes(limit: int = 10, _=Depends(verify_token)):
    """高占用进程"""
    await handle_risk("L1", "进程检查")
    return {"processes": await DevOpsAgent.check_top_processes(limit)}

@router.get("/docker")
async def docker_status(_=Depends(verify_token)):
    """Docker状态"""
    await handle_risk("L1", "Docker检查")
    return await DevOpsAgent.check_docker_status()

@router.post("/docker/restart")
async def restart_container(req: RestartRequest, _=Depends(verify_token)):
    """重启容器"""
    await handle_risk("L2", f"重启容器: {req.name}")
    return await DevOpsAgent.restart_container(req.name)

@router.get("/nginx")
async def nginx_status(_=Depends(verify_token)):
    """Nginx状态"""
    await handle_risk("L1", "Nginx检查")
    return await DevOpsAgent.check_nginx_status()

@router.get("/nginx/logs")
async def nginx_logs(lines: int = 50, _=Depends(verify_token)):
    """Nginx日志"""
    await handle_risk("L1", "Nginx日志")
    return await DevOpsAgent.get_nginx_logs(lines)

@router.post("/auto-heal")
async def auto_heal(_=Depends(verify_token)):
    """自动修复巡检"""
    await handle_risk("L2", "自动修复")
    return await DevOpsAgent.auto_heal_check()