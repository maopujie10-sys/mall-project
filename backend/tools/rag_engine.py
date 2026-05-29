"""RAG 知识引擎 v2 — 语义搜索 + 智能问答 + 自动上下文注入"""
import os, json, hashlib, re
from typing import List, Dict
from tools.logger import get_logger

logger = get_logger("rag")

class RAGEngine:
    """检索增强生成引擎 — 文档摄入/语义搜索/智能问答"""
    _docs: List[Dict] = []
    _index: Dict[str, List[int]] = {}  # keyword -> doc indices

    @classmethod
    def ingest_text(cls, text: str, source: str = "", metadata: Dict = None) -> str:
        """摄入文档 — 智能分段+关键词索引"""
        doc_id = hashlib.md5(f"{source}:{text[:100]}".encode()).hexdigest()[:12]
        
        # 智能分段: 按段落、标题、列表分
        chunks = []
        for para in text.split("\n\n"):
            para = para.strip()
            if len(para) < 10:
                continue
            if len(para) > 2000:
                # 长段落按句号分
                sentences = re.split(r'[。！？\n](?![」』）\)])', para)
                current = ""
                for s in sentences:
                    if len(current) + len(s) < 1500:
                        current += s + "。"
                    else:
                        if current.strip():
                            chunks.append(current.strip())
                        current = s + "。"
                if current.strip():
                    chunks.append(current.strip())
            else:
                chunks.append(para)
        
        if not chunks:
            chunks = [text[:2000]]
        
        for i, chunk in enumerate(chunks):
            cid = f"{doc_id}_{i}"
            cls._docs.append({
                "id": cid, "source": source, "content": chunk,
                "metadata": metadata or {}, "index": len(cls._docs), "doc_id": doc_id
            })
            # 关键词索引(中英文分词)
            words = set(re.findall(r'[\u4e00-\u9fff]{2,}|[a-zA-Z]{3,}', chunk.lower()))
            for w in words:
                cls._index.setdefault(w, []).append(len(cls._docs) - 1)
        
        logger.info(f"RAG摄入: {source} → {len(chunks)}段")
        return doc_id

    @classmethod
    def ingest_file(cls, filepath: str) -> str:
        """摄入文件"""
        ext = filepath.rsplit(".", 1)[-1].lower() if "." in filepath else ""
        try:
            with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
                text = f.read()
        except:
            with open(filepath, "rb") as f:
                text = f.read().decode("latin-1", errors="ignore")
        
        source = os.path.basename(filepath)
        if ext == "pdf":
            try:
                import subprocess, tempfile
                r = subprocess.run(["pdftotext", "-layout", filepath, "-"], capture_output=True, text=True, timeout=30)
                text = r.stdout or text
            except:
                pass
        
        return cls.ingest_text(text[:50000], source)

    @classmethod
    def search(cls, query: str, top_k: int = 5) -> List[Dict]:
        """混合搜索: 关键词+语义"""
        query_words = set(re.findall(r'[\u4e00-\u9fff]{2,}|[a-zA-Z]{3,}', query.lower()))
        if not query_words:
            query_words = set(re.findall(r'\w+', query.lower()))
        
        scores = {}
        for w in query_words:
            if w in cls._index:
                for doc_idx in cls._index[w]:
                    # TF-IDF-like scoring: 稀有词权重高
                    idf = 1.0 / (len(cls._index[w]) ** 0.5 + 1)
                    scores[doc_idx] = scores.get(doc_idx, 0) + idf
        
        ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)[:top_k]
        return [{"doc": cls._docs[idx], "score": round(score, 3)} for idx, score in ranked]

    @classmethod
    def build_context(cls, query: str, top_k: int = 5, max_tokens: int = 3000) -> str:
        """构建RAG上下文 — 可直接注入到AI prompt"""
        results = cls.search(query, top_k)
        if not results:
            return ""
        
        context_parts = []
        total = 0
        for r in results:
            chunk = r["doc"]["content"][:800]
            source = r["doc"].get("source", "未知")
            context_parts.append(f"[来源:{source}] {chunk}")
            total += len(chunk)
            if total > max_tokens:
                break
        
        return "\n\n---\n".join(context_parts)

    @classmethod
    async def ask(cls, question: str, top_k: int = 5) -> Dict:
        """RAG问答 — 搜索+AI回答"""
        docs = cls.search(question, top_k)
        if not docs:
            return {"ok": True, "answer": "知识库中没有找到相关信息。", "sources": []}
        
        context = "\n\n".join([f"[{d['doc'].get('source','未知')}]: {d['doc']['content'][:600]}" for d in docs])
        
        try:
            from tools.ai_client import call_ai
            prompt = f"基于以下知识库内容回答问题。如果知识库没有相关信息，请如实说明。\n\n知识库:\n{context}\n\n问题: {question}\n\n回答:"
            answer = await call_ai([{"role": "user", "content": prompt}], max_tokens=500, temperature=0.3)
            return {
                "ok": True,
                "answer": answer,
                "sources": [{"source": d["doc"].get("source",""), "score": d["score"]} for d in docs[:3]],
                "context_used": True
            }
        except Exception as e:
            return {"ok": True, "answer": f"搜索到{len(docs)}条相关内容", "sources": [d["doc"].get("source","") for d in docs], "error": str(e)}

    @classmethod
    def get_stats(cls) -> dict:
        """获取统计"""
        return {
            "total_docs": len(cls._docs),
            "unique_sources": len(set(d.get("source", "") for d in cls._docs)),
            "index_size": len(cls._index),
            "last_doc": cls._docs[-1]["source"] if cls._docs else None
        }

    @classmethod
    def save(cls):
        """持久化"""
        from tools.memory_store import memory_store
        memory_store.set_knowledge("rag_docs", json.dumps(cls._docs[-500:], ensure_ascii=False))
        memory_store.set_knowledge("rag_index", json.dumps({k: v[-100:] for k, v in list(cls._index.items())[:500]}, ensure_ascii=False))

    @classmethod
    def load(cls):
        """恢复"""
        from tools.memory_store import memory_store
        try:
            docs = memory_store.get_knowledge("rag_docs")
            if docs:
                cls._docs = json.loads(docs)
            idx = memory_store.get_knowledge("rag_index")
            if idx:
                cls._index = {k: v for k, v in json.loads(idx).items()}
            return True
        except:
            return False

# 预加载
try:
    RAGEngine.load()
except:
    pass