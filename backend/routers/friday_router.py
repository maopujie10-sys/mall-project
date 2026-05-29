"""Friday AI OS — Agent API路由"""
from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect, Query
from pydantic import BaseModel
from typing import Optional
from risk import handle_risk
from tools.agent_collab import agent_collab
from state import state
from auth import verify_token
from agents.master_agent import MasterAgent
from agents.code_agent import CodeAgent
from agents.trend_agent import TrendAgent
from agents.vision_agent import VisionAgent
from agents.multi_model import ModelRouter, ModelMode
from websocket_manager import ws_manager
from agents.playwright_agent import PlaywrightAgent
from tools.memory_personality import PersonalityEngine

router = APIRouter(prefix="/agent/friday", tags=["Friday AI OS"])

# ===== WebSocket =====
@router.websocket("/ws")
async def friday_websocket(ws: WebSocket):
    """WebSocket入口 — 先验证Token再建立连接"""
    client_id = "friday-console"
    # 首次消息必须是Token验证
    try:
        token_data = await ws.receive_text()
        try:
            payload = json.loads(token_data)
            token = payload.get("token", "")
        except Exception:
            token = token_data
        from auth import verify_jwt, AGENT_TOKEN
        authed = False
        if token.startswith("eyJ"):
            authed = verify_jwt(token) is not None
        elif token == AGENT_TOKEN:
            authed = True
        if not authed:
            await ws.send_text(json.dumps({"type": "error", "message": "认证失败"}))
            await ws.close()
            return
        await ws.send_text(json.dumps({"type": "auth_ok"}))
    except Exception:
        await ws.close()
        return
    await ws_manager.connect(ws, client_id)
    try:
        while True:
            data = await ws.receive_text()
            if data == "ping" or data == "pong":
                # 更新心跳时间
                if client_id in ws_manager.connections:
                    ws_manager.connections[client_id]["last_heartbeat"] = __import__("time").time()
                continue
    except WebSocketDisconnect:
        await ws_manager.disconnect(ws, client_id)

# ===== Agent状态 =====
@router.get("/agents")
async def list_agents(_=Depends(verify_token)):
    """获取所有Agent状态"""
    agents = MasterAgent.get_agent_status()
    # 推送状态给所有WebSocket客户端
    await ws_manager.agent_status_update(agents)
    return {"ok": True, "agents": agents, "total": len(agents)}

# ===== Master Agent: 意图分析 =====
class IntentRequest(BaseModel):
    message: str

@router.post("/intent")
async def analyze_intent(req: IntentRequest, _=Depends(verify_token)):
    """分析用户意图"""
    result = MasterAgent.analyze_intent(req.message)
    return {"ok": True, **result}

# ===== Code Agent: 代码分析/搜索 =====
@router.get("/code/analyze")
async def analyze_file(filepath: str, _=Depends(verify_token)):
    """分析代码文件"""
    return await CodeAgent.analyze_file(filepath)

@router.get("/code/search")
async def search_code(directory: str, pattern: str, _=Depends(verify_token)):
    """搜索代码"""
    results = await CodeAgent.search_code(directory, pattern)
    return {"ok": True, "results": results, "count": len(results)}

class GenerateAPIRequest(BaseModel):
    name: str
    fields: list = []

@router.post("/code/generate-api")
async def generate_api(req: GenerateAPIRequest, _=Depends(verify_token)):
    """生成API代码"""
    code = await CodeAgent.generate_api(req.name, req.fields)
    return {"ok": True, "code": code}

# ===== Trend Agent: 热点 =====
@router.get("/trends")
async def get_trends(platform: Optional[str] = None, _=Depends(verify_token)):
    """获取热点数据"""
    return await TrendAgent.fetch_trends(platform)

@router.get("/trends/analyze")
async def analyze_trend(keyword: str, _=Depends(verify_token)):
    """分析趋势"""
    return await TrendAgent.analyze_trend(keyword)

@router.get("/trends/predict")
async def predict_hot(category: str = "科技", _=Depends(verify_token)):
    """预测热门"""
    predictions = await TrendAgent.predict_hot(category)
    return {"ok": True, "category": category, "predictions": predictions}

# ===== Vision Agent =====
@router.get("/vision/analyze")
async def analyze_image(url: str, _=Depends(verify_token)):
    """分析图片"""
    return await VisionAgent.analyze_image(image_url=url)

# ===== Multi-Model =====
@router.get("/models")
async def list_models(_=Depends(verify_token)):
    """列出所有模型"""
    return {"ok": True, "models": await ModelRouter.list_models()}

@router.get("/models/route")
async def route_model(mode: str = "quality", _=Depends(verify_token)):
    """智能路由选择模型"""
    try:
        m = ModelMode(mode)
    except ValueError:
        m = ModelMode.QUALITY
    config = ModelRouter.route(m)
    return {"ok": True, "mode": mode, "model": config.model_name, "provider": config.provider}

# ===== WebSocket广播测试 =====

# ===== Playwright 浏览器自动化 =====
@router.post("/models/test")
async def test_model_speed(model_id: str, _=Depends(verify_token)):
    """测试模型响应速度"""
    from agents.multi_model import ModelRouter
    start = __import__("time").time()
    try:
        resp = await ModelRouter.route(
            prompt='你好，请回复"hello"测试响应速度',
            model_id=model_id or None
        )
        elapsed = round(__import__("time").time() - start, 2)
        return {"ok": True, "model_id": model_id or "auto", "latency_ms": round(elapsed * 1000), "response": str(resp)[:100]}
    except Exception as e:
        return {"ok": False, "error": str(e)}


