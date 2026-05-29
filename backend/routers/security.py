"""安全中心 — IP封禁/防火墙/安全评分/威胁检测/安全审计"""
import json, os
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from auth import verify_token, get_audit_logs, get_rate_limit_stats, create_jwt
from state import state
from risk import handle_risk
from executor import execute

router = APIRouter(prefix="/agent/security", tags=["Security"])

def _get_blacklist():
    return state._data.setdefault("ip_blacklist", [])

def _get_firewall_rules():
    return state._data.setdefault("firewall_rules", [])

def _calc_security_score():
    """计算安全评分（0-100）"""
    score = 100
    bl = _get_blacklist()
    fw = _get_firewall_rules()
    if len(bl) > 0: score -= 5
    if len(bl) > 10: score -= 5
    if state.mode != "ai_control": score -= 10
    if state._data.get("emergency_history"): score -= 5 * min(len(state._data["emergency_history"]), 4)
    # Token检查
    from config import AGENT_TOKEN
    if not AGENT_TOKEN or AGENT_TOKEN == "change-me-in-production": score -= 20
    # SSH配置
    if os.path.exists("/etc/ssh/sshd_config"):
        score -= 5  # 有SSH就有风险
    return max(0, min(100, score))

class BlockRequest(BaseModel):
    ip: str
    reason: str = "manual"
    hours: int = 24

class JWTRequest(BaseModel):
    subject: str = "agent"
    expire_hours: int = 24

class FirewallRule(BaseModel):
    port: int
    protocol: str = "tcp"
    action: str = "allow"
    source: str = "0.0.0.0/0"
    comment: str = ""

@router.get("/score")
async def security_score(_=Depends(verify_token)):
    """安全评分"""
    await handle_risk("L1", "安全评分")
    return {"ok": True, "score": _calc_security_score(), "max": 100, "level": "安全" if _calc_security_score() > 80 else ("需关注" if _calc_security_score() > 50 else "危险")}

@router.get("/blacklist")
async def list_blocked(_=Depends(verify_token)):
    """IP黑名单列表"""
    await handle_risk("L1", "查看IP黑名单")
    return {"blacklist": _get_blacklist(), "count": len(_get_blacklist())}

@router.post("/blacklist/block")
async def block_ip(req: BlockRequest, _=Depends(verify_token)):
    """封禁IP（内存+iptables）"""
    await handle_risk("L3", f"封禁IP: {req.ip}", need_confirm=True)
    expires = (datetime.now() + timedelta(hours=req.hours)).isoformat()
    _get_blacklist().append({"ip": req.ip, "reason": req.reason, "blocked_at": datetime.now().isoformat(), "expires_at": expires})
    state._save()
    # iptables 持久化
    await execute(f"iptables -A INPUT -s {req.ip} -j DROP 2>/dev/null || echo 'iptables不可用'")
    return {"ok": True, "ip": req.ip, "expires_at": expires}

@router.post("/blacklist/unblock")
async def unblock_ip(req: BlockRequest, _=Depends(verify_token)):
    """解封IP"""
    await handle_risk("L3", f"解封IP: {req.ip}", need_confirm=True)
    state._data["ip_blacklist"] = [e for e in _get_blacklist() if e["ip"] != req.ip]
    state._save()
    await execute(f"iptables -D INPUT -s {req.ip} -j DROP 2>/dev/null || echo 'iptables不可用'")
    return {"ok": True, "ip": req.ip}

@router.get("/firewall")
async def list_firewall(_=Depends(verify_token)):
    """查看防火墙规则"""
    await handle_risk("L1", "查看防火墙")
    result = await execute("iptables -L -n --line-numbers 2>/dev/null | head -50 || echo 'iptables不可用'")
    return {"rules": _get_firewall_rules(), "iptables_output": result["stdout"][:2000]}

@router.post("/firewall/rule")
async def add_firewall_rule(rule: FirewallRule, _=Depends(verify_token)):
    """添加防火墙规则"""
    await handle_risk("L3", f"添加防火墙规则: {rule.port}/{rule.protocol}", need_confirm=True)
    action_flag = "-A" if rule.action == "allow" else "-A"
    target = "ACCEPT" if rule.action == "allow" else "DROP"
    cmd = f"iptables {action_flag} INPUT -p {rule.protocol} --dport {rule.port} -s {rule.source} -j {target}"
    result = await execute(cmd + " 2>/dev/null || echo 'iptables不可用'")
    rule_entry = rule.model_dump()
    rule_entry["created_at"] = datetime.now().isoformat()
    _get_firewall_rules().append(rule_entry)
    state._save()
    return {"ok": True, "rule": rule_entry, "cmd_output": result["stdout"][:200]}

@router.get("/audit")
async def audit_logs(limit: int = 100, _=Depends(verify_token)):
    """审计日志"""
    await handle_risk("L1", "查看审计日志")
    logs = get_audit_logs(limit)
    return {"ok": True, "logs": logs, "count": len(logs)}

@router.get("/rate-limit")
async def rate_limit_status(_=Depends(verify_token)):
    """速率限制"""
    stats = get_rate_limit_stats()
    return {"ok": True, **stats}

@router.post("/token")
async def generate_token(req: JWTRequest, _=Depends(verify_token)):
    """生成JWT Token"""
    await handle_risk("L2", f"生成JWT: {req.subject}")
    token = create_jwt({"sub": req.subject}, req.expire_hours)
    return {"ok": True, "token": token, "expires_in_hours": req.expire_hours}

@router.get("/threats")
async def threat_detection(_=Depends(verify_token)):
    """威胁检测（检查异常登录/端口扫描等）"""
    await handle_risk("L1", "威胁检测")
    threats = []
    # 检测SSH暴力破解
    ssh_result = await execute("journalctl -u sshd -n 50 --no-pager 2>/dev/null | grep -c 'Failed password' || echo 0")
    failed_ssh = int(ssh_result["stdout"].strip() or 0)
    if failed_ssh > 10:
        threats.append({"type": "ssh_bruteforce", "severity": "high", "detail": f"最近 {failed_ssh} 次SSH登录失败", "count": failed_ssh})
    # 检测黑名单IP数
    bl_count = len(_get_blacklist())
    if bl_count > 0:
        threats.append({"type": "blocked_ips", "severity": "low", "detail": f"已封禁 {bl_count} 个IP", "count": bl_count})
    return {"ok": True, "threats": threats, "total": len(threats), "score": _calc_security_score()}
