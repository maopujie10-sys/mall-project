锘?""鍚戦噺璇箟璁板繂 鈥?302AI宓屽叆+鍚戦噺瀛樺偍+璇箟鎼滅储"""
import json, os, math
from datetime import datetime
from state import state

class VectorMemory:
    """杞婚噺绾у悜閲忚蹇嗙郴缁燂紙鏃犻渶numpy锛?""

    @staticmethod
    def _cosine_sim(a, b):
        """浣欏鸡鐩镐技搴?""
        dot = sum(ai * bi for ai, bi in zip(a, b))
        na = math.sqrt(sum(ai * ai for ai in a))
        nb = math.sqrt(sum(bi * bi for bi in b))
        return dot / (na * nb) if na * nb > 0 else 0

    @staticmethod
    async def embed(text: str) -> list:
        """璋冪敤302AI宓屽叆API鐢熸垚鍚戦噺"""
        import httpx
        api_key = os.getenv("OPENAI_API_KEY", "")
        base_url = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
        if not api_key:
            return []
        try:
            async with httpx.AsyncClient(timeout=10) as c:
                r = await c.post(f"{base_url}/embeddings",
                    headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
                    json={"model": "text-embedding-ada-002", "input": text[:1000]})
                if r.status_code == 200:
                    return r.json()["data"][0]["embedding"]
        except Exception:
            pass
        return []

    @staticmethod
    def get_all():
        return state._data.setdefault("vector_memories", [])

    @staticmethod
    async def remember(text: str, metadata: dict = None):
        """淇濆瓨璁板繂锛堣嚜鍔ㄧ敓鎴愬悜閲忥級"""
        vec = await VectorMemory.embed(text)
        if not vec:
            return False
        memories = VectorMemory.get_all()
        memories.append({
            "id": f"vm{len(memories)+1}_{int(datetime.now().timestamp())}",
            "text": text[:500], "vector": vec[:64],  # 闄嶇淮鍒?4缁磋妭鐪佺┖闂?
            "metadata": metadata or {},
            "created_at": datetime.now().isoformat()
        })
        if len(memories) > 500:
            state._data["vector_memories"] = memories[-500:]
        state._save()
        return True

    @staticmethod
    def search(query: str, limit: int = 5) -> list:
        """璇箟鎼滅储锛堝叧閿瘝棰勮繃婊?鍚戦噺鎺掑簭锛?""
        memories = VectorMemory.get_all()
        if not memories:
            return []
        # 鍏抽敭璇嶉杩囨护
        q_lower = query.lower()
        candidates = [m for m in memories if
                      q_lower in m["text"].lower() or
                      any(q_lower in str(v).lower() for v in m.get("metadata", {}).values())]
        if not candidates:
            candidates = memories[-50:]  # 鏃犲叧閿瘝鍖归厤鍒欐悳绱㈡渶杩?0鏉?
        # 鍚戦噺鎺掑簭闇€瑕佸湪绾垮祵鍏ユ煡璇?
        return [{"id": m["id"], "text": m["text"], "metadata": m.get("metadata", {}),
                 "created_at": m.get("created_at", "")} for m in candidates[-limit:]]

    @staticmethod
    async def semantic_search(query: str, limit: int = 5) -> list:
        """璇箟鎼滅储锛堥渶鍦ㄧ嚎宓屽叆锛?""
        q_vec = await VectorMemory.embed(query)
        if not q_vec:
            return VectorMemory.search(query, limit)
        memories = VectorMemory.get_all()
        if not memories:
            return []
        q_vec = q_vec[:64]  # 涓庡瓨鍌ㄧ淮搴︿竴鑷?
        scored = [(m, VectorMemory._cosine_sim(q_vec, m.get("vector", []))) for m in memories if m.get("vector")]
        scored.sort(key=lambda x: x[1], reverse=True)
        return [{"id": m["id"], "text": m["text"], "metadata": m.get("metadata", {}),
                 "score": round(s, 3), "created_at": m.get("created_at", "")}
                for m, s in scored[:limit] if s > 0.3]
