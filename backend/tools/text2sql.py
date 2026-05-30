''"Text-to-SQL -- ''"
import re, json
from typing import Dict
from tools.logger import get_logger

logger = get_logger("text2sql")

# Schema
_SCHEMA_CACHE = {}

class Text2SQL:
    ''"->SQL''"

    @classmethod
    def set_schema(cls, tables: dict):
        ''"schema''"
        _SCHEMA_CACHE.update(tables)

    @classmethod
    async def query(cls, question: str) -> Dict:
        ''''''
        schema_desc = "\n".join([f" {t}: {', '.join(c)}" for t, c in _SCHEMA_CACHE.items()]) if _SCHEMA_CACHE else "schema"

        try:
            from agents.multi_model import ModelRouter

            prompt = f''"Schema:\n{schema_desc}\n\n: {question}\n\nSELECT(,INSERT/UPDATE/DELETE/DROP).JSON: {{"sql":"SELECT ...", "explanation":''}}''"

            resp = await ModelRouter.smart_chat(messages=[{"role":"user","content":prompt}], mode="fast")
            content = resp.get("content", "{}")

            json_match = re.search(r'\{[\s\S]*\}', content)
            if json_match:
                result = json.loads(json_match.group())
                sql = result.get("sql", '')

                
                dangerous = ["INSERT","UPDATE","DELETE","DROP","ALTER","TRUNCATE","CREATE","EXEC","EXECUTE"]
                if any(d in sql.upper() for d in dangerous):
                    return {"ok": False, "error": "SQL", "sql": sql}

                return {"ok": True, "sql": sql, "explanation": result.get("explanation",'')}
        except Exception as e:
            logger.error(f"Text2SQL: {e}")

        return {"ok": False, "error": "SQL", "sql": ''}

    @classmethod
    def simple_query(cls, question: str) -> Dict:
        ''"()''"
        q = question.lower()

        if '' in question and ('' in question or '' in question or "count" in q):
            return {"ok": True, "sql": "SELECT COUNT(*) as total FROM orders", "explanation": ''}
        if '' in question and ('' in question or '' in question):
            return {"ok": True, "sql": "SELECT COUNT(*) as total FROM users", "explanation": ''}
        if '' in question and ('' in question or '' in question):
            return {"ok": True, "sql": "SELECT COUNT(*) as total FROM products", "explanation": ''}
        if '' in question or '' in question:
            return {"ok": True, "sql": "SELECT * FROM orders WHERE DATE(created_at) = CURDATE() ORDER BY created_at DESC LIMIT 20", "explanation": ''}
        if '' in question:
            return {"ok": True, "sql": "SELECT * FROM orders ORDER BY created_at DESC LIMIT 20", "explanation": ''}

        return {"ok": False, "error": '', "sql": ''}

text2sql = Text2SQL()
