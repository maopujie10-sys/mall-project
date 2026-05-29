"""AI 自我进化引擎 -- 记忆/学习/优化/进化

AI 不再是「死」的:
  ✅ 记住所有行动 + 结果(什么成功、什么失败)
  ✅ 自动评估策略效果(哪个采集源更好?哪种商品更受欢迎?)
  ✅ 从用户纠正中学习(说「不对,做这个」AI 就记住)
  ✅ 意图规则自动优化(常用指令优先级自动提升)
  ✅ 生成进化报告(AI 自己告诉你它学到了什么)
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

# ═══════════════════════════════════════
#  行动记忆
# ═══════════════════════════════════════

class EvolutionEngine:
    """AI 自我进化引擎"""

    @staticmethod
    def log_action(action_type: str, action_name: str, input_params: dict = None,
                   result_status: str = "success", result_detail: str = "", duration_ms: float = 0):
        """记录每次 AI 行动 -- AI 的「记忆」"""
        db = _get_db()
        db.execute(
            "INSERT INTO actions (action_type, action_name, input_params, result_status, result_detail, duration_ms) VALUES (?,?,?,?,?,?)",
            (action_type, action_name, json.dumps(input_params or {}, ensure_ascii=False), result_status, result_detail, duration_ms)
        )
        db.commit()
        db.close()

    @staticmethod
    def get_action_history(action_type: str = None, limit: int = 50) -> list[dict]:
        """查看 AI 的行动历史"""
        db = _get_db()
        if action_type:
            rows = db.execute("SELECT * FROM actions WHERE action_type=? ORDER BY id DESC LIMIT ?", (action_type, limit)).fetchall()
        else:
            rows = db.execute("SELECT * FROM actions ORDER BY id DESC LIMIT ?", (limit,)).fetchall()
        db.close()
        return [dict(r) for r in rows]

    @staticmethod
    def get_success_rate(action_type: str = None, days: int = 30) -> float:
        """计算 AI 行动的成功率"""
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

    # ═══════════════════════════════════════
    #  知识学习
    # ═══════════════════════════════════════

    @staticmethod
    def learn(category: str, key: str, value: str = None, score: float = None):
        """AI 学到新知识 -- 比如「eBay 采集电子产品成功率 85%」"""
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
        """获取 AI 学到的知识"""
        db = _get_db()
        rows = db.execute("SELECT * FROM learning WHERE category=? AND score>=? ORDER BY score DESC", (category, min_score)).fetchall()
        db.close()
        return [dict(r) for r in rows]

    @staticmethod
    def get_best_strategy(category: str) -> Optional[dict]:
        """AI 选择最优策略"""
        knowledge = EvolutionEngine.get_knowledge(category, min_score=0.3)
        if knowledge:
            return max(knowledge, key=lambda k: k["score"] * k["evidence_count"])
        return None

    # ═══════════════════════════════════════
    #  用户纠正学习
    # ═══════════════════════════════════════

    @staticmethod
    def learn_from_correction(original_action: str, user_said: str, correct_approach: str, context: str = ""):
        """用户纠正 AI 时,AI 记住正确的做法"""
        db = _get_db()
        db.execute(
            "INSERT INTO corrections (original_action, user_said, correct_approach, context) VALUES (?,?,?,?)",
            (original_action, user_said, correct_approach, context)
        )
        # 同时强化正确的知识
        EvolutionEngine.learn("correction", user_said[:50], correct_approach, score=0.9)
        db.commit()
        db.close()

    @staticmethod
    def get_corrections(learned: int = 0) -> list[dict]:
        """查看学到的纠正"""
        db = _get_db()
        rows = db.execute("SELECT * FROM corrections WHERE learned=? ORDER BY id DESC", (learned,)).fetchall()
        db.close()
        return [dict(r) for r in rows]

    @staticmethod
    def mark_correction_learned(correction_id: int):
        """标记纠正已被内化"""
        db = _get_db()
        db.execute("UPDATE corrections SET learned=1 WHERE id=?", (correction_id,))
        db.commit()
        db.close()

    # ═══════════════════════════════════════
    #  进化分析
    # ═══════════════════════════════════════

    @staticmethod
    def evolve_report() -> dict:
        """AI 自我进化报告 -- AI 告诉你它学到了什么"""
        db = _get_db()

        # 行动统计
        total_actions = db.execute("SELECT COUNT(*) FROM actions").fetchone()[0]
        recent_actions = db.execute("SELECT COUNT(*) FROM actions WHERE created_at >= date('now','-7 days')").fetchone()[0]

        # 成功率趋势
        success_rate = EvolutionEngine.get_success_rate(days=30)
        last_week_rate = EvolutionEngine.get_success_rate(days=7)

        # 最常用的行动
        top_actions = db.execute("SELECT action_name, COUNT(*) as cnt FROM actions GROUP BY action_name ORDER BY cnt DESC LIMIT 5").fetchall()

        # 学到的知识
        total_learned = db.execute("SELECT COUNT(*) FROM learning").fetchone()[0]
        top_knowledge = db.execute("SELECT category, key, score FROM learning WHERE score > 0.6 ORDER BY score DESC LIMIT 10").fetchall()

        # 纠正次数
        corrections = db.execute("SELECT COUNT(*) FROM corrections").fetchone()[0]
        learned_corrections = db.execute("SELECT COUNT(*) FROM corrections WHERE learned=1").fetchone()[0]

        # 品类效果分析
        cat_performance = db.execute("""
            SELECT json_extract(input_params, '$.platform') as platform, 
                   COUNT(*) as total, 
                   SUM(CASE WHEN result_status='success' THEN 1 ELSE 0 END) as ok
            FROM actions WHERE action_type='scraper'
            GROUP BY platform
        """).fetchall()

        db.close()

        # 进化建议
        suggestions = []
        if last_week_rate > success_rate:
            suggestions.append(f"📈 AI 近期成功率提升 {last_week_rate - success_rate:.1f}%,说明正在变聪明")
        if learned_corrections < corrections:
            suggestions.append(f"🧠 还有 {corrections - learned_corrections} 条用户纠正待学习,请说「AI学习纠正」")
        for ca in cat_performance:
            rate = ca["ok"] / ca["total"] * 100 if ca["total"] > 0 else 0
            if rate > 80:
                suggestions.append(f"✅ 采集源 {ca['platform']} 成功率 {rate:.0f}%,建议继续使用")
            elif rate < 50 and ca["total"] > 3:
                suggestions.append(f"⚠️ 采集源 {ca['platform']} 成功率仅 {rate:.0f}%,建议降低优先级")

        if total_actions < 10:
            suggestions.append("💡 AI 行动记录还很少,多用几次 AI 会越来越懂你")

        return {
            "generated_at": datetime.now().isoformat(),
            "summary": {
                "total_actions": total_actions,
                "recent_7d_actions": recent_actions,
                "success_rate_30d": success_rate,
                "success_rate_7d": last_week_rate,
                "trend": "📈 提升中" if last_week_rate > success_rate else "📉 需优化" if last_week_rate < success_rate else "➡️ 稳定",
                "knowledge_items": total_learned,
                "corrections": corrections,
                "corrections_learned": learned_corrections,
            },
            "top_actions": [{"name": a["action_name"], "count": a["cnt"]} for a in top_actions],
            "top_knowledge": [{"category": k["category"], "key": k["key"], "score": round(k["score"], 2)} for k in top_knowledge],
            "platform_performance": [{"platform": c["platform"], "total": c["total"], "success_rate": round(c["ok"]/c["total"]*100, 1) if c["total"] > 0 else 0} for c in cat_performance],
            "suggestions": suggestions,
        }

    # ═══════════════════════════════════════
    #  快速记录(供其他模块调用)
    # ═══════════════════════════════════════

    @staticmethod
    def record_scrape(source: str, keyword: str, count: int, success: bool):
        """记录采集行动"""
        EvolutionEngine.log_action(
            "scraper", f"采集:{source}:{keyword}",
            {"platform": source, "keyword": keyword, "count": count},
            "success" if success else "failed",
            f"采集到 {count} 个商品" if success else "采集失败"
        )
        if success:
            EvolutionEngine.learn("scraper_sources", source, keyword, score=0.7)

    @staticmethod
    def record_product_replace(old_title: str, new_title: str, success: bool):
        """记录商品替换"""
        EvolutionEngine.log_action(
            "replace", f"替换商品",
            {"old": old_title, "new": new_title},
            "success" if success else "failed",
        )

    @staticmethod
    def record_health_check(total: int, dead: int, hot: int):
        """记录健康检查"""
        EvolutionEngine.log_action(
            "health", "商品健康度扫描",
            {"total": total, "dead": dead, "hot": hot},
            "success",
            f"total={total} dead={dead} hot={hot}"
        )

def _save_evolution():
    from tools.memory_store import memory_store
    import json
    try:
        data = {"metrics": getattr(EvolutionTracker,"_metrics",{}), "reports": getattr(EvolutionTracker,"_reports",[])[-20:]}
        memory_store.set_knowledge("evolution_data", "", json.dumps(data, ensure_ascii=False, default=str))
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