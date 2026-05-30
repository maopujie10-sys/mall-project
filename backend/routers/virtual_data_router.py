''" API -- //''"
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
    target: Optional[str] = None  # : users/products/orders/all

class RealtimeRequest(BaseModel):
    count: int = 20


#  API

@router.post("/generate")
async def generate_data(req: GenerateRequest, _=Depends(verify_token)):
    ''" -- ///K///''"
    await handle_risk("L3", f'', f"scale={req.scale} target={req.target or 'all'}")
    if req.scale not in ("small","medium","large","huge"):
        raise HTTPException(400, "scale must be: small/medium/large/huge")

    result = VirtualDataEngine.generate_all(req.scale)

    #  state
    state._data["virtual_data_last"] = {
        "scale": req.scale,
        "stats": result["stats"],
        "generated_at": result["generated_at"],
    }
    state._save()

    return {"ok": True, "scale": req.scale, "stats": result["stats"], "data_preview": str(result["data"].keys())}

@router.post("/realtime")
async def realtime_activity(req: Optional[RealtimeRequest] = None, _=Depends(verify_token)):
    ''" -- ''"
    await handle_risk("L1", '')
    count = req.count if req else 20
    activities = VirtualDataEngine.generate_realtime_activity(count)
    return {"activities": activities, "count": len(activities)}

@router.get("/dashboard")
async def dashboard_stats(_=Depends(verify_token)):
    ''" -- //''"
    await handle_risk("L1", '')
    stats = VirtualDataEngine.get_dashboard_stats()
    return {"ok": True, "stats": stats}

@router.get("/stats")
async def data_stats(_=Depends(verify_token)):
    ''''''
    await handle_risk("L1", '')
    last = state._data.get("virtual_data_last", {})
    return {"last_generation": last, "current_stats": VirtualDataEngine.get_dashboard_stats()}

@router.get("/preview/users")
async def preview_users(_=Depends(verify_token), limit: int = 10):
    ''''''
    await handle_risk("L1", '')
    last = state._data.get("virtual_data_last", {})
    return {"users_preview": last.get("data", {}).get("users", [])[:limit]}

@router.get("/scales")
async def list_scales(_=Depends(verify_token)):
    ''''''
    await handle_risk("L1", '')
    return {
        "scales": {
            "small": {"users": 1000, "products": 500, '': ","},
            "medium": {"users": 5000, "products": 2000, '': ","},
            "large": {"users": 20000, "products": 5000, '': ","},
            "huge": {"users": 50000, "products": 10000, '': ","},
        }
    }