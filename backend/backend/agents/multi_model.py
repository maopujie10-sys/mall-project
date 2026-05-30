''"Multi-Model Router -- 
: Ollama() / DeepSeek / Claude / GPT / Gemini''"

import os
import httpx
from enum import Enum
from dataclasses import dataclass


class ModelMode(Enum):
    QUALITY = "quality"
    FAST = "fast"
    CHEAP = "cheap"
    DEV = "dev"
    OPS = "ops"
    DEEP = "deep"


@dataclass
class ModelConfig:
    provider: str
    model_name: str
    api_key_env: str
    api_base: str
    cost_per_1k: float
    max_tokens: int
    is_local: bool = False  # API Key


import httpx as _httpx

_model_client = None

def _get_model_client():
    global _model_client
    if _model_client is None:
        limits = _httpx.Limits(max_keepalive_connections=10, max_connections=20)
        _model_client = _httpx.AsyncClient(timeout=30, limits=limits)
    return _model_client

class ModelRouter:
    ''" --  + ''"

    OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")

    MODELS = {
        # ()
        "ollama-qwen": ModelConfig("ollama", "qwen2.5:7b", '', OLLAMA_HOST + "/v1", 0.0, 32768, is_local=True),
        "ollama-r1": ModelConfig("ollama", "deepseek-r1:7b", '', OLLAMA_HOST + "/v1", 0.0, 32768, is_local=True),
        "ollama-llama": ModelConfig("ollama", "llama3:8b", '', OLLAMA_HOST + "/v1", 0.0, 32768, is_local=True),
        # ()
        "deepseek-v3": ModelConfig("deepseek", "deepseek-chat", "DEEPSEEK_API_KEY", "https://api.deepseek.com/v1", 0.001, 65536),
        "deepseek-r1": ModelConfig("deepseek", "deepseek-reasoner", "DEEPSEEK_API_KEY", "https://api.deepseek.com/v1", 0.002, 65536),
        "claude-sonnet": ModelConfig("anthropic", "claude-3-5-sonnet-20241022", "CLAUDE_API_KEY", "https://api.anthropic.com", 0.015, 200000),
        "gpt-4o": ModelConfig("openai", "gpt-4o", "OPENAI_API_KEY", "https://api.openai.com/v1", 0.015, 128000),
        "gemini-flash": ModelConfig("google", "gemini-2.0-flash", "GEMINI_API_KEY", "https://generativelanguage.googleapis.com", 0.001, 1048576),
    }

    # : -> 
    MODE_ROUTING = {
        ModelMode.QUALITY: ["ollama-qwen", "claude-sonnet", "gpt-4o"],
        ModelMode.FAST: ["ollama-qwen", "gemini-flash", "deepseek-v3"],
        ModelMode.CHEAP: ["ollama-qwen", "ollama-r1", "deepseek-v3"],
        ModelMode.DEV: ["ollama-r1", "claude-sonnet", "deepseek-v3"],
        ModelMode.OPS: ["ollama-qwen", "deepseek-v3", "gemini-flash"],
        ModelMode.DEEP: ["ollama-r1", "deepseek-r1", "claude-sonnet"],
    }

    @staticmethod
    async def _check_ollama() -> bool:
        ''" Ollama ''"
        try:
            client = _get_model_client()
            r = await client.get(ModelRouter.OLLAMA_HOST + "/api/tags")
            return r.status_code == 200
        except Exception:
            return False

    @staticmethod
    def route(mode: ModelMode, preferred: str = None) -> ModelConfig:
        ''" -- ''"
        if preferred and preferred in ModelRouter.MODELS:
            return ModelRouter.MODELS[preferred]

        candidates = ModelRouter.MODE_ROUTING.get(mode, ModelRouter.MODE_ROUTING[ModelMode.QUALITY])

        for c in candidates:
            if c not in ModelRouter.MODELS:
                continue
            cfg = ModelRouter.MODELS[c]
            # : API Key,
            if cfg.is_local:
                return cfg
            # : API Key
            if os.getenv(cfg.api_key_env, ''):
                return cfg

        # :
        for name, config in ModelRouter.MODELS.items():
            if config.is_local or os.getenv(config.api_key_env, ''):
                return config

        return ModelRouter.MODELS["ollama-qwen"]

    @staticmethod
    async def list_models() -> list:
        ''''''
        ollama_online = await ModelRouter._check_ollama()
        models = []
        for name, cfg in ModelRouter.MODELS.items():
            if cfg.is_local:
                available = ollama_online
            else:
                available = bool(os.getenv(cfg.api_key_env, ''))
            models.append({
                "id": name,
                "provider": cfg.provider,
                "model": cfg.model_name,
                "cost": '' if cfg.is_local else f"/1K tokens",
                "local": cfg.is_local,
                "available": available,
            })
        return models

    @staticmethod
    async def chat(model_id: str = None, messages: list = None, **kwargs) -> dict:
        ''" --  Ollama(OpenAI)  API, model_idNone''"
        if model_id is None or messages is None:
            return await cls.smart_chat(messages or [], **kwargs)
        cfg = ModelRouter.MODELS.get(model_id)
        if not cfg:
            return {"error": f": {model_id}"}

        headers = {"Content-Type": "application/json"}
        if not cfg.is_local:
            from tools.key_manager import key_manager
            api_key = key_manager.get_value(cfg.api_key_env) or os.getenv(cfg.api_key_env, '')
            if not api_key:
                return {"error": f"{cfg.provider} API Key "}
            headers["Authorization"] = f"Bearer {api_key}"

        payload = {
            "model": cfg.model_name,
            "messages": messages,
            "max_tokens": kwargs.get("max_tokens", cfg.max_tokens),
            "temperature": kwargs.get("temperature", 0.7),
        }

        try:
            client = _get_model_client()
            r = await client.post(
                cfg.api_base + "/chat/completions",
                json=payload,
                headers=headers,
            )
            if r.status_code != 200:
                return {"error": f"{cfg.provider}  {r.status_code}: {r.text[:200]}"}
            data = r.json()
            return {
                "model": model_id,
                "provider": cfg.provider,
                "content": data["choices"][0]["message"]["content"],
                "usage": data.get("usage", {}),
            }
        except Exception as e:
            return {"error": str(e)}


