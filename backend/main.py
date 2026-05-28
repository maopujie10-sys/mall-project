"""TikTokMall AI Agent 总控 - FastAPI :9000"""
import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from config import AGENT_TOKEN, MALL_BASE_URL
from auth import verify_token

@asynccontextmanager
async def lifespan(app: FastAPI):
    print(f"[Agent] 启动中, 商城: {MALL_BASE_URL}")
    # 启动定时任务 + 数字生命体(含进化)
    try:
        from scheduler import start_scheduler
        from digital_lifeform import DigitalLifeform
        start_scheduler()
        # 启动数字生命体自主循环(每5分钟, 含进化)
        asyncio.create_task(DigitalLifeform.start_loop(300))
    except Exception as e:
        print(f"[Agent] 定时任务启动失败(非致命): {e}")
    # 加载持久记忆 + 注册内置工具
    try:
        from tools.memory_store import memory_store
        from digital_lifeform import DigitalLifeform
        stats = memory_store.get_stats()
        print(f"[Agent] 持久记忆已加载: {stats[\"total_conversations\"]}段对话, {len(memory_store.get_knowledge_categories())}个知识分类")
    except Exception as e:
        print(f"[Agent] 记忆加载失败(非致命): {e}")
    # 注册内置工具
    from tools.registry import register_builtin_tools
    register_builtin_tools()
    # 启动自检 + 长期记忆预热
    print("[Agent] 执行启动自检...")
    try:
        from startup import startup_self_check, startup_warmup
        check_result = await startup_self_check()
        print(f"[Agent] 自检结果: {check_result['summary']}")
        await startup_warmup()
    except Exception as e:
        print(f"[Agent] 自检失败(非致命): {e}")
    yield
    # 停止定时任务 + 数字生命体
    print("[Agent] 关闭前同步记忆...")
    try:
        from tools.memory_sync import MemorySync
        push_result = MemorySync.sync_push()
        print(f"[Agent] 记忆同步: {'OK' if push_result['success'] else 'WARN'}")
    except Exception as e:
        print(f"[Agent] 记忆同步失败: {e}")
    try:
        from scheduler import stop_scheduler
        from digital_lifeform import DigitalLifeform
        stop_scheduler()
        asyncio.create_task(DigitalLifeform.stop_loop())
    except Exception:
        pass

app = FastAPI(title="TikTokMall Agent", version="1.0.0", lifespan=lifespan)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["X-Agent-Token", "Content-Type"],
)

# 注册路由模块
from routers.virtual_data_router import router as virtual_data_router
from routers.mall_brain_router import router as mall_brain_router
from routers.evolution_router import router as evolution_router
from routers.friday_router import router as friday_router
from routers.devops_agent_router import router as devops_router
from routers.memory_router import router as memory_router
from routers.heal_router import router as heal_router
from routers.github_router import router as github_router
from routers.plugin_router import router as plugin_router
from routers import (
    health, status, restart, virtual, security, scraper, notify,
    agent_chat, system_mode, server_panel, rotation_panel, rollback_center,
    customer_panel, mall_tools,
    nginx_panel, site_check, alert, inspector, task_queue, safety_api,
    mall_scanner, autopilot, ai_factory_router, batch_ops, sql_executor,
    daily_report, self_service, docker_panel, devops_agent_router, memory_router, heal_router,
)

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
app.include_router(daily_report.router)
app.include_router(self_service.router)
app.include_router(docker_panel.router)
app.include_router(virtual_data_router)
app.include_router(mall_brain_router)
app.include_router(evolution_router)
app.include_router(friday_router)
app.include_router(devops_router)
app.include_router(memory_router)
app.include_router(heal_router)
app.include_router(plugin_router)
app.include_router(github_router)

# 内嵌HTML仪表盘
@app.get("/agent", include_in_schema=False)
async def dashboard():
    from fastapi.responses import HTMLResponse
    with open("templates/dashboard.html", encoding="utf-8") as f:
        return HTMLResponse(f.read())

@app.get("/agent/health")
async def agent_health():
    return {"status": "ok", "timestamp": __import__("datetime").datetime.now().isoformat()}




