"""网络工具 — Ping/DNS/端口扫描/TraceRoute"""
import asyncio, socket, subprocess
from fastapi import APIRouter, Depends, HTTPException
from auth import verify_token
from risk import handle_risk

router = APIRouter(prefix="/network", tags=["Network"])


async def _run(cmd: list, timeout: int = 15) -> dict:
    """运行命令并返回结果"""
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        return {"ok": r.returncode == 0, "stdout": r.stdout[:2000], "stderr": r.stderr[:500]}
    except subprocess.TimeoutExpired:
        return {"ok": False, "error": "执行超时"}
    except FileNotFoundError:
        return {"ok": False, "error": f"命令不存在: {cmd[0]}"}
    except Exception as e:
        return {"ok": False, "error": str(e)}


@router.post("/ping")
async def network_ping(host: str, count: int = 4, _=Depends(verify_token)):
    """Ping 测试"""
    await handle_risk("L1", f"Ping: {host}")
    result = await _run(["ping", "-c", str(count), "-W", "3", host])
    return {"host": host, "count": count, **result}


@router.post("/dns")
async def network_dns(domain: str, _=Depends(verify_token)):
    """DNS 解析"""
    await handle_risk("L1", f"DNS查询: {domain}")
    try:
        result = await asyncio.get_event_loop().run_in_executor(
            None, lambda: socket.getaddrinfo(domain, 443, socket.AF_INET))
        ips = list(set(r[4][0] for r in result))
        return {"ok": True, "domain": domain, "ips": ips, "count": len(ips)}
    except socket.gaierror as e:
        return {"ok": False, "domain": domain, "error": f"解析失败: {e}"}
    except Exception as e:
        return {"ok": False, "error": str(e)}


@router.post("/port-scan")
async def network_port_scan(host: str, ports: str = "22,80,443,3306,6379,8080,9000", _=Depends(verify_token)):
    """端口扫描"""
    await handle_risk("L2", f"端口扫描: {host}")
    port_list = [int(p.strip()) for p in ports.split(",") if p.strip().isdigit()]
    results = []
    for port in port_list[:20]:  # 最多扫20个
        try:
            _, writer = await asyncio.wait_for(
                asyncio.open_connection(host, port), timeout=2)
            writer.close()
            await writer.wait_closed()
            results.append({"port": port, "open": True})
        except Exception:
            results.append({"port": port, "open": False})
    return {"ok": True, "host": host, "results": results, "open_count": sum(1 for r in results if r["open"])}


@router.post("/traceroute")
async def network_traceroute(host: str, _=Depends(verify_token)):
    """路由追踪"""
    await handle_risk("L1", f"路由追踪: {host}")
    result = await _run(["traceroute", "-n", "-m", "15", host])
    return {"host": host, **result}


@router.post("/http-check")
async def network_http_check(url: str, _=Depends(verify_token)):
    """HTTP 状态检查"""
    await handle_risk("L1", f"HTTP检查: {url}")
    import httpx
    try:
        async with httpx.AsyncClient(timeout=10, follow_redirects=True) as c:
            r = await c.get(url, headers={"User-Agent": "Mozilla/5.0"})
            return {"ok": True, "url": url, "status": r.status_code, "elapsed_ms": round(r.elapsed.total_seconds() * 1000), "size": len(r.content)}
    except Exception as e:
        return {"ok": False, "url": url, "error": str(e)[:200]}
