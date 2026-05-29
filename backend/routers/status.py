"""鍏ㄧ珯鏈嶅姟鐘舵€?鈥?妫€鏌?mall-app 杩為€氭€?""
from fastapi import APIRouter, Depends
from auth import verify_token
from config import MALL_BASE_URL
from risk import handle_risk
import httpx

router = APIRouter(prefix="/agent", tags=["Status"])

@router.get("/status")
async def all_status(_=Depends(verify_token)):
    await handle_risk("L1", "鏌ョ湅鍏ㄧ珯鐘舵€?)
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
    await handle_risk("L1", "鏌ョ湅鍏ㄧ珯鐘舵€?璇︾粏)")
    try:
        async with httpx.AsyncClient(timeout=5) as c:
            r = await c.get(f"{MALL_BASE_URL}/agent/health")
            return {"code": r.status_code, "data": r.json() if r.status_code == 200 else r.text}
    except Exception as e:
        return {"code": 503, "error": str(e)}
