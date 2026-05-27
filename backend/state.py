"""In-memory state with JSON persistence for Agent operational data."""
import json, os
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

    def _load(self):
        try:
            if os.path.exists(STATE_FILE):
                with open(STATE_FILE, encoding="utf-8") as f:
                    saved = json.load(f)
                    self._data.update(saved)
        except Exception:
            pass

    def _save(self):
        try:
            with open(STATE_FILE, "w", encoding="utf-8") as f:
                json.dump(self._data, f, ensure_ascii=False, default=str, indent=2)
        except Exception:
            pass

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
