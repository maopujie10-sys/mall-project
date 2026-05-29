"""APScheduler 瀹氭椂浠诲姟 鈥?宸℃/澶囦唤/杞€?瀹㈡湇鎶ュ憡/鍟嗗煄鎵弿/鏃ヨ
瀹氭椂浠诲姟娓呭崟:
  - 姣?0鍒嗛挓 鏈嶅姟鍣ㄥ贰妫€ (CPU/Docker/Nginx/缃戠珯)
  - 姣忔棩鍑屾櫒2鐐?鏁版嵁搴撳浠?
  - 姣忔棩9鐐?21鐐?鍩熷悕杞€兼娴?鑷姩鍒囨崲
  - 姣忔棩18鐐?瀹㈡湇鎶ュ憡
  - 姣忔棩鍑屾櫒3鐐?鍟嗗煄鎵弿
  - 姣忔棩23:55 鏃ヨ鐢熸垚
"""
import asyncio
from datetime import datetime
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.triggers.cron import CronTrigger
from tools.logger import get_logger
from tools.alert_push import push_weekly_report

# 鏈€灏忛棿闅斾繚鎶?绉? 鈥?闃叉浠讳綍瀹氭椂浠诲姟浣庝簬姝ら鐜?
MIN_SCHEDULE_INTERVAL = 60

scheduler = AsyncIOScheduler()
logger = get_logger("scheduler")


async def patrol_task():
    """鏈嶅姟鍣ㄥ贰妫€ 鈥?CPU/Docker/Nginx/缃戠珯"""
    now_str = datetime.now().strftime("%H:%M:%S")
    logger.info(f"鏈嶅姟鍣ㄥ贰妫€ {now_str}")
    try:
        from routers.inspector import run_inspection
        await run_inspection()
    except Exception as e:
        logger.info(f"宸℃寮傚父: {e}")


