"""全站服务状态 — 检查mall-app连通性"""
from fastapi import APIRouter, Depends
from main import verify_token
from config import MALL_BASE_URL
import httpx

router = APIRouter(prefix="/agent", tags=["Status"])

@router.get("/status")
async def all_status(_=Depends(verify_token)):
    """检查mall-app健康 + 本机状态"""
    mall_ok = False
    mall_detail = "unknown"
    try:
        async with httpx.AsyncClient(timeout=5) as c:
            r = await c.get(f"{MALL_BASE_URL}/agent/health")
            mall_ok = r.status_code == 200
            mall_detail = r.text[:200]
    except Exception as e:
        mall_detail = str(e)

    return {
        "agent": "running",
        "mall_app": "healthy" if mall_ok else "unreachable",
        "mall_url": MALL_BASE_URL,
        "mall_detail": mall_detail,
    }

@router.get("/status/full")
async def full_status(_=Depends(verify_token)):
    """检查mall-app详细状态（调用商城自己的health接口）"""
    try:
        async with httpx.AsyncClient(timeout=5) as c:
            r = await c.get(f"{MALL_BASE_URL}/agent/health")
            return {"code": r.status_code, "data": r.json() if r.status_code == 200 else r.text}
    except Exception as e:
        return {"code": 503, "error": str(e)}
