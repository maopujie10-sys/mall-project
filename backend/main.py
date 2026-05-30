"""TikTokMall AI Agent 鎬绘帶 - FastAPI :9000"""
from routers.code_deploy import router as code_deploy_router
from routers.emergency_panel import router as emergency_panel_router
from routers.prompt_templates import router as prompt_templates_router
from routers.semantic_search import router as semantic_search_router
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
    print(f"[Agent] 鍚姩涓? 鍟嗗煄: {MALL_BASE_URL}")
    try:
        from scheduler import start_scheduler
        from digital_lifeform import DigitalLifeform
        start_scheduler()
        asyncio.create_task(DigitalLifeform.start_loop(300))
    except Exception as e:
        print(f"[Agent] 瀹氭椂浠诲姟鍚姩澶辫触(闈炶嚧鍛?: {e}")
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
        print(f"[Agent] 鑷缁撴灉: {summary}")
        await startup_warmup()

        # Dashboard瀹炴椂鎸囨爣鎺ㄩ€?
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
        print(f"[Agent] 鑷澶辫触(闈炶嚧鍛?: {e}")
    yield
    print("[Agent] 鍏抽棴鍓嶅悓姝ヨ蹇?..")
    try:
        from tools.memory_sync import MemorySync
        push_result = MemorySync.sync_push()
        status = "OK" if push_result["success"] else "WARN"
        print(f"[Agent] 璁板繂鍚屾: {status}")
    except Exception as e:
        print(f"[Agent] 璁板繂鍚屾澶辫触: {e}")
    try:
        from scheduler import stop_scheduler
        from digital_lifeform import DigitalLifeform
        stop_scheduler()
        await DigitalLifeform.stop_loop()
    except Exception:
        pass


app = FastAPI(title="TikTokMall Agent", version="1.1.0", lifespan=lifespan)

# === 涓棿浠?椤哄簭寰堥噸瑕?闄愭祦 -> 杩借釜 -> CORS) ===
app.middleware("http")(rate_limit_middleware)
app.middleware("http")(trace_middleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("CORS_ORIGINS", "*").split(","),
    allow_methods=["*"],
    allow_headers=["X-Agent-Token", "Content-Type", "Authorization"],
)

app.include_router(auth_router, prefix="/auth")

# === 璺敱妯″潡 ===
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
# 鏂板: AI瀹氫环 + 璇锋眰杩借釜
from routers.pricing_router import router as pricing_router
from routers.description_router import router as description_router
from routers.fraud_router import router as fraud_router
from routers.trace_router import router as trace_router
from routers.ws_router import router as ws_router
from routers.gateway_router import router as gateway_router
from routers.omni_router import router as omni_router

