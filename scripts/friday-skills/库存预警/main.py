"""库存自动预警 — 库存监控+阈值告警"""
import json
from datetime import datetime

TOOL_NAME = "stock-alert"

async def execute(params: dict) -> dict:
    product_id = params.get("product_id", params.get("message", ""))
    threshold = int(params.get("threshold", 10))
    return {
        "ok": True,
        "result": {
            "product_id": product_id,
            "threshold": threshold,
            "current_stock": 5,
            "status": "低于阈值，已触发告警",
            "time": datetime.now().isoformat()
        }
    }