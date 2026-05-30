''"AI  -- /
AI :
    + ()
   (??)
   (,AI )
   ()
   (AI )
''"
import os
import json
import sqlite3
import time
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import Optional
from collections import Counter

MEMORY_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "ai_memory.db")

def _get_db():
    os.makedirs(os.path.dirname(MEMORY_PATH), exist_ok=True)
    conn = sqlite3.connect(MEMORY_PATH)
    conn.row_factory = sqlite3.Row
    _init_tables(conn)
    return conn

def _init_tables(conn):
    conn.executescript(''"
        CREATE TABLE IF NOT EXISTS actions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            action_type TEXT NOT NULL,
            action_name TEXT NOT NULL,
            input_params TEXT,
            result_status TEXT,
            result_detail TEXT,
            duration_ms REAL,
            user_feedback TEXT,
            created_at TEXT DEFAULT (datetime('now','localtime'))
        );
        CREATE INDEX IF NOT EXISTS idx_actions_type ON actions(action_type);
        CREATE INDEX IF NOT EXISTS idx_actions_status ON actions(result_status);
        CREATE INDEX IF NOT EXISTS idx_actions_time ON actions(created_at);

        CREATE TABLE IF NOT EXISTS learning (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            category TEXT NOT NULL,
            key TEXT NOT NULL,
            value TEXT,
            score REAL DEFAULT 0.5,
            evidence_count INTEGER DEFAULT 1,
            last_updated TEXT DEFAULT (datetime('now','localtime')),
            UNIQUE(category, key)
        );
        CREATE INDEX IF NOT EXISTS idx_learning_cat ON learning(category);

        CREATE TABLE IF NOT EXISTS corrections (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            original_action TEXT,
            user_said TEXT NOT NULL,
            correct_approach TEXT NOT NULL,
            context TEXT,
            learned INTEGER DEFAULT 0,
            created_at TEXT DEFAULT (datetime('now','localtime'))
        );

        CREATE TABLE IF NOT EXISTS evolution_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            event_type TEXT NOT NULL,
            description TEXT,
            metrics TEXT,
            created_at TEXT DEFAULT (datetime('now','localtime'))
        );
    ''")
    conn.commit()


