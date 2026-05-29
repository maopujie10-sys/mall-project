"""AI 鑷垜杩涘寲 API 鈥?璁板繂/瀛︿範/杩涘寲鎶ュ憡"""
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import Optional
from auth import verify_token
from risk import handle_risk
from tools.evolution import EvolutionEngine

router = APIRouter(prefix="/agent/evolution", tags=["Evolution"])

class CorrectionRequest(BaseModel):
    original_action: str
    user_said: str
    correct_approach: str
    context: str = ""

@router.get("/report")
async def evolution_report(_=Depends(verify_token)):
    """AI鑷垜杩涘寲鎶ュ憡 鈥?AI鍛婅瘔浣犲畠瀛﹀埌浜嗕粈涔?""
    await handle_risk("L1", "鏌ョ湅AI杩涘寲鎶ュ憡")
    return {"ok": True, "report": EvolutionEngine.evolve_report()}

@router.get("/memory")
async def recent_actions(_=Depends(verify_token), action_type: Optional[str] = None, limit: int = 30):
    """鏌ョ湅AI鐨勮鍔ㄨ蹇?""
    await handle_risk("L1", "鏌ョ湅AI璁板繂")
    actions = EvolutionEngine.get_action_history(action_type, limit)
    return {"ok": True, "actions": actions, "count": len(actions)}

@router.get("/knowledge")
async def knowledge_base(_=Depends(verify_token), category: Optional[str] = None):
    """鏌ョ湅AI瀛﹀埌鐨勭煡璇嗗簱"""
    await handle_risk("L1", "鏌ョ湅AI鐭ヨ瘑搴?)
    if category:
        data = EvolutionEngine.get_knowledge(category)
    else:
        from collections import defaultdict
        db = __import__('tools.evolution', fromlist=['_get_db'])._get_db()
        rows = db.execute("SELECT category, COUNT(*) as cnt, AVG(score) as avg_score FROM learning GROUP BY category").fetchall()
        db.close()
        data = [{"category": r["category"], "count": r["cnt"], "avg_score": round(r["avg_score"], 2)} for r in rows]
    return {"ok": True, "knowledge": data}

@router.post("/learn")
async def learn_from_user(req: CorrectionRequest, _=Depends(verify_token)):
    """鐢ㄦ埛绾犳AI 鈥?AI璁颁綇姝ｇ‘鍋氭硶"""
    await handle_risk("L2", "AI瀛︿範鐢ㄦ埛绾犳", req.user_said[:50])
    EvolutionEngine.learn_from_correction(
        original_action=req.original_action,
        user_said=req.user_said,
        correct_approach=req.correct_approach,
        context=req.context,
    )
    return {"ok": True, "message": "AI宸茶浣忎綘鐨勭籂姝ｏ紝涓嬫涓嶄細鍐嶇姱"}

@router.get("/corrections")
async def pending_corrections(_=Depends(verify_token)):
    """鏌ョ湅寰呭涔犵殑鐢ㄦ埛绾犳"""
    await handle_risk("L1", "鏌ョ湅AI寰呭涔犵籂姝?)
    return {"ok": True, "corrections": EvolutionEngine.get_corrections(learned=0)}

@router.post("/corrections/{correction_id}/learn")
async def mark_learned(correction_id: int, _=Depends(verify_token)):
    """鏍囪绾犳宸插浼?""
    await handle_risk("L1", "鏍囪绾犳宸插涔?)
    EvolutionEngine.mark_correction_learned(correction_id)
    return {"ok": True, "message": f"绾犳 #{correction_id} 宸插唴鍖?}

@router.get("/stats")
async def quick_stats(_=Depends(verify_token)):
    """AI蹇€熺粺璁?""
    await handle_risk("L1", "AI蹇€熺粺璁?)
    success_rate = EvolutionEngine.get_success_rate(days=7)
    best = EvolutionEngine.get_best_strategy("scraper_sources")
    return {
        "ok": True,
        "success_rate_7d": success_rate,
        "best_strategy": best,
        "motto": "馃К 鎴戝湪涓嶆柇杩涘寲涓?.." if success_rate > 70 else "馃摎 鎴戣繕鍦ㄥ涔犻樁娈?
    }