"""虚拟数据 API -- 一键造数据/实时活动/仪表盘统计"""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional
from auth import verify_token
from risk import handle_risk
from tools.virtual_data import VirtualDataEngine
from state import state

router = APIRouter(prefix="/agent/virtual", tags=["VirtualData"])

class GenerateRequest(BaseModel):
    scale: str = "small"  # small/medium/large/huge
    target: Optional[str] = None  # 可选: users/products/orders/all

class RealtimeRequest(BaseModel):
    count: int = 20

# ═══════════════════════════════════════
#  API
# ═══════════════════════════════════════

@router.post("/generate")
async def generate_data(req: GenerateRequest, _=Depends(verify_token)):
    """一键生成虚拟数据 -- 用户/商品/订单/K线/客服/签到/内容"""
    await handle_risk("L3", f"生成虚拟数据", f"scale={req.scale} target={req.target or 'all'}")
    if req.scale not in ("small","medium","large","huge"):
        raise HTTPException(400, "scale must be: small/medium/large/huge")

    result = VirtualDataEngine.generate_all(req.scale)

    # 存储到 state
    state._data["virtual_data_last"] = {
        "scale": req.scale,
        "stats": result["stats"],
        "generated_at": result["generated_at"],
    }
    state._save()

    return {"ok": True, "scale": req.scale, "stats": result["stats"], "data_preview": str(result["data"].keys())}

@router.post("/realtime")
async def realtime_activity(req: Optional[RealtimeRequest] = None, _=Depends(verify_token)):
    """生成实时活动日志 -- 模拟平台有真人正在使用"""
    await handle_risk("L1", "查看实时活动")
    count = req.count if req else 20
    activities = VirtualDataEngine.generate_realtime_activity(count)
    return {"activities": activities, "count": len(activities)}

@router.get("/dashboard")
async def dashboard_stats(_=Depends(verify_token)):
    """仪表盘实时统计数据 -- 今日新增/交易额/在线人数"""
    await handle_risk("L1", "查看虚拟数据看板")
    stats = VirtualDataEngine.get_dashboard_stats()
    return {"ok": True, "stats": stats}

@router.get("/stats")
async def data_stats(_=Depends(verify_token)):
    """查看已生成的虚拟数据统计"""
    await handle_risk("L1", "查看虚拟数据统计")
    last = state._data.get("virtual_data_last", {})
    return {"last_generation": last, "current_stats": VirtualDataEngine.get_dashboard_stats()}

@router.get("/preview/users")
async def preview_users(_=Depends(verify_token), limit: int = 10):
    """查看生成的示例用户数据"""
    await handle_risk("L1", "预览虚拟用户")
    last = state._data.get("virtual_data_last", {})
    return {"users_preview": last.get("data", {}).get("users", [])[:limit]}

@router.get("/scales")
async def list_scales(_=Depends(verify_token)):
    """查看可用数据规模"""
    await handle_risk("L1", "查看生成规模")
    return {
        "scales": {
            "small": {"users": 1000, "products": 500, "说明": "小型平台,适合测试"},
            "medium": {"users": 5000, "products": 2000, "说明": "中型平台,像区域电商"},
            "large": {"users": 20000, "products": 5000, "说明": "大型平台,像主流商城"},
            "huge": {"users": 50000, "products": 10000, "说明": "巨型平台,像淘宝京东"},
        }
    }