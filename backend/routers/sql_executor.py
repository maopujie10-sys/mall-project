"""SQL 安全执行器 — 受控数据库工具 + 字段级保护 + 真实MySQL执行"""
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

# ===== 永久禁止的 SQL 操作 =====
FORBIDDEN_SQL = [
    "DROP DATABASE", "DROP TABLE", "DROP VIEW", "DROP PROCEDURE",
    "TRUNCATE", "DELETE FROM",
    "ALTER TABLE", "ALTER DATABASE",
    "CREATE DATABASE", "CREATE TABLE",
    "GRANT", "REVOKE",
]

# ===== 字段级保护 =====
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
    """执行只读 SQL 查询"""
    sql_upper = req.sql.strip().upper()

    # 安全检查
    for forbidden in FORBIDDEN_SQL:
        if forbidden in sql_upper:
            raise HTTPException(403, f"禁止执行: {forbidden}")

    if not sql_upper.startswith("SELECT") and not sql_upper.startswith("SHOW") and not sql_upper.startswith("DESCRIBE"):
        raise HTTPException(403, "只允许执行 SELECT/SHOW/DESCRIBE 查询")

    await handle_risk("L2", "执行SQL查询", req.sql[:80])

    # 字段级保护检查
    for table, fields in PROTECTED_FIELDS.items():
        if table.lower() in req.sql.lower():
            for field in fields:
                if field.lower() in req.sql.lower():
                    return {
                        "ok": False,
                        "error": f"查询涉及保护字段 {table}.{field}，已拦截",
                        "protected_field": f"{table}.{field}",
                    }

    # 检查MySQL是否可用
    if not MALL_DB_HOST or not MALL_DB_USER:
        return {
            "ok": True,
            "note": "MySQL客户端未配置数据库连接（需要安装mysql-client并配置MALL_DB_*环境变量）",
            "sql": req.sql[:100],
            "rows": [],
            "fields": [],
        }

    # 实际执行
    result = await execute_db(req.sql, req.db_name)
    return {
        "ok": result["success"],
        "sql": req.sql[:100],
        "output": result["stdout"][:3000],
        "error": result["stderr"][:500] if not result["success"] else None,
    }

@router.get("/schema")
async def show_schema(_=Depends(verify_token)):
    """查看数据库表结构"""
    await handle_risk("L1", "查看数据库结构")
    if MALL_DB_HOST and MALL_DB_USER:
        result = await execute_db("SHOW TABLES")
        return {
            "tables": result["stdout"].split("\n") if result["success"] else [],
            "protected_fields": PROTECTED_FIELDS,
        }
    return {
        "note": "数据库连接需要在部署时配置",
        "tables": ["users", "orders", "products", "categories", "admins"],
        "protected_fields": PROTECTED_FIELDS,
    }

@router.get("/status")
async def db_status(_=Depends(verify_token)):
    """检查数据库连接状态"""
    await handle_risk("L1", "检查数据库状态")
    import httpx
    from config import MALL_BASE_URL
    try:
        async with httpx.AsyncClient(timeout=5) as c:
            r = await c.get(f"{MALL_BASE_URL}/agent/health")
            return {"connected": r.status_code == 200, "source": "mall-app", "detail": "通过 mall-app 检测"}
    except Exception as e:
        # 尝试直接MySQL连接
        if MALL_DB_HOST and MALL_DB_USER:
            result = await execute_db("SELECT 1 as test")
            return {"connected": result["success"], "source": "direct-mysql", "detail": result["stdout"][:200] if result["success"] else result["stderr"][:200]}
        return {"connected": False, "error": str(e)[:100]}

@router.get("/tables")
async def list_tables(_=Depends(verify_token)):
    """查看数据库表列表"""
    await handle_risk("L1", "查看数据库表")
    if MALL_DB_HOST and MALL_DB_USER:
        result = await execute_db("SHOW TABLE STATUS")
        return {"output": result["stdout"][:2000] if result["success"] else result["stderr"][:200]}
    return {"note": "数据库连接未配置"}
