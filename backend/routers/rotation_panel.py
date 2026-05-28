"""域名轮值管理 — 真正的健康检测/自动切换/权重轮值"""
import asyncio
import ssl as ssl_mod
import socket
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from auth import verify_token
from state import state
from risk import handle_risk

router = APIRouter(prefix="/rotation", tags=["Rotation"])

DEFAULT_DOMAINS = [
    {"domain": "tiktook.eu.cc", "active": True, "health": "ok", "type": "主域名", "weight": 5},
    {"domain": "tiktokmall.shop", "active": True, "health": "ok", "type": "轮值", "weight": 3},
    {"domain": "tiktokmall.store", "active": True, "health": "ok", "type": "轮值", "weight": 3},
    {"domain": "tiktokmall.online", "active": True, "health": "ok", "type": "轮值", "weight": 3},
    {"domain": "tiktokmall.live", "active": True, "health": "ok", "type": "轮值", "weight": 3},
    {"domain": "tiktokmall.xyz", "active": True, "health": "ok", "type": "轮值", "weight": 2},
    {"domain": "tiktokmall.top", "active": True, "health": "ok", "type": "轮值", "weight": 2},
    {"domain": "img.tiktook.eu.cc", "active": True, "health": "ok", "type": "CDN图片", "weight": 1},
]


def _get_domains():
    if "rotation_domains" not in state._data:
        state._data["rotation_domains"] = [dict(d) for d in DEFAULT_DOMAINS]
        state._save()
    return state._data["rotation_domains"]


