"""语音对话 API — WebSocket实时流式 + REST降级"""
import json, base64
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from tools.voice_engine import speech_to_text, text_to_speech, stream_voice_chat
from tools.logger import get_logger

logger = get_logger("voice_router")
router = APIRouter(prefix="/agent/voice", tags=["Voice"])

class VoiceRequest(BaseModel):
    audio_b64: str  # base64编码的音频
    fmt: str = "webm"

class VoiceTextRequest(BaseModel):
    text: str
    voice: str = "alloy"

@router.post("/stt")
async def voice_to_text(req: VoiceRequest):
    """语音→文字"""
    audio_bytes = base64.b64decode(req.audio_b64)
    text = await speech_to_text(audio_bytes, req.fmt)
    return {"ok": True, "text": text}

@router.post("/tts")
async def text_to_voice(req: VoiceTextRequest):
    """文字→语音"""
    audio = await text_to_speech(req.text, req.voice)
    audio_b64 = base64.b64encode(audio).decode() if audio else ""
    return {"ok": True, "audio_b64": audio_b64}

@router.post("/chat")
async def voice_chat(req: VoiceRequest):
    """语音对话: STT→LLM→TTS 一体化"""
    audio_bytes = base64.b64decode(req.audio_b64)
    result = await stream_voice_chat(audio_bytes)
    return result

@router.websocket("/ws")
async def voice_websocket(ws: WebSocket):
    """WebSocket流式语音对话"""
    await ws.accept()
    logger.info("语音WebSocket连接建立")

    try:
        while True:
            data = await ws.receive_text()
            msg = json.loads(data)

            if msg.get("type") == "ping":
                await ws.send_text(json.dumps({"type": "pong"}))
                continue

            if msg.get("type") == "voice":
                audio_b64 = msg.get("audio_b64", "")
                if not audio_b64:
                    await ws.send_text(json.dumps({"type": "error", "message": "缺少audio_b64"}))
                    continue

                audio_bytes = base64.b64decode(audio_b64)
                fmt = msg.get("fmt", "webm")

                # Step 1: STT
                await ws.send_text(json.dumps({"type": "status", "step": "stt", "message": "正在识别语音..."}))
                user_text = await speech_to_text(audio_bytes, fmt)

                if not user_text:
                    await ws.send_text(json.dumps({"type": "error", "message": "语音识别失败"}))
                    continue

                await ws.send_text(json.dumps({"type": "user_text", "text": user_text}))

                # Step 2: LLM
                await ws.send_text(json.dumps({"type": "status", "step": "llm", "message": "AI正在思考..."}))

                try:
                    from agents.multi_model import ModelRouter
                    mr = ModelRouter()
                    llm_resp = await mr.chat(
                        messages=[
                            {"role": "system", "content": "你是Friday全能AI助手，简洁友好地回答用户问题"},
                            {"role": "user", "content": user_text}
                        ],
                        mode="fast"
                    )
                    reply_text = llm_resp.get("content", "抱歉我没理解")
                except Exception as e:
                    reply_text = f"AI思考出错了: {e}"

                await ws.send_text(json.dumps({"type": "reply_text", "text": reply_text}))

                # Step 3: TTS
                await ws.send_text(json.dumps({"type": "status", "step": "tts", "message": "正在合成语音..."}))
                audio = await text_to_speech(reply_text)
                audio_b64_out = base64.b64encode(audio).decode() if audio else ""

                await ws.send_text(json.dumps({
                    "type": "voice_reply",
                    "audio_b64": audio_b64_out,
                    "text": reply_text
                }))

    except WebSocketDisconnect:
        logger.info("语音WebSocket断开")
    except Exception as e:
        logger.error(f"语音WebSocket异常: {e}")
        try:
            await ws.send_text(json.dumps({"type": "error", "message": str(e)}))
        except:
            pass
