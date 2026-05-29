"""情感分析 + 客户画像"""
import re
from collections import Counter, defaultdict
from tools.logger import get_logger

logger = get_logger("sentiment")

class SentimentAnalyzer:
    """情感分析 + 客户画像引擎"""

    POSITIVE = {"好","棒","赞","满意","喜欢","快","便宜","实惠","品质","推荐","nice","good","great","excellent"}
    NEGATIVE = {"差","烂","慢","贵","坑","假","退","投诉","垃圾","坏","问题","失望","bad","poor","terrible","worst"}
    URGENT = {"急","马上","立刻","赶紧","快","紧急","退款","报警","投诉"}

    @classmethod
    def analyze(cls, text: str) -> Dict:
        """分析文本情感"""
        words = set(re.findall(r'[\u4e00-\u9fff]+|[a-zA-Z]+', text.lower()))

        pos = len(words & cls.POSITIVE)
        neg = len(words & cls.NEGATIVE)
        urgent = len(words & cls.URGENT)

        if pos > neg:
            sentiment, score = "positive", min(1.0, (pos - neg) / max(pos + neg, 1) * 5)
        elif neg > pos:
            sentiment, score = "negative", min(1.0, (neg - pos) / max(pos + neg, 1) * 5)
        else:
            sentiment, score = "neutral", 0.5

        return {"sentiment": sentiment, "score": round(score, 2), "urgency": min(1.0, urgent * 0.3),
                "positive_words": list(words & cls.POSITIVE), "negative_words": list(words & cls.NEGATIVE),
                "needs_attention": urgent > 0 or sentiment == "negative"}

    @classmethod
    def build_profile(cls, user_id: str, messages: list) -> Dict:
        """构建客户画像"""
        all_text = " ".join(messages)
        words = re.findall(r'[\u4e00-\u9fff]+', all_text)

        interests = Counter()
        categories = {"价格":["价格","钱","便宜","贵","优惠","打折"],"品质":["品质","质量","好","差","正品"],
                      "物流":["物流","快递","发货","收到","包裹"],"服务":["服务","客服","态度","回复"]}

        for cat, keywords in categories.items():
            interests[cat] = sum(all_text.count(k) for k in keywords)

        sentiment_analysis = cls.analyze(all_text)

        return {"user_id": user_id, "message_count": len(messages),
                "dominant_sentiment": sentiment_analysis["sentiment"],
                "interests": interests.most_common(5),
                "top_words": Counter(words).most_common(10),
                "needs_attention": sentiment_analysis["needs_attention"]}

sentiment_analyzer = SentimentAnalyzer()
