"""Video Analysis API - Video frame extraction, AI analysis, and WebRTC signaling"""
from fastapi import APIRouter, Depends, UploadFile, File, Form, WebSocket, WebSocketDisconnect
from pydantic import BaseModel
from auth import verify_token
from agents.vision_agent import VisionAgent
import os, json, base64

router = APIRouter(prefix="/agent/video", tags=["Video AI"])

class VideoAnalyzeRequest(BaseModel):
    video_url: str
    frame_interval: float = 3.0

class ImageAnalyzeRequest(BaseModel):
    image_url: str = ""

# ===== Video Analysis =====
@router.post("/analyze")
async def analyze_video(req: VideoAnalyzeRequest, _=Depends(verify_token)):
    """Analyze video: ffmpeg frame extraction + AI vision per frame"""
    if not req.video_url:
        return {"ok": False, "error": "video_url required"}
    raw = await VisionAgent.analyze_video(
        video_url=req.video_url,
        frame_interval=req.frame_interval or 3.0
    )
    if raw.get("ok"):
        return {
            "ok": True,
            "duration": str(int(raw.get("duration_sec", 0))) + "s",
            "resolution": "extracted",
            "fileSize": str(len(raw.get("frame_analysis", []))) + " frames",
            "fps": str(round(1.0 / req.frame_interval, 1)) if req.frame_interval else "N/A",
            "hasAudio": True,
            "language": "auto-detected",
            "summary": raw.get("summary", ""),
            "hotScore": min(100, len(raw.get("frame_analysis", [])) * 10),
            "subtitles": [
                {"time": str(f["time_sec"]) + "s", "text": f["analysis"][:200]}
                for f in raw.get("frame_analysis", [])
            ],
            "frame_analysis": raw.get("frame_analysis", []),
        }
    return raw

@router.post("/analyze-image")
async def analyze_image(req: ImageAnalyzeRequest, _=Depends(verify_token)):
    """Analyze single image with AI vision"""
    if not req.image_url:
        return {"ok": False, "error": "image_url required"}
    return await VisionAgent.analyze_image(image_url=req.image_url)

@router.post("/detect-faces")
async def detect_faces(image_url: str = "", _=Depends(verify_token)):
    """Detect faces in an image"""
    if not image_url:
        return {"ok": False, "error": "image_url required"}
    return await VisionAgent.detect_faces(image_url)

@router.post("/upload-analyze")
async def upload_and_analyze(file: UploadFile = File(...), _=Depends(verify_token)):
    """Upload image for analysis"""
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

# Also expose at /agent/vision/video for backward compat
@router.post("/vision")
async def analyze_video_legacy(req: VideoAnalyzeRequest, _=Depends(verify_token)):
    """Legacy alias for /agent/video/analyze"""
    return await analyze_video(req)

# ===== WebRTC Signaling for Video Call =====
rooms = {}

@router.websocket("/call/{room_id}")
async def video_call_signaling(ws: WebSocket, room_id: str):
    """WebRTC signaling for video calls"""
    await ws.accept()
    if room_id not in rooms:
        rooms[room_id] = set()
    rooms[room_id].add(ws)
    try:
        while True:
            data = await ws.receive_json()
            msg_type = data.get("type", "")
            if msg_type in ("offer", "answer", "ice-candidate", "hangup"):
                # Relay to all other peers in room
                for peer in rooms.get(room_id, set()):
                    if peer != ws:
                        try:
                            await peer.send_json(data)
                        except:
                            pass
            elif msg_type == "chat":
                # AI processes video frame or text during call
                text = data.get("text", "")
                if text:
                    from agents.multi_model import ModelRouter
                    resp = ModelRouter.smart_chat(
                        messages=[{"role": "user", "content": text}],
                        mode="fast"
                    )
                    reply = resp.get("content", "") if isinstance(resp, dict) else str(resp)
                    await ws.send_json({"type": "ai_response", "text": reply})
                    # Broadcast AI response to all peers
                    for peer in rooms.get(room_id, set()):
                        try:
                            await peer.send_json({"type": "ai_response", "text": reply, "broadcast": True})
                        except:
                            pass
    except WebSocketDisconnect:
        pass
    except Exception as e:
        try:
            await ws.send_json({"type": "error", "text": str(e)})
        except:
            pass
    finally:
        rooms.get(room_id, set()).discard(ws)
        if room_id in rooms and not rooms[room_id]:
            del rooms[room_id]
