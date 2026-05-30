"""语义搜索 API — 自然语言搜商品/订单/日志"""
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from tools.logger import get_logger
from auth import verify_token

router = APIRouter(prefix="/agent/search", tags=["SemanticSearch"])
logger = get_logger("semantic_search")

@router.post("/products")
async def search_products(query: str = "", top_k: int = 10, _=Depends(verify_token)):
    """自然语言搜商品"""
    try:
        from db import get_db
        db = get_db()
        cursor = db.cursor()
        # 先用关键词匹配
        keywords = query.split()
        conditions = " OR ".join(["name LIKE %s" for _ in keywords])
        params = ["%" + k + "%" for k in keywords]
        cursor.execute(f"SELECT id,name,price,sales,category FROM t_mall_goods WHERE {conditions} LIMIT {top_k}", params)
        rows = cursor.fetchall()
        cols = [d[0] for d in cursor.description]
        results = [dict(zip(cols,row)) for row in rows]
        # 如结果太少，用AI理解查询意图
        if len(results) < 3:
            from agents.multi_model import ModelRouter
            resp = ModelRouter.smart_chat(messages=[{"role":"user","content":f"用户想搜: {query}。请提取关键搜索词(JSON数组):"}], mode="fast")
            import json as _json
            try:
                ai_kw = _json.loads(resp.get("content","[]") if isinstance(resp,dict) else "[]")
                for kw in ai_kw[:5]:
                    cursor.execute("SELECT id,name,price,sales,category FROM t_mall_goods WHERE name LIKE %s LIMIT 5", ["%"+kw+"%"])
                    for row in cursor.fetchall():
                        r = dict(zip(cols,row))
                        if r["id"] not in [x["id"] for x in results]:
                            results.append(r)
            except: pass
        return {"ok":True,"query":query,"results":results[:top_k],"count":len(results)}
    except Exception as e:
        return {"ok":False,"error":str(e)}

@router.post("/orders")
async def search_orders(query: str = "", _=Depends(verify_token)):
    """自然语言搜订单"""
    try:
        from agents.multi_model import ModelRouter
        resp = ModelRouter.smart_chat(messages=[{"role":"user","content":f"生成SQL查询订单表: {query}。表:t_mall_orders(id,amount,status,created_at)。只返回SELECT语句。"}], mode="fast")
        sql = resp.get("content","") if isinstance(resp,dict) else str(resp)
        sql = sql.strip().strip("`").strip("sql").strip()
        if sql.upper().startswith("SELECT"):
            from db import get_db
            db = get_db(); cursor = db.cursor()
            cursor.execute(sql + " LIMIT 20")
            cols = [d[0] for d in cursor.description]
            return {"ok":True,"query":query,"sql":sql,"results":[dict(zip(cols,row)) for row in cursor.fetchall()]}
        return {"ok":False,"error":"无法理解查询","sql":sql}
    except Exception as e:
        return {"ok":False,"error":str(e)}

@router.get("/quick")
async def quick_search(q: str = "", _=Depends(verify_token)):
    """快速综合搜索"""
    try:
        from agents.multi_model import ModelRouter
        resp = ModelRouter.smart_chat(messages=[{"role":"user","content":f"用户搜索: {q}。判断属于: product/order/log/none。返回JSON: {{\"type\":\"product\",\"keywords\":[\"kw1\"]}}"}], mode="fast")
        import json as _json
        result = _json.loads(resp.get("content","{}") if isinstance(resp,dict) else "{}")
        return {"ok":True,"intent":result.get("type","none"),"keywords":result.get("keywords",[])}
    except: return {"ok":True,"intent":"none","keywords":[]}