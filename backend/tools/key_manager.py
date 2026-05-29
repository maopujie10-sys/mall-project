"""API Key 管理器 -- 后台增删改查+热切换,SQLite持久化"""
import os, json, time
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict
from tools.logger import get_logger

logger = get_logger("keymgr")

@dataclass
class ApiKey:
    name: str
    env_key: str
    value: str = ""
    provider: str = ""
    description: str = ""
    active: bool = True
    created_at: float = 0.0
    updated_at: float = 0.0

class KeyManager:
    """API Key 管理器 -- 后台管理 > .env 兜底"""

    _keys: Dict[str, ApiKey] = {}
    _env_map = {
        "OPENAI_API_KEY": ("openai", "OpenAI GPT-4/Vision/TTS"),
        "DEEPSEEK_API_KEY": ("deepseek", "DeepSeek V3推理"),
        "CLAUDE_API_KEY": ("claude", "Claude Agent总控"),
        "TELEGRAM_BOT_TOKEN": ("telegram", "Telegram Bot"),
        "WECHAT_TOKEN": ("wechat", "微信公众号Token"),
        "WECOM_CORP_ID": ("wecom", "企业微信CorpID"),
        "DINGTALK_APP_KEY": ("dingtalk", "钉钉AppKey"),
        "GITHUB_TOKEN": ("github", "GitHub Personal Token"),
    }

    @classmethod
    def load(cls):
        """从SQLite恢复 + .env兜底"""
        from tools.memory_store import memory_store
        try:
            raw = memory_store.get_knowledge("api_keys")
            if raw and isinstance(raw, list):
                for row in raw:
                    val = row[2] if isinstance(row, tuple) and len(row) > 2 else str(row)
                    try:
                        d = json.loads(val)
                        cls._keys[d["env_key"]] = ApiKey(**d)
                    except:
                        pass
            logger.info(f"已加载 {len(cls._keys)} 个API Key")
        except Exception as e:
            logger.warning(f"加载API Key失败: {e}")

        # .env 兜底
        for env_key, (provider, desc) in cls._env_map.items():
            if env_key not in cls._keys:
                env_val = os.getenv(env_key, "")
                if env_val:
                    cls._keys[env_key] = ApiKey(
                        name=env_key, env_key=env_key, value=env_val,
                        provider=provider, description=desc, active=True,
                        created_at=time.time(), updated_at=time.time()
                    )

    @classmethod
    def save(cls):
        """持久化到SQLite"""
        from tools.memory_store import memory_store
        try:
            data = {k: asdict(v) for k, v in cls._keys.items()}
            memory_store.set_knowledge("api_keys", "", json.dumps(data, ensure_ascii=False))
        except Exception as e:
            logger.error(f"保存API Key失败: {e}")

    @classmethod
    def get_all(cls) -> List[Dict]:
        """获取所有Key(脱敏)"""
        return [{
            "env_key": k, "name": v.name, "provider": v.provider,
            "description": v.description, "active": v.active,
            "value_preview": v.value[:8] + "***" + v.value[-4:] if len(v.value) > 12 else "***",
            "has_value": bool(v.value),
            "updated_at": v.updated_at
        } for k, v in cls._keys.items()]

    @classmethod
    def get_value(cls, env_key: str) -> str:
        """获取Key实际值(用于API调用)"""
        key = cls._keys.get(env_key)
        if key and key.active and key.value:
            return key.value
        return os.getenv(env_key, "")

    @classmethod
    def set_key(cls, env_key: str, value: str, name: str = "", description: str = "") -> bool:
        """添加或更新Key"""
        provider, desc = cls._env_map.get(env_key, ("custom", description or "自定义Key"))
        now = time.time()
        existing = cls._keys.get(env_key)
        cls._keys[env_key] = ApiKey(
            name=name or env_key, env_key=env_key, value=value,
            provider=provider, description=desc, active=True,
            created_at=existing.created_at if existing else now,
            updated_at=now
        )
        cls.save()
        logger.info(f"Key已更新: {env_key}")
        return True

    @classmethod
    def delete_key(cls, env_key: str) -> bool:
        """删除Key"""
        if env_key in cls._keys:
            del cls._keys[env_key]
            cls.save()
            logger.info(f"Key已删除: {env_key}")
            return True
        return False

    @classmethod
    def toggle_key(cls, env_key: str) -> bool:
        """启用/禁用Key"""
        key = cls._keys.get(env_key)
        if key:
            key.active = not key.active
            key.updated_at = time.time()
            cls.save()
            return True
        return False

    @classmethod
    def get_status(cls) -> Dict:
        """获取所有Key状态"""
        all_keys = cls._env_map.copy()
        all_keys.update({k: ("custom", v.description) for k, v in cls._keys.items() if k not in cls._env_map})
        caps = {}
        for env_key, (provider, desc) in all_keys.items():
            key = cls._keys.get(env_key)
            caps[env_key] = {
                "ok": bool(key and key.active and key.value) or bool(os.getenv(env_key, "")),
                "provider": provider,
                "description": desc,
                "managed": env_key in cls._keys
            }
        available = sum(1 for v in caps.values() if v["ok"])
        return {"ok": True, "available": available, "total": len(caps), "capabilities": caps}

# 启动加载
try:
    KeyManager.load()
except:
    pass

key_manager = KeyManager()
