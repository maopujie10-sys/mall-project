"""Friday AI OS — Agent API路由"""
from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect
from pydantic import BaseModel
from typing import Optional
from risk import handle_risk
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
    client_id = "friday-console"
    await ws_manager.connect(ws, client_id)
    try:
        while True:
            data = await ws.receive_text()
            # 心跳保持
            if data == "ping":
                await ws.send_text('{"type":"pong"}')
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
    return {"ok": True, "models": ModelRouter.list_models()}

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
@router.post("/vision/ocr")
async def vision_ocr(url: str, _=Depends(verify_token)):
    """OCR 文字识别"""
    return await VisionAgent.ocr_recognize(url)

@router.post("/vision/video")
async def vision_video(video_url: str, _=Depends(verify_token)):
    """视频分析"""
    return await VisionAgent.analyze_video(video_url=video_url)

@router.post("/vision/objects")
async def vision_objects(image_url: str, _=Depends(verify_token)):
    """物体检测"""
    return await VisionAgent.detect_objects(image_url)

@router.post("/vision/faces")
async def vision_faces(image_url: str, _=Depends(verify_token)):
    """人脸检测"""
    return await VisionAgent.detect_faces(image_url)

@router.post("/vision/upload")
async def vision_upload(file: bytes = None, url: str = ""):
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



@router.post("/models/switch")
async def switch_model(model_id: str, _=Depends(verify_token)):
    """切换当前模型"""
    await handle_risk("L1", f"切换模型: {model_id}")
    state.current_model = model_id
    state._save()
    return {"ok": True, "current_model": model_id}

@router.post("/models/test")
async def test_model(model_id: str, _=Depends(verify_token)):
    """测试模型响应速度"""
    model = ModelRouter.get_model(model_id)
    if not model:
        return {"ok": False, "error": f"模型 {model_id} 不存在"}
    import time
    start = time.time()
    try:
        result = await model.test()
        latency = int((time.time() - start) * 1000)
        return {"ok": True, "model_id": model_id, "latency_ms": latency, "status": "ok"}
    except Exception as e:
        return {"ok": False, "model_id": model_id, "error": str(e)}

@router.post("/models/compare")
async def compare_models(model_ids: list[str], _=Depends(verify_token)):
    """对比多个模型"""
    results = []
    for mid in model_ids:
        model = ModelRouter.get_model(mid)
        if model:
            results.append({"model_id": mid, "name": model.name if hasattr(model, "name") else mid, "status": "available"})
        else:
            results.append({"model_id": mid, "status": "unavailable"})
    return {"ok": True, "comparison": results}

@router.get("/models/status")
async def model_status(_=Depends(verify_token)):
    """获取所有模型状态"""
    models = ModelRouter.list_models()
    current = getattr(state, "current_model", None)
    return {"ok": True, "models": models, "current": current}



