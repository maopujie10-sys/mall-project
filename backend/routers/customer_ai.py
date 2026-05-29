"""AI智能客服2.0 — 多轮对话+知识库RAG+意图识别+智能转人工+工单创建"""
import json, re, os
from datetime import datetime
from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from auth import verify_token
from state import state
from risk import handle_risk
from tools.vector_memory import VectorMemory

router = APIRouter(prefix="/agent/customer", tags=["CustomerAI"])

# ===== 知识库 =====
FAQ_KNOWLEDGE = {
    "退货": "退货政策：收到商品7天内可申请退货。商品需保持原包装、未使用。请到'我的订单'页面申请退货，客服会在24小时内审核。退货地址将以站内信形式发送。",
    "退款": "退款时效：退货审核通过后，退款将在3-7个工作日内原路返回。支付宝/微信1-3天，银行卡3-7天，信用卡7-15天。",
    "发货": "发货时效：现货商品下单后24-48小时内发货。预售商品按页面标注时间发货。海外直邮商品3-5个工作日发货。",
    "物流": "物流查询：请到'我的订单'点击'查看物流'。国际物流通常7-15天，国内物流3-5天。如超过预计时间未收到，请联系客服。",
    "换货": "换货政策：支持同款换色/换码。请在'我的订单'选择'申请换货'。换货运费由平台承担（质量问题）或用户承担（个人原因）。",
    "支付": "支持支付方式：支付宝、微信支付、银行卡、Binance Pay、Huobi Pay、OKX Wallet。如支付失败请检查银行卡限额或切换支付方式。",
    "优惠券": "优惠券使用：在结算页面选择可用优惠券。满减券需达到最低消费金额。优惠券不可叠加使用，每笔订单限用一张。",
    "会员": "会员等级：普通/银卡/金卡/钻石。升级依据为累计消费金额。金卡及以上享专属客服、优先发货、生日礼包。",
    "投诉": "投诉处理：请描述您的问题，我们会升级给高级客服处理。一般2小时内响应，24小时内给出解决方案。如不满意可申请平台介入。",
    "联系": "客服工作时间：周一至周日 9:00-22:00。在线客服即时回复，电话客服：400-xxx-xxxx。英文客服：support@tiktook.eu.cc。",
}

# 意图->知识库映射
INTENT_MAP = {
    "退货": ["退货", "退", "return", "refund", "退款"],
    "退款": ["退款", "refund", "退钱", "到账"],
    "发货": ["发货", "ship", "送货", "多久", "什么时候"],
    "物流": ["物流", "快递", "track", "到哪", "查询"],
    "换货": ["换货", "换", "exchange", "尺码", "颜色"],
    "支付": ["支付", "pay", "付款", "扣款", "失败"],
    "优惠券": ["优惠券", "coupon", "折扣", "满减"],
    "会员": ["会员", "vip", "等级", "权益"],
    "投诉": ["投诉", "complain", "不满", "举报"],
    "联系": ["客服", "人工", "电话", "邮箱", "联系"],
}

# 转人工触发词
ESCALATE_KEYWORDS = ["人工", "转人工", "人工客服", "投诉", "找你们领导", "电话", "打电话", "升级"]

class CustomerChatRequest(BaseModel):
    message: str
    session_id: str = ""
    user_name: str = ""

def _match_intent(message: str) -> str:
    """匹配用户意图"""
    msg_lower = message.lower()
    scores = {}
    for intent, keywords in INTENT_MAP.items():
        score = sum(1 for kw in keywords if kw in msg_lower)
        if score > 0:
            scores[intent] = score
    if scores:
        return max(scores, key=scores.get)
    return "general"

def _should_escalate(message: str, history_count: int = 0) -> bool:
    """判断是否需要转人工"""
    msg_lower = message.lower()
    if any(kw in msg_lower for kw in ESCALATE_KEYWORDS):
        return True
    if history_count > 5:  # 对话超过5轮自动转人工
        return True
    return False

def _get_knowledge(intent: str, message: str) -> str:
    """获取相关知识"""
    if intent in FAQ_KNOWLEDGE:
        return FAQ_KNOWLEDGE[intent]
    # 通用意图：匹配所有FAQ
    msg_lower = message.lower()
    matches = []
    for topic, answer in FAQ_KNOWLEDGE.items():
        if any(kw in msg_lower for kw in INTENT_MAP.get(topic, [])):
            matches.append(answer)
    return "\n\n".join(matches[:2]) if matches else ""

async def _get_rag_context(message: str) -> str:
    """从向量记忆获取相关历史对话"""
    try:
        results = await VectorMemory.search(message, top_k=3)
        if results:
            return "历史相关对话:\n" + "\n".join([r.get("text", "")[:200] for r in results])
    except Exception:
        pass
    return ""

