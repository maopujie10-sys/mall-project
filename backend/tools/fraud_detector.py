锘?""AI寮傚父璁㈠崟妫€娴?鈥?鍒峰崟璇嗗埆+娆鸿瘓妫€娴?椋庨櫓璇勫垎"""
import os, httpx, json, math
from datetime import datetime, timedelta
from collections import defaultdict
from tools.logger import get_logger

logger = get_logger("fraud_detector")

DEEPSEEK_KEY = os.getenv("DEEPSEEK_API_KEY", "")
OPENAI_KEY = os.getenv("OPENAI_API_KEY", "")

# 椋庨櫓瑙勫垯鏉冮噸
RISK_RULES = {
    "new_user_high_amount": {"weight": 30, "desc": "鏂扮敤鎴峰ぇ棰濊鍗?},
    "rapid_orders": {"weight": 25, "desc": "鐭椂闂村ぇ閲忎笅鍗?},
    "same_ip_multi_account": {"weight": 35, "desc": "鍚孖P澶氳处鍙?},
    "address_mismatch": {"weight": 15, "desc": "鏀惰揣鍦板潃寮傚父"},
    "abnormal_hour": {"weight": 10, "desc": "娣卞寮傚父涓嬪崟"},
    "price_anomaly": {"weight": 20, "desc": "浠锋牸寮傚父锛堣繙浣庝簬甯傚満浠凤級"},
    "refund_rate_high": {"weight": 25, "desc": "閫€璐х巼寮傚父楂?},
    "device_fingerprint": {"weight": 20, "desc": "璁惧鎸囩汗閲嶅"},
}


class FraudDetector:
    """AI椹卞姩鐨勫紓甯歌鍗曟娴嬪紩鎿?""

    @classmethod
    async def analyze_order(cls, order: dict) -> dict:
        """鍒嗘瀽鍗曚釜璁㈠崟鐨勯闄?""
        risk_score = 0
        flags = []
        details = {}

        # 1. 鏂扮敤鎴?澶ч
        if order.get("is_new_user") and float(order.get("amount", 0)) > 500:
            risk_score += RISK_RULES["new_user_high_amount"]["weight"]
            flags.append({"rule": "new_user_high_amount",
                          "detail": f"鏂扮敤鎴蜂笅鍗暵order.get('amount',0)}"})
            details["new_user_high"] = True

        # 2. 鐭椂闂村唴澶ч噺涓嬪崟
        recent_orders = order.get("recent_order_count", 0)
        if recent_orders > 10:
            score = min(RISK_RULES["rapid_orders"]["weight"] * (recent_orders / 10), 50)
            risk_score += score
            flags.append({"rule": "rapid_orders",
                          "detail": f"1灏忔椂鍐厈recent_orders}绗旇鍗?})
            details["rapid_orders"] = recent_orders

        # 3. 鍚孖P澶氳处鍙?
        ip_accounts = order.get("same_ip_accounts", 0)
        if ip_accounts > 3:
            risk_score += RISK_RULES["same_ip_multi_account"]["weight"]
            flags.append({"rule": "same_ip_multi_account",
                          "detail": f"鍚孖P涓媨ip_accounts}涓处鍙?})
            details["ip_multi"] = ip_accounts

        # 4. 鍦板潃寮傚父 鈥?鍦板潃涓嶪P涓嶅尮閰?
        if order.get("ip_country") and order.get("ship_country"):
            if order["ip_country"] != order["ship_country"]:
                risk_score += RISK_RULES["address_mismatch"]["weight"]
                flags.append({"rule": "address_mismatch",
                              "detail": f"IP:{order['ip_country']} vs 鏀惰揣:{order['ship_country']}"})
                details["geo_mismatch"] = True

        # 5. 娣卞寮傚父
        hour = order.get("order_hour", 12)
        if hour < 5 or hour > 23:
            risk_score += RISK_RULES["abnormal_hour"]["weight"]
            flags.append({"rule": "abnormal_hour", "detail": f"涓嬪崟鏃堕棿{hour}:00"})

        # 6. 浠锋牸寮傚父
        avg_price = order.get("category_avg_price", 0)
        order_price = float(order.get("amount", 0))
        if avg_price > 0 and order_price < avg_price * 0.3:
            risk_score += RISK_RULES["price_anomaly"]["weight"]
            flags.append({"rule": "price_anomaly",
                          "detail": f"楼{order_price} vs 鍧囦环楼{avg_price}"})

        # 7. 閫€璐х巼
        refund_rate = order.get("refund_rate", 0)
        if refund_rate > 0.5:
            risk_score += RISK_RULES["refund_rate_high"]["weight"]
            flags.append({"rule": "refund_rate_high", "detail": f"閫€璐х巼{refund_rate:.0%}"})

        # 8. 璁惧鎸囩汗
        device_count = order.get("device_order_count", 1)
        if device_count > 5:
            risk_score += RISK_RULES["device_fingerprint"]["weight"]
            flags.append({"rule": "device_fingerprint",
                          "detail": f"鍚岃澶噞device_count}绗旇鍗?})

        # AI缁煎悎鍒嗘瀽锛堝鏋滄湁API Key锛?
        ai_analysis = ""
        if (DEEPSEEK_KEY or OPENAI_KEY) and risk_score > 40:
            ai_analysis = await cls._ai_fraud_analysis(order, flags, risk_score)

        # 椋庨櫓绛夌骇
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
        """鎵归噺鍒嗘瀽璁㈠崟"""
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
        """蹇€熸壂鎻忥紙涓嶈皟AI锛屾绉掔骇锛?""
        risk = 0
        flags = []

        if float(order.get("amount", 0)) > 10000:
            risk += 30
            flags.append("澶ч璁㈠崟>楼10000")
        if order.get("is_new_user") and float(order.get("amount", 0)) > 1000:
            risk += 25
            flags.append("鏂扮敤鎴峰ぇ棰?)
        if order.get("same_ip_accounts", 0) > 5:
            risk += 35
            flags.append("鍚孖P澶氳处鍙?)
        if order.get("recent_order_count", 0) > 20:
            risk += 30
            flags.append("楂橀涓嬪崟")

        level = "high" if risk >= 60 else ("medium" if risk >= 30 else "low")
        return {
            "order_id": order.get("id", ""),
            "quick_risk": min(risk, 100),
            "level": level,
            "flags": flags,
        }

    @classmethod
    async def _ai_fraud_analysis(cls, order: dict, flags: list, score: float) -> str:
        """AI娣卞害鍒嗘瀽"""
        prompt = f"""鍒嗘瀽浠ヤ笅璁㈠崟鏄惁瀛樺湪娆鸿瘓椋庨櫓:

璁㈠崟ID: {order.get('id','')}
閲戦: 楼{order.get('amount',0)}
鐢ㄦ埛绫诲瀷: {'鏂扮敤鎴? if order.get('is_new_user') else '鑰佺敤鎴?}
宸茶Е鍙戦闄╄鍒? {json.dumps([f['detail'] for f in flags], ensure_ascii=False)}
椋庨櫓璇勫垎: {score}/100

璇风敤涓€鍙ヨ瘽鍒ゆ柇鏄惁瀛樺湪娆鸿瘓,缁欏嚭寤鸿(30瀛椾互鍐?銆?""

        try:
            key = DEEPSEEK_KEY or OPENAI_KEY
            api_url = "https://api.deepseek.com/v1/chat/completions" if DEEPSEEK_KEY else f"https://api.openai.com/v1/chat/completions"
            async with httpx.AsyncClient(timeout=15) as c:
                r = await c.post(api_url,
                    headers={"Authorization": f"Bearer {key}"},
                    json={"model": "deepseek-chat", "messages": [
                        {"role": "system", "content": "浣犳槸鐢靛晢鍙嶆璇堜笓瀹躲€傚洖澶嶇畝娲侊紝30瀛椾互鍐呫€?},
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
            return "寤鸿浜哄伐瀹℃牳锛屾殏涓嶅彂璐?
        elif level == "medium":
            return "寤鸿鍏虫敞锛屽彲姝ｅ父鍙戣揣浣嗘爣璁拌瀵?
        return "姝ｅ父璁㈠崟锛屽彲鍙戣揣"

    @classmethod
    def get_rules(cls) -> dict:
        return {k: {"weight": v["weight"], "desc": v["desc"]} for k, v in RISK_RULES.items()}


fraud_detector = FraudDetector()
