"""客服面板 API — 消息管理/自动回复/日报"""
from datetime import datetime
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from auth import verify_token
from state import state
from risk import handle_risk

router = APIRouter(prefix="/agent/customer", tags=["Customer"])

def _get_messages():
    return state._data.setdefault("customer_messages", [])

class ReplyRequest(BaseModel):
    message_id: str
    reply: str

@router.get("/messages")
async def list_messages(limit: int = 50, _=Depends(verify_token)):
    await handle_risk("L1", "查看客服消息")
    msgs = _get_messages()[-limit:]
    return {"messages": msgs, "total": len(_get_messages()), "unreplied": sum(1 for m in msgs if not m.get("replied"))}

@router.post("/reply")
async def reply_message(req: ReplyRequest, _=Depends(verify_token)):
    await handle_risk("L2", f"回复消息: {req.message_id}")
    for m in _get_messages():
        if m.get("id") == req.message_id:
            m["reply"] = req.reply
            m["replied"] = True
            m["replied_at"] = datetime.now().isoformat()
            state._save()
            return {"ok": True, "message_id": req.message_id}
    return {"ok": False, "error": "消息不存在"}

@router.get("/stats")
async def customer_stats(_=Depends(verify_token)):
    msgs = _get_messages()
    replied = sum(1 for m in msgs if m.get("replied"))
    return {"total": len(msgs), "replied": replied, "pending": len(msgs) - replied}

@router.get("/report")
async def daily_report(_=Depends(verify_token)):
    await handle_risk("L1", "生成客服日报")
    from services import DiaryService
    journal = DiaryService.generate_daily()
    return {"ok": True, "report": journal}