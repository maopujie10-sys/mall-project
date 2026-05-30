"""AI电商引擎 — 选品/客服质检/营销文案/定价/库存预测"""
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import List, Optional
from tools.logger import get_logger
from auth import verify_token

router = APIRouter(prefix="/agent/ecommerce", tags=["EcommerceAI"])
logger = get_logger("ecommerce")

# ===== 1. AI选品助手 =====
@router.post("/product/select")
async def ai_product_selection(category: str = "", trend: str = "", budget: float = 0, _=Depends(verify_token)):
    """AI选品 — 分析TikTok趋势推荐跨境爆品"""
    try:
        from agents.multi_model import ModelRouter
        prompt = f"""你是一个跨境电商选品专家。请分析以下信息推荐5个爆品:
品类: {category or "全品类"}
趋势: {trend or "TikTok热榜"}
预算: {budget or "不限"}
返回JSON: [{{"name":"商品名","reason":"推荐理由","price_range":"价格区间","competition":"竞争度","score":85}}]"""
        resp = ModelRouter.smart_chat(messages=[{"role":"user","content":prompt}], mode="smart")
        import json as _json
        products = _json.loads(resp.get("content","[]") if isinstance(resp,dict) else "[]")
        return {"ok":True,"recommendations":products,"category":category}
    except Exception as e:
        return {"ok":False,"error":str(e)}

# ===== 2. AI客服质检 =====
@router.post("/customer/qa")
async def ai_customer_qa(conversations: List[dict] = [], _=Depends(verify_token)):
    """AI客服质检 — 审查对话+打分+改进建议"""
    if not conversations:
        return {"ok":False,"error":"请提供对话记录"}
    try:
        from agents.multi_model import ModelRouter
        conv_text = "\n".join([f"{c.get('role','')}: {c.get('content','')}" for c in conversations[:20]])
        prompt = f"""审查以下客服对话并评分(1-100):
{conv_text}
返回JSON: {{"score":85,"good":["优点1"],"bad":["问题1"],"suggestions":["改进建议1"],"sentiment":"positive"}}"""
        resp = ModelRouter.smart_chat(messages=[{"role":"user","content":prompt}], mode="smart")
        import json as _json
        result = _json.loads(resp.get("content","{}") if isinstance(resp,dict) else "{}")
        return {"ok":True,"qa_result":result}
    except Exception as e:
        return {"ok":False,"error":str(e)}

# ===== 3. AI营销文案 =====
@router.post("/marketing/copy")
async def ai_marketing_copy(product: dict = {}, platform: str = "tiktok", lang: str = "zh", _=Depends(verify_token)):
    """AI营销文案 — 商品图→多语言标题/描述/卖点"""
    try:
        from agents.multi_model import ModelRouter
        prompt = f"""为以下商品生成{platform}平台的{'中文'if lang=='zh'else'英文'}营销文案:
商品: {product.get('name','')}
价格: {product.get('price','')}
特点: {product.get('features','')}
返回JSON: {{"title":"标题","description":"描述(200字)","hashtags":["#tag1"],"selling_points":["卖点1"]}}"""
        resp = ModelRouter.smart_chat(messages=[{"role":"user","content":prompt}], mode="creative")
        import json as _json
        content = _json.loads(resp.get("content","{}") if isinstance(resp,dict) else "{}")
        return {"ok":True,"copy":content,"platform":platform}
    except Exception as e:
        return {"ok":False,"error":str(e)}

# ===== 4. AI定价引擎 =====
@router.post("/pricing/optimize")
async def ai_pricing_engine(product: dict = {}, competitor_prices: List[float] = [], _=Depends(verify_token)):
    """AI定价 — 竞品价格监控+自动调价策略"""
    try:
        from agents.multi_model import ModelRouter
        prompt = f"""分析定价策略:
商品成本: {product.get('cost',0)}
当前售价: {product.get('price',0)}
竞品价格: {competitor_prices[:5]}
返回JSON: {{"optimal_price":99,"strategy":"penetration/premium/competitive","reason":"理由","margin_percent":35}}"""
        resp = ModelRouter.smart_chat(messages=[{"role":"user","content":prompt}], mode="smart")
        import json as _json
        strategy = _json.loads(resp.get("content","{}") if isinstance(resp,dict) else "{}")
        return {"ok":True,"pricing":strategy}
    except Exception as e:
        return {"ok":False,"error":str(e)}

# ===== 5. AI库存预测 =====
@router.post("/inventory/predict")
async def ai_inventory_predict(product_id: str = "", sales_history: List[int] = [], days: int = 30, _=Depends(verify_token)):
    """AI库存预测 — 销量趋势+季节性预测补货"""
    try:
        from agents.multi_model import ModelRouter
        prompt = f"""基于销量历史预测未来{days}天库存需求:
销量历史: {sales_history[-30:]}
返回JSON: {{"forecast":[[day1,qty1]],"total_demand":500,"reorder_point":100,"suggestion":"建议X天后补货"}}"""
        resp = ModelRouter.smart_chat(messages=[{"role":"user","content":prompt}], mode="smart")
        import json as _json
        forecast = _json.loads(resp.get("content","{}") if isinstance(resp,dict) else "{}")
        return {"ok":True,"forecast":forecast}
    except Exception as e:
        return {"ok":False,"error":str(e)}

# ===== 6. 一键智能上架 =====
@router.post("/product/smart-list")
async def ai_smart_listing(product_info: dict = {}, _=Depends(verify_token)):
    """AI智能上架 — 自动生成全套商品信息"""
    try:
        from agents.multi_model import ModelRouter
        prompt = f"""为商品生成完整上架信息:
基本信息: {product_info}
返回JSON: {{"title":"SEO标题","description":"详细描述","price_suggestion":99,"category":"建议品类","tags":["tag1"],"images_suggestion":["需要XX类型图片"]}}"""
        resp = ModelRouter.smart_chat(messages=[{"role":"user","content":prompt}], mode="creative")
        import json as _json
        listing = _json.loads(resp.get("content","{}") if isinstance(resp,dict) else "{}")
        return {"ok":True,"listing":listing}
    except Exception as e:
        return {"ok":False,"error":str(e)}