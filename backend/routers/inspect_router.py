锘?""鍏ㄧ珯鑷姩宸℃ 鈥?鍩熷悕/SSL/纾佺洏/DB/杩涚▼/瀹夊叏 涓€閿鏌?""
from datetime import datetime
from fastapi import APIRouter, Depends
from auth import verify_token
from risk import handle_risk
from state import state

router = APIRouter(prefix="/agent/inspect", tags=["Inspect"])

@router.get("/full")
async def full_inspection(_=Depends(verify_token)):
    """鍏ㄧ珯宸℃锛氬煙鍚嶅仴搴?SSL+纾佺洏+DB+杩涚▼+瀹夊叏"""
    await handle_risk("L1", "鍏ㄧ珯鑷姩宸℃")
    results = {"time": datetime.now().isoformat(), "checks": [], "passed": 0, "failed": 0, "warnings": 0}

    # 1. 鍩熷悕鍋ュ悍
    domains = state._data.get("rotation_domains", [])
    active = sum(1 for d in domains if d.get("active"))
    results["checks"].append({"name": "鍩熷悕鍋ュ悍", "status": "pass" if active >= len(domains)*0.5 else "fail",
                              "detail": f"{active}/{len(domains)} 鍦ㄧ嚎" if domains else "鏃犻厤缃?})

    # 2. SSL璇佷功
    ssl_info = state._data.get("ssl_certificates", [])
    expiring = [c for c in ssl_info if c.get("days_left", 999) < 14]
    results["checks"].append({"name": "SSL璇佷功", "status": "fail" if expiring else "pass",
                              "detail": f"{len(expiring)}涓嵆灏嗗埌鏈? if expiring else f"{len(ssl_info)}涓甯?})

    # 3. 纾佺洏
    import psutil
    disk = psutil.disk_usage("/")
    if disk.percent > 85:
        results["checks"].append({"name": "纾佺洏绌洪棿", "status": "fail", "detail": f"宸茬敤{disk.percent}%"})
    elif disk.percent > 70:
        results["checks"].append({"name": "纾佺洏绌洪棿", "status": "warn", "detail": f"宸茬敤{disk.percent}%"})
    else:
        results["checks"].append({"name": "纾佺洏绌洪棿", "status": "pass", "detail": f"宸茬敤{disk.percent}%"})

    # 4. 鍐呭瓨
    mem = psutil.virtual_memory()
    if mem.percent > 85:
        results["checks"].append({"name": "鍐呭瓨浣跨敤", "status": "fail", "detail": f"{mem.percent}%"})
    elif mem.percent > 70:
        results["checks"].append({"name": "鍐呭瓨浣跨敤", "status": "warn", "detail": f"{mem.percent}%"})
    else:
        results["checks"].append({"name": "鍐呭瓨浣跨敤", "status": "pass", "detail": f"{mem.percent}%"})

    # 5. CPU璐熻浇
    cpu = psutil.cpu_percent(interval=0.5)
    if cpu > 85:
        results["checks"].append({"name": "CPU璐熻浇", "status": "fail", "detail": f"{cpu}%"})
    elif cpu > 70:
        results["checks"].append({"name": "CPU璐熻浇", "status": "warn", "detail": f"{cpu}%"})
    else:
        results["checks"].append({"name": "CPU璐熻浇", "status": "pass", "detail": f"{cpu}%"})

    # 6. 鏁版嵁搴撹繛鎺?    try:
        from config import DB_CONFIG
        if DB_CONFIG.get("dsn"):
            import pymysql
            conn = pymysql.connect(host=DB_CONFIG["host"], port=DB_CONFIG["port"], user=DB_CONFIG["user"],
                                   password=DB_CONFIG["password"], connect_timeout=3)
            conn.ping(); conn.close()
            results["checks"].append({"name": "鏁版嵁搴?, "status": "pass", "detail": "杩炴帴姝ｅ父"})
        else:
            results["checks"].append({"name": "鏁版嵁搴?, "status": "warn", "detail": "鏈厤缃?})
    except Exception as e:
        results["checks"].append({"name": "鏁版嵁搴?, "status": "fail", "detail": str(e)[:50]})

    # 7. AI鍚庣杩涚▼
    proc_names = ["nginx", "mysql", "redis-server", "python3", "mall-api"]
    import subprocess
    for pn in proc_names:
        r = subprocess.run(["pgrep", "-x", pn], capture_output=True, timeout=3)
        if r.returncode != 0 and pn != "mall-api":
            results["checks"].append({"name": f"杩涚▼ {pn}", "status": "warn" if pn=="mall-api" else "fail",
                                      "detail": "鏈繍琛? if r.returncode != 0 else "杩愯涓?})

    # 8. 瀹℃壒鍫嗙Н
    pending = state._data.get("pending_approvals", [])
    if len(pending) > 5:
        results["checks"].append({"name": "瀹℃壒鍫嗙Н", "status": "warn", "detail": f"{len(pending)}涓緟瀹℃壒"})

    for c in results["checks"]:
        if c["status"] == "pass": results["passed"] += 1
        elif c["status"] == "fail": results["failed"] += 1
        else: results["warnings"] += 1
    # 淇濆瓨鍘嗗彶
    state.append_data("inspection_history", {"time": results["time"], "passed": results["passed"],
        "failed": results["failed"], "warnings": results["warnings"]}, 100)
    return {"ok": True, **results}
