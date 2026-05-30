"""Tool Registry - AI Tool Registry v3"""
from dataclasses import dataclass, field
from typing import Callable, Optional
import asyncio
import os


@dataclass
class ToolDef:
    ''''''
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
        return {"ok": False, "tool": self.name, "error": ''}


class ToolRegistry:
    ''''''
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
            return {"ok": False, "tool": name, "error": f": {name}"}
        return await tool.execute(**params)


registry = ToolRegistry()


# ==========  ==========

def _cmd(cmd: str):
    ''"shellhandler''"
    async def h(**kw):
        from executor import execute
        return await execute(cmd)
    return h

def _cmd_fmt(cmd_tpl: str):
    ''"handler''"
    async def h(**kw):
        from executor import execute
        cmd = cmd_tpl.format(**kw)
        return await execute(cmd)
    return h

def _state(key: str, default=None):
    ''"statehandler''"
    async def h(**kw):
        from state import state as _s
        return _s._data.get(key, default or {})
    return h

def _import_handler(mod_path: str, func_name: str):
    ''"handler''"
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
    ''"handler''"
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
    ''"Java''"
    import httpx
    from config import MALL_BASE_URL
    url = f"{MALL_BASE_URL}{path}"
    try:
        async with httpx.AsyncClient(timeout=10) as c:
            r = await c.get(url, params=kw) if method == "GET" else await c.post(url, json=kw)
            if r.status_code < 500:
                try: return r.json()
                except: return {"raw": r.text[:500]}
            return {"error": f"mall{r.status_code}", "detail": r.text[:200]}
    except Exception as e:
        return {"error": f"mall: {str(e)[:100]}"}


