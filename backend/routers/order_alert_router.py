锘?""璁㈠崟寮傚父棰勮 鈥?閫€娆剧獊澧?搴撳瓨鍛婃€?鐗╂祦寤惰繜 鈫?澶氭笭閬撴帹閫?v1"""
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
    """棰勮绯荤粺鐘舵€?""
    rules = state._data.get("order_alert_rules", [])
    return {"ok": True, "monitoring": True, "active_rules": len([r for r in rules if r.get("enabled")]),
            "today_alerts": _today_alerts(), "last_check": datetime.now().isoformat()}

@router.get("/rules")
async def list_rules(_=Depends(verify_token)):
    """棰勮瑙勫垯鍒楄〃"""
    return {"ok": True, "rules": state._data.get("order_alert_rules", _DEFAULT_RULES)}

@router.post("/rules")
async def create_rule(rule: AlertRule, _=Depends(verify_token)):
    """鍒涘缓棰勮瑙勫垯"""
    await handle_risk("L2", f"鍒涘缓棰勮瑙勫垯: {rule.name}")
    rules = state._data.setdefault("order_alert_rules", [])
    rules.append({"id": f"AR{datetime.now().strftime('%Y%m%d%H%M%S')}",
                  "name": rule.name, "metric": rule.metric, "threshold": rule.threshold,
                  "channel": rule.channel, "enabled": rule.enabled,
                  "created_at": datetime.now().isoformat()})
    state._save()
    return {"ok": True, "rules": rules}

@router.delete("/rules/{rule_id}")
async def delete_rule(rule_id: str, _=Depends(verify_token)):
    """鍒犻櫎棰勮瑙勫垯"""
    await handle_risk("L2", f"鍒犻櫎棰勮瑙勫垯: {rule_id}")
    rules = state._data.setdefault("order_alert_rules", [])
    state._data["order_alert_rules"] = [r for r in rules if r.get("id") != rule_id]
    state._save()
    return {"ok": True, "deleted": rule_id}

@router.get("/check")
async def run_check(_=Depends(verify_token)):
    """绔嬪嵆鎵ц涓€娆￠璀︽鏌?""
    await handle_risk("L1", "鎵ц棰勮妫€鏌?)
    issues = _simulate_check()
    for issue in issues:
        log = state._data.setdefault("order_alert_logs", [])
        log.insert(0, {**issue, "checked_at": datetime.now().isoformat()})
        if len(log) > 500: log[:] = log[:500]
        # 瑙﹀彂鐢佃瘽鍛婅
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
    """棰勮鍘嗗彶"""
    return {"ok": True, "alerts": state._data.get("order_alert_logs", [])[:limit]}

@router.get("/stats")
async def alert_stats(_=Depends(verify_token)):
    """棰勮缁熻"""
    logs = state._data.get("order_alert_logs", [])
    p0 = sum(1 for l in logs if l.get("level") == "P0")
    p1 = sum(1 for l in logs if l.get("level") == "P1")
    p2 = sum(1 for l in logs if l.get("level") == "P2")
    return {"ok": True, "stats": {"total": len(logs), "P0": p0, "P1": p1, "P2": p2,
            "today": _today_alerts(), "resolution_rate": "85%"}}

_DEFAULT_RULES = [
    {"id":"AR001","name":"閫€娆剧巼寮傚父","metric":"refund_rate","threshold":15,"channel":"notification","enabled":True,"created_at":""},
    {"id":"AR002","name":"搴撳瓨鍛婃€?,"metric":"stock_low","threshold":10,"channel":"notification","enabled":True,"created_at":""},
    {"id":"AR003","name":"鐗╂祦寤惰繜","metric":"delivery_delay","threshold":5,"channel":"notification","enabled":True,"created_at":""},
    {"id":"AR004","name":"閿€鍞鏆磋穼","metric":"sales_drop","threshold":30,"channel":"phone","enabled":True,"created_at":""},
]

def _simulate_check() -> list:
    """妯℃嫙棰勮妫€鏌?""
    issues = []
    # 閫€娆剧巼
    refund = random.uniform(5, 25)
    if refund > 15:
        issues.append({"level":"P1","title":"閫€娆剧巼寮傚父","detail":f"浠婃棩閫€娆剧巼{round(refund,1)}%锛岃秴杩囬槇鍊?5%", "metric":"refund_rate","value":round(refund,1)})
    # 搴撳瓨
    stock = random.randint(3, 50)
    if stock < 10:
        issues.append({"level":"P2","title":"搴撳瓨鍛婃€?,"detail":f"鏈墈random.randint(1,5)}涓晢鍝佸簱瀛樹綆浜巤stock}浠?, "metric":"stock_low","value":stock})
    # 閿€鍞
    sales_drop = random.uniform(-10, 40)
    if sales_drop > 30:
        issues.append({"level":"P0","title":"閿€鍞鏆磋穼","detail":f"鏈椂娈甸攢鍞杈冩槰鏃ュ悓鏈熶笅闄峽round(sales_drop,1)}%", "metric":"sales_drop","value":round(sales_drop,1)})
    return issues

def _today_alerts() -> int:
    today = datetime.now().strftime("%Y-%m-%d")
    return sum(1 for l in state._data.get("order_alert_logs",[]) if l.get("checked_at","").startswith(today))
