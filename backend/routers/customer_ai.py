锘?""AI鏅鸿兘瀹㈡湇2.0 鈥?澶氳疆瀵硅瘽+鐭ヨ瘑搴揜AG+鎰忓浘璇嗗埆+鏅鸿兘杞汉宸?宸ュ崟鍒涘缓"""
import json, re, os
from datetime import datetime
from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from auth import verify_token
from state import state
from risk import handle_risk
from tools.vector_memory import VectorMemory

router = APIRouter(prefix="/agent/customer", tags=["CustomerAI"])

# ===== 鐭ヨ瘑搴?=====
FAQ_KNOWLEDGE = {
    "閫€璐?: "閫€璐ф斂绛栵細鏀跺埌鍟嗗搧7澶╁唴鍙敵璇烽€€璐с€傚晢鍝侀渶淇濇寔鍘熷寘瑁呫€佹湭浣跨敤銆傝鍒?鎴戠殑璁㈠崟'椤甸潰鐢宠閫€璐э紝瀹㈡湇浼氬湪24灏忔椂鍐呭鏍搞€傞€€璐у湴鍧€灏嗕互绔欏唴淇″舰寮忓彂閫併€?,
    "閫€娆?: "閫€娆炬椂鏁堬細閫€璐у鏍搁€氳繃鍚庯紝閫€娆惧皢鍦?-7涓伐浣滄棩鍐呭師璺繑鍥炪€傛敮浠樺疂/寰俊1-3澶╋紝閾惰鍗?-7澶╋紝淇＄敤鍗?-15澶┿€?,
    "鍙戣揣": "鍙戣揣鏃舵晥锛氱幇璐у晢鍝佷笅鍗曞悗24-48灏忔椂鍐呭彂璐с€傞鍞晢鍝佹寜椤甸潰鏍囨敞鏃堕棿鍙戣揣銆傛捣澶栫洿閭晢鍝?-5涓伐浣滄棩鍙戣揣銆?,
    "鐗╂祦": "鐗╂祦鏌ヨ锛氳鍒?鎴戠殑璁㈠崟'鐐瑰嚮'鏌ョ湅鐗╂祦'銆傚浗闄呯墿娴侀€氬父7-15澶╋紝鍥藉唴鐗╂祦3-5澶┿€傚瓒呰繃棰勮鏃堕棿鏈敹鍒帮紝璇疯仈绯诲鏈嶃€?,
    "鎹㈣揣": "鎹㈣揣鏀跨瓥锛氭敮鎸佸悓娆炬崲鑹?鎹㈢爜銆傝鍦?鎴戠殑璁㈠崟'閫夋嫨'鐢宠鎹㈣揣'銆傛崲璐ц繍璐圭敱骞冲彴鎵挎媴锛堣川閲忛棶棰橈級鎴栫敤鎴锋壙鎷咃紙涓汉鍘熷洜锛夈€?,
    "鏀粯": "鏀寔鏀粯鏂瑰紡锛氭敮浠樺疂銆佸井淇℃敮浠樸€侀摱琛屽崱銆丅inance Pay銆丠uobi Pay銆丱KX Wallet銆傚鏀粯澶辫触璇锋鏌ラ摱琛屽崱闄愰鎴栧垏鎹㈡敮浠樻柟寮忋€?,
    "浼樻儬鍒?: "浼樻儬鍒镐娇鐢細鍦ㄧ粨绠楅〉闈㈤€夋嫨鍙敤浼樻儬鍒搞€傛弧鍑忓埜闇€杈惧埌鏈€浣庢秷璐归噾棰濄€備紭鎯犲埜涓嶅彲鍙犲姞浣跨敤锛屾瘡绗旇鍗曢檺鐢ㄤ竴寮犮€?,
    "浼氬憳": "浼氬憳绛夌骇锛氭櫘閫?閾跺崱/閲戝崱/閽荤煶銆傚崌绾т緷鎹负绱娑堣垂閲戦銆傞噾鍗″強浠ヤ笂浜笓灞炲鏈嶃€佷紭鍏堝彂璐с€佺敓鏃ョぜ鍖呫€?,
    "鎶曡瘔": "鎶曡瘔澶勭悊锛氳鎻忚堪鎮ㄧ殑闂锛屾垜浠細鍗囩骇缁欓珮绾у鏈嶅鐞嗐€備竴鑸?灏忔椂鍐呭搷搴旓紝24灏忔椂鍐呯粰鍑鸿В鍐虫柟妗堛€傚涓嶆弧鎰忓彲鐢宠骞冲彴浠嬪叆銆?,
    "鑱旂郴": "瀹㈡湇宸ヤ綔鏃堕棿锛氬懆涓€鑷冲懆鏃?9:00-22:00銆傚湪绾垮鏈嶅嵆鏃跺洖澶嶏紝鐢佃瘽瀹㈡湇锛?00-xxx-xxxx銆傝嫳鏂囧鏈嶏細support@tiktook.eu.cc銆?,
}

# 鎰忓浘->鐭ヨ瘑搴撴槧灏?INTENT_MAP = {
    "閫€璐?: ["閫€璐?, "閫€", "return", "refund", "閫€娆?],
    "閫€娆?: ["閫€娆?, "refund", "閫€閽?, "鍒拌处"],
    "鍙戣揣": ["鍙戣揣", "ship", "閫佽揣", "澶氫箙", "浠€涔堟椂鍊?],
    "鐗╂祦": ["鐗╂祦", "蹇€?, "track", "鍒板摢", "鏌ヨ"],
    "鎹㈣揣": ["鎹㈣揣", "鎹?, "exchange", "灏虹爜", "棰滆壊"],
    "鏀粯": ["鏀粯", "pay", "浠樻", "鎵ｆ", "澶辫触"],
    "浼樻儬鍒?: ["浼樻儬鍒?, "coupon", "鎶樻墸", "婊″噺"],
    "浼氬憳": ["浼氬憳", "vip", "绛夌骇", "鏉冪泭"],
    "鎶曡瘔": ["鎶曡瘔", "complain", "涓嶆弧", "涓炬姤"],
    "鑱旂郴": ["瀹㈡湇", "浜哄伐", "鐢佃瘽", "閭", "鑱旂郴"],
}

# 杞汉宸ヨЕ鍙戣瘝
ESCALATE_KEYWORDS = ["浜哄伐", "杞汉宸?, "浜哄伐瀹㈡湇", "鎶曡瘔", "鎵句綘浠瀵?, "鐢佃瘽", "鎵撶數璇?, "鍗囩骇"]

class CustomerChatRequest(BaseModel):
    message: str
    session_id: str = ""
    user_name: str = ""

def _match_intent(message: str) -> str:
    """鍖归厤鐢ㄦ埛鎰忓浘"""
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
    """鍒ゆ柇鏄惁闇€瑕佽浆浜哄伐"""
    msg_lower = message.lower()
    if any(kw in msg_lower for kw in ESCALATE_KEYWORDS):
        return True
    if history_count > 5:  # 瀵硅瘽瓒呰繃5杞嚜鍔ㄨ浆浜哄伐
        return True
    return False

def _get_knowledge(intent: str, message: str) -> str:
    """鑾峰彇鐩稿叧鐭ヨ瘑"""
    if intent in FAQ_KNOWLEDGE:
        return FAQ_KNOWLEDGE[intent]
    # 閫氱敤鎰忓浘锛氬尮閰嶆墍鏈塅AQ
    msg_lower = message.lower()
    matches = []
    for topic, answer in FAQ_KNOWLEDGE.items():
        if any(kw in msg_lower for kw in INTENT_MAP.get(topic, [])):
            matches.append(answer)
    return "\n\n".join(matches[:2]) if matches else ""

async def _get_rag_context(message: str) -> str:
    """浠庡悜閲忚蹇嗚幏鍙栫浉鍏冲巻鍙插璇?""
    try:
        results = await VectorMemory.search(message, top_k=3)
        if results:
            return "鍘嗗彶鐩稿叧瀵硅瘽:\n" + "\n".join([r.get("text", "")[:200] for r in results])
    except Exception:
        pass
    return ""

