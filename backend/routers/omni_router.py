"""Omni API - Knowledge Graph + Business Engine + Smart Pricing"""
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import Optional
from auth import verify_token
from tools.omni_engine import KnowledgeGraph, BusinessEngine, SmartPricing, SelfHealing
from tools.logger import get_logger

logger = get_logger("omni")
router = APIRouter(prefix="/omni", tags=["Omni"])

class GraphNode(BaseModel):
    node_type: str
    node_id: str
    properties: Optional[dict] = None

class GraphEdge(BaseModel):
    from_type: str
    from_id: str
    to_type: str
    to_id: str
    relation: str

class PriceCheck(BaseModel):
    product_id: str
    our_price: float
    competitor_prices: list[float] = []

# =====  =====
@router.post("/graph/node")
async def add_graph_node(req: GraphNode, _=Depends(verify_token)):
    KnowledgeGraph.add_node(req.node_type, req.node_id, req.properties)
    return {"ok": True, "node": f"{req.node_type}:{req.node_id}"}

@router.post("/graph/edge")
async def add_graph_edge(req: GraphEdge, _=Depends(verify_token)):
    KnowledgeGraph.add_edge(req.from_type, req.from_id, req.to_type, req.to_id, req.relation)
    return {"ok": True}

@router.get("/graph/query")
async def query_graph(node_type: str, node_id: str = '', relation: str = '', _=Depends(verify_token)):
    results = KnowledgeGraph.query(node_type, node_id or None, relation or None)
    return {"ok": True, "results": results, "count": len(results)}

@router.post("/graph/build")
async def build_graph(_=Depends(verify_token)):
    ''": ''"
    try:
        from state import state
        
        products = state._data.get("products", [])
        for p in products[:100]:
            pid = p.get("id", p.get("goods_id", ''))
            KnowledgeGraph.add_node("product", str(pid), {"name": p.get("name", ''), "price": p.get("price", 0)})
        
        
        orders = state._data.get("orders", [])
        for o in orders[:100]:
            oid = o.get("id", o.get("order_id", ''))
            KnowledgeGraph.add_node("order", str(oid), {"amount": o.get("amount", 0), "time": o.get("time", '')})
            pid = o.get("product_id", o.get("goods_id", ''))
            if pid:
                KnowledgeGraph.add_edge("order", str(oid), "product", str(pid), "contains")
        
        
        users = state._data.get("users", [])
        for u in users[:50]:
            uid = u.get("id", u.get("username", ''))
            KnowledgeGraph.add_node("user", str(uid), {"role": u.get("role", '')})
        
        return {"ok": True, "nodes": len(KnowledgeGraph._nodes), "edges": len(KnowledgeGraph._edges)}
    except Exception as e:
        return {"ok": False, "error": str(e)}

# =====  =====
@router.get("/business/analyze")
async def analyze_business(_=Depends(verify_token)):
    ''''''
    try:
        from state import state
        orders = state._data.get("orders", [])
        result = BusinessEngine.analyze_sales(orders)
        return {"ok": True, **result}
    except Exception as e:
        return {"ok": False, "error": str(e)}

@router.get("/business/hot-products")
async def hot_products(limit: int = 10, _=Depends(verify_token)):
    ''''''
    try:
        from state import state, defaultdict
        orders = state._data.get("orders", [])
        sales = defaultdict(lambda: {"count": 0, "revenue": 0})
        for o in orders:
            pid = o.get("product_id", o.get("goods_id", str(o.get("id", ''))))
            sales[pid]["count"] += 1
            sales[pid]["revenue"] += float(o.get("amount", o.get("price", 0)))
        ranked = sorted(sales.items(), key=lambda x: x[1]["revenue"], reverse=True)[:limit]
        return {"ok": True, "products": [{"id": pid, **d} for pid, d in ranked]}
    except Exception as e:
        return {"ok": False, "error": str(e)}

# =====  =====
@router.post("/pricing/analyze")
async def analyze_price(req: PriceCheck, _=Depends(verify_token)):
    result = SmartPricing.analyze_competitor(req.product_id, req.our_price, req.competitor_prices)
    return {"ok": True, **result}

@router.get("/pricing/rules")
async def pricing_rules(_=Depends(verify_token)):
    SmartPricing.load_rules()
    return {"ok": True, "rules": SmartPricing._rules}

# =====  =====
@router.get("/heal/status")
async def heal_status(_=Depends(verify_token)):
    return {"ok": True, "failures": dict(SelfHealing._failure_count)}

@router.post("/heal/trigger")
async def trigger_heal(endpoint: str = "all", _=Depends(verify_token)):
    result = await SelfHealing.heal(endpoint)
    return {"ok": True, **result}

# =====  =====
class CodeRequest(BaseModel):
    requirement: str
    language: str = "python"
    file_path: str = ''

@router.post("/code/generate")
async def generate_code(req: CodeRequest, _=Depends(verify_token)):
    ''"AI -- ''"
    try:
        import httpx, os
        key = os.getenv("DEEPSEEK_API_KEY") or os.getenv("OPENAI_API_KEY")
        if not key:
            return {"ok": False, "error": "AI API Key"}
        
        prompt = f''"{req.language}.:
: {req.requirement}
: {req.file_path or ''}

.,.''"
        
        async with httpx.AsyncClient(timeout=60) as client:
            r = await client.post(
                "https://api.deepseek.com/v1/chat/completions",
                headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
                json={"model": "deepseek-chat", "messages": [{"role":"user","content":prompt}], "temperature": 0.3}
            )
            if r.status_code == 200:
                code = r.json()["choices"][0]["message"]["content"]
                
                if req.file_path:
                    with open(req.file_path, 'w', encoding='utf-8') as fh:
                        fh.write(code)
                    return {"ok": True, "saved": req.file_path, "code": code[:500]}
                return {"ok": True, "code": code}
    except Exception as e:
        return {"ok": False, "error": str(e)}

# =====  =====
@router.get("/customer/unified")
async def unified_customer_stats(_=Depends(verify_token)):
    ''''''
    return {
        "ok": True,
        "channels": {
            "web": {"active": True, "sessions": 1},
            "wechat": {"active": bool(os.getenv("WECHAT_TOKEN")), "sessions": 0},
            "wecom": {"active": bool(os.getenv("WECOM_CORP_ID")), "sessions": 0},
            "dingtalk": {"active": bool(os.getenv("DINGTALK_APP_KEY")), "sessions": 0},
            "telegram": {"active": bool(os.getenv("TELEGRAM_BOT_TOKEN")), "sessions": 0},
            "slack": {"active": bool(os.getenv("SLACK_BOT_TOKEN")), "sessions": 0},
            "line": {"active": bool(os.getenv("LINE_CHANNEL_TOKEN")), "sessions": 0},
        }
    }