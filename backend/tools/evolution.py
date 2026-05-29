"""AI 鑷垜杩涘寲寮曟搸 鈥?璁板繂/瀛︿範/浼樺寲/杩涘寲

AI 涓嶅啀鏄€屾銆嶇殑:
  鉁?璁颁綇鎵€鏈夎鍔?+ 缁撴灉锛堜粈涔堟垚鍔熴€佷粈涔堝け璐ワ級
  鉁?鑷姩璇勪及绛栫暐鏁堟灉锛堝摢涓噰闆嗘簮鏇村ソ锛熷摢绉嶅晢鍝佹洿鍙楁杩庯紵锛?  鉁?浠庣敤鎴风籂姝ｄ腑瀛︿範锛堣銆屼笉瀵癸紝鍋氳繖涓€岮I 灏辫浣忥級
  鉁?鎰忓浘瑙勫垯鑷姩浼樺寲锛堝父鐢ㄦ寚浠や紭鍏堢骇鑷姩鎻愬崌锛?  鉁?鐢熸垚杩涘寲鎶ュ憡锛圓I 鑷繁鍛婅瘔浣犲畠瀛﹀埌浜嗕粈涔堬級
"""
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
    conn.executescript("""
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
    """)
    conn.commit()

# 鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺?#  琛屽姩璁板繂
# 鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺?
class EvolutionEngine:
    """AI 鑷垜杩涘寲寮曟搸"""

    @staticmethod
    def log_action(action_type: str, action_name: str, input_params: dict = None,
                   result_status: str = "success", result_detail: str = "", duration_ms: float = 0):
        """璁板綍姣忔 AI 琛屽姩 鈥?AI 鐨勩€岃蹇嗐€?""
        db = _get_db()
        db.execute(
            "INSERT INTO actions (action_type, action_name, input_params, result_status, result_detail, duration_ms) VALUES (?,?,?,?,?,?)",
            (action_type, action_name, json.dumps(input_params or {}, ensure_ascii=False), result_status, result_detail, duration_ms)
        )
        db.commit()
        db.close()

    @staticmethod
    def get_action_history(action_type: str = None, limit: int = 50) -> list[dict]:
        """鏌ョ湅 AI 鐨勮鍔ㄥ巻鍙?""
        db = _get_db()
        if action_type:
            rows = db.execute("SELECT * FROM actions WHERE action_type=? ORDER BY id DESC LIMIT ?", (action_type, limit)).fetchall()
        else:
            rows = db.execute("SELECT * FROM actions ORDER BY id DESC LIMIT ?", (limit,)).fetchall()
        db.close()
        return [dict(r) for r in rows]

    @staticmethod
    def get_success_rate(action_type: str = None, days: int = 30) -> float:
        """璁＄畻 AI 琛屽姩鐨勬垚鍔熺巼"""
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

    # 鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺?    #  鐭ヨ瘑瀛︿範
    # 鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺?
    @staticmethod
    def learn(category: str, key: str, value: str = None, score: float = None):
        """AI 瀛﹀埌鏂扮煡璇?鈥?姣斿銆宔Bay 閲囬泦鐢靛瓙浜у搧鎴愬姛鐜?85%銆?""
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
        """鑾峰彇 AI 瀛﹀埌鐨勭煡璇?""
        db = _get_db()
        rows = db.execute("SELECT * FROM learning WHERE category=? AND score>=? ORDER BY score DESC", (category, min_score)).fetchall()
        db.close()
        return [dict(r) for r in rows]

    @staticmethod
    def get_best_strategy(category: str) -> Optional[dict]:
        """AI 閫夋嫨鏈€浼樼瓥鐣?""
        knowledge = EvolutionEngine.get_knowledge(category, min_score=0.3)
        if knowledge:
            return max(knowledge, key=lambda k: k["score"] * k["evidence_count"])
        return None

    # 鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺?    #  鐢ㄦ埛绾犳瀛︿範
    # 鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺?
    @staticmethod
    def learn_from_correction(original_action: str, user_said: str, correct_approach: str, context: str = ""):
        """鐢ㄦ埛绾犳 AI 鏃讹紝AI 璁颁綇姝ｇ‘鐨勫仛娉?""
        db = _get_db()
        db.execute(
            "INSERT INTO corrections (original_action, user_said, correct_approach, context) VALUES (?,?,?,?)",
            (original_action, user_said, correct_approach, context)
        )
        # 鍚屾椂寮哄寲姝ｇ‘鐨勭煡璇?        EvolutionEngine.learn("correction", user_said[:50], correct_approach, score=0.9)
        db.commit()
        db.close()

    @staticmethod
    def get_corrections(learned: int = 0) -> list[dict]:
        """鏌ョ湅瀛﹀埌鐨勭籂姝?""
        db = _get_db()
        rows = db.execute("SELECT * FROM corrections WHERE learned=? ORDER BY id DESC", (learned,)).fetchall()
        db.close()
        return [dict(r) for r in rows]

    @staticmethod
    def mark_correction_learned(correction_id: int):
        """鏍囪绾犳宸茶鍐呭寲"""
        db = _get_db()
        db.execute("UPDATE corrections SET learned=1 WHERE id=?", (correction_id,))
        db.commit()
        db.close()

    # 鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺?    #  杩涘寲鍒嗘瀽
    # 鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺?
    @staticmethod
    def evolve_report() -> dict:
        """AI 鑷垜杩涘寲鎶ュ憡 鈥?AI 鍛婅瘔浣犲畠瀛﹀埌浜嗕粈涔?""
        db = _get_db()

        # 琛屽姩缁熻
        total_actions = db.execute("SELECT COUNT(*) FROM actions").fetchone()[0]
        recent_actions = db.execute("SELECT COUNT(*) FROM actions WHERE created_at >= date('now','-7 days')").fetchone()[0]

        # 鎴愬姛鐜囪秼鍔?        success_rate = EvolutionEngine.get_success_rate(days=30)
        last_week_rate = EvolutionEngine.get_success_rate(days=7)

        # 鏈€甯哥敤鐨勮鍔?        top_actions = db.execute("SELECT action_name, COUNT(*) as cnt FROM actions GROUP BY action_name ORDER BY cnt DESC LIMIT 5").fetchall()

        # 瀛﹀埌鐨勭煡璇?        total_learned = db.execute("SELECT COUNT(*) FROM learning").fetchone()[0]
        top_knowledge = db.execute("SELECT category, key, score FROM learning WHERE score > 0.6 ORDER BY score DESC LIMIT 10").fetchall()

        # 绾犳娆℃暟
        corrections = db.execute("SELECT COUNT(*) FROM corrections").fetchone()[0]
        learned_corrections = db.execute("SELECT COUNT(*) FROM corrections WHERE learned=1").fetchone()[0]

        # 鍝佺被鏁堟灉鍒嗘瀽
        cat_performance = db.execute("""
            SELECT json_extract(input_params, '$.platform') as platform, 
                   COUNT(*) as total, 
                   SUM(CASE WHEN result_status='success' THEN 1 ELSE 0 END) as ok
            FROM actions WHERE action_type='scraper'
            GROUP BY platform
        """).fetchall()

        db.close()

        # 杩涘寲寤鸿
        suggestions = []
        if last_week_rate > success_rate:
            suggestions.append(f"馃搱 AI 杩戞湡鎴愬姛鐜囨彁鍗?{last_week_rate - success_rate:.1f}%锛岃鏄庢鍦ㄥ彉鑱槑")
        if learned_corrections < corrections:
            suggestions.append(f"馃 杩樻湁 {corrections - learned_corrections} 鏉＄敤鎴风籂姝ｅ緟瀛︿範锛岃璇淬€孉I瀛︿範绾犳銆?)
        for ca in cat_performance:
            rate = ca["ok"] / ca["total"] * 100 if ca["total"] > 0 else 0
            if rate > 80:
                suggestions.append(f"鉁?閲囬泦婧?{ca['platform']} 鎴愬姛鐜?{rate:.0f}%锛屽缓璁户缁娇鐢?)
            elif rate < 50 and ca["total"] > 3:
                suggestions.append(f"鈿狅笍 閲囬泦婧?{ca['platform']} 鎴愬姛鐜囦粎 {rate:.0f}%锛屽缓璁檷浣庝紭鍏堢骇")

        if total_actions < 10:
            suggestions.append("馃挕 AI 琛屽姩璁板綍杩樺緢灏戯紝澶氱敤鍑犳 AI 浼氳秺鏉ヨ秺鎳備綘")

        return {
            "generated_at": datetime.now().isoformat(),
            "summary": {
                "total_actions": total_actions,
                "recent_7d_actions": recent_actions,
                "success_rate_30d": success_rate,
                "success_rate_7d": last_week_rate,
                "trend": "馃搱 鎻愬崌涓? if last_week_rate > success_rate else "馃搲 闇€浼樺寲" if last_week_rate < success_rate else "鉃★笍 绋冲畾",
                "knowledge_items": total_learned,
                "corrections": corrections,
                "corrections_learned": learned_corrections,
            },
            "top_actions": [{"name": a["action_name"], "count": a["cnt"]} for a in top_actions],
            "top_knowledge": [{"category": k["category"], "key": k["key"], "score": round(k["score"], 2)} for k in top_knowledge],
            "platform_performance": [{"platform": c["platform"], "total": c["total"], "success_rate": round(c["ok"]/c["total"]*100, 1) if c["total"] > 0 else 0} for c in cat_performance],
            "suggestions": suggestions,
        }

    # 鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺?    #  蹇€熻褰曪紙渚涘叾浠栨ā鍧楄皟鐢級
    # 鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺?
    @staticmethod
    def record_scrape(source: str, keyword: str, count: int, success: bool):
        """璁板綍閲囬泦琛屽姩"""
        EvolutionEngine.log_action(
            "scraper", f"閲囬泦:{source}:{keyword}",
            {"platform": source, "keyword": keyword, "count": count},
            "success" if success else "failed",
            f"閲囬泦鍒?{count} 涓晢鍝? if success else "閲囬泦澶辫触"
        )
        if success:
            EvolutionEngine.learn("scraper_sources", source, keyword, score=0.7)

    @staticmethod
    def record_product_replace(old_title: str, new_title: str, success: bool):
        """璁板綍鍟嗗搧鏇挎崲"""
        EvolutionEngine.log_action(
            "replace", f"鏇挎崲鍟嗗搧",
            {"old": old_title, "new": new_title},
            "success" if success else "failed",
        )

    @staticmethod
    def record_health_check(total: int, dead: int, hot: int):
        """璁板綍鍋ュ悍妫€鏌?""
        EvolutionEngine.log_action(
            "health", "鍟嗗搧鍋ュ悍搴︽壂鎻?,
            {"total": total, "dead": dead, "hot": hot},
            "success",
            f"total={total} dead={dead} hot={hot}"
        )