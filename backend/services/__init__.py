"""服务层 — 核心业务逻辑
从 Router 中抽离，可复用、可测试"""
from datetime import datetime
from typing import Optional
from tools.memory_store import memory_store
from tools.vector_memory import vector_memory
from digital_lifeform import DigitalLifeform


class SystemService:
    """系统核心服务"""

    @staticmethod
    def get_status() -> dict:
        """获取系统综合状态"""
        mem_stats = memory_store.get_stats()
        vec_stats = vector_memory.get_stats()
        return {
            "mode": "ai_control",
            "time": datetime.now().isoformat(),
            "memory": {
                "conversations": mem_stats["total_conversations"],
                "topics": mem_stats.get("top_topics", []),
            },
            "vector_memory": vec_stats,
            "lifeform": {
                "cycles": DigitalLifeform._cycle_count,
                "mood": DigitalLifeform.get_mood(),
            },
        }

    @staticmethod
    def get_dashboard() -> dict:
        """控制台首页数据"""
        stats = memory_store.get_stats()
        learnings = memory_store.recall_learnings("", 5)
        return {
            "total_memories": stats["total_conversations"],
            "recent_learnings": len(learnings),
            "top_topics": [t["topic"] for t in stats.get("top_topics", [])[:5]],
        }


class MemoryService:
    """记忆服务"""

    @staticmethod
    def search(query: str, limit: int = 10) -> list:
        """搜索记忆"""
        # 优先向量搜索
        vec_results = vector_memory.recall(query, limit)
        if vec_results:
            return vec_results
        # 回退到全文搜索
        return memory_store.search(query, limit)

    @staticmethod
    def remember_fact(category: str, key: str, value: str, confidence: float = 0.7):
        """记住一个知识点"""
        memory_store.set_knowledge(category, key, value, confidence)
        # 同时向量化
        vector_memory.remember(f"[知识] {category}/{key}: {value}", {"type": "knowledge", "category": category})

    @staticmethod
    def recall_context(query: str, limit: int = 5) -> str:
        """获取上下文"""
        # 先向量
        ctx = vector_memory.recall_context(query, limit)
        if ctx:
            return ctx
        # 回退全文
        results = memory_store.search(query, limit)
        if results:
            return "\n".join([f"{r['role']}: {r['content'][:100]}" for r in results])
        return ""


class DiaryService:
    """日记服务 — 自动生成每日报告"""

    @staticmethod
    def generate_daily() -> dict:
        """生成每日日记"""
        today = datetime.now().strftime("%Y-%m-%d")
        stats = memory_store.get_stats()
        learnings = memory_store.recall_learnings("", 50)
        recent = memory_store.recall_recent(30)

        # 分析今日对话主题
        topic_counts = {}
        for r in recent:
            topic = r.get("topic", "未知")
            topic_counts[topic] = topic_counts.get(topic, 0) + 1

        # 今日亮点
        highlights = []
        for l in learnings[:5]:
            if l.get("learned"):
                highlights.append(f"学会了: {l['learned'][:100]}")

        return {
            "date": today,
            "total_memories": stats["total_conversations"],
            "today_conversations": len([r for r in recent if r.get("time", "").startswith(today)]),
            "topics_discussed": sorted(topic_counts.items(), key=lambda x: x[1], reverse=True)[:5],
            "highlights": highlights or ["平静的一天"],
            "mood": DigitalLifeform.get_mood(),
            "summary": f"今日共{len(recent)}段对话，关注{topic_counts}",
        }

    @staticmethod
    def save_journal(journal: dict):
        """保存日记到文件"""
        import json, os
        journal_dir = os.path.join(os.path.dirname(__file__), "..", "..", "memory")
        os.makedirs(journal_dir, exist_ok=True)
        date = journal.get("date", datetime.now().strftime("%Y-%m-%d"))
        path = os.path.join(journal_dir, f"journal_{date}.json")
        with open(path, "w", encoding="utf-8") as f:
            json.dump(journal, f, ensure_ascii=False, indent=2)
        return path