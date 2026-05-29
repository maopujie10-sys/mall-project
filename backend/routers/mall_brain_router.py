"""AI 商城大脑 API — 商品扫描/运营报告/自动执行"""
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from auth import verify_token
from risk import handle_risk
from tools.autopilot_mall import MallBrain

router = APIRouter(prefix="/agent/mall-brain", tags=["MallBrain"])

class AutoActionRequest(BaseModel):
    dry_run: bool = True  # True=仅预览不执行, False=真实执行

@router.post("/scan")
async def scan_products(_=Depends(verify_token)):
    """扫描商品并分析健康状态"""
    await handle_risk("L1", "AI 扫描商品")
    products = await MallBrain.scan_products()
    return {
        "total": len(products),
        "distribution": {
            "hot": len([p for p in products if p.status == "hot"]),
            "warm": len([p for p in products if p.status == "warm"]),
            "cold": len([p for p in products if p.status == "cold"]),
            "dead": len([p for p in products if p.status == "dead"]),
        },
        "products": [{
            "id": p.product_id, "title": p.title, "category": p.category,
            "price": p.price, "sales": p.sales, "stock": p.stock,
            "health_score": round(p.health_score, 1), "status": p.status,
            "recommendation": p.recommendation,
        } for p in products[:50]],
    }

@router.get("/report")
async def generate_report(_=Depends(verify_token)):
    """生成商城运营报告"""
    await handle_risk("L1", "AI 大脑操作")
    products = await MallBrain.scan_products()
    report = MallBrain.generate_report(products)
    return {"ok": True, "report": report.__dict__}

@router.post("/auto")
async def auto_execute(req: AutoActionRequest, _=Depends(verify_token)):
    """AI自动执行运营建议，dry_run=True时仅预览"""
    risk_level = "L1" if req.dry_run else "L3"
    await handle_risk(risk_level, "AI自动执行运营操作", f"dry_run={req.dry_run}")
    products = await MallBrain.scan_products()
    report = MallBrain.generate_report(products)
    result = await MallBrain.execute_auto_actions(report, dry_run=req.dry_run)
    return {
        "ok": True,
        "dry_run": req.dry_run,
        "report_summary": {
            "total": report.total_products,
            "hot": report.hot_products,
            "dead": report.dead_products,
            "suggestions": report.suggestions[:5],
        },
        "execution": result,
    }

@router.get("/gaps")
async def category_gaps(_=Depends(verify_token)):
    """查找品类缺口和热门关键词"""
    await handle_risk("L1", "AI 大脑操作")
    products = await MallBrain.scan_products()
    gaps = MallBrain.find_category_gaps(products)
    return {
        "gaps": [{"category": g.category, "current": g.current_count, "target": g.target_count, "gap": g.gap, "keywords": g.hot_keywords} for g in gaps[:10]]
    }

@router.get("/summary")
async def brain_summary(_=Depends(verify_token)):
    """AI 商城大脑状态摘要"""
    await handle_risk("L1", "AI 商城大脑状态")
    products = await MallBrain.scan_products()
    report = MallBrain.generate_report(products)
    return {
        "status": "Friday AI 商城大脑运行中",
        "products_analyzed": len(products),
        "health": report.health_distribution,
        "top_gaps": [g["category"] for g in report.category_gaps[:3]],
        "top_suggestion": report.suggestions[0] if report.suggestions else "暂无建议",
        "ready_actions": len(report.auto_actions),
        "next": "等待 AI 自动执行下轮运营操作，或手动触发 /auto 接口执行建议动作",
    }
