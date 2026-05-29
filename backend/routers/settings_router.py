"""系统设置 — 环境变量/API密钥/通用配置管理"""
import os
from fastapi import APIRouter, Depends
from auth import verify_token
from risk import handle_risk
from state import state

router = APIRouter(prefix="/settings", tags=["Settings"])

# 安全暴露的环境变量白名单
ALLOWED_ENV_KEYS = [
    "APP_ENV", "AGENT_TOKEN", "MALL_BASE_URL",
    "CLAUDE_API_KEY", "DEEPSEEK_API_KEY", "OPENAI_API_KEY", "GEMINI_API_KEY",
    "OLLAMA_BASE_URL", "OLLAMA_MODEL",
    "MALL_DB_HOST", "MALL_DB_PORT", "MALL_DB_NAME",
    "REDIS_HOST", "REDIS_PORT",
    "BACKUP_DIR", "CERT_DIR", "LOG_DIR",
]


@router.get("/env")
async def get_settings(_=Depends(verify_token)):
    """获取系统环境变量（白名单）"""
    await handle_risk("L1", "查看系统设置")
    envs = {}
    for key in ALLOWED_ENV_KEYS:
        val = os.getenv(key, "")
        if val:
            # 隐藏密钥中间部分
            if "KEY" in key or "TOKEN" in key or "PASSWORD" in key:
                envs[key] = val[:8] + "****" + val[-4:] if len(val) > 12 else "****"
            else:
                envs[key] = val
    return {"ok": True, "env": envs, "count": len(envs)}


@router.get("/state")
async def get_state_keys(_=Depends(verify_token)):
    """查看系统状态数据key列表"""
    await handle_risk("L1", "查看系统状态")
    keys = list(state._data.keys())
    sizes = {}
    for k in keys:
        v = state._data[k]
        if isinstance(v, list):
            sizes[k] = f"{len(v)}条"
        elif isinstance(v, dict):
            sizes[k] = f"{len(v)}项"
        else:
            sizes[k] = str(type(v).__name__)
    return {"ok": True, "keys": [{"key": k, "size": sizes.get(k, "?")} for k in sorted(keys)], "count": len(keys)}


@router.post("/state/clear")
async def clear_state_key(key: str, _=Depends(verify_token)):
    """清空指定状态数据"""
    await handle_risk("L3", f"清空状态数据: {key}")
    if key in state._data:
        if isinstance(state._data[key], list):
            state._data[key] = []
        elif isinstance(state._data[key], dict):
            state._data[key] = {}
        state._save()
        return {"ok": True, "key": key, "cleared": True}
    return {"ok": False, "error": f"key不存在: {key}"}
