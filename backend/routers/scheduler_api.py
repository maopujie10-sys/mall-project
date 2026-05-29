"""定时任务管理API — 查看/触发/暂停/恢复定时任务"""
from fastapi import APIRouter, Depends
from auth import verify_token
from risk import handle_risk
import asyncio
from datetime import datetime

router = APIRouter(prefix="/agent/scheduler", tags=["Scheduler"])

# 任务注册表
TASKS_INFO = [
    {"id":"patrol","name":"服务器巡检","desc":"CPU/Docker/Nginx/网站健康检查","trigger":"每30分钟","last_run":"","next_run":"","status":"running"},
    {"id":"backup","name":"数据库备份","desc":"每日自动备份MySQL数据库","trigger":"每日凌晨2:00","last_run":"","next_run":"","status":"running"},
    {"id":"rotation","name":"域名轮值检测","desc":"检测域名健康+自动切换","trigger":"每5分钟","last_run":"","next_run":"","status":"running"},
    {"id":"customer_report","name":"客服日报","desc":"生成客服工作统计报告","trigger":"每日18:00","last_run":"","next_run":"","status":"running"},
    {"id":"mall_scan","name":"商城扫描","desc":"扫描商城商品/订单/用户状态","trigger":"每日凌晨3:00","last_run":"","next_run":"","status":"running"},
    {"id":"diary","name":"AI日记","desc":"自动生成每日运营日记","trigger":"每日23:55","last_run":"","next_run":"","status":"running"},
    {"id":"ssl_renew","name":"SSL续签检查","desc":"检查SSL证书到期+自动续签","trigger":"每日凌晨3:30","last_run":"","next_run":"","status":"running"},
    {"id":"daily_report","name":"每日运营早报","desc":"生成系统健康+运营数据早报","trigger":"每日8:00","last_run":"","next_run":"","status":"running"},
    {"id":"metrics","name":"系统指标采集","desc":"采集CPU/内存/磁盘等指标","trigger":"每5分钟","last_run":"","next_run":"","status":"running"},
]

@router.get("/tasks")
async def list_tasks(_=Depends(verify_token)):
    """获取所有定时任务状态"""
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
    """手动触发定时任务"""
    from scheduler import scheduler as sched
    await handle_risk("L2", "手动触发定时任务", task_id)
    job = sched.get_job(task_id)
    if not job:
        return {"ok": False, "error": "任务不存在"}
    try:
        await job.func()
        return {"ok": True, "task_id": task_id, "triggered": True, "time": datetime.now().isoformat()}
    except Exception as e:
        return {"ok": False, "task_id": task_id, "error": str(e)[:200]}

@router.post("/tasks/{task_id}/pause")
async def pause_task(task_id: str, _=Depends(verify_token)):
    """暂停定时任务"""
    from scheduler import scheduler as sched
    await handle_risk("L2", "暂停定时任务", task_id)
    job = sched.get_job(task_id)
    if not job:
        return {"ok": False, "error": "任务不存在"}
    sched.pause_job(task_id)
    return {"ok": True, "task_id": task_id, "paused": True}

@router.post("/tasks/{task_id}/resume")
async def resume_task(task_id: str, _=Depends(verify_token)):
    """恢复定时任务"""
    from scheduler import scheduler as sched
    await handle_risk("L2", "恢复定时任务", task_id)
    job = sched.get_job(task_id)
    if not job:
        return {"ok": False, "error": "任务不存在"}
    sched.resume_job(task_id)
    return {"ok": True, "task_id": task_id, "resumed": True}
