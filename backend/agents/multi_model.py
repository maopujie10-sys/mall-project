"""Multi-Model Router — 多模型智能路由
支持: DeepSeek / Claude / GPT / Gemini / OpenRouter / 本地模型"""
import os
from enum import Enum
from dataclasses import dataclass

class ModelMode(Enum):
    QUALITY = "quality"       # 高质量：复杂推理
    FAST = "fast"             # 超高速：简单任务
    CHEAP = "cheap"           # 省钱：批量任务
    DEV = "dev"               # 开发：代码生成
    OPS = "ops"               # 运维：系统操作
    DEEP = "deep"             # 深度推理：复杂分析

@dataclass
class ModelConfig:
    provider: str
    model_name: str
    api_key_env: str
    api_base: str
    cost_per_1k: float
    max_tokens: int

class ModelRouter:
    """多模型智能路由器"""

    MODELS = {
        "deepseek-v3": ModelConfig("deepseek", "deepseek-chat", "DEEPSEEK_API_KEY", "https://api.deepseek.com/v1", 0.001, 65536),
        "deepseek-r1": ModelConfig("deepseek", "deepseek-reasoner", "DEEPSEEK_API_KEY", "https://api.deepseek.com/v1", 0.002, 65536),
        "claude-sonnet": ModelConfig("anthropic", "claude-sonnet-4-20250514", "CLAUDE_API_KEY", "https://api.anthropic.com", 0.015, 200000),
        "gpt-4o": ModelConfig("openai", "gpt-4o", "OPENAI_API_KEY", "https://api.openai.com/v1", 0.015, 128000),
        "gemini-flash": ModelConfig("google", "gemini-2.0-flash", "GEMINI_API_KEY", "https://generativelanguage.googleapis.com", 0.001, 1048576),
    }

    MODE_ROUTING = {
        ModelMode.QUALITY: ["claude-sonnet", "gpt-4o"],
        ModelMode.FAST: ["gemini-flash", "deepseek-v3"],
        ModelMode.CHEAP: ["deepseek-v3", "gemini-flash"],
        ModelMode.DEV: ["claude-sonnet", "deepseek-v3"],
        ModelMode.OPS: ["deepseek-v3", "gemini-flash"],
        ModelMode.DEEP: ["deepseek-r1", "claude-sonnet"],
    }

    @staticmethod
    def route(mode: ModelMode, preferred: str = None) -> ModelConfig:
        """根据模式智能选择模型"""
        if preferred and preferred in ModelRouter.MODELS:
            return ModelRouter.MODELS[preferred]
        candidates = ModelRouter.MODE_ROUTING.get(mode, ModelRouter.MODE_ROUTING[ModelMode.QUALITY])
        for c in candidates:
            if c in ModelRouter.MODELS:
                api_key = os.getenv(ModelRouter.MODELS[c].api_key_env, "")
                if api_key:
                    return ModelRouter.MODELS[c]
        # 兜底：返回第一个配置的模型
        for name, config in ModelRouter.MODELS.items():
            if os.getenv(config.api_key_env, ""):
                return config
        return ModelRouter.MODELS["deepseek-v3"]

    @staticmethod
    def list_models() -> list:
        """列出所有可用模型"""
        return [
            {
                "id": name,
                "provider": cfg.provider,
                "model": cfg.model_name,
                "cost": f"${cfg.cost_per_1k}/1K tokens",
                "available": bool(os.getenv(cfg.api_key_env, "")),
            }
            for name, cfg in ModelRouter.MODELS.items()
        ]


class FridayModes:
    MODES={"quality":{"desc":"high quality","model":"claude-3-5-sonnet-latest","max_tokens":4096},"speed":{"desc":"fast","model":"deepseek-chat","max_tokens":512},"cheap":{"desc":"cheap","model":"deepseek-chat","max_tokens":256},"dev":{"desc":"dev","model":"deepseek-chat","max_tokens":2048},"ops":{"desc":"ops","model":"claude-3-5-sonnet-latest","max_tokens":1024},"deep":{"desc":"deep","model":"claude-3-5-sonnet-latest","max_tokens":8192}}
    @classmethod
    def select(cls,task_type="chat"):
        m={"chat":"quality","quick":"speed","code":"dev","deploy":"ops","analyze":"deep"}.get(task_type,"quality")
        return {"mode":m,**cls.MODES[m]}
    @classmethod
    def list_modes(cls):
        return [{"id":k,**v} for k,v in cls.MODES.items()]