def register_builtin_tools():
    ''" + ''"
    from executor import execute as _exe

    # ---- server ----
    _srv_status_h = _import_handler_noargs("routers.server_panel", "_get_metrics")
    _srv_ports_h = _cmd("ss -tlnp 2>/dev/null || netstat -an 2>/dev/null | findstr LISTENING")
    _srv_procs_h = _cmd("ps aux --sort=-%cpu 2>/dev/null | head -20 || tasklist /FO CSV /NH 2>nul")
    _srv_disk_h = _cmd("df -h 2>/dev/null || wmic logicaldisk get size,freespace,caption 2>nul")

    # ---- Docker ----
    _dk_ps_h = _cmd("docker ps -a --format '{{.ID}}|{{.Names}}|{{.Status}}|{{.Image}}' 2>/dev/null || echo no-docker")
    _dk_logs_h = _cmd_fmt("docker logs --tail 50 {container_id} 2>&1")
    _dk_status_h = _cmd("docker info --format '{{.ContainersRunning}}/{{.Containers}}' 2>/dev/null || echo no-docker")
    _dk_restart_h = _cmd_fmt("docker restart {container_id} 2>&1")
    _dk_images_h = _cmd("docker images --format '{{.Repository}}:{{.Tag}}|{{.Size}}' 2>/dev/null || echo no-docker")
    _dk_net_h = _cmd("docker network ls --format '{{.Name}}|{{.Driver}}' 2>/dev/null || echo no-docker")
    _dk_stats_h = _cmd("docker stats --no-stream --format '{{.Name}}|{{.CPUPerc}}|{{.MemPerc}}' 2>/dev/null || echo no-docker")
    _dk_compose_h = _cmd("docker compose ps --format '{{.Name}}|{{.Status}}' 2>/dev/null || echo no-compose")

    # ---- Nginx ----
    _nx_status_h = _cmd("systemctl is-active nginx 2>/dev/null || pgrep -a nginx 2>/dev/null || echo unknown")
    _nx_test_h = _cmd("nginx -t 2>&1")
    _nx_logs_h = _cmd("tail -n 50 /var/log/nginx/error.log 2>/dev/null || echo no-nginx-log")
    _nx_reload_h = _cmd("nginx -s reload 2>&1 && echo ok || echo fail")

    # ---- Site ----
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

    # ---- System ----
    async def _sys_mode_h(**kw):
        from state import state as _s
        return {"mode": _s.mode, "pending": len(_s.pending_approvals)}
    async def _sys_emergency_h(**kw):
        from state import state as _s
        _s.mode = "human_control"
        return {"mode": "human_control", "note": ''}

    # ---- Backup ----
    _backup_list_h = _import_handler_noargs("routers.rollback_center", "_load_backups")
    async def _backup_create_h(**kw):
        from routers.rollback_center import create_backup as _cb
        from pydantic import BaseModel
        class _BM(BaseModel): name: str = "auto"; type: str = "manual"; target: str = "database"
        return await _cb(_BM(**kw))
    async def _backup_rollback_h(**kw):
        from state import state as _s; from routers.rollback_center import _load_backups
        for r in _load_backups():
            if r.get("id") == kw.get("backup_id", ''):
                return {"status": "rollback_initiated", "backup": r["name"], "target": r.get("target", "unknown")}
        return {"error": "backup not found"}

    # ---- Rotation ----
    _rot_list_h = _state("rotation_domains", [])
    async def _rot_check_h(**kw):
        from routers.rotation_panel import _check_one
        return await _check_one({"domain": kw.get("domain", "unknown"), "type": kw.get("type", "web")})
    async def _rot_toggle_h(**kw):
        from state import state as _s
        domains = _s._data.setdefault("rotation_domains", [])
        for d in domains:
            if d["domain"] == kw.get("domain", ''):
                d["active"] = kw.get("active", not d.get("active", True))
                _s._save()
                return {"domain": d["domain"], "active": d["active"]}
        return {"error": "domain not found"}

    # ---- Customer ----
    async def _cust_msgs_h(**kw):
        from state import state as _s
        return _s._data.get("customer_messages", [])[-20:]
    async def _cust_reply_h(**kw):
        from state import state as _s
        msgs = _s._data.setdefault("customer_messages", [])
        msgs.append({"reply": kw.get("message", ''), "to": kw.get("user_id", ''), "time": __import__("datetime").datetime.now().isoformat()})
        _s._save()
        return {"ok": True, "replied_to": kw.get("user_id", '')}

    # ---- Mall/Shop ----
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

    # ---- Autopilot ----
    _auto_visit_h = _cmd("curl -sI https://example.com 2>/dev/null | head -5 || echo visit-simulated")
    _auto_schedule_h = _state("autopilot_schedule", {"status": "idle", "interval_min": 30})
    _auto_logs_h = _state("autopilot_logs", [])

    # ---- Report ----
    _report_daily_h = _import_handler_noargs("routers.daily_report", "generate_daily_report")
    async def _report_trend_h(**kw):
        from state import state as _s
        return {"recent_actions": _s.tasks[-20:]}

    # ---- DB ----
    async def _db_query_h(**kw):
        from executor import execute_db
        sql = kw.get("sql", "SHOW TABLES")
        return await execute_db(sql)
    _db_status_h = _cmd("mysqladmin ping 2>/dev/null -h localhost -u root || echo db-unreachable")
    _db_schema_h = _cmd("mysql -e 'SELECT TABLE_NAME,ENGINE,TABLE_ROWS FROM information_schema.TABLES WHERE TABLE_SCHEMA=\"mall_db\'' 2>/dev/null | head -30 || echo db-unreachable")
    _db_tables_h = _cmd("mysql -e 'SHOW TABLES' mall_db 2>/dev/null | head -30 || echo db-unreachable")

    # ---- Scraper ----
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

    # ---- Security ----
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

    # ---- Inspector ----
    async def _insp_run_h(**kw):
        from routers.inspector import run_inspection as _ri
        return await _ri() if _ri else {"status": "inspector"}
    async def _insp_history_h(**kw):
        from state import state as _s
        return _s._data.get("inspection_history", [])[-20:]

    # ---- Playwright ----
    async def _pw_screenshot_h(**kw):
        from agents.playwright_agent import PlaywrightAgent
        return await PlaywrightAgent.screenshot(kw.get("url", "https://example.com"))
    async def _pw_scrape_h(**kw):
        from agents.playwright_agent import PlaywrightAgent
        return await PlaywrightAgent.scrape_page(kw.get("url", "https://example.com"))
    async def _pw_search_h(**kw):
        from agents.playwright_agent import PlaywrightAgent
        return await PlaywrightAgent.search_and_scrape(kw.get("keyword", ''), kw.get("site", "ebay"))

    # ---- Virtual ----
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

    # ---- MallBrain ----
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
        return {"status": "Friday AI ", "total": r.total_products, "hot": r.hot_products, "dead": r.dead_products}

    # ---- Evolution ----
    async def _evo_report_h(**kw):
        from tools.evolution import EvolutionEngine
        return EvolutionEngine.evolve_report()
    _evo_history_h = _state("evolution_history", [])
    _evo_rate_h = _state("evolution_rates", {})
    async def _evo_learn_h(**kw):
        from tools.evolution import EvolutionEngine
        return EvolutionEngine.learn(kw.get("correction", ''), kw.get("context", ''))
    _evo_knowledge_h = _state("evolution_knowledge", [])

    # ---- Notification ----
    async def _notify_config_h(**kw):
        from state import state as _s
        return _s._data.get("notify_config", {"enabled": False, "channels": []})
    async def _notify_send_h(**kw):
        from routers.notify import send_notification
        return {"ok": True, "sent_to": kw.get("channel", "unknown"), "message": kw.get("message", '')[:50]}

    tools = [
        ToolDef("server.status", '', "CPU///", "L1", "server", handler=_srv_status_h),
        ToolDef("server.ports", '', '', "L1", "server", handler=_srv_ports_h),
        ToolDef("server.processes", '', "CPU", "L1", "server", handler=_srv_procs_h),
        ToolDef("server.disk", '', '', "L1", "server", handler=_srv_disk_h),

        ToolDef("docker.list", '', "Docker", "L1", "docker", handler=_dk_ps_h),
        ToolDef("docker.logs", '', '', "L1", "docker", params_schema={"container_id": {"type":"string"}}, handler=_dk_logs_h),
        ToolDef("docker.status", "Docker", "Docker", "L1", "docker", handler=_dk_status_h),
        ToolDef("docker.restart", '', "Docker", "L3", "docker", need_confirm=True, handler=_dk_restart_h),
        ToolDef("docker.images", '', "Docker", "L1", "docker", handler=_dk_images_h),
        ToolDef("docker.network", '', "Docker", "L1", "docker", handler=_dk_net_h),
        ToolDef("docker.stats", '', "CPU/", "L1", "docker", handler=_dk_stats_h),
        ToolDef("docker.compose", "Compose", "docker compose", "L1", "docker", handler=_dk_compose_h),

        ToolDef("nginx.status", "Nginx", "Nginx", "L1", "nginx", handler=_nx_status_h),
        ToolDef("nginx.test", "Nginx", "Nginx", "L1", "nginx", handler=_nx_test_h),
        ToolDef("nginx.logs", "Nginx", "Nginx/", "L1", "nginx", handler=_nx_logs_h),
        ToolDef("nginx.reload", "Nginx", "Nginx", "L3", "nginx", need_confirm=True, handler=_nx_reload_h),

        ToolDef("site.check", '', '', "L1", "site", params_schema={"url":{"type":"string"}}, handler=_site_check_h),
        ToolDef("site.ssl", "SSL", "SSL", "L1", "site", params_schema={"domain":{"type":"string"}}, handler=_site_ssl_h),
        ToolDef("site.dns", "DNS", '', "L1", "site", params_schema={"domain":{"type":"string"}}, handler=_site_dns_h),

        ToolDef("system.mode", '', '', "L1", "system", handler=_sys_mode_h),
        ToolDef("system.emergency", '', "Kill Switch", "L4", "system", need_confirm=True, handler=_sys_emergency_h),

        ToolDef("backup.list", '', '', "L1", "backup", handler=_backup_list_h),
        ToolDef("backup.create", '', "/", "L2", "backup", need_confirm=True, need_backup=True, handler=_backup_create_h),
        ToolDef("backup.rollback", '', '', "L4", "backup", need_confirm=True, rollback_supported=True, handler=_backup_rollback_h),
        ToolDef("backup.cleanup", '', '', "L2", "backup", need_confirm=True, handler=_import_handler_noargs("routers.rollback_center", "cleanup_old_backups")),

        ToolDef("rotation.list", '', '', "L1", "rotation", handler=_rot_list_h),
        ToolDef("rotation.check", '', '', "L1", "rotation", params_schema={"domain":{"type":"string"}}, handler=_rot_check_h),
        ToolDef("rotation.toggle", '', "/", "L3", "rotation", need_confirm=True, params_schema={"domain":{"type":"string"},"active":{"type":"boolean"}}, handler=_rot_toggle_h),

        ToolDef("customer.messages", '', '', "L1", "customer", handler=_cust_msgs_h),
        ToolDef("customer.reply", '', '', "L2", "customer", params_schema={"user_id":{"type":"string"},"message":{"type":"string"}}, handler=_cust_reply_h),

        ToolDef("mall.products", '', '', "L1", "mall", handler=_mall_products_h),
        ToolDef("mall.scan", '', '', "L1", "mall", handler=_mall_scan_h),

        ToolDef("autopilot.visit", '', '', "L1", "autopilot", handler=_auto_visit_h),
        ToolDef("autopilot.schedule", '', '', "L1", "autopilot", handler=_auto_schedule_h),
        ToolDef("autopilot.logs", '', '', "L1", "autopilot", handler=_auto_logs_h),

        ToolDef("report.daily", '', '', "L2", "report", handler=_report_daily_h),
        ToolDef("report.trend", '', '', "L1", "report", handler=_report_trend_h),

        ToolDef("db.status", '', '', "L1", "db", handler=_db_status_h),
        ToolDef("db.schema", '', '', "L1", "db", handler=_db_schema_h),
        ToolDef("db.query", "SQL", "SQL", "L2", "db", params_schema={"sql":{"type":"string"}}, handler=_db_query_h),
        ToolDef("db.tables", '', '', "L1", "db", handler=_db_tables_h),

        ToolDef("scraper.start", '', "eBay", "L2", "scraper", need_confirm=True, params_schema={"platform":{"type":"string"},"keyword":{"type":"string"}}, handler=_scraper_start_h),
        ToolDef("scraper.jobs", '', '', "L1", "scraper", handler=_scraper_jobs_h),
        ToolDef("scraper.products", '', '', "L1", "scraper", handler=_scraper_products_h),
        ToolDef("scraper.import", '', '', "L3", "scraper", need_confirm=True),

        ToolDef("security.block_ip", "IP", "IP", "L3", "security", need_confirm=True, params_schema={"ip":{"type":"string"}}, handler=_sec_block_h),
        ToolDef("security.unblock_ip", "IP", "IP", "L3", "security", need_confirm=True, params_schema={"ip":{"type":"string"}}, handler=_sec_unblock_h),

        ToolDef("inspector.run", '', '', "L2", "inspector", handler=_insp_run_h),
        ToolDef("inspector.history", '', '', "L1", "inspector", handler=_insp_history_h),

        ToolDef("playwright.screenshot", '', "URL", "L1", "playwright", params_schema={"url":{"type":"string"}}, handler=_pw_screenshot_h),
        ToolDef("playwright.scrape", '', '', "L1", "playwright", params_schema={"url":{"type":"string"}}, handler=_pw_scrape_h),
        ToolDef("playwright.search", '', "eBay/Amazon", "L2", "playwright", params_schema={"keyword":{"type":"string"},"site":{"type":"string"}}, handler=_pw_search_h),

        ToolDef("virtual.generate", '', "//", "L3", "virtual", need_confirm=True, handler=_virt_gen_h),
        ToolDef("virtual.realtime", '', '', "L2", "virtual", handler=_virt_realtime_h),
        ToolDef("virtual.dashboard", '', '', "L1", "virtual", handler=_virt_dashboard_h),
        ToolDef("virtual.stats", '', '', "L1", "virtual", handler=_state("virtual_stats", {})),

        ToolDef("mallbrain.scan", "AI", "AI", "L1", "brain", handler=_mb_scan_h),
        ToolDef("mallbrain.report", "AI", "AI", "L1", "brain", handler=_mb_report_h),
        ToolDef("mallbrain.auto", "AI", "AI", "L3", "brain", need_confirm=True, handler=_mb_auto_h),
        ToolDef("mallbrain.gaps", '', "AI", "L1", "brain", handler=_mb_gaps_h),
        ToolDef("mallbrain.summary", "AI", '', "L1", "brain", handler=_mb_summary_h),

        ToolDef("evolution.report", '', "AI", "L1", "evolution", handler=_evo_report_h),
        ToolDef("evolution.history", '', "AI", "L1", "evolution", handler=_evo_history_h),
        ToolDef("evolution.rate", '', "AI", "L1", "evolution", handler=_evo_rate_h),
        ToolDef("evolution.learn", '', "AI", "L2", "evolution", params_schema={"correction":{"type":"string"}}, handler=_evo_learn_h),
        ToolDef("evolution.knowledge", '', "AI", "L1", "evolution", handler=_evo_knowledge_h),

        ToolDef("notify.config", '', '', "L1", "notify", handler=_notify_config_h),
    ]

    for t in tools:
        registry.register(t)

    # ---- Desktop ----
    async def _desktop_list_h(**kw):
        from agents.desktop_agent import desktop_control
        return await desktop_control.list_desktops()
    async def _desktop_screenshot_h(**kw):
        from agents.desktop_agent import desktop_control
        return await desktop_control.screenshot(kw.get("agent_id"))
    async def _desktop_click_h(**kw):
        from agents.desktop_agent import desktop_control
        return await desktop_control.click(kw.get("x",0),kw.get("y",0),kw.get("button","left"),kw.get("agent_id"))
    async def _desktop_type_h(**kw):
        from agents.desktop_agent import desktop_control
        return await desktop_control.type_text(kw.get("text",''),kw.get("agent_id"))
    async def _desktop_keys_h(**kw):
        from agents.desktop_agent import desktop_control
        return await desktop_control.press_keys(kw.get("keys",[]),kw.get("agent_id"))
    async def _desktop_open_app_h(**kw):
        from agents.desktop_agent import desktop_control
        return await desktop_control.open_app(kw.get("app_path",''),kw.get("agent_id"))
    async def _desktop_open_url_h(**kw):
        from agents.desktop_agent import desktop_control
        return await desktop_control.open_url(kw.get("url","https://google.com"),kw.get("agent_id"))
    async def _desktop_windows_h(**kw):
        from agents.desktop_agent import desktop_control
        return await desktop_control.list_windows(kw.get("agent_id"))
    async def _desktop_focus_h(**kw):
        from agents.desktop_agent import desktop_control
        return await desktop_control.focus_window(kw.get("title_part",''),kw.get("agent_id"))
    async def _desktop_ocr_h(**kw):
        from agents.desktop_agent import desktop_control
        return await desktop_control.ocr_screen(kw.get("region"),kw.get("agent_id"))
    async def _desktop_move_h(**kw):
        from agents.desktop_agent import desktop_control
        return await desktop_control.move_mouse(kw.get("x",0),kw.get("y",0),kw.get("duration",0.3),kw.get("agent_id"))
    async def _desktop_scroll_h(**kw):
        from agents.desktop_agent import desktop_control
        return await desktop_control.scroll(kw.get("amount",3),kw.get("x"),kw.get("y"),kw.get("agent_id"))
    async def _desktop_drag_h(**kw):
        from agents.desktop_agent import desktop_control
        return await desktop_control.drag(kw.get("x1",0),kw.get("y1",0),kw.get("x2",100),kw.get("y2",100),kw.get("agent_id"))

    _desktop_tools = [
        ToolDef("notify.send", '', '', "L2", "notify", params_schema={"channel":{"type":"string"},"message":{"type":"string"}}, handler=_notify_send_h),
        ToolDef("desktop.list",'',"Agent","L1","desktop",handler=_desktop_list_h),
        ToolDef("desktop.screenshot",'','',"L1","desktop",params_schema={"agent_id":{"type":"string"}},handler=_desktop_screenshot_h),
        ToolDef("desktop.click",'','',"L2","desktop",need_confirm=True,params_schema={"x":{"type":"number"},"y":{"type":"number"}},handler=_desktop_click_h),
        ToolDef("desktop.type",'','',"L2","desktop",need_confirm=True,params_schema={"text":{"type":"string"}},handler=_desktop_type_h),
        ToolDef("desktop.keys",'',"ctrl+c","L2","desktop",need_confirm=True,params_schema={"keys":{"type":"array"}},handler=_desktop_keys_h),
        ToolDef("desktop.open_app",'','',"L2","desktop",need_confirm=True,params_schema={"app_path":{"type":"string"}},handler=_desktop_open_app_h),
        ToolDef("desktop.open_url",'',"URL","L1","desktop",params_schema={"url":{"type":"string"}},handler=_desktop_open_url_h),
        ToolDef("desktop.windows",'','',"L1","desktop",handler=_desktop_windows_h),
        ToolDef("desktop.focus",'','',"L2","desktop",need_confirm=True,params_schema={"title_part":{"type":"string"}},handler=_desktop_focus_h),
        ToolDef("desktop.ocr","OCR","OCR","L1","desktop",handler=_desktop_ocr_h),
        ToolDef("desktop.move",'','',"L2","desktop",need_confirm=True,params_schema={"x":{"type":"number"},"y":{"type":"number"}},handler=_desktop_move_h),
        ToolDef("desktop.scroll",'','',"L1","desktop",params_schema={"amount":{"type":"number"}},handler=_desktop_scroll_h),
        ToolDef("desktop.drag",'',"(x1,y1)(x2,y2)","L2","desktop",need_confirm=True,params_schema={"x1":{"type":"number"},"y1":{"type":"number"},"x2":{"type":"number"},"y2":{"type":"number"}},handler=_desktop_drag_h),
    ]

    for t in _desktop_tools:
        registry.register(t)
    return len(tools) + len(_desktop_tools)
