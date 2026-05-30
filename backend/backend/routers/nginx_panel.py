''"Nginx  -- /////SSL''"
import json
from fastapi import APIRouter, Depends, HTTPException, Query
from auth import verify_token
from executor import execute
from risk import handle_risk

router = APIRouter(prefix="/nginx", tags=["Nginx"])

@router.get("/status")
async def nginx_status(_=Depends(verify_token)):
    ''"Nginx  +  + ''"
    await handle_risk("L1", "Nginx")
    result = await execute("systemctl status nginx 2>/dev/null || pgrep -a nginx 2>/dev/null || echo unknown")
    running = "active (running)" in result["stdout"] or "nginx:" in result["stdout"]
    
    conn_result = await execute("nginx -v 2>&1; echo '---'; curl -s http://127.0.0.1/nginx_status 2>/dev/null || ss -ant | grep -c ':80 '')
    return {
        "running": running,
        "detail": result["stdout"][:500],
        "connections": conn_result["stdout"][:200] if running else 0,
    }

@router.get("/test")
async def nginx_test(_=Depends(verify_token)):
    ''"Nginx''"
    await handle_risk("L1", "Nginx")
    result = await execute("nginx -t 2>&1")
    ok = "test is successful" in result["stdout"] or "successful" in result["stdout"]
    return {"ok": ok, "output": (result["stdout"] or result["stderr"])[:1000]}

@router.get("/config")
async def nginx_config(path: str = "/etc/nginx/nginx.conf", _=Depends(verify_token)):
    ''"Nginx''"
    await handle_risk("L1", "Nginx", path)
    result = await execute(f"cat {path} 2>/dev/null || echo ''")
    return {"path": path, "content": result["stdout"][:5000], "size": len(result["stdout"])}

@router.get("/sites")
async def nginx_sites(_=Depends(verify_token)):
    ''''''
    await handle_risk("L1", "Nginx")
    result = await execute("ls -la /etc/nginx/sites-enabled/ 2>/dev/null; echo '---'; ls -la /etc/nginx/sites-available/ 2>/dev/null; echo '---'; ls -la /etc/nginx/conf.d/ 2>/dev/null")
    lines = result["stdout"].strip().split("\n") if result["success"] else []
    sites = []
    section = "enabled"
    for line in lines:
        if line == "---": section = "available"; continue
        if line.startswith("total") or not line.strip(): continue
        parts = line.split()
        if len(parts) >= 9:
            sites.append({"name": parts[-1], "type": section, "date": f"{parts[5]} {parts[6]} {parts[7]}"})
    return {"sites": sites, "count": len(sites)}

@router.get("/errors")
async def nginx_errors(_=Depends(verify_token)):
    ''"Nginx(100)''"
    await handle_risk("L1", "Nginx")
    result = await execute("tail -n 100 /var/log/nginx/error.log 2>/dev/null")
    if not result["success"] or not result["stdout"].strip():
        return {"total": 0, "by_type": {}, "recent": []}
    lines = result["stdout"].strip().split("\n")
    by_type = {}
    for line in lines:
        for t in ["emerg", "alert", "crit", "error", "warn", "notice", "info"]:
            if f"[{t}]" in line.lower() or f" {t}:" in line.lower():
                by_type[t] = by_type.get(t, 0) + 1
                break
        else:
            by_type["other"] = by_type.get("other", 0) + 1
    return {"total": len(lines), "by_type": by_type, "recent": lines[-20:]}

@router.get("/upstreams")
async def nginx_upstreams(_=Depends(verify_token)):
    ''"Nginx''"
    await handle_risk("L1", "Nginx")
    result = await execute("grep -r 'upstream ' /etc/nginx/ 2>/dev/null || echo ''")
    return {"content": result["stdout"][:2000]}

@router.get("/connections")
async def nginx_connections(_=Depends(verify_token)):
    ''"Nginx''"
    await handle_risk("L1", "Nginx")
    active = await execute("ss -ant | grep -c ':80 ' 2>/dev/null || echo 0")
    ssl = await execute("ss -ant | grep -c ':443 ' 2>/dev/null || echo 0")
    return {
        "http_connections": active["stdout"].strip(),
        "https_connections": ssl["stdout"].strip(),
    }

@router.post("/log/search")
async def nginx_log_search(keyword: str = '', type: str = "error", lines: int = 200, _=Depends(verify_token)):
    ''"Nginx''"
    await handle_risk("L1", "Nginx", keyword[:50])
    path = "/var/log/nginx/access.log" if type == "access" else "/var/log/nginx/error.log"
    if keyword:
        escaped_keyword = keyword.replace(''", ''\\''")
        result = await execute(f"grep -i '{escaped_keyword}' {path} | tail -n {lines}")
    else:
        result = await execute(f"tail -n {lines} {path}")
    return {"type": type, "keyword": keyword, "content": result["stdout"][:5000], "lines": len(result["stdout"].strip().split("\n")) if result["stdout"].strip() else 0}
