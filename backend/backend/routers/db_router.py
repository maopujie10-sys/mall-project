''" -- ///''"
import os
import subprocess
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from auth import verify_token
from risk import handle_risk

router = APIRouter(prefix="/db", tags=["Database"])

DB_CONFIG = {}


def _init():
    if not DB_CONFIG:
        try:
            from config import MALL_DB_HOST, MALL_DB_PORT, MALL_DB_USER, MALL_DB_PASSWORD, MALL_DB_NAME
            DB_CONFIG.update({
                "host": MALL_DB_HOST, "port": MALL_DB_PORT,
                "user": MALL_DB_USER, "password": MALL_DB_PASSWORD,
                "database": MALL_DB_NAME,
            })
        except Exception:
            DB_CONFIG.update({
                "host": "127.0.0.1", "port": 3306,
                "user": "root", "password": '',
                "database": "mall",
            })


def _mysql_cmd(sql: str) -> dict:
    ''" MySQL ''"
    _init()
    try:
        cmd = [
            "mysql", f"-h{DB_CONFIG['host']}", f"-P{DB_CONFIG['port']}",
            f"-u{DB_CONFIG['user']}",
        ]
        if DB_CONFIG.get("password"):
            cmd.append(f"-p{DB_CONFIG['password']}")
        cmd += [DB_CONFIG["database"], "-e", sql]
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        if r.returncode != 0:
            return {"ok": False, "error": r.stderr.strip()[:200]}
        lines = r.stdout.strip().split("\n")
        if len(lines) < 2:
            return {"ok": True, "rows": [], "count": 0}
        headers = [h.strip() for h in lines[0].split("\t")]
        rows = []
        for line in lines[1:]:
            vals = [v.strip() for v in line.split("\t")]
            rows.append(dict(zip(headers, vals)))
        return {"ok": True, "rows": rows, "count": len(rows)}
    except subprocess.TimeoutExpired:
        return {"ok": False, "error": ''}
    except FileNotFoundError:
        return {"ok": False, "error": "mysql "}
    except Exception as e:
        return {"ok": False, "error": str(e)}


@router.get("/status")
async def db_status(_=Depends(verify_token)):
    ''''''
    await handle_risk("L1", '')
    _init()
    info = _mysql_cmd("SHOW GLOBAL STATUS LIKE 'Uptime'')
    vars = _mysql_cmd("SHOW VARIABLES LIKE 'max_connections'')
    size = _mysql_cmd(
        "SELECT table_schema AS db, ROUND(SUM(data_length+index_length)/1024/1024,1) AS size_mb, ''COUNT(*) AS tables FROM information_schema.tables GROUP BY table_schema"
    )
    
    try:
        import psutil
        conn_count = 0
        for c in psutil.net_connections():
            if c.laddr.port == int(DB_CONFIG.get("port", 3306)):
                conn_count += 1
    except Exception:
        conn_count = 0
    return {
        "ok": True,
        "host": DB_CONFIG["host"],
        "port": DB_CONFIG["port"],
        "version": _mysql_cmd("SELECT VERSION() AS v").get("rows", [{}])[0].get("v", '') if _mysql_cmd("SELECT VERSION() AS v").get("ok") else '',
        "uptime_seconds": info.get("rows", [{}])[0].get("Value", 0) if info.get("ok") else 0,
        "max_connections": vars.get("rows", [{}])[0].get("Value", 151) if vars.get("ok") else 151,
        "active_connections": conn_count,
        "databases": size.get("rows", []) if size.get("ok") else [],
    }


@router.get("/tables")
async def db_tables(_=Depends(verify_token)):
    ''''''
    await handle_risk("L1", '')
    _init()
    result = _mysql_cmd(
        "SELECT TABLE_NAME AS name, ENGINE AS engine, ''ROUND((DATA_LENGTH+INDEX_LENGTH)/1024/1024,2) AS size_mb, ''TABLE_ROWS AS rows, CREATE_TIME AS created ''FROM information_schema.tables WHERE table_schema='{db}''
        "ORDER BY size_mb DESC".format(db=DB_CONFIG["database"])
    )
    return {"ok": result.get("ok", False), "tables": result.get("rows", []), "count": result.get("count", 0)}
