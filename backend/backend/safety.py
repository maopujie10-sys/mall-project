''" +  -- AI''"
from datetime import datetime, timedelta
from collections import defaultdict
from state import state


class CircuitBreaker:
    ''"
    .
    -  N ,
    - ,
    ''"

    STATE_CLOSED = "closed"       
    STATE_OPEN = "open"           
    STATE_HALF_OPEN = "half_open"  # ()

    def __init__(self, threshold: int = 2, cooldown_s: int = 300):
        self.threshold = threshold          
        self.cooldown_s = cooldown_s        # ()
        self._failures: dict[str, list[datetime]] = defaultdict(list)
        self._states: dict[str, str] = {}

    def record_failure(self, action: str):
        ''''''
        now = datetime.now()
        self._failures[action].append(now)
        #  threshold 
        if len(self._failures[action]) > self.threshold:
            self._failures[action] = self._failures[action][-self.threshold:]

        
        recent = [t for t in self._failures[action] if now - t < timedelta(seconds=300)]
        if len(recent) >= self.threshold:
            self._states[action] = self.STATE_OPEN
            state.mode = "readonly"  
            state.add_emergency("readonly", f": {action} {self.threshold}")
            return True
        return False

    def record_success(self, action: str):
        ''''''
        self._failures[action].clear()
        if self._states.get(action) == self.STATE_HALF_OPEN:
            self._states[action] = self.STATE_CLOSED

    def can_execute(self, action: str) -> bool:
        ''''''
        s = self._states.get(action, self.STATE_CLOSED)
        if s == self.STATE_CLOSED:
            return True
        if s == self.STATE_OPEN:
            
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


# =====  =====
class AntiLoop:
    ''"
     -- AI.
    :
    -  10  1 
    -  2 
    - 
    - 
    ''"

    def __init__(self):
        self._records: dict[str, list[datetime]] = defaultdict(list)

    def _clean(self, key: str, window_min: int = 10):
        ''''''
        now = datetime.now()
        self._records[key] = [
            t for t in self._records[key]
            if now - t < timedelta(minutes=window_min)
        ]

    def check(self, action_key: str, max_count: int = 1, window_min: int = 10) -> bool:
        ''"
        .
         True=, False=
        ''"
        self._clean(action_key, window_min)
        return len(self._records[action_key]) < max_count

    def record(self, action_key: str):
        ''''''
        self._records[action_key].append(datetime.now())

    def reset(self, action_key: str):
        ''''''
        self._records[action_key].clear()



circuit_breaker = CircuitBreaker()
anti_loop = AntiLoop()
