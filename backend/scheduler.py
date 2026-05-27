"""APScheduler 定时任务 — 自动巡检/备份/报告

定时任务列表:
  - 每30分钟: 自动巡检 (服务器/Docker/Nginx/网站)
  - 每天凌晨2点: 数据库备份
  - 每天上午9点: 轮值域名检测
  - 每天下午6点: 客服日报
  - 每天凌晨3点: 商城健康度扫描"""
import asyncio
from datetime import datetime
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.triggers.cron import CronTrigger

scheduler = AsyncIOScheduler()


async def patrol_task():
    """定时巡检：服务器/Docker/Nginx/网站连通性"""
    print(f"[Scheduler] 自动巡检 {datetime.now().strftime('%H:%M:%S')}")
    try:
        from routers.inspector import run_inspection
        await run_inspection()
    except Exception as e:
        print(f"[Scheduler] 巡检失败: {e}")


async def backup_task():
    """每日数据库备份"""
    print(f"[Scheduler] 每日备份 {datetime.now().strftime('%H:%M:%S')}")
    try:
        from routers.rollback_center import _load_backups, _save_backups
        import subprocess, os
        from config import MALL_DB_HOST, MALL_DB_PORT, MALL_DB_USER, MALL_DB_PASSWORD, MALL_DB_NAME, BACKUP_DIR
        os.makedirs(BACKUP_DIR, exist_ok=True)
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = os.path.join(BACKUP_DIR, f"auto_backup_{ts}.sql")
        cmd = f"mysqldump -h {MALL_DB_HOST} -P {MALL_DB_PORT} -u {MALL_DB_USER} -p{MALL_DB_PASSWORD} {MALL_DB_NAME}"
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=120)
        if result.returncode == 0:
            with open(backup_path, "w", encoding="utf-8") as f:
                f.write(result.stdout)
            records = _load_backups()
            records.append({
                "id": ts, "name": f"自动备份_{ts}", "type": "auto",
                "target": "database", "path": backup_path,
                "size": len(result.stdout), "created_at": datetime.now().isoformat(),
            })
            _save_backups(records)
            print(f"[Scheduler] 备份完成: {backup_path}")
        else:
            print(f"[Scheduler] 备份失败: {result.stderr[:200]}")
    except Exception as e:
        print(f"[Scheduler] 备份异常: {e}")


async def rotation_check_task():
    """轮值域名检测"""
    print(f"[Scheduler] 轮值检测 {datetime.now().strftime('%H:%M:%S')}")
    try:
        from routers.rotation_panel import _check_all
        await _check_all()
    except Exception as e:
        print(f"[Scheduler] 轮值检测失败: {e}")


async def customer_report_task():
    """客服日报"""
    print(f"[Scheduler] 客服日报 {datetime.now().strftime('%H:%M:%S')}")
    try:
        from routers.customer_panel import _generate_report
        await _generate_report()
    except Exception as e:
        print(f"[Scheduler] 客服日报失败: {e}")


async def mall_scan_task():
    """商城健康度扫描"""
    print(f"[Scheduler] 商城扫描 {datetime.now().strftime('%H:%M:%S')}")
    try:
        from routers.mall_scanner import run_scan
        await run_scan()
    except Exception as e:
        print(f"[Scheduler] 商城扫描失败: {e}")


def start_scheduler():
    """启动定时任务"""
    scheduler.add_job(patrol_task, IntervalTrigger(minutes=30), id="patrol", replace_existing=True)
    scheduler.add_job(backup_task, CronTrigger(hour=2, minute=0), id="backup", replace_existing=True)
    scheduler.add_job(rotation_check_task, CronTrigger(hour=9, minute=0), id="rotation", replace_existing=True)
    scheduler.add_job(customer_report_task, CronTrigger(hour=18, minute=0), id="customer_report", replace_existing=True)
    scheduler.add_job(mall_scan_task, CronTrigger(hour=3, minute=0), id="mall_scan", replace_existing=True)
    scheduler.start()
    print("[Scheduler] 定时任务已启动: 巡检/备份/轮值/日报/扫描")


def stop_scheduler():
    """停止定时任务"""
    scheduler.shutdown(wait=False)
    print("[Scheduler] 定时任务已停止")