"""APScheduler 鐎规碍妞傛禒璇插 閳?閼奉亜濮╁鈩冾梾/婢跺洣鍞?閹躲儱鎲?
鐎规碍妞傛禒璇插閸掓銆?
  - 濮?0閸掑棝鎸? 閼奉亜濮╁鈩冾梾 (閺堝秴濮熼崳?Docker/Nginx/缂冩垹鐝?
  - 濮ｅ繐銇夐崙灞炬珤2閻? 閺佺増宓佹惔鎾愁槵娴?  - 濮ｅ繐銇夋稉濠傚磵9閻? 鏉烆喖鈧厧鐓欓崥宥嗩梾濞?  - 濮ｅ繐銇夋稉瀣磵6閻? 鐎广垺婀囬弮銉﹀Г
  - 濮ｅ繐銇夐崙灞炬珤3閻? 閸熷棗鐓勯崑銉ユ倣鎼达附澹傞幓?""
import asyncio
from datetime import datetime
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.triggers.cron import CronTrigger

scheduler = AsyncIOScheduler()


async def patrol_task():
    """鐎规碍妞傚鈩冾梾閿涙碍婀囬崝鈥虫珤/Docker/Nginx/缂冩垹鐝潻鐐衡偓姘偓?""
    print(f"[Scheduler] 閼奉亜濮╁鈩冾梾 {datetime.now().strftime('%H:%M:%S')}")
    try:
        from routers.inspector import run_inspection
        await run_inspection()
    except Exception as e:
        print(f"[Scheduler] 瀹糕剝顥呮径杈Е: {e}")


async def backup_task():
    """濮ｅ繑妫╅弫鐗堝祦鎼存挸顦禒?""
    print(f"[Scheduler] 濮ｅ繑妫╂径鍥﹀敜 {datetime.now().strftime('%H:%M:%S')}")
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
                "id": ts, "name": f"閼奉亜濮╂径鍥﹀敜_{ts}", "type": "auto",
                "target": "database", "path": backup_path,
                "size": len(result.stdout), "created_at": datetime.now().isoformat(),
            })
            _save_backups(records)
            print(f"[Scheduler] 婢跺洣鍞ょ€瑰本鍨? {backup_path}")
        else:
            print(f"[Scheduler] 婢跺洣鍞ゆ径杈Е: {result.stderr[:200]}")
    except Exception as e:
        print(f"[Scheduler] 婢跺洣鍞ゅ鍌氱埗: {e}")


async def rotation_check_task():
    """鏉烆喖鈧厧鐓欓崥宥嗩梾濞?""
    print(f"[Scheduler] 鏉烆喖鈧吋顥呭ù?{datetime.now().strftime('%H:%M:%S')}")
    try:
        from routers.rotation_panel import _check_all
        await _check_all()
    except Exception as e:
        print(f"[Scheduler] 鏉烆喖鈧吋顥呭ù瀣亼鐠? {e}")


async def customer_report_task():
    """鐎广垺婀囬弮銉﹀Г"""
    print(f"[Scheduler] 鐎广垺婀囬弮銉﹀Г {datetime.now().strftime('%H:%M:%S')}")
    try:
        from routers.customer_panel import _generate_report
        await _generate_report()
    except Exception as e:
        print(f"[Scheduler] 鐎广垺婀囬弮銉﹀Г婢惰精瑙? {e}")


async def diary_task():
    """姣忔棩鏃ヨ鑷姩鐢熸垚"""
    print(f"[Scheduler] 鏃ヨ鐢熸垚 {datetime.now().strftime("%H:%M:%S")}")
    try:
        from services import DiaryService
        journal = DiaryService.generate_daily()
        path = DiaryService.save_journal(journal)
        print(f"[Scheduler] 鏃ヨ宸蹭繚瀛? {path}")
    except Exception as e:
        print(f"[Scheduler] 鏃ヨ鐢熸垚澶辫触: {e}")


async def mall_scan_task():
    """閸熷棗鐓勯崑銉ユ倣鎼达附澹傞幓?""
    print(f"[Scheduler] 閸熷棗鐓勯幍顐ｅ伎 {datetime.now().strftime('%H:%M:%S')}")
    try:
        from routers.mall_scanner import run_scan
        await run_scan()
    except Exception as e:
        print(f"[Scheduler] 閸熷棗鐓勯幍顐ｅ伎婢惰精瑙? {e}")


def start_scheduler():
    """閸氼垰濮╃€规碍妞傛禒璇插"""
    scheduler.add_job(patrol_task, IntervalTrigger(minutes=30), id="patrol", replace_existing=True)
    scheduler.add_job(backup_task, CronTrigger(hour=2, minute=0), id="backup", replace_existing=True)
    scheduler.add_job(rotation_check_task, CronTrigger(hour=9, minute=0), id="rotation", replace_existing=True)
    scheduler.add_job(customer_report_task, CronTrigger(hour=18, minute=0), id="customer_report", replace_existing=True)
    scheduler.add_job(mall_scan_task, CronTrigger(hour=3, minute=0), id="mall_scan", replace_existing=True)
    scheduler.add_job(diary_task, CronTrigger(hour=23, minute=55), id="diary", replace_existing=True)
    scheduler.start()
    print("[Scheduler] 鐎规碍妞傛禒璇插瀹告彃鎯庨崝? 瀹糕剝顥?婢跺洣鍞?鏉烆喖鈧?閺冦儲濮?閹殿偅寮?)


def stop_scheduler():
    """閸嬫粍顒涚€规碍妞傛禒璇插"""
    scheduler.shutdown(wait=False)
    print("[Scheduler] 鐎规碍妞傛禒璇插瀹告彃浠犲?)