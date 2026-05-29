"""语音引擎 — STT语音识别 + TTS语音合成 + 流式WebSocket"""
import os, json, base64, asyncio, httpx
from io import BytesIO
from tools.logger import get_logger

logger = get_logger("voice")

OPENAI_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_BASE = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")

# ===== STT: 语音转文字 =====
async def speech_to_text(audio_bytes: bytes, fmt: str = "webm") -> str:
    """将音频转文字，支持 Whisper API / 本地模型"""
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
            logger.error(f"STT失败: {resp.status_code} {resp.text}")
            return ""
    except Exception as e:
        logger.error(f"STT异常: {e}")
        return ""

# ===== TTS: 文字转语音 =====
async def text_to_speech(text: str, voice: str = "alloy") -> bytes:
    """将文字转语音，返回音频bytes"""
    if not OPENAI_KEY:
        return b""

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

# ===== 流式语音对话 =====
async def stream_voice_chat(audio_bytes: bytes, system_prompt: str = "") -> dict:
    """完整的语音对话流程: STT → LLM → TTS"""
    user_text = await speech_to_text(audio_bytes)
    if not user_text:
        return {"ok": False, "error": "语音识别失败", "text": "", "audio": ""}

    from agents.multi_model import ModelRouter
    router = ModelRouter()

    try:
        llm_resp = await router.chat(
            messages=[
                {"role": "system", "content": system_prompt or "你是全能AI助手，简洁回答"},
                {"role": "user", "content": user_text}
            ],
            mode="fast"
        )
        reply_text = llm_resp.get("content", "抱歉我没理解")
    except Exception as e:
        reply_text = f"AI思考出错了: {e}"

    audio_bytes = await text_to_speech(reply_text)
    audio_b64 = base64.b64encode(audio_bytes).decode() if audio_bytes else ""

    return {
        "ok": True,
        "user_text": user_text,
        "reply_text": reply_text,
        "audio_b64": audio_b64
    }
