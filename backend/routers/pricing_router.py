"""AI智能定价API — 单品定价+批量定价+历史查询+定价统计"""
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
    category: str = "其他"
    shipping: float = 0
    packaging: float = 0
    target_margin: Optional[float] = None
    min_price: Optional[float] = None
    max_price: Optional[float] = None


class BatchPriceRequest(BaseModel):
    products: list


@router.post("/recommend")
async def recommend_price(req: PriceRequest, _=Depends(verify_token)):
    """单品AI定价推荐"""
    if req.supply_price <= 0:
        raise HTTPException(400, "供货价必须大于0")
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
        logger.info(f"定价异常: {e}")
        raise HTTPException(500, f"定价失败: {str(e)[:200]}")


@router.post("/batch")
async def batch_recommend(req: BatchPriceRequest, _=Depends(verify_token)):
    """批量定价推荐"""
    if not req.products:
        raise HTTPException(400, "产品列表不能为空")
    if len(req.products) > 50:
        raise HTTPException(400, "单次最多50个产品")
    try:
        results = await pricing_engine.batch_recommend(req.products)
        return {"ok": True, "total": len(results), "results": results}
    except Exception as e:
        raise HTTPException(500, f"批量定价失败: {str(e)[:200]}")


@router.get("/history")
async def pricing_history(limit: int = Query(50, ge=1, le=200), _=Depends(verify_token)):
    """定价推荐历史"""
    history = pricing_engine.get_history(limit)
    return {"ok": True, "total": len(history), "history": history}


@router.get("/stats")
async def pricing_stats(_=Depends(verify_token)):
    """定价统计数据"""
    return {"ok": True, "stats": pricing_engine.get_stats()}


@router.get("/competition/{product_name}")
async def competition_analysis(product_name: str, category: str = Query("其他"), _=Depends(verify_token)):
    """竞品价格分析"""
    result = await pricing_engine.analyze_competitors(product_name, category)
    return {"ok": True, "product": product_name, "competition": result}


# 类目利润率参考
@router.get("/margins")
async def category_margins(_=Depends(verify_token)):
    """类目建议利润率"""
    from tools.pricing_engine import CATEGORY_MARGIN
    return {"ok": True, "margins": CATEGORY_MARGIN}
