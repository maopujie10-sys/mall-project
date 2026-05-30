"""  SQL"""
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from tools.logger import get_logger
from auth import verify_token

router = APIRouter(prefix="/agent/text2sql", tags=["Text2SQL"])
logger = get_logger("text2sql")

class QueryRequest(BaseModel):
    question: str
    db: str = "mall"

MALL_SCHEMA = ''"
(mall):
- t_mall_goods: id, name(), price(), stock(), sales(), category(), status(), created_at
- t_mall_orders: id, goods_id, user_id, amount(), status(), created_at
- t_mall_users: id, username, role, created_at
- t_mall_seller_goods: id, goods_name, price, stock, sales, seller_id
''"

@router.post("/query")
async def text_to_sql(req: QueryRequest, _=Depends(verify_token)):
    ''"SQL''"
    try:
        from agents.multi_model import ModelRouter
        prompt = f''"{MALL_SCHEMA}
: {req.question}
MySQLSQL,SQL
: SELECT,LIMIT 100,''"
        resp = ModelRouter.smart_chat(messages=[{"role":"user","content":prompt}], mode="fast")
        sql = resp.get("content",'') if isinstance(resp,dict) else str(resp)
        sql = sql.strip().strip("'").strip("sql").strip()
        if not sql.upper().startswith("SELECT"):
            return {"ok":False,"error":"SQL","sql":sql}

        # SQL
        from db import get_db
        db = get_db()
        cursor = db.cursor()
        cursor.execute(sql)
        columns = [d[0] for d in cursor.description] if cursor.description else []
        rows = cursor.fetchall()
        data = [dict(zip(columns,row)) for row in rows]

        return {"ok":True,"sql":sql,"columns":columns,"rows":data,"count":len(data)}
    except Exception as e:
        return {"ok":False,"error":str(e)}

@router.get("/schema")
async def get_schema(_=Depends(verify_token)):
    return {"ok":True,"schema":MALL_SCHEMA}