"""虚拟数据生成 — 让商城看起来热闹"""
from fastapi import APIRouter, Depends
from main import verify_token
from config import MALL_BASE_URL
import httpx

router = APIRouter(prefix="/agent/virtual", tags=["Virtual Data"])

@router.get("/status")
async def virtual_status(_=Depends(verify_token)):
    """查看虚拟数据覆盖状态"""
    result = {"virtual_enabled": True, "actions_available": ["orders", "reviews", "views"]}
    try:
        async with httpx.AsyncClient(timeout=5) as c:
            # 尝试调商城接口获取真实统计
            r = await c.get(f"{MALL_BASE_URL}/agent/health")
            result["mall_live"] = r.status_code == 200
    except:
        result["mall_live"] = False
    return result

@router.post("/generate")
async def generate_virtual(type: str = "all", count: int = 10, _=Depends(verify_token)):
    """生成虚拟数据: type=orders|reviews|views|all"""
    results = {}

    if type in ("orders", "all"):
        results["orders"] = f"准备生成 {count} 条虚拟订单（需商城API配合）"
    if type in ("reviews", "all"):
        results["reviews"] = f"准备补充 {count} 条虚拟评价（需提供商品ID列表）"
    if type in ("views", "all"):
        results["views"] = f"准备为 {count} 个商品增加浏览量"

    results["note"] = "当前为模拟模式，真实写入需对接商城API"
    return results

@router.post("/toggle")
async def toggle_virtual(enabled: bool = True, _=Depends(verify_token)):
    """全局开关虚拟数据"""
    return {"virtual_enabled": enabled, "note": "开关状态已更新（需Redis持久化）"}
