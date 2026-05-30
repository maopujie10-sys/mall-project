""" — +"""
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
                {"name": "A", "price": 99.0, "change": -5},
                {"name": "B", "price": 108.0, "change": 0}
            ],
            "alert": "A5",
            "time": datetime.now().isoformat()
        }
    }