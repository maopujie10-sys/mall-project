''" API -- ////''"
from fastapi import APIRouter, Depends
from auth import verify_token
from digital_lifeform import DigitalLifeform

router = APIRouter(prefix="/agent/lifeform", tags=["Lifeform"])

@router.get("/status")
async def lifeform_status(_=Depends(verify_token)):
    ''''''
    return {"ok": True, **DigitalLifeform.get_lifeform_status()}

@router.get("/mood")
async def lifeform_mood(_=Depends(verify_token)):
    ''''''
    return {"ok": True, "mood": DigitalLifeform.get_mood()}

@router.get("/insights")
async def lifeform_insights(_=Depends(verify_token)):
    ''''''
    insights = DigitalLifeform.generate_insights()
    return {"ok": True, "insights": insights, "count": len(insights)}

@router.get("/dreams")
async def lifeform_dreams(_=Depends(verify_token)):
    ''''''
    return {"ok": True, "dreams": DigitalLifeform._dream_log[-10:]}

@router.get("/reflection")
async def lifeform_reflection(_=Depends(verify_token)):
    ''''''
    return {"ok": True, "reflection": DigitalLifeform.reflect()}

@router.post("/cycle")
async def force_cycle(_=Depends(verify_token)):
    ''''''
    from digital_lifeform import DigitalLifeform
    result = await DigitalLifeform.one_cycle()
    return {"ok": True, "cycle": result}
