"""API Key  -- ++SQLite"""
import os, json, time
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict
from tools.logger import get_logger

logger = get_logger("keymgr")

@dataclass
class ApiKey:
    name: str
    env_key: str
    value: str = ''
    provider: str = ''
    description: str = ''
    active: bool = True
    created_at: float = 0.0
    updated_at: float = 0.0

class KeyManager:
    ''"API Key  --  > .env ''"

    _keys: Dict[str, ApiKey] = {}
    _env_map = {
        "OPENAI_API_KEY": ("openai", "OpenAI GPT-4/Vision/TTS"),
        "DEEPSEEK_API_KEY": ("deepseek", "DeepSeek V3"),
        "CLAUDE_API_KEY": ("claude", "Claude Agent"),
        "TELEGRAM_BOT_TOKEN": ("telegram", "Telegram Bot"),
        "WECHAT_TOKEN": ("wechat", "Token"),
        "WECOM_CORP_ID": ("wecom", "CorpID"),
        "DINGTALK_APP_KEY": ("dingtalk", "AppKey"),
        "AI302_API_KEY": ("302ai", "302.AI "),
        "POE_API_KEY": ("poe", "Poe "),
        "GITHUB_TOKEN": ("github", "GitHub Personal Token"),
    }

    @classmethod
    def load(cls):
        ''"SQLite + .env''"
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
            logger.info(f" {len(cls._keys)} API Key")
        except Exception as e:
            logger.warning(f"API Key: {e}")

        # .env 
        for env_key, (provider, desc) in cls._env_map.items():
            if env_key not in cls._keys:
                env_val = os.getenv(env_key, '')
                if env_val:
                    cls._keys[env_key] = ApiKey(
                        name=env_key, env_key=env_key, value=env_val,
                        provider=provider, description=desc, active=True,
                        created_at=time.time(), updated_at=time.time()
                    )

    @classmethod
    def save(cls):
        ''"SQLite''"
        from tools.memory_store import memory_store
        try:
            data = {k: asdict(v) for k, v in cls._keys.items()}
            memory_store.set_knowledge("api_keys", '', json.dumps(data, ensure_ascii=False))
        except Exception as e:
            logger.error(f"API Key: {e}")

    @classmethod
    def get_all(cls) -> List[Dict]:
        ''"Key()''"
        return [{
            "env_key": k, "name": v.name, "provider": v.provider,
            "description": v.description, "active": v.active,
            "value_preview": v.value[:8] + "***" + v.value[-4:] if len(v.value) > 12 else "***",
            "has_value": bool(v.value),
            "updated_at": v.updated_at
        } for k, v in cls._keys.items()]

    @classmethod
    def get_value(cls, env_key: str) -> str:
        ''"Key(API)''"
        key = cls._keys.get(env_key)
        if key and key.active and key.value:
            return key.value
        return os.getenv(env_key, '')

    @classmethod
    def set_key(cls, env_key: str, value: str, name: str = '', description: str = '') -> bool:
        ''"Key''"
        provider, desc = cls._env_map.get(env_key, ("custom", description or "Key"))
        now = time.time()
        existing = cls._keys.get(env_key)
        cls._keys[env_key] = ApiKey(
            name=name or env_key, env_key=env_key, value=value,
            provider=provider, description=desc, active=True,
            created_at=existing.created_at if existing else now,
            updated_at=now
        )
        cls.save()
        logger.info(f"Key: {env_key}")
        return True

    @classmethod
    def delete_key(cls, env_key: str) -> bool:
        ''"Key''"
        if env_key in cls._keys:
            del cls._keys[env_key]
            cls.save()
            logger.info(f"Key: {env_key}")
            return True
        return False

    @classmethod
    def toggle_key(cls, env_key: str) -> bool:
        ''"/Key''"
        key = cls._keys.get(env_key)
        if key:
            key.active = not key.active
            key.updated_at = time.time()
            cls.save()
            return True
        return False

    @classmethod
    def get_status(cls) -> Dict:
        ''"Key''"
        all_keys = cls._env_map.copy()
        all_keys.update({k: ("custom", v.description) for k, v in cls._keys.items() if k not in cls._env_map})
        caps = {}
        for env_key, (provider, desc) in all_keys.items():
            key = cls._keys.get(env_key)
            caps[env_key] = {
                "ok": bool(key and key.active and key.value) or bool(os.getenv(env_key, '')),
                "provider": provider,
                "description": desc,
                "managed": env_key in cls._keys
            }
        available = sum(1 for v in caps.values() if v["ok"])
        return {"ok": True, "available": available, "total": len(caps), "capabilities": caps}


try:
    KeyManager.load()
except:
    pass

key_manager = KeyManager()
