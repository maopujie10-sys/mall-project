''"Memory Personality Engine -- AI
 +  +  + ''"
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
    conn.executescript(''"
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
    ''")
    conn.commit()

# ============================================================

# ============================================================

class PersonalityEngine:
    ''"AI -- AI''"

    
    TRAIT_DIMENSIONS = {
        "helpfulness": {"name": '', "icon": "", "initial": 0.8},
        "creativity": {"name": '', "icon": "", "initial": 0.6},
        "precision": {"name": '', "icon": "", "initial": 0.7},
        "proactivity": {"name": '', "icon": "", "initial": 0.5},
        "curiosity": {"name": '', "icon": "", "initial": 0.6},
        "resilience": {"name": '', "icon": "", "initial": 0.5},
        "efficiency": {"name": '', "icon": "", "initial": 0.7},
        "empathy": {"name": '', "icon": "", "initial": 0.5},
    }

    @staticmethod
    def _ensure_traits():
        ''''''
        db = _get_personality_db()
        for key, info in PersonalityEngine.TRAIT_DIMENSIONS.items():
            existing = db.execute("SELECT id FROM personality_traits WHERE trait=?", (key,)).fetchone()
            if not existing:
                db.execute("INSERT INTO personality_traits (trait, value) VALUES (?, ?)", (key, info["initial"]))
        db.commit()
        db.close()

    @staticmethod
    def get_personality() -> dict:
        ''"AI''"
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
                "icon": info.get("icon", ""),
                "value": round(r["value"], 3),
                "evidence": r["evidence_count"],
            }

        
        dominant = max(traits.items(), key=lambda x: x[1]["value"]) if traits else (None, {})
        personality_type = _classify_personality(traits)

        return {
            "traits": traits,
            "dominant_trait": dominant[0],
            "dominant_name": dominant[1].get("name", '') if dominant[0] else '',
            "personality_type": personality_type,
            "total_interactions": total_interactions,
            "recent_7d_interactions": recent,
            "evolution_stage": _get_evolution_stage(total_interactions),
            "generated_at": datetime.now().isoformat(),
        }

    @staticmethod
    def learn_from_interaction(user_message: str, ai_response: str, sentiment: str = "neutral",
                               topics: list = None, duration_ms: float = 0):
        ''",''"
        db = _get_personality_db()

        
        session_id = hashlib.md5(datetime.now().isoformat().encode()).hexdigest()[:12]
        db.execute(
            "INSERT INTO interactions (session_id, user_message, ai_response, sentiment, topics, duration_ms) VALUES (?,?,?,?,?,?)",
            (session_id, user_message[:500], ai_response[:500], sentiment, json.dumps(topics or [], ensure_ascii=False), duration_ms)
        )

        
        adjustments = {}
        msg_lower = user_message.lower()

        if any(kw in msg_lower for kw in ['', '', '', '', '', '']):
            adjustments["helpfulness"] = 0.02
            adjustments["empathy"] = 0.01
        if any(kw in msg_lower for kw in ['', '', '', '', '']):
            adjustments["precision"] = -0.01
            adjustments["resilience"] = 0.02
        if any(kw in msg_lower for kw in ['', '', '', '']):
            adjustments["proactivity"] = 0.01
        if any(kw in msg_lower for kw in ['', '', '', '', '']):
            adjustments["curiosity"] = 0.01
        if any(kw in msg_lower for kw in ['', '', '', '']):
            adjustments["efficiency"] = 0.01
        if any(kw in msg_lower for kw in ['', '', '', '']):
            adjustments["creativity"] = 0.01

        # ()
        for trait, delta in adjustments.items():
            db.execute(
                "UPDATE personality_traits SET value = MIN(1.0, MAX(0.1, value + ?)), evidence_count = evidence_count + 1, last_updated = datetime('now','localtime') WHERE trait = ?",
                (delta, trait)
            )

        
        _learn_user_preferences(db, user_message)

        db.commit()
        db.close()

    @staticmethod
    def generate_daily_journal() -> dict:
        ''"AI''"
        db = _get_personality_db()

        today = datetime.now().strftime("%Y-%m-%d")
        
        existing = db.execute("SELECT id FROM daily_journal WHERE date=?", (today,)).fetchone()

        
        today_count = db.execute(
            "SELECT COUNT(*) FROM interactions WHERE created_at >= ?", (today,)
        ).fetchone()[0]

        sentiments = db.execute(
            "SELECT sentiment, COUNT(*) as cnt FROM interactions WHERE created_at >= ? GROUP BY sentiment", (today,)
        ).fetchall()

        topics_raw = db.execute(
            "SELECT topics FROM interactions WHERE created_at >= ?", (today,)
        ).fetchall()

        
        all_topics = []
        for r in topics_raw:
            try:
                all_topics.extend(json.loads(r["topics"]))
            except Exception:
                pass
        top_topics = Counter(all_topics).most_common(5)

        # evolution
        try:
            from tools.evolution import EvolutionEngine
            success_rate = EvolutionEngine.get_success_rate(days=1)
        except Exception:
            success_rate = 0

        
        personality = PersonalityEngine.get_personality()

        
        positive = sum(s["cnt"] for s in sentiments if s["sentiment"] == "positive")
        negative = sum(s["cnt"] for s in sentiments if s["sentiment"] == "negative")
        mood = " " if positive > negative else " " if positive == negative else " "

        summary = f"Friday AI{today_count}."
        if top_topics:
            summary += f":{''.join(t[0] for t in top_topics[:3])}."

        highlights = []
        if success_rate > 80:
            highlights.append(f" : {success_rate}%")
        if top_topics:
            highlights.append(f" : {top_topics[0][0]}")
        if personality.get("dominant_trait"):
            highlights.append(f" : {personality.get('dominant_name', '')}")

        learnings = []
        
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
            "learnings": learnings or [''],
            "mood": mood,
            "interaction_count": today_count,
            "top_topics": [{"topic": t, "count": c} for t, c in top_topics],
            "personality_snapshot": {
                "dominant": personality.get("dominant_name"),
                "type": personality.get("personality_type"),
            },
            "productivity_score": round(min(100, today_count * 5 + success_rate * 0.5), 1),
        }

        
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
        ''"HANDOFF -- AI/''"
        db = _get_personality_db()
        personality = PersonalityEngine.get_personality()

        # 7
        recent = db.execute(''"
            SELECT COUNT(*) as cnt, 
                   SUM(CASE WHEN sentiment='positive' THEN 1 ELSE 0 END) as positive,
                   SUM(CASE WHEN sentiment='negative' THEN 1 ELSE 0 END) as negative
            FROM interactions WHERE created_at >= date('now','-7 days')
        ''").fetchone()

        
        important = db.execute(
            "SELECT category, key, value, importance FROM context_memory ORDER BY importance DESC LIMIT 10"
        ).fetchall()

        
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
                {"date": j["date"], "mood": j["mood"], "summary": j["summary"][:150] if j["summary"] else ''}
                for j in journals
            ],
            "next_steps": _suggest_next_steps(personality, recent),
        }

        # HANDOFF
        PersonalityEngine._save_handoff("HANDOFF", handoff)
        return handoff

    @staticmethod
    def get_journal_history(days: int = 30) -> list:
        ''''''
        db = _get_personality_db()
        rows = db.execute(
            "SELECT * FROM daily_journal ORDER BY date DESC LIMIT ?", (days,)
        ).fetchall()
        db.close()
        return [dict(r) for r in rows]

    @staticmethod
    def get_context(category: str = None) -> list:
        ''''''
        db = _get_personality_db()
        if category:
            rows = db.execute(
                "SELECT * FROM context_memory WHERE category=? ORDER BY importance DESC", (category,)
            ).fetchall()
        else:
            rows = db.execute("SELECT * FROM context_memory ORDER BY importance DESC LIMIT 50").fetchall()
        
        for r in rows:
            db.execute("UPDATE context_memory SET access_count=access_count+1, last_accessed=datetime('now','localtime') WHERE id=?", (r["id"],))
        db.commit()
        db.close()
        return [dict(r) for r in rows]

    @staticmethod
    def remember(category: str, key: str, value: str, importance: float = 0.5):
        ''''''
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
    ''''''
    if not traits:
        return " - "
    sorted_traits = sorted(traits.items(), key=lambda x: x[1]["value"], reverse=True)
    top = [sorted_traits[0][0], sorted_traits[1][0]] if len(sorted_traits) >= 2 else [sorted_traits[0][0]]

    if "proactivity" in top and "efficiency" in top:
        return " - "
    elif "creativity" in top and "curiosity" in top:
        return " - "
    elif "helpfulness" in top and "empathy" in top:
        return " - "
    elif "precision" in top:
        return " - "
    return " - "


