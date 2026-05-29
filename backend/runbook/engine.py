锘?""鑷姪杩愮淮 Runbook 鈥?鑷姩鍖栨晠闅滃鐞嗘祦绋嬪紩鎿?""
import httpx
from datetime import datetime
from typing import Optional
from state import state
from risk import handle_risk
from config import MALL_BASE_URL

class StepResult:
    """鍗曟鎵ц缁撴灉"""
    def __init__(self, name: str, ok: bool, detail: str = "", evidence: str = ""):
        self.name = name
        self.ok = ok
        self.detail = detail
        self.evidence = evidence
        self.time = datetime.now().strftime("%H:%M:%S")

    def to_dict(self):
        return {"name": self.name, "ok": self.ok, "detail": self.detail, "evidence": self.evidence, "time": self.time}


class Runbook:
    """Runbook 鍩虹被"""

    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
        self.steps: list[StepResult] = []
        self._failed = False

    async def run(self) -> dict:
        """鎵ц runbook锛岃繑鍥炲畬鏁存姤鍛?""
        raise NotImplementedError

    def _add_step(self, name: str, ok: bool, detail: str = "", evidence: str = ""):
        self.steps.append(StepResult(name, ok, detail, evidence))
        if not ok:
            self._failed = True

    def _report(self) -> dict:
        return {
            "runbook": self.name,
            "description": self.description,
            "time": datetime.now().strftime("%H:%M:%S"),
            "total_steps": len(self.steps),
            "passed": sum(1 for s in self.steps if s.ok),
            "failed": sum(1 for s in self.steps if not s.ok),
            "all_passed": not self._failed,
            "steps": [s.to_dict() for s in self.steps],
            "summary": self._generate_summary(),
        }

    def _generate_summary(self) -> str:
        passed = sum(1 for s in self.steps if s.ok)
        total = len(self.steps)
        if self._failed:
            failed_steps = [s.name for s in self.steps if not s.ok]
            return f"瀹屾垚 {passed}/{total} 姝ャ€傗潓 寮傚父: {', '.join(failed_steps)}銆傚缓璁汉宸ヤ粙鍏ャ€?
        return f"鍏ㄩ儴 {total} 姝ラ€氳繃 鉁咃紝绯荤粺杩愯姝ｅ父銆?


# ===== 鍏蜂綋 Runbook =====

class MallDownRunbook(Runbook):
    """鍟嗗煄鎵撲笉寮€ 鈥?绔埌绔瘖鏂?""

    def __init__(self):
        super().__init__("鍟嗗煄鎵撲笉寮€璇婃柇", "妫€鏌NS鈫掓湇鍔″櫒鈫掔鍙ｂ啋Nginx鈫扗ocker鈫掓棩蹇椻啋鏁版嵁搴撯啋璇婃柇鎶ュ憡")

    async def run(self) -> dict:
        async with httpx.AsyncClient(timeout=10, follow_redirects=True) as c:
            # 1. 妫€鏌ュ煙鍚嶈В鏋?            try:
                r = await c.get(f"https://dns.google/resolve?name={MALL_BASE_URL.replace('http://','').replace('https://','').split(':')[0]}&type=A")
                data = r.json()
                ips = [a.get("data") for a in data.get("Answer", [])] if data.get("Status") == 0 else []
                self._add_step("DNS瑙ｆ瀽", len(ips) > 0, f"瑙ｆ瀽鍒?{len(ips)} 涓狪P: {', '.join(ips[:3])}", str(ips[:3]))
            except Exception as e:
                self._add_step("DNS瑙ｆ瀽", False, f"DNS鏌ヨ澶辫触: {str(e)}")

            # 2. 妫€娴嬫湇鍔″櫒杩為€氭€?            for port, name in [(80, "HTTP"), (443, "HTTPS"), (9000, "Agent")]:
                try:
                    r = await c.get(f"{MALL_BASE_URL if port != 9000 else 'http://localhost:9000'}/agent/health", timeout=5)
                    self._add_step(f"{name}绔彛", r.status_code == 200, f"鐘舵€佺爜 {r.status_code}")
                except Exception as e:
                    self._add_step(f"{name}绔彛", False, f"杩炴帴澶辫触: {str(e)[:50]}")

            # 3. 妫€鏌ュ晢鍩庡叧閿〉闈?            for path, name in [("/", "棣栭〉"), ("/api/products", "鍟嗗搧鎺ュ彛"), ("/api/categories", "鍒嗙被鎺ュ彛")]:
                try:
                    r = await c.get(f"{MALL_BASE_URL}{path}", timeout=5)
                    self._add_step(f"鍟嗗煄{name}", r.status_code < 500, f"鐘舵€佺爜 {r.status_code}")
                except Exception as e:
                    self._add_step(f"鍟嗗煄{name}", False, str(e)[:50])

        return self._report()


