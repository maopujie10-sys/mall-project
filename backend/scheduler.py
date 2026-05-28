"""APScheduler 定时任务 — 巡检/备份/轮值/客服报告/商城扫描/日记
定时任务清单:
  - 每30分钟 服务器巡检 (CPU/Docker/Nginx/网站)
  - 每日凌晨2点 数据库备份
  - 每日9点+21点 域名轮值检测+自动切换
  - 每日18点 客服报告
  - 每日凌晨3点 商城扫描
  - 每日23:55 日记生成
"""
import asyncio
from datetime import datetime
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.triggers.cron import CronTrigger

scheduler = AsyncIOScheduler()


async def patrol_task():
    """服务器巡检 — CPU/Docker/Nginx/网站"""
    print(f"[Scheduler] 服务器巡检 {datetime.now().strftime("%H:%M:%S")}")
    try:
        from routers.inspector import run_inspection
        await run_inspection()
    except Exception as e:
        print(f"[Scheduler] 巡检异常: {e}")


async def backup_task():
    """每日数据库备份"""
    print(f"[Scheduler] 数据库备份 {datetime.now().strftime("%H:%M:%S")}")
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
            print(f"[Scheduler] 备份成功 {backup_path}")
        else:
            print(f"[Scheduler] 备份失败: {result.stderr[:200]}")
    except Exception as e:
        print(f"[Scheduler] 备份异常: {e}")


async def rotation_check_task():
    """域名轮值检测 + 自动切换"""
    print(f"[Scheduler] 域名轮值检测 {datetime.now().strftime("%H:%M:%S")}")
    try:
        from routers.rotation_panel import _check_all
        result = await _check_all()
        if result.get("rotated_to"):
            print(f"[Scheduler] 自动轮值 → {result['rotated_to']}")
        print(f"[Scheduler] 域名健康: {result.get('checked', 0)} 个已检测")
    except Exception as e:
        print(f"[Scheduler] 域名轮值异常: {e}")


async def customer_report_task():
    """客服报告生成"""
    print(f"[Scheduler] 客服报告 {datetime.now().strftime("%H:%M:%S")}")
    try:
        from routers.customer_panel import _generate_report
        await _generate_report()
    except Exception as e:
        print(f"[Scheduler] 客服报告异常: {e}")


async def diary_task():
    """每日日记自动生成"""
    print(f"[Scheduler] 日记生成 {datetime.now().strftime("%H:%M:%S")}")
    try:
        from services import DiaryService
        journal = DiaryService.generate_daily()
        path = DiaryService.save_journal(journal)
        print(f"[Scheduler] 日记已保存 {path}")
    except Exception as e:
        print(f"[Scheduler] 日记生成失败: {e}")


async def mall_scan_task():
    """商城扫描"""
    print(f"[Scheduler] 商城扫描 {datetime.now().strftime("%H:%M:%S")}")
    try:
        from routers.mall_scanner import run_scan
        await run_scan()
    except Exception as e:
        print(f"[Scheduler] 商城扫描异常: {e}")


def start_scheduler():
    """启动定时任务"""
    scheduler.add_job(patrol_task, IntervalTrigger(minutes=30), id="patrol", replace_existing=True)
    scheduler.add_job(backup_task, CronTrigger(hour=2, minute=0), id="backup", replace_existing=True)
    scheduler.add_job(rotation_check_task, CronTrigger(hour="9,21", minute=0), id="rotation", replace_existing=True)
    scheduler.add_job(customer_report_task, CronTrigger(hour=18, minute=0), id="customer_report", replace_existing=True)
    scheduler.add_job(mall_scan_task, CronTrigger(hour=3, minute=0), id="mall_scan", replace_existing=True)
    scheduler.add_job(diary_task, CronTrigger(hour=23, minute=55), id="diary", replace_existing=True)
    scheduler.start()
    print("[Scheduler] 定时任务启动完成: 巡检/备份/轮值/商城扫描/客服/日记")


def stop_scheduler():
    """停止定时任务"""
    scheduler.shutdown(wait=False)
    print("[Scheduler] 定时任务已停止")
