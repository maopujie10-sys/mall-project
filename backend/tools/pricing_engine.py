"""AI智能定价引擎 — 竞品分析+成本计算+AI推荐定价+价格历史追踪"""
import json, os, httpx
from datetime import datetime
from dataclasses import dataclass, field
from typing import Optional
from tools.logger import get_logger

logger = get_logger("pricing_engine")

DEEPSEEK_KEY = os.getenv("DEEPSEEK_API_KEY", "")
OPENAI_KEY = os.getenv("OPENAI_API_KEY", "")
AI_BASE_URL = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
AI_MODEL = os.getenv("AI_MODEL", "deepseek-chat")

# 类目利润率基准
CATEGORY_MARGIN = {
    "服装": 0.45, "鞋包": 0.40, "配饰": 0.50, "美妆": 0.35,
    "3C数码": 0.12, "家居": 0.30, "玩具": 0.35, "运动": 0.28,
    "食品": 0.20, "母婴": 0.30, "汽车": 0.25, "办公": 0.22,
    "宠物": 0.35, "图书": 0.15, "乐器": 0.30, "其他": 0.30,
}

# 竞争强度调整系数
COMPETITION_ADJUST = {
    "low": 1.15,     # 竞争低 → 加价15%
    "medium": 1.00,  # 正常
    "high": 0.88,    # 竞争高 → 降价12%
    "extreme": 0.80, # 极度竞争 → 降价20%
}

@dataclass
class PriceRecommendation:
    product_id: str
    product_name: str
    cost_price: float
    competitor_avg: float
    competitor_min: float
    competitor_max: float
    competitor_count: int
    recommended_price: float
    profit_margin: float
    profit_amount: float
    competition_level: str
    ai_reasoning: str
    confidence: float
    alternatives: list = field(default_factory=list)
    created_at: str = ""


