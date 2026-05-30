""" API"""
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from tools.predict_engine import predict_engine
from auth import verify_token

router = APIRouter(prefix="/agent/predict", tags=["Predict"])

class RecordRequest(BaseModel):
    metric: str
    value: float

@router.post("/record")
async def predict_record(req: RecordRequest, _=Depends(verify_token)):
    predict_engine.record(req.metric, req.value)
    return {"ok": True}

@router.get("/forecast/{metric}")
async def predict_forecast(metric: str, horizon: int = 7, _=Depends(verify_token)):
    return predict_engine.predict(metric, horizon)

@router.get("/stats")
async def predict_stats(_=Depends(verify_token)):
    return {"ok": True, **predict_engine.get_stats()}
