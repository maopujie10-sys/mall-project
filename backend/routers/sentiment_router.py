"""情感分析 API"""
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from tools.sentiment_analyzer import sentiment_analyzer
from auth import verify_token

router = APIRouter(prefix="/agent/sentiment", tags=["Sentiment"])

class TextRequest(BaseModel):
    text: str

class ProfileRequest(BaseModel):
    user_id: str
    messages: list = []

@router.post("/analyze")
async def sent_analyze(req: TextRequest, _=Depends(verify_token)):
    result = sentiment_analyzer.analyze(req.text)
    return {"ok": True, **result}

@router.post("/profile")
async def sent_profile(req: ProfileRequest, _=Depends(verify_token)):
    result = sentiment_analyzer.build_profile(req.user_id, req.messages)
    return {"ok": True, **result}
