"""AI 自我进化 API — 记忆/学习/进化报告"""
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
    """AI自我进化报告 — AI告诉你它学到了什么"""
    await handle_risk("L1", "查看AI进化报告")
    return {"ok": True, "report": EvolutionEngine.evolve_report()}

@router.get("/memory")
async def recent_actions(_=Depends(verify_token), action_type: Optional[str] = None, limit: int = 30):
    """查看AI的行动记忆"""
    await handle_risk("L1", "查看AI记忆")
    actions = EvolutionEngine.get_action_history(action_type, limit)
    return {"ok": True, "actions": actions, "count": len(actions)}

@router.get("/knowledge")
async def knowledge_base(_=Depends(verify_token), category: Optional[str] = None):
    """查看AI学到的知识库"""
    await handle_risk("L1", "查看AI知识库")
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
    """用户纠正AI — AI记住正确做法"""
    await handle_risk("L2", "AI学习用户纠正", req.user_said[:50])
    EvolutionEngine.learn_from_correction(
        original_action=req.original_action,
        user_said=req.user_said,
        correct_approach=req.correct_approach,
        context=req.context,
    )
    return {"ok": True, "message": "AI已记住你的纠正，下次不会再犯"}

@router.get("/corrections")
async def pending_corrections(_=Depends(verify_token)):
    """查看待学习的用户纠正"""
    await handle_risk("L1", "查看AI待学习纠正")
    return {"ok": True, "corrections": EvolutionEngine.get_corrections(learned=0)}

@router.post("/corrections/{correction_id}/learn")
async def mark_learned(correction_id: int, _=Depends(verify_token)):
    """标记纠正已学会"""
    await handle_risk("L1", "标记纠正已学习")
    EvolutionEngine.mark_correction_learned(correction_id)
    return {"ok": True, "message": f"纠正 #{correction_id} 已内化"}

@router.get("/stats")
async def quick_stats(_=Depends(verify_token)):
    """AI快速统计"""
    await handle_risk("L1", "AI快速统计")
    success_rate = EvolutionEngine.get_success_rate(days=7)
    best = EvolutionEngine.get_best_strategy("scraper_sources")
    return {
        "ok": True,
        "success_rate_7d": success_rate,
        "best_strategy": best,
        "motto": "🧬 我在不断进化中..." if success_rate > 70 else "📚 我还在学习阶段"
    }