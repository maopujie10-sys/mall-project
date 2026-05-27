"""任务队列 + 任务锁 — 排队/优先级/暂停/取消/超时/并发锁"""
from datetime import datetime, timedelta
from typing import Optional
from state import state

# ===== 任务状态 =====
TASK_PENDING = "pending"
TASK_RUNNING = "running"
TASK_PAUSED = "paused"
TASK_CANCELLED = "cancelled"
TASK_TIMEOUT = "timeout"
TASK_DONE = "done"
TASK_FAILED = "failed"


class TaskQueue:
    """内存任务队列，支持优先级/暂停/取消/超时"""

    def __init__(self):
        self._tasks: list[dict] = []
        self._counter = 0

    def enqueue(self, name: str, risk: str = "L1", priority: int = 5, timeout_s: int = 60) -> str:
        """添加任务到队列，priority 越小优先级越高"""
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
        """取出下一个待执行任务"""
        for t in self._tasks:
            if t["status"] == TASK_PENDING:
                # 检查超时
                created = datetime.fromisoformat(t["created_at"])
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


# ===== 任务锁 =====
class TaskLock:
    """任务锁，防止并发冲突"""

    def __init__(self):
        self._locks: dict[str, str] = {}  # lock_name -> task_id

    def acquire(self, lock_name: str, task_id: str) -> bool:
        """获取锁，成功返回 True"""
        if lock_name not in self._locks:
            self._locks[lock_name] = task_id
            return True
        return False

    def release(self, lock_name: str, task_id: str) -> bool:
        """释放锁，只有持有者才能释放"""
        if self._locks.get(lock_name) == task_id:
            del self._locks[lock_name]
            return True
        return False

    def is_locked(self, lock_name: str) -> bool:
        return lock_name in self._locks

    def force_release(self, lock_name: str):
        """强制释放锁（管理员操作）"""
        self._locks.pop(lock_name, None)

    def list_locks(self) -> dict:
        return dict(self._locks)

    def status(self) -> dict:
        return {
            "locks": self._locks,
            "count": len(self._locks),
        }


# 全局单例
task_queue = TaskQueue()
task_lock = TaskLock()

# 注册默认锁
LOCK_BACKUP = "backup"       # 备份锁
LOCK_DEPLOY = "deploy"       # 部署锁
LOCK_RESTART = "restart"     # 重启锁
LOCK_ROLLBACK = "rollback"   # 回滚锁
