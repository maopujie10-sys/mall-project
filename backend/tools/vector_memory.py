"""向量记忆 — ChromaDB 语义检索
让 AI 真正"理解"对话，而非关键词匹配

依赖: pip install chromadb sentence-transformers"""
import os
import json
from datetime import datetime
from typing import Optional

try:
    import chromadb
    from chromadb.config import Settings
    HAS_CHROMA = True
except ImportError:
    HAS_CHROMA = False

try:
    from sentence_transformers import SentenceTransformer
    HAS_EMBEDDING = True
except ImportError:
    HAS_EMBEDDING = False

VECTOR_DIR = os.path.join(os.path.dirname(__file__), "..", "vector_db")


class VectorMemory:
    """ChromaDB 向量记忆 — 语义级别的记忆检索"""

    def __init__(self):
        self._client = None
        self._collection = None
        self._embedder = None
        self._init()

    def _init(self):
        if not HAS_CHROMA:
            print("[VectorMemory] ChromaDB 未安装，使用纯文本模式。pip install chromadb")
            return
        try:
            os.makedirs(VECTOR_DIR, exist_ok=True)
            self._client = chromadb.PersistentClient(path=VECTOR_DIR)
            self._collection = self._client.get_or_create_collection(
                name="friday_memories",
                metadata={"hnsw:space": "cosine"}
            )
        except Exception as e:
            print(f"[VectorMemory] 初始化失败: {e}")
            self._client = None

    def _get_embedder(self):
        """懒加载嵌入模型"""
        if not self._embedder and HAS_EMBEDDING:
            try:
                # 使用轻量中文模型
                self._embedder = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
            except:
                try:
                    self._embedder = SentenceTransformer('all-MiniLM-L6-v2')
                except:
                    pass
        return self._embedder

    @property
    def available(self) -> bool:
        return self._client is not None

    def remember(self, text: str, metadata: dict = None, doc_id: str = None):
        """向量化并存储一段对话"""
        if not self.available:
            return False
        embedder = self._get_embedder()
        if not embedder:
            return False
        try:
            embedding = embedder.encode(text).tolist()
            doc_id = doc_id or f"mem_{datetime.now().timestamp()}"
            self._collection.add(
                embeddings=[embedding],
                documents=[text[:2000]],
                metadatas=[metadata or {}],
                ids=[doc_id],
            )
            return True
        except Exception as e:
            print(f"[VectorMemory] 存储失败: {e}")
            return False

    def recall(self, query: str, limit: int = 10) -> list:
        """语义搜索记忆"""
        if not self.available:
            return []
        embedder = self._get_embedder()
        if not embedder:
            return []
        try:
            embedding = embedder.encode(query).tolist()
            results = self._collection.query(
                query_embeddings=[embedding],
                n_results=limit,
            )
            if not results or not results.get("documents"):
                return []
            memories = []
            for i, doc in enumerate(results["documents"][0]):
                meta = results["metadatas"][0][i] if results.get("metadatas") else {}
                distance = results["distances"][0][i] if results.get("distances") else 0
                memories.append({
                    "content": doc,
                    "metadata": meta,
                    "relevance": round(1 - min(distance, 1), 3),
                })
            return memories
        except Exception as e:
            print(f"[VectorMemory] 检索失败: {e}")
            return []

    def recall_context(self, query: str, limit: int = 5) -> str:
        """语义搜索并返回格式化的上下文"""
        memories = self.recall(query, limit)
        if not memories:
            return ""
        lines = []
        for m in memories:
            role = m.get("metadata", {}).get("role", "")
            prefix = "用户" if role == "user" else "AI" if role == "ai" else ""
            lines.append(f"{prefix}: {m['content'][:120]}")
        return "\n".join(lines)

    def get_stats(self) -> dict:
        """向量记忆统计"""
        if not self.available:
            return {"available": False, "count": 0}
        try:
            count = self._collection.count()
            return {"available": True, "count": count, "embedding_model": str(self._get_embedder()) if self._get_embedder() else "N/A"}
        except:
            return {"available": True, "count": -1}

    def clear(self):
        """清空向量记忆"""
        if self.available:
            try:
                self._client.delete_collection("friday_memories")
                self._collection = self._client.get_or_create_collection(name="friday_memories")
            except:
                pass


# 全局单例
vector_memory = VectorMemory()