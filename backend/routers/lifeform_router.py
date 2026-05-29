"""数字生命体 API — 状态/情绪/洞察/梦境/进化"""
from fastapi import APIRouter, Depends
from auth import verify_token
from digital_lifeform import DigitalLifeform

router = APIRouter(prefix="/agent/lifeform", tags=["Lifeform"])

@router.get("/status")
async def lifeform_status(_=Depends(verify_token)):
    """生命体完整状态"""
    return {"ok": True, **DigitalLifeform.get_lifeform_status()}

@router.get("/mood")
async def lifeform_mood(_=Depends(verify_token)):
    """当前情绪"""
    return {"ok": True, "mood": DigitalLifeform.get_mood()}

@router.get("/insights")
async def lifeform_insights(_=Depends(verify_token)):
    """最新洞察"""
    insights = DigitalLifeform.generate_insights()
    return {"ok": True, "insights": insights, "count": len(insights)}

@router.get("/dreams")
async def lifeform_dreams(_=Depends(verify_token)):
    """梦境记录"""
    return {"ok": True, "dreams": DigitalLifeform._dream_log[-10:]}

@router.get("/reflection")
async def lifeform_reflection(_=Depends(verify_token)):
    """当前反思"""
    return {"ok": True, "reflection": DigitalLifeform.reflect()}

@router.post("/cycle")
async def force_cycle(_=Depends(verify_token)):
    """强制触发一个自主循环"""
    from digital_lifeform import DigitalLifeform
    result = await DigitalLifeform.one_cycle()
    return {"ok": True, "cycle": result}
