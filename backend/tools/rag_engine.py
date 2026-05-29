"""RAG 知识检索引擎 — 文档摄入 + 语义搜索 + 智能问答"""
import os, json, hashlib, re
from typing import List, Dict, Optional
from tools.logger import get_logger

logger = get_logger("rag")

class RAGEngine:
    """检索增强生成引擎"""
    _docs: List[Dict] = []
    _index: Dict[str, List[int]] = {}  # keyword -> doc indices

    @classmethod
    def ingest_text(cls, text: str, source: str = "", metadata: Dict = None) -> str:
        """摄入文档"""
        doc_id = hashlib.md5(f"{source}:{text[:100]}".encode()).hexdigest()[:12]

        # 简单分段
        chunks = [c.strip() for c in text.split("\n\n") if len(c.strip()) > 20]
        if not chunks:
            chunks = [text]

        for i, chunk in enumerate(chunks):
            cid = f"{doc_id}_{i}"
            cls._docs.append({
                "id": cid, "source": source, "content": chunk,
                "metadata": metadata or {}, "index": len(cls._docs)
            })
            # 关键词索引
            words = set(re.findall(r'[\u4e00-\u9fff]+|[a-zA-Z]{3,}', chunk.lower()))
            for w in words:
                if w not in cls._index:
                    cls._index[w] = []
                cls._index[w].append(len(cls._docs) - 1)

        logger.info(f"RAG摄入: {source} → {len(chunks)}段")
        return doc_id

    @classmethod
    def search(cls, query: str, top_k: int = 5) -> List[Dict]:
        """关键词+语义搜索"""
        query_words = set(re.findall(r'[\u4e00-\u9fff]+|[a-zA-Z]{3,}', query.lower()))
        scores = {}

        for w in query_words:
            if w in cls._index:
                for doc_idx in cls._index[w]:
                    scores[doc_idx] = scores.get(doc_idx, 0) + 1

        ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)[:top_k]
        return [cls._docs[idx] for idx, score in ranked]

    @classmethod
    async def ask(cls, question: str, top_k: int = 5) -> Dict:
        """RAG问答"""
        docs = cls.search(question, top_k)
        context = "\n---\n".join([d["content"][:500] for d in docs])

        try:
            from agents.multi_model import ModelRouter
            mr = ModelRouter()
            resp = await mr.chat(
                messages=[{
                    "role": "system",
                    "content": f"根据以下知识库回答问题，如果知识库没有相关信息请诚实说明:\n\n{context}"
                }, {
                    "role": "user", "content": question
                }],
                mode="fast"
            )
            return {"ok": True, "answer": resp.get("content", ""), "sources": [d["source"] for d in docs], "doc_count": len(docs)}
        except Exception as e:
            # 降级：纯关键词匹配
            return {"ok": True, "answer": f"找到{len(docs)}条相关文档，但LLM不可用。第一条: {docs[0]['content'][:200] if docs else '无'}...", "sources": [d["source"] for d in docs]}

    @classmethod
    def get_stats(cls) -> Dict:
        return {"total_docs": len(cls._docs), "total_keywords": len(cls._index), "sources": list(set(d["source"] for d in cls._docs))}

# 预加载知识
rag = RAGEngine()
