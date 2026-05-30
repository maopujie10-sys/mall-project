"""RAG知识库引擎 — ChromaDB向量检索 + AI问答"""
import os, re, json, time, hashlib
from typing import Dict, List, Optional
from tools.logger import get_logger

logger = get_logger("rag")

# 轻量embedding: 优先sentence-transformers, 回退到内置hash
_embedder = None
_embed_dim = 384

def _get_embedder():
    global _embedder, _embed_dim
    if _embedder is not None:
        return _embedder
    try:
        from sentence_transformers import SentenceTransformer
        _embedder = SentenceTransformer("all-MiniLM-L6-v2")
        _embed_dim = 384
        logger.info("RAG: 已加载 sentence-transformers/all-MiniLM-L6-v2")
    except Exception as e:
        logger.warning(f"RAG: sentence-transformers不可用({e}), 使用hash嵌入")
        _embed_dim = 256
        _embedder = "hash"
    return _embedder

def _embed(text: str) -> List[float]:
    embedder = _get_embedder()
    if embedder == "hash":
        h = hashlib.sha256(text.encode()).digest()
        return [float(b) / 255.0 for b in h[:256]]
    return embedder.encode(text).tolist()

def _cosine(a: List[float], b: List[float]) -> float:
    dot = sum(x*y for x,y in zip(a,b))
    na = sum(x*x for x in a)**0.5
    nb = sum(x*x for x in b)**0.5
    return dot/(na*nb) if na*nb>0 else 0


