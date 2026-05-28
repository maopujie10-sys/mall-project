"""In-memory state with JSON persistence for Agent operational data.
v2: 原子写入 + 全key上限控制 + 敏感数据保护 + 连接池"""
import json, os, tempfile
import sqlite3
from datetime import datetime
from typing import Optional

STATE_FILE = os.path.join(os.path.dirname(__file__), "agent_state.json")

# ===== 全局 key 上限控制 =====
KEY_LIMITS = {
    "tasks": 200,
    "emergency_history": 50,
    "approval_history": 100,
    "pending_approvals": 50,
    "scraped_products": 500,
    "scraping_jobs": 100,
    "rotation_domains": 100,
    "rotation_history": 200,
    "customer_messages": 200,
    "notifications": 100,
    "alerts": 200,
    "inspection_history": 100,
    "plugin_configs": 100,
    "mall_maps": 20,
    "autopilot_logs": 200,
    "virtual_stats": 1,
    "evolution_history": 200,
    "evolution_knowledge": 500,
    "plugins": 100,
}

SENSITIVE_KEYS = ["password", "secret", "token", "key", "api_key", "auth"]

_db_conn = None


def _get_db_path():
    return os.path.join(os.path.dirname(__file__), "agent_state.db")


class _AgentState:
    def __init__(self):
        self._data = {
            "mode": "ai_control",
            "emergency_history": [],
            "pending_approvals": [],
            "approval_history": [],
            "tasks": [],
        }
        self._load()
        self._ensure_limits()

    def _ensure_limits(self):
        """强制所有key不超限（已知key按KEY_LIMITS，未知key默认上限1000）"""
        for key in list(self._data.keys()):
            val = self._data[key]
            limit = KEY_LIMITS.get(key, 1000)  # 未知key默认上限1000
            if isinstance(val, list) and len(val) > limit:
                self._data[key] = val[-limit:]
            elif isinstance(val, dict):
                keys = list(val.keys())
                if len(keys) > limit:
                    for k in keys[:-limit]:
                        del val[k]
        """强制所有key不超限（惰性裁剪，每次save前执行）"""
        for key, limit in KEY_LIMITS.items():
            val = self._data.get(key)
            if isinstance(val, list) and len(val) > limit:
                self._data[key] = val[-limit:]
            elif isinstance(val, dict):
                keys = list(val.keys())
                if len(keys) > limit:
                    for k in keys[:-limit]:
                        del val[k]

    def _mask_sensitive(self, data):
        """递归掩码敏感字段"""
        if isinstance(data, dict):
            return {k: ("***masked***" if any(s in k.lower() for s in SENSITIVE_KEYS) else self._mask_sensitive(v))
                    for k, v in data.items()}
        if isinstance(data, list):
            return [self._mask_sensitive(i) for i in data]
        return data

    def _atomic_save_json(self):
        """原子写入：写临时文件 → rename"""
        try:
            fd, tmp = tempfile.mkstemp(suffix=".json", dir=os.path.dirname(STATE_FILE))
            with os.fdopen(fd, "w", encoding="utf-8") as f:
                json.dump(self._data, f, ensure_ascii=False, default=str, indent=2)
            os.replace(tmp, STATE_FILE)
        except Exception:
            try:
                os.unlink(tmp)
            except:
                pass

    def _save_db(self):
        """SQLite持久化（复用连接+批量操作）"""
        global _db_conn
        try:
            if _db_conn is None:
                _db_conn = sqlite3.connect(_get_db_path(), check_same_thread=False)
                _db_conn.execute("""CREATE TABLE IF NOT EXISTS agent_state (
                    key TEXT PRIMARY KEY, value TEXT, updated_at TEXT)""")
            for k, v in self._data.items():
                if isinstance(v, (dict, list)):
                    v = json.dumps(v, ensure_ascii=False, default=str)
                _db_conn.execute(
                    "INSERT OR REPLACE INTO agent_state VALUES (?, ?, ?)",
                    (k, str(v), datetime.now().isoformat())
                )
            _db_conn.commit()
        except Exception:
            pass  # SQLite不可用时静默降级

    def _load(self):
        """启动时恢复状态"""
        try:
            if os.path.exists(STATE_FILE):
                with open(STATE_FILE, encoding="utf-8") as f:
                    saved = json.load(f)
                    self._data.update(saved)
        except Exception:
            pass
        # 尝试从数据库恢复JSON可能丢失的最新数据
        try:
            db_path = _get_db_path()
            if os.path.exists(db_path):
                conn = sqlite3.connect(db_path)
                rows = conn.execute("SELECT key, value FROM agent_state").fetchall()
                for k, v in rows:
                    if k not in self._data or not self._data[k]:
                        try:
                            self._data[k] = json.loads(v)
                        except:
                            self._data[k] = v
                conn.close()
        except Exception:
            pass

    def _save(self):
        """统一持久化入口：JSON原子写入 + SQLite"""
        self._ensure_limits()
        self._atomic_save_json()
        self._save_db()

    @property
    def mode(self) -> str:
        return self._data.get("mode", "ai_control")

    @mode.setter
    def mode(self, val: str):
        self._data["mode"] = val
        self._save()

    @property
    def emergency_history(self) -> list:
        return self._data.get("emergency_history", [])

    def add_emergency(self, mode: str, reason: str):
        lst = self._data.setdefault("emergency_history", [])
        lst.insert(0, {"time": datetime.now().strftime("%H:%M:%S"), "mode": mode, "reason": reason})
        if len(lst) > 50:
            lst[:] = lst[:50]
        self._save()

    @property
    def pending_approvals(self) -> list:
        return self._data.get("pending_approvals", [])

    def add_approval(self, task_id: str, risk: str, name: str, description: str = ""):
        entry = {"id": task_id, "risk": risk, "name": name, "description": description,
                 "time": datetime.now().strftime("%H:%M:%S")}
        lst = self._data.setdefault("pending_approvals", [])
        lst.append(entry)
        if len(lst) > 50:
            lst[:] = lst[-50:]
        self._save()
        return entry

    def decide_approval(self, task_id: str, approved: bool) -> Optional[dict]:
        pending = self._data.get("pending_approvals", [])
        for i, item in enumerate(pending):
            if item["id"] == task_id:
                pending.pop(i)
                item["result"] = "approved" if approved else "rejected"
                item["decided_at"] = datetime.now().strftime("%H:%M:%S")
                hist = self._data.setdefault("approval_history", [])
                hist.insert(0, item)
                if len(hist) > 100:
                    hist[:] = hist[:100]
                self._save()
                return item
        return None

    @property
    def approval_history(self) -> list:
        return self._data.get("approval_history", [])

    @property
    def tasks(self) -> list:
        return self._data.get("tasks", [])

    def add_task(self, name: str, risk: str = "L1", status: str = "完成"):
        entry = {"id": f"task_{len(self._data.get('tasks',[]))+1}_{int(datetime.now().timestamp())}",
                 "name": name, "risk": risk, "status": status,
                 "time": datetime.now().strftime("%H:%M:%S")}
        lst = self._data.setdefault("tasks", [])
        lst.insert(0, entry)
        if len(lst) > 200:
            lst[:] = lst[:200]
        self._save()
        return entry

    def set_data(self, key: str, value, max_size: int = None):
        """安全设置_data中的key，带上限控制"""
        self._data[key] = value
        if max_size and isinstance(value, list) and len(value) > max_size:
            self._data[key] = value[-max_size:]
        elif max_size and isinstance(value, dict):
            keys = list(value.keys())
            if len(keys) > max_size:
                for k in keys[:-max_size]:
                    del value[k]
        self._save()

    def append_data(self, key: str, item, max_size: int = None):
        """安全追加到列表型key，超过上限自动裁剪"""
        lst = self._data.setdefault(key, [])
        lst.append(item)
        limit = max_size or KEY_LIMITS.get(key)
        if limit and len(lst) > limit:
            self._data[key] = lst[-limit:]
        self._save()

    def get_data(self, key: str, default=None):
        return self._data.get(key, default)


state = _AgentState()

