"""电商AI功能 -- 选品/客服质检/营销文案/定价/库存预测"""
import json, httpx, asyncio
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from auth import verify_token
from config import OPENAI_API_KEY, OPENAI_BASE_URL, DEEPSEEK_API_KEY

router = APIRouter(prefix="/agent/ecommerce", tags=["EcommerceAI"])

API_KEY = OPENAI_API_KEY or DEEPSEEK_API_KEY
BASE_URL = OPENAI_BASE_URL or "https://api.openai.com/v1"

async def call_ai(prompt: str, system: str = "你是一个电商专家") -> str:
    if not API_KEY:
        return f"[需要配置API Key] {system}: {prompt[:100]}..."
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            resp = await client.post(f"{BASE_URL}/chat/completions",
                headers={"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"},
                json={"model": "gpt-3.5-turbo", "messages": [
                    {"role": "system", "content": system},
                    {"role": "user", "content": prompt}
                ], "temperature": 0.7, "max_tokens": 1000})
            if resp.status_code == 200:
                return resp.json().get("choices",[{}])[0].get("message",{}).get("content", "无响应")
            return f"AI调用失败: {resp.status_code}"
    except Exception as e:
        return f"网络错误: {str(e)}"

# ===== 1. AI选品助手 =====
class ProductSelectRequest(BaseModel):
    category: str = ""
    market: str = "TikTok"
    budget: float = 0
    count: int = 5

@router.post("/product-select")
async def product_select(req: ProductSelectRequest, _=Depends(verify_token)):
    prompt = f"分析{req.market}平台'{req.category or '热门'}'品类,推荐{req.count}个跨境爆品.考虑:竞争度、利润空间、物流可行性、趋势热度.给出具体产品名称和理由."
    result = await call_ai(prompt, "你是TikTok跨境选品专家,精通东南亚和欧美市场")
    return {"ok": True, "result": result, "market": req.market}

# ===== 2. AI客服质检 =====
class CSQualityRequest(BaseModel):
    conversations: list = []  # [{role, content, time}]

@router.post("/cs-quality")
async def cs_quality_check(req: CSQualityRequest, _=Depends(verify_token)):
    if not req.conversations:
        return {"ok": False, "error": "请提供客服对话记录"}
    conv_text = "\n".join([f"{m.get('role','')}: {m.get('content','')}" for m in req.conversations])
    prompt = f"请质检以下客服对话,从响应速度、态度、专业度、问题解决率4个维度打分(1-10),给出总分和改进建议:\n\n{conv_text[:3000]}"
    result = await call_ai(prompt, "你是客服质检专家,客观公正地评估客服表现")
    return {"ok": True, "result": result}

# ===== 3. AI营销文案 =====
class CopyRequest(BaseModel):
    product_name: str
    features: str = ""
    target_audience: str = ""
    platform: str = "TikTok"
    language: str = "中文"
    style: str = "卖货"

@router.post("/marketing-copy")
async def generate_copy(req: CopyRequest, _=Depends(verify_token)):
    prompt = f"""为产品生成{req.platform}营销文案:
产品:{req.product_name}
特点:{req.features or '优质商品'}
目标人群:{req.target_audience or '年轻人'}
风格:{req.style}
语言:{req.language}
请生成:1) 爆款标题(3个) 2) 短视频口播文案 3) 卖点提炼(5条) 4) 行动号召CTA"""
    result = await call_ai(prompt, "你是跨境电商顶级文案策划,擅长TikTok爆款文案")
    return {"ok": True, "result": result}

# ===== 4. AI定价引擎 =====
class PricingRequest(BaseModel):
    product_name: str
    cost: float
    competitor_prices: list = []
    target_margin: float = 30
    market: str = ""

@router.post("/pricing")
async def ai_pricing(req: PricingRequest, _=Depends(verify_token)):
    comp_text = "\n".join([f"{c.get('name','')}: ¥{c.get('price',0)}" for c in req.competitor_prices]) if req.competitor_prices else "无竞品数据"
    prompt = f"""分析定价策略:
产品:{req.product_name}
成本:¥{req.cost}
目标利润率:{req.target_margin}%
市场:{req.market or '通用'}
竞品价格:
{comp_text}

请给出:1) 建议售价 2) 促销价 3) 阶梯定价 4) 价格竞争力分析 5) 调价建议"""
    result = await call_ai(prompt, "你是电商定价策略专家,精通价格心理学和竞争定价")
    return {"ok": True, "result": result}

# ===== 5. AI库存预测 =====
class InventoryRequest(BaseModel):
    product_name: str
    sales_history: list = []  # [{date, quantity}]
    current_stock: int = 0
    lead_time_days: int = 7

@router.post("/inventory-forecast")
async def inventory_forecast(req: InventoryRequest, _=Depends(verify_token)):
    sales_text = "\n".join([f"{s.get('date','')}: {s.get('quantity',0)}件" for s in (req.sales_history or [])[-30:]])
    if not sales_text:
        sales_text = "无历史销售数据"
    prompt = f"""分析库存补货建议:
产品:{req.product_name}
近30天销量:
{sales_text}
当前库存:{req.current_stock}件
补货周期:{req.lead_time_days}天

请给出:1) 日均销量估算 2) 建议安全库存 3) 下次补货时间 4) 补货数量 5) 库存风险预警"""
    result = await call_ai(prompt, "你是供应链管理专家,精通库存优化和需求预测")
    return {"ok": True, "result": result}

# ===== 6. AI语义搜索 =====
class SearchRequest(BaseModel):
    query: str
    category: str = ""
    limit: int = 20

@router.post("/search")
async def semantic_search(req: SearchRequest, _=Depends(verify_token)):
    prompt = f"用户想找:{req.query}(品类:{req.category or '不限'}).请理解用户意图,提取3-5个关键搜索词,用逗号分隔.只返回关键词."
    result = await call_ai(prompt, "你是电商搜索专家")
    keywords = [k.strip() for k in result.replace(',',',').split(',') if k.strip()]
    return {"ok": True, "query": req.query, "intent": result, "keywords": keywords[:5]}

# ===== 7. AI工作流 =====
class WorkflowRequest(BaseModel):
    name: str = ""
    steps: list = []  # [{action, params}]

@router.post("/workflow")
async def execute_workflow(req: WorkflowRequest, _=Depends(verify_token)):
    results = []
    for step in req.steps:
        action = step.get("action", "")
        params = step.get("params", {})
        if action == "search":
            r = await semantic_search(SearchRequest(query=params.get("query",""), category=params.get("category","")), _)
            results.append({"step": action, "result": r})
        elif action == "copy":
            r = await generate_copy(CopyRequest(**params), _)
            results.append({"step": action, "result": r})
        elif action == "analyze":
            prompt = params.get("prompt", "")
            r = await call_ai(prompt, params.get("system", "你是AI助手"))
            results.append({"step": action, "result": r})
        else:
            results.append({"step": action, "error": f"未知操作: {action}"})
    
    return {"ok": True, "workflow": req.name or "未命名", "results": results}