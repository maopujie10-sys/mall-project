""" -- IP////"""
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
    ''"(0-100)''"
    score = 100
    bl = _get_blacklist()
    fw = _get_firewall_rules()
    if len(bl) > 0: score -= 5
    if len(bl) > 10: score -= 5
    if state.mode != "ai_control": score -= 10
    if state._data.get("emergency_history"): score -= 5 * min(len(state._data["emergency_history"]), 4)
    # Token
    from config import AGENT_TOKEN
    if not AGENT_TOKEN or AGENT_TOKEN == "change-me-in-production": score -= 20
    # SSH
    if os.path.exists("/etc/ssh/sshd_config"):
        score -= 5  # SSH
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
    comment: str = ''

@router.get("/score")
async def security_score(_=Depends(verify_token)):
    ''''''
    await handle_risk("L1", '')
    return {"ok": True, "score": _calc_security_score(), "max": 100, "level": '' if _calc_security_score() > 80 else ('' if _calc_security_score() > 50 else '')}

@router.get("/blacklist")
async def list_blocked(_=Depends(verify_token)):
    ''"IP''"
    await handle_risk("L1", "IP")
    return {"blacklist": _get_blacklist(), "count": len(_get_blacklist())}

@router.post("/blacklist/block")
async def block_ip(req: BlockRequest, _=Depends(verify_token)):
    ''"IP(+iptables)''"
    await handle_risk("L3", f"IP: {req.ip}", need_confirm=True)
    expires = (datetime.now() + timedelta(hours=req.hours)).isoformat()
    _get_blacklist().append({"ip": req.ip, "reason": req.reason, "blocked_at": datetime.now().isoformat(), "expires_at": expires})
    state._save()
    # iptables 
    await execute(f"iptables -A INPUT -s {req.ip} -j DROP 2>/dev/null || echo 'iptables'')
    return {"ok": True, "ip": req.ip, "expires_at": expires}

@router.post("/blacklist/unblock")
async def unblock_ip(req: BlockRequest, _=Depends(verify_token)):
    ''"IP''"
    await handle_risk("L3", f"IP: {req.ip}", need_confirm=True)
    state._data["ip_blacklist"] = [e for e in _get_blacklist() if e["ip"] != req.ip]
    state._save()
    await execute(f"iptables -D INPUT -s {req.ip} -j DROP 2>/dev/null || echo 'iptables'')
    return {"ok": True, "ip": req.ip}

@router.get("/firewall")
async def list_firewall(_=Depends(verify_token)):
    ''''''
    await handle_risk("L1", '')
    result = await execute("iptables -L -n --line-numbers 2>/dev/null | head -50 || echo 'iptables'')
    return {"rules": _get_firewall_rules(), "iptables_output": result["stdout"][:2000]}

@router.post("/firewall/rule")
async def add_firewall_rule(rule: FirewallRule, _=Depends(verify_token)):
    ''''''
    await handle_risk("L3", f": {rule.port}/{rule.protocol}", need_confirm=True)
    action_flag = "-A" if rule.action == "allow" else "-A"
    target = "ACCEPT" if rule.action == "allow" else "DROP"
    cmd = f"iptables {action_flag} INPUT -p {rule.protocol} --dport {rule.port} -s {rule.source} -j {target}"
    result = await execute(cmd + " 2>/dev/null || echo 'iptables'')
    rule_entry = rule.model_dump()
    rule_entry["created_at"] = datetime.now().isoformat()
    _get_firewall_rules().append(rule_entry)
    state._save()
    return {"ok": True, "rule": rule_entry, "cmd_output": result["stdout"][:200]}

@router.get("/audit")
async def audit_logs(limit: int = 100, _=Depends(verify_token)):
    ''''''
    await handle_risk("L1", '')
    logs = get_audit_logs(limit)
    return {"ok": True, "logs": logs, "count": len(logs)}

@router.get("/rate-limit")
async def rate_limit_status(_=Depends(verify_token)):
    ''''''
    stats = get_rate_limit_stats()
    return {"ok": True, **stats}

@router.post("/token")
async def generate_token(req: JWTRequest, _=Depends(verify_token)):
    ''"JWT Token''"
    await handle_risk("L2", f"JWT: {req.subject}")
    token = create_jwt({"sub": req.subject}, req.expire_hours)
    return {"ok": True, "token": token, "expires_in_hours": req.expire_hours}

@router.get("/threats")
async def threat_detection(_=Depends(verify_token)):
    ''"(/)''"
    await handle_risk("L1", '')
    threats = []
    # SSH
    ssh_result = await execute("journalctl -u sshd -n 50 --no-pager 2>/dev/null | grep -c 'Failed password' || echo 0")
    failed_ssh = int(ssh_result["stdout"].strip() or 0)
    if failed_ssh > 10:
        threats.append({"type": "ssh_bruteforce", "severity": "high", "detail": f" {failed_ssh} SSH", "count": failed_ssh})
    # IP
    bl_count = len(_get_blacklist())
    if bl_count > 0:
        threats.append({"type": "blocked_ips", "severity": "low", "detail": f" {bl_count} IP", "count": bl_count})
    return {"ok": True, "threats": threats, "total": len(threats), "score": _calc_security_score()}
