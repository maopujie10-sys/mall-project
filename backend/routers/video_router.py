"""Video Analysis API - Video frame extraction & AI-powered understanding"""
from fastapi import APIRouter, Depends, UploadFile, File, Form
from pydantic import BaseModel
from auth import verify_token
from agents.vision_agent import VisionAgent
import os

router = APIRouter(prefix="/agent/video", tags=["Video AI"])

class VideoAnalyzeRequest(BaseModel):
    video_url: str
    frame_interval: float = 3.0

class ImageAnalyzeRequest(BaseModel):
    image_url: str = ""
    prompt: str = ""

@router.post("/analyze")
async def analyze_video(req: VideoAnalyzeRequest, _=Depends(verify_token)):
    """Analyze video content: extract key frames and run AI vision analysis"""
    if not req.video_url:
        return {"ok": False, "error": "video_url required"}
    result = await VisionAgent.analyze_video(
        video_url=req.video_url,
        frame_interval=req.frame_interval or 3.0
    )
    return result

@router.post("/analyze-image")
async def analyze_image(req: ImageAnalyzeRequest, _=Depends(verify_token)):
    """Analyze a single image with AI vision model"""
    if not req.image_url:
        return {"ok": False, "error": "image_url required"}
    result = await VisionAgent.analyze_image(image_url=req.image_url)
    return result

@router.post("/detect-faces")
async def detect_faces(image_url: str = "", _=Depends(verify_token)):
    """Detect and analyze faces in an image"""
    if not image_url:
        return {"ok": False, "error": "image_url required"}
    result = await VisionAgent.detect_faces(image_url)
    return result

@router.post("/upload-analyze")
async def upload_and_analyze(file: UploadFile = File(...), _=Depends(verify_token)):
    """Upload an image file and analyze it"""
    import tempfile
    try:
        content = await file.read()
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".jpg")
        tmp.write(content)
        tmp_path = tmp.name
        tmp.close()
        result = await VisionAgent.analyze_image(image_path=tmp_path)
        os.unlink(tmp_path)
        return result
    except Exception as e:
        return {"ok": False, "error": str(e)}
