"""推荐引擎 API"""
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from tools.recommend_engine import recommend_engine
from auth import verify_token

router = APIRouter(prefix="/agent/recommend", tags=["Recommend"])

class RecordAction(BaseModel):
    user_id: str
    item_id: str
    action: str = "view"

class SetFeatures(BaseModel):
    item_id: str
    features: dict = {}

@router.post("/action")
async def rec_action(req: RecordAction, _=Depends(verify_token)):
    recommend_engine.record_action(req.user_id, req.item_id, req.action)
    return {"ok": True}

@router.post("/features")
async def rec_features(req: SetFeatures, _=Depends(verify_token)):
    recommend_engine.set_item_features(req.item_id, req.features)
    return {"ok": True}

@router.get("/for_user/{user_id}")
async def rec_for_user(user_id: str, top_k: int = 10, _=Depends(verify_token)):
    items = recommend_engine.recommend_for_user(user_id, top_k)
    return {"ok": True, "items": items}

@router.get("/similar/{item_id}")
async def rec_similar(item_id: str, top_k: int = 10, _=Depends(verify_token)):
    items = recommend_engine.recommend_similar_items(item_id, top_k)
    return {"ok": True, "items": items}

@router.get("/stats")
async def rec_stats(_=Depends(verify_token)):
    return {"ok": True, **recommend_engine.get_stats()}
