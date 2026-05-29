锘?""鏁板瓧鐢熷懡浣?API 鈥?鐘舵€?鎯呯华/娲炲療/姊﹀/杩涘寲"""
from fastapi import APIRouter, Depends
from auth import verify_token
from digital_lifeform import DigitalLifeform

router = APIRouter(prefix="/agent/lifeform", tags=["Lifeform"])

@router.get("/status")
async def lifeform_status(_=Depends(verify_token)):
    """鐢熷懡浣撳畬鏁寸姸鎬?""
    return {"ok": True, **DigitalLifeform.get_lifeform_status()}

@router.get("/mood")
async def lifeform_mood(_=Depends(verify_token)):
    """褰撳墠鎯呯华"""
    return {"ok": True, "mood": DigitalLifeform.get_mood()}

@router.get("/insights")
async def lifeform_insights(_=Depends(verify_token)):
    """鏈€鏂版礊瀵?""
    insights = DigitalLifeform.generate_insights()
    return {"ok": True, "insights": insights, "count": len(insights)}

@router.get("/dreams")
async def lifeform_dreams(_=Depends(verify_token)):
    """姊﹀璁板綍"""
    return {"ok": True, "dreams": DigitalLifeform._dream_log[-10:]}

@router.get("/reflection")
async def lifeform_reflection(_=Depends(verify_token)):
    """褰撳墠鍙嶆€?""
    return {"ok": True, "reflection": DigitalLifeform.reflect()}

@router.post("/cycle")
async def force_cycle(_=Depends(verify_token)):
    """寮哄埗瑙﹀彂涓€涓嚜涓诲惊鐜?""
    from digital_lifeform import DigitalLifeform
    result = await DigitalLifeform.one_cycle()
    return {"ok": True, "cycle": result}
