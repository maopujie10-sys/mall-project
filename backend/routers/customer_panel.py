"""客服面板 API -- 消息管理/自动回复/日报"""
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

@router.get("/messages/stats")
async def customer_message_stats(_=Depends(verify_token)):
    msgs = _get_messages()
    replied = sum(1 for m in msgs if m.get("replied"))
    return {"total": len(msgs), "replied": replied, "pending": len(msgs) - replied}

class ReadRequest(BaseModel):
    messageId: str

@router.post("/read")
async def mark_read(req: ReadRequest, _=Depends(verify_token)):
    for m in _get_messages():
        if m.get("id") == req.messageId:
            m["read"] = True
            state._save()
            return {"ok": True}
    return {"ok": False, "error": "消息不存在"}

@router.post("/read-all")
async def mark_all_read(_=Depends(verify_token)):
    for m in _get_messages():
        m["read"] = True
    state._save()
    return {"ok": True, "count": len(_get_messages())}

class TransferRequest(BaseModel):
    messageIds: list

@router.post("/transfer")
async def transfer_to_human(req: TransferRequest, _=Depends(verify_token)):
    await handle_risk("L2", f"转人工: {len(req.messageIds)}条消息")
    for m in _get_messages():
        if m.get("id") in req.messageIds:
            m["transferred"] = True
            m["transferred_at"] = datetime.now().isoformat()
    state._save()
    return {"ok": True, "count": len(req.messageIds)}

@router.get("/report")
async def daily_report(_=Depends(verify_token)):
    await handle_risk("L1", "生成客服日报")
    from services import DiaryService
    journal = DiaryService.generate_daily()
    return {"ok": True, "report": journal}