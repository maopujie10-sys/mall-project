"""AI异常订单检测 — 刷单识别+欺诈检测+风险评分"""
import os, httpx, json, math
from datetime import datetime, timedelta
from collections import defaultdict
from tools.logger import get_logger

logger = get_logger("fraud_detector")

DEEPSEEK_KEY = os.getenv("DEEPSEEK_API_KEY", "")
OPENAI_KEY = os.getenv("OPENAI_API_KEY", "")

# 风险规则权重
RISK_RULES = {
    "new_user_high_amount": {"weight": 30, "desc": "新用户大额订单"},
    "rapid_orders": {"weight": 25, "desc": "短时间大量下单"},
    "same_ip_multi_account": {"weight": 35, "desc": "同IP多账号"},
    "address_mismatch": {"weight": 15, "desc": "收货地址异常"},
    "abnormal_hour": {"weight": 10, "desc": "深夜异常下单"},
    "price_anomaly": {"weight": 20, "desc": "价格异常（远低于市场价）"},
    "refund_rate_high": {"weight": 25, "desc": "退货率异常高"},
    "device_fingerprint": {"weight": 20, "desc": "设备指纹重复"},
}


class FraudDetector:
    """AI驱动的异常订单检测引擎"""

    @classmethod
    async def analyze_order(cls, order: dict) -> dict:
        """分析单个订单的风险"""
        risk_score = 0
        flags = []
        details = {}

        # 1. 新用户+大额
        if order.get("is_new_user") and float(order.get("amount", 0)) > 500:
            risk_score += RISK_RULES["new_user_high_amount"]["weight"]
            flags.append({"rule": "new_user_high_amount",
                          "detail": f"新用户下单¥{order.get('amount',0)}"})
            details["new_user_high"] = True

        # 2. 短时间内大量下单
        recent_orders = order.get("recent_order_count", 0)
        if recent_orders > 10:
            score = min(RISK_RULES["rapid_orders"]["weight"] * (recent_orders / 10), 50)
            risk_score += score
            flags.append({"rule": "rapid_orders",
                          "detail": f"1小时内{recent_orders}笔订单"})
            details["rapid_orders"] = recent_orders

        # 3. 同IP多账号
        ip_accounts = order.get("same_ip_accounts", 0)
        if ip_accounts > 3:
            risk_score += RISK_RULES["same_ip_multi_account"]["weight"]
            flags.append({"rule": "same_ip_multi_account",
                          "detail": f"同IP下{ip_accounts}个账号"})
            details["ip_multi"] = ip_accounts

        # 4. 地址异常 — 地址与IP不匹配
        if order.get("ip_country") and order.get("ship_country"):
            if order["ip_country"] != order["ship_country"]:
                risk_score += RISK_RULES["address_mismatch"]["weight"]
                flags.append({"rule": "address_mismatch",
                              "detail": f"IP:{order['ip_country']} vs 收货:{order['ship_country']}"})
                details["geo_mismatch"] = True

        # 5. 深夜异常
        hour = order.get("order_hour", 12)
        if hour < 5 or hour > 23:
            risk_score += RISK_RULES["abnormal_hour"]["weight"]
            flags.append({"rule": "abnormal_hour", "detail": f"下单时间{hour}:00"})

        # 6. 价格异常
        avg_price = order.get("category_avg_price", 0)
        order_price = float(order.get("amount", 0))
        if avg_price > 0 and order_price < avg_price * 0.3:
            risk_score += RISK_RULES["price_anomaly"]["weight"]
            flags.append({"rule": "price_anomaly",
                          "detail": f"¥{order_price} vs 均价¥{avg_price}"})

        # 7. 退货率
        refund_rate = order.get("refund_rate", 0)
        if refund_rate > 0.5:
            risk_score += RISK_RULES["refund_rate_high"]["weight"]
            flags.append({"rule": "refund_rate_high", "detail": f"退货率{refund_rate:.0%}"})

        # 8. 设备指纹
        device_count = order.get("device_order_count", 1)
        if device_count > 5:
            risk_score += RISK_RULES["device_fingerprint"]["weight"]
            flags.append({"rule": "device_fingerprint",
                          "detail": f"同设备{device_count}笔订单"})

        # AI综合分析（如果有API Key）
        ai_analysis = ""
        if (DEEPSEEK_KEY or OPENAI_KEY) and risk_score > 40:
            ai_analysis = await cls._ai_fraud_analysis(order, flags, risk_score)

        # 风险等级
        risk_score = min(risk_score, 100)
        if risk_score >= 70:
            level = "high"
        elif risk_score >= 40:
            level = "medium"
        else:
            level = "low"

        return {
            "order_id": order.get("id", ""),
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
        """批量分析订单"""
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
        """快速扫描（不调AI，毫秒级）"""
        risk = 0
        flags = []

        if float(order.get("amount", 0)) > 10000:
            risk += 30
            flags.append("大额订单>¥10000")
        if order.get("is_new_user") and float(order.get("amount", 0)) > 1000:
            risk += 25
            flags.append("新用户大额")
        if order.get("same_ip_accounts", 0) > 5:
            risk += 35
            flags.append("同IP多账号")
        if order.get("recent_order_count", 0) > 20:
            risk += 30
            flags.append("高频下单")

        level = "high" if risk >= 60 else ("medium" if risk >= 30 else "low")
        return {
            "order_id": order.get("id", ""),
            "quick_risk": min(risk, 100),
            "level": level,
            "flags": flags,
        }

    @classmethod
    async def _ai_fraud_analysis(cls, order: dict, flags: list, score: float) -> str:
        """AI深度分析"""
        prompt = f"""分析以下订单是否存在欺诈风险:

订单ID: {order.get('id','')}
金额: ¥{order.get('amount',0)}
用户类型: {'新用户' if order.get('is_new_user') else '老用户'}
已触发风险规则: {json.dumps([f['detail'] for f in flags], ensure_ascii=False)}
风险评分: {score}/100

请用一句话判断是否存在欺诈,给出建议(30字以内)。"""

        try:
            key = DEEPSEEK_KEY or OPENAI_KEY
            api_url = "https://api.deepseek.com/v1/chat/completions" if DEEPSEEK_KEY else f"https://api.openai.com/v1/chat/completions"
            async with httpx.AsyncClient(timeout=15) as c:
                r = await c.post(api_url,
                    headers={"Authorization": f"Bearer {key}"},
                    json={"model": "deepseek-chat", "messages": [
                        {"role": "system", "content": "你是电商反欺诈专家。回复简洁，30字以内。"},
                        {"role": "user", "content": prompt}
                    ], "temperature": 0.3, "max_tokens": 80})
                if r.status_code == 200:
                    return r.json()["choices"][0]["message"]["content"].strip()
        except Exception:
            pass
        return ""

    @classmethod
    def _get_recommendation(cls, level: str, score: float) -> str:
        if level == "high":
            return "建议人工审核，暂不发货"
        elif level == "medium":
            return "建议关注，可正常发货但标记观察"
        return "正常订单，可发货"

    @classmethod
    def get_rules(cls) -> dict:
        return {k: {"weight": v["weight"], "desc": v["desc"]} for k, v in RISK_RULES.items()}


fraud_detector = FraudDetector()
