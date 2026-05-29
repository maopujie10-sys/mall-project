"""熔断机制 + 防循环 -- 防止AI无限重试和雪崩"""
from datetime import datetime, timedelta
from collections import defaultdict
from state import state


class CircuitBreaker:
    """
    熔断器.
    - 同一操作连续失败 N 次后熔断,切换到只读模式
    - 熔断后冷却一段时间自动半开,重试成功则恢复
    """

    STATE_CLOSED = "closed"       # 正常
    STATE_OPEN = "open"           # 熔断
    STATE_HALF_OPEN = "half_open"  # 半开(尝试恢复)

    def __init__(self, threshold: int = 2, cooldown_s: int = 300):
        self.threshold = threshold          # 连续失败次数阈值
        self.cooldown_s = cooldown_s        # 熔断冷却时间(秒)
        self._failures: dict[str, list[datetime]] = defaultdict(list)
        self._states: dict[str, str] = {}

    def record_failure(self, action: str):
        """记录一次失败"""
        now = datetime.now()
        self._failures[action].append(now)
        # 只保留最近 threshold 次
        if len(self._failures[action]) > self.threshold:
            self._failures[action] = self._failures[action][-self.threshold:]

        # 判断是否触发熔断
        recent = [t for t in self._failures[action] if now - t < timedelta(seconds=300)]
        if len(recent) >= self.threshold:
            self._states[action] = self.STATE_OPEN
            state.mode = "readonly"  # 自动切换只读模式
            state.add_emergency("readonly", f"熔断触发: {action} 连续失败{self.threshold}次")
            return True
        return False

    def record_success(self, action: str):
        """记录一次成功"""
        self._failures[action].clear()
        if self._states.get(action) == self.STATE_HALF_OPEN:
            self._states[action] = self.STATE_CLOSED

    def can_execute(self, action: str) -> bool:
        """检查是否允许执行"""
        s = self._states.get(action, self.STATE_CLOSED)
        if s == self.STATE_CLOSED:
            return True
        if s == self.STATE_OPEN:
            # 检查冷却是否结束
            last_fail = self._failures[action][-1] if self._failures[action] else None
            if last_fail and datetime.now() - last_fail > timedelta(seconds=self.cooldown_s):
                self._states[action] = self.STATE_HALF_OPEN
                return True
            return False
        if s == self.STATE_HALF_OPEN:
            return True
        return True

    def get_state(self, action: str) -> str:
        return self._states.get(action, self.STATE_CLOSED)

    def status(self) -> dict:
        return {
            action: {
                "state": self._states.get(action, self.STATE_CLOSED),
                "recent_failures": len(self._failures.get(action, [])),
            }
            for action in set(list(self._states.keys()) + list(self._failures.keys()))
        }


# ===== 防循环机制 =====
class AntiLoop:
    """
    防循环 -- 防止AI反复执行同一操作.
    规则:
    - 同一容器 10 分钟内最多重启 1 次
    - 同一故障最多自动修复 2 次
    - 同一域名不得反复暂停恢复
    - 同一告警不得无限发送
    """

    def __init__(self):
        self._records: dict[str, list[datetime]] = defaultdict(list)

    def _clean(self, key: str, window_min: int = 10):
        """清理窗口外的记录"""
        now = datetime.now()
        self._records[key] = [
            t for t in self._records[key]
            if now - t < timedelta(minutes=window_min)
        ]

    def check(self, action_key: str, max_count: int = 1, window_min: int = 10) -> bool:
        """
        检查是否允许执行.
        返回 True=允许, False=被限制
        """
        self._clean(action_key, window_min)
        return len(self._records[action_key]) < max_count

    def record(self, action_key: str):
        """记录一次操作"""
        self._records[action_key].append(datetime.now())

    def reset(self, action_key: str):
        """重置某个操作的计数"""
        self._records[action_key].clear()


# 全局单例
circuit_breaker = CircuitBreaker()
anti_loop = AntiLoop()
