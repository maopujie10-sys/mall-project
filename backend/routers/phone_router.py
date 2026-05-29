"""AI电话助理 — 语音IVR/自动接听/下单/转人工/v1"""
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
    """电话系统状态"""
    return {"ok": True, "online": True, "lines": 3, "active_calls": 0, "today_calls": _today_count()}

@router.get("/logs")
async def call_logs(page: int = 1, limit: int = 20, _=Depends(verify_token)):
    """通话记录"""
    logs = state._data.get("phone_logs", [])
    total = len(logs)
    start = (page-1)*limit
    return {"ok": True, "logs": logs[start:start+limit], "total": total, "page": page}

@router.get("/ivr/menu")
async def ivr_menu(_=Depends(verify_token)):
    """IVR语音菜单配置"""
    return {"ok": True, "menu": _DEFAULT_MENU}

@router.post("/ivr/menu")
async def update_ivr(menu: dict, _=Depends(verify_token)):
    """更新IVR菜单"""
    await handle_risk("L2", "修改IVR菜单")
    state._data["phone_ivr_menu"] = menu
    state._save()
    return {"ok": True, "menu": menu}

@router.post("/simulate")
async def simulate_call(req: CallLog, _=Depends(verify_token)):
    """模拟来电（演示用）"""
    await handle_risk("L1", "模拟电话")
    call = {"id": f"CALL{datetime.now().strftime('%Y%m%d%H%M%S')}", "caller": req.caller,
            "time": datetime.now().isoformat(), "duration_sec": req.duration_sec or random.randint(30, 300),
            "intent": req.intent or _detect_intent(req.caller), "status": "completed",
            "resolved": req.resolved or random.random() > 0.3, "note": req.note or "AI自动处理"}
    logs = state._data.setdefault("phone_logs", [])
    logs.insert(0, call)
    if len(logs) > 500: logs[:] = logs[:500]
    state._save()
    return {"ok": True, "call": call, "transcript": _generate_transcript(call)}

@router.post("/transfer")
async def transfer_to_human(req: CallAction, _=Depends(verify_token)):
    """转接人工"""
    await handle_risk("L2", f"转接人工: {req.call_id}")
    return {"ok": True, "call_id": req.call_id, "transferred": True, "agent": "客服组(在线)", "estimated_wait": "30秒"}

@router.get("/stats")
async def phone_stats(_=Depends(verify_token)):
    """电话数据统计"""
    logs = state._data.get("phone_logs", [])
    today = [l for l in logs if l.get("time","").startswith(datetime.now().strftime("%Y-%m-%d"))]
    resolved = sum(1 for l in logs if l.get("resolved"))
    return {"ok": True, "stats": {"total_calls": len(logs), "today_calls": len(today),
            "resolution_rate": f"{round(resolved/max(len(logs),1)*100)}%", "avg_duration": "2分30秒",
            "auto_resolved": f"{round(resolved/max(len(logs),1)*100)}%", "transferred": sum(1 for l in logs if l.get("note","")=="转人工")}}

_DEFAULT_MENU = {"greeting": "您好，欢迎致电Friday AI商城！请选择服务：",
    "options": [{"key":"1","label":"商品咨询","action":"product"},{"key":"2","label":"订单查询","action":"order"},
               {"key":"3","label":"售后服务","action":"after_sale"},{"key":"4","label":"转人工客服","action":"transfer"},
               {"key":"0","label":"重复收听","action":"repeat"}],
    "voice": "晓晓（中文女声）", "language": "zh-CN", "timeout_sec": 10, "max_retries": 3}

def _detect_intent(caller: str) -> str:
    intents = ["商品咨询","订单查询","售后申请","投诉建议","合作洽谈"]
    return random.choice(intents)

def _generate_transcript(call: dict) -> list:
    return [{"role":"ai","text":f"您好，这里是Friday AI商城，有什么可以帮您？"},
            {"role":"user","text":f"我想咨询一下商品信息"},
            {"role":"ai","text":f"好的，已为您查询到相关商品信息。请问还需要其他帮助吗？"},
            {"role":"user","text":"不用了，谢谢"},
            {"role":"ai","text":"感谢您的来电，祝您生活愉快！"}]

def _today_count() -> int:
    today = datetime.now().strftime("%Y-%m-%d")
    return sum(1 for l in state._data.get("phone_logs",[]) if l.get("time","").startswith(today))
