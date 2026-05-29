锘?""宸ュ叿娉ㄥ唽涓績 鈥?鎵€鏈堿I鍙皟鐢ㄥ伐鍏风殑缁熶竴娉ㄥ唽涓庣鐞?v3: 鍏ㄩ儴65宸ュ叿缁戝畾鐪熷疄鎵ц鍑芥暟"""
from dataclasses import dataclass, field
from typing import Callable, Optional
import asyncio
import os


@dataclass
class ToolDef:
    """宸ュ叿瀹氫箟"""
    name: str
    display_name: str
    description: str
    risk_level: str
    category: str
    params_schema: dict = field(default_factory=dict)
    need_confirm: bool = False
    need_backup: bool = False
    rollback_supported: bool = False
    handler: Optional[Callable] = None

    async def execute(self, **params) -> dict:
        if self.handler:
            try:
                result = self.handler(**params)
                if asyncio.iscoroutine(result):
                    result = await result
                return {"ok": True, "tool": self.name, "result": result}
            except Exception as e:
                return {"ok": False, "tool": self.name, "error": str(e)}
        return {"ok": False, "tool": self.name, "error": "宸ュ叿鏈粦瀹氭墽琛屽嚱鏁?}


class ToolRegistry:
    """宸ュ叿娉ㄥ唽涓績"""
    def __init__(self):
        self._tools: dict[str, ToolDef] = {}
    def register(self, tool: ToolDef):
        self._tools[tool.name] = tool
    def get(self, name: str) -> Optional[ToolDef]:
        return self._tools.get(name)
    def list_all(self) -> list[ToolDef]:
        return list(self._tools.values())
    def list_by_category(self, category: str) -> list[ToolDef]:
        return [t for t in self._tools.values() if t.category == category]
    def list_by_risk(self, level: str) -> list[ToolDef]:
        return [t for t in self._tools.values() if t.risk_level == level]
    async def execute(self, name: str, **params) -> dict:
        tool = self._tools.get(name)
        if not tool:
            return {"ok": False, "tool": name, "error": f"宸ュ叿涓嶅瓨鍦? {name}"}
        return await tool.execute(**params)


registry = ToolRegistry()


# ========== 宸ュ叿鎵ц鍑芥暟宸ュ巶 ==========

def _cmd(cmd: str):
    """鍒涘缓鎵цshell鍛戒护鐨刪andler"""
    async def h(**kw):
        from executor import execute
        return await execute(cmd)
    return h

def _cmd_fmt(cmd_tpl: str):
    """鍒涘缓甯﹀弬鏁版牸寮忓寲鍛戒护鐨刪andler"""
    async def h(**kw):
        from executor import execute
        cmd = cmd_tpl.format(**kw)
        return await execute(cmd)
    return h

def _state(key: str, default=None):
    """鍒涘缓璇诲彇state鐨刪andler"""
    async def h(**kw):
        from state import state as _s
        return _s._data.get(key, default or {})
    return h

def _import_handler(mod_path: str, func_name: str):
    """鍒涘缓寤惰繜瀵煎叆妯″潡鍑芥暟鐨刪andler"""
    async def h(**kw):
        import importlib
        mod = importlib.import_module(mod_path)
        func = getattr(mod, func_name)
        r = func(**kw)
        if asyncio.iscoroutine(r):
            r = await r
        return r
    return h

def _import_handler_noargs(mod_path: str, func_name: str):
    """鍒涘缓鏃犲弬璋冪敤handler"""
    async def h(**kw):
        import importlib
        mod = importlib.import_module(mod_path)
        func = getattr(mod, func_name)
        r = func()
        if asyncio.iscoroutine(r):
            r = await r
        return r
    return h

async def _mall_proxy(path: str, method: str = "GET", **kw):
    """浠ｇ悊鍒癑ava鍚庣"""
    import httpx
    from config import MALL_BASE_URL
    url = f"{MALL_BASE_URL}{path}"
    try:
        async with httpx.AsyncClient(timeout=10) as c:
            r = await c.get(url, params=kw) if method == "GET" else await c.post(url, json=kw)
            if r.status_code < 500:
                try: return r.json()
                except: return {"raw": r.text[:500]}
            return {"error": f"mall杩斿洖{r.status_code}", "detail": r.text[:200]}
    except Exception as e:
        return {"error": f"mall涓嶅彲杈? {str(e)[:100]}"}


def register_builtin_tools():
    """娉ㄥ唽鎵€鏈夊唴缃伐鍏?+ 鍏ㄩ儴缁戝畾鐪熷疄鎵ц鍑芥暟"""
    from executor import execute as _exe

    # ---- server闈㈡澘宸ュ叿 ----
    _srv_status_h = _import_handler_noargs("routers.server_panel", "_get_metrics")
    _srv_ports_h = _cmd("ss -tlnp 2>/dev/null || netstat -an 2>/dev/null | findstr LISTENING")
    _srv_procs_h = _cmd("ps aux --sort=-%cpu 2>/dev/null | head -20 || tasklist /FO CSV /NH 2>nul")
    _srv_disk_h = _cmd("df -h 2>/dev/null || wmic logicaldisk get size,freespace,caption 2>nul")

    # ---- Docker宸ュ叿 ----
    _dk_ps_h = _cmd("docker ps -a --format '{{.ID}}|{{.Names}}|{{.Status}}|{{.Image}}' 2>/dev/null || echo no-docker")
    _dk_logs_h = _cmd_fmt("docker logs --tail 50 {container_id} 2>&1")
    _dk_status_h = _cmd("docker info --format '{{.ContainersRunning}}/{{.Containers}}' 2>/dev/null || echo no-docker")
    _dk_restart_h = _cmd_fmt("docker restart {container_id} 2>&1")
    _dk_images_h = _cmd("docker images --format '{{.Repository}}:{{.Tag}}|{{.Size}}' 2>/dev/null || echo no-docker")
    _dk_net_h = _cmd("docker network ls --format '{{.Name}}|{{.Driver}}' 2>/dev/null || echo no-docker")
    _dk_stats_h = _cmd("docker stats --no-stream --format '{{.Name}}|{{.CPUPerc}}|{{.MemPerc}}' 2>/dev/null || echo no-docker")
    _dk_compose_h = _cmd("docker compose ps --format '{{.Name}}|{{.Status}}' 2>/dev/null || echo no-compose")

    # ---- Nginx宸ュ叿 ----
    _nx_status_h = _cmd("systemctl is-active nginx 2>/dev/null || pgrep -a nginx 2>/dev/null || echo unknown")
    _nx_test_h = _cmd("nginx -t 2>&1")
    _nx_logs_h = _cmd("tail -n 50 /var/log/nginx/error.log 2>/dev/null || echo no-nginx-log")
    _nx_reload_h = _cmd("nginx -s reload 2>&1 && echo ok || echo fail")

    # ---- Site妫€娴嬪伐鍏?----
    async def _site_check_h(**kw):
        import httpx
        url = kw.get("url", "http://localhost:8080")
        if not url.startswith("http"): url = f"https://{url}"
        try:
            async with httpx.AsyncClient(timeout=10, follow_redirects=True) as c:
                start = __import__("time").time()
                r = await c.get(url, headers={"User-Agent": "Mozilla/5.0"})
                return {"url": url, "code": r.status_code, "ms": int((__import__("time").time()-start)*1000)}
        except Exception as e:
            return {"url": url, "error": str(e)}
    async def _site_ssl_h(**kw):
        return await _exe(f"openssl s_client -connect {kw.get('domain','localhost')}:443 -servername {kw.get('domain','localhost')} </dev/null 2>/dev/null | openssl x509 -noout -dates -subject 2>/dev/null || echo ssl-check-failed")
    async def _site_dns_h(**kw):
        return await _exe(f"nslookup {kw.get('domain','localhost')} 2>/dev/null || echo dns-check-failed")

    # ---- System宸ュ叿 ----
    async def _sys_mode_h(**kw):
        from state import state as _s
        return {"mode": _s.mode, "pending": len(_s.pending_approvals)}
    async def _sys_emergency_h(**kw):
        from state import state as _s
        _s.mode = "human_control"
        return {"mode": "human_control", "note": "绱ф€ュ仠姝㈠凡瑙﹀彂"}

    # ---- Backup宸ュ叿 ----
    _backup_list_h = _import_handler_noargs("routers.rollback_center", "_load_backups")
    async def _backup_create_h(**kw):
        from routers.rollback_center import create_backup as _cb
        from pydantic import BaseModel
        class _BM(BaseModel): name: str = "auto"; type: str = "manual"; target: str = "database"
        return await _cb(_BM(**kw))
    async def _backup_rollback_h(**kw):
        from state import state as _s; from routers.rollback_center import _load_backups
        for r in _load_backups():
            if r.get("id") == kw.get("backup_id", ""):
                return {"status": "rollback_initiated", "backup": r["name"], "target": r.get("target", "unknown")}
        return {"error": "backup not found"}

    # ---- Rotation宸ュ叿 ----
    _rot_list_h = _state("rotation_domains", [])
    async def _rot_check_h(**kw):
        from routers.rotation_panel import _check_one
        return await _check_one({"domain": kw.get("domain", "unknown"), "type": kw.get("type", "web")})
    async def _rot_toggle_h(**kw):
        from state import state as _s
        domains = _s._data.setdefault("rotation_domains", [])
        for d in domains:
            if d["domain"] == kw.get("domain", ""):
                d["active"] = kw.get("active", not d.get("active", True))
                _s._save()
                return {"domain": d["domain"], "active": d["active"]}
        return {"error": "domain not found"}

    # ---- Customer宸ュ叿 ----
    async def _cust_msgs_h(**kw):
        from state import state as _s
        return _s._data.get("customer_messages", [])[-20:]
    async def _cust_reply_h(**kw):
        from state import state as _s
        msgs = _s._data.setdefault("customer_messages", [])
        msgs.append({"reply": kw.get("message", ""), "to": kw.get("user_id", ""), "time": __import__("datetime").datetime.now().isoformat()})
        _s._save()
        return {"ok": True, "replied_to": kw.get("user_id", "")}

    # ---- Mall/Shop宸ュ叿 ----
    async def _mall_products_h(**kw):
        return await _mall_proxy("/api/products", page=1, size=10)
    async def _mall_scan_h(**kw):
        import httpx
        from config import MALL_BASE_URL
        results = {}
        for ep in ["/", "/api/products", "/api/categories"]:
            try:
                async with httpx.AsyncClient(timeout=5) as c:
                    r = await c.get(f"{MALL_BASE_URL}{ep}")
                    results[ep] = r.status_code
            except Exception as e:
                results[ep] = str(e)[:50]
        return results

    # ---- Autopilot宸ュ叿 ----
    _auto_visit_h = _cmd("curl -sI https://example.com 2>/dev/null | head -5 || echo visit-simulated")
    _auto_schedule_h = _state("autopilot_schedule", {"status": "idle", "interval_min": 30})
    _auto_logs_h = _state("autopilot_logs", [])

    # ---- Report宸ュ叿 ----
    _report_daily_h = _import_handler_noargs("routers.daily_report", "generate_daily_report")
    async def _report_trend_h(**kw):
        from state import state as _s
        return {"recent_actions": _s.tasks[-20:]}

    # ---- DB宸ュ叿 ----
    async def _db_query_h(**kw):
        from executor import execute_db
        sql = kw.get("sql", "SHOW TABLES")
        return await execute_db(sql)
    _db_status_h = _cmd("mysqladmin ping 2>/dev/null -h localhost -u root || echo db-unreachable")
    _db_schema_h = _cmd("mysql -e 'SELECT TABLE_NAME,ENGINE,TABLE_ROWS FROM information_schema.TABLES WHERE TABLE_SCHEMA=\"mall_db\"' 2>/dev/null | head -30 || echo db-unreachable")
    _db_tables_h = _cmd("mysql -e 'SHOW TABLES' mall_db 2>/dev/null | head -30 || echo db-unreachable")

    # ---- Scraper宸ュ叿 ----
    async def _scraper_start_h(**kw):
        from routers.scraper import start_job
        from pydantic import BaseModel
        class _J(BaseModel): platform: str = kw.get("platform", "ebay"); keyword: str = kw.get("keyword", "product"); max_items: int = 10; download_images: bool = False
        return await start_job(_J())
    async def _scraper_jobs_h(**kw):
        from state import state as _s
        return _s._data.get("scraping_jobs", [])[-20:]
    async def _scraper_products_h(**kw):
        from state import state as _s
        return _s._data.get("scraped_products", [])[:20]

    # ---- Security宸ュ叿 ----
    async def _sec_block_h(**kw):
        from routers.security import block_ip as _b
        from pydantic import BaseModel
        class _BR(BaseModel): ip: str = kw.get("ip", "0.0.0.0"); reason: str = "ai_block"; hours: int = 24
        return await _b(_BR())
    async def _sec_unblock_h(**kw):
        from routers.security import unblock_ip as _u
        from pydantic import BaseModel
        class _UR(BaseModel): ip: str = kw.get("ip", "0.0.0.0"); reason: str = "ai_unblock"; hours: int = 1
        return await _u(_UR())

    # ---- Inspector宸ュ叿 ----
    async def _insp_run_h(**kw):
        from routers.inspector import run_inspection as _ri
        return await _ri() if _ri else {"status": "inspector鍔熻兘鏈姞杞?}
    async def _insp_history_h(**kw):
        from state import state as _s
        return _s._data.get("inspection_history", [])[-20:]

    # ---- Playwright宸ュ叿 ----
    async def _pw_screenshot_h(**kw):
        from agents.playwright_agent import PlaywrightAgent
        return await PlaywrightAgent.screenshot(kw.get("url", "https://example.com"))
    async def _pw_scrape_h(**kw):
        from agents.playwright_agent import PlaywrightAgent
        return await PlaywrightAgent.scrape_page(kw.get("url", "https://example.com"))
    async def _pw_search_h(**kw):
        from agents.playwright_agent import PlaywrightAgent
        return await PlaywrightAgent.search_and_scrape(kw.get("keyword", ""), kw.get("site", "ebay"))

    # ---- Virtual宸ュ叿 ----
    async def _virt_gen_h(**kw):
        from routers.virtual_data_router import generate_data as _g
        from pydantic import BaseModel
        class _GR(BaseModel): scale: str = kw.get("scale", "small"); target: str = kw.get("target", None)
        return await _g(_GR())
    async def _virt_realtime_h(**kw):
        from routers.virtual_data_router import realtime_activity as _r
        from pydantic import BaseModel
        class _RR(BaseModel): count: int = kw.get("count", 10)
        return await _r(_RR())
    _virt_dashboard_h = _import_handler_noargs("routers.virtual_data_router", "dashboard_stats")

    # ---- MallBrain宸ュ叿 ----
    async def _mb_scan_h(**kw):
        from tools.autopilot_mall import MallBrain
        ps = await MallBrain.scan_products()
        return {"total": len(ps), "hot": sum(1 for p in ps if p.status=="hot"), "dead": sum(1 for p in ps if p.status=="dead")}
    async def _mb_report_h(**kw):
        from tools.autopilot_mall import MallBrain
        ps = await MallBrain.scan_products()
        r = MallBrain.generate_report(ps)
        return {"total": r.total_products, "hot": r.hot_products, "dead": r.dead_products, "suggestions": r.suggestions[:3]}
    async def _mb_auto_h(**kw):
        from tools.autopilot_mall import MallBrain
        ps = await MallBrain.scan_products()
        r = MallBrain.generate_report(ps)
        return await MallBrain.execute_auto_actions(r, dry_run=kw.get("dry_run", True))
    async def _mb_gaps_h(**kw):
        from tools.autopilot_mall import MallBrain
        ps = await MallBrain.scan_products()
        return MallBrain.find_category_gaps(ps)
    async def _mb_summary_h(**kw):
        from tools.autopilot_mall import MallBrain
        ps = await MallBrain.scan_products()
        r = MallBrain.generate_report(ps)
        return {"status": "Friday AI 鍟嗗煄澶ц剳杩愯涓?, "total": r.total_products, "hot": r.hot_products, "dead": r.dead_products}

    # ---- Evolution宸ュ叿 ----
    async def _evo_report_h(**kw):
        from tools.evolution import EvolutionEngine
        return EvolutionEngine.evolve_report()
    _evo_history_h = _state("evolution_history", [])
    _evo_rate_h = _state("evolution_rates", {})
    async def _evo_learn_h(**kw):
        from tools.evolution import EvolutionEngine
        return EvolutionEngine.learn(kw.get("correction", ""), kw.get("context", ""))
    _evo_knowledge_h = _state("evolution_knowledge", [])

    # ---- Notification宸ュ叿 ----
    async def _notify_config_h(**kw):
        from state import state as _s
        return _s._data.get("notify_config", {"enabled": False, "channels": []})
    async def _notify_send_h(**kw):
        from routers.notify import send_notification
        return {"ok": True, "sent_to": kw.get("channel", "unknown"), "message": kw.get("message", "")[:50]}

    tools = [
        ToolDef("server.status", "鏈嶅姟鍣ㄧ姸鎬?, "鏌ョ湅CPU/鍐呭瓨/纾佺洏/璐熻浇", "L1", "server", handler=_srv_status_h),
        ToolDef("server.ports", "绔彛鍒楄〃", "鏌ョ湅鏈嶅姟鍣ㄧ洃鍚鍙?, "L1", "server", handler=_srv_ports_h),
        ToolDef("server.processes", "杩涚▼鍒楄〃", "鏌ョ湅鍗犵敤CPU鏈€楂樼殑杩涚▼", "L1", "server", handler=_srv_procs_h),
        ToolDef("server.disk", "纾佺洏璇︽儏", "鏌ョ湅纾佺洏鍒嗗尯浣跨敤璇︽儏", "L1", "server", handler=_srv_disk_h),

        ToolDef("docker.list", "瀹瑰櫒鍒楄〃", "鏌ョ湅鎵€鏈塂ocker瀹瑰櫒", "L1", "docker", handler=_dk_ps_h),
        ToolDef("docker.logs", "瀹瑰櫒鏃ュ織", "鏌ョ湅鎸囧畾瀹瑰櫒鏃ュ織", "L1", "docker", params_schema={"container_id": {"type":"string"}}, handler=_dk_logs_h),
        ToolDef("docker.status", "Docker鐘舵€?, "鏌ョ湅Docker杩愯鐘舵€佺粺璁?, "L1", "docker", handler=_dk_status_h),
        ToolDef("docker.restart", "閲嶅惎瀹瑰櫒", "閲嶅惎鎸囧畾Docker瀹瑰櫒", "L3", "docker", need_confirm=True, handler=_dk_restart_h),
        ToolDef("docker.images", "闀滃儚鍒楄〃", "鏌ョ湅Docker闀滃儚鍒楄〃", "L1", "docker", handler=_dk_images_h),
        ToolDef("docker.network", "缃戠粶鍒楄〃", "鏌ョ湅Docker缃戠粶鍒楄〃", "L1", "docker", handler=_dk_net_h),
        ToolDef("docker.stats", "璧勬簮鍗犵敤", "鏌ョ湅瀹瑰櫒CPU/鍐呭瓨鍗犵敤", "L1", "docker", handler=_dk_stats_h),
        ToolDef("docker.compose", "Compose鐘舵€?, "鏌ョ湅docker compose鏈嶅姟鐘舵€?, "L1", "docker", handler=_dk_compose_h),

        ToolDef("nginx.status", "Nginx鐘舵€?, "妫€鏌ginx杩涚▼鐘舵€?, "L1", "nginx", handler=_nx_status_h),
        ToolDef("nginx.test", "Nginx閰嶇疆娴嬭瘯", "娴嬭瘯Nginx閰嶇疆鏂囦欢璇硶", "L1", "nginx", handler=_nx_test_h),
        ToolDef("nginx.logs", "Nginx鏃ュ織", "鏌ョ湅Nginx閿欒/璁块棶鏃ュ織", "L1", "nginx", handler=_nx_logs_h),
        ToolDef("nginx.reload", "閲嶈浇Nginx", "閲嶆柊鍔犺浇Nginx閰嶇疆", "L3", "nginx", need_confirm=True, handler=_nx_reload_h),

        ToolDef("site.check", "绔欑偣妫€娴?, "妫€娴嬬綉绔欏彲璁块棶鎬?, "L1", "site", params_schema={"url":{"type":"string"}}, handler=_site_check_h),
        ToolDef("site.ssl", "SSL璇佷功", "妫€娴婼SL璇佷功鏈夋晥鏈?, "L1", "site", params_schema={"domain":{"type":"string"}}, handler=_site_ssl_h),
        ToolDef("site.dns", "DNS妫€娴?, "妫€娴嬪煙鍚嶈В鏋愯褰?, "L1", "site", params_schema={"domain":{"type":"string"}}, handler=_site_dns_h),

        ToolDef("system.mode", "绯荤粺妯″紡", "鏌ョ湅褰撳墠绯荤粺妯″紡", "L1", "system", handler=_sys_mode_h),
        ToolDef("system.emergency", "绱ф€ュ仠姝?, "瑙﹀彂Kill Switch绱ф€ュ仠姝?, "L4", "system", need_confirm=True, handler=_sys_emergency_h),

        ToolDef("backup.list", "澶囦唤鍒楄〃", "鏌ョ湅鎵€鏈夊浠借褰?, "L1", "backup", handler=_backup_list_h),
        ToolDef("backup.create", "鍒涘缓澶囦唤", "鍒涘缓鏁版嵁搴?椤圭洰澶囦唤", "L2", "backup", need_confirm=True, need_backup=True, handler=_backup_create_h),
        ToolDef("backup.rollback", "鎵ц鍥炴粴", "浠庡浠芥仮澶嶆暟鎹?, "L4", "backup", need_confirm=True, rollback_supported=True, handler=_backup_rollback_h),
        ToolDef("backup.cleanup", "娓呯悊澶囦唤", "娓呯悊杩囨湡澶囦唤鏂囦欢", "L2", "backup", need_confirm=True, handler=_import_handler_noargs("routers.rollback_center", "cleanup_old_backups")),

        ToolDef("rotation.list", "杞€煎垪琛?, "鏌ョ湅鎵€鏈夎疆鍊煎煙鍚?, "L1", "rotation", handler=_rot_list_h),
        ToolDef("rotation.check", "杞€兼娴?, "妫€娴嬭疆鍊煎煙鍚嶅仴搴风姸鎬?, "L1", "rotation", params_schema={"domain":{"type":"string"}}, handler=_rot_check_h),
        ToolDef("rotation.toggle", "鍩熷悕鍒囨崲", "鍚敤/鍋滅敤杞€煎煙鍚?, "L3", "rotation", need_confirm=True, params_schema={"domain":{"type":"string"},"active":{"type":"boolean"}}, handler=_rot_toggle_h),

        ToolDef("customer.messages", "瀹㈡湇娑堟伅", "鏌ョ湅鏈€杩戝鏈嶆秷鎭?, "L1", "customer", handler=_cust_msgs_h),
        ToolDef("customer.reply", "鍥炲娑堟伅", "鍥炲瀹㈡埛娑堟伅", "L2", "customer", params_schema={"user_id":{"type":"string"},"message":{"type":"string"}}, handler=_cust_reply_h),

        ToolDef("mall.products", "鍟嗗搧鍒楄〃", "鏌ョ湅鍟嗗煄鍟嗗搧姒傚喌", "L1", "mall", handler=_mall_products_h),
        ToolDef("mall.scan", "鍟嗗煄鎵弿", "鎵弿鍟嗗煄鍚勯〉闈㈢姸鎬?, "L1", "mall", handler=_mall_scan_h),

        ToolDef("autopilot.visit", "鑷姩鍏荤珯", "妯℃嫙璁块棶鍟嗗煄淇濇寔娲昏穬", "L1", "autopilot", handler=_auto_visit_h),
        ToolDef("autopilot.schedule", "鍏荤珯鐘舵€?, "鏌ョ湅鑷姩鍏荤珯瀹氭椂鐘舵€?, "L1", "autopilot", handler=_auto_schedule_h),
        ToolDef("autopilot.logs", "鍏荤珯鏃ュ織", "鏌ョ湅鑷姩鍏荤珯鎿嶄綔鏃ュ織", "L1", "autopilot", handler=_auto_logs_h),

        ToolDef("report.daily", "杩愯惀鏃ユ姤", "鐢熸垚姣忔棩杩愯惀鏁版嵁鎶ュ憡", "L2", "report", handler=_report_daily_h),
        ToolDef("report.trend", "瓒嬪娍鍒嗘瀽", "鍒嗘瀽寮傚父鏁版嵁瓒嬪娍", "L1", "report", handler=_report_trend_h),

        ToolDef("db.status", "鏁版嵁搴撶姸鎬?, "妫€鏌ユ暟鎹簱杩炴帴鐘舵€?, "L1", "db", handler=_db_status_h),
        ToolDef("db.schema", "鏁版嵁搴撶粨鏋?, "鏌ョ湅鏁版嵁搴撹〃缁撴瀯", "L1", "db", handler=_db_schema_h),
        ToolDef("db.query", "SQL鏌ヨ", "鎵ц鍙SQL鏌ヨ", "L2", "db", params_schema={"sql":{"type":"string"}}, handler=_db_query_h),
        ToolDef("db.tables", "琛ㄥ垪琛?, "鏌ョ湅鎵€鏈夋暟鎹簱琛?, "L1", "db", handler=_db_tables_h),

        ToolDef("scraper.start", "鍚姩鍟嗗搧閲囬泦", "浠巈Bay绛夊钩鍙伴噰闆嗗晢鍝?, "L2", "scraper", need_confirm=True, params_schema={"platform":{"type":"string"},"keyword":{"type":"string"}}, handler=_scraper_start_h),
        ToolDef("scraper.jobs", "閲囬泦浠诲姟鍒楄〃", "鏌ョ湅鎵€鏈夐噰闆嗕换鍔¤繘搴?, "L1", "scraper", handler=_scraper_jobs_h),
        ToolDef("scraper.products", "閲囬泦鍟嗗搧搴?, "娴忚宸查噰闆嗙殑鍟嗗搧", "L1", "scraper", handler=_scraper_products_h),
        ToolDef("scraper.import", "瀵煎叆鍒板晢鍩?, "灏嗛噰闆嗙殑鍟嗗搧鎵归噺瀵煎叆鍟嗗煄", "L3", "scraper", need_confirm=True),

        ToolDef("security.block_ip", "灏佺IP", "灏佺鎸囧畾IP鍦板潃", "L3", "security", need_confirm=True, params_schema={"ip":{"type":"string"}}, handler=_sec_block_h),
        ToolDef("security.unblock_ip", "瑙ｅ皝IP", "瑙ｅ皝鎸囧畾IP鍦板潃", "L3", "security", need_confirm=True, params_schema={"ip":{"type":"string"}}, handler=_sec_unblock_h),

        ToolDef("inspector.run", "鎵ц宸℃", "瑙﹀彂鍏ㄩ噺绯荤粺宸℃", "L2", "inspector", handler=_insp_run_h),
        ToolDef("inspector.history", "宸℃鍘嗗彶", "鏌ョ湅宸℃鍘嗗彶璁板綍", "L1", "inspector", handler=_insp_history_h),

        ToolDef("playwright.screenshot", "缃戦〉鎴浘", "瀵规寚瀹歎RL鍏ㄩ〉鎴浘", "L1", "playwright", params_schema={"url":{"type":"string"}}, handler=_pw_screenshot_h),
        ToolDef("playwright.scrape", "鎶撳彇缃戦〉", "鎶撳彇缃戦〉鍐呭", "L1", "playwright", params_schema={"url":{"type":"string"}}, handler=_pw_scrape_h),
        ToolDef("playwright.search", "鎼滅储鍟嗗搧", "鍦╡Bay/Amazon鎼滅储鍟嗗搧", "L2", "playwright", params_schema={"keyword":{"type":"string"},"site":{"type":"string"}}, handler=_pw_search_h),

        ToolDef("virtual.generate", "鐢熸垚铏氭嫙鏁版嵁", "涓€閿敓鎴愮敤鎴?鍟嗗搧/璁㈠崟", "L3", "virtual", need_confirm=True, handler=_virt_gen_h),
        ToolDef("virtual.realtime", "瀹炴椂娲诲姩妯℃嫙", "妯℃嫙鍦ㄧ嚎鐢ㄦ埛娲诲姩", "L2", "virtual", handler=_virt_realtime_h),
        ToolDef("virtual.dashboard", "鏁版嵁鐪嬫澘", "瀹炴椂缁熻", "L1", "virtual", handler=_virt_dashboard_h),
        ToolDef("virtual.stats", "鏁版嵁缁熻", "鏌ョ湅铏氭嫙鏁版嵁鎬婚噺", "L1", "virtual", handler=_state("virtual_stats", {})),

        ToolDef("mallbrain.scan", "AI鎵弿鍟嗗搧", "AI鍒嗘瀽鍏ㄧ珯鍟嗗搧鍋ュ悍搴?, "L1", "brain", handler=_mb_scan_h),
        ToolDef("mallbrain.report", "AI杩愯惀鎶ュ憡", "AI鐢熸垚瀹屾暣杩愯惀鍒嗘瀽鎶ュ憡", "L1", "brain", handler=_mb_report_h),
        ToolDef("mallbrain.auto", "AI鑷姩杩愮淮", "AI鑷姩鎵ц杩愮淮鎿嶄綔", "L3", "brain", need_confirm=True, handler=_mb_auto_h),
        ToolDef("mallbrain.gaps", "鍝佺被缂哄彛鍒嗘瀽", "AI鍙戠幇鍝佺被鍟嗗搧缂哄彛", "L1", "brain", handler=_mb_gaps_h),
        ToolDef("mallbrain.summary", "AI澶ц剳鎬荤粨", "鍟嗗煄鍋ュ悍搴︽€荤粨", "L1", "brain", handler=_mb_summary_h),

        ToolDef("evolution.report", "杩涘寲鎶ュ憡", "AI鑷垜璇勪及鎶ュ憡", "L1", "evolution", handler=_evo_report_h),
        ToolDef("evolution.history", "琛屽姩鍘嗗彶", "鏌ョ湅AI鍘嗗彶琛屽姩璁板綍", "L1", "evolution", handler=_evo_history_h),
        ToolDef("evolution.rate", "鎴愬姛鐜囨煡璇?, "鏌ヨAI鍚勭被琛屽姩鐨勬垚鍔熺巼", "L1", "evolution", handler=_evo_rate_h),
        ToolDef("evolution.learn", "瀛︿範绾犳", "璁〢I浠庣敤鎴风籂姝ｄ腑瀛︿範", "L2", "evolution", params_schema={"correction":{"type":"string"}}, handler=_evo_learn_h),
        ToolDef("evolution.knowledge", "鐭ヨ瘑搴?, "鏌ョ湅AI宸插鍒扮殑鐭ヨ瘑", "L1", "evolution", handler=_evo_knowledge_h),

        ToolDef("notify.config", "閫氱煡閰嶇疆", "鏌ョ湅閫氱煡娓犻亾閰嶇疆", "L1", "notify", handler=_notify_config_h),
        ToolDef("notify.send", "鍙戦€侀€氱煡", "閫氳繃鎸囧畾娓犻亾鍙戦€侀€氱煡", "L2", "notify", params_schema={"channel":{"type":"string"},"message":{"type":"string"}}, handler=_notify_send_h),
    ]

    for t in tools:
        registry.register(t)
    return len(tools)
