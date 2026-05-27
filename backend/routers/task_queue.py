"""任务队列 + 任务锁 API"""
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from auth import verify_token
from risk import handle_risk
from tasks import task_queue, task_lock

router = APIRouter(prefix="/tasks", tags=["Tasks"])

class EnqueueRequest(BaseModel):
    name: str
    risk: str = "L1"
    priority: int = 5
    timeout_s: int = 60

@router.post("/enqueue")
async def enqueue_task(req: EnqueueRequest, _=Depends(verify_token)):
    await handle_risk("L1", "添加任务到队列", req.name)
    task_id = task_queue.enqueue(req.name, req.risk, req.priority, req.timeout_s)
    return {"task_id": task_id, "status": "queued"}

@router.get("/queue")
async def list_queue(_=Depends(verify_token)):
    await handle_risk("L1", "查看任务队列")
    return {"tasks": task_queue.list(), "pending": task_queue.pending_count()}

@router.get("/queue/{task_id}")
async def get_task(task_id: str, _=Depends(verify_token)):
    t = task_queue.get(task_id)
    if not t:
        return {"error": "任务不存在"}
    return t

@router.post("/queue/{task_id}/pause")
async def pause_task(task_id: str, _=Depends(verify_token)):
    ok = task_queue.pause(task_id)
    return {"ok": ok, "task_id": task_id}

@router.post("/queue/{task_id}/cancel")
async def cancel_task(task_id: str, _=Depends(verify_token)):
    ok = task_queue.cancel(task_id)
    return {"ok": ok, "task_id": task_id}

@router.post("/queue/{task_id}/finish")
async def finish_task(task_id: str, success: bool = True, result: str = "", _=Depends(verify_token)):
    task_queue.finish(task_id, success, result)
    return {"task_id": task_id, "success": success}

@router.post("/queue/dequeue")
async def dequeue_task(_=Depends(verify_token)):
    t = task_queue.dequeue()
    if t:
        return {"task": t, "dequeued": True}
    return {"task": None, "dequeued": False}

@router.get("/locks")
async def list_locks(_=Depends(verify_token)):
    await handle_risk("L1", "查看任务锁")
    return task_lock.status()

@router.post("/locks/acquire")
async def acquire_lock(lock_name: str, task_id: str, _=Depends(verify_token)):
    ok = task_lock.acquire(lock_name, task_id)
    return {"lock": lock_name, "acquired": ok}

@router.post("/locks/release")
async def release_lock(lock_name: str, task_id: str, _=Depends(verify_token)):
    ok = task_lock.release(lock_name, task_id)
    return {"lock": lock_name, "released": ok}

@router.post("/locks/force-release")
async def force_release_lock(lock_name: str, _=Depends(verify_token)):
    task_lock.force_release(lock_name)
    return {"lock": lock_name, "released": True}