# === 鍏ㄨ兘AI鍗囩骇 v5 ===
from routers.vision_router import router as vision_router
from routers.video_call_router import router as video_call_router
from routers.voice_router import router as voice_router
from routers.tools_router import router as tools_router
from routers.advanced_ai import router as advanced_router
from routers.collab_router import router as collab_router
from routers.rag_router import router as rag_router
from routers.predict_router import router as predict_router
from routers.recommend_router import router as recommend_router
from routers.content_router import router as content_router
from routers.sentiment_router import router as sentiment_router
from routers.text2sql_router import router as text2sql_router
from routers.abtest_router import router as abtest_router
from routers.security_scan_router import router as security_scan_router
from routers.capabilities_router import router as capabilities_router
from routers.key_router import router as key_router
from routers.wechat_admin import router as wechat_admin_router`nfrom routers.ecommerce_ai import router as ecommerce_ai_router
# === 钀藉湴椤佃疆鍊?===
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

# === 娉ㄥ唽鎵€鏈夎矾鐢?===
app.include_router(health.router)
app.include_router(status.router)
app.include_router(restart.router)
app.include_router(virtual.router)
app.include_router(security.router, prefix="/security")
app.include_router(scraper.router)
app.include_router(notify.router)
app.include_router(agent_chat.router, prefix="/chat")
app.include_router(system_mode.router)
app.include_router(server_panel.router)
app.include_router(rotation_panel.router)
app.include_router(rollback_center.router)
app.include_router(customer_panel.router, prefix="/customer-panel")
app.include_router(mall_tools.router)
app.include_router(nginx_panel.router, prefix="/nginx-panel")
app.include_router(site_check.router)
app.include_router(alert.router)
app.include_router(inspector.router, prefix="/inspector")
app.include_router(task_queue.router)
app.include_router(safety_api.router, prefix="/safety")
app.include_router(mall_scanner.router, prefix="/mall-scanner")
app.include_router(autopilot.router, prefix="/autopilot")
app.include_router(ai_factory_router.router, prefix="/ai-factory")
app.include_router(batch_ops.router, prefix="/batch")
app.include_router(sql_executor.router)
app.include_router(self_service.router)
app.include_router(docker_panel.router, prefix="/docker-panel")
app.include_router(virtual_data_router, prefix="/virtual-data")
app.include_router(mall_brain_router, prefix="/mall-brain")
app.include_router(evolution_router, prefix="/evolution")
app.include_router(friday_router, prefix="/friday")
app.include_router(devops_agent_router.router, prefix="/devops")
app.include_router(memory_router.router, prefix="/memory")
app.include_router(heal_router.router, prefix="/heal")
app.include_router(ssl_router, prefix="/ssl")
app.include_router(scheduler_api_router, prefix="/scheduler_api")
app.include_router(weekly_report_router, prefix="/weekly_report")
app.include_router(log_manager_router, prefix="/logs")
app.include_router(archive_router, prefix="/archive")
app.include_router(customer_ai_router, prefix="/customer")
app.include_router(obs_router, prefix="/obs")
app.include_router(db_router, prefix="/db")
app.include_router(audit_router, prefix="/audit")
app.include_router(network_router, prefix="/network")
app.include_router(settings_router, prefix="/settings")
app.include_router(dashboard_router, prefix="/dashboard")
app.include_router(daily_report.router)
app.include_router(notification_router, prefix="/notification")
app.include_router(phone_router, prefix="/phone")
app.include_router(image_router, prefix="/image")
app.include_router(translate_router, prefix="/translate")
app.include_router(excel_router, prefix="/excel")
app.include_router(auto_reply_router, prefix="/auto-reply")
app.include_router(order_alert_router, prefix="/order-alert")
app.include_router(plugin_router, prefix="/plugins")
app.include_router(lifeform_router, prefix="/lifeform")
app.include_router(workflow_router, prefix="/workflow")
app.include_router(user_auth_router, prefix="/user_auth")
app.include_router(inspect_router, prefix="/inspect")
app.include_router(knowledge_router, prefix="/knowledge")
app.include_router(competitor_router, prefix="/competitor")
app.include_router(vector_router, prefix="/vector")
app.include_router(backup_router, prefix="/backup")
app.include_router(copy_router, prefix="/copy")
app.include_router(github_router, prefix="/github")
# 鏂板璺敱
app.include_router(pricing_router, prefix="/pricing")
app.include_router(description_router, prefix="/description")
app.include_router(fraud_router, prefix="/fraud")
app.include_router(trace_router, prefix="/trace")
app.include_router(ws_router, prefix="/ws")
app.include_router(gateway_router, prefix="/api")
app.include_router(omni_router, prefix="/omni")
app.include_router(vision_router, prefix="/vision")
app.include_router(video_call_router, prefix="/video")
app.include_router(voice_router, prefix="/voice")
app.include_router(tools_router, prefix="/tools")
app.include_router(advanced_router, prefix="/advanced")
app.include_router(collab_router, prefix="/collab")
app.include_router(rag_router, prefix="/rag")
app.include_router(predict_router, prefix="/predict")
app.include_router(recommend_router, prefix="/recommend")
app.include_router(content_router, prefix="/content")
app.include_router(sentiment_router, prefix="/sentiment")
app.include_router(text2sql_router, prefix="/text2sql")
app.include_router(abtest_router, prefix="/abtest")
app.include_router(security_scan_router, prefix="/security_scan")
app.include_router(capabilities_router, prefix="/capabilities")
app.include_router(key_router, prefix="/keys")
app.include_router(wechat_admin_router, prefix="/agent/wechat")`napp.include_router(ecommerce_ai_router, prefix="/ecommerce_ai")

app.include_router(code_deploy_router, prefix="/agent/deploy")
app.include_router(emergency_panel_router, prefix="/agent/emergency")
app.include_router(prompt_templates_router, prefix="/prompt_templates")
app.include_router(semantic_search_router, prefix="/semantic_search")
@app.get("/agent", include_in_schema=False)
async def dashboard():
    from fastapi.responses import HTMLResponse
    with open("templates/dashboard.html", encoding="utf-8") as f:
        return HTMLResponse(f.read())

@app.get("/agent/health")
async def agent_health():
    return {"status": "ok", "timestamp": __import__("datetime").datetime.now().isoformat()}
