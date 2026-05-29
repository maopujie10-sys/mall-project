"""内容工厂 API"""
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from tools.content_factory import content_factory
from auth import verify_token

router = APIRouter(prefix="/agent/content", tags=["Content"])

class DescRequest(BaseModel):
    name: str = ""; category: str = ""; price: str = ""; features: str = ""

class CampaignRequest(BaseModel):
    name: str = ""; discount: str = ""; audience: str = ""; platform: str = ""

class SocialRequest(BaseModel):
    theme: str = ""; style: str = "轻松活泼"; include: str = ""

class TranslateRequest(BaseModel):
    text: str; target_lang: str = "en"

@router.post("/description")
async def gen_desc(req: DescRequest, _=Depends(verify_token)):
    text = await content_factory.generate_product_desc(req.dict())
    return {"ok": True, "text": text}

@router.post("/marketing")
async def gen_marketing(req: CampaignRequest, _=Depends(verify_token)):
    text = await content_factory.generate_marketing_copy(req.dict())
    return {"ok": True, "text": text}

@router.post("/social")
async def gen_social(req: SocialRequest, _=Depends(verify_token)):
    text = await content_factory.generate_social_post(req.dict())
    return {"ok": True, "text": text}

@router.post("/translate")
async def gen_translate(req: TranslateRequest, _=Depends(verify_token)):
    text = await content_factory.translate_content(req.text, req.target_lang)
    return {"ok": True, "text": text}
