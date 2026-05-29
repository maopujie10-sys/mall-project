"""Text-to-SQL — 自然语言查数据库"""
import re, json
from tools.logger import get_logger

logger = get_logger("text2sql")

# 数据库Schema缓存
_SCHEMA_CACHE = {}

class Text2SQL:
    """自然语言→SQL查询"""

    @classmethod
    def set_schema(cls, tables: dict):
        """设置数据库schema"""
        _SCHEMA_CACHE.update(tables)

    @classmethod
    async def query(cls, question: str) -> Dict:
        """自然语言查询"""
        schema_desc = "\n".join([f"表 {t}: {', '.join(c)}" for t, c in _SCHEMA_CACHE.items()]) if _SCHEMA_CACHE else "无schema缓存"

        try:
            from agents.multi_model import ModelRouter
            mr = ModelRouter()

            prompt = f"""数据库Schema:\n{schema_desc}\n\n用户问题: {question}\n\n请生成一个安全的SELECT查询(只读,禁止INSERT/UPDATE/DELETE/DROP)。返回JSON: {{"sql":"SELECT ...", "explanation":"查询说明"}}"""

            resp = await mr.chat(messages=[{"role":"user","content":prompt}], mode="fast")
            content = resp.get("content", "{}")

            json_match = re.search(r'\{[\s\S]*\}', content)
            if json_match:
                result = json.loads(json_match.group())
                sql = result.get("sql", "")

                # 安全检查
                dangerous = ["INSERT","UPDATE","DELETE","DROP","ALTER","TRUNCATE","CREATE","EXEC","EXECUTE"]
                if any(d in sql.upper() for d in dangerous):
                    return {"ok": False, "error": "禁止执行写操作SQL", "sql": sql}

                return {"ok": True, "sql": sql, "explanation": result.get("explanation","")}
        except Exception as e:
            logger.error(f"Text2SQL失败: {e}")

        return {"ok": False, "error": "无法生成SQL", "sql": ""}

    @classmethod
    def simple_query(cls, question: str) -> Dict:
        """简单规则匹配(降级方案)"""
        q = question.lower()

        if "订单" in question and ("多少" in question or "数量" in question or "count" in q):
            return {"ok": True, "sql": "SELECT COUNT(*) as total FROM orders", "explanation": "统计订单总数"}
        if "用户" in question and ("多少" in question or "数量" in question):
            return {"ok": True, "sql": "SELECT COUNT(*) as total FROM users", "explanation": "统计用户总数"}
        if "商品" in question and ("多少" in question or "数量" in question):
            return {"ok": True, "sql": "SELECT COUNT(*) as total FROM products", "explanation": "统计商品总数"}
        if "今天" in question or "今日" in question:
            return {"ok": True, "sql": "SELECT * FROM orders WHERE DATE(created_at) = CURDATE() ORDER BY created_at DESC LIMIT 20", "explanation": "查询今日订单"}
        if "最近" in question:
            return {"ok": True, "sql": "SELECT * FROM orders ORDER BY created_at DESC LIMIT 20", "explanation": "查询最近订单"}

        return {"ok": False, "error": "无法匹配查询意图", "sql": ""}

text2sql = Text2SQL()
