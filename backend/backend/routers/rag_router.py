''"RAG API''"
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from tools.rag_engine import rag
from auth import verify_token

router = APIRouter(prefix="/agent/rag", tags=["RAG"])

class IngestRequest(BaseModel):
    text: str
    source: str = ''

class AskRequest(BaseModel):
    question: str
    top_k: int = 5

@router.post("/ingest")
async def rag_ingest(req: IngestRequest, _=Depends(verify_token)):
    doc_id = rag.ingest_text(req.text, req.source)
    return {"ok": True, "doc_id": doc_id}

@router.post("/ask")
async def rag_ask(req: AskRequest, _=Depends(verify_token)):
    result = await rag.ask(req.question, req.top_k)
    return result

@router.get("/stats")
async def rag_stats(_=Depends(verify_token)):
    return {"ok": True, **rag.get_stats()}
