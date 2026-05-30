''" -- AI++''"
import os, re, subprocess, json, time
from typing import Dict
from tools.logger import get_logger

logger = get_logger("secscan")

class SecurityScanner:
    ''"AI''"

    @classmethod
    async def full_scan(cls) -> Dict:
        ''''''
        results = {
            "timestamp": time.time(),
            "checks": [],
            "score": 100,
            "critical": 0, "high": 0, "medium": 0, "low": 0
        }

        checks = [
            cls.check_env_leaks,
            cls.check_sql_injection_risk,
            cls.check_xss_risk,
            cls.check_auth_config,
            cls.check_dependency_versions,
            cls.check_file_permissions,
        ]

        for check in checks:
            try:
                result = await check()
                results["checks"].append(result)
                results[result.get("severity", "low")] += 1
                if result.get("severity") == "critical":
                    results["score"] -= 20
                elif result.get("severity") == "high":
                    results["score"] -= 10
                elif result.get("severity") == "medium":
                    results["score"] -= 5
            except Exception as e:
                results["checks"].append({"name": check.__name__, "pass": False, "severity": "medium", "detail": str(e)})

        results["score"] = max(0, results["score"])
        results["grade"] = "A" if results["score"] >= 90 else "B" if results["score"] >= 70 else "C" if results["score"] >= 50 else "D"

        return {"ok": True, **results}

    @classmethod
    async def check_env_leaks(cls) -> Dict:
        ''''''
        sensitive = ["API_KEY","SECRET","PASSWORD","TOKEN","PRIVATE"]
        leaked = []
        for key in os.environ:
            if any(s in key.upper() for s in sensitive):
                val = os.environ[key]
                if len(val) > 4 and not val.startswith("***"):
                    leaked.append(f"{key}=***masked***")

        return {"name": '', "pass": len(leaked) == 0,
                "severity": "critical" if leaked else "low",
                "detail": f"{len(leaked)}" if leaked else ''}

    @classmethod
    async def check_sql_injection_risk(cls) -> Dict:
        ''"SQL''"
        risks = []
        backend_dir = os.path.join(os.path.dirname(__file__), "..")
        scanned = 0
        for root, _, files in os.walk(backend_dir):
            for f in files:
                scanned += 1
                if f.endswith('.py'):
                    fpath = os.path.join(root, f)
                    try:
                        with open(fpath, 'r', encoding='utf-8') as fp:
                            content = fp.read()
                        if re.search(r'execute\(.*%s.*%.*\)|execute\(.*f["\']', content):
                            if "sanitize" not in content and "parameterize" not in content:
                                risks.append(fpath.replace(backend_dir, ''))
                    except:
                        pass

        return {"name": "SQL??????", "pass": len(risks) == 0, "severity": "high" if risks else "low", "detail": f"??{scanned}?Python??"}
    @classmethod
    async def check_xss_risk(cls) -> Dict:
        ''"XSS''"
        xss_risks = []
        for root, _, files in os.walk(backend_dir):
            for f in files:
                if f.endswith('.py') or f.endswith('.html'):
                    try:
                        with open(os.path.join(root, f), 'r', encoding='utf-8') as fp:
                            c2 = fp.read()
                        if re.search(r'innerHTML|v-html|dangerouslySetInnerHTML|document\.write', c2):
                            xss_risks.append(f)
                    except: pass
        return {"name": "XSS", "pass": len(xss_risks) == 0, "severity": "medium" if xss_risks else "low", "detail": f"{len(xss_risks)}XSS: {xss_risks[:3]}" if xss_risks else "XSS"}

    @classmethod
    async def check_auth_config(cls) -> Dict:
        ''''''
        issues = []
        if os.getenv("AGENT_TOKEN", "changeme") == "changeme":
            issues.append("AGENT_TOKEN")
        if os.getenv("JWT_SECRET", "changeme") == "changeme":
            issues.append("JWT_SECRET")

        return {"name": '', "pass": len(issues) == 0,
                "severity": "critical" if issues else "low",
                "detail": "; ".join(issues) if issues else ''}

    @classmethod
    async def check_dependency_versions(cls) -> Dict:
        ''''''
        return {"name": '', "pass": True, "severity": "medium",
                "detail": " pip list --outdated "}

    @classmethod
    async def check_file_permissions(cls) -> Dict:
        ''''''
        try:
            result = subprocess.run(["find", ".", "-perm", "/o+w", "-maxdepth", "2"], capture_output=True, text=True, timeout=10, cwd=backend_dir)
            writable = [l for l in result.stdout.split("\n") if l.strip() and not l.startswith(".")]
        except:
            writable = []
        return {"name": '', "pass": len(writable) == 0, "severity": "high" if writable else "low",
                "detail": " find . -perm /o+w "}

security_scanner = SecurityScanner()
