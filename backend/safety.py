閿?""閻旀梹鏌囬張鍝勫煑 + 闂冩彃鎯婇悳?閳?闂冨弶顒汚I閺冪娀妾洪柌宥堢槸閸滃矂娲╁畷?""
from datetime import datetime, timedelta
from collections import defaultdict
from state import state


class CircuitBreaker:
    """
    閻旀梹鏌囬崳銊ｂ偓?    - 閸氬奔绔撮幙宥勭稊鏉╃偟鐢绘径杈Е N 濞嗏€虫倵閻旀梹鏌囬敍灞藉瀼閹广垹鍩岄崣顏囶嚢濡€崇础
    - 閻旀梹鏌囬崥搴″枎閸楃繝绔村▓鍨闂傜鍤滈崝銊ュ磹瀵偓閿涘矂鍣哥拠鏇熷灇閸旂喎鍨幁銏狀槻
    """

    STATE_CLOSED = "closed"       # 濮濓絽鐖?    STATE_OPEN = "open"           # 閻旀梹鏌?    STATE_HALF_OPEN = "half_open"  # 閸楀﹤绱戦敍鍫濈毦鐠囨洘浠径宥忕礆

    def __init__(self, threshold: int = 2, cooldown_s: int = 300):
        self.threshold = threshold          # 鏉╃偟鐢绘径杈Е濞嗏剝鏆熼梼鍫濃偓?        self.cooldown_s = cooldown_s        # 閻旀梹鏌囬崘宄板祱閺冨爼妫块敍鍫㈩潡閿?        self._failures: dict[str, list[datetime]] = defaultdict(list)
        self._states: dict[str, str] = {}

    def record_failure(self, action: str):
        """鐠佹澘缍嶆稉鈧▎鈥炽亼鐠?""
        now = datetime.now()
        self._failures[action].append(now)
        # 閸欘亙绻氶悾娆愭付鏉?threshold 濞?        if len(self._failures[action]) > self.threshold:
            self._failures[action] = self._failures[action][-self.threshold:]

        # 閸掋倖鏌囬弰顖氭儊鐟欙箑褰傞悢鏃€鏌?        recent = [t for t in self._failures[action] if now - t < timedelta(seconds=300)]
        if len(recent) >= self.threshold:
            self._states[action] = self.STATE_OPEN
            state.mode = "readonly"  # 閼奉亜濮╅崚鍥ㄥ床閸欘亣顕板Ο鈥崇础
            state.add_emergency("readonly", f"閻旀梹鏌囩憴锕€褰? {action} 鏉╃偟鐢绘径杈Е{self.threshold}濞?)
            return True
        return False

    def record_success(self, action: str):
        """鐠佹澘缍嶆稉鈧▎鈩冨灇閸?""
        self._failures[action].clear()
        if self._states.get(action) == self.STATE_HALF_OPEN:
            self._states[action] = self.STATE_CLOSED

    def can_execute(self, action: str) -> bool:
        """濡偓閺屻儲妲搁崥锕€鍘戠拋鍛婂⒔鐞?""
        s = self._states.get(action, self.STATE_CLOSED)
        if s == self.STATE_CLOSED:
            return True
        if s == self.STATE_OPEN:
            # 濡偓閺屻儱鍠庨崡瀛樻Ц閸氾妇绮ㄩ弶?            last_fail = self._failures[action][-1] if self._failures[action] else None
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


# ===== 闂冩彃鎯婇悳顖涙簚閸?=====
class AntiLoop:
    """
    闂冩彃鎯婇悳?閳?闂冨弶顒汚I閸欏秴顦查幍褑顢戦崥灞肩閹垮秳缍旈妴?    鐟欏嫬鍨敍?    - 閸氬奔绔寸€圭懓娅?10 閸掑棝鎸撻崘鍛付婢舵岸鍣搁崥?1 濞?    - 閸氬奔绔撮弫鍛存閺堚偓婢舵俺鍤滈崝銊ゆ叏婢?2 濞?    - 閸氬奔绔撮崺鐔锋倳娑撳秴绶遍崣宥咁槻閺嗗倸浠犻幁銏狀槻
    - 閸氬奔绔撮崨濠咁劅娑撳秴绶遍弮鐘绘閸欐垿鈧?    """

    def __init__(self):
        self._records: dict[str, list[datetime]] = defaultdict(list)

    def _clean(self, key: str, window_min: int = 10):
        """濞撳懐鎮婄粣妤€褰涙径鏍畱鐠佹澘缍?""
        now = datetime.now()
        self._records[key] = [
            t for t in self._records[key]
            if now - t < timedelta(minutes=window_min)
        ]

    def check(self, action_key: str, max_count: int = 1, window_min: int = 10) -> bool:
        """
        濡偓閺屻儲妲搁崥锕€鍘戠拋鍛婂⒔鐞涘被鈧?        鏉╂柨娲?True=閸忎浇顔? False=鐞氼偊妾洪崚?        """
        self._clean(action_key, window_min)
        return len(self._records[action_key]) < max_count

    def record(self, action_key: str):
        """鐠佹澘缍嶆稉鈧▎鈩冩惙娴?""
        self._records[action_key].append(datetime.now())

    def reset(self, action_key: str):
        """闁插秶鐤嗛弻鎰嚋閹垮秳缍旈惃鍕吀閺?""
        self._records[action_key].clear()


# 閸忋劌鐪崡鏇氱伐
circuit_breaker = CircuitBreaker()
anti_loop = AntiLoop()
