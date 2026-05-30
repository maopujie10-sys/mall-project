"""Vision API — 图片/视频/OCR分析 (独立路由, 前缀 /agent/vision)"""
import json, base64, os, tempfile
from fastapi import APIRouter, Depends, UploadFile, File
from pydantic import BaseModel
from auth import verify_token
from tools.logger import get_logger

router = APIRouter(prefix="/agent/vision", tags=["Vision"])
logger = get_logger("vision")

class VisionRequest(BaseModel):
    image_base64: str = ""
    question: str = "描述这张图片的内容"

@router.post("/analyze")
async def analyze(req: VisionRequest, _=Depends(verify_token)):
    """分析图片 — 接收base64编码, 调用多模型视觉API"""
    if not req.image_base64:
        return {"ok": False, "error": "请提供图片数据"}
    try:
        from agents.multi_model import ModelRouter
        mime = "image/jpeg"
        if req.image_base64.startswith("iVBOR"): mime = "image/png"
        elif req.image_base64.startswith("/9j"): mime = "image/jpeg"
        elif req.image_base64.startswith("R0lG"): mime = "image/gif"
        elif req.image_base64.startswith("Qk"): mime = "image/bmp"

        resp = ModelRouter.smart_chat(messages=[{"role": "user", "content": [
            {"type": "text", "text": req.question},
            {"type": "image_url", "image_url": {"url": f"data:{mime};base64,{req.image_base64}"}}
        ]}])
        result = resp.get("content", "") if isinstance(resp, dict) else str(resp)
        return {"ok": True, "result": result, "model": resp.get("model", "") if isinstance(resp, dict) else ""}
    except Exception as e:
        logger.info(f"视觉分析失败: {e}")
        return {"ok": False, "error": str(e)}

@router.post("/ocr")
async def ocr_analyze(req: VisionRequest, _=Depends(verify_token)):
    """OCR文字识别"""
    from agents.vision_agent import VisionAgent
    return await VisionAgent.ocr_recognize(image_base64=req.image_base64)

@router.post("/objects")
async def detect_objects(req: VisionRequest, _=Depends(verify_token)):
    """物体检测"""
    from agents.vision_agent import VisionAgent
    return await VisionAgent.detect_objects(image_base64=req.image_base64)

@router.post("/faces")
async def detect_faces(req: VisionRequest, _=Depends(verify_token)):
    """人脸检测"""
    from agents.vision_agent import VisionAgent
    return await VisionAgent.detect_faces(image_base64=req.image_base64)

@router.post("/upload")
async def vision_upload(file: UploadFile = File(...), question: str = "描述图片", _=Depends(verify_token)):
    """上传图片文件分析"""
    try:
        content = await file.read()
        b64 = base64.b64encode(content).decode()
        return await analyze(VisionRequest(image_base64=b64, question=question), _)
    except Exception as e:
        return {"ok": False, "error": str(e)}