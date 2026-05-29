锘?""AI瀹㈡湇鑷姩鍥炲 鈥?瑙勫垯寮曟搸/甯歌闂/杞汉宸?v1"""
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
    user_id: str = ""

@router.post("/reply")
async def auto_reply(req: AutoReplyRequest, _=Depends(verify_token)):
    """AI鑷姩鍥炲娑堟伅"""
    await handle_risk("L1", "AI瀹㈡湇鍥炲")
    rules = state._data.get("auto_reply_rules", [])
    msg_lower = req.message.lower()
    # 瑙勫垯鍖归厤
    for rule in sorted(rules, key=lambda r: -r.get("priority", 0)):
        if rule.get("keyword","").lower() in msg_lower:
            reply = rule["reply"]
            _log_conversation(req.message, reply, "rule")
            return {"ok": True, "reply": reply, "matched": True, "method": "rule",
                    "confidence": "high", "transfer": False}
    # AI鑷姩鍥炲锛堟棤瑙勫垯鍖归厤鏃讹級
    from agents.multi_model import ModelRouter, ModelMode
    try:
        config = ModelRouter.route(ModelMode.BALANCE)
        import httpx
        async with httpx.AsyncClient(timeout=15) as c:
            resp = await c.post(f"{config.base_url}/chat/completions",
                headers={"Authorization": f"Bearer {config.api_key}"},
                json={"model": config.model_name, "messages": [
                    {"role":"system","content":"浣犳槸Friday AI鍟嗗煄鐨勬櫤鑳藉鏈嶃€傝鐢ㄤ腑鏂囧弸濂藉洖澶嶅鎴峰挩璇€傚鏋滃鎴烽棶鐨勬槸閫€娆俱€侀€€璐с€佹姇璇夌瓑闇€瑕佷汉宸ュ鐞嗙殑闂锛屽湪鍥炲缁撳熬鍔?[杞汉宸銆?},
                    {"role":"user","content": req.message}], "max_tokens": 300})
            data = resp.json()
            reply = data.get("choices",[{}])[0].get("message",{}).get("content","")
            need_transfer = "[杞汉宸" in reply
            if need_transfer: reply = reply.replace("[杞汉宸","").strip()
            _log_conversation(req.message, reply, "ai")
            return {"ok": True, "reply": reply, "matched": True, "method": "ai",
                    "confidence": "medium", "transfer": need_transfer}
    except Exception as e:
        fallback = f"鎰熻阿鎮ㄧ殑鍜ㄨ锛屾垜姝ｅ湪鏌ヨ鐩稿叧淇℃伅锛岃绋嶅€欍€傚鎬ラ渶甯姪璇疯仈绯讳汉宸ュ鏈嶃€?
        _log_conversation(req.message, fallback, "fallback")
        return {"ok": True, "reply": fallback, "matched": False, "method": "fallback", "transfer": True}

@router.get("/rules")
async def list_rules(_=Depends(verify_token)):
    """鏌ョ湅鎵€鏈夎嚜鍔ㄥ洖澶嶈鍒?""
    return {"ok": True, "rules": state._data.get("auto_reply_rules", [])}

@router.post("/rules")
async def create_rule(rule: RuleCreate, _=Depends(verify_token)):
    """鍒涘缓鑷姩鍥炲瑙勫垯"""
    await handle_risk("L2", f"鍒涘缓鑷姩鍥炲瑙勫垯: {rule.keyword}")
    rules = state._data.setdefault("auto_reply_rules", [])
    rules.append({"id": f"R{datetime.now().strftime('%Y%m%d%H%M%S')}",
                  "keyword": rule.keyword, "reply": rule.reply,
                  "category": rule.category, "priority": rule.priority,
                  "created_at": datetime.now().isoformat(), "enabled": True})
    state._save()
    return {"ok": True, "rules": rules}

@router.delete("/rules/{rule_id}")
async def delete_rule(rule_id: str, _=Depends(verify_token)):
    """鍒犻櫎鑷姩鍥炲瑙勫垯"""
    await handle_risk("L2", f"鍒犻櫎鑷姩鍥炲瑙勫垯: {rule_id}")
    rules = state._data.setdefault("auto_reply_rules", [])
    state._data["auto_reply_rules"] = [r for r in rules if r.get("id") != rule_id]
    state._save()
    return {"ok": True, "deleted": rule_id}

@router.get("/conversations")
async def recent_conversations(limit: int = 20, _=Depends(verify_token)):
    """鏈€杩戝璇濊褰?""
    return {"ok": True, "conversations": state._data.get("auto_reply_logs", [])[-limit:]}

@router.get("/stats")
async def auto_reply_stats(_=Depends(verify_token)):
    """鑷姩鍥炲缁熻"""
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
