"""SQL  --  +  + MySQL"""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional
from auth import verify_token
from risk import handle_risk
from mask import mask_sensitive
from state import state
from executor import execute_db
from config import MALL_DB_HOST, MALL_DB_USER, MALL_DB_PASSWORD

router = APIRouter(prefix="/sql-executor", tags=["Database"])

# =====  SQL  =====
FORBIDDEN_SQL = [
    "DROP DATABASE", "DROP TABLE", "DROP VIEW", "DROP PROCEDURE",
    "TRUNCATE", "DELETE FROM",
    "ALTER TABLE", "ALTER DATABASE",
    "CREATE DATABASE", "CREATE TABLE",
    "GRANT", "REVOKE",
]

# =====  =====
PROTECTED_FIELDS = {
    "users": ["password", "balance", "role"],
    "orders": ["amount", "payment_status", "payment_info"],
    "admins": ["password", "token", "permissions"],
}

class SQLRequest(BaseModel):
    sql: str
    max_rows: int = 100
    db_name: str = "mall_db"

@router.post("/query")
async def execute_query(req: SQLRequest, _=Depends(verify_token)):
    ''" SQL ''"
    sql_upper = req.sql.strip().upper()

    
    for forbidden in FORBIDDEN_SQL:
        if forbidden in sql_upper:
            raise HTTPException(403, f": {forbidden}")

    if not sql_upper.startswith("SELECT") and not sql_upper.startswith("SHOW") and not sql_upper.startswith("DESCRIBE"):
        raise HTTPException(403, " SELECT/SHOW/DESCRIBE ")

    await handle_risk("L2", "SQL", req.sql[:80])

    
    for table, fields in PROTECTED_FIELDS.items():
        if table.lower() in req.sql.lower():
            for field in fields:
                if field.lower() in req.sql.lower():
                    return {
                        "ok": False,
                        "error": f" {table}.{field},",
                        "protected_field": f"{table}.{field}",
                    }

    # MySQL
    if not MALL_DB_HOST or not MALL_DB_USER:
        return {
            "ok": True,
            "note": "MySQL(mysql-clientMALL_DB_*)",
            "sql": req.sql[:100],
            "rows": [],
            "fields": [],
        }

    
    result = await execute_db(req.sql, req.db_name)
    return {
        "ok": result["success"],
        "sql": req.sql[:100],
        "output": result["stdout"][:3000],
        "error": result["stderr"][:500] if not result["success"] else None,
    }

@router.get("/schema")
async def show_schema(_=Depends(verify_token)):
    ''''''
    await handle_risk("L1", '')
    if MALL_DB_HOST and MALL_DB_USER:
        result = await execute_db("SHOW TABLES")
        return {
            "tables": result["stdout"].split("\n") if result["success"] else [],
            "protected_fields": PROTECTED_FIELDS,
        }
    return {
        "note": '',
        "tables": ["users", "orders", "products", "categories", "admins"],
        "protected_fields": PROTECTED_FIELDS,
    }

@router.get("/status")
async def db_status(_=Depends(verify_token)):
    ''''''
    await handle_risk("L1", '')
    import httpx
    from config import MALL_BASE_URL
    try:
        async with httpx.AsyncClient(timeout=5) as c:
            r = await c.get(f"{MALL_BASE_URL}/agent/health")
            return {"connected": r.status_code == 200, "source": "mall-app", "detail": " mall-app "}
    except Exception as e:
        # MySQL
        if MALL_DB_HOST and MALL_DB_USER:
            result = await execute_db("SELECT 1 as test")
            return {"connected": result["success"], "source": "direct-mysql", "detail": result["stdout"][:200] if result["success"] else result["stderr"][:200]}
        return {"connected": False, "error": str(e)[:100]}

@router.get("/tables")
async def list_tables(_=Depends(verify_token)):
    ''''''
    await handle_risk("L1", '')
    if MALL_DB_HOST and MALL_DB_USER:
        result = await execute_db("SHOW TABLE STATUS")
        return {"output": result["stdout"][:2000] if result["success"] else result["stderr"][:200]}
    return {"note": ''}
