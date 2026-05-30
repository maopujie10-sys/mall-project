"""鎯呮劅鍒嗘瀽 + 瀹㈡埛鐢诲儚"""
import re
from typing import Dict
from collections import Counter, defaultdict
from tools.logger import get_logger

logger = get_logger("sentiment")

class SentimentAnalyzer:
    """鎯呮劅鍒嗘瀽 + 瀹㈡埛鐢诲儚寮曟搸"""

    POSITIVE = {"濂?,"妫?,"璧?,"婊℃剰","鍠滄","蹇?,"渚垮疁","瀹炴儬","鍝佽川","鎺ㄨ崘","nice","good","great","excellent","浼樼","瀹岀編","鎯婂枩","瓒呭€?,"鑸掗€?,"鏂逛究","瀹炵敤","鑰愮敤","婕備寒","绮捐嚧","鏃跺皻","鍒掔畻","鐑儏","鑰愬績","涓撲笟","闈犺氨","绋冲畾","娴佺晠","瀹夊叏","楂樻晥","鐪佸績","鏀惧績","鐗╃編浠峰粔","濂借瘎","浜旀槦","鍥炶喘","缁欏姏","鐗?,"鐖变簡","缁濅簡","yyds","awesome","amazing","fantastic","love","wonderful","perfect","best"}
    NEGATIVE = {"宸?,"鐑?,"鎱?,"璐?,"鍧?,"鍋?,"閫€","鎶曡瘔","鍨冨溇","鍧?,"闂","澶辨湜","bad","poor","terrible","worst","绯?,"鐮?,"鍔ｈ川","闅剧敤","涓戦檵","绮楃硻","鏁疯","鍐锋紶","蹇芥偁","楠楀瓙","鍋囪揣","鐮存崯","鐟曠柕","杩囨湡","鍙樿川","寮傚懗","鎺夎壊","缂╂按","鍗￠】","闂€€","宕╂簝","姝绘満","鍙戠儹","鍣煶","璐圭數","涓嶅€?,"鍚庢倲","韪╅浄","宸瘎","鎭跺績","鏃犺","awful","horrible","disappointed","hate","waste"}
    URGENT = {"鎬?,"椹笂","绔嬪埢","璧剁揣","蹇?,"绱ф€?,"閫€娆?,"鎶ヨ","鎶曡瘔"}

    # 鍚﹀畾璇?鍙嶈浆鎯呮劅)
    NEGATORS = {"涓?,"娌?,"鏃?,"闈?,"鍒?,"鏈?,"鍚?,"鑾?,"浼?}

    # 绋嬪害璇?鏉冮噸璋冩暣)
    INTENSIFIERS = {"寰?:1.5,"闈炲父":1.8,"鐗瑰埆":2.0,"澶?:1.6,"鏋?:2.0,"瓒呯骇":2.0,
                    "鏈夌偣":0.5,"绋嶅井":0.6,"鐣ュ井":0.5,"涓嶅お":0.4}

    @classmethod
    def analyze(cls, text: str) -> Dict:
        """鍒嗘瀽鏂囨湰鎯呮劅"""
        words = set(re.findall(r'[\u4e00-\u9fff]+|[a-zA-Z]+', text.lower()))

        pos = len(words & cls.POSITIVE)
        neg = len(words & cls.NEGATIVE)
        urgent = len(words & cls.URGENT)

        # 鍚﹀畾璇嶅鐞? 鍚﹀畾璇?姝ｉ潰璇?璐熼潰
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
        """鏋勫缓瀹㈡埛鐢诲儚"""
        all_text = " ".join(messages)
        words = re.findall(r'[\u4e00-\u9fff]+', all_text)

        interests = Counter()
        categories = {"浠锋牸":["浠锋牸","閽?,"渚垮疁","璐?,"浼樻儬","鎵撴姌"],"鍝佽川":["鍝佽川","璐ㄩ噺","濂?,"宸?,"姝ｅ搧"],
                      "鐗╂祦":["鐗╂祦","蹇€?,"鍙戣揣","鏀跺埌","鍖呰９"],"鏈嶅姟":["鏈嶅姟","瀹㈡湇","鎬佸害","鍥炲"]}

        for cat, keywords in categories.items():
            interests[cat] = sum(all_text.count(k) for k in keywords)

        sentiment_analysis = cls.analyze(all_text)

        return {"user_id": user_id, "message_count": len(messages),
                "dominant_sentiment": sentiment_analysis["sentiment"],
                "interests": interests.most_common(5),
                "top_words": Counter(words).most_common(10),
                "needs_attention": sentiment_analysis["needs_attention"]}

sentiment_analyzer = SentimentAnalyzer()
