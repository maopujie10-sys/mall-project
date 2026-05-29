"""Docker 绠＄悊 API 鈥?瀹瑰櫒鍒楄〃/鏃ュ織/鐘舵€?閲嶅惎/鍋ュ悍妫€鏌?""
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from typing import Optional
from auth import verify_token
from executor import execute
from risk import handle_risk
from safety import anti_loop

router = APIRouter(prefix="/docker", tags=["Docker"])

class ContainerAction(BaseModel):
    container_id: str
    action: str  # restart / stop / start

@router.get("/ps")
async def docker_ps(_=Depends(verify_token)):
    """鏌ョ湅鎵€鏈?Docker 瀹瑰櫒"""
    await handle_risk("L1", "鏌ョ湅Docker瀹瑰櫒鍒楄〃")
    result = await execute("docker ps -a --format '{{.ID}}|{{.Image}}|{{.Status}}|{{.Names}}|{{.Ports}}'")
    containers = []
    if result["success"]:
        for line in result["stdout"].strip().split("\n"):
            if "|" in line:
                parts = line.split("|")
                containers.append({
                    "id": parts[0][:12],
                    "image": parts[1],
                    "status": parts[2],
                    "name": parts[3],
                    "ports": parts[4] if len(parts) > 4 else "",
                })
    return {"containers": containers, "count": len(containers)}

@router.get("/stats")
async def docker_stats(_=Depends(verify_token)):
    """鏌ョ湅瀹瑰櫒璧勬簮鍗犵敤"""
    await handle_risk("L1", "鏌ョ湅Docker璧勬簮鍗犵敤")
    result = await execute("docker stats --no-stream --format '{{.Name}}|{{.CPUPerc}}|{{.MemUsage}}|{{.MemPerc}}|{{.NetIO}}'")
    stats = []
    if result["success"]:
        for line in result["stdout"].strip().split("\n"):
            if "|" in line:
                parts = line.split("|")
                stats.append({
                    "name": parts[0],
                    "cpu": parts[1],
                    "memory": parts[2],
                    "mem_percent": parts[3],
                    "net_io": parts[4] if len(parts) > 4 else "",
                })
    return {"stats": stats}

@router.get("/logs")
async def docker_logs(
    container: str = Query("", description="瀹瑰櫒鍚嶇О鎴朓D"),
    lines: int = Query(50, description="琛屾暟"),
    _=Depends(verify_token)
):
    """鏌ョ湅鎸囧畾瀹瑰櫒鏃ュ織"""
    await handle_risk("L1", f"鏌ョ湅瀹瑰櫒鏃ュ織", f"{container} {lines}琛?)
    if not container:
        raise HTTPException(400, "璇锋寚瀹氬鍣ㄥ悕绉版垨ID")
    result = await execute(f"docker logs --tail {lines} {container} 2>&1")
    return {
        "container": container,
        "lines": lines,
        "content": result["stdout"][:3000],
        "truncated": len(result["stdout"]) > 3000,
    }

@router.get("/status")
async def docker_status(container: Optional[str] = Query(None), _=Depends(verify_token)):
    """鏌ョ湅瀹瑰櫒鍋ュ悍鐘舵€?""
    await handle_risk("L1", "鏌ョ湅Docker鐘舵€?)
    if container:
        result = await execute(f"docker inspect {container} --format '{{.State.Status}}|{{.State.Health.Status}}|{{.State.Running}}'")
        if result["success"]:
            parts = result["stdout"].strip().split("|")
            return {
                "container": container,
                "status": parts[0] if len(parts) > 0 else "unknown",
                "health": parts[1] if len(parts) > 1 else "N/A",
                "running": parts[2] if len(parts) > 2 else "N/A",
            }
        raise HTTPException(404, f"瀹瑰櫒 {container} 涓嶅瓨鍦?)
    else:
        result = await execute("docker ps --format '{{.Names}}' | wc -l")
        running = result["stdout"].strip() if result["success"] else "0"
        total = await execute("docker ps -a --format '{{.Names}}' | wc -l")
        total_count = total["stdout"].strip() if total["success"] else "0"
        return {"running": int(running or 0), "total": int(total_count or 0)}

@router.post("/restart")
async def docker_restart(req: ContainerAction, _=Depends(verify_token)):
    """閲嶅惎瀹瑰櫒锛堥潪鏍稿績瀹瑰櫒鑷姩鎵ц锛屾牳蹇冨鍣ㄩ渶瀹℃壒锛?""
    # 妫€鏌ラ槻寰幆
    loop_key = f"restart:{req.container_id}"
    if not anti_loop.check(loop_key, max_count=1, window_min=10):
        return {"ok": False, "error": f"瀹瑰櫒 {req.container_id} 10鍒嗛挓鍐呭凡閲嶅惎杩囷紝闃插惊鐜満鍒跺凡闄愬埗"}

    # 鍒ゆ柇鏄惁鏍稿績瀹瑰櫒
    core_containers = ["mall", "mall-app", "mall-admin", "mysql", "redis", "database"]
    is_core = any(c in req.container_id.lower() for c in core_containers)

    if is_core:
        risk = await handle_risk("L3", f"閲嶅惎鏍稿績瀹瑰櫒", req.container_id)
        if not risk["allowed"]:
            return risk
    else:
        await handle_risk("L2", f"閲嶅惎闈炴牳蹇冨鍣?, req.container_id)

    result = await execute(f"docker restart {req.container_id}")
    if result["success"]:
        anti_loop.record(loop_key)
    return {"ok": result["success"], "container": req.container_id, "output": result["stdout"][:200]}

@router.get("/compose")
async def docker_compose_ps(_=Depends(verify_token)):
    """鏌ョ湅 docker compose 鏈嶅姟鐘舵€?""
    await handle_risk("L1", "鏌ョ湅Docker Compose鐘舵€?)
    result = await execute("docker compose ps --format 'table {{.Name}}\t{{.Status}}\t{{.Ports}}' 2>/dev/null || docker compose ls 2>/dev/null || echo 'compose not available'")
    return {"output": result["stdout"][:1000]}

@router.get("/images")
async def docker_images(_=Depends(verify_token)):
    """鏌ョ湅 Docker 闀滃儚鍒楄〃"""
    await handle_risk("L1", "鏌ョ湅Docker闀滃儚")
    result = await execute("docker images --format '{{.Repository}}|{{.Tag}}|{{.ID}}|{{.Size}}'")
    images = []
    if result["success"]:
        for line in result["stdout"].strip().split("\n"):
            if "|" in line:
                parts = line.split("|")
                images.append({"repo": parts[0], "tag": parts[1], "id": parts[2][:12], "size": parts[3]})
    return {"images": images, "count": len(images)}

@router.get("/network")
async def docker_network(_=Depends(verify_token)):
    """鏌ョ湅 Docker 缃戠粶"""
    await handle_risk("L1", "鏌ョ湅Docker缃戠粶")
    result = await execute("docker network ls --format '{{.ID}}|{{.Name}}|{{.Driver}}|{{.Scope}}'")
    networks = []
    if result["success"]:
        for line in result["stdout"].strip().split("\n"):
            if "|" in line:
                parts = line.split("|")
                networks.append({"id": parts[0][:12], "name": parts[1], "driver": parts[2], "scope": parts[3]})
    return {"networks": networks, "count": len(networks)}
