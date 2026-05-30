''"AI2.0 -- +RAG+++''"
import json, re, os
from datetime import datetime
from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from auth import verify_token
from state import state
from risk import handle_risk
from tools.vector_memory import VectorMemory

router = APIRouter(prefix="/agent/customer", tags=["CustomerAI"])

# =====  =====
FAQ_KNOWLEDGE = {
    '': ":7..'',24..",
    '': ":,3-7./1-3,3-7,7-15.",
    '': ":24-48..3-5.",
    '': ":''''.7-15,3-5.,.",
    '': ":/.''''.()().",
    '': ":Binance PayHuobi PayOKX Wallet..",
    '': ":..,.",
    '': ":///...",
    '': ":,.2,24..",
    '': ": 9:00-22:00.,:400-xxx-xxxx.:support@tiktook.eu.cc.",
}

# ->
INTENT_MAP = {
    '': ['', '', "return", "refund", ''],
    '': ['', "refund", '', ''],
    '': ['', "ship", '', '', ''],
    '': ['', '', "track", '', ''],
    '': ['', '', "exchange", '', ''],
    '': ['', "pay", '', '', ''],
    '': ['', "coupon", '', ''],
    '': ['', "vip", '', ''],
    '': ['', "complain", '', ''],
    '': ['', '', '', '', ''],
}


ESCALATE_KEYWORDS = ['', '', '', '', '', '', '', '']

class CustomerChatRequest(BaseModel):
    message: str
    session_id: str = ''
    user_name: str = ''

def _match_intent(message: str) -> str:
    ''''''
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
    ''''''
    msg_lower = message.lower()
    if any(kw in msg_lower for kw in ESCALATE_KEYWORDS):
        return True
    if history_count > 5:  # 5
        return True
    return False

def _get_knowledge(intent: str, message: str) -> str:
    ''''''
    if intent in FAQ_KNOWLEDGE:
        return FAQ_KNOWLEDGE[intent]
    # :FAQ
    msg_lower = message.lower()
    matches = []
    for topic, answer in FAQ_KNOWLEDGE.items():
        if any(kw in msg_lower for kw in INTENT_MAP.get(topic, [])):
            matches.append(answer)
    return "\n\n".join(matches[:2]) if matches else ''

async def _get_rag_context(message: str) -> str:
    ''''''
    try:
        results = await VectorMemory.search(message, top_k=3)
        if results:
            return ":\n" + "\n".join([r.get("text", '')[:200] for r in results])
    except Exception:
        pass
    return ''

# =====  =====
@router.post("/chat")
async def customer_chat(req: CustomerChatRequest, _=Depends(verify_token)):
    ''"AI -- +++''"
    message = req.message.strip()
    if not message:
        return {"reply": ",?", "intent": "greeting"}

    
    session_id = req.session_id or f"cs_{datetime.now().strftime('%Y%m%d%H%M%S')}"
    sessions = state._data.setdefault("customer_sessions", {})
    session = sessions.setdefault(session_id, {"messages": [], "intent": '', "escalated": False})
    session["messages"].append({"role": "user", "content": message, "time": datetime.now().isoformat()})
    
    
    intent = _match_intent(message)
    session["intent"] = intent
    
    
    if _should_escalate(message, len(session["messages"])):
        if not session["escalated"]:
            session["escalated"] = True
            
            tickets = state._data.setdefault("customer_tickets", [])
            ticket = {
                "id": f"TK{len(tickets)+1:04d}",
                "session": session_id,
                "user": req.user_name or '',
                "intent": intent,
                "last_message": message[:200],
                "created_at": datetime.now().isoformat(),
                "status": "pending",
                "priority": "P2",
            }
            tickets.insert(0, ticket)
            state._save()
            reply = f", {ticket['id']}.\n\n,.9:00-22:00,2."
        else:
            reply = f",.,."
    else:
        
        kb = _get_knowledge(intent, message)
        
        # RAG
        rag_ctx = await _get_rag_context(message)
        
        if kb:
            
            greetings = {
                1: f"!{intent},:\n\n{kb}\n\n?",
                2: f":\n\n{kb}\n\n?",
            }
            turn = len([m for m in session["messages"] if m["role"] == "user"])
            reply = greetings.get(turn, kb)
        else:
            
            reply = f"!AI,:\n\n /\n /\n /\n /\n /\n\n?"

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

# =====  =====
@router.get("/tickets")
async def list_tickets(status: str = Query(''), _=Depends(verify_token)):
    ''''''
    tickets = state._data.get("customer_tickets", [])
    if status:
        tickets = [t for t in tickets if t.get("status") == status]
    return {"ok": True, "total": len(tickets), "tickets": tickets[-50:]}

@router.post("/tickets/{ticket_id}/resolve")
async def resolve_ticket(ticket_id: str, resolution: str = Query(''), _=Depends(verify_token)):
    ''''''
    tickets = state._data.get("customer_tickets", [])
    for t in tickets:
        if t["id"] == ticket_id:
            t["status"] = "resolved"
            t["resolution"] = resolution
            t["resolved_at"] = datetime.now().isoformat()
            state._save()
            return {"ok": True, "ticket": ticket_id}
    return {"ok": False, "error": ''}

@router.get("/stats")
async def customer_stats(_=Depends(verify_token)):
    ''''''
    tickets = state._data.get("customer_tickets", [])
    sessions = state._data.get("customer_sessions", {})
    today = datetime.now().strftime("%Y-%m-%d")
    today_tickets = [t for t in tickets if t.get("created_at",'')[:10] == today]
    pending = [t for t in tickets if t.get("status") == "pending"]
    
    return {
        "ok": True,
        "today_tickets": len(today_tickets),
        "pending_tickets": len(pending),
        "total_tickets": len(tickets),
        "active_sessions": len(sessions),
        "avg_resolution_time": "2",  
    }

# =====  =====
@router.get("/faq")
async def list_faq(_=Depends(verify_token)):
    ''"FAQ''"
    return {"ok": True, "faq": [{"topic": k, "answer": v} for k, v in FAQ_KNOWLEDGE.items()]}

@router.post("/faq")
async def update_faq(topic: str = Query(...), answer: str = Query(...), _=Depends(verify_token)):
    ''"FAQ''"
    FAQ_KNOWLEDGE[topic] = answer
    return {"ok": True, "topic": topic}
