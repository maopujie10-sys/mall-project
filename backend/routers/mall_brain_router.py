"""閸熷棗鐓凙I閸忋劏鍤滈崝銊ㄧ箥缂API 閳閹殿偅寮閸掑棙鐎閸愬磭鐡閹笛嗩攽"""
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from auth import verify_token
from risk import handle_risk
from tools.autopilot_mall import MallBrain

router = APIRouter(prefix="/agent/mall-brain", tags=["MallBrain"])

class AutoActionRequest(BaseModel):
    dry_run: bool = True  # True=娴犲懎鍨庨弸鎰瑝閹笛嗩攽, False=閻喓娈戦幍褑顢
@router.post("/scan")
async def scan_products(_=Depends(verify_token)):
    """AI閹殿偅寮块崗銊х彲閸熷棗鎼ч敍灞藉瀻閺嬫劖鐦℃稉顏勬櫌閸濅胶娈戦崑銉ユ倣鎼""
    await handle_risk("L1", "AI閹殿偅寮块崯鍡楁惂閸嬨儱鎮嶆惔)
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
    """AI閻㈢喐鍨氶崯鍡楃厔鏉╂劘鎯閸掑棙鐎介幎銉ユ啞"""
    await handle_risk("L1", "AI澶ц剳鎿嶄綔")
    products = await MallBrain.scan_products()
    report = MallBrain.generate_report(products)
    return {"ok": True, "report": report.__dict__}

@router.post("/auto")
async def auto_execute(req: AutoActionRequest, _=Depends(verify_token)):
    """AI閼奉亜╅幍褑顢戞潻鎰樊閸愬磭鐡閳娑撳鐏﹀璇叉惂/闁插洭娉﹂弬鏉挎惂/鐞涖儱绨辩""
    risk_level = "L1" if req.dry_run else "L3"
    await handle_risk(risk_level, f"AI閼奉亜╂潻鎰樊", f"dry_run={req.dry_run}")
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
    """閺屻儳婀呴崫浣鸿缂傚搫褰閳閸濐亙绨洪崫浣鸿闂団偓鐟曚浇藟""
    await handle_risk("L1", "AI澶ц剳鎿嶄綔")
    products = await MallBrain.scan_products()
    gaps = MallBrain.find_category_gaps(products)
    return {
        "gaps": [{"category": g.category, "current": g.current_count, "target": g.target_count, "gap": g.gap, "keywords": g.hot_keywords} for g in gaps[:10]]
    }

@router.get("/summary")
async def brain_summary(_=Depends(verify_token)):
    """AI婢堆嗗壋娑撯偓閻╊喕绨￠悞鑸碘偓鑽ょ波"""
    await handle_risk("L1", "AI澶ц剳鎿嶄綔")
    products = await MallBrain.scan_products()
    report = MallBrain.generate_report(products)
    return {
        "status": "棣冾潵 AI婢堆嗗壋閸︺劎鍤,
        "products_analyzed": len(products),
        "health": report.health_distribution,
        "top_gaps": [g["category"] for g in report.category_gaps[:3]],
        "top_suggestion": report.suggestions[0] if report.suggestions else "娑撯偓閸掑洦顒滅敮,
        "ready_actions": len(report.auto_actions),
        "next": "囨番鈧瓑I鐢喗鍨滄潻鎰樊閸熷棗鐓勯妴宥呯磻婵鍙忛懛顏勫З鏉╂劘鎯",
    }