閿?""娴犺濮熼梼鐔峰灙 + 娴犺濮熼柨?閳?閹烘帡妲?娴兼ê鍘涚痪?閺嗗倸浠?閸欐牗绉?鐡掑懏妞?楠炶泛褰傞柨?""
from datetime import datetime, timedelta
from typing import Optional
from state import state

# ===== 娴犺濮熼悩鑸碘偓?=====
TASK_PENDING = "pending"
TASK_RUNNING = "running"
TASK_PAUSED = "paused"
TASK_CANCELLED = "cancelled"
TASK_TIMEOUT = "timeout"
TASK_DONE = "done"
TASK_FAILED = "failed"


class TaskQueue:
    """閸愬懎鐡ㄦ禒璇插闂冪喎鍨敍灞炬暜閹镐椒绱崗鍫㈤獓/閺嗗倸浠?閸欐牗绉?鐡掑懏妞?""

    def __init__(self):
        self._tasks: list[dict] = []
        self._counter = 0

    def enqueue(self, name: str, risk: str = "L1", priority: int = 5, timeout_s: int = 60) -> str:
        """濞ｈ濮炴禒璇插閸掍即妲﹂崚妤嬬礉priority 鐡掑﹤鐨导妯哄帥缁狙嗙Ш妤?""
        self._counter += 1
        task = {
            "id": f"q_{self._counter}_{int(datetime.now().timestamp())}",
            "name": name,
            "risk": risk,
            "priority": priority,
            "status": TASK_PENDING,
            "timeout_s": timeout_s,
            "created_at": datetime.now().isoformat(),
            "started_at": None,
            "finished_at": None,
            "result": None,
            "error": None,
        }
        self._tasks.append(task)
        self._tasks.sort(key=lambda t: (t["priority"], t["created_at"]))
        return task["id"]

    def dequeue(self) -> Optional[dict]:
        """閸欐牕鍤稉瀣╃娑擃亜绶熼幍褑顢戞禒璇插"""
        for t in self._tasks:
            if t["status"] == TASK_PENDING:
                # 濡偓閺屻儴绉撮弮?                created = datetime.fromisoformat(t["created_at"])
                if datetime.now() - created > timedelta(seconds=t["timeout_s"]):
                    t["status"] = TASK_TIMEOUT
                    continue
                t["status"] = TASK_RUNNING
                t["started_at"] = datetime.now().isoformat()
                return t
        return None

    def get(self, task_id: str) -> Optional[dict]:
        for t in self._tasks:
            if t["id"] == task_id:
                return t
        return None

    def pause(self, task_id: str) -> bool:
        t = self.get(task_id)
        if t and t["status"] == TASK_PENDING:
            t["status"] = TASK_PAUSED
            return True
        return False

    def cancel(self, task_id: str) -> bool:
        t = self.get(task_id)
        if t and t["status"] in (TASK_PENDING, TASK_PAUSED):
            t["status"] = TASK_CANCELLED
            return True
        return False

    def finish(self, task_id: str, success: bool, result: str = ""):
        t = self.get(task_id)
        if t:
            t["status"] = TASK_DONE if success else TASK_FAILED
            t["finished_at"] = datetime.now().isoformat()
            t["result"] = result

    def list(self, status: str = None) -> list[dict]:
        if status:
            return [t for t in self._tasks if t["status"] == status]
        return self._tasks[-50:]

    def pending_count(self) -> int:
        return sum(1 for t in self._tasks if t["status"] == TASK_PENDING)


# ===== 娴犺濮熼柨?=====
class TaskLock:
    """娴犺濮熼柨渚婄礉闂冨弶顒涢獮璺哄絺閸愯尙鐛?""

    def __init__(self):
        self._locks: dict[str, str] = {}  # lock_name -> task_id

    def acquire(self, lock_name: str, task_id: str) -> bool:
        """閼惧嘲褰囬柨渚婄礉閹存劕濮涙潻鏂挎礀 True"""
        if lock_name not in self._locks:
            self._locks[lock_name] = task_id
            return True
        return False

    def release(self, lock_name: str, task_id: str) -> bool:
        """闁插﹥鏂侀柨渚婄礉閸欘亝婀侀幐浣规箒閼板懏澧犻懗浠嬪櫞閺€?""
        if self._locks.get(lock_name) == task_id:
            del self._locks[lock_name]
            return True
        return False

    def is_locked(self, lock_name: str) -> bool:
        return lock_name in self._locks

    def force_release(self, lock_name: str):
        """瀵搫鍩楅柌濠冩杹闁夸緤绱欑粻锛勬倞閸涙ɑ鎼锋担婊愮礆"""
        self._locks.pop(lock_name, None)

    def list_locks(self) -> dict:
        return dict(self._locks)

    def status(self) -> dict:
        return {
            "locks": self._locks,
            "count": len(self._locks),
        }


# 閸忋劌鐪崡鏇氱伐
task_queue = TaskQueue()
task_lock = TaskLock()

# 濞夈劌鍞芥妯款吇闁?LOCK_BACKUP = "backup"       # 婢跺洣鍞ら柨?LOCK_DEPLOY = "deploy"       # 闁劎璁查柨?LOCK_RESTART = "restart"     # 闁插秴鎯庨柨?LOCK_ROLLBACK = "rollback"   # 閸ョ偞绮撮柨?
