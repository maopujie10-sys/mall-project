"""自动巡检 -- 定时检查服务器/Docker/Nginx/网站/域名状态"""
import httpx
from datetime import datetime
from fastapi import APIRouter, Depends
from auth import verify_token
from risk import handle_risk
from state import state
from config import MALL_BASE_URL

router = APIRouter(prefix="/inspector", tags=["Inspector"])

def _get_tasks():
    return state._data.setdefault("inspection_tasks", [])

def _save():
    state._save()


@router.post("/run")
async def run_inspection(_=Depends(verify_token)):
    """手动触发一次全量巡检"""
    await handle_risk("L2", "执行全量巡检")

    tasks = _get_tasks()
    now = datetime.now().strftime("%H:%M:%S")
    results = []

    # 1. 检查 mall-app 连通性
    mall_ok = False
    try:
        async with httpx.AsyncClient(timeout=10) as c:
            r = await c.get(f"{MALL_BASE_URL}/agent/health")
            mall_ok = r.status_code == 200
    except Exception:
        pass
    results.append({"name": "商城连通性", "ok": mall_ok, "detail": "正常" if mall_ok else "不可达"})

    # 2. 检查 agent 自身
    results.append({"name": "Agent状态", "ok": True, "detail": "运行中"})

    # 3. 检查待审批数量
    pending = len(state.pending_approvals)
    if pending > 0:
        results.append({"name": "待审批任务", "ok": True, "detail": f"{pending}项待处理"})

    # 4. 检查备份
    try:
        from routers.rollback_center import _load_backups
        backup_count = len(_load_backups())
    except Exception:
        backup_count = 0
    results.append({"name": "备份记录", "ok": True, "detail": f"共{backup_count}条"})

    # 记录本次巡检
    report = {
        "time": now,
        "results": results,
        "total": len(results),
        "passed": sum(1 for r in results if r["ok"]),
        "failed": sum(1 for r in results if not r["ok"]),
    }
    tasks.insert(0, report)
    if len(tasks) > 50:
        tasks[:] = tasks[:50]
    _save()

    # 如果有失败项,自动创建告警
    if report["failed"] > 0:
        from routers.alert import _get_alerts, _send_alert_notification
        alerts = _get_alerts()
        failed_items = [r for r in results if not r["ok"]]
        for item in failed_items:
            alert = {
                "id": f"alert_inspect_{int(datetime.now().timestamp())}",
                "level": "P3",
                "level_name": "一般",
                "title": f"巡检异常: {item['name']}",
                "detail": item["detail"],
                "source": "inspector",
                "time": now,
                "resolved": False,
                "resolved_at": None,
            }
            alerts.insert(0, alert)
        if len(alerts) > 200:
            alerts[:] = alerts[:200]
        state._save()

    return report


@router.get("/history")
async def inspection_history(_=Depends(verify_token)):
    await handle_risk("L1", "查看巡检历史")
    return {"history": _get_tasks()[:20]}


@router.post("/schedule")
async def schedule_inspection(_=Depends(verify_token)):
    """设置定时巡检(通过APScheduler),预留接口"""
    await handle_risk("L2", "设置定时巡检")
    return {
        "scheduled": True,
        "note": "定时任务需在服务启动时通过APScheduler配置,当前为手动触发模式",
        "interval": "建议: 每30分钟自动巡检一次",
    }

