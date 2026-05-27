"""自助运维 — 一键诊断/修复入口"""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional
from auth import verify_token
from risk import handle_risk
from runbook.engine import (
    MallDownRunbook, ServerHealthRunbook, DiskFullRunbook,
    RotationCheckRunbook, CustomerOrderRunbook,
)

router = APIRouter(prefix="/self-service", tags=["SelfService"])

RUNBOOKS = {
    "mall_down": {"name": "商城打不开诊断", "class": MallDownRunbook, "risk": "L1"},
    "server_health": {"name": "服务器健康检查", "class": ServerHealthRunbook, "risk": "L1"},
    "disk_full": {"name": "磁盘清理", "class": DiskFullRunbook, "risk": "L2"},
    "rotation_check": {"name": "轮值域名巡检", "class": RotationCheckRunbook, "risk": "L1"},
}

@router.get("/runbooks")
async def list_runbooks(_=Depends(verify_token)):
    """查看所有可用自助运维场景"""
    await handle_risk("L1", "查看自助运维场景")
    return {
        "runbooks": [
            {"id": k, "name": v["name"], "risk": v["risk"]}
            for k, v in RUNBOOKS.items()
        ]
    }

@router.post("/run/{runbook_id}")
async def run_runbook(runbook_id: str, user_id: Optional[str] = None, order_id: Optional[str] = None, _=Depends(verify_token)):
    """执行自助运维场景"""
    if runbook_id not in RUNBOOKS:
        raise HTTPException(404, f"不支持的场景: {runbook_id}")

    info = RUNBOOKS[runbook_id]
    await handle_risk(info["risk"], f"自助运维: {info['name']}")

    if runbook_id == "customer_order":
        rb = CustomerOrderRunbook(user_id=user_id or "", order_id=order_id or "")
    else:
        rb = RUNBOOKS[runbook_id]["class"]()

    report = await rb.run()

    # 如果有失败步骤，自动创建告警
    if report["failed"] > 0:
        from routers.alert import _get_alerts
        from datetime import datetime
        alerts = _get_alerts()
        for step in report["steps"]:
            if not step["ok"]:
                alerts.insert(0, {
                    "id": f"alert_rb_{int(datetime.now().timestamp())}",
                    "level": "P3",
                    "level_name": "一般",
                    "title": f"[自助运维] {step['name']} 异常",
                    "detail": step["detail"],
                    "source": "self-service",
                    "time": datetime.now().strftime("%H:%M:%S"),
                    "resolved": False,
                    "resolved_at": None,
                })
        if len(alerts) > 200:
            alerts[:] = alerts[:200]
        state._save()

    return report
