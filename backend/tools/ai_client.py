"""统一AI客户端 -- 多provider自动路由, 被agent_chat.py和advanced_ai.py共用"""
import os, json, httpx
from config import OPENAI_API_KEY, OPENAI_BASE_URL, DEEPSEEK_API_KEY

DEEPSEEK_BASE_URL = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com/v1")

# 模型注册表
AVAILABLE_MODELS = {
    "deepseek-chat":       {"provider": "deepseek", "cost": "0.14/1M",  "vision": False},
    "deepseek-reasoner":   {"provider": "deepseek", "cost": "0.55/1M",  "vision": False},
    "gpt-3.5-turbo":       {"provider": "openai",   "cost": "0.50/1M",  "vision": False},
    "gpt-4o-mini":         {"provider": "openai",   "cost": "0.15/1M",  "vision": True},
    "gpt-4o":              {"provider": "openai",   "cost": "2.50/1M",  "vision": True},
}

# 默认模型(环境变量可覆盖)
DEFAULT_MODEL = os.getenv("CHEAP_MODEL", "deepseek-chat")
SMART_MODEL = os.getenv("SMART_MODEL", "gpt-4o")

def _route_model(model):
    """根据模型名返回 (api_key, base_url)"""
    if model.startswith("deepseek"):
        return DEEPSEEK_API_KEY, DEEPSEEK_BASE_URL
    return OPENAI_API_KEY, OPENAI_BASE_URL or "https://api.openai.com/v1"

def pick_model(task_complexity="auto", need_vision=False, step_count=0):
    """AI自动选模型"""
    if need_vision:
        # 视觉任务需要多模态模型
        if OPENAI_API_KEY:
            return "gpt-4o-mini" if task_complexity != "hard" else "gpt-4o"
        return DEFAULT_MODEL  # 降级(可能不支持视觉)
    if task_complexity == "hard" or step_count > 5:
        return SMART_MODEL
    return DEFAULT_MODEL

async def call_ai(messages, model=None, max_tokens=1000, temperature=0.7):
    """调用AI -- 自动路由provider"""
    if model is None:
        model = DEFAULT_MODEL
    
    key, base = _route_model(model)
    if not key:
        # 降级到有key的provider
        if OPENAI_API_KEY and model.startswith("deepseek"):
            key, base = OPENAI_API_KEY, OPENAI_BASE_URL or "https://api.openai.com/v1"
            model = "gpt-3.5-turbo"  # 降级模型
        elif DEEPSEEK_API_KEY and not model.startswith("deepseek"):
            key, base = DEEPSEEK_API_KEY, DEEPSEEK_BASE_URL
            model = "deepseek-chat"
        else:
            return "需要配置API Key (DEEPSEEK_API_KEY或OPENAI_API_KEY)"
    
    async with httpx.AsyncClient(timeout=120) as c:
        r = await c.post(
            f"{base}/chat/completions",
            headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
            json={"model": model, "messages": messages, "max_tokens": max_tokens, "temperature": temperature}
        )
        if r.status_code == 200:
            return r.json().get("choices", [{}])[0].get("message", {}).get("content", "")
        return f"API错误:{r.status_code}"

async def stream_ai(messages, model=None, temperature=0.8):
    """流式调用AI -- 逐token返回"""
    if model is None:
        model = DEFAULT_MODEL
    
    key, base = _route_model(model)
    if not key:
        yield "需要配置API Key"
        return
    
    async with httpx.AsyncClient(timeout=120) as c:
        async with c.stream(
            "POST", f"{base}/chat/completions",
            headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
            json={"model": model, "messages": messages, "stream": True, "temperature": temperature}
        ) as r:
            async for line in r.aiter_lines():
                if line.startswith("data: "):
                    d = line[6:]
                    if d == "[DONE]":
                        break
                    try:
                        j = json.loads(d)
                        t = j.get("choices", [{}])[0].get("delta", {}).get("content", "")
                        if t:
                            yield t
                    except:
                        pass

async def vision_analyze(image_base64, question="描述这张图片", model="gpt-4o-mini"):
    """视觉分析 -- 需要多模态模型"""
    if not OPENAI_API_KEY:
        return {"ok": False, "error": "视觉分析需要OPENAI_API_KEY"}
    
    key, base = OPENAI_API_KEY, OPENAI_BASE_URL or "https://api.openai.com/v1"
    
    async with httpx.AsyncClient(timeout=60) as c:
        r = await c.post(
            f"{base}/chat/completions",
            headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
            json={
                "model": model,
                "messages": [{
                    "role": "user",
                    "content": [
                        {"type": "text", "text": question},
                        {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{image_base64}", "detail": "low"}}
                    ]
                }],
                "max_tokens": 500
            }
        )
        if r.status_code == 200:
            return {"ok": True, "reply": r.json().get("choices", [{}])[0].get("message", {}).get("content", "")}
        return {"ok": False, "error": f"API:{r.status_code}"}

def get_available_models():
    """列出所有可用模型及状态"""
    result = {}
    for name, info in AVAILABLE_MODELS.items():
        key = DEEPSEEK_API_KEY if info["provider"] == "deepseek" else OPENAI_API_KEY
        result[name] = {**info, "available": bool(key)}
    return result