''" -- /SSL//DB// ''"
from datetime import datetime
from fastapi import APIRouter, Depends
from auth import verify_token
from risk import handle_risk
from state import state

router = APIRouter(prefix="/agent/inspect", tags=["Inspect"])

@router.get("/full")
async def full_inspection(_=Depends(verify_token)):
    ''":+SSL++DB++''"
    await handle_risk("L1", '')
    results = {"time": datetime.now().isoformat(), "checks": [], "passed": 0, "failed": 0, "warnings": 0}

    # 1. 
    domains = state._data.get("rotation_domains", [])
    active = sum(1 for d in domains if d.get("active"))
    results["checks"].append({"name": '', "status": "pass" if active >= len(domains)*0.5 else "fail",
                              "detail": f"{active}/{len(domains)} " if domains else ''})

    # 2. SSL
    ssl_info = state._data.get("ssl_certificates", [])
    expiring = [c for c in ssl_info if c.get("days_left", 999) < 14]
    results["checks"].append({"name": "SSL", "status": "fail" if expiring else "pass",
                              "detail": f"{len(expiring)}" if expiring else f"{len(ssl_info)}"})

    # 3. 
    import psutil
    disk = psutil.disk_usage("/")
    if disk.percent > 85:
        results["checks"].append({"name": '', "status": "fail", "detail": f"{disk.percent}%"})
    elif disk.percent > 70:
        results["checks"].append({"name": '', "status": "warn", "detail": f"{disk.percent}%"})
    else:
        results["checks"].append({"name": '', "status": "pass", "detail": f"{disk.percent}%"})

    # 4. 
    mem = psutil.virtual_memory()
    if mem.percent > 85:
        results["checks"].append({"name": '', "status": "fail", "detail": f"{mem.percent}%"})
    elif mem.percent > 70:
        results["checks"].append({"name": '', "status": "warn", "detail": f"{mem.percent}%"})
    else:
        results["checks"].append({"name": '', "status": "pass", "detail": f"{mem.percent}%"})

    # 5. CPU
    cpu = psutil.cpu_percent(interval=0.5)
    if cpu > 85:
        results["checks"].append({"name": "CPU", "status": "fail", "detail": f"{cpu}%"})
    elif cpu > 70:
        results["checks"].append({"name": "CPU", "status": "warn", "detail": f"{cpu}%"})
    else:
        results["checks"].append({"name": "CPU", "status": "pass", "detail": f"{cpu}%"})

    # 6. 
    try:
        from config import DB_CONFIG
        if DB_CONFIG.get("dsn"):
            import pymysql
            conn = pymysql.connect(host=DB_CONFIG["host"], port=DB_CONFIG["port"], user=DB_CONFIG["user"],
                                   password=DB_CONFIG["password"], connect_timeout=3)
            conn.ping(); conn.close()
            results["checks"].append({"name": '', "status": "pass", "detail": ''})
        else:
            results["checks"].append({"name": '', "status": "warn", "detail": ''})
    except Exception as e:
        results["checks"].append({"name": '', "status": "fail", "detail": str(e)[:50]})

    # 7. AI
    proc_names = ["nginx", "mysql", "redis-server", "python3", "mall-api"]
    import subprocess
    for pn in proc_names:
        r = subprocess.run(["pgrep", "-x", pn], capture_output=True, timeout=3)
        if r.returncode != 0 and pn != "mall-api":
            results["checks"].append({"name": f" {pn}", "status": "warn" if pn=="mall-api" else "fail",
                                      "detail": '' if r.returncode != 0 else ''})

    # 8. 
    pending = state._data.get("pending_approvals", [])
    if len(pending) > 5:
        results["checks"].append({"name": '', "status": "warn", "detail": f"{len(pending)}"})

    for c in results["checks"]:
        if c["status"] == "pass": results["passed"] += 1
        elif c["status"] == "fail": results["failed"] += 1
        else: results["warnings"] += 1
    
    state.append_data("inspection_history", {"time": results["time"], "passed": results["passed"],
        "failed": results["failed"], "warnings": results["warnings"]}, 100)
    return {"ok": True, **results}
