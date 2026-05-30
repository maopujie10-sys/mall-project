"""APScheduler 定时任务 -- 巡检/备份/轮值/客服报告/商城扫描/日记
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
from tools.logger import get_logger
from tools.alert_push import push_weekly_report

# 最小间隔保护(秒) -- 防止任何定时任务低于此频率
MIN_SCHEDULE_INTERVAL = 60

scheduler = AsyncIOScheduler()
logger = get_logger("scheduler")


async def patrol_task():
    """服务器巡检 -- CPU/Docker/Nginx/网站"""
    now_str = datetime.now().strftime("%H:%M:%S")
    logger.info(f"服务器巡检 {now_str}")
    try:
        from routers.inspector import run_inspection
        await run_inspection()
    except Exception as e:
        logger.info(f"巡检异常: {e}")


async def backup_task():
    """每日数据库备份"""
    now_str = datetime.now().strftime("%H:%M:%S")
    logger.info(f"数据库备份 {now_str}")
    try:
        from routers.rollback_center import _load_backups, _save_backups
        import subprocess, os, tempfile
        from config import MALL_DB_HOST, MALL_DB_PORT, MALL_DB_USER, MALL_DB_PASSWORD, MALL_DB_NAME, BACKUP_DIR
        os.makedirs(BACKUP_DIR, exist_ok=True)
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = os.path.join(BACKUP_DIR, f"auto_backup_{ts}.sql")
        # 使用临时配置文件避免密码暴露在ps aux中
        fd, cnf_path = tempfile.mkstemp(suffix='.cnf')
        with os.fdopen(fd, 'w') as f:
            f.write(f"[client]\nuser={MALL_DB_USER}\npassword={MALL_DB_PASSWORD}\nhost={MALL_DB_HOST}\nport={MALL_DB_PORT}\n")
        os.chmod(cnf_path, 0o600)
        try:
            cmd = ["mysqldump", f"--defaults-extra-file={cnf_path}", MALL_DB_NAME]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
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
                logger.info(f"备份成功 {backup_path}")
            else:
                logger.info(f"备份失败: {result.stderr[:200]}")
        finally:
            os.unlink(cnf_path)
    except Exception as e:
        logger.info(f"备份异常: {e}")


async def rotation_check_task():
    """域名轮值检测 + 自动切换"""
    now_str = datetime.now().strftime("%H:%M:%S")
    logger.info(f"域名轮值检测 {now_str}")
    try:
        from routers.rotation_panel import _check_all
        result = await _check_all()
        if result.get("rotated_to"):
            logger.info(f"自动轮值 -> {result['rotated_to']}")
        logger.info(f"域名健康: {result.get('checked', 0)} 个已检测")
    except Exception as e:
        logger.info(f"域名轮值异常: {e}")


async def customer_report_task():
    """客服报告生成"""
    now_str = datetime.now().strftime("%H:%M:%S")
    logger.info(f"客服报告 {now_str}")
    try:
        from routers.customer_panel import _generate_report
        await _generate_report()
    except Exception as e:
        logger.info(f"客服报告异常: {e}")


async def diary_task():
    """每日日记自动生成"""
    now_str = datetime.now().strftime("%H:%M:%S")
    logger.info(f"日记生成 {now_str}")
    try:
        from services import DiaryService
        journal = DiaryService.generate_daily()
        path = DiaryService.save_journal(journal)
        logger.info(f"日记已保存 {path}")
    except Exception as e:
        logger.info(f"日记生成失败: {e}")


async def mall_scan_task():
    """商城扫描"""
    now_str = datetime.now().strftime("%H:%M:%S")
    logger.info(f"商城扫描 {now_str}")
    try:
        from routers.mall_scanner import run_scan
        await run_scan()
    except Exception as e:
        logger.info(f"商城扫描异常: {e}")



async def ssl_renew_check_task():
    """SSL证书到期检查 + 自动续签"""
    logger.info("SSL证书检查 {datetime.now().strftime('%H:%M:%S')}")
    try:
        from routers.ssl_router import _cert_valid, _issue
        from routers.rotation_panel import _get_domains
        domains = _get_domains()
        for d in domains:
            info = _cert_valid(d["domain"])
            if info.get("ok") and info.get("days_left", 0) > 30:
                continue
            logger.info("SSL到期({info.get('days_left', 0)}天), 自动续签: {d['domain']}")
            result = _issue(d["domain"], "")
            if result.get("ok"):
                logger.info("SSL续签成功: {d['domain']}")
            else:
                logger.info("SSL续签失败: {d['domain']} - {result.get('error', '')}")
    except Exception as e:
        logger.info(f"SSL检查异常: {e}")


async def daily_report_task():
    """每日8点生成运营早报"""
    try:
        from routers.daily_report import daily_report
        from auth import verify_token
        from fastapi import Depends
        logger.info("生成每日早报...")
        # 直接调用生成逻辑
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
        # 发通知
        state._data["last_notification"] = f"每日早报: 健康分{score}, CPU{cpu}%, 内存{mem.percent}%, 磁盘{disk.percent}%"
        state._save()
        logger.info(f"每日早报: 健康分{score}")
        # 周一自动推送周报
        if __import__("datetime").datetime.now().weekday() == 0:
            try:
                from routers.weekly_report import router as wr
                # 生成并推送
                await push_weekly_report({"summary": f"本周健康分{score}, CPU{cpu}%, 内存{mem.percent}%, 订单{len(state._data.get('orders',[]))}"})
            except Exception as e:
                logger.info(f"周报推送跳过: {e}")
    except Exception as e:
        logger.info(f"早报失败: {e}")

async def metrics_record_task():
    """定时记录系统指标"""
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
        logger.info(f"指标记录异常: {e}")

def start_scheduler():
    """启动定时任务"""
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
    logger.info("定时任务启动完成: 巡检/备份/轮值/SSL续签/商城扫描/客服/日记/早报/指标")


def stop_scheduler():
    """停止定时任务"""
    scheduler.shutdown(wait=False)
    logger.info("定时任务已停止")




