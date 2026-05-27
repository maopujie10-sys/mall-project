"""Redis 任务队列 — 替代内存队列的持久化任务系统

当 Redis 可用时使用 Redis 队列，否则回退到内存队列。
"""
import json
import os


class RedisQueue:
    """Redis 任务队列"""

    _redis = None

    @classmethod
    def _get_redis(cls):
        if cls._redis is not None:
            return cls._redis
        try:
            import redis as _r
            dsn = os.getenv("REDIS_DSN", "redis://localhost:6379/0")
            cls._redis = _r.from_url(dsn, decode_responses=True)
            cls._redis.ping()
            return cls._redis
        except Exception:
            cls._redis = False
            return None

    @classmethod
    def enqueue(cls, queue_name: str, task: dict) -> str:
        """加入任务队列"""
        import uuid
        task_id = str(uuid.uuid4())[:8]
        task["id"] = task_id
        r = cls._get_redis()
        if r:
            r.lpush(queue_name, json.dumps(task, ensure_ascii=False, default=str))
            return task_id
        # Fallback: 内存队列
        from state import state
        key = f"redis_queue_{queue_name}"
        q = state._data.setdefault(key, [])
        q.insert(0, task)
        state._save()
        return task_id

    @classmethod
    def dequeue(cls, queue_name: str) -> dict:
        """取出任务"""
        r = cls._get_redis()
        if r:
            data = r.rpop(queue_name)
            return json.loads(data) if data else None
        from state import state
        key = f"redis_queue_{queue_name}"
        q = state._data.get(key, [])
        return q.pop() if q else None

    @classmethod
    def length(cls, queue_name: str) -> int:
        """队列长度"""
        r = cls._get_redis()
        if r:
            return r.llen(queue_name)
        from state import state
        return len(state._data.get(f"redis_queue_{queue_name}", []))
