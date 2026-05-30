"""API -- ///"""
from fastapi import APIRouter, Depends
from auth import verify_token
from risk import handle_risk
import asyncio
from datetime import datetime

router = APIRouter(prefix="/agent/scheduler", tags=["Scheduler"])


TASKS_INFO = [
    {"id":"patrol","name":'',"desc":"CPU/Docker/Nginx/","trigger":"30","last_run":'',"next_run":'',"status":"running"},
    {"id":"backup","name":'',"desc":"MySQL","trigger":"2:00","last_run":'',"next_run":'',"status":"running"},
    {"id":"rotation","name":'',"desc":"+","trigger":"5","last_run":'',"next_run":'',"status":"running"},
    {"id":"customer_report","name":'',"desc":'',"trigger":"18:00","last_run":'',"next_run":'',"status":"running"},
    {"id":"mall_scan","name":'',"desc":"//","trigger":"3:00","last_run":'',"next_run":'',"status":"running"},
    {"id":"diary","name":"AI","desc":'',"trigger":"23:55","last_run":'',"next_run":'',"status":"running"},
    {"id":"ssl_renew","name":"SSL","desc":"SSL+","trigger":"3:30","last_run":'',"next_run":'',"status":"running"},
    {"id":"daily_report","name":'',"desc":"+","trigger":"8:00","last_run":'',"next_run":'',"status":"running"},
    {"id":"metrics","name":'',"desc":"CPU//","trigger":"5","last_run":'',"next_run":'',"status":"running"},
]

@router.get("/tasks")
async def list_tasks(_=Depends(verify_token)):
    ''''''
    from scheduler import scheduler as sched
    jobs = []
    for job in sched.get_jobs():
        info = next((t for t in TASKS_INFO if t["id"] == job.id), None)
        jobs.append({
            "id": job.id,
            "name": info["name"] if info else job.id,
            "desc": info["desc"] if info else '',
            "trigger": info["trigger"] if info else str(job.trigger),
            "next_run": job.next_run_time.isoformat() if job.next_run_time else '',
            "status": "running" if job.next_run_time else "paused",
            "pending": job.pending if hasattr(job, 'pending') else False
        })
    return {"ok": True, "total": len(jobs), "tasks": jobs}

@router.post("/tasks/{task_id}/trigger")
async def trigger_task(task_id: str, _=Depends(verify_token)):
    ''''''
    from scheduler import scheduler as sched
    await handle_risk("L2", '', task_id)
    job = sched.get_job(task_id)
    if not job:
        return {"ok": False, "error": ''}
    try:
        await job.func()
        return {"ok": True, "task_id": task_id, "triggered": True, "time": datetime.now().isoformat()}
    except Exception as e:
        return {"ok": False, "task_id": task_id, "error": str(e)[:200]}

@router.post("/tasks/{task_id}/pause")
async def pause_task(task_id: str, _=Depends(verify_token)):
    ''''''
    from scheduler import scheduler as sched
    await handle_risk("L2", '', task_id)
    job = sched.get_job(task_id)
    if not job:
        return {"ok": False, "error": ''}
    sched.pause_job(task_id)
    return {"ok": True, "task_id": task_id, "paused": True}

@router.post("/tasks/{task_id}/resume")
async def resume_task(task_id: str, _=Depends(verify_token)):
    ''''''
    from scheduler import scheduler as sched
    await handle_risk("L2", '', task_id)
    job = sched.get_job(task_id)
    if not job:
        return {"ok": False, "error": ''}
    sched.resume_job(task_id)
    return {"ok": True, "task_id": task_id, "resumed": True}
