''" -- STT + TTS + WebSocket''"
import os, json, base64, asyncio, httpx
from io import BytesIO
from tools.logger import get_logger

logger = get_logger("voice")

OPENAI_KEY = os.getenv("OPENAI_API_KEY", '')
OPENAI_BASE = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
DEEPSEEK_KEY = os.getenv("DEEPSEEK_API_KEY", '')
DEFAULT_MODEL = os.getenv("CHEAP_MODEL", "deepseek-chat")

# ===== STT:  =====
async def speech_to_text(audio_bytes: bytes, fmt: str = "webm") -> str:
    ''",Whisper API''"
    if not OPENAI_KEY:
        return "[API Key]"
    try:
        async with httpx.AsyncClient(timeout=30) as client:
            files = {"file": ("audio." + fmt, BytesIO(audio_bytes), f"audio/{fmt}")}
            headers = {"Authorization": f"Bearer {OPENAI_KEY}"}
            resp = await client.post(
                f"{OPENAI_BASE}/audio/transcriptions",
                headers=headers,
                data={"model": "whisper-1", "language": "zh"},
                files=files
            )
            if resp.status_code == 200:
                return resp.json().get("text", '')
            logger.error(f"STT: {resp.status_code}")
            return ''
    except Exception as e:
        logger.error(f"STT: {e}")
        return ''

# ===== TTS:  =====
async def text_to_speech(text: str, voice: str = "alloy") -> bytes:
    ''",bytes.voice: alloy/echo/fable/onyx/nova/shimmer''"
    if not OPENAI_KEY:
        return b''
    if len(text) > 4000:
        text = text[:4000]  # TTS
    try:
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.post(
                f"{OPENAI_BASE}/audio/speech",
                headers={"Authorization": f"Bearer {OPENAI_KEY}", "Content-Type": "application/json"},
                json={"model": "tts-1", "voice": voice, "input": text, "speed": 1.1}
            )
            if resp.status_code == 200:
                return resp.content
            logger.error(f"TTS: {resp.status_code}")
            return b''
    except Exception as e:
        logger.error(f"TTS: {e}")
        return b''

# =====  =====
async def stream_voice_chat(audio_bytes: bytes, system_prompt: str = '') -> dict:
    ''": STT -> AI -> TTS''"
    # Step 1: 
    user_text = await speech_to_text(audio_bytes)
    if not user_text:
        return {"ok": False, "error": '', "text": '', "audio": ''}

    # Step 2: AI(DeepSeek,OpenAI)
    try:
        from tools.ai_client import call_ai
        msgs = [
            {"role": "system", "content": system_prompt or "AI,."},
            {"role": "user", "content": user_text}
        ]
        reply_text = await call_ai(msgs, model=DEFAULT_MODEL, max_tokens=200, temperature=0.7)
    except Exception:
        try:
            # :httpx
            key = OPENAI_KEY or DEEPSEEK_KEY
            base = OPENAI_BASE if OPENAI_KEY else "https://api.deepseek.com/v1"
            async with httpx.AsyncClient(timeout=30) as c:
                r = await c.post(f"{base}/chat/completions",
                    headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
                    json={"model": "gpt-3.5-turbo" if OPENAI_KEY else "deepseek-chat",
                          "messages": msgs, "max_tokens": 200})
                reply_text = r.json().get("choices", [{}])[0].get("message", {}).get("content", '') if r.status_code == 200 else "AI"
        except:
            reply_text = "AI,"

    # Step 3: 
    audio_result = await text_to_speech(reply_text)
    audio_b64 = base64.b64encode(audio_result).decode() if audio_result else ''

    return {
        "ok": True,
        "user_text": user_text,
        "reply_text": reply_text,
        "audio_b64": audio_b64
    }