"""AI Content Factory API - 100% Free Open Source Pipeline"""
from fastapi import APIRouter, Depends, UploadFile, File, Form
from fastapi.responses import FileResponse
from pydantic import BaseModel
from auth import verify_token
from tools.free_media import *
import os

router = APIRouter(prefix="/agent/media", tags=["Content Factory"])

# ---- Rewrite (DeepSeek) ----
class RewriteReq(BaseModel): text: str; style: str = "professional"
@router.post("/rewrite")
async def api_rewrite(req: RewriteReq, _=Depends(verify_token)):
    return await rewrite_text_free(req.text, req.style)

# ---- Image (Pollinations + local SD) ----
class ImageReq(BaseModel): prompt: str; style: str = "realistic"; size: str = "1024x1024"
@router.post("/image")
async def api_image(req: ImageReq, _=Depends(verify_token)):
    return await generate_image_free(req.prompt, req.style, req.size)

@router.get("/styles")
async def api_styles(_=Depends(verify_token)):
    return {"ok":True,"styles":["realistic","cinematic","anime","oil-painting","watercolor","pixel-art","3d-render","sketch","cyberpunk","minimalist"]}

# ---- TTS (Edge-TTS free) ----
class TTSReq(BaseModel): text: str; voice: str = "xiaoxiao"
@router.post("/tts")
async def api_tts(req: TTSReq, _=Depends(verify_token)):
    return await edge_tts(req.text, EDGE_VOICES.get(req.voice, "zh-CN-XiaoxiaoNeural"))

@router.get("/voices")
async def api_voices(_=Depends(verify_token)):
    return {"ok":True,"voices":[{"id":k,"name":v} for k,v in EDGE_VOICES.items()]}

# ---- Digital Human (Wav2Lip + fallback) ----
class AvatarReq(BaseModel): text: str; voice: str = "xiaoxiao"; image_b64: str = ""
@router.post("/avatar")
async def api_avatar(req: AvatarReq, _=Depends(verify_token)):
    return await generate_digital_human(req.text, req.image_b64 or None, req.voice)

# ---- Image-to-Video (AnimateDiff + Ken Burns) ----
class Img2VidReq(BaseModel): image_b64: str; duration: float = 3.0; prompt: str = ""
@router.post("/image-to-video")
async def api_img2vid(req: Img2VidReq, _=Depends(verify_token)):
    return await image_to_video_free(req.image_b64, req.duration, req.prompt)

# ---- Full Video Pipeline ----
class VideoReq(BaseModel):
    prompt: str; duration: int = 15; template: str = "product_showcase"
    style: str = "cinematic"; voice: str = "xiaoxiao"; include_captions: bool = True

@router.post("/video")
async def api_video(req: VideoReq, _=Depends(verify_token)):
    return await generate_video_free(req.prompt, req.duration, req.template, req.style, req.voice, req.include_captions)

# ---- Batch ----
class BatchReq(BaseModel): prompts: list = []; template: str = "social_ad"; voice: str = "xiaoxiao"
@router.post("/batch")
async def api_batch(req: BatchReq, _=Depends(verify_token)):
    results = []
    for p in req.prompts[:10]:
        r = await generate_video_free(p, 15, req.template, "cinematic", req.voice)
        results.append({"prompt":p,"ok":r.get("ok",False),"video_id":r.get("video_id","")})
    return {"ok":True,"total":len(req.prompts),"results":results}

@router.get("/templates")
async def api_templates(_=Depends(verify_token)):
    return {"ok":True,"templates":[{"id":k,"desc":v["desc"],"scenes":v["scenes"]} for k,v in VIDEO_TEMPLATES.items()]}

# ---- Engine Status ----
@router.get("/engines")
async def api_engines(_=Depends(verify_token)):
    status = {"edge_tts": False, "stable_diffusion": False, "wav2lip": False, "animatediff": False}
    try:
        import edge_tts; status["edge_tts"] = True
    except: pass
    try:
        import httpx
        async with httpx.AsyncClient(timeout=2) as c:
            r = await c.get("http://localhost:7860/docs")
            status["stable_diffusion"] = r.status_code == 200
    except: pass
    try:
        import httpx
        async with httpx.AsyncClient(timeout=2) as c:
            r = await c.get("http://localhost:5001/")
            status["wav2lip"] = r.status_code < 500
    except: pass
    try:
        import httpx
        async with httpx.AsyncClient(timeout=2) as c:
            r = await c.get("http://localhost:7861/docs")
            status["animatediff"] = r.status_code == 200
    except: pass
    return {"ok": True, "engines": status}

# ---- Gallery ----
@router.get("/gallery")
async def api_gallery(_=Depends(verify_token)):
    return {"ok":True,"videos":list_videos()}

# ---- Edit ----
@router.post("/edit")
async def api_edit(video: UploadFile = File(...), action: str = Form("trim"),
                   start: float = Form(0), end: float = Form(30), speed: float = Form(1.5),
                   _=Depends(verify_token)):
    import base64
    return await edit_video_free(action, base64.b64encode(await video.read()).decode(), {"start":start,"end":end,"speed":speed})

# ---- Serve ----
@router.get("/serve/{video_id}")
async def serve_video(video_id: str):
    path = os.path.join(MEDIA_DIR, f"{video_id}.mp4")
    if os.path.exists(path): return FileResponse(path, media_type="video/mp4")
    return {"ok":False,"error":"Not found"}

# ---- Multi-Platform Publish ----
class PublishReq(BaseModel):
    title: str; description: str = ""; tags: str = ""
    platforms: list = ["tiktok"]; video_id: str = ""
    schedule: str = ""; ai_optimize: bool = True; ai_hashtags: bool = True

@router.post("/publish")
async def api_publish(req: PublishReq, video: UploadFile = File(None), _=Depends(verify_token)):
    """Publish video to multiple short-video platforms"""
    results = []
    platforms_info = {
        "tiktok": "TikTok", "youtube": "YouTube Shorts", "instagram": "Instagram Reels",
        "facebook": "Facebook Reels", "snapchat": "Snapchat Spotlight",
        "xiaohongshu": "RED", "kuaishou": "Kuaishou", "bilibili": "Bilibili"
    }
    
    # Save uploaded video
    video_path = None
    if video:
        import uuid, aiofiles
        video_id = str(uuid.uuid4())[:8]
        video_path = os.path.join(MEDIA_DIR, f"publish_{video_id}.mp4")
        async with aiofiles.open(video_path, 'wb') as f:
            await f.write(await video.read())
    
    for platform_id in req.platforms[:8]:
        platform_name = platforms_info.get(platform_id, platform_id)
        try:
            result = await publish_to_platform(
                platform=platform_id,
                title=req.title,
                description=req.description,
                tags=req.tags,
                video_path=video_path,
                video_id=req.video_id,
                schedule=req.schedule,
                ai_optimize=req.ai_optimize,
                ai_hashtags=req.ai_hashtags
            )
            results.append({"platform": platform_name, "status": "published", "url": result.get("url",""), "message": result.get("message","OK")})
        except Exception as e:
            results.append({"platform": platform_name, "status": "failed", "url": "", "message": str(e)})
    
    return {"ok": True, "results": results, "total": len(results)}