async def backup_task():
    """姣忔棩鏁版嵁搴撳浠?""
    now_str = datetime.now().strftime("%H:%M:%S")
    logger.info(f"鏁版嵁搴撳浠?{now_str}")
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
                "id": ts, "name": f"鑷姩澶囦唤_{ts}", "type": "auto",
                "target": "database", "path": backup_path,
                "size": len(result.stdout), "created_at": datetime.now().isoformat(),
            })
            _save_backups(records)
            logger.info(f"澶囦唤鎴愬姛 {backup_path}")
        else:
            logger.info(f"澶囦唤澶辫触: {result.stderr[:200]}")
    except Exception as e:
        logger.info(f"澶囦唤寮傚父: {e}")


async def rotation_check_task():
    """鍩熷悕杞€兼娴?+ 鑷姩鍒囨崲"""
    now_str = datetime.now().strftime("%H:%M:%S")
    logger.info(f"鍩熷悕杞€兼娴?{now_str}")
    try:
        from routers.rotation_panel import _check_all
        result = await _check_all()
        if result.get("rotated_to"):
            logger.info(f"鑷姩杞€?鈫?{result['rotated_to']}")
        logger.info(f"鍩熷悕鍋ュ悍: {result.get('checked', 0)} 涓凡妫€娴?)
    except Exception as e:
        logger.info(f"鍩熷悕杞€煎紓甯? {e}")


async def customer_report_task():
    """瀹㈡湇鎶ュ憡鐢熸垚"""
    now_str = datetime.now().strftime("%H:%M:%S")
    logger.info(f"瀹㈡湇鎶ュ憡 {now_str}")
    try:
        from routers.customer_panel import _generate_report
        await _generate_report()
    except Exception as e:
        logger.info(f"瀹㈡湇鎶ュ憡寮傚父: {e}")


async def diary_task():
    """姣忔棩鏃ヨ鑷姩鐢熸垚"""
    now_str = datetime.now().strftime("%H:%M:%S")
    logger.info(f"鏃ヨ鐢熸垚 {now_str}")
    try:
        from services import DiaryService
        journal = DiaryService.generate_daily()
        path = DiaryService.save_journal(journal)
        logger.info(f"鏃ヨ宸蹭繚瀛?{path}")
    except Exception as e:
        logger.info(f"鏃ヨ鐢熸垚澶辫触: {e}")


async def mall_scan_task():
    """鍟嗗煄鎵弿"""
    now_str = datetime.now().strftime("%H:%M:%S")
    logger.info(f"鍟嗗煄鎵弿 {now_str}")
    try:
        from routers.mall_scanner import run_scan
        await run_scan()
    except Exception as e:
        logger.info(f"鍟嗗煄鎵弿寮傚父: {e}")



async def ssl_renew_check_task():
    """SSL璇佷功鍒版湡妫€鏌?+ 鑷姩缁"""
    logger.info("SSL璇佷功妫€鏌?{datetime.now().strftime('%H:%M:%S')}")
    try:
        from routers.ssl_router import _cert_valid, _issue
        from routers.rotation_panel import _get_domains
        domains = _get_domains()
        for d in domains:
            info = _cert_valid(d["domain"])
            if info.get("ok") and info.get("days_left", 0) > 30:
                continue
            logger.info("SSL鍒版湡({info.get('days_left', 0)}澶?, 鑷姩缁: {d['domain']}")
            result = _issue(d["domain"], "")
            if result.get("ok"):
                logger.info("SSL缁鎴愬姛: {d['domain']}")
            else:
                logger.info("SSL缁澶辫触: {d['domain']} - {result.get('error', '')}")
    except Exception as e:
        logger.info(f"SSL妫€鏌ュ紓甯? {e}")


async def daily_report_task():
    """姣忔棩8鐐圭敓鎴愯繍钀ユ棭鎶?""
    try:
        from routers.daily_report import daily_report
        from auth import verify_token
        from fastapi import Depends
        logger.info("鐢熸垚姣忔棩鏃╂姤...")
        # 鐩存帴璋冪敤鐢熸垚閫昏緫
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
        # 鍙戦€氱煡
        state._data["last_notification"] = f"姣忔棩鏃╂姤: 鍋ュ悍鍒唟score}, CPU{cpu}%, 鍐呭瓨{mem.percent}%, 纾佺洏{disk.percent}%"
        state._save()
        logger.info(f"姣忔棩鏃╂姤: 鍋ュ悍鍒唟score}")
        # 鍛ㄤ竴鑷姩鎺ㄩ€佸懆鎶?
        if __import__("datetime").datetime.now().weekday() == 0:
            try:
                from routers.weekly_report import router as wr
                # 鐢熸垚骞舵帹閫?
                await push_weekly_report({"summary": f"鏈懆鍋ュ悍鍒唟score}, CPU{cpu}%, 鍐呭瓨{mem.percent}%, 璁㈠崟{len(state._data.get("orders",[]))}"})
            except Exception as e:
                logger.info(f"鍛ㄦ姤鎺ㄩ€佽烦杩? {e}")
    except Exception as e:
        logger.info(f"鏃╂姤澶辫触: {e}")

async def metrics_record_task():
    """瀹氭椂璁板綍绯荤粺鎸囨爣"""
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
        logger.info(f"鎸囨爣璁板綍寮傚父: {e}")

def start_scheduler():
    """鍚姩瀹氭椂浠诲姟"""
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
    logger.info("瀹氭椂浠诲姟鍚姩瀹屾垚: 宸℃/澶囦唤/杞€?SSL缁/鍟嗗煄鎵弿/瀹㈡湇/鏃ヨ/鏃╂姤/鎸囨爣")


def stop_scheduler():
    """鍋滄瀹氭椂浠诲姟"""
    scheduler.shutdown(wait=False)
    logger.info("瀹氭椂浠诲姟宸插仠姝?)