def _get_evolution_stage(total: int) -> str:
    if total < 10: return " "
    if total < 100: return " "
    if total < 500: return " "
    if total < 2000: return " "
    return " "


def _learn_user_preferences(db, message: str):
    ''''''
    prefs = {
        "language": {"zh": ['', ''], "en": ["english"]},
        "detail_level": {"detailed": ['', '', ''], "concise": ['', '', '']},
        "tone": {"formal": ['', ''], "casual": ['', '']},
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
    ''''''
    steps = []
    if recent_stats and recent_stats["cnt"] and recent_stats["cnt"] < 5:
        steps.append(" ,AI")
    try:
        from tools.evolution import EvolutionEngine
        rate = EvolutionEngine.get_success_rate(days=7)
        if rate < 70:
            steps.append(" ,AI")
    except Exception:
        pass
    steps.append(" AI:GET /agent/friday/journal")
    steps.append(" AI:GET /agent/friday/personality")
    return steps

def _save_personality():
    from tools.memory_store import memory_store
    import json
    try:
        data = {"traits": getattr(MemoryPersonality,"_traits",{}), "history": getattr(MemoryPersonality,"_interactions",[])[-100:]}
        memory_store.set_knowledge("personality_data", '', json.dumps(data, ensure_ascii=False, default=str))
    except: pass
def _load_personality():
    from tools.memory_store import memory_store
    import json
    try:
        raw = memory_store.get_knowledge("personality_data")
        if raw and isinstance(raw,list) and raw:
            d = json.loads(raw[0][2] if isinstance(raw[0],tuple) else str(raw[0]))
            if hasattr(MemoryPersonality,"_traits"): MemoryPersonality._traits.update(d.get("traits",{}))
    except: pass
try: _load_personality()
except: pass