class PricingEngine:
    """AI驱动的智能定价引擎"""

    @classmethod
    async def analyze_competitors(cls, product_name: str, category: str = "其他") -> dict:
        """分析竞品价格 — 从已采集数据+实时搜索"""
        from state import state
        products = state._data.get("scraped_products", [])

        # 从已采集数据匹配
        matches = []
        keywords = product_name.lower().split()[:3]
        for p in products:
            p_name = p.get("name", "").lower()
            p_price = float(p.get("price", 0) or 0)
            if p_price > 0 and any(kw in p_name for kw in keywords if len(kw) > 1):
                matches.append(p)

        if not matches and any(kw in product_name.lower() for kw in ["手机","电脑","衣服","鞋子"]):
            matches = [p for p in products if float(p.get("price", 0) or 0) > 0][:20]

        prices = [float(p.get("price", 0)) for p in matches if float(p.get("price", 0)) > 0]

        if not prices:
            return {
                "avg": 0, "min": 0, "max": 0, "count": 0,
                "level": "unknown", "samples": []
            }

        prices_sorted = sorted(prices)
        avg = sum(prices) / len(prices)
        variance = sum((p - avg) ** 2 for p in prices) / max(len(prices), 1)

        # 竞争强度判断
        if len(prices) < 5:
            level = "low"
        elif variance < avg * 0.1:
            level = "extreme"
        elif variance < avg * 0.3:
            level = "high"
        else:
            level = "medium"

        return {
            "avg": round(avg, 2),
            "min": round(prices_sorted[0], 2),
            "max": round(prices_sorted[-1], 2),
            "count": len(prices),
            "level": level,
            "samples": [{"name": m.get("name",""), "price": m.get("price",0)}
                       for m in matches[:5]]
        }

    @classmethod
    def calculate_cost_price(cls, supply_price: float, shipping: float = 0,
                              platform_fee_rate: float = 0.08, packaging: float = 0,
                              labor: float = 0) -> float:
        """计算真实成本价"""
        platform_fee = supply_price * platform_fee_rate
        return round(supply_price + shipping + platform_fee + packaging + labor, 2)

    @classmethod
    async def recommend_price(cls, product_id: str, product_name: str,
                               supply_price: float, category: str = "其他",
                               shipping: float = 0, packaging: float = 0,
                               target_margin: Optional[float] = None,
                               min_price: Optional[float] = None,
                               max_price: Optional[float] = None) -> PriceRecommendation:
        """AI综合推荐定价"""
        # 1. 计算成本
        cost = cls.calculate_cost_price(supply_price, shipping, packaging=packaging)
        base_margin = target_margin or CATEGORY_MARGIN.get(category, 0.30)

        # 2. 分析竞品
        competitor = await cls.analyze_competitors(product_name, category)

        # 3. 基础定价 = 成本 / (1 - 利润率)
        base_price = round(cost / max(1 - base_margin, 0.01), 2)

        # 4. 竞品调整
        comp_adjust = COMPETITION_ADJUST.get(competitor["level"], 1.0)
        market_price = round(base_price * comp_adjust, 2)

        # 5. 竞品锚定
        if competitor["avg"] > 0:
            if market_price > competitor["max"] * 1.3:
                market_price = round(competitor["max"] * 1.15, 2)
            elif market_price < competitor["min"] * 0.7:
                market_price = round(competitor["min"] * 0.85, 2)

        # 6. 价格边界
        if min_price and market_price < min_price:
            market_price = min_price
        if max_price and market_price > max_price:
            market_price = max_price

        # 确保有利润
        if market_price < cost * 1.05:
            market_price = round(cost * 1.08, 2)

        profit = round(market_price - cost, 2)
        margin = round(profit / market_price, 3) if market_price > 0 else 0

        # 7. AI推理 — 给出定价理由
        ai_reasoning = await cls._ai_price_reasoning(
            product_name, category, cost, market_price, competitor, margin
        )

        # 8. 备选方案
        alternatives = [
            {"strategy": "保守低价", "price": round(market_price * 0.92, 2),
             "margin": round(1 - cost / max(market_price * 0.92, 0.01), 3),
             "note": "适合冲销量/清库存"},
            {"strategy": "品质高价", "price": round(market_price * 1.12, 2),
             "margin": round(1 - cost / max(market_price * 1.12, 0.01), 3),
             "note": "适合品牌款/独家品"},
            {"strategy": "竞品跟随", "price": competitor["avg"] or market_price,
             "margin": round(1 - cost / max(competitor["avg"] or market_price, 0.01), 3) if competitor["avg"] else 0,
             "note": "与市场均价持平"},
        ]

        rec = PriceRecommendation(
            product_id=product_id,
            product_name=product_name,
            cost_price=cost,
            competitor_avg=competitor["avg"],
            competitor_min=competitor["min"],
            competitor_max=competitor["max"],
            competitor_count=competitor["count"],
            recommended_price=market_price,
            profit_margin=margin,
            profit_amount=profit,
            competition_level=competitor["level"],
            ai_reasoning=ai_reasoning,
            confidence=min(0.95, 0.5 + competitor["count"] * 0.05),
            alternatives=alternatives,
            created_at=datetime.now().isoformat(),
        )

        # 9. 记录推荐历史
        cls._save_recommendation(rec)

        return rec

    @classmethod
    async def _ai_price_reasoning(cls, product_name: str, category: str,
                                   cost: float, recommended: float,
                                   competitor: dict, margin: float) -> str:
        """AI模型给出定价理由"""
        if not (DEEPSEEK_KEY or OPENAI_KEY):
            return cls._rule_based_reasoning(category, cost, recommended, competitor, margin)

        prompt = f"""你是电商定价专家。分析以下商品并给出定价理由(50字以内):

商品: {product_name}
类目: {category}
成本: ¥{cost}
建议售价: ¥{recommended}
竞品均价: ¥{competitor.get("avg", "N/A")}
竞品数量: {competitor.get("count", 0)}
竞争强度: {competitor.get("level", "unknown")}
利润率: {margin:.0%}

请给出简洁的定价理由。"""

        try:
            key = DEEPSEEK_KEY or OPENAI_KEY
            api_url = "https://api.deepseek.com/v1/chat/completions" if DEEPSEEK_KEY else f"{AI_BASE_URL}/chat/completions"
            async with httpx.AsyncClient(timeout=15) as c:
                r = await c.post(api_url,
                    headers={"Authorization": f"Bearer {key}"},
                    json={"model": AI_MODEL, "messages": [
                        {"role": "system", "content": "你是电商定价专家。回复简洁，50字以内。"},
                        {"role": "user", "content": prompt}
                    ], "temperature": 0.5, "max_tokens": 100})
                if r.status_code == 200:
                    return r.json()["choices"][0]["message"]["content"].strip()
        except Exception:
            pass

        return cls._rule_based_reasoning(category, cost, recommended, competitor, margin)

    @classmethod
    def _rule_based_reasoning(cls, category: str, cost: float, price: float,
                               competitor: dict, margin: float) -> str:
        """基于规则的定价理由（AI不可用时的降级）"""
        parts = []
        parts.append(f"{category}类目基准利润率{CATEGORY_MARGIN.get(category,0.30):.0%}")
        if competitor["count"] > 0:
            parts.append(f"参考{competitor['count']}个竞品,均价¥{competitor['avg']}")
        parts.append(f"竞争强度:{competitor['level']}")
        if margin > 0.4:
            parts.append("高利润空间,可适当促销")
        elif margin < 0.15:
            parts.append("薄利多销,需控制成本")
        return "; ".join(parts)

    @classmethod
    def _save_recommendation(cls, rec: PriceRecommendation):
        """保存定价推荐到state"""
        from state import state
        history = state._data.setdefault("pricing_history", [])
        history.append({
            "product_id": rec.product_id,
            "product_name": rec.product_name,
            "cost_price": rec.cost_price,
            "recommended_price": rec.recommended_price,
            "profit_margin": rec.profit_margin,
            "competition_level": rec.competition_level,
            "created_at": rec.created_at,
        })
        if len(history) > 500:
            state._data["pricing_history"] = history[-500:]
        state._save()

    @classmethod
    async def batch_recommend(cls, products: list) -> list:
        """批量定价推荐"""
        results = []
        for p in products:
            try:
                rec = await cls.recommend_price(
                    product_id=p.get("id", ""),
                    product_name=p.get("name", ""),
                    supply_price=float(p.get("supply_price", 0)),
                    category=p.get("category", "其他"),
                    shipping=float(p.get("shipping", 0)),
                )
                results.append(rec.__dict__)
            except Exception as e:
                results.append({"product_id": p.get("id"), "error": str(e)[:100]})
        return results

    @classmethod
    def get_history(cls, limit: int = 50) -> list:
        """获取定价历史"""
        from state import state
        return state._data.get("pricing_history", [])[-limit:]

    @classmethod
    def get_stats(cls) -> dict:
        """定价统计"""
        history = cls.get_history(500)
        if not history:
            return {"total": 0}
        margins = [h["profit_margin"] for h in history if h.get("profit_margin")]
        return {
            "total_recommendations": len(history),
            "avg_margin": round(sum(margins)/max(len(margins),1), 3) if margins else 0,
            "today": len([h for h in history if h.get("created_at","")[:10] == datetime.now().strftime("%Y-%m-%d")]),
        }


# 全局实例
pricing_engine = PricingEngine()