class EvolutionEngine:
    ''"AI ''"

    @staticmethod
    def log_action(action_type: str, action_name: str, input_params: dict = None,
                   result_status: str = "success", result_detail: str = '', duration_ms: float = 0):
        ''" AI  -- AI ''"
        db = _get_db()
        db.execute(
            "INSERT INTO actions (action_type, action_name, input_params, result_status, result_detail, duration_ms) VALUES (?,?,?,?,?,?)",
            (action_type, action_name, json.dumps(input_params or {}, ensure_ascii=False), result_status, result_detail, duration_ms)
        )
        db.commit()
        db.close()

    @staticmethod
    def get_action_history(action_type: str = None, limit: int = 50) -> list[dict]:
        ''" AI ''"
        db = _get_db()
        if action_type:
            rows = db.execute("SELECT * FROM actions WHERE action_type=? ORDER BY id DESC LIMIT ?", (action_type, limit)).fetchall()
        else:
            rows = db.execute("SELECT * FROM actions ORDER BY id DESC LIMIT ?", (limit,)).fetchall()
        db.close()
        return [dict(r) for r in rows]

    @staticmethod
    def get_success_rate(action_type: str = None, days: int = 30) -> float:
        ''" AI ''"
        db = _get_db()
        since = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
        if action_type:
            total = db.execute("SELECT COUNT(*) FROM actions WHERE action_type=? AND created_at>=?", (action_type, since)).fetchone()[0]
            ok = db.execute("SELECT COUNT(*) FROM actions WHERE action_type=? AND result_status='success' AND created_at>=?", (action_type, since)).fetchone()[0]
        else:
            total = db.execute("SELECT COUNT(*) FROM actions WHERE created_at>=?", (since,)).fetchone()[0]
            ok = db.execute("SELECT COUNT(*) FROM actions WHERE result_status='success' AND created_at>=?", (since,)).fetchone()[0]
        db.close()
        return round(ok / total * 100, 1) if total > 0 else 100.0

    
    
    @staticmethod
    def learn(category: str, key: str, value: str = None, score: float = None):
        ''"AI  -- eBay  85%''"
        db = _get_db()
        existing = db.execute("SELECT * FROM learning WHERE category=? AND key=?", (category, key)).fetchone()
        if existing:
            new_count = existing["evidence_count"] + 1
            new_score = ((existing["score"] * existing["evidence_count"]) + (score or 0.5)) / new_count
            db.execute("UPDATE learning SET score=?, evidence_count=?, value=COALESCE(?,value), last_updated=datetime('now','localtime') WHERE id=?",
                       (new_score, new_count, value, existing["id"]))
        else:
            db.execute("INSERT INTO learning (category, key, value, score) VALUES (?,?,?,?)", (category, key, value, score or 0.5))
        db.commit()
        db.close()

    @staticmethod
    def get_knowledge(category: str, min_score: float = 0.0) -> list[dict]:
        ''" AI ''"
        db = _get_db()
        rows = db.execute("SELECT * FROM learning WHERE category=? AND score>=? ORDER BY score DESC", (category, min_score)).fetchall()
        db.close()
        return [dict(r) for r in rows]

    @staticmethod
    def get_best_strategy(category: str) -> Optional[dict]:
        ''"AI ''"
        knowledge = EvolutionEngine.get_knowledge(category, min_score=0.3)
        if knowledge:
            return max(knowledge, key=lambda k: k["score"] * k["evidence_count"])
        return None

    
    
    @staticmethod
    def learn_from_correction(original_action: str, user_said: str, correct_approach: str, context: str = ''):
        ''" AI ,AI ''"
        db = _get_db()
        db.execute(
            "INSERT INTO corrections (original_action, user_said, correct_approach, context) VALUES (?,?,?,?)",
            (original_action, user_said, correct_approach, context)
        )
        
        EvolutionEngine.learn("correction", user_said[:50], correct_approach, score=0.9)
        db.commit()
        db.close()

    @staticmethod
    def get_corrections(learned: int = 0) -> list[dict]:
        ''''''
        db = _get_db()
        rows = db.execute("SELECT * FROM corrections WHERE learned=? ORDER BY id DESC", (learned,)).fetchall()
        db.close()
        return [dict(r) for r in rows]

    @staticmethod
    def mark_correction_learned(correction_id: int):
        ''''''
        db = _get_db()
        db.execute("UPDATE corrections SET learned=1 WHERE id=?", (correction_id,))
        db.commit()
        db.close()

    
    
    @staticmethod
    def evolve_report() -> dict:
        ''"AI  -- AI ''"
        db = _get_db()

        
        total_actions = db.execute("SELECT COUNT(*) FROM actions").fetchone()[0]
        recent_actions = db.execute("SELECT COUNT(*) FROM actions WHERE created_at >= date('now','-7 days')").fetchone()[0]

        
        success_rate = EvolutionEngine.get_success_rate(days=30)
        last_week_rate = EvolutionEngine.get_success_rate(days=7)

        
        top_actions = db.execute("SELECT action_name, COUNT(*) as cnt FROM actions GROUP BY action_name ORDER BY cnt DESC LIMIT 5").fetchall()

        
        total_learned = db.execute("SELECT COUNT(*) FROM learning").fetchone()[0]
        top_knowledge = db.execute("SELECT category, key, score FROM learning WHERE score > 0.6 ORDER BY score DESC LIMIT 10").fetchall()

        
        corrections = db.execute("SELECT COUNT(*) FROM corrections").fetchone()[0]
        learned_corrections = db.execute("SELECT COUNT(*) FROM corrections WHERE learned=1").fetchone()[0]

        
        cat_performance = db.execute(''"
            SELECT json_extract(input_params, '$.platform') as platform, 
                   COUNT(*) as total, 
                   SUM(CASE WHEN result_status='success' THEN 1 ELSE 0 END) as ok
            FROM actions WHERE action_type='scraper'
            GROUP BY platform
        ''").fetchall()

        db.close()

        
        suggestions = []
        if last_week_rate > success_rate:
            suggestions.append(f" AI  {last_week_rate - success_rate:.1f}%,")
        if learned_corrections < corrections:
            suggestions.append(f"  {corrections - learned_corrections} ,AI")
        for ca in cat_performance:
            rate = ca["ok"] / ca["total"] * 100 if ca["total"] > 0 else 0
            if rate > 80:
                suggestions.append(f"  {ca['platform']}  {rate:.0f}%,")
            elif rate < 50 and ca["total"] > 3:
                suggestions.append(f"  {ca['platform']}  {rate:.0f}%,")

        if total_actions < 10:
            suggestions.append(" AI , AI ")

        return {
            "generated_at": datetime.now().isoformat(),
            "summary": {
                "total_actions": total_actions,
                "recent_7d_actions": recent_actions,
                "success_rate_30d": success_rate,
                "success_rate_7d": last_week_rate,
                "trend": " " if last_week_rate > success_rate else " " if last_week_rate < success_rate else " ",
                "knowledge_items": total_learned,
                "corrections": corrections,
                "corrections_learned": learned_corrections,
            },
            "top_actions": [{"name": a["action_name"], "count": a["cnt"]} for a in top_actions],
            "top_knowledge": [{"category": k["category"], "key": k["key"], "score": round(k["score"], 2)} for k in top_knowledge],
            "platform_performance": [{"platform": c["platform"], "total": c["total"], "success_rate": round(c["ok"]/c["total"]*100, 1) if c["total"] > 0 else 0} for c in cat_performance],
            "suggestions": suggestions,
        }

    
    #  ()
    
    @staticmethod
    def record_scrape(source: str, keyword: str, count: int, success: bool):
        ''''''
        EvolutionEngine.log_action(
            "scraper", f":{source}:{keyword}",
            {"platform": source, "keyword": keyword, "count": count},
            "success" if success else "failed",
            f" {count} " if success else ''
        )
        if success:
            EvolutionEngine.learn("scraper_sources", source, keyword, score=0.7)

    @staticmethod
    def record_product_replace(old_title: str, new_title: str, success: bool):
        ''''''
        EvolutionEngine.log_action(
            "replace", f'',
            {"old": old_title, "new": new_title},
            "success" if success else "failed",
        )

    @staticmethod
    def record_health_check(total: int, dead: int, hot: int):
        ''''''
        EvolutionEngine.log_action(
            "health", '',
            {"total": total, "dead": dead, "hot": hot},
            "success",
            f"total={total} dead={dead} hot={hot}"
        )

def _save_evolution():
    from tools.memory_store import memory_store
    import json
    try:
        data = {"metrics": getattr(EvolutionTracker,"_metrics",{}), "reports": getattr(EvolutionTracker,"_reports",[])[-20:]}
        memory_store.set_knowledge("evolution_data", '', json.dumps(data, ensure_ascii=False, default=str))
    except: pass
def _load_evolution():
    from tools.memory_store import memory_store
    import json
    try:
        raw = memory_store.get_knowledge("evolution_data")
        if raw and isinstance(raw,list) and raw:
            d = json.loads(raw[0][2] if isinstance(raw[0],tuple) else str(raw[0]))
            if hasattr(EvolutionTracker,"_metrics"): EvolutionTracker._metrics.update(d.get("metrics",{}))
            if hasattr(EvolutionTracker,"_reports"): EvolutionTracker._reports = d.get("reports",[])
    except: pass
try: _load_evolution()
except: pass