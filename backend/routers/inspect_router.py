"""全站自动巡检 -- 域名/SSL/磁盘/DB/进程/安全 一键检查"""
from datetime import datetime
from fastapi import APIRouter, Depends
from auth import verify_token
from risk import handle_risk
from state import state

router = APIRouter(prefix="/agent/inspect", tags=["Inspect"])

@router.get("/full")
async def full_inspection(_=Depends(verify_token)):
    """全站巡检:域名健康+SSL+磁盘+DB+进程+安全"""
    await handle_risk("L1", "全站自动巡检")
    results = {"time": datetime.now().isoformat(), "checks": [], "passed": 0, "failed": 0, "warnings": 0}

    # 1. 域名健康
    domains = state._data.get("rotation_domains", [])
    active = sum(1 for d in domains if d.get("active"))
    results["checks"].append({"name": "域名健康", "status": "pass" if active >= len(domains)*0.5 else "fail",
                              "detail": f"{active}/{len(domains)} 在线" if domains else "无配置"})

    # 2. SSL证书
    ssl_info = state._data.get("ssl_certificates", [])
    expiring = [c for c in ssl_info if c.get("days_left", 999) < 14]
    results["checks"].append({"name": "SSL证书", "status": "fail" if expiring else "pass",
                              "detail": f"{len(expiring)}个即将到期" if expiring else f"{len(ssl_info)}个正常"})

    # 3. 磁盘
    import psutil
    disk = psutil.disk_usage("/")
    if disk.percent > 85:
        results["checks"].append({"name": "磁盘空间", "status": "fail", "detail": f"已用{disk.percent}%"})
    elif disk.percent > 70:
        results["checks"].append({"name": "磁盘空间", "status": "warn", "detail": f"已用{disk.percent}%"})
    else:
        results["checks"].append({"name": "磁盘空间", "status": "pass", "detail": f"已用{disk.percent}%"})

    # 4. 内存
    mem = psutil.virtual_memory()
    if mem.percent > 85:
        results["checks"].append({"name": "内存使用", "status": "fail", "detail": f"{mem.percent}%"})
    elif mem.percent > 70:
        results["checks"].append({"name": "内存使用", "status": "warn", "detail": f"{mem.percent}%"})
    else:
        results["checks"].append({"name": "内存使用", "status": "pass", "detail": f"{mem.percent}%"})

    # 5. CPU负载
    cpu = psutil.cpu_percent(interval=0.5)
    if cpu > 85:
        results["checks"].append({"name": "CPU负载", "status": "fail", "detail": f"{cpu}%"})
    elif cpu > 70:
        results["checks"].append({"name": "CPU负载", "status": "warn", "detail": f"{cpu}%"})
    else:
        results["checks"].append({"name": "CPU负载", "status": "pass", "detail": f"{cpu}%"})

    # 6. 数据库连接
    try:
        from config import DB_CONFIG
        if DB_CONFIG.get("dsn"):
            import pymysql
            conn = pymysql.connect(host=DB_CONFIG["host"], port=DB_CONFIG["port"], user=DB_CONFIG["user"],
                                   password=DB_CONFIG["password"], connect_timeout=3)
            conn.ping(); conn.close()
            results["checks"].append({"name": "数据库", "status": "pass", "detail": "连接正常"})
        else:
            results["checks"].append({"name": "数据库", "status": "warn", "detail": "未配置"})
    except Exception as e:
        results["checks"].append({"name": "数据库", "status": "fail", "detail": str(e)[:50]})

    # 7. AI后端进程
    proc_names = ["nginx", "mysql", "redis-server", "python3", "mall-api"]
    import subprocess
    for pn in proc_names:
        r = subprocess.run(["pgrep", "-x", pn], capture_output=True, timeout=3)
        if r.returncode != 0 and pn != "mall-api":
            results["checks"].append({"name": f"进程 {pn}", "status": "warn" if pn=="mall-api" else "fail",
                                      "detail": "未运行" if r.returncode != 0 else "运行中"})

    # 8. 审批堆积
    pending = state._data.get("pending_approvals", [])
    if len(pending) > 5:
        results["checks"].append({"name": "审批堆积", "status": "warn", "detail": f"{len(pending)}个待审批"})

    for c in results["checks"]:
        if c["status"] == "pass": results["passed"] += 1
        elif c["status"] == "fail": results["failed"] += 1
        else: results["warnings"] += 1
    # 保存历史
    state.append_data("inspection_history", {"time": results["time"], "passed": results["passed"],
        "failed": results["failed"], "warnings": results["warnings"]}, 100)
    return {"ok": True, **results}
