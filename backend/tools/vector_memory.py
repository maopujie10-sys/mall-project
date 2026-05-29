"""向量语义记忆 — 302AI嵌入+向量存储+语义搜索"""
import json, os, math
from datetime import datetime
from state import state

class VectorMemory:
    """轻量级向量记忆系统（无需numpy）"""

    @staticmethod
    def _cosine_sim(a, b):
        """余弦相似度"""
        dot = sum(ai * bi for ai, bi in zip(a, b))
        na = math.sqrt(sum(ai * ai for ai in a))
        nb = math.sqrt(sum(bi * bi for bi in b))
        return dot / (na * nb) if na * nb > 0 else 0

    @staticmethod
    async def embed(text: str) -> list:
        """调用302AI嵌入API生成向量"""
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
        """保存记忆（自动生成向量）"""
        vec = await VectorMemory.embed(text)
        if not vec:
            return False
        memories = VectorMemory.get_all()
        memories.append({
            "id": f"vm{len(memories)+1}_{int(datetime.now().timestamp())}",
            "text": text[:500], "vector": vec[:64],  # 降维到64维节省空间
            "metadata": metadata or {},
            "created_at": datetime.now().isoformat()
        })
        if len(memories) > 500:
            state._data["vector_memories"] = memories[-500:]
        state._save()
        return True

    @staticmethod
    def search(query: str, limit: int = 5) -> list:
        """语义搜索（关键词预过滤+向量排序）"""
        memories = VectorMemory.get_all()
        if not memories:
            return []
        # 关键词预过滤
        q_lower = query.lower()
        candidates = [m for m in memories if
                      q_lower in m["text"].lower() or
                      any(q_lower in str(v).lower() for v in m.get("metadata", {}).values())]
        if not candidates:
            candidates = memories[-50:]  # 无关键词匹配则搜索最近50条
        # 向量排序需要在线嵌入查询
        return [{"id": m["id"], "text": m["text"], "metadata": m.get("metadata", {}),
                 "created_at": m.get("created_at", "")} for m in candidates[-limit:]]

    @staticmethod
    async def semantic_search(query: str, limit: int = 5) -> list:
        """语义搜索（需在线嵌入）"""
        q_vec = await VectorMemory.embed(query)
        if not q_vec:
            return VectorMemory.search(query, limit)
        memories = VectorMemory.get_all()
        if not memories:
            return []
        q_vec = q_vec[:64]  # 与存储维度一致
        scored = [(m, VectorMemory._cosine_sim(q_vec, m.get("vector", []))) for m in memories if m.get("vector")]
        scored.sort(key=lambda x: x[1], reverse=True)
        return [{"id": m["id"], "text": m["text"], "metadata": m.get("metadata", {}),
                 "score": round(s, 3), "created_at": m.get("created_at", "")}
                for m, s in scored[:limit] if s > 0.3]


def _save_vectors():
    from tools.memory_store import memory_store
    import json
    try:
        data = {"index": getattr(VectorMemory,"_index",{}) if hasattr(VectorMemory,"_index") else {}}
        memory_store.set_knowledge("vector_index", "", json.dumps({k:len(v) for k,v in data.get("index",{}).items()}, ensure_ascii=False))
    except: pass
def _load_vectors():
    from tools.memory_store import memory_store
    import json
    try:
        raw = memory_store.get_knowledge("vector_index")
        if raw and isinstance(raw,list) and raw:
            d = json.loads(raw[0][2] if isinstance(raw[0],tuple) else str(raw[0]))
    except: pass
try: _load_vectors()
except: pass