class RAGEngine:
    """RAG知识库 — ChromaDB向量检索 + 关键词混合"""

    _collection = None
    _docs: List[Dict] = []
    _index: Dict[str, List[int]] = {}  # 关键词倒排索引

    @classmethod
    def _get_collection(cls):
        if cls._collection is not None:
            return cls._collection
        try:
            import chromadb
            from chromadb.config import Settings
            client = chromadb.Client(Settings(
                chroma_db_impl="duckdb+parquet",
                persist_directory=os.path.join(os.path.dirname(__file__), "..", "chroma_data"),
                anonymized_telemetry=False
            ))
            cls._collection = client.get_or_create_collection(
                name="friday_knowledge",
                metadata={"hnsw:space": "cosine"}
            )
            logger.info("RAG: ChromaDB已连接")
        except Exception as e:
            logger.warning(f"RAG: ChromaDB不可用({e}), 使用内存模式")
            cls._collection = None
        return cls._collection

    @classmethod
    def add_document(cls, text: str, source: str = "", title: str = "", tags: str = "") -> Dict:
        """摄入文档到知识库"""
        doc_id = hashlib.md5((text + source).encode()).hexdigest()[:16]
        embedding = _embed(text)
        doc = {
            "id": doc_id, "content": text, "source": source or "manual",
            "title": title or text[:50], "tags": tags,
            "created_at": time.time(), "chunks": 1
        }

        # ChromaDB
        col = cls._get_collection()
        if col:
            try:
                col.add(
                    ids=[doc_id], documents=[text], embeddings=[embedding],
                    metadatas=[{"source": doc["source"], "title": doc["title"], "tags": tags}]
                )
            except Exception as e:
                logger.warning(f"ChromaDB写入失败: {e}")

        # 关键词索引
        words = set(re.findall(r'[\u4e00-\u9fff]{2,}|[a-zA-Z]{3,}', text.lower()))
        idx = len(cls._docs)
        cls._docs.append(doc)
        for w in words:
            cls._index.setdefault(w, []).append(idx)

        cls.save()
        return {"ok": True, "doc_id": doc_id, "title": doc["title"]}

    @classmethod
    def search(cls, query: str, top_k: int = 5) -> List[Dict]:
        """混合搜索: 向量 + 关键词"""
        results = []
        seen = set()

        # 向量搜索
        col = cls._get_collection()
        if col and cls._docs:
            try:
                q_emb = _embed(query)
                chroma_results = col.query(query_embeddings=[q_emb], n_results=top_k)
                if chroma_results and chroma_results.get("ids"):
                    for i, cid in enumerate(chroma_results["ids"][0]):
                        score = 1.0 - (chroma_results.get("distances", [[0]]*top_k)[0][i] or 0)
                        meta = chroma_results.get("metadatas", [[{}]])[0][i] if chroma_results.get("metadatas") else {}
                        text = chroma_results.get("documents", [[""]])[0][i] if chroma_results.get("documents") else ""
                        results.append({"doc": {"content": text, "source": meta.get("source",""), "title": meta.get("title",""), "id": cid}, "score": round(score, 3), "method": "vector"})
                        seen.add(cid)
            except Exception as e:
                logger.warning(f"向量搜索失败: {e}")

        # 关键词搜索
        query_words = set(re.findall(r'[\u4e00-\u9fff]{2,}|[a-zA-Z]{3,}', query.lower()))
        kw_scores = {}
        for w in query_words:
            if w in cls._index:
                idf = 1.0 / (len(cls._index[w])**0.5 + 1)
                for doc_idx in cls._index[w]:
                    kw_scores[doc_idx] = kw_scores.get(doc_idx, 0) + idf

        ranked = sorted(kw_scores.items(), key=lambda x: x[1], reverse=True)[:top_k]
        for doc_idx, score in ranked:
            if cls._docs[doc_idx]["id"] not in seen:
                results.append({"doc": cls._docs[doc_idx], "score": round(score*0.8, 3), "method": "keyword"})

        return sorted(results, key=lambda x: x["score"], reverse=True)[:top_k]

    @classmethod
    def ask(cls, question: str, top_k: int = 5) -> Dict:
        """RAG问答 — 检索+AI回答"""
        docs = cls.search(question, top_k)
        if not docs:
            return {"ok": True, "answer": "知识库中没有找到相关信息。", "sources": []}

        context = "\n\n".join([
            f"[来源:{d['doc'].get('source','未知')}] {d['doc']['content'][:600]}"
            for d in docs
        ])

        try:
            from agents.multi_model import ModelRouter
            prompt = f"""基于以下知识库内容回答问题。如果知识库没有相关信息，请如实说明。

知识库内容:
{context}

问题: {question}

请用中文回答，标注信息来源。"""
            resp = ModelRouter.smart_chat(messages=[{"role":"user","content":prompt}], mode="smart")
            answer = resp.get("content", "") if isinstance(resp, dict) else str(resp)
        except Exception as e:
            answer = f"AI回答生成失败: {e}\n\n检索到的相关内容:\n{context[:1000]}"

        return {
            "ok": True, "answer": answer,
            "sources": [{"title": d["doc"].get("title",""), "source": d["doc"].get("source",""), "score": d["score"]} for d in docs]
        }

    @classmethod
    def get_stats(cls) -> Dict:
        return {"total_docs": len(cls._docs), "indexed_words": len(cls._index), "has_chromadb": cls._get_collection() is not None}

    @classmethod
    def save(cls):
        from tools.memory_store import memory_store
        try:
            data = json.dumps([{"id": d["id"], "content": d["content"], "source": d.get("source",""), "title": d.get("title",""), "tags": d.get("tags",""), "created_at": d.get("created_at", 0)} for d in cls._docs], ensure_ascii=False)
            memory_store.set_knowledge("rag_docs", data)
        except Exception as e:
            logger.error(f"RAG持久化失败: {e}")

    @classmethod
    def load(cls):
        from tools.memory_store import memory_store
        try:
            data = memory_store.get_knowledge("rag_docs")
            if data:
                docs = json.loads(data) if isinstance(data, str) else data
                for d in docs:
                    cls.add_document(d["content"], d.get("source",""), d.get("title",""), d.get("tags",""))
                logger.info(f"RAG: 已恢复{len(docs)}篇文档")
                return True
        except Exception as e:
            logger.warning(f"RAG恢复失败: {e}")
        return False

rag_engine = RAGEngine()
try:
    RAGEngine.load()
except:
    pass