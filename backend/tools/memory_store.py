锘?""璁板繂鎸佷箙鍖栧瓨鍌?鈥?瀵硅瘽涓嶅啀鍥犻噸鍚涪澶?SQLite + JSON 鍙屽眰锛屾敮鎸佽涔夋爣绛惧拰閲嶈鎬ц瘎鍒?""
import sqlite3
import json
import os
from datetime import datetime
from typing import Optional

MEMORY_DB = os.path.join(os.getenv("APP_MEMORY_DIR", os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "memory")), "memory_store.db")


class MemoryStore:
    """鎸佷箙鍖栬蹇嗗瓨鍌?""

    def __init__(self):
        self._init_db()

    def _init_db(self):
        with sqlite3.connect(MEMORY_DB) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS conversations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    role TEXT NOT NULL,
                    content TEXT NOT NULL,
                    topic TEXT DEFAULT '',
                    importance REAL DEFAULT 0.5,
                    created_at TEXT DEFAULT (datetime('now','localtime'))
                )
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS learning_log (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    action TEXT NOT NULL,
                    result TEXT DEFAULT '',
                    user_feedback TEXT DEFAULT '',
                    learned TEXT DEFAULT '',
                    created_at TEXT DEFAULT (datetime('now','localtime'))
                )
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS knowledge (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    category TEXT NOT NULL,
                    key TEXT NOT NULL,
                    value TEXT NOT NULL,
                    confidence REAL DEFAULT 0.5,
                    created_at TEXT DEFAULT (datetime('now','localtime')),
                    UNIQUE(category, key)
                )
            """)
            conn.execute("CREATE INDEX IF NOT EXISTS idx_conv_created ON conversations(created_at)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_learning_created ON learning_log(created_at)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_knowledge_cat ON knowledge(category)")
            conn.commit()

    def remember_conversation(self, role: str, content: str, topic: str = "", importance: float = 0.5):
        """淇濆瓨涓€娈靛璇?""
        with sqlite3.connect(MEMORY_DB) as conn:
            conn.execute(
                "INSERT INTO conversations (role, content, topic, importance) VALUES (?, ?, ?, ?)",
                (role, content[:2000], topic[:100], importance),
            )
            conn.commit()
            # 淇濈暀鏈€杩?5000 鏉?            conn.execute("DELETE FROM conversations WHERE id NOT IN (SELECT id FROM conversations ORDER BY id DESC LIMIT 5000)")
            conn.commit()

    def recall_recent(self, limit: int = 50) -> list:
        """鑾峰彇鏈€杩戝璇?""
        with sqlite3.connect(MEMORY_DB) as conn:
            rows = conn.execute(
                "SELECT role, content, topic, created_at FROM conversations ORDER BY id DESC LIMIT ?",
                (limit,)
            ).fetchall()
            return [{"role": r[0], "content": r[1], "topic": r[2], "time": r[3]} for r in rows]

    def recall_by_topic(self, topic: str, limit: int = 20) -> list:
        """鎸変富棰樻绱㈠璇?""
        with sqlite3.connect(MEMORY_DB) as conn:
            rows = conn.execute(
                "SELECT role, content, topic, created_at FROM conversations WHERE topic LIKE ? ORDER BY id DESC LIMIT ?",
                (f"%{topic}%", limit)
            ).fetchall()
            return [{"role": r[0], "content": r[1], "topic": r[2], "time": r[3]} for r in rows]

    def search(self, query: str, limit: int = 20) -> list:
        """鍏ㄦ枃鎼滅储瀵硅瘽"""
        with sqlite3.connect(MEMORY_DB) as conn:
            rows = conn.execute(
                "SELECT role, content, topic, created_at FROM conversations WHERE content LIKE ? ORDER BY id DESC LIMIT ?",
                (f"%{query}%", limit)
            ).fetchall()
            return [{"role": r[0], "content": r[1], "topic": r[2], "time": r[3]} for r in rows]

    def get_stats(self) -> dict:
        """璁板繂缁熻"""
        with sqlite3.connect(MEMORY_DB) as conn:
            total = conn.execute("SELECT COUNT(*) FROM conversations").fetchone()[0]
            topics = conn.execute("SELECT topic, COUNT(*) as cnt FROM conversations WHERE topic != '' GROUP BY topic ORDER BY cnt DESC LIMIT 10").fetchall()
            return {
                "total_conversations": total,
                "top_topics": [{"topic": t[0], "count": t[1]} for t in topics],
                "oldest": conn.execute("SELECT created_at FROM conversations ORDER BY id ASC LIMIT 1").fetchone(),
                "newest": conn.execute("SELECT created_at FROM conversations ORDER BY id DESC LIMIT 1").fetchone(),
            }

    # ===== 瀛︿範鏃ュ織 =====
    def log_learning(self, action: str, result: str, feedback: str = "", learned: str = ""):
        """璁板綍瀛︿範缁忛獙"""
        with sqlite3.connect(MEMORY_DB) as conn:
            conn.execute(
                "INSERT INTO learning_log (action, result, user_feedback, learned) VALUES (?, ?, ?, ?)",
                (action[:200], result[:500], feedback[:500], learned[:500]),
            )
            conn.commit()

    def recall_learnings(self, action_hint: str = "", limit: int = 20) -> list:
        """妫€绱㈢浉鍏冲涔犵粡楠?""
        with sqlite3.connect(MEMORY_DB) as conn:
            if action_hint:
                rows = conn.execute(
                    "SELECT action, result, user_feedback, learned, created_at FROM learning_log WHERE action LIKE ? ORDER BY id DESC LIMIT ?",
                    (f"%{action_hint}%", limit)
                ).fetchall()
            else:
                rows = conn.execute(
                    "SELECT action, result, user_feedback, learned, created_at FROM learning_log ORDER BY id DESC LIMIT ?",
                    (limit,)
                ).fetchall()
            return [{"action": r[0], "result": r[1], "feedback": r[2], "learned": r[3], "time": r[4]} for r in rows]

    # ===== 鐭ヨ瘑搴?=====
    def set_knowledge(self, category: str, key: str, value: str, confidence: float = 0.5):
        """瀛樺偍涓€鏉＄煡璇?""
        with sqlite3.connect(MEMORY_DB) as conn:
            conn.execute(
                "INSERT OR REPLACE INTO knowledge (category, key, value, confidence) VALUES (?, ?, ?, ?)",
                (category[:50], key[:100], value[:2000], confidence),
            )
            conn.commit()

    def get_knowledge(self, category: str = "", key: str = "") -> list:
        """妫€绱㈢煡璇?""
        with sqlite3.connect(MEMORY_DB) as conn:
            if category and key:
                rows = conn.execute(
                    "SELECT category, key, value, confidence FROM knowledge WHERE category=? AND key=?",
                    (category, key)
                ).fetchall()
            elif category:
                rows = conn.execute(
                    "SELECT category, key, value, confidence FROM knowledge WHERE category=?",
                    (category,)
                ).fetchall()
            else:
                rows = conn.execute("SELECT category, key, value, confidence FROM knowledge").fetchall()
            return [{"category": r[0], "key": r[1], "value": r[2], "confidence": r[3]} for r in rows]

    def get_knowledge_categories(self) -> list:
        """鎵€鏈夌煡璇嗗垎绫?""
        with sqlite3.connect(MEMORY_DB) as conn:
            rows = conn.execute("SELECT DISTINCT category, COUNT(*) FROM knowledge GROUP BY category").fetchall()
            return [{"category": r[0], "count": r[1]} for r in rows]


# 鍏ㄥ眬鍗曚緥
memory_store = MemoryStore()

