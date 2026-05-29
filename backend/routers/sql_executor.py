"""SQL 瀹夊叏鎵ц鍣?鈥?鍙楁帶鏁版嵁搴撳伐鍏?+ 瀛楁绾т繚鎶?+ 鐪熷疄MySQL鎵ц"""
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

# ===== 姘镐箙绂佹鐨?SQL 鎿嶄綔 =====
FORBIDDEN_SQL = [
    "DROP DATABASE", "DROP TABLE", "DROP VIEW", "DROP PROCEDURE",
    "TRUNCATE", "DELETE FROM",
    "ALTER TABLE", "ALTER DATABASE",
    "CREATE DATABASE", "CREATE TABLE",
    "GRANT", "REVOKE",
]

# ===== 瀛楁绾т繚鎶?=====
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
    """鎵ц鍙 SQL 鏌ヨ"""
    sql_upper = req.sql.strip().upper()

    # 瀹夊叏妫€鏌?    for forbidden in FORBIDDEN_SQL:
        if forbidden in sql_upper:
            raise HTTPException(403, f"绂佹鎵ц: {forbidden}")

    if not sql_upper.startswith("SELECT") and not sql_upper.startswith("SHOW") and not sql_upper.startswith("DESCRIBE"):
        raise HTTPException(403, "鍙厑璁告墽琛?SELECT/SHOW/DESCRIBE 鏌ヨ")

    await handle_risk("L2", "鎵цSQL鏌ヨ", req.sql[:80])

    # 瀛楁绾т繚鎶ゆ鏌?    for table, fields in PROTECTED_FIELDS.items():
        if table.lower() in req.sql.lower():
            for field in fields:
                if field.lower() in req.sql.lower():
                    return {
                        "ok": False,
                        "error": f"鏌ヨ娑夊強淇濇姢瀛楁 {table}.{field}锛屽凡鎷︽埅",
                        "protected_field": f"{table}.{field}",
                    }

    # 妫€鏌ySQL鏄惁鍙敤
    if not MALL_DB_HOST or not MALL_DB_USER:
        return {
            "ok": True,
            "note": "MySQL瀹㈡埛绔湭閰嶇疆鏁版嵁搴撹繛鎺ワ紙闇€瑕佸畨瑁卪ysql-client骞堕厤缃甅ALL_DB_*鐜鍙橀噺锛?,
            "sql": req.sql[:100],
            "rows": [],
            "fields": [],
        }

    # 瀹為檯鎵ц
    result = await execute_db(req.sql, req.db_name)
    return {
        "ok": result["success"],
        "sql": req.sql[:100],
        "output": result["stdout"][:3000],
        "error": result["stderr"][:500] if not result["success"] else None,
    }

@router.get("/schema")
async def show_schema(_=Depends(verify_token)):
    """鏌ョ湅鏁版嵁搴撹〃缁撴瀯"""
    await handle_risk("L1", "鏌ョ湅鏁版嵁搴撶粨鏋?)
    if MALL_DB_HOST and MALL_DB_USER:
        result = await execute_db("SHOW TABLES")
        return {
            "tables": result["stdout"].split("\n") if result["success"] else [],
            "protected_fields": PROTECTED_FIELDS,
        }
    return {
        "note": "鏁版嵁搴撹繛鎺ラ渶瑕佸湪閮ㄧ讲鏃堕厤缃?,
        "tables": ["users", "orders", "products", "categories", "admins"],
        "protected_fields": PROTECTED_FIELDS,
    }

@router.get("/status")
async def db_status(_=Depends(verify_token)):
    """妫€鏌ユ暟鎹簱杩炴帴鐘舵€?""
    await handle_risk("L1", "妫€鏌ユ暟鎹簱鐘舵€?)
    import httpx
    from config import MALL_BASE_URL
    try:
        async with httpx.AsyncClient(timeout=5) as c:
            r = await c.get(f"{MALL_BASE_URL}/agent/health")
            return {"connected": r.status_code == 200, "source": "mall-app", "detail": "閫氳繃 mall-app 妫€娴?}
    except Exception as e:
        # 灏濊瘯鐩存帴MySQL杩炴帴
        if MALL_DB_HOST and MALL_DB_USER:
            result = await execute_db("SELECT 1 as test")
            return {"connected": result["success"], "source": "direct-mysql", "detail": result["stdout"][:200] if result["success"] else result["stderr"][:200]}
        return {"connected": False, "error": str(e)[:100]}

@router.get("/tables")
async def list_tables(_=Depends(verify_token)):
    """鏌ョ湅鏁版嵁搴撹〃鍒楄〃"""
    await handle_risk("L1", "鏌ョ湅鏁版嵁搴撹〃")
    if MALL_DB_HOST and MALL_DB_USER:
        result = await execute_db("SHOW TABLE STATUS")
        return {"output": result["stdout"][:2000] if result["success"] else result["stderr"][:200]}
    return {"note": "鏁版嵁搴撹繛鎺ユ湭閰嶇疆"}
