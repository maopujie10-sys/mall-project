''" + ''"
import re
from typing import Dict
from collections import Counter, defaultdict
from tools.logger import get_logger

logger = get_logger("sentiment")

class SentimentAnalyzer:
    ''" + ''"

    POSITIVE = {'','','','','','','','','','',"nice","good","great","excellent",'','','','','','','','','','','','','','','','','','','','','','','','','','','','','','',"yyds","awesome","amazing","fantastic","love","wonderful","perfect","best"}
    NEGATIVE = {'','','','','','','','','','','','',"bad","poor","terrible","worst",'','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','',"awful","horrible","disappointed","hate","waste"}
    URGENT = {'','','','','','','','',''}

    # ()
    NEGATORS = {'','','','','','','','',''}

    # ()
    INTENSIFIERS = {'':1.5,'':1.8,'':2.0,'':1.6,'':2.0,'':2.0,
                    '':0.5,'':0.6,'':0.5,'':0.4}

    @classmethod
    def analyze(cls, text: str) -> Dict:
        ''''''
        words = set(re.findall(r'[-]+|[a-zA-Z]+', text.lower()))

        pos = len(words & cls.POSITIVE)
        neg = len(words & cls.NEGATIVE)
        urgent = len(words & cls.URGENT)

        # : +=
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
        ''''''
        all_text = ''.join(messages)
        words = re.findall(r'[-]+', all_text)

        interests = Counter()
        categories = {'':['','','','','',''],'':['','','','',''],
                      '':['','','','',''],'':['','','','']}

        for cat, keywords in categories.items():
            interests[cat] = sum(all_text.count(k) for k in keywords)

        sentiment_analysis = cls.analyze(all_text)

        return {"user_id": user_id, "message_count": len(messages),
                "dominant_sentiment": sentiment_analysis["sentiment"],
                "interests": interests.most_common(5),
                "top_words": Counter(words).most_common(10),
                "needs_attention": sentiment_analysis["needs_attention"]}

sentiment_analyzer = SentimentAnalyzer()
