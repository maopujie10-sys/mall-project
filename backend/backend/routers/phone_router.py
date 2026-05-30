''"AI -- IVR////v1''"
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
    intent: str = ''
    resolved: bool = False
    note: str = ''

class CallAction(BaseModel):
    call_id: str
    action: str  # transfer/complete/note

@router.get("/status")
async def phone_status(_=Depends(verify_token)):
    ''''''
    return {"ok": True, "online": True, "lines": 3, "active_calls": 0, "today_calls": _today_count()}

@router.get("/logs")
async def call_logs(page: int = 1, limit: int = 20, _=Depends(verify_token)):
    ''''''
    logs = state._data.get("phone_logs", [])
    total = len(logs)
    start = (page-1)*limit
    return {"ok": True, "logs": logs[start:start+limit], "total": total, "page": page}

@router.get("/ivr/menu")
async def ivr_menu(_=Depends(verify_token)):
    ''"IVR''"
    return {"ok": True, "menu": _DEFAULT_MENU}

@router.post("/ivr/menu")
async def update_ivr(menu: dict, _=Depends(verify_token)):
    ''"IVR''"
    await handle_risk("L2", "IVR")
    state._data["phone_ivr_menu"] = menu
    state._save()
    return {"ok": True, "menu": menu}

@router.post("/simulate")
async def simulate_call(req: CallLog, _=Depends(verify_token)):
    ''"()''"
    await handle_risk("L1", '')
    call = {"id": f"CALL{datetime.now().strftime('%Y%m%d%H%M%S')}", "caller": req.caller,
            "time": datetime.now().isoformat(), "duration_sec": req.duration_sec or random.randint(30, 300),
            "intent": req.intent or _detect_intent(req.caller), "status": "completed",
            "resolved": req.resolved or random.random() > 0.3, "note": req.note or "AI"}
    logs = state._data.setdefault("phone_logs", [])
    logs.insert(0, call)
    if len(logs) > 500: logs[:] = logs[:500]
    state._save()
    return {"ok": True, "call": call, "transcript": _generate_transcript(call)}

@router.post("/transfer")
async def transfer_to_human(req: CallAction, _=Depends(verify_token)):
    ''''''
    await handle_risk("L2", f": {req.call_id}")
    return {"ok": True, "call_id": req.call_id, "transferred": True, "agent": "()", "estimated_wait": "30"}

@router.get("/stats")
async def phone_stats(_=Depends(verify_token)):
    ''''''
    logs = state._data.get("phone_logs", [])
    today = [l for l in logs if l.get("time",'').startswith(datetime.now().strftime("%Y-%m-%d"))]
    resolved = sum(1 for l in logs if l.get("resolved"))
    return {"ok": True, "stats": {"total_calls": len(logs), "today_calls": len(today),
            "resolution_rate": f"{round(resolved/max(len(logs),1)*100)}%", "avg_duration": "230",
            "auto_resolved": f"{round(resolved/max(len(logs),1)*100)}%", "transferred": sum(1 for l in logs if l.get("note",'')=='')}}

_DEFAULT_MENU = {"greeting": ",Friday AI!:",
    "options": [{"key":"1","label":'',"action":"product"},{"key":"2","label":'',"action":"order"},
               {"key":"3","label":'',"action":"after_sale"},{"key":"4","label":'',"action":"transfer"},
               {"key":"0","label":'',"action":"repeat"}],
    "voice": "()", "language": "zh-CN", "timeout_sec": 10, "max_retries": 3}

def _detect_intent(caller: str) -> str:
    intents = ['','','','','']
    return random.choice(intents)

def _generate_transcript(call: dict) -> list:
    return [{"role":"ai","text":f",Friday AI,?"},
            {"role":"user","text":f''},
            {"role":"ai","text":f",.?"},
            {"role":"user","text":","},
            {"role":"ai","text":",!"}]

def _today_count() -> int:
    today = datetime.now().strftime("%Y-%m-%d")
    return sum(1 for l in state._data.get("phone_logs",[]) if l.get("time",'').startswith(today))