class FridayModes:
    MODES = {
        "quality": {"desc": '', "model": "ollama-qwen", "max_tokens": 4096},
        "speed": {"desc": '', "model": "ollama-qwen", "max_tokens": 512},
        "cheap": {"desc": '', "model": "ollama-qwen", "max_tokens": 256},
        "dev": {"desc": '', "model": "ollama-r1", "max_tokens": 2048},
        "ops": {"desc": '', "model": "ollama-qwen", "max_tokens": 1024},
        "deep": {"desc": '', "model": "ollama-r1", "max_tokens": 8192},
    }

    @classmethod
    def select(cls, task_type="chat"):
        m = {"chat": "quality", "quick": "speed", "code": "dev", "deploy": "ops", "analyze": "deep"}.get(task_type, "quality")
        return {"mode": m, **cls.MODES[m]}


    @classmethod
    def judge_task_complexity(cls, prompt: str) -> str:
        ''''''
        simple_kw = ["hello","hi",'','','','']
        complex_kw = ['','','','','','','',"debug"]
        lower = prompt.lower()
        if any(k in lower for k in complex_kw) or len(prompt) > 500: return "complex"
        if len(prompt) < 50 and any(k in lower for k in simple_kw): return "simple"
        return "medium"

    @classmethod
    def smart_chat_with_fallback(cls, messages: list, mode: str = "smart") -> dict:
        ''"+''"
        prompt = ''.join([m.get("content",'') for m in messages if m.get("role")=="user"])[:2000]
        complexity = cls.judge_task_complexity(prompt)
        models = ["deepseek-chat"] if complexity == "simple" else (["openai/gpt-4o","claude-sonnet","deepseek-chat"] if complexity == "complex" else ["deepseek-chat","openai/gpt-4o-mini"])
        for model in models:
            try:
                result = cls._call_model(model, messages) if hasattr(cls,"_call_model") else {"content":'',"model":model}
                if result and result.get("content"):
                    result["model_used"] = model; result["complexity"] = complexity; return result
            except: continue
        return {"content":'',"model_used":"none","complexity":complexity}
    @classmethod
    def list_modes(cls):
        return [{"id": k, **v} for k, v in cls.MODES.items()]



    @staticmethod
    async def vote(prompt, models=None):
        ''": 3, ''"
        import asyncio, httpx, os
        candidates = models or ["deepseek-chat", "gpt-4o-mini"]
        async def ask(model):
            try:
                key = os.getenv("DEEPSEEK_API_KEY") if model == "deepseek-chat" else os.getenv("OPENAI_API_KEY")
                if not key: return {"model": model, "error": "no key"}
                if model == "deepseek-chat":
                    url = "https://api.deepseek.com/v1/chat/completions"
                else:
                    base = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
                    url = f"{base}/chat/completions"
                async with httpx.AsyncClient(timeout=30) as c:
                    body = {"model": model, "messages": [{"role": "user", "content": prompt}], "max_tokens": 512}
                    r = await c.post(url, headers={"Authorization": f"Bearer {key}"}, json=body)
                    if r.status_code == 200:
                        return {"model": model, "text": r.json()["choices"][0]["message"]["content"]}
            except Exception as e:
                return {"model": model, "error": str(e)[:50]}
            return {"model": model, "error": "failed"}
        results = await asyncio.gather(*[ask(m) for m in candidates[:3]])
        valid = [r for r in results if r.get("text")]
        best = max(valid, key=lambda x: len(x.get("text", ''))) if valid else None
        return {"ok": bool(best), "results": results, "winner": best["model"] if best else None}
