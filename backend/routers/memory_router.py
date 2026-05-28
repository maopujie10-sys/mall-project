"""Memory Agent API — 记忆系统入口"""
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
    """保存记忆"""
    await handle_risk("L1", "保存记忆", req.content[:50])
    return await MemoryAgent.remember(req.content, req.category, req.importance, req.tags)

@router.get("/recall")
async def recall(query: str = "", category: str = None, limit: int = 20, _=Depends(verify_token)):
    """检索记忆"""
    await handle_risk("L1", "检索记忆", query[:50])
    return await MemoryAgent.recall(query=query, category=category, limit=limit)

@router.post("/learn")
async def learn(req: LearnRequest, _=Depends(verify_token)):
    """从对话中学习"""
    await handle_risk("L1", "对话学习", req.topic)
    return await MemoryAgent.learn_from_conversation(req.user_message, req.ai_response, req.topic)

@router.get("/summary")
async def summary(category: str = None, days: int = 7, _=Depends(verify_token)):
    """记忆总结"""
    await handle_risk("L1", "记忆总结")
    return await MemoryAgent.summarize_memories(category, days)

@router.get("/related/{memory_id}")
async def related(memory_id: str, _=Depends(verify_token)):
    """相关记忆"""
    await handle_risk("L1", "相关记忆")
    return await MemoryAgent.find_related(memory_id)

@router.get("/profile")
async def user_profile(_=Depends(verify_token)):
    """用户画像"""
    await handle_risk("L1", "用户画像")
    return await MemoryAgent.get_user_profile()

@router.post("/habit")
async def learn_habit(habit_type: str = Query(...), detail: str = Query(...), _=Depends(verify_token)):
    """学习用户习惯"""
    await handle_risk("L1", "习惯学习")
    return await MemoryAgent.learn_user_habit(habit_type, detail)

@router.get("/stats")
async def memory_stats(_=Depends(verify_token)):
    """记忆统计"""
    await handle_risk("L1", "记忆统计")
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
    """清除旧记忆"""
    await handle_risk("L2", f"清除{days_old}天前旧记忆")
    return await MemoryAgent.cleanup(days_old)
