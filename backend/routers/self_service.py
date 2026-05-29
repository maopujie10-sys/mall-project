"""鑷姪杩愮淮 鈥?涓€閿瘖鏂?淇鍏ュ彛"""
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
    "mall_down": {"name": "鍟嗗煄鎵撲笉寮€璇婃柇", "class": MallDownRunbook, "risk": "L1"},
    "server_health": {"name": "鏈嶅姟鍣ㄥ仴搴锋鏌?, "class": ServerHealthRunbook, "risk": "L1"},
    "disk_full": {"name": "纾佺洏娓呯悊", "class": DiskFullRunbook, "risk": "L2"},
    "rotation_check": {"name": "杞€煎煙鍚嶅贰妫€", "class": RotationCheckRunbook, "risk": "L1"},
    "customer_order": {"name": "璁㈠崟闂鎺掓煡", "class": CustomerOrderRunbook, "risk": "L1"},
}

@router.get("/runbooks")
async def list_runbooks(_=Depends(verify_token)):
    """鏌ョ湅鎵€鏈夊彲鐢ㄨ嚜鍔╄繍缁村満鏅?""
    await handle_risk("L1", "鏌ョ湅鑷姪杩愮淮鍦烘櫙")
    return {
        "runbooks": [
            {"id": k, "name": v["name"], "risk": v["risk"]}
            for k, v in RUNBOOKS.items()
        ]
    }

@router.post("/run/{runbook_id}")
async def run_runbook(runbook_id: str, user_id: Optional[str] = None, order_id: Optional[str] = None, _=Depends(verify_token)):
    """鎵ц鑷姪杩愮淮鍦烘櫙"""
    if runbook_id not in RUNBOOKS:
        raise HTTPException(404, f"涓嶆敮鎸佺殑鍦烘櫙: {runbook_id}")

    info = RUNBOOKS[runbook_id]
    await handle_risk(info["risk"], f"鑷姪杩愮淮: {info['name']}")

    cls = RUNBOOKS[runbook_id]["class"]
    if runbook_id == "customer_order":
        rb = cls(user_id=user_id or "", order_id=order_id or "")
    else:
        rb = cls()

    report = await rb.run()

    # 濡傛灉鏈夊け璐ユ楠わ紝鑷姩鍒涘缓鍛婅
    if report["failed"] > 0:
        from routers.alert import _get_alerts
        from datetime import datetime
        alerts = _get_alerts()
        for step in report["steps"]:
            if not step["ok"]:
                alerts.insert(0, {
                    "id": f"alert_rb_{int(datetime.now().timestamp())}",
                    "level": "P3",
                    "level_name": "涓€鑸?,
                    "title": f"[鑷姪杩愮淮] {step['name']} 寮傚父",
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
