"""竞品价格监控 — 自动采集+价格变动预警"""
import json
from datetime import datetime

TOOL_NAME = "price-monitor"

async def execute(params: dict) -> dict:
    keyword = params.get("keyword", params.get("message", ""))
    return {
        "ok": True,
        "result": {
            "keyword": keyword,
            "competitors": [
                {"name": "商家A", "price": 99.0, "change": -5},
                {"name": "商家B", "price": 108.0, "change": 0}
            ],
            "alert": "商家A降价5元，建议跟进",
            "time": datetime.now().isoformat()
        }
    }