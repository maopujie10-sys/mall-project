"""客服消息管理"""
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from main import verify_token
from state import state

router = APIRouter(prefix="/customer", tags=["Customer"])

# In-memory message store
_messages = [
    {"id": 1, "user": "用户***123", "content": "我的订单什么时候发货？", "time": "10:23", "unread": True},
    {"id": 2, "user": "用户***456", "content": "充值还没到账，麻烦查一下", "time": "10:45", "unread": True},
    {"id": 3, "user": "用户***789", "content": "想退货，怎么操作？", "time": "11:02", "unread": True},
    {"id": 4, "user": "用户***012", "content": "商品质量很好，好评！", "time": "11:15", "unread": False},
    {"id": 5, "user": "用户***345", "content": "可以开发票吗？", "time": "11:30", "unread": True},
]


class ReadRequest(BaseModel):
    messageId: int


class TransferRequest(BaseModel):
    messageIds: list[int]


@router.get("/messages")
async def get_messages(_=Depends(verify_token)):
    return _messages


@router.post("/read")
async def mark_read(req: ReadRequest, _=Depends(verify_token)):
    for m in _messages:
        if m["id"] == req.messageId:
            m["unread"] = False
            return {"result": "ok", "messageId": req.messageId}
    raise HTTPException(status_code=404, detail="Message not found")


@router.post("/read-all")
async def mark_all_read(_=Depends(verify_token)):
    count = 0
    for m in _messages:
        if m["unread"]:
            m["unread"] = False
            count += 1
    return {"result": "ok", "marked": count}


@router.post("/transfer")
async def transfer_to_human(req: TransferRequest, _=Depends(verify_token)):
    transferred = []
    for mid in req.messageIds:
        for m in _messages:
            if m["id"] == mid:
                m["unread"] = False
                transferred.append(mid)
                break
    state.add_task(f"客服转人工: {len(transferred)}条消息", risk="L2", status="完成")
    return {"result": "ok", "transferred": len(transferred), "messageIds": transferred}
