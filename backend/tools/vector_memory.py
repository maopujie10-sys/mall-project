"""向量语义记忆 v2 — ChromaDB持久化 + 302AI嵌入 + 语义搜索"""
import json, os, math, hashlib
from datetime import datetime
from pathlib import Path
from state import state

HAS_CHROMADB = False
try:
    import chromadb
    from chromadb.config import Settings
    HAS_CHROMADB = True
except ImportError:
    pass

CHROMA_DIR = Path(__file__).parent.parent / "data" / "chroma_db"


class VectorMemory:
    """向量记忆系统 — ChromaDB(优先) / 内存(降级) 双模式"""

    _chroma_client = None
    _chroma_collection = None

    @classmethod
    def _get_chroma(cls):
        """获取ChromaDB集合(延迟初始化)"""
        if not HAS_CHROMADB:
            return None
        if cls._chroma_collection is not None:
            return cls._chroma_collection
        try:
            CHROMA_DIR.mkdir(parents=True, exist_ok=True)
            cls._chroma_client = chromadb.PersistentClient(
                path=str(CHROMA_DIR),
                settings=Settings(anonymized_telemetry=False)
            )
            cls._chroma_collection = cls._chroma_client.get_or_create_collection(
                name="friday_memories",
                metadata={"hnsw:space": "cosine"}
            )
            print(f"[VectorMemory] ChromaDB已连接, {cls._chroma_collection.count()}条记忆")
            return cls._chroma_collection
        except Exception as e:
            print(f"[VectorMemory] ChromaDB连接失败, 降级到内存模式: {e}")
            return None

    @staticmethod
    def _cosine_sim(a, b):
        if not a or not b:
            return 0
        dot = sum(ai * bi for ai, bi in zip(a, b))
        na = math.sqrt(sum(ai * ai for ai in a))
        nb = math.sqrt(sum(bi * bi for bi in b))
        return dot / (na * nb) if na * nb > 0 else 0

    @staticmethod
    async def embed(text: str) -> list:
        """调用嵌入API生成向量 — 优先DeepSeek, 降级OpenAI"""
        import httpx
        # 尝试DeepSeek
        deepseek_key = os.getenv("DEEPSEEK_API_KEY", "")
        if deepseek_key:
            try:
                async with httpx.AsyncClient(timeout=15) as c:
                    r = await c.post("https://api.deepseek.com/v1/embeddings",
                        headers={"Authorization": f"Bearer {deepseek_key}", "Content-Type": "application/json"},
                        json={"model": "deepseek-chat", "input": text[:2000]})
                    if r.status_code == 200:
                        return r.json()["data"][0]["embedding"]
            except Exception:
                pass
        # 降级OpenAI
        api_key = os.getenv("OPENAI_API_KEY", "")
        base_url = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
        if not api_key:
            # 无API Key, 用简单哈希向量(关键词匹配)
            return VectorMemory._hash_embed(text)
        try:
            async with httpx.AsyncClient(timeout=15) as c:
                r = await c.post(f"{base_url}/embeddings",
                    headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
                    json={"model": "text-embedding-ada-002", "input": text[:2000]})
                if r.status_code == 200:
                    return r.json()["data"][0]["embedding"]
        except Exception:
            pass
        return VectorMemory._hash_embed(text)

    @staticmethod
    def _hash_embed(text: str) -> list:
        """无API Key时的简单哈希向量(256维)"""
        h = hashlib.sha256(text.encode()).digest()
        return [int(b) / 255.0 for b in h * 8][:256]

    @staticmethod
    def get_all():
        return state._data.setdefault("vector_memories", [])

    @staticmethod
    async def remember(text: str, metadata: dict = None) -> bool:
        """保存记忆 — ChromaDB优先, 内存降级"""
        vec = await VectorMemory.embed(text)
        if not vec:
            return False
        mem_id = f"vm{int(datetime.now().timestamp())}_{hashlib.md5(text.encode()).hexdigest()[:8]}"
        meta = metadata or {}
        now = datetime.now().isoformat()

        # ChromaDB模式
        coll = VectorMemory._get_chroma()
        if coll is not None:
            try:
                coll.add(
                    ids=[mem_id],
                    embeddings=[vec],
                    documents=[text[:2000]],
                    metadatas=[{"source": meta.get("source", ""), "type": meta.get("type", "doc"),
                                "chunk": meta.get("chunk", 0), "created_at": now}]
                )
                return True
            except Exception as e:
                print(f"[VectorMemory] ChromaDB写入失败, 降级内存: {e}")

        # 内存降级模式
        memories = VectorMemory.get_all()
        memories.append({
            "id": mem_id, "text": text[:500], "vector": vec[:64],
            "metadata": meta, "created_at": now
        })
        if len(memories) > 1000:
            state._data["vector_memories"] = memories[-500:]
        state._save()
        return True

    @staticmethod
    def search(query: str, limit: int = 5) -> list:
        """快速搜索(关键词匹配, 无需API)"""
        memories = VectorMemory.get_all()
        if not memories:
            return []
        q_lower = query.lower()
        candidates = [m for m in memories if
                      q_lower in m["text"].lower() or
                      any(q_lower in str(v).lower() for v in m.get("metadata", {}).values())]
        if not candidates:
            candidates = memories[-50:]
        return [{"id": m["id"], "text": m["text"], "metadata": m.get("metadata", {}),
                 "created_at": m.get("created_at", "")} for m in candidates[-limit:]]

    @staticmethod
    async def semantic_search(query: str, limit: int = 5) -> list:
        """语义搜索 — ChromaDB优先, 在线嵌入降级"""
        # ChromaDB模式
        coll = VectorMemory._get_chroma()
        if coll is not None:
            try:
                q_vec = await VectorMemory.embed(query)
                if q_vec:
                    results = coll.query(query_embeddings=[q_vec], n_results=limit)
                    items = []
                    for i, doc_id in enumerate(results["ids"][0]):
                        items.append({
                            "id": doc_id,
                            "text": results["documents"][0][i] if results.get("documents") else "",
                            "metadata": results["metadatas"][0][i] if results.get("metadatas") else {},
                            "score": round(1 - results["distances"][0][i], 3) if results.get("distances") else 0,
                        })
                    return items
            except Exception as e:
                print(f"[VectorMemory] ChromaDB搜索失败: {e}")

        # 内存降级模式
        q_vec = await VectorMemory.embed(query)
        if not q_vec:
            return VectorMemory.search(query, limit)
        memories = VectorMemory.get_all()
        if not memories:
            return []
        q_vec = q_vec[:64]
        scored = [(m, VectorMemory._cosine_sim(q_vec, m.get("vector", []))) for m in memories if m.get("vector")]
        scored.sort(key=lambda x: x[1], reverse=True)
        return [{"id": m["id"], "text": m["text"], "metadata": m.get("metadata", {}),
                 "score": round(s, 3), "created_at": m.get("created_at", "")}
                for m, s in scored[:limit] if s > 0.2]

    @classmethod
    def get_stats(cls) -> dict:
        """获取记忆统计"""
        coll = cls._get_chroma()
        if coll is not None:
            try:
                return {"mode": "chromadb", "count": coll.count(), "path": str(CHROMA_DIR)}
            except:
                pass
        return {"mode": "memory", "count": len(cls.get_all()), "path": "state.json"}