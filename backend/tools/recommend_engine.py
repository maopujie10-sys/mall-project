"""鎺ㄨ崘寮曟搸 -- 鍗忓悓杩囨护 + 鍚戦噺鐩镐技搴?""
import math, json
from collections import defaultdict, Counter
from typing import List, Dict
from tools.logger import get_logger

logger = get_logger("recommend")

class RecommendEngine:
    """AI鎺ㄨ崘寮曟搸"""
    _user_actions: Dict[str, List[Dict]] = defaultdict(list)  # user_id -> [{item_id, action, time}]
    _item_features: Dict[str, Dict] = {}  # item_id -> {category, price, tags, vector}

    @classmethod
    def record_action(cls, user_id: str, item_id: str, action: str):
        """璁板綍鐢ㄦ埛琛屼负"""
        import time
        cls._user_actions[user_id].append({"item_id": item_id, "action": action, "time": time.time()})

    @classmethod
    def set_item_features(cls, item_id: str, features: Dict):
        cls._item_features[item_id] = features

    @classmethod
    def recommend_for_user(cls, user_id: str, top_k: int = 10) -> List[Dict]:
        """涓虹敤鎴锋帹鑽愬晢鍝?""
        user_items = set(a["item_id"] for a in cls._user_actions.get(user_id, []))

        # 鍗忓悓杩囨护:鎵剧浉浼肩敤鎴?
        similar_users = cls._find_similar_users(user_id)
        candidate_items = Counter()
        for su, sim in similar_users[:20]:
            for action in cls._user_actions.get(su, []):
                if action["item_id"] not in user_items:
                    candidate_items[action["item_id"]] += sim

        # 鍩轰簬鍐呭鐨勬帹鑽?
        user_categories = Counter()
        for item_id in user_items:
            if item_id in cls._item_features:
                cat = cls._item_features[item_id].get("category", "")
                if cat:
                    user_categories[cat] += 1

        for item_id, features in cls._item_features.items():
            if item_id not in user_items and features.get("category") in user_categories:
                candidate_items[item_id] += user_categories[features["category"]] * 0.5

        # 鎺掑簭杩斿洖
        ranked = candidate_items.most_common(top_k)
        return [{"item_id": item_id, "score": round(score, 2), "features": cls._item_features.get(item_id, {})}
                for item_id, score in ranked]

    @classmethod
    def _find_similar_users(cls, user_id: str, top_k: int = 30) -> List[tuple]:
        """鎵剧浉浼肩敤鎴?Jaccard)"""
        user_items = set(a["item_id"] for a in cls._user_actions.get(user_id, []))
        if not user_items:
            return []

        similarities = []
        for other_id, actions in cls._user_actions.items():
            if other_id == user_id:
                continue
            other_items = set(a["item_id"] for a in actions)
            intersection = len(user_items & other_items)
            union = len(user_items | other_items)
            if union > 0:
                similarities.append((other_id, round(intersection / union, 3)))

        similarities.sort(key=lambda x: x[1], reverse=True)
        return similarities[:top_k]

    @classmethod
    def recommend_similar_items(cls, item_id: str, top_k: int = 10) -> List[Dict]:
        """鐩镐技鍟嗗搧鎺ㄨ崘"""
        features = cls._item_features.get(item_id, {})
        if not features:
            return []

        category = features.get("category", "")
        similar = []
        for iid, feat in cls._item_features.items():
            if iid != item_id and feat.get("category") == category:
                # 绠€鍗曚环鏍肩浉浼煎害
                p1 = features.get("price", 0)
                p2 = feat.get("price", 0)
                price_sim = 1 - abs(p1 - p2) / max(p1, p2, 1)
                similar.append({"item_id": iid, "score": round(price_sim, 2), "features": feat})

        similar.sort(key=lambda x: x["score"], reverse=True)
        return similar[:top_k]

    @classmethod
    def get_stats(cls) -> Dict:
        return {"total_users": len(cls._user_actions), "total_items": len(cls._item_features),
                "total_actions": sum(len(v) for v in cls._user_actions.values())}

    @classmethod
    def save(cls):
        """持久化到SQLite"""
        from tools.memory_store import memory_store
        import json
        data = {"actions": dict(cls._user_actions), "features": cls._item_features}
        memory_store.set_knowledge("recommend_data", json.dumps(data, ensure_ascii=False))

    @classmethod
    def load(cls):
        """从SQLite恢复"""
        from tools.memory_store import memory_store
        import json
        try:
            data = memory_store.get_knowledge("recommend_data")
            if data:
                d = json.loads(data)
                cls._user_actions.update(d.get("actions", {}))
                cls._item_features.update(d.get("features", {}))
            return True
        except:
            return False

recommend_engine = RecommendEngine()

try:
    RecommendEngine.load()
except:
    pass
