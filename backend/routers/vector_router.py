锘?""鍚戦噺璇箟璁板繂 API"""
from fastapi import APIRouter, Depends, Query
from auth import verify_token
from tools.vector_memory import VectorMemory

router = APIRouter(prefix="/agent/vector", tags=["VectorMemory"])

@router.post("/remember")
async def vector_remember(text: str = Query(...), category: str = "general", _=Depends(verify_token)):
    """淇濆瓨鍚戦噺璁板繂"""
    ok = await VectorMemory.remember(text, {"category": category})
    return {"ok": ok, "text": text[:50]}

@router.get("/search")
async def vector_search(q: str = Query(...), _=Depends(verify_token)):
    """璇箟鎼滅储"""
    results = await VectorMemory.semantic_search(q)
    return {"ok": True, "results": results, "count": len(results)}

@router.get("/stats")
async def vector_stats(_=Depends(verify_token)):
    """鍚戦噺璁板繂缁熻"""
    memories = VectorMemory.get_all()
    return {"ok": True, "total": len(memories), "avg_dim": len(memories[0]["vector"]) if memories else 0}
