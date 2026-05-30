"""自然语言查库 — 中文→SQL→执行→结果"""
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from tools.logger import get_logger
from auth import verify_token

router = APIRouter(prefix="/agent/text2sql", tags=["Text2SQL"])
logger = get_logger("text2sql")

class QueryRequest(BaseModel):
    question: str
    db: str = "mall"

MALL_SCHEMA = """
数据库表结构(mall库):
- t_mall_goods: id, name(商品名), price(价格), stock(库存), sales(销量), category(品类), status(状态), created_at
- t_mall_orders: id, goods_id, user_id, amount(金额), status(状态), created_at
- t_mall_users: id, username, role, created_at
- t_mall_seller_goods: id, goods_name, price, stock, sales, seller_id
"""

@router.post("/query")
async def text_to_sql(req: QueryRequest, _=Depends(verify_token)):
    """中文问题转SQL查询"""
    try:
        from agents.multi_model import ModelRouter
        prompt = f"""{MALL_SCHEMA}
用户问题: {req.question}
请生成一条MySQL查询SQL,只返回SQL不要解释。
要求: 使用SELECT语句,加LIMIT 100,只用上述表中的字段。"""
        resp = ModelRouter.smart_chat(messages=[{"role":"user","content":prompt}], mode="fast")
        sql = resp.get("content","") if isinstance(resp,dict) else str(resp)
        sql = sql.strip().strip("`").strip("sql").strip()
        if not sql.upper().startswith("SELECT"):
            return {"ok":False,"error":"生成的SQL无效","sql":sql}

        # 执行SQL
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