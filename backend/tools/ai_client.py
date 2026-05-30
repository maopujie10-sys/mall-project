"""AI -- provider, agent_chat.pyadvanced_ai.py"""
import os, json, httpx
from config import OPENAI_API_KEY, OPENAI_BASE_URL, DEEPSEEK_API_KEY

DEEPSEEK_BASE_URL = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com/v1")

AVAILABLE_MODELS = {
    "deepseek-chat":       {"provider": "deepseek", "cost": "0.14/1M",  "vision": False},
    "deepseek-reasoner":   {"provider": "deepseek", "cost": "0.55/1M",  "vision": False},
    "gpt-3.5-turbo":       {"provider": "openai",   "cost": "0.50/1M",  "vision": False},
    "gpt-4o-mini":         {"provider": "openai",   "cost": "0.15/1M",  "vision": True},
    "gpt-4o":              {"provider": "openai",   "cost": "2.50/1M",  "vision": True},
}

# ()
DEFAULT_MODEL = os.getenv("CHEAP_MODEL", "deepseek-chat")
SMART_MODEL = os.getenv("SMART_MODEL", "gpt-4o")

def _route_model(model):
    ''" (api_key, base_url)''"
    if model.startswith("deepseek"):
        return DEEPSEEK_API_KEY, DEEPSEEK_BASE_URL
    return OPENAI_API_KEY, OPENAI_BASE_URL or "https://api.openai.com/v1"

def pick_model(task_complexity="auto", need_vision=False, step_count=0):
    ''"AI''"
    if need_vision:
        
        if OPENAI_API_KEY:
            return "gpt-4o-mini" if task_complexity != "hard" else "gpt-4o"
        return DEFAULT_MODEL  # ()
    if task_complexity == "hard" or step_count > 5:
        return SMART_MODEL
    return DEFAULT_MODEL

async def call_ai(messages, model=None, max_tokens=1000, temperature=0.7):
    ''"AI -- provider''"
    if model is None:
        model = DEFAULT_MODEL
    
    key, base = _route_model(model)
    if not key:
        # keyprovider
        if OPENAI_API_KEY and model.startswith("deepseek"):
            key, base = OPENAI_API_KEY, OPENAI_BASE_URL or "https://api.openai.com/v1"
            model = "gpt-3.5-turbo"  
        elif DEEPSEEK_API_KEY and not model.startswith("deepseek"):
            key, base = DEEPSEEK_API_KEY, DEEPSEEK_BASE_URL
            model = "deepseek-chat"
        else:
            return "API Key (DEEPSEEK_API_KEYOPENAI_API_KEY)"
    
    async with httpx.AsyncClient(timeout=120) as c:
        r = await c.post(
            f"{base}/chat/completions",
            headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
            json={"model": model, "messages": messages, "max_tokens": max_tokens, "temperature": temperature}
        )
        if r.status_code == 200:
            return r.json().get("choices", [{}])[0].get("message", {}).get("content", '')
        return f"API:{r.status_code}"

async def stream_ai(messages, model=None, temperature=0.8):
    ''"AI -- token''"
    if model is None:
        model = DEFAULT_MODEL
    
    key, base = _route_model(model)
    if not key:
        yield "API Key"
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
                        t = j.get("choices", [{}])[0].get("delta", {}).get("content", '')
                        if t:
                            yield t
                    except:
                        pass

async def vision_analyze(image_base64, question='', model="gpt-4o-mini"):
    ''" -- ''"
    if not OPENAI_API_KEY:
        return {"ok": False, "error": "OPENAI_API_KEY"}
    
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
            return {"ok": True, "reply": r.json().get("choices", [{}])[0].get("message", {}).get("content", '')}
        return {"ok": False, "error": f"API:{r.status_code}"}

def get_available_models():
    ''''''
    result = {}
    for name, info in AVAILABLE_MODELS.items():
        key = DEEPSEEK_API_KEY if info["provider"] == "deepseek" else OPENAI_API_KEY
        result[name] = {**info, "available": bool(key)}
    return result