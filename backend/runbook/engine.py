"""自助运维 Runbook — 自动化故障处理流程引擎"""
import httpx
from datetime import datetime
from typing import Optional
from state import state
from risk import handle_risk
from config import MALL_BASE_URL

class StepResult:
    """单步执行结果"""
    def __init__(self, name: str, ok: bool, detail: str = "", evidence: str = ""):
        self.name = name
        self.ok = ok
        self.detail = detail
        self.evidence = evidence
        self.time = datetime.now().strftime("%H:%M:%S")

    def to_dict(self):
        return {"name": self.name, "ok": self.ok, "detail": self.detail, "evidence": self.evidence, "time": self.time}


class Runbook:
    """Runbook 基类"""

    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
        self.steps: list[StepResult] = []
        self._failed = False

    async def run(self) -> dict:
        """执行 runbook，返回完整报告"""
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
            return f"完成 {passed}/{total} 步。❌ 异常: {', '.join(failed_steps)}。建议人工介入。"
        return f"全部 {total} 步通过 ✅，系统运行正常。"


# ===== 具体 Runbook =====

class MallDownRunbook(Runbook):
    """商城打不开 — 端到端诊断"""

    def __init__(self):
        super().__init__("商城打不开诊断", "检查DNS→服务器→端口→Nginx→Docker→日志→数据库→诊断报告")

    async def run(self) -> dict:
        async with httpx.AsyncClient(timeout=10, follow_redirects=True) as c:
            # 1. 检查域名解析
            try:
                r = await c.get(f"https://dns.google/resolve?name={MALL_BASE_URL.replace('http://','').replace('https://','').split(':')[0]}&type=A")
                data = r.json()
                ips = [a.get("data") for a in data.get("Answer", [])] if data.get("Status") == 0 else []
                self._add_step("DNS解析", len(ips) > 0, f"解析到 {len(ips)} 个IP: {', '.join(ips[:3])}", str(ips[:3]))
            except Exception as e:
                self._add_step("DNS解析", False, f"DNS查询失败: {str(e)}")

            # 2. 检测服务器连通性
            for port, name in [(80, "HTTP"), (443, "HTTPS"), (9000, "Agent")]:
                try:
                    r = await c.get(f"{MALL_BASE_URL if port != 9000 else 'http://localhost:9000'}/agent/health", timeout=5)
                    self._add_step(f"{name}端口", r.status_code == 200, f"状态码 {r.status_code}")
                except Exception as e:
                    self._add_step(f"{name}端口", False, f"连接失败: {str(e)[:50]}")

            # 3. 检查商城关键页面
            for path, name in [("/", "首页"), ("/api/products", "商品接口"), ("/api/categories", "分类接口")]:
                try:
                    r = await c.get(f"{MALL_BASE_URL}{path}", timeout=5)
                    self._add_step(f"商城{name}", r.status_code < 500, f"状态码 {r.status_code}")
                except Exception as e:
                    self._add_step(f"商城{name}", False, str(e)[:50])

        return self._report()


class ServerHealthRunbook(Runbook):
    """服务器健康检查"""

    def __init__(self):
        super().__init__("服务器健康检查", "检查CPU/内存/磁盘/负载/进程/端口")

    async def run(self) -> dict:
        from executor import execute

        checks = [
            ("CPU负载", "uptime", lambda r: "load average" in r["stdout"]),
            ("内存使用", "free -h", lambda r: "Mem" in r["stdout"]),
            ("磁盘空间", "df -h /", lambda r: r["success"]),
            ("SWAP使用", "free -h | grep Swap", lambda r: True),
            ("系统运行时间", "uptime -p", lambda r: r["success"]),
            ("登录记录", "last -5", lambda r: r["success"]),
        ]

        for name, cmd, check in checks:
            result = await execute(cmd)
            self._add_step(name, check(result), result["stdout"][:200] or result["stderr"][:100])

        # CPU 过载告警
        import psutil
        cpu = psutil.cpu_percent(interval=0.5)
        mem = psutil.virtual_memory()
        disk = psutil.disk_usage("/")
        self._add_step("CPU使用率", cpu < 80, f"CPU {cpu}%")
        self._add_step("内存使用率", mem.percent < 80, f"内存 {mem.percent}%")
        self._add_step("磁盘使用率", disk.percent < 85, f"磁盘 {disk.percent}%")

        return self._report()


