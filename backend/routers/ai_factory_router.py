"""AI 内容工厂 API — 文案/作图/视频生成"""
from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from auth import verify_token
from risk import handle_risk
from tools.ai_factory import generate_copy, generate_image, generate_video, save_record, get_history

router = APIRouter(prefix="/ai-factory", tags=["AIFactory"])

class CopyRequest(BaseModel):
    product_info: str
    style: str = "title"  # title / description / seo / ad

class ImageRequest(BaseModel):
    prompt: str
    size: str = "1024x1024"
    style: str = "realistic"

class VideoRequest(BaseModel):
    product_name: str
    script: str = ""
    duration: int = 15

@router.post("/copy")
async def generate_copy_api(req: CopyRequest, _=Depends(verify_token)):
    """AI 生成商品文案"""
    await handle_risk("L2", f"AI生成文案: {req.style}", req.product_info[:50])
    result = await generate_copy(req.product_info, req.style)
    save_record("copy", {"style": req.style, "product": req.product_info[:50], "result": result.get("content", "")[:100], "ok": result["ok"]})
    return result

@router.post("/image")
async def generate_image_api(req: ImageRequest, _=Depends(verify_token)):
    """AI 生成商品图片"""
    await handle_risk("L2", "AI生成图片", req.prompt[:50])
    result = await generate_image(req.prompt, req.size, req.style)
    save_record("image", {"prompt": req.prompt[:50], "url": result.get("url", ""), "ok": result["ok"]})
    return result

@router.post("/video")
async def generate_video_api(req: VideoRequest, _=Depends(verify_token)):
    """AI 生成商品视频"""
    await handle_risk("L2", "AI生成视频", req.product_name)
    result = await generate_video(req.product_name, req.script, req.duration)
    save_record("video", {"product": req.product_name, "ok": result["ok"]})
    return result

@router.get("/history")
async def factory_history(category: str = "all", _=Depends(verify_token)):
    """查看生成历史"""
    await handle_risk("L1", "查看AI工厂历史")
    return {"records": get_history(category), "category": category}
