"""情感分析 + 客户画像"""
import re
from typing import Dict
from collections import Counter, defaultdict
from tools.logger import get_logger

logger = get_logger("sentiment")

class SentimentAnalyzer:
    """情感分析 + 客户画像引擎"""

    POSITIVE = {"好","棒","赞","满意","喜欢","快","便宜","实惠","品质","推荐","nice","good","great","excellent","优秀","完美","惊喜","超值","舒适","方便","实用","耐用","漂亮","精致","时尚","划算","热情","耐心","专业","靠谱","稳定","流畅","安全","高效","省心","放心","物美价廉","好评","五星","回购","给力","牛","爱了","绝了","yyds","awesome","amazing","fantastic","love","wonderful","perfect","best"}
    NEGATIVE = {"差","烂","慢","贵","坑","假","退","投诉","垃圾","坏","问题","失望","bad","poor","terrible","worst","糟","破","劣质","难用","丑陋","粗糙","敷衍","冷漠","忽悠","骗子","假货","破损","瑕疵","过期","变质","异味","掉色","缩水","卡顿","闪退","崩溃","死机","发热","噪音","费电","不值","后悔","踩雷","差评","恶心","无语","awful","horrible","disappointed","hate","waste"}
    URGENT = {"急","马上","立刻","赶紧","快","紧急","退款","报警","投诉"}

    # 否定词(反转情感)
    NEGATORS = {"不","没","无","非","别","未","否","莫","休"}

    # 程度词(权重调整)
    INTENSIFIERS = {"很":1.5,"非常":1.8,"特别":2.0,"太":1.6,"极":2.0,"超级":2.0,
                    "有点":0.5,"稍微":0.6,"略微":0.5,"不太":0.4}

    @classmethod
    def analyze(cls, text: str) -> Dict:
        """分析文本情感"""
        words = set(re.findall(r'[\u4e00-\u9fff]+|[a-zA-Z]+', text.lower()))

        pos = len(words & cls.POSITIVE)
        neg = len(words & cls.NEGATIVE)
        urgent = len(words & cls.URGENT)

        # 否定词处理: 否定词+正面词=负面
        negated = False
        weighted_pos = 0
        weighted_neg = 0
        words_list = list(words)
        for i, w in enumerate(words_list):
            if w in cls.NEGATORS:
                negated = True
                continue
            intensity = 1.0
            if i > 0 and words_list[i-1] in cls.INTENSIFIERS:
                intensity = cls.INTENSIFIERS[words_list[i-1]]
            if w in cls.POSITIVE:
                if negated:
                    weighted_neg += 1 * intensity
                else:
                    weighted_pos += 1 * intensity
            elif w in cls.NEGATIVE:
                if negated:
                    weighted_pos += 0.5 * intensity
                else:
                    weighted_neg += 1 * intensity
            negated = False

        if weighted_pos > weighted_neg:
                sentiment, score = "positive", min(1.0, (weighted_pos - weighted_neg) / max(weighted_pos + weighted_neg, 1) * 5)
        elif neg > pos:
            sentiment, score = "negative", min(1.0, (weighted_neg - weighted_pos) / max(weighted_pos + weighted_neg, 1) * 5)
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
