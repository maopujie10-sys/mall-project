"""RAG Knowledge API - Document ingestion, semantic search, AI Q&A"""
from fastapi import APIRouter, Depends, UploadFile, File, Form
from pydantic import BaseModel
from tools.rag_engine import RAGEngine
from auth import verify_token

router = APIRouter(prefix="/agent/rag", tags=["RAG"])

class IngestRequest(BaseModel):
    text: str
    source: str = ""
    title: str = ""
    tags: str = ""

class AskRequest(BaseModel):
    question: str
    top_k: int = 5

@router.post("/ingest")
async def rag_ingest(req: IngestRequest, _=Depends(verify_token)):
    """Ingest a text document into the knowledge base"""
    result = RAGEngine.add_document(req.text, req.source, req.title, req.tags)
    RAGEngine.save()
    return {"ok": True, "doc_id": result["id"], "stats": RAGEngine.get_stats()}

@router.post("/ingest-file")
async def rag_ingest_file(file: UploadFile = File(...), source: str = Form(""), _=Depends(verify_token)):
    """Upload and ingest a file into the knowledge base"""
    try:
        content = await file.read()
        text = content.decode("utf-8", errors="replace")
    except Exception as e:
        return {"ok": False, "error": f"File read error: {str(e)}"}
    
    if not text.strip():
        return {"ok": False, "error": "File is empty"}
    
    title = file.filename or "uploaded_doc"
    result = RAGEngine.add_document(text, source or "file_upload", title)
    RAGEngine.save()
    return {"ok": True, "doc_id": result["id"], "title": title, "stats": RAGEngine.get_stats()}

@router.post("/ask")
async def rag_ask(req: AskRequest, _=Depends(verify_token)):
    """Ask a question against the knowledge base with AI-powered answer"""
    result = RAGEngine.ask(req.question, req.top_k)
    return result

@router.get("/stats")
async def rag_stats(_=Depends(verify_token)):
    """Get RAG knowledge base statistics"""
    return {"ok": True, **RAGEngine.get_stats()}

@router.get("/search")
async def rag_search(q: str = "", top_k: int = 10, _=Depends(verify_token)):
    """Search documents by query"""
    if not q:
        return {"ok": False, "error": "Query required"}
    results = RAGEngine.search(q, top_k)
    return {"ok": True, "results": results, "query": q}

@router.delete("/clear")
async def rag_clear(_=Depends(verify_token)):
    """Clear all documents from the knowledge base"""
    RAGEngine._docs = []
    RAGEngine._index = {}
    RAGEngine._collection = None
    RAGEngine.save()
    return {"ok": True, "message": "Knowledge base cleared"}
