"""AI 鍟嗗煄澶ц剳 API 鈥?鍟嗗搧鎵弿/杩愯惀鎶ュ憡/鑷姩鎵ц"""
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from auth import verify_token
from risk import handle_risk
from tools.autopilot_mall import MallBrain

router = APIRouter(prefix="/agent/mall-brain", tags=["MallBrain"])

class AutoActionRequest(BaseModel):
    dry_run: bool = True  # True=浠呴瑙堜笉鎵ц, False=鐪熷疄鎵ц

@router.post("/scan")
async def scan_products(_=Depends(verify_token)):
    """鎵弿鍟嗗搧骞跺垎鏋愬仴搴风姸鎬?""
    await handle_risk("L1", "AI 鎵弿鍟嗗搧")
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
    """鐢熸垚鍟嗗煄杩愯惀鎶ュ憡"""
    await handle_risk("L1", "AI 澶ц剳鎿嶄綔")
    products = await MallBrain.scan_products()
    report = MallBrain.generate_report(products)
    return {"ok": True, "report": report.__dict__}

@router.post("/auto")
async def auto_execute(req: AutoActionRequest, _=Depends(verify_token)):
    """AI鑷姩鎵ц杩愯惀寤鸿锛宒ry_run=True鏃朵粎棰勮"""
    risk_level = "L1" if req.dry_run else "L3"
    await handle_risk(risk_level, "AI鑷姩鎵ц杩愯惀鎿嶄綔", f"dry_run={req.dry_run}")
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
    """鏌ユ壘鍝佺被缂哄彛鍜岀儹闂ㄥ叧閿瘝"""
    await handle_risk("L1", "AI 澶ц剳鎿嶄綔")
    products = await MallBrain.scan_products()
    gaps = MallBrain.find_category_gaps(products)
    return {
        "gaps": [{"category": g.category, "current": g.current_count, "target": g.target_count, "gap": g.gap, "keywords": g.hot_keywords} for g in gaps[:10]]
    }

@router.get("/summary")
async def brain_summary(_=Depends(verify_token)):
    """AI 鍟嗗煄澶ц剳鐘舵€佹憳瑕?""
    await handle_risk("L1", "AI 鍟嗗煄澶ц剳鐘舵€?)
    products = await MallBrain.scan_products()
    report = MallBrain.generate_report(products)
    return {
        "status": "Friday AI 鍟嗗煄澶ц剳杩愯涓?,
        "products_analyzed": len(products),
        "health": report.health_distribution,
        "top_gaps": [g["category"] for g in report.category_gaps[:3]],
        "top_suggestion": report.suggestions[0] if report.suggestions else "鏆傛棤寤鸿",
        "ready_actions": len(report.auto_actions),
        "next": "绛夊緟 AI 鑷姩鎵ц涓嬭疆杩愯惀鎿嶄綔锛屾垨鎵嬪姩瑙﹀彂 /auto 鎺ュ彛鎵ц寤鸿鍔ㄤ綔",
    }
