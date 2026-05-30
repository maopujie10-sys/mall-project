''" API  WebSocket STTLLMTTS''"
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
    ''''''
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
        return {"ok": False, "error": "TTS"}
    except Exception as e:
        return {"ok": False, "error": str(e)}

@router.post("/stt")
async def speech_to_text(file: UploadFile = File(...), _=Depends(verify_token)):
    ''" STT''"
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
                    return {"ok": True, "text": data.get("text", ''), "language": data.get("language", "zh")}
        # : DeepSeekSTT, 
        return {"ok": False, "error": "STTOpenAI API Key,"}
    except Exception as e:
        return {"ok": False, "error": str(e)}

@router.websocket("/ws")
async def voice_websocket(ws: WebSocket):
    ''"WebSocket ''"
    await ws.accept()
    logger.info("WebSocket")
    try:
        while True:
            data = await ws.receive_json()
            msg_type = data.get("type", '')
            if msg_type == "stt":
                audio_b64 = data.get("audio", '')
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
                                    text = resp.json().get("text", '')
                                    await ws.send_json({"type": "stt_result", "text": text})
                                    # LLM
                                    if text:
                                        from agents.multi_model import ModelRouter
                                        llm_resp = ModelRouter.smart_chat(messages=[{"role":"user","content":text}], mode="fast")
                                        reply = llm_resp.get("content", '') if isinstance(llm_resp, dict) else str(llm_resp)
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
                            await ws.send_json({"type":"error","text":"OpenAI API Key"})
                    except Exception as e:
                        await ws.send_json({"type":"error","text":str(e)})
            elif msg_type == "text":
                text = data.get("text", '')
                if text:
                    from agents.multi_model import ModelRouter
                    resp = ModelRouter.smart_chat(messages=[{"role":"user","content":text}], mode="fast")
                    reply = resp.get("content",'') if isinstance(resp,dict) else str(resp)
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
        logger.info("WebSocket")
    except Exception as e:
        logger.error(f"WebSocket: {e}")
        try:
            await ws.send_json({"type":"error","text":str(e)})
        except:
            pass