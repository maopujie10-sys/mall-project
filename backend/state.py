"""In-memory state with JSON persistence for Agent operational data."""
import json, os
import sqlite3  # fallback when MySQL unavailable
from datetime import datetime
from typing import Optional

STATE_FILE = os.path.join(os.path.dirname(__file__), "agent_state.json")

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


    def _save_db(self):
        """持久化到 MySQL（如果可用），否则用 SQLite"""
        try:
            from config import DB_CONFIG
            import pymysql
            conn = pymysql.connect(
                host=DB_CONFIG["host"], port=DB_CONFIG["port"],
                user=DB_CONFIG["user"], password=DB_CONFIG["password"],
                database=DB_CONFIG["name"], charset="utf8mb4",
                connect_timeout=3
            )
            cur = conn.cursor()
            # 写入 agent_tasks
            for t in self._data.get("tasks", [])[-50:]:
                cur.execute(
                    """INSERT INTO agent_tasks (task_id, user_message, intent, mode, risk_level, status)
                       VALUES (%s, %s, %s, %s, %s, %s)
                       ON DUPLICATE KEY UPDATE status=VALUES(status)""",
                    (t.get("id",""), t.get("name",""), t.get("name",""),
                     self._data.get("mode","ai_control"), t.get("risk","L1"), t.get("status","完成"))
                )
            # 写入 agent_confirmations
            for a in self._data.get("pending_approvals", []):
                cur.execute(
                    """INSERT INTO agent_confirmations (task_id, action_name, risk_level, status)
                       VALUES (%s, %s, %s, 'pending')
                       ON DUPLICATE KEY UPDATE status='pending'""",
                    (a.get("id",""), a.get("name",""), a.get("risk","L3"))
                )
            conn.commit()
            cur.close()
            conn.close()
            return True
        except Exception:
            pass
        # Fallback: SQLite
        try:
            db_path = os.path.join(os.path.dirname(__file__), "agent_state.db")
            conn = sqlite3.connect(db_path)
            conn.execute("""CREATE TABLE IF NOT EXISTS agent_state (
                key TEXT PRIMARY KEY, value TEXT, updated_at TEXT)""")
            for k, v in self._data.items():
                if isinstance(v, (dict, list)):
                    v = json.dumps(v, ensure_ascii=False, default=str)
                conn.execute(
                    "INSERT OR REPLACE INTO agent_state VALUES (?, ?, ?)",
                    (k, str(v), datetime.now().isoformat())
                )
            conn.commit()
            conn.close()
            return True
        except Exception:
            return False

    def _load(self):
        try:
            if os.path.exists(STATE_FILE):
                with open(STATE_FILE, encoding="utf-8") as f:
                    saved = json.load(f)
                    self._data.update(saved)
            # 尝试从数据库恢复
            self._load_db()
        except Exception:
            pass

    def _save(self):
        try:
            with open(STATE_FILE, "w", encoding="utf-8") as f:
                json.dump(self._data, f, ensure_ascii=False, default=str, indent=2)
        except Exception:
            pass
        # 并行持久化到数据库
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
        self._data.setdefault("emergency_history", []).insert(0, {
            "time": datetime.now().strftime("%H:%M:%S"),
            "mode": mode,
            "reason": reason,
        })
        if len(self._data["emergency_history"]) > 50:
            self._data["emergency_history"] = self._data["emergency_history"][:50]
        self._save()

    @property
    def pending_approvals(self) -> list:
        return self._data.get("pending_approvals", [])

    def add_approval(self, task_id: str, risk: str, name: str, description: str = ""):
        entry = {
            "id": task_id, "risk": risk, "name": name,
            "description": description,
            "time": datetime.now().strftime("%H:%M:%S"),
        }
        self._data.setdefault("pending_approvals", []).append(entry)
        self._save()
        return entry

    def decide_approval(self, task_id: str, approved: bool) -> Optional[dict]:
        pending = self._data.get("pending_approvals", [])
        for i, item in enumerate(pending):
            if item["id"] == task_id:
                pending.pop(i)
                item["result"] = "approved" if approved else "rejected"
                item["decided_at"] = datetime.now().strftime("%H:%M:%S")
                self._data.setdefault("approval_history", []).insert(0, item)
                if len(self._data["approval_history"]) > 100:
                    self._data["approval_history"] = self._data["approval_history"][:100]
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
        entry = {
            "id": f"task_{len(self._data.get('tasks',[]))+1}_{int(datetime.now().timestamp())}",
            "name": name, "risk": risk, "status": status,
            "time": datetime.now().strftime("%H:%M:%S"),
        }
        self._data.setdefault("tasks", []).insert(0, entry)
        if len(self._data["tasks"]) > 200:
            self._data["tasks"] = self._data["tasks"][:200]
        self._save()
        return entry

state = _AgentState()