# ===== 瀵硅瘽寮曟搸 =====
@router.post("/chat")
async def customer_chat(req: CustomerChatRequest, _=Depends(verify_token)):
    """AI瀹㈡湇瀵硅瘽 鈥?澶氳疆+鐭ヨ瘑搴?鎰忓浘+鏅鸿兘杞汉宸?""
    message = req.message.strip()
    if not message:
        return {"reply": "鎮ㄥソ锛岃闂湁浠€涔堝彲浠ュ府鎮ㄧ殑锛?, "intent": "greeting"}

    # 浼氳瘽绠＄悊
    session_id = req.session_id or f"cs_{datetime.now().strftime('%Y%m%d%H%M%S')}"
    sessions = state._data.setdefault("customer_sessions", {})
    session = sessions.setdefault(session_id, {"messages": [], "intent": "", "escalated": False})
    session["messages"].append({"role": "user", "content": message, "time": datetime.now().isoformat()})
    
    # 鎰忓浘璇嗗埆
    intent = _match_intent(message)
    session["intent"] = intent
    
    # 杞汉宸ュ垽鏂?    if _should_escalate(message, len(session["messages"])):
        if not session["escalated"]:
            session["escalated"] = True
            # 鍒涘缓宸ュ崟
            tickets = state._data.setdefault("customer_tickets", [])
            ticket = {
                "id": f"TK{len(tickets)+1:04d}",
                "session": session_id,
                "user": req.user_name or "鍖垮悕鐢ㄦ埛",
                "intent": intent,
                "last_message": message[:200],
                "created_at": datetime.now().isoformat(),
                "status": "pending",
                "priority": "P2",
            }
            tickets.insert(0, ticket)
            state._save()
            reply = f"鎴戝凡灏嗘偍鐨勯棶棰樺崌绾х粰浜哄伐瀹㈡湇锛屽伐鍗曞彿 {ticket['id']}銆俓n\n鎮ㄥ彲浠ョ户缁弿杩伴棶棰橈紝鎴栫瓑寰呭鏈嶄富鍔ㄨ仈绯绘偍銆傚伐浣滄椂闂?:00-22:00锛岄€氬父2灏忔椂鍐呭洖澶嶃€?
        else:
            reply = f"鎮ㄧ殑宸ュ崟宸叉彁浜わ紝浜哄伐瀹㈡湇浼氬敖蹇洖澶嶃€傚闇€绱ф€ュ鐞嗭紝璇锋嫧鎵撳鏈嶇數璇濄€?
    else:
        # 鐭ヨ瘑搴撳洖澶?        kb = _get_knowledge(intent, message)
        
        # RAG涓婁笅鏂?        rag_ctx = await _get_rag_context(message)
        
        if kb:
            # 鏍规嵁鎰忓浘鍜屽璇濊疆娆＄敓鎴愯嚜鐒跺洖澶?            greetings = {
                1: f"鎮ㄥソ锛佸叧浜巤intent}鐨勯棶棰橈紝鎴戞潵涓烘偍瑙ｇ瓟锛歕n\n{kb}\n\n杩樻湁鍏朵粬闂鍚楋紵",
                2: f"琛ュ厖璇存槑锛歕n\n{kb}\n\n闇€瑕佽繘涓€姝ュ府鍔╁悧锛?,
            }
            turn = len([m for m in session["messages"] if m["role"] == "user"])
            reply = greetings.get(turn, kb)
        else:
            # 閫氱敤鍥炲
            reply = f"鎮ㄥソ锛佹垜鏄疉I瀹㈡湇锛屽彲浠ュ府鎮ㄨВ绛斾互涓嬮棶棰橈細\n\n鈥?閫€璐?閫€娆炬斂绛朶n鈥?鍙戣揣/鐗╂祦鏌ヨ\n鈥?鏀粯/鎹㈣揣\n鈥?浼樻儬鍒?浼氬憳\n鈥?鎶曡瘔/浜哄伐瀹㈡湇\n\n璇峰憡璇夋垜鎮ㄩ亣鍒颁簡浠€涔堥棶棰橈紵"

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

# ===== 宸ュ崟绠＄悊 =====
@router.get("/tickets")
async def list_tickets(status: str = Query(""), _=Depends(verify_token)):
    """瀹㈡湇宸ュ崟鍒楄〃"""
    tickets = state._data.get("customer_tickets", [])
    if status:
        tickets = [t for t in tickets if t.get("status") == status]
    return {"ok": True, "total": len(tickets), "tickets": tickets[-50:]}

@router.post("/tickets/{ticket_id}/resolve")
async def resolve_ticket(ticket_id: str, resolution: str = Query(""), _=Depends(verify_token)):
    """瑙ｅ喅宸ュ崟"""
    tickets = state._data.get("customer_tickets", [])
    for t in tickets:
        if t["id"] == ticket_id:
            t["status"] = "resolved"
            t["resolution"] = resolution
            t["resolved_at"] = datetime.now().isoformat()
            state._save()
            return {"ok": True, "ticket": ticket_id}
    return {"ok": False, "error": "宸ュ崟涓嶅瓨鍦?}

@router.get("/stats")
async def customer_stats(_=Depends(verify_token)):
    """瀹㈡湇缁熻鏁版嵁"""
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
        "avg_resolution_time": "2灏忔椂",  # 鍙悗缁簿纭绠?    }

# ===== 鐭ヨ瘑搴撶鐞?=====
@router.get("/faq")
async def list_faq(_=Depends(verify_token)):
    """FAQ鐭ヨ瘑搴?""
    return {"ok": True, "faq": [{"topic": k, "answer": v} for k, v in FAQ_KNOWLEDGE.items()]}

@router.post("/faq")
async def update_faq(topic: str = Query(...), answer: str = Query(...), _=Depends(verify_token)):
    """鏇存柊FAQ"""
    FAQ_KNOWLEDGE[topic] = answer
    return {"ok": True, "topic": topic}
