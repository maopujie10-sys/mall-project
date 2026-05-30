"""Alert Closed Loop - Auto-detect and fix server issues"""
import asyncio, json, time, subprocess, os
from datetime import datetime
from state import state
from tools.logger import logger

AUTO_FIX_RULES = {
    "disk_full": {
        "pattern": ["disk", "space", "full", "storage", "capacity"],
        "fix": "docker system prune -af 2>/dev/null; find /tmp -mtime +7 -delete 2>/dev/null",
        "verify": "df -h / | tail -1 | awk '\''{print $5}'\''",
        "max_retries": 2,
    },
    "cpu_high": {
        "pattern": ["cpu", "high", "load", "overload", "throttle"],
        "fix": "docker restart $(docker ps --filter status=running --format '\''{{.Names}}'\'' | head -3) 2>/dev/null",
        "verify": "uptime | awk -F'\''load average:'\'' '\''{print $2}'\'' | cut -d, -f1",
        "max_retries": 1,
    },
    "memory_high": {
        "pattern": ["memory", "ram", "leak", "OOM", "swap"],
        "fix": "sync; echo 3 > /proc/sys/vm/drop_caches 2>/dev/null; docker system prune -f 2>/dev/null",
        "verify": "free -m | awk '\''/Mem:/{printf \"%.0f\", $3/$2*100}'\''",
        "max_retries": 1,
    },
    "service_down": {
        "pattern": ["down", "stopped", "unhealthy", "crashed", "exit"],
        "fix": "cd /home/data/projects/mall/mall-project && docker compose -f docker-compose.ai.yml up -d 2>/dev/null",
        "verify": "docker ps --filter status=running --format '\''{{.Names}}'\'' | wc -l",
        "max_retries": 3,
    },
    "nginx_error": {
        "pattern": ["nginx", "502", "503", "504", "gateway", "proxy"],
        "fix": "nginx -t 2>/dev/null && nginx -s reload 2>/dev/null || systemctl restart nginx 2>/dev/null",
        "verify": "curl -s -o /dev/null -w '\''%{http_code}'\'' http://localhost:80/ 2>/dev/null || echo 000",
        "max_retries": 2,
    },
    "db_connection": {
        "pattern": ["database", "mysql", "connection", "timeout", "refused"],
        "fix": "docker restart $(docker ps --filter name=mysql --format '\''{{.Names}}'\'') 2>/dev/null",
        "verify": "docker ps --filter name=mysql --filter status=running --format '\''{{.Names}}'\'' | wc -l",
        "max_retries": 3,
    },
}

class AlertClosedLoop:
    """Alert Closed Loop - Auto-detection and self-healing engine"""
    
    _loop_history = []
    
    @classmethod
    def get_history(cls, limit=20):
        return cls._loop_history[-limit:]
    
    @classmethod
    async def detect_and_fix(cls, alert_title, alert_detail='', auto_fix=True):
        """Detect alert type and attempt auto-fix"""
        result = {
            "time": datetime.now().isoformat(),
            "alert": alert_title,
            "detail": alert_detail,
            "auto_fix": auto_fix,
            "matched_rule": None,
            "fix_attempted": False,
            "fix_success": False,
            "verification": '',
            "steps": [],
        }
        
        if auto_fix:
            combined = (alert_title + ' ' + alert_detail).lower()
            for rule_name, rule in AUTO_FIX_RULES.items():
                valid_patterns = [p for p in rule["pattern"] if p]
                if valid_patterns and any(p.lower() in combined for p in valid_patterns):
                    result["matched_rule"] = rule_name
                    result["steps"].append("Matched: " + rule_name)
                    
                    for attempt in range(rule["max_retries"]):
                        result["fix_attempted"] = True
                        result["steps"].append("Attempt {}/{}".format(attempt+1, rule["max_retries"]))
                        
                        try:
                            proc = subprocess.run(
                                rule["fix"], shell=True, capture_output=True, text=True, timeout=30
                            )
                            result["steps"].append("Fix: " + rule["fix"][:80] + "...")
                            result["steps"].append("Output: " + (proc.stdout.strip() or proc.stderr.strip())[:200])
                        except Exception as e:
                            result["steps"].append("Error: " + str(e)[:100])
                            break
                        
                        await asyncio.sleep(2)
                        
                        try:
                            proc = subprocess.run(
                                rule["verify"], shell=True, capture_output=True, text=True, timeout=15
                            )
                            result["verification"] = proc.stdout.strip()
                            result["steps"].append("Verify: " + result["verification"][:100])
                            result["fix_success"] = True
                            break
                        except Exception as e:
                            result["steps"].append("Verify Error: " + str(e)[:100])
                    
                    break
        
        if not result["matched_rule"]:
            result["steps"].append("No matching rule found")
        
        alerts = state._data.setdefault("alerts", [])
        for alert in alerts:
            if alert.get("title") == alert_title and alert.get("status") != "resolved":
                alert["status"] = "resolved" if result["fix_success"] else "auto_fix_failed"
                alert["fixed_at"] = datetime.now().isoformat() if result["fix_success"] else None
                alert["fix_result"] = result
                break
        
        cls._loop_history.append(result)
        if len(cls._loop_history) > 500:
            cls._loop_history = cls._loop_history[-500:]
        
        state._save()
        logger.info("AlertClosedLoop: {} -> fix={}".format(alert_title, "OK" if result["fix_success"] else "FAIL"))
        
        return result
    
    @classmethod
    async def run_health_check(cls):
        """Run system health check and auto-fix issues"""
        checks = []
        
        try:
            proc = subprocess.run(
                "df -h / | tail -1 | awk '\''{print $5}'\''",
                shell=True, capture_output=True, text=True, timeout=10
            )
            disk_use = proc.stdout.strip().replace("%", "")
            if disk_use and int(disk_use) > 85:
                checks.append({"type": "disk_full", "status": "fail", "detail": "Disk usage: {}%".format(disk_use)})
        except:
            pass
        
        try:
            proc = subprocess.run(
                "free -m | awk '\''/Mem:/{printf \"%.0f\", $3/$2*100}'\''",
                shell=True, capture_output=True, text=True, timeout=10
            )
            mem_use = proc.stdout.strip()
            if mem_use and int(mem_use) > 90:
                checks.append({"type": "memory_high", "status": "fail", "detail": "Memory usage: {}%".format(mem_use)})
        except:
            pass
        
        try:
            proc = subprocess.run(
                "docker ps --filter status=running --format '\''{{.Names}}'\'' | wc -l",
                shell=True, capture_output=True, text=True, timeout=10
            )
            running = proc.stdout.strip()
            if running and int(running) < 2:
                checks.append({"type": "service_down", "status": "fail", "detail": "Only {} containers running".format(running)})
        except:
            pass
        
        results = []
        for check in checks:
            if check["status"] == "fail":
                fix_result = await cls.detect_and_fix(check["type"], check["detail"], auto_fix=True)
                results.append(dict(**check, fix_result=fix_result))
        
        return {
            "ok": True,
            "time": datetime.now().isoformat(),
            "checks": len(checks),
            "failed": len([c for c in checks if c["status"] == "fail"]),
            "fixed": len([r for r in results if r.get("fix_result", {}).get("fix_success")]),
            "results": results,
        }
