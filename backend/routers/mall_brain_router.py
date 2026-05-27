"""商城AI全自动运维 API — 扫描/分析/决策/执行"""
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from auth import verify_token
from risk import handle_risk
from tools.autopilot_mall import MallBrain

router = APIRouter(prefix="/agent/mall-brain", tags=["MallBrain"])

class AutoActionRequest(BaseModel):
    dry_run: bool = True  # True=仅分析不执行, False=真的执行

@router.post("/scan")
async def scan_products(_=Depends(verify_token)):
    """AI扫描全站商品，分析每个商品的健康度"""
    await handle_risk("L1", "AI扫描商品健康度")
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
    """AI生成商城运营分析报告"""
    await handle_risk("L1", "AI生成运营报告")
    products = await MallBrain.scan_products()
    report = MallBrain.generate_report(products)
    return {"ok": True, "report": report.__dict__}

@router.post("/auto")
async def auto_execute(req: AutoActionRequest, _=Depends(verify_token)):
    """AI自动执行运维决策 — 下架死品/采集新品/补库存"""
    risk_level = "L1" if req.dry_run else "L3"
    await handle_risk(risk_level, f"AI自动运维", f"dry_run={req.dry_run}")
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
    """查看品类缺口 — 哪些品类需要补货"""
    await handle_risk("L1", "查看品类缺口")
    products = await MallBrain.scan_products()
    gaps = MallBrain.find_category_gaps(products)
    return {
        "gaps": [{"category": g.category, "current": g.current_count, "target": g.target_count, "gap": g.gap, "keywords": g.hot_keywords} for g in gaps[:10]]
    }

@router.get("/summary")
async def brain_summary(_=Depends(verify_token)):
    """AI大脑一目了然总结"""
    await handle_risk("L1", "AI大脑总结")
    products = await MallBrain.scan_products()
    report = MallBrain.generate_report(products)
    return {
        "status": "🧠 AI大脑在线",
        "products_analyzed": len(products),
        "health": report.health_distribution,
        "top_gaps": [g["category"] for g in report.category_gaps[:3]],
        "top_suggestion": report.suggestions[0] if report.suggestions else "一切正常",
        "ready_actions": len(report.auto_actions),
        "next": "说「AI帮我运维商城」开始全自动运营",
    }