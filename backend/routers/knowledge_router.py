"""RAG知识库 — 文档管理+向量化+检索增强"""
import json, os, hashlib
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Query
from auth import verify_token
from state import state
from risk import handle_risk

router = APIRouter(prefix="/agent/knowledge", tags=["RAG"])

def _get_kb():
    return state._data.setdefault("knowledge_base", [])

@router.post("/documents")
async def add_document(title: str = Query(...), content: str = Query(...), category: str = "general", tags: str = "",
                       _=Depends(verify_token)):
    """添加知识文档"""
    await handle_risk("L1", f"添加知识: {title}")
    kb = _get_kb()
    doc_id = hashlib.md5(title.encode()).hexdigest()[:12]
    doc = {"id": doc_id, "title": title, "content": content, "category": category,
           "tags": [t.strip() for t in tags.split(",") if t.strip()],
           "created_at": datetime.now().isoformat(), "updated_at": datetime.now().isoformat(),
           "chunks": [], "embedding": []}
    # 分块
    chunk_size = 500; overlap = 50
    for i in range(0, len(content), chunk_size - overlap):
        chunk = content[i:i+chunk_size]
        doc["chunks"].append({"index": len(doc["chunks"]), "text": chunk, "embedding": []})
    kb.append(doc)
    state._save()
    return {"ok": True, "document": {"id": doc_id, "title": title, "chunks": len(doc["chunks"])}}

@router.get("/documents")
async def list_documents(category: str = "", _=Depends(verify_token)):
    """知识文档列表"""
    kb = _get_kb()
    if category: kb = [d for d in kb if d.get("category") == category]
    summary = [{"id": d["id"], "title": d["title"], "category": d.get("category", "general"),
                "chunks": len(d.get("chunks", [])), "updated_at": d.get("updated_at", "")} for d in kb]
    return {"ok": True, "documents": summary, "count": len(summary)}

@router.get("/documents/{doc_id}")
async def get_document(doc_id: str, _=Depends(verify_token)):
    """获取文档详情"""
    kb = _get_kb()
    doc = next((d for d in kb if d["id"] == doc_id), None)
    if not doc: raise HTTPException(404, "文档不存在")
    return {"ok": True, "document": doc}

@router.delete("/documents/{doc_id}")
async def delete_document(doc_id: str, _=Depends(verify_token)):
    """删除文档"""
    kb = _get_kb()
    state._data["knowledge_base"] = [d for d in kb if d["id"] != doc_id]
    state._save()
    return {"ok": True}

@router.get("/search")
async def search_knowledge(q: str = Query(...), _=Depends(verify_token)):
    """搜索知识库(关键词+分块匹配)"""
    await handle_risk("L1", f"搜索知识: {q}")
    kb = _get_kb()
    results = []
    q_lower = q.lower()
    for doc in kb:
        score = 0
        if q_lower in doc["title"].lower(): score += 5
        for tag in doc.get("tags", []):
            if q_lower in tag.lower(): score += 3
        for chunk in doc.get("chunks", []):
            if q_lower in chunk["text"].lower(): score += 1
        if score > 0:
            results.append({"id": doc["id"], "title": doc["title"], "category": doc.get("category", "general"),
                           "score": score, "snippet": doc["content"][:200]})
    results.sort(key=lambda x: x["score"], reverse=True)
    return {"ok": True, "results": results, "count": len(results)}

@router.get("/categories")
async def list_categories(_=Depends(verify_token)):
    """知识分类"""
    kb = _get_kb()
    cats = {}
    for d in kb:
        cat = d.get("category", "general")
        cats[cat] = cats.get(cat, 0) + 1
    return {"ok": True, "categories": [{"name": k, "count": v} for k, v in cats.items()]}

@router.get("/rag/context")
async def get_rag_context(q: str = Query(...), max_chars: int = 2000, _=Depends(verify_token)):
    """获取RAG上下文(供AI对话注入)"""
    kb = _get_kb()
    if not kb: return {"ok": True, "context": "", "sources": []}
    q_lower = q.lower()
    scored = []
    for doc in kb:
        score = 0
        if q_lower in doc["title"].lower(): score += 5
        for chunk in doc.get("chunks", []):
            if q_lower in chunk["text"].lower(): score += 1
        if score > 0: scored.append({"doc": doc, "score": score})
    scored.sort(key=lambda x: x["score"], reverse=True)
    context_parts = []; sources = []
    chars = 0
    for s in scored[:5]:
        snippet = s["doc"]["content"][:500]
        if chars + len(snippet) > max_chars: break
        context_parts.append(f"[{s['doc']['title']}]\n{snippet}")
        sources.append(s["doc"]["title"])
        chars += len(snippet)
    return {"ok": True, "context": "\n\n".join(context_parts), "sources": sources}
