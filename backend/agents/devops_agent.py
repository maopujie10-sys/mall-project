锘?""DevOps Agent 鈥?鏈嶅姟鍣?Docker/Nginx/閮ㄧ讲鑷姩鍖?
鑱岃矗锛歋SH鎺у埗銆丏ocker杩愮淮銆丩inux绠＄悊銆丯ginx閰嶇疆銆佽嚜鍔ㄩ儴缃层€佽嚜鍔ㄦ仮澶?""
import os
import time
from datetime import datetime
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class ServerHealth:
    """鏈嶅姟鍣ㄥ仴搴风姸鎬?""
    host: str
    cpu_percent: float = 0
    mem_percent: float = 0
    disk_percent: float = 0
    load_avg: list = field(default_factory=list)
    uptime_days: int = 0
    status: str = "unknown"  # healthy/warning/critical
    checked_at: str = ""


@dataclass
class DockerService:
    """Docker鏈嶅姟鐘舵€?""
    name: str
    status: str = "unknown"  # running/stopped/restarting
    uptime: str = ""
    cpu_percent: float = 0
    mem_usage: str = ""
    ports: str = ""
    restart_count: int = 0


class DevOpsAgent:
    """DevOps Agent 鈥?鍩虹璁炬柦鍏ㄨ嚜鍔ㄨ繍缁?""

    @staticmethod
    async def check_server_health(host: str = "localhost") -> dict:
        """鍏ㄩ潰鏈嶅姟鍣ㄥ仴搴锋鏌?""
        import psutil
        health = ServerHealth(host=host, checked_at=datetime.now().isoformat())
        try:
            health.cpu_percent = psutil.cpu_percent(interval=1)
            mem = psutil.virtual_memory()
            health.mem_percent = mem.percent
            disk = psutil.disk_usage("/")
            health.disk_percent = disk.percent
            load = os.getloadavg() if hasattr(os, "getloadavg") else [0, 0, 0]
            health.load_avg = [round(l, 2) for l in load]

            # 鍒ゆ柇鍋ュ悍鐘舵€?
            if health.cpu_percent > 90 or health.mem_percent > 90 or health.disk_percent > 90:
                health.status = "critical"
            elif health.cpu_percent > 70 or health.mem_percent > 80 or health.disk_percent > 80:
                health.status = "warning"
            else:
                health.status = "healthy"

            return {
                "ok": True,
                "host": host,
                "cpu_percent": health.cpu_percent,
                "mem_percent": health.mem_percent,
                "disk_percent": health.disk_percent,
                "load_avg": health.load_avg,
                "status": health.status,
                "checked_at": health.checked_at,
                "suggestions": DevOpsAgent._get_suggestions(health),
            }
        except Exception as e:
            return {"ok": False, "error": str(e), "host": host}

    @staticmethod
    def _get_suggestions(health: ServerHealth) -> list:
        """鏍规嵁鍋ュ悍鐘舵€佺敓鎴愬缓璁?""
        suggestions = []
        if health.cpu_percent > 70:
            suggestions.append("CPU浣跨敤鐜囧亸楂橈紝寤鸿妫€鏌ラ珮鍗犵敤杩涚▼")
        if health.mem_percent > 80:
            suggestions.append("鍐呭瓨浣跨敤鐜囧亸楂橈紝寤鸿妫€鏌ュ唴瀛樻硠婕忔垨澧炲姞鍐呭瓨")
        if health.disk_percent > 80:
            suggestions.append("纾佺洏浣跨敤鐜囧亸楂橈紝寤鸿娓呯悊鏃ュ織鎴栨墿瀹?)
        if health.cpu_percent > 90:
            suggestions.append("鈿狅笍 CPU鍗辨€ワ紒寤鸿绔嬪嵆鎺掓煡")
        return suggestions

    @staticmethod
    async def check_ports() -> list:
        """妫€鏌ュ叧閿鍙ｇ姸鎬?""
        key_ports = [80, 443, 22, 3306, 5432, 6379, 8080, 9000, 5173]
        results = []
        import socket
        for port in key_ports:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(2)
            result = sock.connect_ex(("127.0.0.1", port))
            sock.close()
            results.append({
                "port": port,
                "open": result == 0,
                "service": {
                    80: "HTTP", 443: "HTTPS", 22: "SSH",
                    3306: "MySQL", 5432: "PostgreSQL", 6379: "Redis",
                    8080: "Java", 9000: "Agent API", 5173: "Vite Dev",
                }.get(port, "鏈煡"),
            })
        return results

    @staticmethod
    async def check_top_processes(limit: int = 10) -> list:
        """鏌ョ湅楂樺崰鐢ㄨ繘绋?""
        try:
            import psutil
            procs = []
            for p in psutil.process_iter(["pid", "name", "cpu_percent", "memory_percent"]):
                try:
                    procs.append(p.info)
                except Exception:
                    pass
            procs.sort(key=lambda x: x.get("cpu_percent", 0) or 0, reverse=True)
            return [
                {"pid": p["pid"], "name": p["name"], "cpu": round(p.get("cpu_percent", 0) or 0, 1), "mem": round(p.get("memory_percent", 0) or 0, 1)}
                for p in procs[:limit]
            ]
        except Exception as e:
            return [{"error": str(e)}]

    @staticmethod
    async def check_docker_status() -> dict:
        """Docker鍏ㄩ潰鐘舵€佹鏌?""
        import subprocess
        try:
            # 妫€鏌ocker鏄惁杩愯
            result = subprocess.run(["docker", "info"], capture_output=True, text=True, timeout=10)
            docker_running = result.returncode == 0

            if not docker_running:
                return {"ok": False, "error": "Docker鏈繍琛?, "containers": []}

            # 鍒楀嚭鎵€鏈夊鍣?
            result = subprocess.run(
                ["docker", "ps", "-a", "--format", "{{.Names}}|{{.Status}}|{{.Ports}}|{{.Image}}"],
                capture_output=True, text=True, timeout=10,
            )
            containers = []
            for line in result.stdout.strip().split("\n"):
                if not line:
                    continue
                parts = line.split("|")
                if len(parts) >= 3:
                    name, status, ports = parts[0], parts[1], parts[2] if len(parts) > 2 else ""
                    is_running = "Up" in status
                    containers.append({
                        "name": name,
                        "status": status,
                        "running": is_running,
                        "ports": ports,
                        "image": parts[3] if len(parts) > 3 else "",
                    })

            running_count = sum(1 for c in containers if c["running"])
            return {
                "ok": True,
                "docker_running": True,
                "total_containers": len(containers),
                "running_containers": running_count,
                "containers": containers,
            }
        except FileNotFoundError:
            return {"ok": False, "error": "Docker鏈畨瑁?, "containers": []}
        except Exception as e:
            return {"ok": False, "error": str(e), "containers": []}

    @staticmethod
    async def restart_container(name: str) -> dict:
        """閲嶅惎Docker瀹瑰櫒"""
        import subprocess
        try:
            result = subprocess.run(
                ["docker", "restart", name],
                capture_output=True, text=True, timeout=30,
            )
            return {
                "ok": result.returncode == 0,
                "container": name,
                "output": result.stdout.strip() or result.stderr.strip(),
            }
        except Exception as e:
            return {"ok": False, "container": name, "error": str(e)}

    @staticmethod
    async def check_nginx_status() -> dict:
        """Nginx鐘舵€佹鏌?""
        import subprocess
        try:
            result = subprocess.run(
                ["nginx", "-t"], capture_output=True, text=True, timeout=10,
            )
            config_ok = result.returncode == 0
            return {
                "ok": config_ok,
                "config_test": result.stdout.strip() + result.stderr.strip(),
                "config_valid": config_ok,
            }
        except FileNotFoundError:
            return {"ok": False, "error": "Nginx鏈畨瑁?}

    @staticmethod
    async def get_nginx_logs(lines: int = 50) -> dict:
        """鑾峰彇Nginx鏃ュ織"""
        import subprocess
        log_files = ["/var/log/nginx/access.log", "/var/log/nginx/error.log"]
        logs = {}
        for log_file in log_files:
            try:
                result = subprocess.run(
                    ["tail", f"-n{lines}", log_file],
                    capture_output=True, text=True, timeout=10,
                )
                logs[os.path.basename(log_file)] = result.stdout.strip().split("\n")[-lines:]
            except Exception:
                logs[os.path.basename(log_file)] = ["鏃犳硶璇诲彇"]
        return {"ok": True, "logs": logs}

    @staticmethod
    async def auto_heal_check() -> dict:
        """鑷姩淇妫€鏌?鈥?妫€娴嬪父瑙侀棶棰樺苟灏濊瘯淇"""
        fixes_applied = []
        issues_found = []

        # 1. 妫€鏌ocker
        docker_status = await DevOpsAgent.check_docker_status()
        if not docker_status.get("docker_running"):
            issues_found.append("Docker鏈繍琛?)
            try:
                import subprocess
                subprocess.run(["systemctl", "start", "docker"], timeout=10)
                fixes_applied.append("灏濊瘯鍚姩Docker")
            except Exception:
                pass

        # 2. 妫€鏌ュ叧閿鍣?
        for container in docker_status.get("containers", []):
            if not container["running"]:
                issues_found.append(f"瀹瑰櫒 {container['name']} 宸插仠姝?)
                try:
                    await DevOpsAgent.restart_container(container["name"])
                    fixes_applied.append(f"閲嶅惎瀹瑰櫒 {container['name']}")
                except Exception:
                    pass

        # 3. 妫€鏌ginx
        nginx_status = await DevOpsAgent.check_nginx_status()
        if not nginx_status.get("ok"):
            issues_found.append("Nginx閰嶇疆寮傚父")

        return {
            "ok": True,
            "issues_found": issues_found,
            "fixes_applied": fixes_applied,
            "all_healthy": len(issues_found) == 0,
            "checked_at": datetime.now().isoformat(),
        }