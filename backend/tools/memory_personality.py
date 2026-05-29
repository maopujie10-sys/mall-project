锘?""Memory Personality Engine 鈥?AI鏁板瓧浜烘牸
闀挎湡璁板繂 + 浜烘牸褰㈡垚 + 鑷姩鏃ヨ + 璺ㄤ細璇濅笂涓嬫枃"""
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
#  浜烘牸寮曟搸
# ============================================================

class PersonalityEngine:
    """AI鏁板瓧浜烘牸寮曟搸 鈥?璁〢I鎷ユ湁鎸佺画杩涘寲鐨勪汉鏍?""

    # 浜烘牸缁村害瀹氫箟
    TRAIT_DIMENSIONS = {
        "helpfulness": {"name": "涔愪簬鍔╀汉", "icon": "馃", "initial": 0.8},
        "creativity": {"name": "鍒涢€犲姏", "icon": "馃帹", "initial": 0.6},
        "precision": {"name": "绮惧噯搴?, "icon": "馃幆", "initial": 0.7},
        "proactivity": {"name": "涓诲姩鎬?, "icon": "鈿?, "initial": 0.5},
        "curiosity": {"name": "濂藉蹇?, "icon": "馃攳", "initial": 0.6},
        "resilience": {"name": "闊ф€?, "icon": "馃洝锔?, "initial": 0.5},
        "efficiency": {"name": "鏁堢巼", "icon": "鈿欙笍", "initial": 0.7},
        "empathy": {"name": "鍏辨儏鍔?, "icon": "馃挋", "initial": 0.5},
    }

    @staticmethod
    def _ensure_traits():
        """纭繚浜烘牸缁村害鐨勫垵濮嬪€?""
        db = _get_personality_db()
        for key, info in PersonalityEngine.TRAIT_DIMENSIONS.items():
            existing = db.execute("SELECT id FROM personality_traits WHERE trait=?", (key,)).fetchone()
            if not existing:
                db.execute("INSERT INTO personality_traits (trait, value) VALUES (?, ?)", (key, info["initial"]))
        db.commit()
        db.close()

    @staticmethod
    def get_personality() -> dict:
        """鑾峰彇AI褰撳墠浜烘牸鐢诲儚"""
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
                "icon": info.get("icon", "馃搳"),
                "value": round(r["value"], 3),
                "evidence": r["evidence_count"],
            }

        # 璁＄畻涓诲浜烘牸
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
        """浠庢瘡娆″璇濅腑瀛︿範锛屽井璋冧汉鏍?""
        db = _get_personality_db()

        # 璁板綍浜や簰
        session_id = hashlib.md5(datetime.now().isoformat().encode()).hexdigest()[:12]
        db.execute(
            "INSERT INTO interactions (session_id, user_message, ai_response, sentiment, topics, duration_ms) VALUES (?,?,?,?,?,?)",
            (session_id, user_message[:500], ai_response[:500], sentiment, json.dumps(topics or [], ensure_ascii=False), duration_ms)
        )

        # 鏍规嵁浜や簰鍐呭璋冩暣浜烘牸
        adjustments = {}
        msg_lower = user_message.lower()

        if any(kw in msg_lower for kw in ["璋㈣阿", "鎰熻阿", "寰堝ソ", "涓嶉敊", "鍘夊", "妫?]):
            adjustments["helpfulness"] = 0.02
            adjustments["empathy"] = 0.01
        if any(kw in msg_lower for kw in ["涓嶅", "閿欎簡", "涓嶆槸", "閲嶆潵", "淇敼"]):
            adjustments["precision"] = -0.01
            adjustments["resilience"] = 0.02
        if any(kw in msg_lower for kw in ["鑷姩", "甯垜鐪?, "妫€鏌?, "鐩戞帶"]):
            adjustments["proactivity"] = 0.01
        if any(kw in msg_lower for kw in ["涓轰粈涔?, "鎬庝箞", "濡備綍", "鏄粈涔?, "鍒嗘瀽"]):
            adjustments["curiosity"] = 0.01
        if any(kw in msg_lower for kw in ["蹇偣", "鍔犻€?, "浼樺寲", "鎬ц兘"]):
            adjustments["efficiency"] = 0.01
        if any(kw in msg_lower for kw in ["鍒涙剰", "璁捐", "鎯虫硶", "鏂伴"]):
            adjustments["creativity"] = 0.01

        # 搴旂敤璋冩暣锛堝甫琛板噺锛?
        for trait, delta in adjustments.items():
            db.execute(
                "UPDATE personality_traits SET value = MIN(1.0, MAX(0.1, value + ?)), evidence_count = evidence_count + 1, last_updated = datetime('now','localtime') WHERE trait = ?",
                (delta, trait)
            )

        # 瀛︿範鐢ㄦ埛鍋忓ソ
        _learn_user_preferences(db, user_message)

        db.commit()
        db.close()

    @staticmethod
    def generate_daily_journal() -> dict:
        """鐢熸垚姣忔棩AI鏃ヨ"""
        db = _get_personality_db()

        today = datetime.now().strftime("%Y-%m-%d")
        # 妫€鏌ヤ粖澶╂槸鍚﹀凡鏈夋棩璁?
        existing = db.execute("SELECT id FROM daily_journal WHERE date=?", (today,)).fetchone()

        # 浠婃棩缁熻
        today_count = db.execute(
            "SELECT COUNT(*) FROM interactions WHERE created_at >= ?", (today,)
        ).fetchone()[0]

        sentiments = db.execute(
            "SELECT sentiment, COUNT(*) as cnt FROM interactions WHERE created_at >= ? GROUP BY sentiment", (today,)
        ).fetchall()

        topics_raw = db.execute(
            "SELECT topics FROM interactions WHERE created_at >= ?", (today,)
        ).fetchall()

        # 鍒嗘瀽浠婂ぉ鐨勪富棰?
        all_topics = []
        for r in topics_raw:
            try:
                all_topics.extend(json.loads(r["topics"]))
            except Exception:
                pass
        top_topics = Counter(all_topics).most_common(5)

        # 浠巈volution寮曟搸鍙栨垚鍔熺巼
        try:
            from tools.evolution import EvolutionEngine
            success_rate = EvolutionEngine.get_success_rate(days=1)
        except Exception:
            success_rate = 0

        # 浜烘牸浠婃棩鐘舵€?
        personality = PersonalityEngine.get_personality()

        # 蹇冩儏鍒ゅ畾
        positive = sum(s["cnt"] for s in sentiments if s["sentiment"] == "positive")
        negative = sum(s["cnt"] for s in sentiments if s["sentiment"] == "negative")
        mood = "馃槉 鎰夊揩" if positive > negative else "馃槓 骞抽潤" if positive == negative else "馃様 鍙嶆€濅腑"

        summary = f"浠婂ぉFriday AI涓庣敤鎴疯繘琛屼簡{today_count}娆′氦娴併€?
        if top_topics:
            summary += f"涓昏璁ㄨ浜嗭細{'銆?.join(t[0] for t in top_topics[:3])}銆?

        highlights = []
        if success_rate > 80:
            highlights.append(f"鉁?鎴愬姛鐜囦繚鎸侀珮浣? {success_rate}%")
        if top_topics:
            highlights.append(f"馃搳 鏈€鐑瘽棰? {top_topics[0][0]}")
        if personality.get("dominant_trait"):
            highlights.append(f"馃К 涓诲浜烘牸: {personality.get('dominant_name', '')}")

        learnings = []
        # 浠庣籂姝ｈ〃鍙栦粖澶╃殑瀛﹀埌鐨?
        try:
            learn_rows = db.execute(
                "SELECT correct_approach FROM corrections WHERE created_at >= ? AND learned=1 LIMIT 3",
                (today,)
            ).fetchall()
            learnings = [r["correct_approach"][:100] for r in learn_rows]
        except Exception:
            pass

        journal = {
            "date": today,
            "summary": summary,
            "highlights": highlights,
            "learnings": learnings or ["浠婂ぉ娌℃湁鏂扮殑绾犳瀛︿範"],
            "mood": mood,
            "interaction_count": today_count,
            "top_topics": [{"topic": t, "count": c} for t, c in top_topics],
            "personality_snapshot": {
                "dominant": personality.get("dominant_name"),
                "type": personality.get("personality_type"),
            },
            "productivity_score": round(min(100, today_count * 5 + success_rate * 0.5), 1),
        }

        # 淇濆瓨
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
        """鐢熸垚HANDOFF浜ゆ帴鏂囨。 鈥?缁欎笅涓€涓狝I浼氳瘽/寮€鍙戣€?""
        db = _get_personality_db()
        personality = PersonalityEngine.get_personality()

        # 鏈€杩?澶╂憳瑕?
        recent = db.execute("""
            SELECT COUNT(*) as cnt, 
                   SUM(CASE WHEN sentiment='positive' THEN 1 ELSE 0 END) as positive,
                   SUM(CASE WHEN sentiment='negative' THEN 1 ELSE 0 END) as negative
            FROM interactions WHERE created_at >= date('now','-7 days')
        """).fetchone()

        # 浠庝笂涓嬫枃璁板繂鍙栨渶杩戦噸瑕佷俊鎭?
        important = db.execute(
            "SELECT category, key, value, importance FROM context_memory ORDER BY importance DESC LIMIT 10"
        ).fetchall()

        # 鏈€杩戠殑鏃ヨ
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

        # 淇濆瓨HANDOFF
        PersonalityEngine._save_handoff("HANDOFF", handoff)
        return handoff

    @staticmethod
    def get_journal_history(days: int = 30) -> list:
        """鑾峰彇鍘嗗彶鏃ヨ"""
        db = _get_personality_db()
        rows = db.execute(
            "SELECT * FROM daily_journal ORDER BY date DESC LIMIT ?", (days,)
        ).fetchall()
        db.close()
        return [dict(r) for r in rows]

    @staticmethod
    def get_context(category: str = None) -> list:
        """鑾峰彇涓婁笅鏂囪蹇?""
        db = _get_personality_db()
        if category:
            rows = db.execute(
                "SELECT * FROM context_memory WHERE category=? ORDER BY importance DESC", (category,)
            ).fetchall()
        else:
            rows = db.execute("SELECT * FROM context_memory ORDER BY importance DESC LIMIT 50").fetchall()
        # 鏇存柊璁块棶璁℃暟
        for r in rows:
            db.execute("UPDATE context_memory SET access_count=access_count+1, last_accessed=datetime('now','localtime') WHERE id=?", (r["id"],))
        db.commit()
        db.close()
        return [dict(r) for r in rows]

    @staticmethod
    def remember(category: str, key: str, value: str, importance: float = 0.5):
        """璁颁綇涓€浠朵簨"""
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
    """鏍规嵁浜烘牸缁村害鍒嗙被"""
    if not traits:
        return "钀岃娊鏈?路 鏁板瓧鐢熷懡鍒濆"
    sorted_traits = sorted(traits.items(), key=lambda x: x[1]["value"], reverse=True)
    top = [sorted_traits[0][0], sorted_traits[1][0]] if len(sorted_traits) >= 2 else [sorted_traits[0][0]]

    if "proactivity" in top and "efficiency" in top:
        return "鎵ц鑰呭瀷 路 楂樻晥鍔″疄"
    elif "creativity" in top and "curiosity" in top:
        return "鎺㈢储鑰呭瀷 路 鍒涙剰鏃犻檺"
    elif "helpfulness" in top and "empathy" in top:
        return "鏈嶅姟鑰呭瀷 路 娓╂殩璐村績"
    elif "precision" in top:
        return "鍒嗘瀽甯堝瀷 路 绮惧噯涓ヨ皑"
    return "鍧囪　鍨?路 鍏ㄩ潰鍙戝睍"


def _get_evolution_stage(total: int) -> str:
    if total < 10: return "馃尡 钀岃娊鏈?
    if total < 100: return "馃尶 鎴愰暱鏈?
    if total < 500: return "馃尦 鎴愮啛鏈?
    if total < 2000: return "猸?鍗撹秺鏈?
    return "馃憫 浼犲鏈?


def _learn_user_preferences(db, message: str):
    """浠庡璇濅腑瀛︿範鐢ㄦ埛鍋忓ソ"""
    prefs = {
        "language": {"zh": ["涓枃", "姹夎"], "en": ["english"]},
        "detail_level": {"detailed": ["璇︾粏", "澶氳", "瑙ｉ噴"], "concise": ["绠€娲?, "绠€鐭?, "鎬荤粨"]},
        "tone": {"formal": ["姝ｅ紡", "涓撲笟"], "casual": ["闅忔剰", "杞绘澗"]},
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
    """鏍规嵁褰撳墠鐘舵€佸缓璁笅涓€姝?""
    steps = []
    if recent_stats and recent_stats["cnt"] and recent_stats["cnt"] < 5:
        steps.append("馃摑 浜掑姩杈冨皯锛屽缓璁浣跨敤AI瀵硅瘽绉疮璁板繂")
    try:
        from tools.evolution import EvolutionEngine
        rate = EvolutionEngine.get_success_rate(days=7)
        if rate < 70:
            steps.append("鈿狅笍 杩戞湡鎴愬姛鐜囧亸浣庯紝寤鸿璁〢I瀛︿範绾犳")
    except Exception:
        pass
    steps.append("馃搵 鏌ョ湅浠婃棩AI鏃ヨ锛欸ET /agent/friday/journal")
    steps.append("馃К 鏌ョ湅AI浜烘牸鐢诲儚锛欸ET /agent/friday/personality")
    return steps
