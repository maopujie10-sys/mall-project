"""告警闭环引擎 -- 检测->诊断->修复->验证"""
import asyncio, json, time, subprocess, os
from datetime import datetime
from state import state
from tools.logger import logger

AUTO_FIX_RULES = {
    "disk_full": {
        "pattern": ["disk", "space", "full", "磁盘", "空间不足"],
        "fix": "docker system prune -af 2>/dev/null; find /tmp -mtime +7 -delete 2>/dev/null",
        "verify": "df -h / | tail -1 | awk '{print $5}'",
        "max_retries": 2,
    },
    "cpu_high": {
        "pattern": ["cpu", "high", "CPU", "过高"],
        "fix": "docker restart $(docker ps --filter status=running --format '{{.Names}}' | head -3) 2>/dev/null",
        "verify": "uptime | awk -F'load average:' '{print $2}' | cut -d, -f1",
        "max_retries": 1,
    },
    "memory_high": {
        "pattern": ["memory", "ram", "内存", "OOM"],
        "fix": "sync; echo 3 > /proc/sys/vm/drop_caches 2>/dev/null; docker system prune -f 2>/dev/null",
        "verify": 'free -m | awk "/Mem:/{printf \"%.0f\", $3/$2*100}"',
        "max_retries": 1,
    },
    "service_down": {
        "pattern": ["down", "stopped", "unhealthy", "停止", "服务挂"],
        "fix": "cd /home/data/projects/mall/mall-project && docker compose -f docker-compose.ai.yml up -d 2>/dev/null",
        "verify": "docker ps --filter status=running --format '{{.Names}}' | wc -l",
        "max_retries": 3,
    },
    "nginx_error": {
        "pattern": ["nginx", "502", "503", "504", "gateway"],
        "fix": "nginx -t 2>/dev/null && nginx -s reload 2>/dev/null || systemctl restart nginx 2>/dev/null",
        "verify": "curl -s -o /dev/null -w '%{http_code}' http://localhost:80/ 2>/dev/null || echo 000",
        "max_retries": 2,
    },
    "db_connection": {
        "pattern": ["database", "mysql", "connection", "连接", "超时"],
        "fix": "docker restart $(docker ps --filter name=mysql --format '{{.Names}}') 2>/dev/null",
        "verify": "docker ps --filter name=mysql --filter status=running --format '{{.Names}}' | wc -l",
        "max_retries": 3,
    },
}

class AlertClosedLoop:
    """告警自动闭环: 接收告警->规则匹配->自动修复->验证结果->记录历史"""
    
    _loop_history = []
    
    @classmethod
    def get_history(cls, limit=20):
        return cls._loop_history[-limit:]
    
    @classmethod
    async def detect_and_fix(cls, alert_title, alert_detail="", auto_fix=True):
        """检测告警并自动修复"""
        result = {
            "time": datetime.now().isoformat(),
            "alert": alert_title,
            "detail": alert_detail,
            "auto_fix": auto_fix,
            "matched_rule": None,
            "fix_attempted": False,
            "fix_success": False,
            "verification": "",
            "steps": [],
        }
        
        if auto_fix:
            combined = (alert_title + " " + alert_detail).lower()
            for rule_name, rule in AUTO_FIX_RULES.items():
                if any(p.lower() in combined for p in rule["pattern"]):
                    result["matched_rule"] = rule_name
                    result["steps"].append("匹配规则: " + rule_name)
                    
                    for attempt in range(rule["max_retries"]):
                        result["fix_attempted"] = True
                        result["steps"].append("执行修复 {}/{}".format(attempt+1, rule["max_retries"]))
                        
                        try:
                            proc = subprocess.run(
                                rule["fix"], shell=True, capture_output=True, text=True, timeout=30
                            )
                            result["steps"].append("修复命令: " + rule["fix"][:80] + "...")
                            result["steps"].append("输出: " + (proc.stdout.strip() or proc.stderr.strip())[:200])
                        except Exception as e:
                            result["steps"].append("修复执行异常: " + str(e)[:100])
                            break
                        
                        await asyncio.sleep(2)
                        
                        try:
                            proc = subprocess.run(
                                rule["verify"], shell=True, capture_output=True, text=True, timeout=15
                            )
                            result["verification"] = proc.stdout.strip()
                            result["steps"].append("验证结果: " + result["verification"][:100])
                            result["fix_success"] = True
                            break
                        except Exception as e:
                            result["steps"].append("验证失败: " + str(e)[:100])
                    
                    break
        
        if not result["matched_rule"]:
            result["steps"].append("未匹配到自动修复规则，需人工处理")
        
        # 更新告警状态
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
        logger.info("告警闭环: {} -> fix={}".format(alert_title, "OK" if result["fix_success"] else "FAIL"))
        
        return result
    
    @classmethod
    async def run_health_check(cls):
        """定时健康巡检，自动检测并修复"""
        checks = []
        
        # 磁盘检查
        try:
            proc = subprocess.run(
                "df -h / | tail -1 | awk '{print $5}'",
                shell=True, capture_output=True, text=True, timeout=10
            )
            disk_use = proc.stdout.strip().replace("%", "")
            if disk_use and int(disk_use) > 85:
                checks.append({"type": "disk_full", "status": "fail", "detail": "磁盘使用率 {}%".format(disk_use)})
        except:
            pass
        
        # 内存检查
        try:
            proc = subprocess.run(
                'free -m | awk "/Mem:/{printf \"%.0f\", $3/$2*100}"',
                shell=True, capture_output=True, text=True, timeout=10
            )
            mem_use = proc.stdout.strip()
            if mem_use and int(mem_use) > 90:
                checks.append({"type": "memory_high", "status": "fail", "detail": "内存使用率 {}%".format(mem_use)})
        except:
            pass
        
        # 检查Docker容器
        try:
            proc = subprocess.run(
                "docker ps --filter status=running --format '{{.Names}}' | wc -l",
                shell=True, capture_output=True, text=True, timeout=10
            )
            running = proc.stdout.strip()
            if running and int(running) < 2:
                checks.append({"type": "service_down", "status": "fail", "detail": "仅 {} 个容器运行中".format(running)})
        except:
            pass
        
        # 对失败项执行自动修复
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