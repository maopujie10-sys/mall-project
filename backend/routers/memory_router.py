"""Memory Agent API 鈥?璁板繂绯荤粺鍏ュ彛"""
from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from typing import Optional
from auth import verify_token
from risk import handle_risk
from agents.memory_agent import MemoryAgent

router = APIRouter(prefix="/memory", tags=["Memory"])

class RememberRequest(BaseModel):
    content: str
    category: str = "general"
    importance: int = 1
    tags: list = []

class LearnRequest(BaseModel):
    user_message: str
    ai_response: str
    topic: str = ""

@router.post("/remember")
async def remember(req: RememberRequest, _=Depends(verify_token)):
    """淇濆瓨璁板繂"""
    await handle_risk("L1", "淇濆瓨璁板繂", req.content[:50])
    return await MemoryAgent.remember(req.content, req.category, req.importance, req.tags)

@router.get("/recall")
async def recall(query: str = "", category: str = None, limit: int = 20, _=Depends(verify_token)):
    """妫€绱㈣蹇?""
    await handle_risk("L1", "妫€绱㈣蹇?, query[:50])
    return await MemoryAgent.recall(query=query, category=category, limit=limit)

@router.post("/learn")
async def learn(req: LearnRequest, _=Depends(verify_token)):
    """浠庡璇濅腑瀛︿範"""
    await handle_risk("L1", "瀵硅瘽瀛︿範", req.topic)
    return await MemoryAgent.learn_from_conversation(req.user_message, req.ai_response, req.topic)

@router.get("/summary")
async def summary(category: str = None, days: int = 7, _=Depends(verify_token)):
    """璁板繂鎬荤粨"""
    await handle_risk("L1", "璁板繂鎬荤粨")
    return await MemoryAgent.summarize_memories(category, days)

@router.get("/related/{memory_id}")
async def related(memory_id: str, _=Depends(verify_token)):
    """鐩稿叧璁板繂"""
    await handle_risk("L1", "鐩稿叧璁板繂")
    return await MemoryAgent.find_related(memory_id)

@router.get("/profile")
async def user_profile(_=Depends(verify_token)):
    """鐢ㄦ埛鐢诲儚"""
    await handle_risk("L1", "鐢ㄦ埛鐢诲儚")
    return await MemoryAgent.get_user_profile()

@router.post("/habit")
async def learn_habit(habit_type: str = Query(...), detail: str = Query(...), _=Depends(verify_token)):
    """瀛︿範鐢ㄦ埛涔犳儻"""
    await handle_risk("L1", "涔犳儻瀛︿範")
    return await MemoryAgent.learn_user_habit(habit_type, detail)

@router.get("/stats")
async def memory_stats(_=Depends(verify_token)):
    """璁板繂缁熻"""
    await handle_risk("L1", "璁板繂缁熻")
    memories = await MemoryAgent.recall(limit=9999)
    memories_list = memories.get("memories", [])
    total = len(memories_list)
    categories = {}
    for m in memories_list:
        cat = m.get("category", "general")
        categories[cat] = categories.get(cat, 0) + 1
    return {
        "total": total,
        "categories": categories,
        "avg_importance": round(sum(m.get("importance", 1) for m in memories_list) / max(total, 1), 1),
    }

@router.post("/cleanup")
async def cleanup_memory(days_old: int = 30, _=Depends(verify_token)):
    """娓呴櫎鏃ц蹇?""
    await handle_risk("L2", f"娓呴櫎{days_old}澶╁墠鏃ц蹇?)
    return await MemoryAgent.cleanup(days_old)
