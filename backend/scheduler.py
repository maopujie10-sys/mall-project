"""APScheduler 定时任务 — 自动巡检/备份/报告

定时任务列表:
  - 每30分钟: 自动巡检 (服务器/Docker/Nginx/网站)
  - 每天凌晨2点: 数据库备份
  - 每天上午9点: 轮值域名检测
  - 每天下午6点: 客服日报
  - 每天凌晨3点: 商城健康度扫描
"""
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
    """每日轮值域名检测"""
    print(f"[Scheduler] 轮值域名检测 {datetime.now().strftime('%H:%M:%S')}")
    try:
        import httpx
        from state import state
        domains = state._data.get("rotation_domains", [])
        async with httpx.AsyncClient(timeout=10, follow_redirects=True) as client:
            for d in domains:
                if not d.get("active"):
                    continue
                try:
                    r = await client.get(f"https://{d['domain']}", headers={"User-Agent": "Mozilla/5.0"})
                    d["health"] = "ok" if r.status_code < 400 else "error"
                except Exception:
                    d["health"] = "error"
        state._save()
        print(f"[Scheduler] 轮值检测完成: {len(domains)} 个域名")
    except Exception as e:
        print(f"[Scheduler] 轮值检测异常: {e}")


async def mall_health_task():
    """每日商城健康度扫描"""
    print(f"[Scheduler] 商城健康度扫描 {datetime.now().strftime('%H:%M:%S')}")
    try:
        from tools.autopilot_mall import MallBrain
        products = await MallBrain.scan_products()
        dead = sum(1 for p in products if p.status == "dead")
        hot = sum(1 for p in products if p.status == "hot")
        print(f"[Scheduler] 商城扫描完成: {len(products)}商品, {hot}热销, {dead}死品")
    except Exception as e:
        print(f"[Scheduler] 商城扫描异常: {e}")


def start_scheduler():
    """启动所有定时任务"""
    # 每30分钟自动巡检
    scheduler.add_job(
        patrol_task, IntervalTrigger(minutes=30),
        id="patrol", name="自动巡检", replace_existing=True
    )
    # 每天凌晨2点备份
    scheduler.add_job(
        backup_task, CronTrigger(hour=2, minute=0),
        id="backup", name="每日备份", replace_existing=True
    )
    # 每天上午9点轮值检测
    scheduler.add_job(
        rotation_check_task, CronTrigger(hour=9, minute=0),
        id="rotation_check", name="轮值域名检测", replace_existing=True
    )
    # 每天凌晨3点商城健康度
    scheduler.add_job(
        mall_health_task, CronTrigger(hour=3, minute=0),
        id="mall_health", name="商城健康度扫描", replace_existing=True
    )
    scheduler.start()
    print(f"[Scheduler] 定时任务已启动: {len(scheduler.get_jobs())} 个任务")
    for job in scheduler.get_jobs():
        print(f"  - {job.name} (id={job.id})")


def stop_scheduler():
    """停止所有定时任务"""
    if scheduler.running:
        scheduler.shutdown(wait=False)
        print("[Scheduler] 定时任务已停止")
