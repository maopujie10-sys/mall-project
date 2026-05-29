"""TikTokMall AI Agent 总控 - FastAPI :9000"""
import os
import random
import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, RedirectResponse
from tools.logger import setup_logging
from tools.rate_limiter import rate_limit_middleware
from tools.trace import trace_middleware
from config import AGENT_TOKEN, MALL_BASE_URL
from auth import verify_token, auth_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    print(f"[Agent] 启动中, 商城: {MALL_BASE_URL}")
    try:
        from scheduler import start_scheduler
        from digital_lifeform import DigitalLifeform
        start_scheduler()
        asyncio.create_task(DigitalLifeform.start_loop(300))
    except Exception as e:
        print(f"[Agent] 定时任务启动失败(非致命): {e}")
    try:
        from tools.memory_store import memory_store
        stats = memory_store.get_stats()
        conv_count = stats["total_conversations"]
        cat_count = len(memory_store.get_knowledge_categories())
        print(f"[Agent] 持久记忆已加载: {conv_count}段对话, {cat_count}个知识分类")
    except Exception as e:
        print(f"[Agent] 记忆加载失败(非致命): {e}")
    from tools.registry import register_builtin_tools
    register_builtin_tools()
    print("[Agent] 执行启动自检...")
    try:
        from startup import startup_self_check, startup_warmup
        check_result = await startup_self_check()
        summary = check_result["summary"]
        print(f"[Agent] 自检结果: {summary}")
        await startup_warmup()

        # Dashboard实时指标推送
        async def push_metrics_loop():
            from websocket_manager import ws_manager
            while True:
                await asyncio.sleep(10)
                try:
                    await ws_manager.push_system_metrics()
                except Exception:
                    pass
        asyncio.create_task(push_metrics_loop())
    except Exception as e:
        print(f"[Agent] 自检失败(非致命): {e}")
    yield
    print("[Agent] 关闭前同步记忆...")
    try:
        from tools.memory_sync import MemorySync
        push_result = MemorySync.sync_push()
        status = "OK" if push_result["success"] else "WARN"
        print(f"[Agent] 记忆同步: {status}")
    except Exception as e:
        print(f"[Agent] 记忆同步失败: {e}")
    try:
        from scheduler import stop_scheduler
        from digital_lifeform import DigitalLifeform
        stop_scheduler()
        await DigitalLifeform.stop_loop()
    except Exception:
        pass


app = FastAPI(title="TikTokMall Agent", version="1.1.0", lifespan=lifespan)

# === 中间件（顺序很重要：限流 → 追踪 → CORS） ===
app.middleware("http")(rate_limit_middleware)
app.middleware("http")(trace_middleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("CORS_ORIGINS", "*").split(","),
    allow_methods=["*"],
    allow_headers=["X-Agent-Token", "Content-Type", "Authorization"],
)

app.include_router(auth_router)

# === 路由模块 ===
from routers.vector_router import router as vector_router
from routers.backup_router import router as backup_router
from routers.copy_router import router as copy_router
from routers import (
    health, status, restart, virtual, security, scraper, notify,
    agent_chat, system_mode, server_panel, rotation_panel, rollback_center,
    customer_panel, mall_tools, nginx_panel, site_check, alert, inspector,
    task_queue, safety_api, mall_scanner, autopilot, ai_factory_router,
    batch_ops, sql_executor, daily_report, self_service, docker_panel,
    devops_agent_router, memory_router, heal_router,
)
from routers.virtual_data_router import router as virtual_data_router
from routers.mall_brain_router import router as mall_brain_router
from routers.evolution_router import router as evolution_router
from routers.friday_router import router as friday_router
from routers.github_router import router as github_router
from routers.lifeform_router import router as lifeform_router
from routers.workflow_router import router as workflow_router
from routers.user_auth_router import router as user_auth_router
from routers.inspect_router import router as inspect_router
from routers.knowledge_router import router as knowledge_router
from routers.competitor_router import router as competitor_router
from routers.plugin_router import router as plugin_router
from routers.ssl_router import router as ssl_router
from routers.scheduler_api import router as scheduler_api_router
from routers.weekly_report import router as weekly_report_router
from routers.log_manager import router as log_manager_router
from routers.archive_router import router as archive_router
from routers.customer_ai import router as customer_ai_router
from routers.observability import router as obs_router
from routers.db_router import router as db_router
from routers.audit_router import router as audit_router
from routers.network_router import router as network_router
from routers.settings_router import router as settings_router
from routers.dashboard_router import router as dashboard_router
from routers.notification_router import router as notification_router
from routers.phone_router import router as phone_router
from routers.image_router import router as image_router
from routers.translate_router import router as translate_router
from routers.excel_router import router as excel_router
from routers.auto_reply_router import router as auto_reply_router
from routers.order_alert_router import router as order_alert_router
# 新增: AI定价 + 请求追踪
from routers.pricing_router import router as pricing_router
from routers.description_router import router as description_router
from routers.fraud_router import router as fraud_router
from routers.trace_router import router as trace_router
from routers.ws_router import router as ws_router

