"""系统能力状态 API -- 检测各API Key配置 + 模型可用性"""
import os
from fastapi import APIRouter, Depends
from auth import verify_token

router = APIRouter(prefix="/agent/capabilities", tags=["Capabilities"])

@router.get("/status")
async def capabilities_status(_=Depends(verify_token)):
    """检测所有AI能力状态"""
    caps = {}

    # API Keys
    caps["openai"] = {"ok": bool(os.getenv("OPENAI_API_KEY")), "label": "OpenAI GPT-4/Vision/TTS/STT"}
    caps["deepseek"] = {"ok": bool(os.getenv("DEEPSEEK_API_KEY")), "label": "DeepSeek V3推理"}
    caps["claude"] = {"ok": bool(os.getenv("CLAUDE_API_KEY")), "label": "Claude Agent总控"}
    caps["ollama"] = {"ok": False, "label": "Ollama本地模型(免费)"}

    # 检测Ollama
    try:
        import httpx
        async with httpx.AsyncClient(timeout=3) as client:
            resp = await client.get(os.getenv("OLLAMA_HOST", "http://localhost:11434") + "/api/tags")
            if resp.status_code == 200:
                models = resp.json().get("models", [])
                caps["ollama"] = {"ok": True, "label": f"Ollama本地({len(models)}模型)", "models": [m["name"] for m in models[:5]]}
    except:
        pass

    # 其他服务
    caps["telegram"] = {"ok": bool(os.getenv("TELEGRAM_BOT_TOKEN")), "label": "Telegram Bot"}
    caps["wechat"] = {"ok": bool(os.getenv("WECHAT_TOKEN")), "label": "微信公众号"}
    caps["database"] = {"ok": True, "label": "MySQL/SQLite"}
    caps["redis"] = {"ok": bool(os.getenv("REDIS_URL")), "label": "Redis队列"}

    # 统计
    available = sum(1 for v in caps.values() if v["ok"])
    total = len(caps)

    return {
        "ok": True,
        "available": available,
        "total": total,
        "score": round(available / total * 100),
        "grade": "A" if available >= 6 else "B" if available >= 4 else "C" if available >= 2 else "D",
        "capabilities": caps,
        "tip": "配置更多API Key提升能力" if available < total else "全部能力就绪"
    }

@router.get("/quick")
async def capabilities_quick():
    """无需认证的快速检测"""
    ok_count = 0
    if os.getenv("OPENAI_API_KEY"): ok_count += 1
    if os.getenv("DEEPSEEK_API_KEY"): ok_count += 1
    if os.getenv("CLAUDE_API_KEY"): ok_count += 1
    return {"ok": True, "ready": ok_count > 0, "api_keys": ok_count, "message": f"{ok_count}个API Key已配置" if ok_count else "未配置API Key"}
