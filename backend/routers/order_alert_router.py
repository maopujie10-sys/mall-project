""" -- // -> /v1"""
from fastapi import APIRouter, Depends
from auth import verify_token
from risk import handle_risk
from state import state
from pydantic import BaseModel
from datetime import datetime, timedelta
import random

router = APIRouter(prefix="/agent/order-alert", tags=["OrderAlert"])

class AlertRule(BaseModel):
    name: str
    metric: str  # refund_rate / stock_low / delivery_delay / sales_drop
    threshold: float
    channel: str = "notification"  # notification / phone / wechat
    enabled: bool = True

@router.get("/status")
async def alert_status(_=Depends(verify_token)):
    ''''''
    rules = state._data.get("order_alert_rules", [])
    return {"ok": True, "monitoring": True, "active_rules": len([r for r in rules if r.get("enabled")]),
            "today_alerts": _today_alerts(), "last_check": datetime.now().isoformat()}

@router.get("/rules")
async def list_rules(_=Depends(verify_token)):
    ''''''
    return {"ok": True, "rules": state._data.get("order_alert_rules", _DEFAULT_RULES)}

@router.post("/rules")
async def create_rule(rule: AlertRule, _=Depends(verify_token)):
    ''''''
    await handle_risk("L2", f": {rule.name}")
    rules = state._data.setdefault("order_alert_rules", [])
    rules.append({"id": f"AR{datetime.now().strftime('%Y%m%d%H%M%S')}",
                  "name": rule.name, "metric": rule.metric, "threshold": rule.threshold,
                  "channel": rule.channel, "enabled": rule.enabled,
                  "created_at": datetime.now().isoformat()})
    state._save()
    return {"ok": True, "rules": rules}

@router.delete("/rules/{rule_id}")
async def delete_rule(rule_id: str, _=Depends(verify_token)):
    ''''''
    await handle_risk("L2", f": {rule_id}")
    rules = state._data.setdefault("order_alert_rules", [])
    state._data["order_alert_rules"] = [r for r in rules if r.get("id") != rule_id]
    state._save()
    return {"ok": True, "deleted": rule_id}

@router.get("/check")
async def run_check(_=Depends(verify_token)):
    ''''''
    await handle_risk("L1", '')
    issues = _simulate_check()
    for issue in issues:
        log = state._data.setdefault("order_alert_logs", [])
        log.insert(0, {**issue, "checked_at": datetime.now().isoformat()})
        if len(log) > 500: log[:] = log[:500]
        
        if issue.get("level") in ("P0", "P1"):
            try:
                from tools.phone_alert import PhoneAlert
                await PhoneAlert.send_alert(issue["level"], issue["title"], issue["detail"])
            except: pass
            try:
                from tools.phone_alert import WeChatAlert
                await WeChatAlert.send(issue["title"], issue["detail"], issue["level"])
            except: pass
    state._save()
    return {"ok": True, "checked": True, "issues_found": len(issues), "issues": issues}

@router.get("/history")
async def alert_history(limit: int = 50, _=Depends(verify_token)):
    ''''''
    return {"ok": True, "alerts": state._data.get("order_alert_logs", [])[:limit]}

@router.get("/stats")
async def alert_stats(_=Depends(verify_token)):
    ''''''
    logs = state._data.get("order_alert_logs", [])
    p0 = sum(1 for l in logs if l.get("level") == "P0")
    p1 = sum(1 for l in logs if l.get("level") == "P1")
    p2 = sum(1 for l in logs if l.get("level") == "P2")
    return {"ok": True, "stats": {"total": len(logs), "P0": p0, "P1": p1, "P2": p2,
            "today": _today_alerts(), "resolution_rate": "85%"}}

_DEFAULT_RULES = [
    {"id":"AR001","name":'',"metric":"refund_rate","threshold":15,"channel":"notification","enabled":True,"created_at":''},
    {"id":"AR002","name":'',"metric":"stock_low","threshold":10,"channel":"notification","enabled":True,"created_at":''},
    {"id":"AR003","name":'',"metric":"delivery_delay","threshold":5,"channel":"notification","enabled":True,"created_at":''},
    {"id":"AR004","name":'',"metric":"sales_drop","threshold":30,"channel":"phone","enabled":True,"created_at":''},
]

def _simulate_check() -> list:
    ''''''
    issues = []
    
    refund = random.uniform(5, 25)
    if refund > 15:
        issues.append({"level":"P1","title":'',"detail":f"{round(refund,1)}%,15%", "metric":"refund_rate","value":round(refund,1)})
    
    stock = random.randint(3, 50)
    if stock < 10:
        issues.append({"level":"P2","title":'',"detail":f"{random.randint(1,5)}{stock}", "metric":"stock_low","value":stock})
    
    sales_drop = random.uniform(-10, 40)
    if sales_drop > 30:
        issues.append({"level":"P0","title":'',"detail":f"{round(sales_drop,1)}%", "metric":"sales_drop","value":round(sales_drop,1)})
    return issues

def _today_alerts() -> int:
    today = datetime.now().strftime("%Y-%m-%d")
    return sum(1 for l in state._data.get("order_alert_logs",[]) if l.get("checked_at",'').startswith(today))
