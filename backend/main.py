"""TikTokMall AI Agent — FastAPI :9000"""
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from config import AGENT_TOKEN, MALL_BASE_URL

@asynccontextmanager
async def lifespan(app: FastAPI):
    print(f"[Agent] 启动完成, 商城: {MALL_BASE_URL}")
    yield
    print("[Agent] 关闭")

app = FastAPI(title="TikTokMall Agent", version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Token鉴权 ──
async def verify_token(request: Request):
    token = request.headers.get("X-Agent-Token", "")
    if token != AGENT_TOKEN:
        raise HTTPException(status_code=403, detail="Invalid agent token")

# ── 注册路由 ──
from routers import health, status, restart, virtual, security, scraper, notify, agent_chat, system_mode, server_panel, rotation_panel, rollback_center, customer_panel, mall_tools

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

# ── 仪表盘HTML ──
@app.get("/agent", include_in_schema=False)
async def dashboard():
    from fastapi.responses import HTMLResponse
    with open("templates/dashboard.html") as f:
        return HTMLResponse(f.read())
