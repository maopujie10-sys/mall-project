"""API Key 绠＄悊鍣?-- 鍚庡彴澧炲垹鏀规煡+鐑垏鎹?SQLite鎸佷箙鍖?""
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
    """API Key 绠＄悊鍣?-- 鍚庡彴绠＄悊 > .env 鍏滃簳"""

    _keys: Dict[str, ApiKey] = {}
    _env_map = {
        "OPENAI_API_KEY": ("openai", "OpenAI GPT-4/Vision/TTS"),
        "DEEPSEEK_API_KEY": ("deepseek", "DeepSeek V3鎺ㄧ悊"),
        "CLAUDE_API_KEY": ("claude", "Claude Agent鎬绘帶"),
        "TELEGRAM_BOT_TOKEN": ("telegram", "Telegram Bot"),
        "WECHAT_TOKEN": ("wechat", "寰俊鍏紬鍙稵oken"),
        "WECOM_CORP_ID": ("wecom", "浼佷笟寰俊CorpID"),
        "DINGTALK_APP_KEY": ("dingtalk", "閽夐拤AppKey"),
        "AI302_API_KEY": ("302ai", "302.AI 多模型聚合"),
        "POE_API_KEY": ("poe", "Poe 多模型平台"),
        "GITHUB_TOKEN": ("github", "GitHub Personal Token"),
    }

    @classmethod
    def load(cls):
        """浠嶴QLite鎭㈠ + .env鍏滃簳"""
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
            logger.info(f"宸插姞杞?{len(cls._keys)} 涓狝PI Key")
        except Exception as e:
            logger.warning(f"鍔犺浇API Key澶辫触: {e}")

        # .env 鍏滃簳
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
        """鎸佷箙鍖栧埌SQLite"""
        from tools.memory_store import memory_store
        try:
            data = {k: asdict(v) for k, v in cls._keys.items()}
            memory_store.set_knowledge("api_keys", "", json.dumps(data, ensure_ascii=False))
        except Exception as e:
            logger.error(f"淇濆瓨API Key澶辫触: {e}")

    @classmethod
    def get_all(cls) -> List[Dict]:
        """鑾峰彇鎵€鏈塊ey(鑴辨晱)"""
        return [{
            "env_key": k, "name": v.name, "provider": v.provider,
            "description": v.description, "active": v.active,
            "value_preview": v.value[:8] + "***" + v.value[-4:] if len(v.value) > 12 else "***",
            "has_value": bool(v.value),
            "updated_at": v.updated_at
        } for k, v in cls._keys.items()]

    @classmethod
    def get_value(cls, env_key: str) -> str:
        """鑾峰彇Key瀹為檯鍊?鐢ㄤ簬API璋冪敤)"""
        key = cls._keys.get(env_key)
        if key and key.active and key.value:
            return key.value
        return os.getenv(env_key, "")

    @classmethod
    def set_key(cls, env_key: str, value: str, name: str = "", description: str = "") -> bool:
        """娣诲姞鎴栨洿鏂癒ey"""
        provider, desc = cls._env_map.get(env_key, ("custom", description or "鑷畾涔塊ey"))
        now = time.time()
        existing = cls._keys.get(env_key)
        cls._keys[env_key] = ApiKey(
            name=name or env_key, env_key=env_key, value=value,
            provider=provider, description=desc, active=True,
            created_at=existing.created_at if existing else now,
            updated_at=now
        )
        cls.save()
        logger.info(f"Key宸叉洿鏂? {env_key}")
        return True

    @classmethod
    def delete_key(cls, env_key: str) -> bool:
        """鍒犻櫎Key"""
        if env_key in cls._keys:
            del cls._keys[env_key]
            cls.save()
            logger.info(f"Key宸插垹闄? {env_key}")
            return True
        return False

    @classmethod
    def toggle_key(cls, env_key: str) -> bool:
        """鍚敤/绂佺敤Key"""
        key = cls._keys.get(env_key)
        if key:
            key.active = not key.active
            key.updated_at = time.time()
            cls.save()
            return True
        return False

    @classmethod
    def get_status(cls) -> Dict:
        """鑾峰彇鎵€鏈塊ey鐘舵€?""
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

# 鍚姩鍔犺浇
try:
    KeyManager.load()
except:
    pass

key_manager = KeyManager()
