"""实时语音对话 API — WebSocket STT→LLM→TTS"""
import json, base64, io, wave, asyncio
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, UploadFile, File
from pydantic import BaseModel
from tools.logger import get_logger
from auth import verify_token

router = APIRouter(prefix="/agent/voice", tags=["Voice"])
logger = get_logger("voice")

class TTSRequest(BaseModel):
    text: str
    voice: str = "alloy"

@router.post("/tts")
async def text_to_speech(req: TTSRequest, _=Depends(verify_token)):
    """文字转语音"""
    try:
        from agents.multi_model import ModelRouter
        import httpx
        api_key = ModelRouter.get_key("openai")
        if api_key:
            async with httpx.AsyncClient(timeout=30) as client:
                resp = await client.post("https://api.openai.com/v1/audio/speech", json={
                    "model": "tts-1", "input": req.text, "voice": req.voice
                }, headers={"Authorization": f"Bearer {api_key}"})
                if resp.status_code == 200:
                    audio_b64 = base64.b64encode(resp.content).decode()
                    return {"ok": True, "audio": audio_b64, "format": "mp3"}
        return {"ok": False, "error": "TTS服务不可用"}
    except Exception as e:
        return {"ok": False, "error": str(e)}

@router.post("/stt")
async def speech_to_text(file: UploadFile = File(...), _=Depends(verify_token)):
    """语音转文字 STT"""
    try:
        audio_bytes = await file.read()
        from agents.multi_model import ModelRouter
        import httpx
        api_key = ModelRouter.get_key("openai")
        if api_key:
            async with httpx.AsyncClient(timeout=60) as client:
                resp = await client.post("https://api.openai.com/v1/audio/transcriptions", data={
                    "model": "whisper-1", "language": "zh"
                }, files={"file": (file.filename or "audio.webm", audio_bytes, file.content_type or "audio/webm")}, headers={"Authorization": f"Bearer {api_key}"})
                if resp.status_code == 200:
                    data = resp.json()
                    return {"ok": True, "text": data.get("text", ""), "language": data.get("language", "zh")}
        # 回退: DeepSeek暂不支持STT, 返回提示
        return {"ok": False, "error": "STT需要OpenAI API Key,请在后台配置"}
    except Exception as e:
        return {"ok": False, "error": str(e)}

@router.websocket("/ws")
async def voice_websocket(ws: WebSocket):
    """WebSocket 实时语音对话"""
    await ws.accept()
    logger.info("语音WebSocket已连接")
    try:
        while True:
            data = await ws.receive_json()
            msg_type = data.get("type", "")
            if msg_type == "stt":
                audio_b64 = data.get("audio", "")
                if audio_b64:
                    try:
                        audio_bytes = base64.b64decode(audio_b64)
                        from agents.multi_model import ModelRouter
                        import httpx
                        api_key = ModelRouter.get_key("openai")
                        if api_key:
                            async with httpx.AsyncClient(timeout=60) as client:
                                resp = await client.post("https://api.openai.com/v1/audio/transcriptions", data={"model": "whisper-1", "language": "zh"}, files={"file": ("audio.webm", audio_bytes, "audio/webm")}, headers={"Authorization": f"Bearer {api_key}"})
                                if resp.status_code == 200:
                                    text = resp.json().get("text", "")
                                    await ws.send_json({"type": "stt_result", "text": text})
                                    # 继续LLM
                                    if text:
                                        from agents.multi_model import ModelRouter
                                        llm_resp = ModelRouter.smart_chat(messages=[{"role":"user","content":text}], mode="fast")
                                        reply = llm_resp.get("content", "") if isinstance(llm_resp, dict) else str(llm_resp)
                                        await ws.send_json({"type": "llm", "text": reply})
                                        # TTS
                                        tts_key = ModelRouter.get_key("openai")
                                        if tts_key:
                                            async with httpx.AsyncClient(timeout=30) as client2:
                                                tts_resp = await client2.post("https://api.openai.com/v1/audio/speech", json={"model":"tts-1","input":reply[:500],"voice":"alloy"}, headers={"Authorization":f"Bearer {tts_key}"})
                                                if tts_resp.status_code == 200:
                                                    tts_b64 = base64.b64encode(tts_resp.content).decode()
                                                    await ws.send_json({"type":"tts","audio":tts_b64})
                        else:
                            await ws.send_json({"type":"error","text":"语音服务需要OpenAI API Key"})
                    except Exception as e:
                        await ws.send_json({"type":"error","text":str(e)})
            elif msg_type == "text":
                text = data.get("text", "")
                if text:
                    from agents.multi_model import ModelRouter
                    resp = ModelRouter.smart_chat(messages=[{"role":"user","content":text}], mode="fast")
                    reply = resp.get("content","") if isinstance(resp,dict) else str(resp)
                    await ws.send_json({"type":"llm","text":reply})
                    tts_key = ModelRouter.get_key("openai")
                    if tts_key:
                        import httpx
                        async with httpx.AsyncClient(timeout=30) as client:
                            tts_resp = await client.post("https://api.openai.com/v1/audio/speech", json={"model":"tts-1","input":reply[:500],"voice":"alloy"}, headers={"Authorization":f"Bearer {tts_key}"})
                            if tts_resp.status_code == 200:
                                tts_b64 = base64.b64encode(tts_resp.content).decode()
                                await ws.send_json({"type":"tts","audio":tts_b64})
    except WebSocketDisconnect:
        logger.info("语音WebSocket断开")
    except Exception as e:
        logger.error(f"语音WebSocket错误: {e}")
        try:
            await ws.send_json({"type":"error","text":str(e)})
        except:
            pass