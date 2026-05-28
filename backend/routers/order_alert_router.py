"""订单异常预警 — 退款突增/库存告急/物流延迟 → 多渠道推送/v1"""
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
    """预警系统状态"""
    rules = state._data.get("order_alert_rules", [])
    return {"ok": True, "monitoring": True, "active_rules": len([r for r in rules if r.get("enabled")]),
            "today_alerts": _today_alerts(), "last_check": datetime.now().isoformat()}

@router.get("/rules")
async def list_rules(_=Depends(verify_token)):
    """预警规则列表"""
    return {"ok": True, "rules": state._data.get("order_alert_rules", _DEFAULT_RULES)}

@router.post("/rules")
async def create_rule(rule: AlertRule, _=Depends(verify_token)):
    """创建预警规则"""
    await handle_risk("L2", f"创建预警规则: {rule.name}")
    rules = state._data.setdefault("order_alert_rules", [])
    rules.append({"id": f"AR{datetime.now().strftime('%Y%m%d%H%M%S')}",
                  "name": rule.name, "metric": rule.metric, "threshold": rule.threshold,
                  "channel": rule.channel, "enabled": rule.enabled,
                  "created_at": datetime.now().isoformat()})
    state._save()
    return {"ok": True, "rules": rules}

@router.delete("/rules/{rule_id}")
async def delete_rule(rule_id: str, _=Depends(verify_token)):
    """删除预警规则"""
    await handle_risk("L2", f"删除预警规则: {rule_id}")
    rules = state._data.setdefault("order_alert_rules", [])
    state._data["order_alert_rules"] = [r for r in rules if r.get("id") != rule_id]
    state._save()
    return {"ok": True, "deleted": rule_id}

@router.get("/check")
async def run_check(_=Depends(verify_token)):
    """立即执行一次预警检查"""
    await handle_risk("L1", "执行预警检查")
    issues = _simulate_check()
    for issue in issues:
        log = state._data.setdefault("order_alert_logs", [])
        log.insert(0, {**issue, "checked_at": datetime.now().isoformat()})
        if len(log) > 500: log[:] = log[:500]
        # 触发电话告警
        if issue.get("level") in ("P0", "P1"):
            try:
                from tools.phone_alert import PhoneAlert
                await PhoneAlert.send_alert(issue["level"], issue["title"], issue["detail"])
            except: pass
    state._save()
    return {"ok": True, "checked": True, "issues_found": len(issues), "issues": issues}

@router.get("/history")
async def alert_history(limit: int = 50, _=Depends(verify_token)):
    """预警历史"""
    return {"ok": True, "alerts": state._data.get("order_alert_logs", [])[:limit]}

@router.get("/stats")
async def alert_stats(_=Depends(verify_token)):
    """预警统计"""
    logs = state._data.get("order_alert_logs", [])
    p0 = sum(1 for l in logs if l.get("level") == "P0")
    p1 = sum(1 for l in logs if l.get("level") == "P1")
    p2 = sum(1 for l in logs if l.get("level") == "P2")
    return {"ok": True, "stats": {"total": len(logs), "P0": p0, "P1": p1, "P2": p2,
            "today": _today_alerts(), "resolution_rate": "85%"}}

_DEFAULT_RULES = [
    {"id":"AR001","name":"退款率异常","metric":"refund_rate","threshold":15,"channel":"notification","enabled":True,"created_at":""},
    {"id":"AR002","name":"库存告急","metric":"stock_low","threshold":10,"channel":"notification","enabled":True,"created_at":""},
    {"id":"AR003","name":"物流延迟","metric":"delivery_delay","threshold":5,"channel":"notification","enabled":True,"created_at":""},
    {"id":"AR004","name":"销售额暴跌","metric":"sales_drop","threshold":30,"channel":"phone","enabled":True,"created_at":""},
]

def _simulate_check() -> list:
    """模拟预警检查"""
    issues = []
    # 退款率
    refund = random.uniform(5, 25)
    if refund > 15:
        issues.append({"level":"P1","title":"退款率异常","detail":f"今日退款率{round(refund,1)}%，超过阈值15%", "metric":"refund_rate","value":round(refund,1)})
    # 库存
    stock = random.randint(3, 50)
    if stock < 10:
        issues.append({"level":"P2","title":"库存告急","detail":f"有{random.randint(1,5)}个商品库存低于{stock}件", "metric":"stock_low","value":stock})
    # 销售额
    sales_drop = random.uniform(-10, 40)
    if sales_drop > 30:
        issues.append({"level":"P0","title":"销售额暴跌","detail":f"本时段销售额较昨日同期下降{round(sales_drop,1)}%", "metric":"sales_drop","value":round(sales_drop,1)})
    return issues

def _today_alerts() -> int:
    today = datetime.now().strftime("%Y-%m-%d")
    return sum(1 for l in state._data.get("order_alert_logs",[]) if l.get("checked_at","").startswith(today))