@router.post("/models/compare")
async def compare_models(model_ids: list[str], _=Depends(verify_token)):
    """对比多个模型"""
    from agents.multi_model import ModelRouter
    results = []
    for mid in model_ids[:3]:  # 最多比3个
        start = __import__("time").time()
        try:
            resp = await ModelRouter.route(prompt='回复"hello world"', model_id=mid)
            elapsed = round(__import__("time").time() - start, 2)
            results.append({"model_id": mid, "latency_ms": round(elapsed * 1000), "ok": True})
        except Exception as e:
            results.append({"model_id": mid, "ok": False, "error": str(e)})
    return {"ok": True, "results": results}


@router.post("/models/switch")
async def switch_active_model(model_id: str, _=Depends(verify_token)):
    """切换当前使用的模型"""
    from state import state
    state._data["active_model"] = model_id
    state._save()
    return {"ok": True, "active_model": model_id}


@router.get("/models/status")
async def model_status(_=Depends(verify_token)):
    """获取模型状态"""
    from agents.multi_model import ModelRouter
    return {
        "ok": True,
        "active_model": ModelRouter.get_config().get("default_model", "auto"),
        "available_models": list(ModelRouter.get_config().get("models", {}).keys()),
        "mode": "auto",
    }
@router.get("/playwright/status")
async def playwright_status(_=Depends(verify_token)):
    installed = await PlaywrightAgent.check_installed()
    return {"ok": True, "installed": installed, "note": "pip install playwright && playwright install chromium" if not installed else ""}

@router.get("/playwright/screenshot")
async def take_screenshot(url: str, _=Depends(verify_token)):
    result = await PlaywrightAgent.screenshot(url)
    return result

@router.get("/playwright/scrape")
async def scrape_page(url: str, _=Depends(verify_token)):
    result = await PlaywrightAgent.scrape_page(url)
    return result

@router.get("/playwright/search")
async def search_products(keyword: str, site: str = "ebay", _=Depends(verify_token)):
    result = await PlaywrightAgent.search_and_scrape(keyword, site)
    return result

# ===== 记忆人格 =====
@router.post("/collaborate")
async def agent_collaborate(goal: str = Query(...), _=Depends(verify_token)):
    """多Agent协作: 分析目标->拆解任务->并行执行->汇总结果"""
    await handle_risk("L2", "多Agent协作", goal[:100])
    result = await agent_collab.execute_all(goal)
    return result

@router.get("/lifeform/status")
async def lifeform_status(_=Depends(verify_token)):
    """数字生命体状态"""
    return DigitalLifeform.get_status()

@router.get("/lifeform/start")
async def lifeform_start(interval: int = 120, _=Depends(verify_token)):
    """启动/重启生命体"""
    await DigitalLifeform.start_loop(interval)
    return {"ok": True, "interval": interval}

@router.get("/lifeform/stop")
async def lifeform_stop(_=Depends(verify_token)):
    """停止生命体"""
    return await DigitalLifeform.stop_loop()

@router.get("/personality")
async def get_personality(_=Depends(verify_token)):
    return {"ok": True, **PersonalityEngine.get_personality()}

@router.get("/journal")
async def get_journal(days: int = 7, _=Depends(verify_token)):
    journals = PersonalityEngine.get_journal_history(days)
    return {"ok": True, "journals": journals, "count": len(journals)}

@router.post("/journal/generate")
async def generate_journal(_=Depends(verify_token)):
    journal = PersonalityEngine.generate_daily_journal()
    return {"ok": True, "journal": journal}

@router.get("/handoff")
async def get_handoff(_=Depends(verify_token)):
    handoff = PersonalityEngine.generate_handoff()
    return {"ok": True, "handoff": handoff}

@router.get("/context")
async def get_context(category: str = None, _=Depends(verify_token)):
    items = PersonalityEngine.get_context(category)
    return {"ok": True, "items": items, "count": len(items)}

class RememberRequest(BaseModel):
    category: str
    key: str
    value: str
    importance: float = 0.5

@router.post("/remember")
async def remember_something(req: RememberRequest, _=Depends(verify_token)):
    PersonalityEngine.remember(req.category, req.key, req.value, req.importance)
    return {"ok": True, "message": f"已记住: {req.category}/{req.key}"}
@router.post("/broadcast")
async def test_broadcast(message: str = "Friday AI OS 在线", _=Depends(verify_token)):
    await ws_manager.broadcast("test", {"message": message})
    return {"ok": True, "clients": ws_manager.count()}


# ===== Vision Agent: OCR/视频/物体/人脸 =====
@router.get("/vision/ocr")
async def vision_ocr(image_url: str = Query(...), _=Depends(verify_token)):
    """OCR 文字识别"""
    return await VisionAgent.ocr_recognize(image_url)

@router.get("/vision/video")
async def vision_video(video_url: str = Query(...), _=Depends(verify_token)):
    """视频分析"""
    return await VisionAgent.analyze_video(video_url=video_url)

@router.get("/vision/objects")
async def vision_objects(image_url: str = Query(...), _=Depends(verify_token)):
    """物体检测"""
    return await VisionAgent.detect_objects(image_url)

@router.get("/vision/faces")
async def vision_faces(image_url: str = Query(...), _=Depends(verify_token)):
    """人脸检测"""
    return await VisionAgent.detect_faces(image_url)

@router.post("/vision/upload")
async def vision_upload(url: str = Query(""), file: bytes = None, _=Depends(verify_token)):
    """上传图片并分析（支持文件上传或URL）"""
    if url:
        return await VisionAgent.analyze_image(image_url=url)
    if file:
        import tempfile, os, base64
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".jpg")
        tmp.write(file)
        tmp.close()
        try:
            result = await VisionAgent.analyze_image(image_path=tmp.name)
            return result
        finally:
            os.unlink(tmp.name)
    return {"ok": False, "error": "请提供图片URL或上传文件"}







