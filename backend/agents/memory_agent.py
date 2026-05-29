"""Memory Agent 鈥?闀挎湡璁板繂/鐢ㄦ埛涔犳儻/椤圭洰鐘舵€?Bug鍘嗗彶/鑷姩鎬荤粨
鑱岃矗锛氳褰曚竴鍒囥€佹绱㈠巻鍙层€佸涔犳ā寮忋€佸叧鑱旂煡璇?""
import json
import os
import hashlib
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Memory:
    """鍗曟潯璁板繂"""
    id: str
    category: str  # user_pref / project / bug / decision / learning
    content: str
    tags: list = field(default_factory=list)
    importance: int = 1  # 1-5
    created_at: str = ""
    last_accessed: str = ""
    access_count: int = 0
    related_memories: list = field(default_factory=list)


class MemoryAgent:
    """Memory Agent 鈥?鏁板瓧澶ц剳鐨勬捣椹綋"""

    MEMORY_DIR = os.getenv("APP_MEMORY_DIR", "memory")
    MEMORY_FILE = os.path.join(os.getenv("APP_MEMORY_DIR", "memory"), "agent_memory.json")

    @staticmethod
    def _ensure_dir():
        os.makedirs(MemoryAgent.MEMORY_DIR, exist_ok=True)

    @staticmethod
    def _load_memories() -> list:
        MemoryAgent._ensure_dir()
        if not os.path.exists(MemoryAgent.MEMORY_FILE):
            return []
        try:
            with open(MemoryAgent.MEMORY_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []

    @staticmethod
    def _save_memories(memories: list):
        MemoryAgent._ensure_dir()
        with open(MemoryAgent.MEMORY_FILE, "w", encoding="utf-8") as f:
            json.dump(memories, f, ensure_ascii=False, indent=2)

    @staticmethod
    async def remember(content: str, category: str = "general", importance: int = 1, tags: list = None) -> dict:
        """淇濆瓨涓€鏉¤蹇?""
        memories = MemoryAgent._load_memories()
        mem = {
            "id": hashlib.md5(f"{category}:{content}:{datetime.now().isoformat()}".encode()).hexdigest()[:12],
            "category": category,
            "content": content,
            "tags": tags or [],
            "importance": importance,
            "created_at": datetime.now().isoformat(),
            "last_accessed": datetime.now().isoformat(),
            "access_count": 1,
            "related_memories": [],
        }
        memories.insert(0, mem)
        # 闄愬埗鎬绘暟
        if len(memories) > 10000:
            # 淇濈暀閲嶈鐨勶紝鍒犻櫎鏃х殑
            memories.sort(key=lambda x: (x.get("importance", 1), x.get("access_count", 0)), reverse=True)
            memories = memories[:10000]
        MemoryAgent._save_memories(memories)
        return {"ok": True, "memory_id": mem["id"], "category": category}

    @staticmethod
    async def recall(query: str = None, category: str = None, tags: list = None, limit: int = 20) -> dict:
        """妫€绱㈣蹇?""
        memories = MemoryAgent._load_memories()
        results = []

        for mem in memories:
            score = 0
            # 鍒嗙被鍖归厤
            if category and mem.get("category") == category:
                score += 3
            # 鏍囩鍖归厤
            if tags:
                mem_tags = set(mem.get("tags", []))
                query_tags = set(tags)
                score += len(mem_tags & query_tags) * 2
            # 鍐呭鍖归厤
            if query:
                content_lower = mem.get("content", "").lower()
                for word in query.lower().split():
                    if word in content_lower:
                        score += 1
            if score > 0 or not query:
                mem["_score"] = score
                results.append(mem)

        results.sort(key=lambda x: (x.get("importance", 1), x.get("_score", 0)), reverse=True)
        results = results[:limit]

        # 鏇存柊璁块棶璁℃暟
        for r in results:
            r["last_accessed"] = datetime.now().isoformat()
            r["access_count"] = r.get("access_count", 0) + 1
        MemoryAgent._save_memories(memories)

        return {
            "ok": True,
            "query": query,
            "found": len(results),
            "memories": [{k: v for k, v in m.items() if k != "_score"} for m in results],
        }

    @staticmethod
    async def learn_from_conversation(user_message: str, ai_response: str, topic: str = "") -> dict:
        """浠庡璇濅腑瀛︿範"""
        memories = MemoryAgent._load_memories()

        # 鎻愬彇鍏抽敭淇℃伅
        keywords = MemoryAgent._extract_keywords(user_message)
        summary = ai_response[:200] if len(ai_response) > 200 else ai_response

        learnings = [
            {"category": "conversation", "content": f"鐢ㄦ埛: {user_message[:100]}", "tags": keywords, "importance": 2},
            {"category": "learning", "content": f"AI瀛︿範: {summary}", "tags": keywords + [topic] if topic else keywords, "importance": 3},
        ]

        for l in learnings:
            mem = {
                "id": hashlib.md5(f"{l['category']}:{l['content']}:{datetime.now().isoformat()}".encode()).hexdigest()[:12],
                "category": l["category"],
                "content": l["content"],
                "tags": l["tags"],
                "importance": l["importance"],
                "created_at": datetime.now().isoformat(),
                "last_accessed": datetime.now().isoformat(),
                "access_count": 1,
                "related_memories": [],
            }
            memories.insert(0, mem)

        MemoryAgent._save_memories(memories)
        return {"ok": True, "learned": len(learnings), "keywords": keywords}

    @staticmethod
    def _extract_keywords(text: str) -> list:
        """绠€鍗曞叧閿瘝鎻愬彇"""
        stop_words = {"鐨?, "浜?, "鏄?, "鍦?, "鎴?, "鏈?, "鍜?, "灏?, "涓?, "浜?, "閮?, "涓€", "涓€涓?, "涓?, "涔?, "寰?, "鍒?, "璇?, "瑕?, "鍘?, "浣?, "浼?, "鐫€", "娌℃湁", "鐪?, "濂?, "鑷繁", "杩?}
        words = text.replace("锛?, " ").replace("銆?, " ").replace("锛?, " ").replace("锛?, " ").split()
        keywords = [w for w in words if len(w) >= 2 and w not in stop_words]
        return keywords[:10]

    @staticmethod
    async def summarize_memories(category: str = None, days: int = 7) -> dict:
        """鎬荤粨鏈€杩戣蹇?""
        memories = MemoryAgent._load_memories()
        cutoff = (datetime.now() - timedelta(days=days)).isoformat()

        recent = [m for m in memories if m.get("created_at", "") >= cutoff]
        if category:
            recent = [m for m in recent if m.get("category") == category]

        if not recent:
            return {"ok": True, "summary": "鏈€杩戞病鏈夋柊璁板繂", "count": 0}

        categories = {}
        for m in recent:
            cat = m.get("category", "other")
            categories[cat] = categories.get(cat, 0) + 1

        return {
            "ok": True,
            "period": f"鏈€杩憑days}澶?,
            "total": len(recent),
            "categories": categories,
            "top_tags": MemoryAgent._get_top_tags(recent, 10),
            "sample": recent[:3],
        }

    @staticmethod
    def _get_top_tags(memories: list, limit: int = 10) -> list:
        tag_counts = {}
        for m in memories:
            for tag in m.get("tags", []):
                tag_counts[tag] = tag_counts.get(tag, 0) + 1
        sorted_tags = sorted(tag_counts.items(), key=lambda x: x[1], reverse=True)
        return [{"tag": t, "count": c} for t, c in sorted_tags[:limit]]

    @staticmethod
    async def find_related(memory_id: str) -> dict:
        """鎵惧埌鐩稿叧璁板繂"""
        memories = MemoryAgent._load_memories()
        target = next((m for m in memories if m.get("id") == memory_id), None)
        if not target:
            return {"ok": False, "error": "璁板繂涓嶅瓨鍦?}

        target_tags = set(target.get("tags", []))
        related = []
        for m in memories:
            if m.get("id") == memory_id:
                continue
            overlap = len(target_tags & set(m.get("tags", [])))
            if overlap > 0:
                m["_overlap"] = overlap
                related.append(m)

        related.sort(key=lambda x: x.get("_overlap", 0), reverse=True)
        return {
            "ok": True,
            "source": {k: v for k, v in target.items() if k != "_overlap"},
            "related": [{k: v for k, v in m.items() if k not in ("_overlap", "_score")} for m in related[:10]],
        }

    # ===== 鐢ㄦ埛涔犳儻瀛︿範 =====

    @staticmethod
    async def learn_user_habit(habit_type: str, detail: str) -> dict:
        """瀛︿範鐢ㄦ埛涔犳儻"""
        return await MemoryAgent.remember(
            content=f"[涔犳儻] {habit_type}: {detail}",
            category="user_habit",
            importance=4,
            tags=["habit", habit_type],
        )

    @staticmethod
    async def get_user_profile() -> dict:
        """鑾峰彇鐢ㄦ埛鐢诲儚"""
        result = await MemoryAgent.recall(category="user_habit", limit=50)
        habits = [m["content"].replace("[涔犳儻] ", "") for m in result.get("memories", [])]
        return {
            "ok": True,
            "habits_count": len(habits),
            "habits": habits[:20],
            "frequent_topics": MemoryAgent._get_top_tags(result.get("memories", []), 10),
        }

    @staticmethod
    async def cleanup(days_old: int = 30) -> dict:
        """娓呴櫎鏃ц蹇?""
        memories = MemoryAgent._load_memories()
        cutoff = (datetime.now() - timedelta(days=days_old)).isoformat()
        before = len(memories)
        kept = []
        removed = 0
        for m in memories:
            if m.get("created_at", "") < cutoff and m.get("importance", 1) < 3:
                removed += 1
            else:
                kept.append(m)
        MemoryAgent._save_memories(kept)
        return {"ok": True, "before": before, "after": len(kept), "removed": removed}
