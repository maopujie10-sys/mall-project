锘?""AI鏅鸿兘瀹氫环API 鈥?鍗曞搧瀹氫环+鎵归噺瀹氫环+鍘嗗彶鏌ヨ+瀹氫环缁熻"""
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from typing import Optional
from auth import verify_token, require_role
from tools.pricing_engine import pricing_engine
from tools.logger import get_logger

logger = get_logger("pricing_router")
router = APIRouter(prefix="/agent/pricing", tags=["Pricing"])


class PriceRequest(BaseModel):
    product_id: str = ""
    product_name: str
    supply_price: float
    category: str = "鍏朵粬"
    shipping: float = 0
    packaging: float = 0
    target_margin: Optional[float] = None
    min_price: Optional[float] = None
    max_price: Optional[float] = None


class BatchPriceRequest(BaseModel):
    products: list


@router.post("/recommend")
async def recommend_price(req: PriceRequest, _=Depends(verify_token)):
    """鍗曞搧AI瀹氫环鎺ㄨ崘"""
    if req.supply_price <= 0:
        raise HTTPException(400, "渚涜揣浠峰繀椤诲ぇ浜?")
    try:
        result = await pricing_engine.recommend_price(
            product_id=req.product_id or f"p_{hash(req.product_name) % 100000}",
            product_name=req.product_name,
            supply_price=req.supply_price,
            category=req.category,
            shipping=req.shipping,
            packaging=req.packaging,
            target_margin=req.target_margin,
            min_price=req.min_price,
            max_price=req.max_price,
        )
        return {"ok": True, "data": result.__dict__}
    except Exception as e:
        logger.info(f"瀹氫环寮傚父: {e}")
        raise HTTPException(500, f"瀹氫环澶辫触: {str(e)[:200]}")


@router.post("/batch")
async def batch_recommend(req: BatchPriceRequest, _=Depends(verify_token)):
    """鎵归噺瀹氫环鎺ㄨ崘"""
    if not req.products:
        raise HTTPException(400, "浜у搧鍒楄〃涓嶈兘涓虹┖")
    if len(req.products) > 50:
        raise HTTPException(400, "鍗曟鏈€澶?0涓骇鍝?)
    try:
        results = await pricing_engine.batch_recommend(req.products)
        return {"ok": True, "total": len(results), "results": results}
    except Exception as e:
        raise HTTPException(500, f"鎵归噺瀹氫环澶辫触: {str(e)[:200]}")


@router.get("/history")
async def pricing_history(limit: int = Query(50, ge=1, le=200), _=Depends(verify_token)):
    """瀹氫环鎺ㄨ崘鍘嗗彶"""
    history = pricing_engine.get_history(limit)
    return {"ok": True, "total": len(history), "history": history}


@router.get("/stats")
async def pricing_stats(_=Depends(verify_token)):
    """瀹氫环缁熻鏁版嵁"""
    return {"ok": True, "stats": pricing_engine.get_stats()}


@router.get("/competition/{product_name}")
async def competition_analysis(product_name: str, category: str = Query("鍏朵粬"), _=Depends(verify_token)):
    """绔炲搧浠锋牸鍒嗘瀽"""
    result = await pricing_engine.analyze_competitors(product_name, category)
    return {"ok": True, "product": product_name, "competition": result}


# 绫荤洰鍒╂鼎鐜囧弬鑰?
@router.get("/margins")
async def category_margins(_=Depends(verify_token)):
    """绫荤洰寤鸿鍒╂鼎鐜?""
    from tools.pricing_engine import CATEGORY_MARGIN
    return {"ok": True, "margins": CATEGORY_MARGIN}
