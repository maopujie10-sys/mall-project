"""铏氭嫙鏁版嵁 API 鈥?涓€閿€犳暟鎹?瀹炴椂娲诲姩/浠〃鐩樼粺璁?""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional
from auth import verify_token
from risk import handle_risk
from tools.virtual_data import VirtualDataEngine
from state import state

router = APIRouter(prefix="/agent/virtual", tags=["VirtualData"])

class GenerateRequest(BaseModel):
    scale: str = "small"  # small/medium/large/huge
    target: Optional[str] = None  # 鍙€? users/products/orders/all

class RealtimeRequest(BaseModel):
    count: int = 20

# 鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺?#  API
# 鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺?
@router.post("/generate")
async def generate_data(req: GenerateRequest, _=Depends(verify_token)):
    """涓€閿敓鎴愯櫄鎷熸暟鎹?鈥?鐢ㄦ埛/鍟嗗搧/璁㈠崟/K绾?瀹㈡湇/绛惧埌/鍐呭"""
    await handle_risk("L3", f"鐢熸垚铏氭嫙鏁版嵁", f"scale={req.scale} target={req.target or 'all'}")
    if req.scale not in ("small","medium","large","huge"):
        raise HTTPException(400, "scale must be: small/medium/large/huge")

    result = VirtualDataEngine.generate_all(req.scale)

    # 瀛樺偍鍒?state
    state._data["virtual_data_last"] = {
        "scale": req.scale,
        "stats": result["stats"],
        "generated_at": result["generated_at"],
    }
    state._save()

    return {"ok": True, "scale": req.scale, "stats": result["stats"], "data_preview": str(result["data"].keys())}

@router.post("/realtime")
async def realtime_activity(req: Optional[RealtimeRequest] = None, _=Depends(verify_token)):
    """鐢熸垚瀹炴椂娲诲姩鏃ュ織 鈥?妯℃嫙骞冲彴鏈夌湡浜烘鍦ㄤ娇鐢?""
    await handle_risk("L1", "鏌ョ湅瀹炴椂娲诲姩")
    count = req.count if req else 20
    activities = VirtualDataEngine.generate_realtime_activity(count)
    return {"activities": activities, "count": len(activities)}

@router.get("/dashboard")
async def dashboard_stats(_=Depends(verify_token)):
    """浠〃鐩樺疄鏃剁粺璁℃暟鎹?鈥?浠婃棩鏂板/浜ゆ槗棰?鍦ㄧ嚎浜烘暟"""
    await handle_risk("L1", "鏌ョ湅铏氭嫙鏁版嵁鐪嬫澘")
    stats = VirtualDataEngine.get_dashboard_stats()
    return {"ok": True, "stats": stats}

@router.get("/stats")
async def data_stats(_=Depends(verify_token)):
    """鏌ョ湅宸茬敓鎴愮殑铏氭嫙鏁版嵁缁熻"""
    await handle_risk("L1", "鏌ョ湅铏氭嫙鏁版嵁缁熻")
    last = state._data.get("virtual_data_last", {})
    return {"last_generation": last, "current_stats": VirtualDataEngine.get_dashboard_stats()}

@router.get("/preview/users")
async def preview_users(_=Depends(verify_token), limit: int = 10):
    """鏌ョ湅鐢熸垚鐨勭ず渚嬬敤鎴锋暟鎹?""
    await handle_risk("L1", "棰勮铏氭嫙鐢ㄦ埛")
    last = state._data.get("virtual_data_last", {})
    return {"users_preview": last.get("data", {}).get("users", [])[:limit]}

@router.get("/scales")
async def list_scales(_=Depends(verify_token)):
    """鏌ョ湅鍙敤鏁版嵁瑙勬ā"""
    await handle_risk("L1", "鏌ョ湅鐢熸垚瑙勬ā")
    return {
        "scales": {
            "small": {"users": 1000, "products": 500, "璇存槑": "灏忓瀷骞冲彴锛岄€傚悎娴嬭瘯"},
            "medium": {"users": 5000, "products": 2000, "璇存槑": "涓瀷骞冲彴锛屽儚鍖哄煙鐢靛晢"},
            "large": {"users": 20000, "products": 5000, "璇存槑": "澶у瀷骞冲彴锛屽儚涓绘祦鍟嗗煄"},
            "huge": {"users": 50000, "products": 10000, "璇存槑": "宸ㄥ瀷骞冲彴锛屽儚娣樺疂浜笢"},
        }
    }