# === 落地页轮值 ===
ROTATION_DOMAINS = [
    "chxhx.eu.cc", "drrgr.eu.cc", "drrimrf.eu.cc", "drriiu.eu.cc",
    "duomi.eu.cc", "dengruihan.eu.cc", "yyawzx.eu.cc", "gamed.eu.cc"
]

FLAG_ROUTES = {
    "pc": "/home", "spc": "/seller/", "ldy": "/partner", "admin": "/seller/"
}

@app.get("/api/r")
async def rotation_redirect(flag: str = "pc"):
    domain = random.choice(ROTATION_DOMAINS)
    path = FLAG_ROUTES.get(flag, "/home")
    return RedirectResponse(f"https://{domain}{path}", status_code=302)

# === 注册所有路由 ===
app.include_router(health.router)
app.include_router(status.router)
app.include_router(restart.router)
app.include_router(virtual.router)
app.include_router(security.router)
app.include_router(scraper.router)
app.include_router(notify.router)
app.include_router(agent_chat.router)
app.include_router(system_mode.router)
app.include_router(server_panel.router)
app.include_router(rotation_panel.router)
app.include_router(rollback_center.router)
app.include_router(customer_panel.router)
app.include_router(mall_tools.router)
app.include_router(nginx_panel.router)
app.include_router(site_check.router)
app.include_router(alert.router)
app.include_router(inspector.router)
app.include_router(task_queue.router)
app.include_router(safety_api.router)
app.include_router(mall_scanner.router)
app.include_router(autopilot.router)
app.include_router(ai_factory_router.router)
app.include_router(batch_ops.router)
app.include_router(sql_executor.router)
app.include_router(self_service.router)
app.include_router(docker_panel.router)
app.include_router(virtual_data_router)
app.include_router(mall_brain_router)
app.include_router(evolution_router)
app.include_router(friday_router)
app.include_router(devops_agent_router.router)
app.include_router(memory_router.router)
app.include_router(heal_router.router)
app.include_router(ssl_router)
app.include_router(scheduler_api_router)
app.include_router(weekly_report_router)
app.include_router(log_manager_router)
app.include_router(archive_router)
app.include_router(customer_ai_router)
app.include_router(obs_router)
app.include_router(db_router)
app.include_router(audit_router)
app.include_router(network_router)
app.include_router(settings_router)
app.include_router(dashboard_router)
app.include_router(daily_report.router)
app.include_router(notification_router)
app.include_router(phone_router)
app.include_router(image_router)
app.include_router(translate_router)
app.include_router(excel_router)
app.include_router(auto_reply_router)
app.include_router(order_alert_router)
app.include_router(plugin_router)
app.include_router(lifeform_router)
app.include_router(workflow_router)
app.include_router(user_auth_router)
app.include_router(inspect_router)
app.include_router(knowledge_router)
app.include_router(competitor_router)
app.include_router(vector_router)
app.include_router(backup_router)
app.include_router(copy_router)
app.include_router(github_router)
# 新增路由
app.include_router(pricing_router)
app.include_router(description_router)
app.include_router(fraud_router)
app.include_router(trace_router)
app.include_router(ws_router)

@app.get("/agent", include_in_schema=False)
async def dashboard():
    from fastapi.responses import HTMLResponse
    with open("templates/dashboard.html", encoding="utf-8") as f:
        return HTMLResponse(f.read())

@app.get("/agent/health")
async def agent_health():
    return {"status": "ok", "timestamp": __import__("datetime").datetime.now().isoformat()}