async def _check_one(d: dict) -> dict:
    """检测单个域名，返回带实时指标的结果"""
    import httpx
    domain = d["domain"]
    url = f"https://{domain}"
    result = {
        "domain": domain,
        "ok": False,
        "status_code": 0,
        "latency_ms": 0,
        "redirect_to": "",
        "redirect_chain": [],
        "ip": "",
        "error": "",
    }
    # DNS 解析
    try:
        ips = await asyncio.get_event_loop().run_in_executor(None, lambda: socket.getaddrinfo(domain, 443, socket.AF_INET))
        if ips:
            result["ip"] = ips[0][4][0]
    except Exception:
        pass
    # HTTP 检测
    try:
        start = datetime.now()
        async with httpx.AsyncClient(timeout=10, follow_redirects=True, verify=False) as c:
            r = await c.get(url, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"})
            elapsed = (datetime.now() - start).total_seconds() * 1000
            result["latency_ms"] = round(elapsed, 1)
            result["status_code"] = r.status_code
            result["ok"] = r.status_code < 400
            if r.history:
                result["redirect_chain"] = [str(h.url) for h in r.history]
                result["redirect_to"] = str(r.url)
    except Exception as e:
        result["error"] = str(e)[:100]
        result["ok"] = False
    return result


async def _check_ssl(domain: str) -> dict:
    """检查 SSL 证书有效期"""
    try:
        ctx = ssl_mod.create_default_context()
        with socket.create_connection((domain, 443), timeout=5) as sock:
            with ctx.wrap_socket(sock, server_hostname=domain) as ssock:
                cert = ssock.getpeercert()
                if cert and "notAfter" in cert:
                    expiry = datetime.strptime(cert["notAfter"], "%b %d %H:%M:%S %Y %Z")
                    now = datetime.now()
                    days_left = (expiry - now).days
                    return {
                        "expiry": expiry.strftime("%Y-%m-%d"),
                        "days_left": days_left,
                        "issuer": dict(cert.get("issuer", [])).get("organizationName", ""),
                        "ok": days_left > 30,
                    }
    except Exception:
        pass
    return {"expiry": "", "days_left": 0, "issuer": "", "ok": False}


async def _enrich_domain(d: dict) -> dict:
    """给域名补充实时检测数据"""
    check = await _check_one(d)
    ssl_info = await _check_ssl(d["domain"])
    enriched = dict(d)
    enriched.update({
        "ip": check.get("ip", ""),
        "latency": check.get("latency_ms", 0),
        "status_code": check.get("status_code", 0),
        "redirect_to": check.get("redirect_to", ""),
        "redirect_chain": check.get("redirect_chain", []),
        "ssl_expiry": ssl_info.get("expiry", ""),
        "ssl_days": ssl_info.get("days_left", 0),
        "ssl_issuer": ssl_info.get("issuer", ""),
    })
    if check.get("ok"):
        enriched["health"] = "ok"
    elif check.get("error"):
        enriched["health"] = "error"
        enriched["error"] = check["error"]
    else:
        enriched["health"] = "warning"
    return enriched


async def _check_all():
    """给调度器用的全量检测（无需鉴权），同时执行自动轮值"""
    print(f"[Rotation] 开始全量域名检测 {datetime.now().strftime('%H:%M:%S')}")
    domains = _get_domains()
    changed = False
    for d in domains:
        if not d.get("active"):
            continue
        check = await _check_one(d)
        old_health = d.get("health", "ok")
        if check.get("ok"):
            d["health"] = "ok"
        else:
            d["health"] = "error"
            d["last_error"] = check.get("error", "")
        d["latency"] = check.get("latency_ms", 0)
        d["ip"] = check.get("ip", "")
        d["status_code"] = check.get("status_code", 0)
        d["last_check"] = datetime.now().isoformat()
        ssl_info = await _check_ssl(d["domain"])
        d["ssl_expiry"] = ssl_info.get("expiry", "")
        d["ssl_days"] = ssl_info.get("days_left", 0)
        if d["health"] != old_health:
            changed = True
            print(f"[Rotation] {d['domain']}: {old_health} → {d['health']}")
    # 自动轮值：如果主域名挂了，切换到下一个健康域名
    rotated = await _auto_rotate()
    if rotated:
        print(f"[Rotation] 自动轮值 → {rotated}")
    if changed or rotated:
        state._save()
    print(f"[Rotation] 检测完成: {sum(1 for d in domains if d.get('health')=='ok')}/{len(domains)} 健康")
    return {"checked": len(domains), "rotated_to": rotated}


async def _auto_rotate() -> str:
    """自动轮值逻辑：按权重选择最健康的域名"""
    domains = _get_domains()
    primary = next((d for d in domains if d.get("type") == "主域名"), None)
    # 主域名健康 → 不切换
    if primary and primary.get("health") == "ok" and primary.get("active"):
        return ""
    # 主域名挂了或没设 → 选权重最高的健康域名
    healthy = [d for d in domains if d.get("active") and d.get("health") == "ok" and d.get("type") != "主域名"]
    if not healthy:
        return ""
    # 按权重降序，同权重随机
    healthy.sort(key=lambda d: (-d.get("weight", 1), d["domain"]))
    best = healthy[0]
    # 如果主域名存在但不健康，停用它，激活最佳替补
    if primary and primary.get("health") != "ok":
        primary["active"] = False
    best["active"] = True
    return best["domain"]


# ===== API 端点 =====

@router.get("/domains")
async def get_domains(_=Depends(verify_token)):
    """获取域名列表（附带实时检测数据）"""
    await handle_risk("L1", "查看轮值域名列表")
    domains = _get_domains()
    # 并发补充实时数据，最快速度返回
    results = await asyncio.gather(*[_enrich_domain(d) for d in domains], return_exceptions=True)
    enriched = []
    for i, r in enumerate(results):
        if isinstance(r, Exception):
            enriched.append(dict(domains[i]))
        else:
            enriched.append(r)
    state._save()
    return enriched


@router.post("/domains")
async def add_domain(req: "AddDomainRequest", _=Depends(verify_token)):
    """添加域名"""
    domains = _get_domains()
    if any(d["domain"] == req.domain for d in domains):
        raise HTTPException(400, "域名已存在")
    domains.append({
        "domain": req.domain, "active": True, "health": "ok",
        "type": req.type, "weight": 1,
    })
    state._save()
    return {"domain": req.domain, "added": True}


@router.delete("/domains/{domain}")
async def remove_domain(domain: str, _=Depends(verify_token)):
    """删除域名"""
    domains = _get_domains()
    before = len(domains)
    state._data["rotation_domains"] = [d for d in domains if d["domain"] != domain]
    state._save()
    if len(_get_domains()) == before:
        raise HTTPException(404, "域名不存在")
    return {"domain": domain, "removed": True}


class AddDomainRequest(BaseModel):
    domain: str
    type: str = "轮值"


class ToggleRequest(BaseModel):
    domain: str
    active: bool


class CheckRequest(BaseModel):
    domain: str


class WeightRequest(BaseModel):
    domain: str
    weight: int = 1


@router.post("/toggle")
async def toggle_domain(req: ToggleRequest, _=Depends(verify_token)):
    """启用/停用域名"""
    await handle_risk("L2", f"域名轮值: {req.domain} {'启用' if req.active else '停用'}")
    for d in _get_domains():
        if d["domain"] == req.domain:
            d["active"] = req.active
            if req.active:
                d["health"] = "ok"
            else:
                d["health"] = "disabled"
            state._save()
            return {"domain": req.domain, "active": req.active, "health": d["health"]}
    raise HTTPException(status_code=404, detail="域名不存在")


@router.post("/check")
async def check_domain(req: CheckRequest, _=Depends(verify_token)):
    """检测单个域名（真实 HTTP 检测）"""
    await handle_risk("L1", f"域名检测", req.domain)
    for d in _get_domains():
        if d["domain"] == req.domain:
            check = await _check_one(d)
            ssl_info = await _check_ssl(d["domain"])
            d["health"] = "ok" if check.get("ok") else "error"
            d["latency"] = check.get("latency_ms", 0)
            d["ip"] = check.get("ip", "")
            d["status_code"] = check.get("status_code", 0)
            d["ssl_expiry"] = ssl_info.get("expiry", "")
            d["ssl_days"] = ssl_info.get("days_left", 0)
            d["last_check"] = datetime.now().isoformat()
            if not check.get("ok"):
                d["last_error"] = check.get("error", "")
            state._save()
            return {
                "domain": req.domain,
                "health": d["health"],
                "latency": d["latency"],
                "ip": d["ip"],
                "status_code": d["status_code"],
                "ssl_expiry": d["ssl_expiry"],
                "ssl_days": d["ssl_days"],
                "online": check.get("ok", False),
            }
    raise HTTPException(status_code=404, detail="域名不存在")


@router.get("/report")
async def rotation_report(_=Depends(verify_token)):
    """生成轮值报告"""
    await handle_risk("L1", "生成轮值报告")
    domains = _get_domains()
    active = [d for d in domains if d.get("active")]
    inactive = [d for d in domains if not d.get("active")]
    unhealthy = [d for d in domains if d.get("health") not in ("ok", "disabled")]
    healthy_active = [d for d in active if d.get("health") == "ok"]
    primary = next((d for d in domains if d.get("type") == "主域名"), None)
    return {
        "total": len(domains),
        "active": len(active),
        "inactive": len(inactive),
        "unhealthy": len(unhealthy),
        "health_rate": f"{len(healthy_active)/max(len(active),1)*100:.0f}%",
        "primary_domain": primary["domain"] if primary else "未设置",
        "primary_healthy": primary.get("health") == "ok" if primary else False,
        "current_rotation": primary["domain"] if (primary and primary.get("health") == "ok" and primary.get("active")) else
            (next((d["domain"] for d in active if d.get("health") == "ok"), "无可用")),
        "avg_latency": round(sum(d.get("latency", 0) for d in active if d.get("latency")) / max(len([d for d in active if d.get("latency")]), 1), 1),
        "unhealthy_domains": [{"domain": d["domain"], "error": d.get("last_error", "")} for d in unhealthy],
        "ssl_expiring_soon": [{"domain": d["domain"], "days_left": d.get("ssl_days", 0)} for d in domains if d.get("ssl_days", 999) < 30],
    }


@router.post("/weight")
async def set_weight(req: WeightRequest, _=Depends(verify_token)):
    """调整域名权重（权重越高越优先被选为轮值目标）"""
    await handle_risk("L2", "调整域名权重", f"{req.domain}={req.weight}")
    for d in _get_domains():
        if d["domain"] == req.domain:
            d["weight"] = max(1, min(10, req.weight))
            state._save()
            return {"domain": req.domain, "weight": d["weight"]}
    raise HTTPException(status_code=404, detail="域名不存在")


@router.post("/check-all")
async def check_all_domains(_=Depends(verify_token)):
    """检测所有域名并执行自动轮值"""
    await handle_risk("L2", "全量检测轮值域名")
    result = await _check_all()
    domain_list = _get_domains()
    return {
        "ok": True,
        "total_checked": result["checked"],
        "rotated_to": result["rotated_to"],
        "healthy_count": sum(1 for d in domain_list if d.get("health") == "ok"),
        "unhealthy_count": sum(1 for d in domain_list if d.get("health") == "error"),
    }


@router.get("/history")
async def rotation_history(_=Depends(verify_token)):
    """获取域名检测历史"""
    history = state._data.get("rotation_history", [])
    return {"history": history[-50:]}


@router.post("/rotate")
async def manual_rotate(_=Depends(verify_token)):
    """手动触发轮值切换"""
    await handle_risk("L2", "手动触发域名轮值")
    rotated = await _auto_rotate()
    state._save()
    return {"ok": bool(rotated), "rotated_to": rotated or "无可用替补"}
