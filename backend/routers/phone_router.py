锘?""AI鐢佃瘽鍔╃悊 鈥?璇煶IVR/鑷姩鎺ュ惉/涓嬪崟/杞汉宸?v1"""
from fastapi import APIRouter, Depends, HTTPException
from auth import verify_token
from risk import handle_risk
from state import state
from pydantic import BaseModel
from datetime import datetime
import random, json

router = APIRouter(prefix="/agent/phone", tags=["PhoneAssistant"])

class CallLog(BaseModel):
    caller: str
    duration_sec: int = 0
    intent: str = ""
    resolved: bool = False
    note: str = ""

class CallAction(BaseModel):
    call_id: str
    action: str  # transfer/complete/note

@router.get("/status")
async def phone_status(_=Depends(verify_token)):
    """鐢佃瘽绯荤粺鐘舵€?""
    return {"ok": True, "online": True, "lines": 3, "active_calls": 0, "today_calls": _today_count()}

@router.get("/logs")
async def call_logs(page: int = 1, limit: int = 20, _=Depends(verify_token)):
    """閫氳瘽璁板綍"""
    logs = state._data.get("phone_logs", [])
    total = len(logs)
    start = (page-1)*limit
    return {"ok": True, "logs": logs[start:start+limit], "total": total, "page": page}

@router.get("/ivr/menu")
async def ivr_menu(_=Depends(verify_token)):
    """IVR璇煶鑿滃崟閰嶇疆"""
    return {"ok": True, "menu": _DEFAULT_MENU}

@router.post("/ivr/menu")
async def update_ivr(menu: dict, _=Depends(verify_token)):
    """鏇存柊IVR鑿滃崟"""
    await handle_risk("L2", "淇敼IVR鑿滃崟")
    state._data["phone_ivr_menu"] = menu
    state._save()
    return {"ok": True, "menu": menu}

@router.post("/simulate")
async def simulate_call(req: CallLog, _=Depends(verify_token)):
    """妯℃嫙鏉ョ數锛堟紨绀虹敤锛?""
    await handle_risk("L1", "妯℃嫙鐢佃瘽")
    call = {"id": f"CALL{datetime.now().strftime('%Y%m%d%H%M%S')}", "caller": req.caller,
            "time": datetime.now().isoformat(), "duration_sec": req.duration_sec or random.randint(30, 300),
            "intent": req.intent or _detect_intent(req.caller), "status": "completed",
            "resolved": req.resolved or random.random() > 0.3, "note": req.note or "AI鑷姩澶勭悊"}
    logs = state._data.setdefault("phone_logs", [])
    logs.insert(0, call)
    if len(logs) > 500: logs[:] = logs[:500]
    state._save()
    return {"ok": True, "call": call, "transcript": _generate_transcript(call)}

@router.post("/transfer")
async def transfer_to_human(req: CallAction, _=Depends(verify_token)):
    """杞帴浜哄伐"""
    await handle_risk("L2", f"杞帴浜哄伐: {req.call_id}")
    return {"ok": True, "call_id": req.call_id, "transferred": True, "agent": "瀹㈡湇缁?鍦ㄧ嚎)", "estimated_wait": "30绉?}

@router.get("/stats")
async def phone_stats(_=Depends(verify_token)):
    """鐢佃瘽鏁版嵁缁熻"""
    logs = state._data.get("phone_logs", [])
    today = [l for l in logs if l.get("time","").startswith(datetime.now().strftime("%Y-%m-%d"))]
    resolved = sum(1 for l in logs if l.get("resolved"))
    return {"ok": True, "stats": {"total_calls": len(logs), "today_calls": len(today),
            "resolution_rate": f"{round(resolved/max(len(logs),1)*100)}%", "avg_duration": "2鍒?0绉?,
            "auto_resolved": f"{round(resolved/max(len(logs),1)*100)}%", "transferred": sum(1 for l in logs if l.get("note","")=="杞汉宸?)}}

_DEFAULT_MENU = {"greeting": "鎮ㄥソ锛屾杩庤嚧鐢礔riday AI鍟嗗煄锛佽閫夋嫨鏈嶅姟锛?,
    "options": [{"key":"1","label":"鍟嗗搧鍜ㄨ","action":"product"},{"key":"2","label":"璁㈠崟鏌ヨ","action":"order"},
               {"key":"3","label":"鍞悗鏈嶅姟","action":"after_sale"},{"key":"4","label":"杞汉宸ュ鏈?,"action":"transfer"},
               {"key":"0","label":"閲嶅鏀跺惉","action":"repeat"}],
    "voice": "鏅撴檽锛堜腑鏂囧コ澹帮級", "language": "zh-CN", "timeout_sec": 10, "max_retries": 3}

def _detect_intent(caller: str) -> str:
    intents = ["鍟嗗搧鍜ㄨ","璁㈠崟鏌ヨ","鍞悗鐢宠","鎶曡瘔寤鸿","鍚堜綔娲借皥"]
    return random.choice(intents)

def _generate_transcript(call: dict) -> list:
    return [{"role":"ai","text":f"鎮ㄥソ锛岃繖閲屾槸Friday AI鍟嗗煄锛屾湁浠€涔堝彲浠ュ府鎮紵"},
            {"role":"user","text":f"鎴戞兂鍜ㄨ涓€涓嬪晢鍝佷俊鎭?},
            {"role":"ai","text":f"濂界殑锛屽凡涓烘偍鏌ヨ鍒扮浉鍏冲晢鍝佷俊鎭€傝闂繕闇€瑕佸叾浠栧府鍔╁悧锛?},
            {"role":"user","text":"涓嶇敤浜嗭紝璋㈣阿"},
            {"role":"ai","text":"鎰熻阿鎮ㄧ殑鏉ョ數锛岀鎮ㄧ敓娲绘剦蹇紒"}]

def _today_count() -> int:
    today = datetime.now().strftime("%Y-%m-%d")
    return sum(1 for l in state._data.get("phone_logs",[]) if l.get("time","").startswith(today))
