''"AI -- ++''"
import os, httpx, json, math
from datetime import datetime, timedelta
from collections import defaultdict
from tools.logger import get_logger

logger = get_logger("fraud_detector")

DEEPSEEK_KEY = os.getenv("DEEPSEEK_API_KEY", '')
OPENAI_KEY = os.getenv("OPENAI_API_KEY", '')


RISK_RULES = {
    "new_user_high_amount": {"weight": 30, "desc": ''},
    "rapid_orders": {"weight": 25, "desc": ''},
    "same_ip_multi_account": {"weight": 35, "desc": "IP"},
    "address_mismatch": {"weight": 15, "desc": ''},
    "abnormal_hour": {"weight": 10, "desc": ''},
    "price_anomaly": {"weight": 20, "desc": "()"},
    "refund_rate_high": {"weight": 25, "desc": ''},
    "device_fingerprint": {"weight": 20, "desc": ''},
}


class FraudDetector:
    ''"AI''"

    @classmethod
    async def analyze_order(cls, order: dict) -> dict:
        ''''''
        risk_score = 0
        flags = []
        details = {}

        # 1. +
        if order.get("is_new_user") and float(order.get("amount", 0)) > 500:
            risk_score += RISK_RULES["new_user_high_amount"]["weight"]
            flags.append({"rule": "new_user_high_amount",
                          "detail": f"{order.get('amount',0)}"})
            details["new_user_high"] = True

        # 2. 
        recent_orders = order.get("recent_order_count", 0)
        if recent_orders > 10:
            score = min(RISK_RULES["rapid_orders"]["weight"] * (recent_orders / 10), 50)
            risk_score += score
            flags.append({"rule": "rapid_orders",
                          "detail": f"1{recent_orders}"})
            details["rapid_orders"] = recent_orders

        # 3. IP
        ip_accounts = order.get("same_ip_accounts", 0)
        if ip_accounts > 3:
            risk_score += RISK_RULES["same_ip_multi_account"]["weight"]
            flags.append({"rule": "same_ip_multi_account",
                          "detail": f"IP{ip_accounts}"})
            details["ip_multi"] = ip_accounts

        # 4.  -- IP
        if order.get("ip_country") and order.get("ship_country"):
            if order["ip_country"] != order["ship_country"]:
                risk_score += RISK_RULES["address_mismatch"]["weight"]
                flags.append({"rule": "address_mismatch",
                              "detail": f"IP:{order['ip_country']} vs :{order['ship_country']}"})
                details["geo_mismatch"] = True

        # 5. 
        hour = order.get("order_hour", 12)
        if hour < 5 or hour > 23:
            risk_score += RISK_RULES["abnormal_hour"]["weight"]
            flags.append({"rule": "abnormal_hour", "detail": f"{hour}:00"})

        # 6. 
        avg_price = order.get("category_avg_price", 0)
        order_price = float(order.get("amount", 0))
        if avg_price > 0 and order_price < avg_price * 0.3:
            risk_score += RISK_RULES["price_anomaly"]["weight"]
            flags.append({"rule": "price_anomaly",
                          "detail": f"{order_price} vs {avg_price}"})

        # 7. 
        refund_rate = order.get("refund_rate", 0)
        if refund_rate > 0.5:
            risk_score += RISK_RULES["refund_rate_high"]["weight"]
            flags.append({"rule": "refund_rate_high", "detail": f"{refund_rate:.0%}"})

        # 8. 
        device_count = order.get("device_order_count", 1)
        if device_count > 5:
            risk_score += RISK_RULES["device_fingerprint"]["weight"]
            flags.append({"rule": "device_fingerprint",
                          "detail": f"{device_count}"})

        # AI(API Key)
        ai_analysis = ''
        if (DEEPSEEK_KEY or OPENAI_KEY) and risk_score > 40:
            ai_analysis = await cls._ai_fraud_analysis(order, flags, risk_score)

        
        risk_score = min(risk_score, 100)
        if risk_score >= 70:
            level = "high"
        elif risk_score >= 40:
            level = "medium"
        else:
            level = "low"

        return {
            "order_id": order.get("id", ''),
            "risk_score": round(risk_score, 1),
            "risk_level": level,
            "flags": flags,
            "details": details,
            "ai_analysis": ai_analysis,
            "recommendation": cls._get_recommendation(level, risk_score),
            "checked_at": datetime.now().isoformat(),
        }

    @classmethod
    async def batch_analyze(cls, orders: list) -> dict:
        ''''''
        results = []
        high_risk = []
        for order in orders[:100]:
            try:
                result = await cls.analyze_order(order)
                results.append(result)
                if result["risk_level"] == "high":
                    high_risk.append(result)
            except Exception as e:
                results.append({"order_id": order.get("id"), "error": str(e)[:100]})

        return {
            "total": len(results),
            "high_risk": len(high_risk),
            "medium_risk": sum(1 for r in results if r.get("risk_level") == "medium"),
            "low_risk": sum(1 for r in results if r.get("risk_level") == "low"),
            "results": results,
            "high_risk_orders": high_risk,
        }

    @classmethod
    def quick_scan(cls, order: dict) -> dict:
        ''"(AI,)''"
        risk = 0
        flags = []

        if float(order.get("amount", 0)) > 10000:
            risk += 30
            flags.append(">10000")
        if order.get("is_new_user") and float(order.get("amount", 0)) > 1000:
            risk += 25
            flags.append('')
        if order.get("same_ip_accounts", 0) > 5:
            risk += 35
            flags.append("IP")
        if order.get("recent_order_count", 0) > 20:
            risk += 30
            flags.append('')

        level = "high" if risk >= 60 else ("medium" if risk >= 30 else "low")
        return {
            "order_id": order.get("id", ''),
            "quick_risk": min(risk, 100),
            "level": level,
            "flags": flags,
        }

    @classmethod
    async def _ai_fraud_analysis(cls, order: dict, flags: list, score: float) -> str:
        ''"AI''"
        prompt = f''":

ID: {order.get('id','')}
: {order.get('amount',0)}
: {'' if order.get('is_new_user') else ''}
: {json.dumps([f['detail'] for f in flags], ensure_ascii=False)}
: {score}/100

,(30).''"

        try:
            key = DEEPSEEK_KEY or OPENAI_KEY
            api_url = "https://api.deepseek.com/v1/chat/completions" if DEEPSEEK_KEY else f"https://api.openai.com/v1/chat/completions"
            async with httpx.AsyncClient(timeout=15) as c:
                r = await c.post(api_url,
                    headers={"Authorization": f"Bearer {key}"},
                    json={"model": "deepseek-chat", "messages": [
                        {"role": "system", "content": ".,30."},
                        {"role": "user", "content": prompt}
                    ], "temperature": 0.3, "max_tokens": 80})
                if r.status_code == 200:
                    return r.json()["choices"][0]["message"]["content"].strip()
        except Exception:
            pass
        return ''

    @classmethod
    def _get_recommendation(cls, level: str, score: float) -> str:
        if level == "high":
            return ","
        elif level == "medium":
            return ","
        return ","

    @classmethod
    def get_rules(cls) -> dict:
        return {k: {"weight": v["weight"], "desc": v["desc"]} for k, v in RISK_RULES.items()}


fraud_detector = FraudDetector()
