"""语音引擎 — STT语音识别 + TTS语音合成 + 流式WebSocket"""
import os, json, base64, asyncio, httpx
from io import BytesIO
from tools.logger import get_logger

logger = get_logger("voice")

OPENAI_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_BASE = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
DEEPSEEK_KEY = os.getenv("DEEPSEEK_API_KEY", "")
DEFAULT_MODEL = os.getenv("CHEAP_MODEL", "deepseek-chat")

# ===== STT: 语音转文字 =====
async def speech_to_text(audio_bytes: bytes, fmt: str = "webm") -> str:
    """将音频转文字，支持Whisper API"""
    if not OPENAI_KEY:
        return "[语音识别未配置API Key]"
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
                return resp.json().get("text", "")
            logger.error(f"STT失败: {resp.status_code}")
            return ""
    except Exception as e:
        logger.error(f"STT异常: {e}")
        return ""

# ===== TTS: 文字转语音 =====
async def text_to_speech(text: str, voice: str = "alloy") -> bytes:
    """将文字转语音，返回音频bytes。支持voice: alloy/echo/fable/onyx/nova/shimmer"""
    if not OPENAI_KEY:
        return b""
    if len(text) > 4000:
        text = text[:4000]  # TTS限制
    try:
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.post(
                f"{OPENAI_BASE}/audio/speech",
                headers={"Authorization": f"Bearer {OPENAI_KEY}", "Content-Type": "application/json"},
                json={"model": "tts-1", "voice": voice, "input": text, "speed": 1.1}
            )
            if resp.status_code == 200:
                return resp.content
            logger.error(f"TTS失败: {resp.status_code}")
            return b""
    except Exception as e:
        logger.error(f"TTS异常: {e}")
        return b""

# ===== 完整语音对话 =====
async def stream_voice_chat(audio_bytes: bytes, system_prompt: str = "") -> dict:
    """完整语音对话: STT -> AI思考 -> TTS"""
    # Step 1: 语音转文字
    user_text = await speech_to_text(audio_bytes)
    if not user_text:
        return {"ok": False, "error": "语音识别失败", "text": "", "audio": ""}

    # Step 2: AI思考（优先DeepSeek省钱，OpenAI备选）
    try:
        from tools.ai_client import call_ai
        msgs = [
            {"role": "system", "content": system_prompt or "你是全能AI助手，简洁回复用户。"},
            {"role": "user", "content": user_text}
        ]
        reply_text = await call_ai(msgs, model=DEFAULT_MODEL, max_tokens=200, temperature=0.7)
    except Exception:
        try:
            # 降级：直接用httpx
            key = OPENAI_KEY or DEEPSEEK_KEY
            base = OPENAI_BASE if OPENAI_KEY else "https://api.deepseek.com/v1"
            async with httpx.AsyncClient(timeout=30) as c:
                r = await c.post(f"{base}/chat/completions",
                    headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
                    json={"model": "gpt-3.5-turbo" if OPENAI_KEY else "deepseek-chat",
                          "messages": msgs, "max_tokens": 200})
                reply_text = r.json().get("choices", [{}])[0].get("message", {}).get("content", "抱歉没理解") if r.status_code == 200 else "AI暂时无法响应"
        except:
            reply_text = "AI出错了，请稍后再试"

    # Step 3: 文字转语音
    audio_result = await text_to_speech(reply_text)
    audio_b64 = base64.b64encode(audio_result).decode() if audio_result else ""

    return {
        "ok": True,
        "user_text": user_text,
        "reply_text": reply_text,
        "audio_b64": audio_b64
    }