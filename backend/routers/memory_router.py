"""Memory Agent API -- 鐠佹澘绻傜化鑽ょ埠閸忋儱褰?""
from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from typing import Optional
from auth import verify_token
from risk import handle_risk
from agents.memory_agent import MemoryAgent

router = APIRouter(prefix="/agent/memory", tags=["Memory"])

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
    """娣囨繂鐡ㄧ拋鏉跨箓"""
    await handle_risk("L1", "娣囨繂鐡ㄧ拋鏉跨箓", req.content[:50])
    return await MemoryAgent.remember(req.content, req.category, req.importance, req.tags)

@router.get("/recall")
async def recall(query: str = "", category: str = None, limit: int = 20, _=Depends(verify_token)):
    """濡偓缁便垼顔囪箛?""
    await handle_risk("L1", "濡偓缁便垼顔囪箛?, query[:50])
    return await MemoryAgent.recall(query=query, category=category, limit=limit)

@router.post("/learn")
async def learn(req: LearnRequest, _=Depends(verify_token)):
    """娴犲骸顕拠婵呰厬鐎涳缚绡?""
    await handle_risk("L1", "鐎电鐦界€涳缚绡?, req.topic)
    return await MemoryAgent.learn_from_conversation(req.user_message, req.ai_response, req.topic)

@router.get("/summary")
async def summary(category: str = None, days: int = 7, _=Depends(verify_token)):
    """鐠佹澘绻傞幀鑽ょ波"""
    await handle_risk("L1", "鐠佹澘绻傞幀鑽ょ波")
    return await MemoryAgent.summarize_memories(category, days)

@router.get("/related/{memory_id}")
async def related(memory_id: str, _=Depends(verify_token)):
    """閻╃鍙х拋鏉跨箓"""
    await handle_risk("L1", "閻╃鍙х拋鏉跨箓")
    return await MemoryAgent.find_related(memory_id)

@router.get("/profile")
async def user_profile(_=Depends(verify_token)):
    """閻劍鍩涢悽璇插剼"""
    await handle_risk("L1", "閻劍鍩涢悽璇插剼")
    return await MemoryAgent.get_user_profile()

@router.post("/habit")
async def learn_habit(habit_type: str = Query(...), detail: str = Query(...), _=Depends(verify_token)):
    """鐎涳缚绡勯悽銊﹀煕娑旂姵鍎?""
    await handle_risk("L1", "娑旂姵鍎荤€涳缚绡?)
    return await MemoryAgent.learn_user_habit(habit_type, detail)

@router.get("/stats")
async def memory_stats(_=Depends(verify_token)):
    """鐠佹澘绻傜紒鐔活吀"""
    await handle_risk("L1", "鐠佹澘绻傜紒鐔活吀")
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
    """濞撳懘娅庨弮褑顔囪箛?""
    await handle_risk("L2", f"濞撳懘娅巤days_old}婢垛晛澧犻弮褑顔囪箛?)
    return await MemoryAgent.cleanup(days_old)

@router.get("/stats")
async def memory_stats(_=Depends(verify_token)):
    """鍚勫钩鍙拌蹇嗙粺璁?""
    try:
        from tools.memory_sync import MemorySync
        local = MemorySync.sync_pull() if hasattr(MemorySync,"sync_pull") else {}
        return {"ok":True,"local":len(local) if isinstance(local,dict) else 0,"telegram":0,"wechat":0}
    except:
        return {"ok":True,"local":0,"telegram":0,"wechat":0}

@router.post("/sync/{platform}")
async def sync_platform(platform: str, _=Depends(verify_token)):
    """鍚屾鎸囧畾骞冲彴璁板繂"""
    try:
        from tools.memory_sync import MemorySync
        if platform == "telegram":
            return MemorySync.push_to_telegram("鎵嬪姩鍚屾瑙﹀彂")
        elif platform == "wechat":
            return MemorySync.push_to_wechat("鎵嬪姩鍚屾瑙﹀彂")
        else:
            return {"ok":True,"message":"鏈湴宸插悓姝?,"local":MemorySync.sync_push({"synced":True,"time":__import__("time").time()})}
    except Exception as e:
        return {"ok":False,"error":str(e)}

@router.post("/push")
async def push_memory(data: dict = {}, _=Depends(verify_token)):
    """鎺ㄩ€佽蹇嗗埌鎵€鏈夊钩鍙?""
    try:
        msg = data.get("message","")
        from tools.memory_sync import MemorySync
        return MemorySync.sync_all_platforms(msg) if hasattr(MemorySync,"sync_all_platforms") else {"ok":False,"error":"sync_all_platforms not available"}
    except Exception as e:
        return {"ok":False,"error":str(e)}
