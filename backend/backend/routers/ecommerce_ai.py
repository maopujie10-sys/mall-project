''"AI  ////''"
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import List, Optional
from tools.logger import get_logger
from auth import verify_token

router = APIRouter(prefix="/agent/ecommerce", tags=["EcommerceAI"])
logger = get_logger("ecommerce")

# ===== 1. AI =====
@router.post("/product/select")
async def ai_product_selection(category: str = '', trend: str = '', budget: float = 0, _=Depends(verify_token)):
    ''"AI  TikTok''"
    try:
        from agents.multi_model import ModelRouter
        prompt = f''"5:
: {category or ''}
: {trend or "TikTok"}
: {budget or ''}
JSON: [{{"name":'',"reason":'',"price_range":'',"competition":'',"score":85}}]''"
        resp = ModelRouter.smart_chat(messages=[{"role":"user","content":prompt}], mode="smart")
        import json as _json
        products = _json.loads(resp.get("content","[]") if isinstance(resp,dict) else "[]")
        return {"ok":True,"recommendations":products,"category":category}
    except Exception as e:
        return {"ok":False,"error":str(e)}

# ===== 2. AI =====
@router.post("/customer/qa")
async def ai_customer_qa(conversations: List[dict] = [], _=Depends(verify_token)):
    ''"AI  ++''"
    if not conversations:
        return {"ok":False,"error":''}
    try:
        from agents.multi_model import ModelRouter
        conv_text = "\n".join([f"{c.get('role','')}: {c.get('content','')}" for c in conversations[:20]])
        prompt = f''"(1-100):
{conv_text}
JSON: {{"score":85,"good":["1"],"bad":["1"],"suggestions":["1"],"sentiment":"positive"}}''"
        resp = ModelRouter.smart_chat(messages=[{"role":"user","content":prompt}], mode="smart")
        import json as _json
        result = _json.loads(resp.get("content","{}") if isinstance(resp,dict) else "{}")
        return {"ok":True,"qa_result":result}
    except Exception as e:
        return {"ok":False,"error":str(e)}

# ===== 3. AI =====
@router.post("/marketing/copy")
async def ai_marketing_copy(product: dict = {}, platform: str = "tiktok", lang: str = "zh", _=Depends(verify_token)):
    ''"AI  //''"
    try:
        from agents.multi_model import ModelRouter
        prompt = f''"{platform}{''if lang=='zh'else''}:
: {product.get('name','')}
: {product.get('price','')}
: {product.get('features','')}
JSON: {{"title":'',"description":"(200)","hashtags":["#tag1"],"selling_points":["1"]}}''"
        resp = ModelRouter.smart_chat(messages=[{"role":"user","content":prompt}], mode="creative")
        import json as _json
        content = _json.loads(resp.get("content","{}") if isinstance(resp,dict) else "{}")
        return {"ok":True,"copy":content,"platform":platform}
    except Exception as e:
        return {"ok":False,"error":str(e)}

# ===== 4. AI =====
@router.post("/pricing/optimize")
async def ai_pricing_engine(product: dict = {}, competitor_prices: List[float] = [], _=Depends(verify_token)):
    ''"AI  +''"
    try:
        from agents.multi_model import ModelRouter
        prompt = f''":
: {product.get('cost',0)}
: {product.get('price',0)}
: {competitor_prices[:5]}
JSON: {{"optimal_price":99,"strategy":"penetration/premium/competitive","reason":'',"margin_percent":35}}''"
        resp = ModelRouter.smart_chat(messages=[{"role":"user","content":prompt}], mode="smart")
        import json as _json
        strategy = _json.loads(resp.get("content","{}") if isinstance(resp,dict) else "{}")
        return {"ok":True,"pricing":strategy}
    except Exception as e:
        return {"ok":False,"error":str(e)}

# ===== 5. AI =====
@router.post("/inventory/predict")
async def ai_inventory_predict(product_id: str = '', sales_history: List[int] = [], days: int = 30, _=Depends(verify_token)):
    ''"AI  +''"
    try:
        from agents.multi_model import ModelRouter
        prompt = f''"{days}:
: {sales_history[-30:]}
JSON: {{"forecast":[[day1,qty1]],"total_demand":500,"reorder_point":100,"suggestion":"X"}}''"
        resp = ModelRouter.smart_chat(messages=[{"role":"user","content":prompt}], mode="smart")
        import json as _json
        forecast = _json.loads(resp.get("content","{}") if isinstance(resp,dict) else "{}")
        return {"ok":True,"forecast":forecast}
    except Exception as e:
        return {"ok":False,"error":str(e)}

# ===== 6.  =====
@router.post("/product/smart-list")
async def ai_smart_listing(product_info: dict = {}, _=Depends(verify_token)):
    ''"AI  ''"
    try:
        from agents.multi_model import ModelRouter
        prompt = f''":
: {product_info}
JSON: {{"title":"SEO","description":'',"price_suggestion":99,"category":'',"tags":["tag1"],"images_suggestion":["XX"]}}''"
        resp = ModelRouter.smart_chat(messages=[{"role":"user","content":prompt}], mode="creative")
        import json as _json
        listing = _json.loads(resp.get("content","{}") if isinstance(resp,dict) else "{}")
        return {"ok":True,"listing":listing}
    except Exception as e:
        return {"ok":False,"error":str(e)}