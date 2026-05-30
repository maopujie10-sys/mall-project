"""AI -- ///v1"""
from fastapi import APIRouter, Depends
from auth import verify_token
from risk import handle_risk
from state import state
from pydantic import BaseModel
from datetime import datetime

router = APIRouter(prefix="/agent/autoreply", tags=["AutoReply"])

class RuleCreate(BaseModel):
    keyword: str
    reply: str
    category: str = "general"
    priority: int = 0

class AutoReplyRequest(BaseModel):
    message: str
    user_id: str = ''

@router.post("/reply")
async def auto_reply(req: AutoReplyRequest, _=Depends(verify_token)):
    ''"AI''"
    await handle_risk("L1", "AI")
    rules = state._data.get("auto_reply_rules", [])
    msg_lower = req.message.lower()
    
    for rule in sorted(rules, key=lambda r: -r.get("priority", 0)):
        if rule.get("keyword",'').lower() in msg_lower:
            reply = rule["reply"]
            _log_conversation(req.message, reply, "rule")
            return {"ok": True, "reply": reply, "matched": True, "method": "rule",
                    "confidence": "high", "transfer": False}
    # AI()
    from agents.multi_model import ModelRouter, ModelMode
    try:
        config = ModelRouter.route(ModelMode.BALANCE)
        import httpx
        async with httpx.AsyncClient(timeout=15) as c:
            resp = await c.post(f"{config.base_url}/chat/completions",
                headers={"Authorization": f"Bearer {config.api_key}"},
                json={"model": config.model_name, "messages": [
                    {"role":"system","content":"Friday AI.., []."},
                    {"role":"user","content": req.message}], "max_tokens": 300})
            data = resp.json()
            reply = data.get("choices",[{}])[0].get("message",{}).get("content",'')
            need_transfer = "[]" in reply
            if need_transfer: reply = reply.replace("[]",'').strip()
            _log_conversation(req.message, reply, "ai")
            return {"ok": True, "reply": reply, "matched": True, "method": "ai",
                    "confidence": "medium", "transfer": need_transfer}
    except Exception as e:
        fallback = f",.."
        _log_conversation(req.message, fallback, "fallback")
        return {"ok": True, "reply": fallback, "matched": False, "method": "fallback", "transfer": True}

@router.get("/rules")
async def list_rules(_=Depends(verify_token)):
    ''''''
    return {"ok": True, "rules": state._data.get("auto_reply_rules", [])}

@router.post("/rules")
async def create_rule(rule: RuleCreate, _=Depends(verify_token)):
    ''''''
    await handle_risk("L2", f": {rule.keyword}")
    rules = state._data.setdefault("auto_reply_rules", [])
    rules.append({"id": f"R{datetime.now().strftime('%Y%m%d%H%M%S')}",
                  "keyword": rule.keyword, "reply": rule.reply,
                  "category": rule.category, "priority": rule.priority,
                  "created_at": datetime.now().isoformat(), "enabled": True})
    state._save()
    return {"ok": True, "rules": rules}

@router.delete("/rules/{rule_id}")
async def delete_rule(rule_id: str, _=Depends(verify_token)):
    ''''''
    await handle_risk("L2", f": {rule_id}")
    rules = state._data.setdefault("auto_reply_rules", [])
    state._data["auto_reply_rules"] = [r for r in rules if r.get("id") != rule_id]
    state._save()
    return {"ok": True, "deleted": rule_id}

@router.get("/conversations")
async def recent_conversations(limit: int = 20, _=Depends(verify_token)):
    ''''''
    return {"ok": True, "conversations": state._data.get("auto_reply_logs", [])[-limit:]}

@router.get("/stats")
async def auto_reply_stats(_=Depends(verify_token)):
    ''''''
    logs = state._data.get("auto_reply_logs", [])
    total = len(logs)
    rule_count = sum(1 for l in logs if l.get("method") == "rule")
    ai_count = sum(1 for l in logs if l.get("method") == "ai")
    fallback_count = sum(1 for l in logs if l.get("method") == "fallback")
    return {"ok": True, "stats": {"total_replies": total, "rule_matched": rule_count,
            "ai_replied": ai_count, "fallback": fallback_count,
            "auto_rate": f"{round((rule_count+ai_count)/max(total,1)*100)}%"}}

def _log_conversation(msg: str, reply: str, method: str):
    logs = state._data.setdefault("auto_reply_logs", [])
    logs.append({"time": datetime.now().isoformat(), "message": msg[:200],
                 "reply": reply[:200], "method": method})
    if len(logs) > 1000: logs[:] = logs[-500:]
    state._save()
