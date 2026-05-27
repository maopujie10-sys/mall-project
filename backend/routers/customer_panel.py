"""客服消息管理 + 自动回复 + 话术库 + 日报"""
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from auth import verify_token
from state import state
from risk import handle_risk
from mask import mask_text

router = APIRouter(prefix="/customer", tags=["Customer"])

def _get_messages():
    return state._data.setdefault("customer_messages", [])

class Message(BaseModel):
    user: str
    content: str
    source: str = "web"

class ReadRequest(BaseModel):
    messageId: int

class TransferRequest(BaseModel):
    messageIds: list[int]

class AutoReplyRequest(BaseModel):
    message: str
    userId: str = ""

class FaqRequest(BaseModel):
    question: str
    answer: str

# ===== 话术库 =====
FAQ = {
    "发货": "您的订单一般付款后 24 小时内发货，节假日顺延。如需加急请联系在线客服。",
    "退货": "支持 7 天无理由退货，商品需保持原样。请在后台申请退货并填写退货原因。",
    "退款": "退款将在卖家确认退货后 1-3 个工作日原路返回。如超时未到账请联系客服。",
    "物流": "您可以在订单详情页查看物流信息。如长期未更新，请提供订单号为您查询。",
    "优惠券": "优惠券可在【我的-优惠券】中查看。部分优惠券有使用门槛，请仔细阅读规则。",
    "密码": "请在登录页点击【忘记密码】，通过注册手机号或邮箱重置。",
    "注册": "点击首页【注册】按钮，使用手机号完成注册。如收不到验证码请检查拦截短信。",
    "投诉": "已记录您的投诉，将在 1 个工作日内由专人处理。如情况紧急请拨打客服热线。",
}

COMPLAINT_KEYWORDS = ["投诉", "退款", "骗子", "报警", "没人处理", "不到账", "举报", "诈骗"]

@router.post("/messages")
async def add_message(req: Message):
    msgs = _get_messages()
    msg_id = len(msgs) + 1
    entry = {"id": msg_id, "user": req.user, "content": req.content, "source": req.source, "time": datetime.now().strftime("%H:%M:%S"), "unread": True}
    msgs.insert(0, entry)
    if len(msgs) > 500:
        msgs[:] = msgs[:500]
    state._save()
    entry["user"] = mask_text(entry["user"], level="user")
    return entry

@router.get("/messages")
async def get_messages(_=Depends(verify_token)):
    await handle_risk("L1", "查看客服消息")
    msgs = _get_messages()
    for m in msgs:
        if "content" in m:
            m["content"] = mask_text(m["content"], level="user")
    return msgs

@router.post("/read")
async def mark_read(req: ReadRequest, _=Depends(verify_token)):
    await handle_risk("L1", "标记消息已读", f"messageId={req.messageId}")
    for m in _get_messages():
        if m["id"] == req.messageId:
            m["unread"] = False
            state._save()
            return {"result": "ok", "messageId": req.messageId}
    raise HTTPException(status_code=404, detail="Message not found")

@router.post("/read-all")
async def mark_all_read(_=Depends(verify_token)):
    await handle_risk("L1", "标记全部已读")
    count = sum(1 for m in _get_messages() if m["unread"])
    for m in _get_messages():
        m["unread"] = False
    state._save()
    return {"result": "ok", "marked": count}

@router.post("/transfer")
async def transfer_to_human(req: TransferRequest, _=Depends(verify_token)):
    await handle_risk("L2", "客服转人工", f"{len(req.messageIds)}条消息")
    transferred = []
    for mid in req.messageIds:
        for m in _get_messages():
            if m["id"] == mid:
                m["unread"] = False
                transferred.append(mid)
                break
    state._save()
    return {"result": "ok", "transferred": len(transferred), "messageIds": transferred}

@router.post("/auto-reply")
async def auto_reply(req: AutoReplyRequest, _=Depends(verify_token)):
    """自动回复 — 识别问题类型并回复"""
    await handle_risk("L1", "客服自动回复", req.message[:50])
    msg = req.message.lower()
    is_complaint = any(kw in msg for kw in COMPLAINT_KEYWORDS)
    reply = ""
    for keyword, answer in FAQ.items():
        if keyword in msg:
            reply = answer
            break
    if not reply:
        reply = "您好，您的问题已收到，正在为您查询，请稍候。"
    return {"reply": reply, "matched": bool(reply), "is_complaint": is_complaint, "need_human": is_complaint or not reply}

@router.get("/faq")
async def list_faq(_=Depends(verify_token)):
    """查看话术库"""
    await handle_risk("L1", "查看客服话术库")
    return {"faq": [{"keyword": k, "answer": v} for k, v in FAQ.items()], "count": len(FAQ)}

@router.post("/faq")
async def add_faq(req: FaqRequest, _=Depends(verify_token)):
    """添加话术"""
    await handle_risk("L2", "添加客服话术", req.question)
    FAQ[req.question] = req.answer
    return {"added": True, "keyword": req.question}

@router.get("/report")
async def daily_report(_=Depends(verify_token)):
    """生成客服日报"""
    await handle_risk("L1", "生成客服日报")
    msgs = state._data.get("customer_messages", [])
    today = datetime.now().strftime("%Y-%m-%d")
    today_msgs = [m for m in msgs if today in m.get("time", "")]
    complaints = [m for m in today_msgs if any(k in m.get("content", "").lower() for k in COMPLAINT_KEYWORDS)]
    return {
        "date": today,
        "total": len(msgs),
        "today": len(today_msgs),
        "complaints": len(complaints),
        "complaint_rate": f"{len(complaints)/max(len(today_msgs),1)*100:.1f}%",
    }