class ServerHealthRunbook(Runbook):
    """鏈嶅姟鍣ㄥ仴搴锋鏌?""

    def __init__(self):
        super().__init__("鏈嶅姟鍣ㄥ仴搴锋鏌?, "妫€鏌PU/鍐呭瓨/纾佺洏/璐熻浇/杩涚▼/绔彛")

    async def run(self) -> dict:
        from executor import execute

        checks = [
            ("CPU璐熻浇", "uptime", lambda r: "load average" in r["stdout"]),
            ("鍐呭瓨浣跨敤", "free -h", lambda r: "Mem" in r["stdout"]),
            ("纾佺洏绌洪棿", "df -h /", lambda r: r["success"]),
            ("SWAP浣跨敤", "free -h | grep Swap", lambda r: True),
            ("绯荤粺杩愯鏃堕棿", "uptime -p", lambda r: r["success"]),
            ("鐧诲綍璁板綍", "last -5", lambda r: r["success"]),
        ]

        for name, cmd, check in checks:
            result = await execute(cmd)
            self._add_step(name, check(result), result["stdout"][:200] or result["stderr"][:100])

        # CPU 杩囪浇鍛婅
        import psutil
        cpu = psutil.cpu_percent(interval=0.5)
        mem = psutil.virtual_memory()
        disk = psutil.disk_usage("/")
        self._add_step("CPU浣跨敤鐜?, cpu < 80, f"CPU {cpu}%")
        self._add_step("鍐呭瓨浣跨敤鐜?, mem.percent < 80, f"鍐呭瓨 {mem.percent}%")
        self._add_step("纾佺洏浣跨敤鐜?, disk.percent < 85, f"纾佺洏 {disk.percent}%")

        return self._report()


class DiskFullRunbook(Runbook):
    """纾佺洏蹇弧 鈥?鍒嗘瀽澶ф枃浠?娓呯悊鏃ュ織/鍘嬬缉"""

    def __init__(self):
        super().__init__("纾佺洏娓呯悊", "鍒嗘瀽纾佺洏浣跨敤鈫掑畾浣嶅ぇ鏂囦欢鈫掓竻鐞嗘棩蹇椻啋鍘嬬缉澶囦唤")

    async def run(self) -> dict:
        from executor import execute
        import shutil, psutil

        # 1. 纾佺洏鐜扮姸
        disk = psutil.disk_usage("/")
        self._add_step("纾佺洏浣跨敤鐜?, disk.percent < 90, f"宸茬敤 {disk.percent}% ({disk.used/1024**3:.1f}GB/{disk.total/1024**3:.1f}GB)")

        # 2. 鎵惧ぇ鐩綍
        result = await execute("du -sh /var/log /tmp /opt 2>/dev/null | sort -rh | head -5")
        self._add_step("澶х洰褰曞垎鏋?, result["success"], result["stdout"][:300])

        # 3. 娓呯悊鏃ュ織缂撳瓨
        result = await execute("journalctl --vacuum-time=3d 2>/dev/null || echo 'journalctl not available'")
        self._add_step("娓呯悊绯荤粺鏃ュ織", True, result["stdout"][:200])

        # 4. 娓呯悊 Docker 缂撳瓨
        result = await execute("docker system df 2>/dev/null || echo 'docker not available'")
        self._add_step("Docker纾佺洏浣跨敤", True, result["stdout"][:300])

        # 5. 娓呯悊涓存椂鏂囦欢
        result = await execute("rm -rf /tmp/* 2>/dev/null; echo done")
        self._add_step("娓呯悊涓存椂鏂囦欢", True, "瀹屾垚")

        # 鏈€缁?        disk2 = psutil.disk_usage("/")
        freed = disk.used - disk2.used
        self._add_step("娓呯悊缁撴灉", True, f"閲婃斁 {freed/1024**3:.2f}GB锛屼娇鐢ㄧ巼 {disk.percent}% 鈫?{disk2.percent}%")

        return self._report()


class RotationCheckRunbook(Runbook):
    """杞€煎煙鍚嶅贰妫€"""

    def __init__(self):
        super().__init__("杞€煎煙鍚嶅贰妫€", "妫€鏌ユ墍鏈夎疆鍊煎煙鍚岲NS/HTTPS/璺宠浆閾捐矾")

    async def run(self) -> dict:
        domains = state._data.get("rotation_domains", [])
        if not domains:
            self._add_step("鍩熷悕鍒楄〃", False, "娌℃湁閰嶇疆杞€煎煙鍚?)
            return self._report()

        self._add_step("鍩熷悕鎬绘暟", True, f"鍏?{len(domains)} 涓煙鍚?)

        async with httpx.AsyncClient(timeout=10, follow_redirects=True) as c:
            active = [d for d in domains if d.get("active")]
            self._add_step("娲昏穬鍩熷悕", True, f"{len(active)}/{len(domains)} 涓椿璺?)

            ok_count = 0
            for d in active:
                url = f"https://{d['domain']}"
                try:
                    r = await c.get(url, headers={"User-Agent": "Mozilla/5.0"})
                    chain = [str(h.url) for h in r.history] if r.history else []
                    ok = r.status_code < 400
                    if ok: ok_count += 1
                    d["health"] = "ok" if ok else "error"
                    self._add_step(d["domain"], ok, f"鐘舵€佺爜 {r.status_code}", " 鈫?".join(chain + [str(r.url)])[:200])
                except Exception as e:
                    d["health"] = "error"
                    self._add_step(d["domain"], False, str(e)[:100])

            state._save()
            self._add_step("妫€娴嬬粨鏋?, ok_count == len(active), f"{ok_count}/{len(active)} 姝ｅ父")

        return self._report()


class CustomerOrderRunbook(Runbook):
    """瀹㈡湇璁㈠崟鏌ヨ 鈥?鏌ョ敤鎴封啋鏌ヨ鍗曗啋鏌ユ敮浠樷啋鍥炲"""

    def __init__(self, user_id: str = "", order_id: str = ""):
        super().__init__("瀹㈡湇璁㈠崟鏌ヨ", "纭鐢ㄦ埛韬唤鈫掓煡璇㈣鍗曗啋鏀粯鐘舵€佲啋鍒ゆ柇寮傚父鈫掔敓鎴愬洖澶?)
        self.user_id = user_id
        self.order_id = order_id

    async def run(self) -> dict:
        async with httpx.AsyncClient(timeout=10) as c:
            # 鏌ョ敤鎴?            if self.user_id:
                try:
                    r = await c.get(f"{MALL_BASE_URL}/api/users", params={"id": self.user_id})
                    self._add_step("鐢ㄦ埛鏌ヨ", r.status_code == 200, f"鐢ㄦ埛 {self.user_id}" if r.status_code == 200 else f"閿欒 {r.status_code}")
                except Exception as e:
                    self._add_step("鐢ㄦ埛鏌ヨ", False, str(e)[:100])

            # 鏌ヨ鍗?            params = {}
            if self.order_id: params["id"] = self.order_id
            if self.user_id: params["userId"] = self.user_id
            try:
                r = await c.get(f"{MALL_BASE_URL}/api/orders", params=params)
                if r.status_code == 200:
                    data = r.json()
                    total = data.get("total", data.get("totalCount", "N/A"))
                    self._add_step("璁㈠崟鏌ヨ", True, f"鏌ュ埌 {total} 鏉¤鍗?)
                else:
                    self._add_step("璁㈠崟鏌ヨ", False, f"閿欒 {r.status_code}")
            except Exception as e:
                self._add_step("璁㈠崟鏌ヨ", False, str(e)[:100])

        # 鑷姩鐢熸垚鍥炲寤鸿
        if self._failed:
            self._add_step("鍥炲寤鸿", True, "璁㈠崟鏌ヨ寮傚父锛屽缓璁浆浜哄伐瀹㈡湇澶勭悊")
        else:
            self._add_step("鍥炲寤鸿", True, "璁㈠崟淇℃伅宸茶幏鍙栵紝鍙嚜鍔ㄥ洖澶嶅鎴?)

        return self._report()