# ===== 对话引擎 =====
@router.post("/chat")
async def customer_chat(req: CustomerChatRequest, _=Depends(verify_token)):
    """AI客服对话 — 多轮+知识库+意图+智能转人工"""
    message = req.message.strip()
    if not message:
        return {"reply": "您好，请问有什么可以帮您的？", "intent": "greeting"}

    # 会话管理
    session_id = req.session_id or f"cs_{datetime.now().strftime('%Y%m%d%H%M%S')}"
    sessions = state._data.setdefault("customer_sessions", {})
    session = sessions.setdefault(session_id, {"messages": [], "intent": "", "escalated": False})
    session["messages"].append({"role": "user", "content": message, "time": datetime.now().isoformat()})
    
    # 意图识别
    intent = _match_intent(message)
    session["intent"] = intent
    
    # 转人工判断
    if _should_escalate(message, len(session["messages"])):
        if not session["escalated"]:
            session["escalated"] = True
            # 创建工单
            tickets = state._data.setdefault("customer_tickets", [])
            ticket = {
                "id": f"TK{len(tickets)+1:04d}",
                "session": session_id,
                "user": req.user_name or "匿名用户",
                "intent": intent,
                "last_message": message[:200],
                "created_at": datetime.now().isoformat(),
                "status": "pending",
                "priority": "P2",
            }
            tickets.insert(0, ticket)
            state._save()
            reply = f"我已将您的问题升级给人工客服，工单号 {ticket['id']}。\n\n您可以继续描述问题，或等待客服主动联系您。工作时间9:00-22:00，通常2小时内回复。"
        else:
            reply = f"您的工单已提交，人工客服会尽快回复。如需紧急处理，请拨打客服电话。"
    else:
        # 知识库回复
        kb = _get_knowledge(intent, message)
        
        # RAG上下文
        rag_ctx = await _get_rag_context(message)
        
        if kb:
            # 根据意图和对话轮次生成自然回复
            greetings = {
                1: f"您好！关于{intent}的问题，我来为您解答：\n\n{kb}\n\n还有其他问题吗？",
                2: f"补充说明：\n\n{kb}\n\n需要进一步帮助吗？",
            }
            turn = len([m for m in session["messages"] if m["role"] == "user"])
            reply = greetings.get(turn, kb)
        else:
            # 通用回复
            reply = f"您好！我是AI客服，可以帮您解答以下问题：\n\n• 退货/退款政策\n• 发货/物流查询\n• 支付/换货\n• 优惠券/会员\n• 投诉/人工客服\n\n请告诉我您遇到了什么问题？"

    session["messages"].append({"role": "assistant", "content": reply, "time": datetime.now().isoformat()})
    if len(session["messages"]) > 20:
        session["messages"] = session["messages"][-20:]
    state._save()

    return {
        "reply": reply,
        "intent": intent,
        "session_id": session_id,
        "escalated": session["escalated"],
        "turn": len([m for m in session["messages"] if m["role"] == "user"]),
    }

# ===== 工单管理 =====
@router.get("/tickets")
async def list_tickets(status: str = Query(""), _=Depends(verify_token)):
    """客服工单列表"""
    tickets = state._data.get("customer_tickets", [])
    if status:
        tickets = [t for t in tickets if t.get("status") == status]
    return {"ok": True, "total": len(tickets), "tickets": tickets[-50:]}

@router.post("/tickets/{ticket_id}/resolve")
async def resolve_ticket(ticket_id: str, resolution: str = Query(""), _=Depends(verify_token)):
    """解决工单"""
    tickets = state._data.get("customer_tickets", [])
    for t in tickets:
        if t["id"] == ticket_id:
            t["status"] = "resolved"
            t["resolution"] = resolution
            t["resolved_at"] = datetime.now().isoformat()
            state._save()
            return {"ok": True, "ticket": ticket_id}
    return {"ok": False, "error": "工单不存在"}

@router.get("/stats")
async def customer_stats(_=Depends(verify_token)):
    """客服统计数据"""
    tickets = state._data.get("customer_tickets", [])
    sessions = state._data.get("customer_sessions", {})
    today = datetime.now().strftime("%Y-%m-%d")
    today_tickets = [t for t in tickets if t.get("created_at","")[:10] == today]
    pending = [t for t in tickets if t.get("status") == "pending"]
    
    return {
        "ok": True,
        "today_tickets": len(today_tickets),
        "pending_tickets": len(pending),
        "total_tickets": len(tickets),
        "active_sessions": len(sessions),
        "avg_resolution_time": "2小时",  # 可后续精确计算
    }

# ===== 知识库管理 =====
@router.get("/faq")
async def list_faq(_=Depends(verify_token)):
    """FAQ知识库"""
    return {"ok": True, "faq": [{"topic": k, "answer": v} for k, v in FAQ_KNOWLEDGE.items()]}

@router.post("/faq")
async def update_faq(topic: str = Query(...), answer: str = Query(...), _=Depends(verify_token)):
    """更新FAQ"""
    FAQ_KNOWLEDGE[topic] = answer
    return {"ok": True, "topic": topic}
