''" Runbook -- ''"
import httpx
from datetime import datetime
from typing import Optional
from state import state
from risk import handle_risk
from config import MALL_BASE_URL

class StepResult:
    ''''''
    def __init__(self, name: str, ok: bool, detail: str = '', evidence: str = ''):
        self.name = name
        self.ok = ok
        self.detail = detail
        self.evidence = evidence
        self.time = datetime.now().strftime("%H:%M:%S")

    def to_dict(self):
        return {"name": self.name, "ok": self.ok, "detail": self.detail, "evidence": self.evidence, "time": self.time}


class Runbook:
    ''"Runbook ''"

    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
        self.steps: list[StepResult] = []
        self._failed = False

    async def run(self) -> dict:
        ''" runbook,''"
        raise NotImplementedError

    def _add_step(self, name: str, ok: bool, detail: str = '', evidence: str = ''):
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
            return f" {passed}/{total} . : {', '.join(failed_steps)}.."
        return f" {total}  ,."


# =====  Runbook =====

class MallDownRunbook(Runbook):
    ''" -- ''"

    def __init__(self):
        super().__init__('', "DNS->->->Nginx->Docker->->->")

    async def run(self) -> dict:
        async with httpx.AsyncClient(timeout=10, follow_redirects=True) as c:
            # 1. 
            try:
                r = await c.get(f"https://dns.google/resolve?name={MALL_BASE_URL.replace('http://','').replace('https://','').split(':')[0]}&type=A")
                data = r.json()
                ips = [a.get("data") for a in data.get("Answer", [])] if data.get("Status") == 0 else []
                self._add_step("DNS", len(ips) > 0, f" {len(ips)} IP: {', '.join(ips[:3])}", str(ips[:3]))
            except Exception as e:
                self._add_step("DNS", False, f"DNS: {str(e)}")

            # 2. 
            for port, name in [(80, "HTTP"), (443, "HTTPS"), (9000, "Agent")]:
                try:
                    r = await c.get(f"{MALL_BASE_URL if port != 9000 else 'http://localhost:9000'}/agent/health", timeout=5)
                    self._add_step(f"{name}", r.status_code == 200, f" {r.status_code}")
                except Exception as e:
                    self._add_step(f"{name}", False, f": {str(e)[:50]}")

            # 3. 
            for path, name in [("/", ''), ("/api/products", ''), ("/api/categories", '')]:
                try:
                    r = await c.get(f"{MALL_BASE_URL}{path}", timeout=5)
                    self._add_step(f"{name}", r.status_code < 500, f" {r.status_code}")
                except Exception as e:
                    self._add_step(f"{name}", False, str(e)[:50])

        return self._report()


class ServerHealthRunbook(Runbook):
    ''''''

    def __init__(self):
        super().__init__('', "CPU/////")

    async def run(self) -> dict:
        from executor import execute

        checks = [
            ("CPU", "uptime", lambda r: "load average" in r["stdout"]),
            ('', "free -h", lambda r: "Mem" in r["stdout"]),
            ('', "df -h /", lambda r: r["success"]),
            ("SWAP", "free -h | grep Swap", lambda r: True),
            ('', "uptime -p", lambda r: r["success"]),
            ('', "last -5", lambda r: r["success"]),
        ]

        for name, cmd, check in checks:
            result = await execute(cmd)
            self._add_step(name, check(result), result["stdout"][:200] or result["stderr"][:100])

        # CPU 
        import psutil
        cpu = psutil.cpu_percent(interval=0.5)
        mem = psutil.virtual_memory()
        disk = psutil.disk_usage("/")
        self._add_step("CPU", cpu < 80, f"CPU {cpu}%")
        self._add_step('', mem.percent < 80, f" {mem.percent}%")
        self._add_step('', disk.percent < 85, f" {disk.percent}%")

        return self._report()


class DiskFullRunbook(Runbook):
    ''" -- //''"

    def __init__(self):
        super().__init__('', "->->->")

    async def run(self) -> dict:
        from executor import execute
        import shutil, psutil

        # 1. 
        disk = psutil.disk_usage("/")
        self._add_step('', disk.percent < 90, f" {disk.percent}% ({disk.used/1024**3:.1f}GB/{disk.total/1024**3:.1f}GB)")

        # 2. 
        result = await execute("du -sh /var/log /tmp /opt 2>/dev/null | sort -rh | head -5")
        self._add_step('', result["success"], result["stdout"][:300])

        # 3. 
        result = await execute("journalctl --vacuum-time=3d 2>/dev/null || echo 'journalctl not available'')
        self._add_step('', True, result["stdout"][:200])

        # 4.  Docker 
        result = await execute("docker system df 2>/dev/null || echo 'docker not available'')
        self._add_step("Docker", True, result["stdout"][:300])

        # 5. 
        result = await execute("rm -rf /tmp/* 2>/dev/null; echo done")
        self._add_step('', True, '')

        
        disk2 = psutil.disk_usage("/")
        freed = disk.used - disk2.used
        self._add_step('', True, f" {freed/1024**3:.2f}GB, {disk.percent}% -> {disk2.percent}%")

        return self._report()


class RotationCheckRunbook(Runbook):
    ''''''

    def __init__(self):
        super().__init__('', "DNS/HTTPS/")

    async def run(self) -> dict:
        domains = state._data.get("rotation_domains", [])
        if not domains:
            self._add_step('', False, '')
            return self._report()

        self._add_step('', True, f" {len(domains)} ")

        async with httpx.AsyncClient(timeout=10, follow_redirects=True) as c:
            active = [d for d in domains if d.get("active")]
            self._add_step('', True, f"{len(active)}/{len(domains)} ")

            ok_count = 0
            for d in active:
                url = f"https://{d['domain']}"
                try:
                    r = await c.get(url, headers={"User-Agent": "Mozilla/5.0"})
                    chain = [str(h.url) for h in r.history] if r.history else []
                    ok = r.status_code < 400
                    if ok: ok_count += 1
                    d["health"] = "ok" if ok else "error"
                    self._add_step(d["domain"], ok, f" {r.status_code}", " -> ".join(chain + [str(r.url)])[:200])
                except Exception as e:
                    d["health"] = "error"
                    self._add_step(d["domain"], False, str(e)[:100])

            state._save()
            self._add_step('', ok_count == len(active), f"{ok_count}/{len(active)} ")

        return self._report()


class CustomerOrderRunbook(Runbook):
    ''" -- ->->->''"

    def __init__(self, user_id: str = '', order_id: str = ''):
        super().__init__('', "->->->->")
        self.user_id = user_id
        self.order_id = order_id

    async def run(self) -> dict:
        async with httpx.AsyncClient(timeout=10) as c:
            
            if self.user_id:
                try:
                    r = await c.get(f"{MALL_BASE_URL}/api/users", params={"id": self.user_id})
                    self._add_step('', r.status_code == 200, f" {self.user_id}" if r.status_code == 200 else f" {r.status_code}")
                except Exception as e:
                    self._add_step('', False, str(e)[:100])

            
            params = {}
            if self.order_id: params["id"] = self.order_id
            if self.user_id: params["userId"] = self.user_id
            try:
                r = await c.get(f"{MALL_BASE_URL}/api/orders", params=params)
                if r.status_code == 200:
                    data = r.json()
                    total = data.get("total", data.get("totalCount", "N/A"))
                    self._add_step('', True, f" {total} ")
                else:
                    self._add_step('', False, f" {r.status_code}")
            except Exception as e:
                self._add_step('', False, str(e)[:100])

        
        if self._failed:
            self._add_step('', True, ",")
        else:
            self._add_step('', True, ",")

        return self._report()
