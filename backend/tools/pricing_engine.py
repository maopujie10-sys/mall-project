锘?""AI鏅鸿兘瀹氫环寮曟搸 鈥?绔炲搧鍒嗘瀽+鎴愭湰璁＄畻+AI鎺ㄨ崘瀹氫环+浠锋牸鍘嗗彶杩借釜"""
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

# 绫荤洰鍒╂鼎鐜囧熀鍑?
CATEGORY_MARGIN = {
    "鏈嶈": 0.45, "闉嬪寘": 0.40, "閰嶉グ": 0.50, "缇庡": 0.35,
    "3C鏁扮爜": 0.12, "瀹跺眳": 0.30, "鐜╁叿": 0.35, "杩愬姩": 0.28,
    "椋熷搧": 0.20, "姣嶅┐": 0.30, "姹借溅": 0.25, "鍔炲叕": 0.22,
    "瀹犵墿": 0.35, "鍥句功": 0.15, "涔愬櫒": 0.30, "鍏朵粬": 0.30,
}

# 绔炰簤寮哄害璋冩暣绯绘暟
COMPETITION_ADJUST = {
    "low": 1.15,     # 绔炰簤浣?鈫?鍔犱环15%
    "medium": 1.00,  # 姝ｅ父
    "high": 0.88,    # 绔炰簤楂?鈫?闄嶄环12%
    "extreme": 0.80, # 鏋佸害绔炰簤 鈫?闄嶄环20%
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
    """AI椹卞姩鐨勬櫤鑳藉畾浠峰紩鎿?""

    @classmethod
    async def analyze_competitors(cls, product_name: str, category: str = "鍏朵粬") -> dict:
        """鍒嗘瀽绔炲搧浠锋牸 鈥?浠庡凡閲囬泦鏁版嵁+瀹炴椂鎼滅储"""
        from state import state
        products = state._data.get("scraped_products", [])

        # 浠庡凡閲囬泦鏁版嵁鍖归厤
        matches = []
        keywords = product_name.lower().split()[:3]
        for p in products:
            p_name = p.get("name", "").lower()
            p_price = float(p.get("price", 0) or 0)
            if p_price > 0 and any(kw in p_name for kw in keywords if len(kw) > 1):
                matches.append(p)

        if not matches and any(kw in product_name.lower() for kw in ["鎵嬫満","鐢佃剳","琛ｆ湇","闉嬪瓙"]):
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

        # 绔炰簤寮哄害鍒ゆ柇
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
        """璁＄畻鐪熷疄鎴愭湰浠?""
        platform_fee = supply_price * platform_fee_rate
        return round(supply_price + shipping + platform_fee + packaging + labor, 2)

    @classmethod
    async def recommend_price(cls, product_id: str, product_name: str,
                               supply_price: float, category: str = "鍏朵粬",
                               shipping: float = 0, packaging: float = 0,
                               target_margin: Optional[float] = None,
                               min_price: Optional[float] = None,
                               max_price: Optional[float] = None) -> PriceRecommendation:
        """AI缁煎悎鎺ㄨ崘瀹氫环"""
        # 1. 璁＄畻鎴愭湰
        cost = cls.calculate_cost_price(supply_price, shipping, packaging=packaging)
        base_margin = target_margin or CATEGORY_MARGIN.get(category, 0.30)

        # 2. 鍒嗘瀽绔炲搧
        competitor = await cls.analyze_competitors(product_name, category)

        # 3. 鍩虹瀹氫环 = 鎴愭湰 / (1 - 鍒╂鼎鐜?
        base_price = round(cost / max(1 - base_margin, 0.01), 2)

        # 4. 绔炲搧璋冩暣
        comp_adjust = COMPETITION_ADJUST.get(competitor["level"], 1.0)
        market_price = round(base_price * comp_adjust, 2)

        # 5. 绔炲搧閿氬畾
        if competitor["avg"] > 0:
            if market_price > competitor["max"] * 1.3:
                market_price = round(competitor["max"] * 1.15, 2)
            elif market_price < competitor["min"] * 0.7:
                market_price = round(competitor["min"] * 0.85, 2)

        # 6. 浠锋牸杈圭晫
        if min_price and market_price < min_price:
            market_price = min_price
        if max_price and market_price > max_price:
            market_price = max_price

        # 纭繚鏈夊埄娑?
        if market_price < cost * 1.05:
            market_price = round(cost * 1.08, 2)

        profit = round(market_price - cost, 2)
        margin = round(profit / market_price, 3) if market_price > 0 else 0

        # 7. AI鎺ㄧ悊 鈥?缁欏嚭瀹氫环鐞嗙敱
        ai_reasoning = await cls._ai_price_reasoning(
            product_name, category, cost, market_price, competitor, margin
        )

        # 8. 澶囬€夋柟妗?
        alternatives = [
            {"strategy": "淇濆畧浣庝环", "price": round(market_price * 0.92, 2),
             "margin": round(1 - cost / max(market_price * 0.92, 0.01), 3),
             "note": "閫傚悎鍐查攢閲?娓呭簱瀛?},
            {"strategy": "鍝佽川楂樹环", "price": round(market_price * 1.12, 2),
             "margin": round(1 - cost / max(market_price * 1.12, 0.01), 3),
             "note": "閫傚悎鍝佺墝娆?鐙鍝?},
            {"strategy": "绔炲搧璺熼殢", "price": competitor["avg"] or market_price,
             "margin": round(1 - cost / max(competitor["avg"] or market_price, 0.01), 3) if competitor["avg"] else 0,
             "note": "涓庡競鍦哄潎浠锋寔骞?},
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

        # 9. 璁板綍鎺ㄨ崘鍘嗗彶
        cls._save_recommendation(rec)

        return rec

    @classmethod
    async def _ai_price_reasoning(cls, product_name: str, category: str,
                                   cost: float, recommended: float,
                                   competitor: dict, margin: float) -> str:
        """AI妯″瀷缁欏嚭瀹氫环鐞嗙敱"""
        if not (DEEPSEEK_KEY or OPENAI_KEY):
            return cls._rule_based_reasoning(category, cost, recommended, competitor, margin)

        prompt = f"""浣犳槸鐢靛晢瀹氫环涓撳銆傚垎鏋愪互涓嬪晢鍝佸苟缁欏嚭瀹氫环鐞嗙敱(50瀛椾互鍐?:

鍟嗗搧: {product_name}
绫荤洰: {category}
鎴愭湰: 楼{cost}
寤鸿鍞环: 楼{recommended}
绔炲搧鍧囦环: 楼{competitor.get("avg", "N/A")}
绔炲搧鏁伴噺: {competitor.get("count", 0)}
绔炰簤寮哄害: {competitor.get("level", "unknown")}
鍒╂鼎鐜? {margin:.0%}

璇风粰鍑虹畝娲佺殑瀹氫环鐞嗙敱銆?""

        try:
            key = DEEPSEEK_KEY or OPENAI_KEY
            api_url = "https://api.deepseek.com/v1/chat/completions" if DEEPSEEK_KEY else f"{AI_BASE_URL}/chat/completions"
            async with httpx.AsyncClient(timeout=15) as c:
                r = await c.post(api_url,
                    headers={"Authorization": f"Bearer {key}"},
                    json={"model": AI_MODEL, "messages": [
                        {"role": "system", "content": "浣犳槸鐢靛晢瀹氫环涓撳銆傚洖澶嶇畝娲侊紝50瀛椾互鍐呫€?},
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
        """鍩轰簬瑙勫垯鐨勫畾浠风悊鐢憋紙AI涓嶅彲鐢ㄦ椂鐨勯檷绾э級"""
        parts = []
        parts.append(f"{category}绫荤洰鍩哄噯鍒╂鼎鐜噞CATEGORY_MARGIN.get(category,0.30):.0%}")
        if competitor["count"] > 0:
            parts.append(f"鍙傝€儃competitor['count']}涓珵鍝?鍧囦环楼{competitor['avg']}")
        parts.append(f"绔炰簤寮哄害:{competitor['level']}")
        if margin > 0.4:
            parts.append("楂樺埄娑︾┖闂?鍙€傚綋淇冮攢")
        elif margin < 0.15:
            parts.append("钖勫埄澶氶攢,闇€鎺у埗鎴愭湰")
        return "; ".join(parts)

    @classmethod
    def _save_recommendation(cls, rec: PriceRecommendation):
        """淇濆瓨瀹氫环鎺ㄨ崘鍒皊tate"""
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
        """鎵归噺瀹氫环鎺ㄨ崘"""
        results = []
        for p in products:
            try:
                rec = await cls.recommend_price(
                    product_id=p.get("id", ""),
                    product_name=p.get("name", ""),
                    supply_price=float(p.get("supply_price", 0)),
                    category=p.get("category", "鍏朵粬"),
                    shipping=float(p.get("shipping", 0)),
                )
                results.append(rec.__dict__)
            except Exception as e:
                results.append({"product_id": p.get("id"), "error": str(e)[:100]})
        return results

    @classmethod
    def get_history(cls, limit: int = 50) -> list:
        """鑾峰彇瀹氫环鍘嗗彶"""
        from state import state
        return state._data.get("pricing_history", [])[-limit:]

    @classmethod
    def get_stats(cls) -> dict:
        """瀹氫环缁熻"""
        history = cls.get_history(500)
        if not history:
            return {"total": 0}
        margins = [h["profit_margin"] for h in history if h.get("profit_margin")]
        return {
            "total_recommendations": len(history),
            "avg_margin": round(sum(margins)/max(len(margins),1), 3) if margins else 0,
            "today": len([h for h in history if h.get("created_at","")[:10] == datetime.now().strftime("%Y-%m-%d")]),
        }


# 鍏ㄥ眬瀹炰緥
pricing_engine = PricingEngine()