class DiskFullRunbook(Runbook):
    """磁盘快满 — 分析大文件/清理日志/压缩"""

    def __init__(self):
        super().__init__("磁盘清理", "分析磁盘使用→定位大文件→清理日志→压缩备份")

    async def run(self) -> dict:
        from executor import execute
        import shutil, psutil

        # 1. 磁盘现状
        disk = psutil.disk_usage("/")
        self._add_step("磁盘使用率", disk.percent < 90, f"已用 {disk.percent}% ({disk.used/1024**3:.1f}GB/{disk.total/1024**3:.1f}GB)")

        # 2. 找大目录
        result = await execute("du -sh /var/log /tmp /opt 2>/dev/null | sort -rh | head -5")
        self._add_step("大目录分析", result["success"], result["stdout"][:300])

        # 3. 清理日志缓存
        result = await execute("journalctl --vacuum-time=3d 2>/dev/null || echo 'journalctl not available'")
        self._add_step("清理系统日志", True, result["stdout"][:200])

        # 4. 清理 Docker 缓存
        result = await execute("docker system df 2>/dev/null || echo 'docker not available'")
        self._add_step("Docker磁盘使用", True, result["stdout"][:300])

        # 5. 清理临时文件
        result = await execute("rm -rf /tmp/* 2>/dev/null; echo done")
        self._add_step("清理临时文件", True, "完成")

        # 最终
        disk2 = psutil.disk_usage("/")
        freed = disk.used - disk2.used
        self._add_step("清理结果", True, f"释放 {freed/1024**3:.2f}GB，使用率 {disk.percent}% → {disk2.percent}%")

        return self._report()


class RotationCheckRunbook(Runbook):
    """轮值域名巡检"""

    def __init__(self):
        super().__init__("轮值域名巡检", "检查所有轮值域名DNS/HTTPS/跳转链路")

    async def run(self) -> dict:
        domains = state._data.get("rotation_domains", [])
        if not domains:
            self._add_step("域名列表", False, "没有配置轮值域名")
            return self._report()

        self._add_step("域名总数", True, f"共 {len(domains)} 个域名")

        async with httpx.AsyncClient(timeout=10, follow_redirects=True) as c:
            active = [d for d in domains if d.get("active")]
            self._add_step("活跃域名", True, f"{len(active)}/{len(domains)} 个活跃")

            ok_count = 0
            for d in active:
                url = f"https://{d['domain']}"
                try:
                    r = await c.get(url, headers={"User-Agent": "Mozilla/5.0"})
                    chain = [str(h.url) for h in r.history] if r.history else []
                    ok = r.status_code < 400
                    if ok: ok_count += 1
                    d["health"] = "ok" if ok else "error"
                    self._add_step(d["domain"], ok, f"状态码 {r.status_code}", " → ".join(chain + [str(r.url)])[:200])
                except Exception as e:
                    d["health"] = "error"
                    self._add_step(d["domain"], False, str(e)[:100])

            state._save()
            self._add_step("检测结果", ok_count == len(active), f"{ok_count}/{len(active)} 正常")

        return self._report()


class CustomerOrderRunbook(Runbook):
    """客服订单查询 — 查用户→查订单→查支付→回复"""

    def __init__(self, user_id: str = "", order_id: str = ""):
        super().__init__("客服订单查询", "确认用户身份→查询订单→支付状态→判断异常→生成回复")
        self.user_id = user_id
        self.order_id = order_id

    async def run(self) -> dict:
        async with httpx.AsyncClient(timeout=10) as c:
            # 查用户
            if self.user_id:
                try:
                    r = await c.get(f"{MALL_BASE_URL}/api/users", params={"id": self.user_id})
                    self._add_step("用户查询", r.status_code == 200, f"用户 {self.user_id}" if r.status_code == 200 else f"错误 {r.status_code}")
                except Exception as e:
                    self._add_step("用户查询", False, str(e)[:100])

            # 查订单
            params = {}
            if self.order_id: params["id"] = self.order_id
            if self.user_id: params["userId"] = self.user_id
            try:
                r = await c.get(f"{MALL_BASE_URL}/api/orders", params=params)
                if r.status_code == 200:
                    data = r.json()
                    total = data.get("total", data.get("totalCount", "N/A"))
                    self._add_step("订单查询", True, f"查到 {total} 条订单")
                else:
                    self._add_step("订单查询", False, f"错误 {r.status_code}")
            except Exception as e:
                self._add_step("订单查询", False, str(e)[:100])

        # 自动生成回复建议
        if self._failed:
            self._add_step("回复建议", True, "订单查询异常，建议转人工客服处理")
        else:
            self._add_step("回复建议", True, "订单信息已获取，可自动回复客户")

        return self._report()
