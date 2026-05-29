锘?""Self-Healing Agent 鈥?鑷姩妫€娴嬪紓甯?鑷姩淇/鑷姩鍥炴粴/鑷姩鎭㈠
鑱岃矗锛?x24宸℃銆佹晠闅滆嚜鍔ㄨ瘖鏂€佹櫤鑳戒慨澶嶃€佹湇鍔¤嚜鍔ㄦ仮澶?""
import json
import os
import time
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import Optional
from tools.alert_push import push_alert


@dataclass
class Anomaly:
    """寮傚父浜嬩欢"""
    id: str
    severity: str  # P1/P2/P3/P4
    source: str
    description: str
    detected_at: str
    status: str = "open"  # open/investigating/fixing/resolved
    auto_fix_attempted: bool = False
    fix_result: str = ""
    resolved_at: str = ""


class SelfHealingAgent:
    """Self-Healing Agent 鈥?鏁板瓧鍏嶇柅绯荤粺"""

    HEAL_DIR = "memory"
    ANOMALY_FILE = "memory/anomalies.json"

    @staticmethod
    def _ensure_dir():
        os.makedirs(SelfHealingAgent.HEAL_DIR, exist_ok=True)

    @staticmethod
    def _load_anomalies() -> list:
        SelfHealingAgent._ensure_dir()
        if not os.path.exists(SelfHealingAgent.ANOMALY_FILE):
            return []
        try:
            with open(SelfHealingAgent.ANOMALY_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []

    @staticmethod
    def _save_anomalies(anomalies: list):
        SelfHealingAgent._ensure_dir()
        with open(SelfHealingAgent.ANOMALY_FILE, "w", encoding="utf-8") as f:
            json.dump(anomalies, f, ensure_ascii=False, indent=2)

    # ===== 鑷姩宸℃ =====

    @staticmethod
    async def run_patrol() -> dict:
        """鎵ц鍏ㄩ潰宸℃"""
        issues = []
        checks_passed = 0
        checks_total = 0

        # 1. CPU妫€鏌?
        try:
            import psutil
            cpu = psutil.cpu_percent(interval=1)
            checks_total += 1
            if cpu > 95:
                issues.append({"severity": "P1", "source": "CPU", "detail": f"CPU浣跨敤鐜?{cpu}%锛屽嵄鎬?})
            elif cpu > 80:
                issues.append({"severity": "P2", "source": "CPU", "detail": f"CPU浣跨敤鐜?{cpu}%锛屽亸楂?})
            else:
                checks_passed += 1
        except Exception:
            issues.append({"severity": "P3", "source": "CPU", "detail": "鏃犳硶妫€鏌PU"})

        # 2. 鍐呭瓨妫€鏌?
        try:
            import psutil
            mem = psutil.virtual_memory().percent
            checks_total += 1
            if mem > 95:
                issues.append({"severity": "P1", "source": "Memory", "detail": f"鍐呭瓨浣跨敤鐜?{mem}%锛屽嵄鎬?})
            elif mem > 85:
                issues.append({"severity": "P2", "source": "Memory", "detail": f"鍐呭瓨浣跨敤鐜?{mem}%锛屽亸楂?})
            else:
                checks_passed += 1
        except Exception:
            issues.append({"severity": "P3", "source": "Memory", "detail": "鏃犳硶妫€鏌ュ唴瀛?})

        # 3. 纾佺洏妫€鏌?
        try:
            import psutil
            disk = psutil.disk_usage("/").percent
            checks_total += 1
            if disk > 95:
                issues.append({"severity": "P1", "source": "Disk", "detail": f"纾佺洏浣跨敤鐜?{disk}%锛屽嵄鎬?})
            elif disk > 85:
                issues.append({"severity": "P2", "source": "Disk", "detail": f"纾佺洏浣跨敤鐜?{disk}%锛屽亸楂?})
            else:
                checks_passed += 1
        except Exception:
            issues.append({"severity": "P3", "source": "Disk", "detail": "鏃犳硶妫€鏌ョ鐩?})

        # 4. Docker妫€鏌?
        try:
            import subprocess
            result = subprocess.run(["docker", "info"], capture_output=True, timeout=10)
            checks_total += 1
            if result.returncode != 0:
                issues.append({"severity": "P2", "source": "Docker", "detail": "Docker鏈嶅姟寮傚父"})
            else:
                # 妫€鏌ュ仠姝㈢殑瀹瑰櫒
                result = subprocess.run(
                    ["docker", "ps", "-a", "--filter", "status=exited", "--format", "{{.Names}}"],
                    capture_output=True, text=True, timeout=10,
                )
                stopped = [n for n in result.stdout.strip().split("\n") if n]
                if stopped:
                    issues.append({"severity": "P3", "source": "Docker", "detail": f"宸插仠姝㈠鍣? {', '.join(stopped[:5])}"})
                else:
                    checks_passed += 1
        except FileNotFoundError:
            checks_total += 1
            checks_passed += 1  # Docker鏈畨瑁呬笉绠楀紓甯?
        except Exception as e:
            issues.append({"severity": "P3", "source": "Docker", "detail": str(e)[:100]})

        # 5. 绔彛妫€鏌?
        key_ports = [80, 443, 8080, 9000, 5173]
        import socket
        for port in key_ports:
            checks_total += 1
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(2)
                result = sock.connect_ex(("127.0.0.1", port))
                sock.close()
                if result != 0:
                    issues.append({"severity": "P3", "source": "Port", "detail": f"绔彛 {port} 鏈洃鍚?})
                else:
                    checks_passed += 1
            except Exception:
                pass

        # 淇濆瓨寮傚父
        anomalies = SelfHealingAgent._load_anomalies()
        new_anomalies = 0
        for issue in issues:
            anomaly = {
                "id": str(int(time.time() * 1000)),
                "severity": issue["severity"],
                "source": issue["source"],
                "description": issue["detail"],
                "detected_at": datetime.now().isoformat(),
                "status": "open",
                "auto_fix_attempted": False,
                "fix_result": "",
                "resolved_at": "",
            }
            anomalies.insert(0, anomaly)
            new_anomalies += 1

        if len(anomalies) > 500:
            anomalies = anomalies[:500]
        SelfHealingAgent._save_anomalies(anomalies)

        health_score = round(checks_passed / max(checks_total, 1) * 100, 1)

        return {
            "ok": True,
            "patrol_at": datetime.now().isoformat(),
            "checks_total": checks_total,
            "checks_passed": checks_passed,
            "health_score": health_score,
            "issues_found": len(issues),
            "new_anomalies": new_anomalies,
            "issues": issues,
            "status": "healthy" if health_score >= 90 else ("warning" if health_score >= 70 else "critical"),
        }

    # ===== 鑷姩淇 =====

    @staticmethod
    async def auto_fix(anomaly_id: str = None) -> dict:
        """灏濊瘯鑷姩淇寮傚父"""
        anomalies = SelfHealingAgent._load_anomalies()

        if anomaly_id:
            targets = [a for a in anomalies if a["id"] == anomaly_id]
        else:
            # 鑷姩淇鎵€鏈塷pen鐨勫紓甯?
            targets = [a for a in anomalies if a["status"] == "open"]

        fixed = 0
        failed = 0
        results = []

        for target in targets:
            target["auto_fix_attempted"] = True
            fix = SelfHealingAgent._attempt_fix(target)
            results.append({"id": target["id"], "source": target["source"], "result": fix})

            if fix.get("fixed"):
                target["status"] = "resolved"
                target["fix_result"] = "auto"
                target["resolved_at"] = datetime.now().isoformat()
                fixed += 1
            else:
                target["status"] = "investigating"
                target["fix_result"] = f"auto_failed: {fix.get('error', 'unknown')}"
                failed += 1

        SelfHealingAgent._save_anomalies(anomalies)
        return {
            "ok": True,
            "attempted": len(targets),
            "fixed": fixed,
            "failed": failed,
            "results": results,
        }

    @staticmethod
    def _attempt_fix(anomaly: dict) -> dict:
        """灏濊瘯淇鍗曚釜寮傚父"""
        source = anomaly.get("source", "")

        if source == "Docker":
            try:
                import subprocess
                # 灏濊瘯閲嶅惎Docker
                result = subprocess.run(["systemctl", "restart", "docker"], capture_output=True, timeout=30)
                if result.returncode == 0:
                    return {"fixed": True, "action": "Docker鏈嶅姟宸查噸鍚?}
                # 灏濊瘯閲嶅惎鍋滄鐨勫鍣?
                stopped = anomaly.get("description", "")
                if "宸插仠姝㈠鍣? in stopped:
                    for name in stopped.replace("宸插仠姝㈠鍣? ", "").split(", "):
                        subprocess.run(["docker", "restart", name], capture_output=True, timeout=30)
                    return {"fixed": True, "action": "宸插皾璇曢噸鍚仠姝㈢殑瀹瑰櫒"}
            except Exception:
                pass
            return {"fixed": False, "error": "鏃犳硶鑷姩淇Docker"}

        if source in ("CPU", "Memory"):
            try:
                import psutil
                # 鎵惧嚭楂樺崰鐢ㄨ繘绋?
                high_procs = []
                for p in psutil.process_iter(["pid", "name", "cpu_percent", "memory_percent"]):
                    try:
                        if source == "CPU" and (p.info.get("cpu_percent", 0) or 0) > 50:
                            high_procs.append(f"{p.info['name']}(PID:{p.info['pid']})")
                        if source == "Memory" and (p.info.get("memory_percent", 0) or 0) > 30:
                            high_procs.append(f"{p.info['name']}(PID:{p.info['pid']})")
                    except Exception:
                        pass
                if high_procs:
                    return {"fixed": False, "error": f"楂樺崰鐢ㄨ繘绋? {', '.join(high_procs[:5])}锛岄渶浜哄伐浠嬪叆"}
            except Exception:
                pass
            return {"fixed": False, "error": "璧勬簮闂闇€浜哄伐鎺掓煡"}

        if source == "Disk":
            try:
                import subprocess
                # 娓呯悊Docker鏃ュ織
                subprocess.run(["docker", "system", "prune", "-f"], capture_output=True, timeout=60)
                return {"fixed": True, "action": "宸叉竻鐞咲ocker缂撳瓨"}
            except Exception:
                pass
            return {"fixed": False, "error": "纾佺洏娓呯悊澶辫触"}

        return {"fixed": False, "error": "鏃犺嚜鍔ㄤ慨澶嶆柟妗?}

    # ===== 寮傚父鍘嗗彶 =====

    @staticmethod
    async def get_anomaly_history(days: int = 7) -> dict:
        """鑾峰彇寮傚父鍘嗗彶"""
        anomalies = SelfHealingAgent._load_anomalies()
        cutoff = (datetime.now() - timedelta(days=days)).isoformat()

        recent = [a for a in anomalies if a.get("detected_at", "") >= cutoff]

        severity_counts = {"P1": 0, "P2": 0, "P3": 0, "P4": 0}
        source_counts = {}
        for a in recent:
            sev = a.get("severity", "P4")
            severity_counts[sev] = severity_counts.get(sev, 0) + 1
            src = a.get("source", "other")
            source_counts[src] = source_counts.get(src, 0) + 1

        return {
            "ok": True,
            "period": f"鏈€杩憑days}澶?,
            "total": len(recent),
            "open": sum(1 for a in recent if a.get("status") == "open"),
            "resolved": sum(1 for a in recent if a.get("status") == "resolved"),
            "auto_fixed": sum(1 for a in recent if a.get("fix_result") == "auto"),
            "by_severity": severity_counts,
            "by_source": source_counts,
            "recent": recent[:20],
        }

    @staticmethod
    async def resolve_anomaly(anomaly_id: str, resolution: str = "manual") -> dict:
        """鎵嬪姩鏍囪寮傚父宸茶В鍐?""
        anomalies = SelfHealingAgent._load_anomalies()
        for a in anomalies:
            if a["id"] == anomaly_id:
                a["status"] = "resolved"
                a["fix_result"] = resolution
                a["resolved_at"] = datetime.now().isoformat()
                SelfHealingAgent._save_anomalies(anomalies)
                return {"ok": True, "id": anomaly_id, "resolved": True}
        return {"ok": False, "error": "寮傚父涓嶅瓨鍦?}
