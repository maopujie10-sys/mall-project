''"APScheduler  -- /
:
  - 30  (CPU/Docker/Nginx/)
  - 2 
  - 9+21 +
  - 18 
  - 3 
  - 23:55 
''"
import asyncio
from datetime import datetime
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.triggers.cron import CronTrigger
from tools.logger import get_logger
from tools.alert_push import push_weekly_report

# () -- 
MIN_SCHEDULE_INTERVAL = 60

scheduler = AsyncIOScheduler()
logger = get_logger("scheduler")


async def patrol_task():
    ''" -- CPU/Docker/Nginx/''"
    now_str = datetime.now().strftime("%H:%M:%S")
    logger.info(f" {now_str}")
    try:
        from routers.inspector import run_inspection
        await run_inspection()
    except Exception as e:
        logger.info(f": {e}")


async def backup_task():
    ''''''
    now_str = datetime.now().strftime("%H:%M:%S")
    logger.info(f" {now_str}")
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
                "id": ts, "name": f"_{ts}", "type": "auto",
                "target": "database", "path": backup_path,
                "size": len(result.stdout), "created_at": datetime.now().isoformat(),
            })
            _save_backups(records)
            logger.info(f" {backup_path}")
        else:
            logger.info(f": {result.stderr[:200]}")
    except Exception as e:
        logger.info(f": {e}")


async def rotation_check_task():
    ''" + ''"
    now_str = datetime.now().strftime("%H:%M:%S")
    logger.info(f" {now_str}")
    try:
        from routers.rotation_panel import _check_all
        result = await _check_all()
        if result.get("rotated_to"):
            logger.info(f" -> {result['rotated_to']}")
        logger.info(f": {result.get('checked', 0)} ")
    except Exception as e:
        logger.info(f": {e}")


async def customer_report_task():
    ''''''
    now_str = datetime.now().strftime("%H:%M:%S")
    logger.info(f" {now_str}")
    try:
        from routers.customer_panel import _generate_report
        await _generate_report()
    except Exception as e:
        logger.info(f": {e}")


async def diary_task():
    ''''''
    now_str = datetime.now().strftime("%H:%M:%S")
    logger.info(f" {now_str}")
    try:
        from services import DiaryService
        journal = DiaryService.generate_daily()
        path = DiaryService.save_journal(journal)
        logger.info(f" {path}")
    except Exception as e:
        logger.info(f": {e}")


async def mall_scan_task():
    ''''''
    now_str = datetime.now().strftime("%H:%M:%S")
    logger.info(f" {now_str}")
    try:
        from routers.mall_scanner import run_scan
        await run_scan()
    except Exception as e:
        logger.info(f": {e}")



async def ssl_renew_check_task():
    ''"SSL + ''"
    logger.info("SSL {datetime.now().strftime('%H:%M:%S')}")
    try:
        from routers.ssl_router import _cert_valid, _issue
        from routers.rotation_panel import _get_domains
        domains = _get_domains()
        for d in domains:
            info = _cert_valid(d["domain"])
            if info.get("ok") and info.get("days_left", 0) > 30:
                continue
            logger.info("SSL({info.get('days_left', 0)}), : {d['domain']}")
            result = _issue(d["domain"], '')
            if result.get("ok"):
                logger.info("SSL: {d['domain']}")
            else:
                logger.info("SSL: {d['domain']} - {result.get('error', '')}")
    except Exception as e:
        logger.info(f"SSL: {e}")


async def daily_report_task():
    ''"8''"
    try:
        from routers.daily_report import daily_report
        from auth import verify_token
        from fastapi import Depends
        logger.info("...")
        
        import psutil
        from state import state
        mem = psutil.virtual_memory()
        disk = psutil.disk_usage("/")
        cpu = psutil.cpu_percent(interval=0.3)
        domains = state._data.get("rotation_domains", [])
        active = sum(1 for d in domains if d.get("active"))
        pending = state._data.get("pending_approvals", [])
        score = 100
        if mem.percent > 80: score -= 15
        if disk.percent > 85: score -= 15
        if cpu > 80: score -= 10
        if pending: score -= 5 * min(len(pending), 4)
        score = max(0, score)
        report = {"date": __import__("datetime").datetime.now().strftime("%Y-%m-%d"),
                  "time": __import__("datetime").datetime.now().strftime("%H:%M"),
                  "health_score": score, "server": {"cpu":f"{cpu}%","memory":f"{mem.percent}%","disk":f"{disk.percent}%"},
                  "domains":{"total":len(domains),"active":active},"pending_approvals":len(pending)}
        state.append_data("daily_reports", report, 365)
        
        state._data["last_notification"] = f": {score}, CPU{cpu}%, {mem.percent}%, {disk.percent}%"
        state._save()
        logger.info(f": {score}")
        
        if __import__("datetime").datetime.now().weekday() == 0:
            try:
                from routers.weekly_report import router as wr
                
                await push_weekly_report({"summary": f"{score}, CPU{cpu}%, {mem.percent}%, {len(state._data.get('orders',[]))}"})
            except Exception as e:
                logger.info(f": {e}")
    except Exception as e:
        logger.info(f": {e}")

async def metrics_record_task():
    ''''''
    try:
        from routers.dashboard_router import collect_metrics
        from state import state as _s
        m = await collect_metrics()
        history = _s._data.setdefault("metrics_history", [])
        history.append(m)
        if len(history) > 500:
            _s._data["metrics_history"] = history[-500:]
        _s._save()
    except Exception as e:
        logger.info(f": {e}")

def start_scheduler():
    ''''''
    scheduler.add_job(patrol_task, IntervalTrigger(minutes=30), id="patrol", replace_existing=True)
    scheduler.add_job(backup_task, CronTrigger(hour=2, minute=0), id="backup", replace_existing=True)
    scheduler.add_job(rotation_check_task, CronTrigger(minute='*/5'), id='rotation', replace_existing=True)
    scheduler.add_job(customer_report_task, CronTrigger(hour=18, minute=0), id="customer_report", replace_existing=True)
    scheduler.add_job(mall_scan_task, CronTrigger(hour=3, minute=0), id="mall_scan", replace_existing=True)
    scheduler.add_job(diary_task, CronTrigger(hour=23, minute=55), id="diary", replace_existing=True)
    scheduler.add_job(ssl_renew_check_task, CronTrigger(hour=3, minute=30), id="ssl_renew", replace_existing=True)
    scheduler.add_job(daily_report_task, CronTrigger(hour=8, minute=0), id="daily_report", replace_existing=True)
    scheduler.add_job(metrics_record_task, IntervalTrigger(minutes=5), id="metrics", replace_existing=True)
    scheduler.start()
    logger.info(": ///SSL/////")


def stop_scheduler():
    ''''''
    scheduler.shutdown(wait=False)
    logger.info('')




