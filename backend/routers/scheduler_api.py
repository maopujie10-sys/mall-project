锘?""瀹氭椂浠诲姟绠＄悊API 鈥?鏌ョ湅/瑙﹀彂/鏆傚仠/鎭㈠瀹氭椂浠诲姟"""
from fastapi import APIRouter, Depends
from auth import verify_token
from risk import handle_risk
import asyncio
from datetime import datetime

router = APIRouter(prefix="/agent/scheduler", tags=["Scheduler"])

# 浠诲姟娉ㄥ唽琛?
TASKS_INFO = [
    {"id":"patrol","name":"鏈嶅姟鍣ㄥ贰妫€","desc":"CPU/Docker/Nginx/缃戠珯鍋ュ悍妫€鏌?,"trigger":"姣?0鍒嗛挓","last_run":"","next_run":"","status":"running"},
    {"id":"backup","name":"鏁版嵁搴撳浠?,"desc":"姣忔棩鑷姩澶囦唤MySQL鏁版嵁搴?,"trigger":"姣忔棩鍑屾櫒2:00","last_run":"","next_run":"","status":"running"},
    {"id":"rotation","name":"鍩熷悕杞€兼娴?,"desc":"妫€娴嬪煙鍚嶅仴搴?鑷姩鍒囨崲","trigger":"姣?鍒嗛挓","last_run":"","next_run":"","status":"running"},
    {"id":"customer_report","name":"瀹㈡湇鏃ユ姤","desc":"鐢熸垚瀹㈡湇宸ヤ綔缁熻鎶ュ憡","trigger":"姣忔棩18:00","last_run":"","next_run":"","status":"running"},
    {"id":"mall_scan","name":"鍟嗗煄鎵弿","desc":"鎵弿鍟嗗煄鍟嗗搧/璁㈠崟/鐢ㄦ埛鐘舵€?,"trigger":"姣忔棩鍑屾櫒3:00","last_run":"","next_run":"","status":"running"},
    {"id":"diary","name":"AI鏃ヨ","desc":"鑷姩鐢熸垚姣忔棩杩愯惀鏃ヨ","trigger":"姣忔棩23:55","last_run":"","next_run":"","status":"running"},
    {"id":"ssl_renew","name":"SSL缁妫€鏌?,"desc":"妫€鏌SL璇佷功鍒版湡+鑷姩缁","trigger":"姣忔棩鍑屾櫒3:30","last_run":"","next_run":"","status":"running"},
    {"id":"daily_report","name":"姣忔棩杩愯惀鏃╂姤","desc":"鐢熸垚绯荤粺鍋ュ悍+杩愯惀鏁版嵁鏃╂姤","trigger":"姣忔棩8:00","last_run":"","next_run":"","status":"running"},
    {"id":"metrics","name":"绯荤粺鎸囨爣閲囬泦","desc":"閲囬泦CPU/鍐呭瓨/纾佺洏绛夋寚鏍?,"trigger":"姣?鍒嗛挓","last_run":"","next_run":"","status":"running"},
]

@router.get("/tasks")
async def list_tasks(_=Depends(verify_token)):
    """鑾峰彇鎵€鏈夊畾鏃朵换鍔＄姸鎬?""
    from scheduler import scheduler as sched
    jobs = []
    for job in sched.get_jobs():
        info = next((t for t in TASKS_INFO if t["id"] == job.id), None)
        jobs.append({
            "id": job.id,
            "name": info["name"] if info else job.id,
            "desc": info["desc"] if info else "",
            "trigger": info["trigger"] if info else str(job.trigger),
            "next_run": job.next_run_time.isoformat() if job.next_run_time else "",
            "status": "running" if job.next_run_time else "paused",
            "pending": job.pending if hasattr(job, 'pending') else False
        })
    return {"ok": True, "total": len(jobs), "tasks": jobs}

@router.post("/tasks/{task_id}/trigger")
async def trigger_task(task_id: str, _=Depends(verify_token)):
    """鎵嬪姩瑙﹀彂瀹氭椂浠诲姟"""
    from scheduler import scheduler as sched
    await handle_risk("L2", "鎵嬪姩瑙﹀彂瀹氭椂浠诲姟", task_id)
    job = sched.get_job(task_id)
    if not job:
        return {"ok": False, "error": "浠诲姟涓嶅瓨鍦?}
    try:
        await job.func()
        return {"ok": True, "task_id": task_id, "triggered": True, "time": datetime.now().isoformat()}
    except Exception as e:
        return {"ok": False, "task_id": task_id, "error": str(e)[:200]}

@router.post("/tasks/{task_id}/pause")
async def pause_task(task_id: str, _=Depends(verify_token)):
    """鏆傚仠瀹氭椂浠诲姟"""
    from scheduler import scheduler as sched
    await handle_risk("L2", "鏆傚仠瀹氭椂浠诲姟", task_id)
    job = sched.get_job(task_id)
    if not job:
        return {"ok": False, "error": "浠诲姟涓嶅瓨鍦?}
    sched.pause_job(task_id)
    return {"ok": True, "task_id": task_id, "paused": True}

@router.post("/tasks/{task_id}/resume")
async def resume_task(task_id: str, _=Depends(verify_token)):
    """鎭㈠瀹氭椂浠诲姟"""
    from scheduler import scheduler as sched
    await handle_risk("L2", "鎭㈠瀹氭椂浠诲姟", task_id)
    job = sched.get_job(task_id)
    if not job:
        return {"ok": False, "error": "浠诲姟涓嶅瓨鍦?}
    sched.resume_job(task_id)
    return {"ok": True, "task_id": task_id, "resumed": True}
