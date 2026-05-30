""" -- /"""
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
    "mall_down": {"name": '', "class": MallDownRunbook, "risk": "L1"},
    "server_health": {"name": '', "class": ServerHealthRunbook, "risk": "L1"},
    "disk_full": {"name": '', "class": DiskFullRunbook, "risk": "L2"},
    "rotation_check": {"name": '', "class": RotationCheckRunbook, "risk": "L1"},
    "customer_order": {"name": '', "class": CustomerOrderRunbook, "risk": "L1"},
}

@router.get("/runbooks")
async def list_runbooks(_=Depends(verify_token)):
    ''''''
    await handle_risk("L1", '')
    return {
        "runbooks": [
            {"id": k, "name": v["name"], "risk": v["risk"]}
            for k, v in RUNBOOKS.items()
        ]
    }

@router.post("/run/{runbook_id}")
async def run_runbook(runbook_id: str, user_id: Optional[str] = None, order_id: Optional[str] = None, _=Depends(verify_token)):
    ''''''
    if runbook_id not in RUNBOOKS:
        raise HTTPException(404, f": {runbook_id}")

    info = RUNBOOKS[runbook_id]
    await handle_risk(info["risk"], f": {info['name']}")

    cls = RUNBOOKS[runbook_id]["class"]
    if runbook_id == "customer_order":
        rb = cls(user_id=user_id or '', order_id=order_id or '')
    else:
        rb = cls()

    report = await rb.run()

    # ,
    if report["failed"] > 0:
        from routers.alert import _get_alerts
        from datetime import datetime
        alerts = _get_alerts()
        for step in report["steps"]:
            if not step["ok"]:
                alerts.insert(0, {
                    "id": f"alert_rb_{int(datetime.now().timestamp())}",
                    "level": "P3",
                    "level_name": '',
                    "title": f"[] {step['name']} ",
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
