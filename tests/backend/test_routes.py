"""AI Agent """
import pytest, sys, os, json
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))

def test_health_router():
    """"""
    from routers.health import router
    routes = [r.path for r in router.routes]
    assert "/health" in routes, "health"

def test_agent_chat_router():
    """AI"""
    from routers.agent_chat import router
    routes = {r.path for r in router.routes}
    for p in ["/chat", "/tools", "/tasks", "/confirm", "/handover", "/models/status"]:
        assert p in routes, f"agent_chat {p} "

def test_rotation_router():
    """"""
    from routers.rotation_panel import router
    routes = {r.path for r in router.routes}
    for p in ["/domains", "/check-all", "/history", "/rotate", "/auto-discover"]:
        assert p in routes, f"rotation {p} "

def test_all_routers_registered():
    """44routermain.py"""
    import importlib, inspect
    from main import app
    registered = set()
    for route in app.routes:
        if hasattr(route, "path") and hasattr(route, "methods"):
            registered.add(route.path)
    # 
    for path in ["/health", "/agent/chat", "/rotation/domains", "/docker/ps", "/db/status",
                  "/nginx/status", "/memory/recall", "/agent/evolution/report", "/agent/friday/agents",
                  "/github/repo", "/agent/plugins/list", "/ssl/status", "/audit/stats",
                  "/agent/mall-brain/scan"]:
        assert path in registered, f" {path} "

def test_scheduler_tasks():
    """"""
    from scheduler import start_scheduler
    scheduler = start_scheduler()
    job_ids = [job.id for job in scheduler.get_jobs()]
    for jid in ["patrol", "backup", "rotation", "customer_report", "mall_scan", "ssl_renew", "metrics"]:
        assert jid in job_ids, f" {jid} "
