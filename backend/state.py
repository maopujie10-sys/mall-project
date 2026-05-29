閿?""In-memory state with JSON persistence for Agent operational data.
v2: 閸樼喎鐡欓崘娆忓弳 + 閸忊暓ey娑撳﹪妾洪幒褍鍩?+ 閺佸繑鍔呴弫鐗堝祦娣囨繃濮?+ 鏉╃偞甯村Ч?""
import json, os, tempfile
import sqlite3
from datetime import datetime
from typing import Optional

_BASE = os.getenv("APP_STATE_DIR", os.path.dirname(os.path.abspath(__file__)))
STATE_FILE = os.path.join(_BASE, "agent_state.json")

# ===== 閸忋劌鐪?key 娑撳﹪妾洪幒褍鍩?=====
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
    return os.path.join(_BASE, "agent_state.db")


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
        """瀵搫鍩楅幍鈧張濉砮y娑撳秷绉撮梽鎰剁礄瀹歌尙鐓ey閹稿EY_LIMITS閿涘本婀惌顧眅y姒涙顓绘稉濠囨1000閿?""
        for key in list(self._data.keys()):
            val = self._data[key]
            limit = KEY_LIMITS.get(key, 1000)
            if isinstance(val, list) and len(val) > limit:
                self._data[key] = val[-limit:]
            elif isinstance(val, dict):
                keys = list(val.keys())
                if len(keys) > limit:
                    for k in keys[:-limit]:
                        del val[k]

    def _mask_sensitive(self, data):
        """闁帒缍婇幒鈺冪垳閺佸繑鍔呯€涙顔?""
        if isinstance(data, dict):
            return {k: ("***masked***" if any(s in k.lower() for s in SENSITIVE_KEYS) else self._mask_sensitive(v))
                    for k, v in data.items()}
        if isinstance(data, list):
            return [self._mask_sensitive(i) for i in data]
        return data

    def _atomic_save_json(self):
        """閸樼喎鐡欓崘娆忓弳閿涙艾鍟撴稉瀛樻閺傚洣娆?閳?rename"""
        try:
            fd, tmp = tempfile.mkstemp(suffix=".json", dir=os.path.dirname(STATE_FILE))
            with os.fdopen(fd, "w", encoding="utf-8") as f:
                json.dump(self._data, f, ensure_ascii=False, default=str, indent=2)
            os.replace(tmp, STATE_FILE)
        except Exception:
            try:
                os.unlink(tmp)
            except Exception:
                pass

    def _save_db(self):
        """SQLite閹镐椒绠欓崠鏍电礄婢跺秶鏁ゆ潻鐐村复+閹靛綊鍣洪幙宥勭稊閿?""
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
            pass  # SQLite娑撳秴褰查悽銊︽闂堟瑩绮梽宥囬獓

    def _load(self):
        """閸氼垰濮╅弮鑸典划婢跺秶濮搁幀?""
        try:
            if os.path.exists(STATE_FILE):
                with open(STATE_FILE, encoding="utf-8") as f:
                    saved = json.load(f)
                    self._data.update(saved)
        except Exception:
            pass
        # 鐏忔繆鐦禒搴㈡殶閹诡喖绨遍幁銏狀槻JSON閸欘垵鍏樻稉銏犮亼閻ㄥ嫭娓堕弬鐗堟殶閹?
        try:
            db_path = _get_db_path()
            if os.path.exists(db_path):
                conn = sqlite3.connect(db_path)
                rows = conn.execute("SELECT key, value FROM agent_state").fetchall()
                for k, v in rows:
                    if k not in self._data or not self._data[k]:
                        try:
                            self._data[k] = json.loads(v)
                        except Exception:
                            self._data[k] = v
                conn.close()
        except Exception:
            pass

    def _save(self):
        """缂佺喍绔撮幐浣风畽閸栨牕鍙嗛崣锝忕窗JSON閸樼喎鐡欓崘娆忓弳 + SQLite"""
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

    def add_task(self, name: str, risk: str = "L1", status: str = "鐎瑰本鍨?):
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
        """鐎瑰鍙忕拋鍓х枂_data娑擃厾娈慿ey閿涘苯鐢稉濠囨閹貉冨煑"""
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
        """鐎瑰鍙忔潻钘夊閸掓澘鍨悰銊ョ€穔ey閿涘矁绉存潻鍥︾瑐闂勬劘鍤滈崝銊梿閸?""
        lst = self._data.setdefault(key, [])
        lst.append(item)
        limit = max_size or KEY_LIMITS.get(key)
        if limit and len(lst) > limit:
            self._data[key] = lst[-limit:]
        self._save()

    def get_data(self, key: str, default=None):
        return self._data.get(key, default)


state = _AgentState()




