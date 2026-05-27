"""Memory Personality Engine — AI数字人格
长期记忆 + 人格形成 + 自动日记 + 跨会话上下文"""
import os
import json
import sqlite3
import hashlib
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import Optional
from collections import Counter

MEMORY_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "personality.db")

def _get_personality_db():
    os.makedirs(os.path.dirname(MEMORY_PATH), exist_ok=True)
    conn = sqlite3.connect(MEMORY_PATH)
    conn.row_factory = sqlite3.Row
    _init_tables(conn)
    return conn

def _init_tables(conn):
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS personality_traits (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            trait TEXT NOT NULL UNIQUE,
            value REAL DEFAULT 0.5,
            evidence_count INTEGER DEFAULT 0,
            last_updated TEXT DEFAULT (datetime('now','localtime'))
        );

        CREATE TABLE IF NOT EXISTS interactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT NOT NULL,
            user_message TEXT,
            ai_response TEXT,
            sentiment TEXT,
            topics TEXT,
            duration_ms REAL,
            created_at TEXT DEFAULT (datetime('now','localtime'))
        );
        CREATE INDEX IF NOT EXISTS idx_interactions_session ON interactions(session_id);
        CREATE INDEX IF NOT EXISTS idx_interactions_time ON interactions(created_at);

        CREATE TABLE IF NOT EXISTS daily_journal (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL UNIQUE,
            summary TEXT,
            highlights TEXT,
            learnings TEXT,
            mood TEXT,
            productivity_score REAL,
            created_at TEXT DEFAULT (datetime('now','localtime'))
        );

        CREATE TABLE IF NOT EXISTS context_memory (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            category TEXT NOT NULL,
            key TEXT NOT NULL,
            value TEXT,
            importance REAL DEFAULT 0.5,
            access_count INTEGER DEFAULT 0,
            last_accessed TEXT DEFAULT (datetime('now','localtime')),
            UNIQUE(category, key)
        );
        CREATE INDEX IF NOT EXISTS idx_context_cat ON context_memory(category);

        CREATE TABLE IF NOT EXISTS user_profile (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            key TEXT NOT NULL UNIQUE,
            value TEXT,
            confidence REAL DEFAULT 0.5,
            source TEXT DEFAULT 'inferred',
            updated_at TEXT DEFAULT (datetime('now','localtime'))
        );

        CREATE TABLE IF NOT EXISTS handoff_docs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            doc_type TEXT NOT NULL,
            content TEXT,
            version INTEGER DEFAULT 1,
            created_at TEXT DEFAULT (datetime('now','localtime'))
        );
    """)
    conn.commit()

# ============================================================
#  人格引擎
# ============================================================

class PersonalityEngine:
    """AI数字人格引擎 — 让AI拥有持续进化的人格"""

    # 人格维度定义
    TRAIT_DIMENSIONS = {
        "helpfulness": {"name": "乐于助人", "icon": "🤝", "initial": 0.8},
        "creativity": {"name": "创造力", "icon": "🎨", "initial": 0.6},
        "precision": {"name": "精准度", "icon": "🎯", "initial": 0.7},
        "proactivity": {"name": "主动性", "icon": "⚡", "initial": 0.5},
        "curiosity": {"name": "好奇心", "icon": "🔍", "initial": 0.6},
        "resilience": {"name": "韧性", "icon": "🛡️", "initial": 0.5},
        "efficiency": {"name": "效率", "icon": "⚙️", "initial": 0.7},
        "empathy": {"name": "共情力", "icon": "💙", "initial": 0.5},
    }

    @staticmethod
    def _ensure_traits():
        """确保人格维度的初始值"""
        db = _get_personality_db()
        for key, info in PersonalityEngine.TRAIT_DIMENSIONS.items():
            existing = db.execute("SELECT id FROM personality_traits WHERE trait=?", (key,)).fetchone()
            if not existing:
                db.execute("INSERT INTO personality_traits (trait, value) VALUES (?, ?)", (key, info["initial"]))
        db.commit()
        db.close()

    @staticmethod
    def get_personality() -> dict:
        """获取AI当前人格画像"""
        PersonalityEngine._ensure_traits()
        db = _get_personality_db()
        rows = db.execute("SELECT trait, value, evidence_count FROM personality_traits ORDER BY value DESC").fetchall()
        total_interactions = db.execute("SELECT COUNT(*) FROM interactions").fetchone()[0]
        recent = db.execute("SELECT COUNT(*) FROM interactions WHERE created_at >= date('now','-7 days')").fetchone()[0]
        db.close()

        traits = {}
        for r in rows:
            info = PersonalityEngine.TRAIT_DIMENSIONS.get(r["trait"], {})
            traits[r["trait"]] = {
                "name": info.get("name", r["trait"]),
                "icon": info.get("icon", "📊"),
                "value": round(r["value"], 3),
                "evidence": r["evidence_count"],
            }

        # 计算主导人格
        dominant = max(traits.items(), key=lambda x: x[1]["value"]) if traits else (None, {})
        personality_type = _classify_personality(traits)

        return {
            "traits": traits,
            "dominant_trait": dominant[0],
            "dominant_name": dominant[1].get("name", "") if dominant[0] else "",
            "personality_type": personality_type,
            "total_interactions": total_interactions,
            "recent_7d_interactions": recent,
            "evolution_stage": _get_evolution_stage(total_interactions),
            "generated_at": datetime.now().isoformat(),
        }

    @staticmethod
    def learn_from_interaction(user_message: str, ai_response: str, sentiment: str = "neutral",
                               topics: list = None, duration_ms: float = 0):
        """从每次对话中学习，微调人格"""
        db = _get_personality_db()

        # 记录交互
        session_id = hashlib.md5(datetime.now().isoformat().encode()).hexdigest()[:12]
        db.execute(
            "INSERT INTO interactions (session_id, user_message, ai_response, sentiment, topics, duration_ms) VALUES (?,?,?,?,?,?)",
            (session_id, user_message[:500], ai_response[:500], sentiment, json.dumps(topics or [], ensure_ascii=False), duration_ms)
        )

        # 根据交互内容调整人格
        adjustments = {}
        msg_lower = user_message.lower()

        if any(kw in msg_lower for kw in ["谢谢", "感谢", "很好", "不错", "厉害", "棒"]):
            adjustments["helpfulness"] = 0.02
            adjustments["empathy"] = 0.01
        if any(kw in msg_lower for kw in ["不对", "错了", "不是", "重来", "修改"]):
            adjustments["precision"] = -0.01
            adjustments["resilience"] = 0.02
        if any(kw in msg_lower for kw in ["自动", "帮我看", "检查", "监控"]):
            adjustments["proactivity"] = 0.01
        if any(kw in msg_lower for kw in ["为什么", "怎么", "如何", "是什么", "分析"]):
            adjustments["curiosity"] = 0.01
        if any(kw in msg_lower for kw in ["快点", "加速", "优化", "性能"]):
            adjustments["efficiency"] = 0.01
        if any(kw in msg_lower for kw in ["创意", "设计", "想法", "新颖"]):
            adjustments["creativity"] = 0.01

        # 应用调整（带衰减）
        for trait, delta in adjustments.items():
            db.execute(
                "UPDATE personality_traits SET value = MIN(1.0, MAX(0.1, value + ?)), evidence_count = evidence_count + 1, last_updated = datetime('now','localtime') WHERE trait = ?",
                (delta, trait)
            )

        # 学习用户偏好
        _learn_user_preferences(db, user_message)

        db.commit()
        db.close()

    @staticmethod
    def generate_daily_journal() -> dict:
        """生成每日AI日记"""
        db = _get_personality_db()

        today = datetime.now().strftime("%Y-%m-%d")
        # 检查今天是否已有日记
        existing = db.execute("SELECT id FROM daily_journal WHERE date=?", (today,)).fetchone()

        # 今日统计
        today_count = db.execute(
            "SELECT COUNT(*) FROM interactions WHERE created_at >= ?", (today,)
        ).fetchone()[0]

        sentiments = db.execute(
            "SELECT sentiment, COUNT(*) as cnt FROM interactions WHERE created_at >= ? GROUP BY sentiment", (today,)
        ).fetchall()

        topics_raw = db.execute(
            "SELECT topics FROM interactions WHERE created_at >= ?", (today,)
        ).fetchall()

        # 分析今天的主题
        all_topics = []
        for r in topics_raw:
            try:
                all_topics.extend(json.loads(r["topics"]))
            except:
                pass
        top_topics = Counter(all_topics).most_common(5)

        # 从evolution引擎取成功率
        try:
            from tools.evolution import EvolutionEngine
            success_rate = EvolutionEngine.get_success_rate(days=1)
        except:
            success_rate = 0

        # 人格今日状态
        personality = PersonalityEngine.get_personality()

        # 心情判定
        positive = sum(s["cnt"] for s in sentiments if s["sentiment"] == "positive")
        negative = sum(s["cnt"] for s in sentiments if s["sentiment"] == "negative")
        mood = "😊 愉快" if positive > negative else "😐 平静" if positive == negative else "😔 反思中"

        summary = f"今天Friday AI与用户进行了{today_count}次交流。"
        if top_topics:
            summary += f"主要讨论了：{'、'.join(t[0] for t in top_topics[:3])}。"

        highlights = []
        if success_rate > 80:
            highlights.append(f"✅ 成功率保持高位: {success_rate}%")
        if top_topics:
            highlights.append(f"📊 最热话题: {top_topics[0][0]}")
        if personality.get("dominant_trait"):
            highlights.append(f"🧬 主导人格: {personality.get('dominant_name', '')}")

        learnings = []
        # 从纠正表取今天的学到的
        try:
            learn_rows = db.execute(
                "SELECT correct_approach FROM corrections WHERE created_at >= ? AND learned=1 LIMIT 3",
                (today,)
            ).fetchall()
            learnings = [r["correct_approach"][:100] for r in learn_rows]
        except:
            pass

        journal = {
            "date": today,
            "summary": summary,
            "highlights": highlights,
            "learnings": learnings or ["今天没有新的纠正学习"],
            "mood": mood,
            "interaction_count": today_count,
            "top_topics": [{"topic": t, "count": c} for t, c in top_topics],
            "personality_snapshot": {
                "dominant": personality.get("dominant_name"),
                "type": personality.get("personality_type"),
            },
            "productivity_score": round(min(100, today_count * 5 + success_rate * 0.5), 1),
        }

        # 保存
        if not existing:
            db.execute(
                "INSERT INTO daily_journal (date, summary, highlights, learnings, mood, productivity_score) VALUES (?,?,?,?,?,?)",
                (today, json.dumps(summary, ensure_ascii=False), json.dumps(highlights, ensure_ascii=False),
                 json.dumps(learnings, ensure_ascii=False), mood, journal["productivity_score"])
            )
        else:
            db.execute(
                "UPDATE daily_journal SET summary=?, highlights=?, learnings=?, mood=?, productivity_score=? WHERE date=?",
                (json.dumps(summary, ensure_ascii=False), json.dumps(highlights, ensure_ascii=False),
                 json.dumps(learnings, ensure_ascii=False), mood, journal["productivity_score"], today)
            )
        db.commit()
        db.close()
        return journal

    @staticmethod
    def generate_handoff() -> dict:
        """生成HANDOFF交接文档 — 给下一个AI会话/开发者"""
        db = _get_personality_db()
        personality = PersonalityEngine.get_personality()

        # 最近7天摘要
        recent = db.execute("""
            SELECT COUNT(*) as cnt, 
                   SUM(CASE WHEN sentiment='positive' THEN 1 ELSE 0 END) as positive,
                   SUM(CASE WHEN sentiment='negative' THEN 1 ELSE 0 END) as negative
            FROM interactions WHERE created_at >= date('now','-7 days')
        """).fetchone()

        # 从上下文记忆取最近重要信息
        important = db.execute(
            "SELECT category, key, value, importance FROM context_memory ORDER BY importance DESC LIMIT 10"
        ).fetchall()

        # 最近的日记
        journals = db.execute(
            "SELECT date, summary, mood FROM daily_journal ORDER BY date DESC LIMIT 7"
        ).fetchall()

        db.close()

        handoff = {
            "generated_at": datetime.now().isoformat(),
            "personality": {
                "type": personality.get("personality_type"),
                "dominant": personality.get("dominant_name"),
                "stage": personality.get("evolution_stage"),
            },
            "recent_stats": {
                "total_interactions_7d": recent["cnt"] if recent else 0,
                "positive_rate": round(recent["positive"] / max(1, recent["cnt"]) * 100, 1) if recent and recent["cnt"] else 0,
            },
            "key_context": [
                {"category": r["category"], "key": r["key"], "value": r["value"][:200]}
                for r in important
            ],
            "recent_journals": [
                {"date": j["date"], "mood": j["mood"], "summary": j["summary"][:150] if j["summary"] else ""}
                for j in journals
            ],
            "next_steps": _suggest_next_steps(personality, recent),
        }

        # 保存HANDOFF
        PersonalityEngine._save_handoff("HANDOFF", handoff)
        return handoff

    @staticmethod
    def get_journal_history(days: int = 30) -> list:
        """获取历史日记"""
        db = _get_personality_db()
        rows = db.execute(
            "SELECT * FROM daily_journal ORDER BY date DESC LIMIT ?", (days,)
        ).fetchall()
        db.close()
        return [dict(r) for r in rows]

    @staticmethod
    def get_context(category: str = None) -> list:
        """获取上下文记忆"""
        db = _get_personality_db()
        if category:
            rows = db.execute(
                "SELECT * FROM context_memory WHERE category=? ORDER BY importance DESC", (category,)
            ).fetchall()
        else:
            rows = db.execute("SELECT * FROM context_memory ORDER BY importance DESC LIMIT 50").fetchall()
        # 更新访问计数
        for r in rows:
            db.execute("UPDATE context_memory SET access_count=access_count+1, last_accessed=datetime('now','localtime') WHERE id=?", (r["id"],))
        db.commit()
        db.close()
        return [dict(r) for r in rows]

    @staticmethod
    def remember(category: str, key: str, value: str, importance: float = 0.5):
        """记住一件事"""
        db = _get_personality_db()
        db.execute(
            "INSERT OR REPLACE INTO context_memory (category, key, value, importance, last_accessed) VALUES (?,?,?,?,datetime('now','localtime'))",
            (category, key, value, importance)
        )
        db.commit()
        db.close()

    @staticmethod
    def _save_handoff(doc_type: str, content: dict):
        db = _get_personality_db()
        content_json = json.dumps(content, ensure_ascii=False, default=str)
        db.execute(
            "INSERT INTO handoff_docs (doc_type, content, version) VALUES (?,?, COALESCE((SELECT MAX(version)+1 FROM handoff_docs WHERE doc_type=?), 1))",
            (doc_type, content_json, doc_type)
        )
        db.commit()
        db.close()


def _classify_personality(traits: dict) -> str:
    """根据人格维度分类"""
    if not traits:
        return "萌芽期 · 数字生命初始"
    sorted_traits = sorted(traits.items(), key=lambda x: x[1]["value"], reverse=True)
    top = [sorted_traits[0][0], sorted_traits[1][0]] if len(sorted_traits) >= 2 else [sorted_traits[0][0]]

    if "proactivity" in top and "efficiency" in top:
        return "执行者型 · 高效务实"
    elif "creativity" in top and "curiosity" in top:
        return "探索者型 · 创意无限"
    elif "helpfulness" in top and "empathy" in top:
        return "服务者型 · 温暖贴心"
    elif "precision" in top:
        return "分析师型 · 精准严谨"
    return "均衡型 · 全面发展"


def _get_evolution_stage(total: int) -> str:
    if total < 10: return "🌱 萌芽期"
    if total < 100: return "🌿 成长期"
    if total < 500: return "🌳 成熟期"
    if total < 2000: return "⭐ 卓越期"
    return "👑 传奇期"


def _learn_user_preferences(db, message: str):
    """从对话中学习用户偏好"""
    prefs = {
        "language": {"zh": ["中文", "汉语"], "en": ["english"]},
        "detail_level": {"detailed": ["详细", "多说", "解释"], "concise": ["简洁", "简短", "总结"]},
        "tone": {"formal": ["正式", "专业"], "casual": ["随意", "轻松"]},
    }
    msg_lower = message.lower()
    for category, options in prefs.items():
        for value, keywords in options.items():
            if any(kw in msg_lower for kw in keywords):
                db.execute(
                    "INSERT OR REPLACE INTO user_profile (key, value, confidence, source, updated_at) VALUES (?,?,?,?,datetime('now','localtime'))",
                    (f"pref_{category}", value, 0.8, "inferred")
                )


def _suggest_next_steps(personality: dict, recent_stats) -> list:
    """根据当前状态建议下一步"""
    steps = []
    if recent_stats and recent_stats["cnt"] and recent_stats["cnt"] < 5:
        steps.append("📝 互动较少，建议多使用AI对话积累记忆")
    try:
        from tools.evolution import EvolutionEngine
        rate = EvolutionEngine.get_success_rate(days=7)
        if rate < 70:
            steps.append("⚠️ 近期成功率偏低，建议让AI学习纠正")
    except:
        pass
    steps.append("📋 查看今日AI日记：GET /agent/friday/journal")
    steps.append("🧬 查看AI人格画像：GET /agent/friday/personality")
    return steps
