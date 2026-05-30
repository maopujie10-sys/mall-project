''" API -- API Key + ''"
import os
from fastapi import APIRouter, Depends
from auth import verify_token

router = APIRouter(prefix="/agent/capabilities", tags=["Capabilities"])

@router.get("/status")
async def capabilities_status(_=Depends(verify_token)):
    ''"AI''"
    caps = {}

    # API Keys
    caps["openai"] = {"ok": bool(os.getenv("OPENAI_API_KEY")), "label": "OpenAI GPT-4/Vision/TTS/STT"}
    caps["deepseek"] = {"ok": bool(os.getenv("DEEPSEEK_API_KEY")), "label": "DeepSeek V3"}
    caps["claude"] = {"ok": bool(os.getenv("CLAUDE_API_KEY")), "label": "Claude Agent"}
    caps["ollama"] = {"ok": False, "label": "Ollama()"}

    # Ollama
    try:
        import httpx
        async with httpx.AsyncClient(timeout=3) as client:
            resp = await client.get(os.getenv("OLLAMA_HOST", "http://localhost:11434") + "/api/tags")
            if resp.status_code == 200:
                models = resp.json().get("models", [])
                caps["ollama"] = {"ok": True, "label": f"Ollama({len(models)})", "models": [m["name"] for m in models[:5]]}
    except:
        pass

    
    caps["telegram"] = {"ok": bool(os.getenv("TELEGRAM_BOT_TOKEN")), "label": "Telegram Bot"}
    caps["wechat"] = {"ok": bool(os.getenv("WECHAT_TOKEN")), "label": ''}
    caps["database"] = {"ok": True, "label": "MySQL/SQLite"}
    caps["redis"] = {"ok": bool(os.getenv("REDIS_URL")), "label": "Redis"}

    
    available = sum(1 for v in caps.values() if v["ok"])
    total = len(caps)

    return {
        "ok": True,
        "available": available,
        "total": total,
        "score": round(available / total * 100),
        "grade": "A" if available >= 6 else "B" if available >= 4 else "C" if available >= 2 else "D",
        "capabilities": caps,
        "tip": "API Key" if available < total else ''
    }

@router.get("/quick")
async def capabilities_quick():
    ''''''
    ok_count = 0
    if os.getenv("OPENAI_API_KEY"): ok_count += 1
    if os.getenv("DEEPSEEK_API_KEY"): ok_count += 1
    if os.getenv("CLAUDE_API_KEY"): ok_count += 1
    return {"ok": True, "ready": ok_count > 0, "api_keys": ok_count, "message": f"{ok_count}API Key" if ok_count else "API Key"}
