"""Friday AI OS -- Agent API"""
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
    ''"WebSocket -- Token''"
    client_id = "friday-console"
    # Token
    try:
        token_data = await ws.receive_text()
        try:
            payload = json.loads(token_data)
            token = payload.get("token", '')
        except Exception:
            token = token_data
        from auth import verify_jwt, AGENT_TOKEN
        authed = False
        if token.startswith("eyJ"):
            authed = verify_jwt(token) is not None
        elif token == AGENT_TOKEN:
            authed = True
        if not authed:
            await ws.send_text(json.dumps({"type": "error", "message": ''}))
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
                
                if client_id in ws_manager.connections:
                    ws_manager.connections[client_id]["last_heartbeat"] = __import__("time").time()
                continue
    except WebSocketDisconnect:
        await ws_manager.disconnect(ws, client_id)

# ===== Agent =====
@router.get("/agents")
async def list_agents(_=Depends(verify_token)):
    ''"Agent''"
    agents = MasterAgent.get_agent_status()
    # WebSocket
    await ws_manager.agent_status_update(agents)
    return {"ok": True, "agents": agents, "total": len(agents)}

# ===== Master Agent:  =====
class IntentRequest(BaseModel):
    message: str

@router.post("/intent")
async def analyze_intent(req: IntentRequest, _=Depends(verify_token)):
    ''''''
    result = MasterAgent.analyze_intent(req.message)
    return {"ok": True, **result}

# ===== Code Agent: / =====
@router.get("/code/analyze")
async def analyze_file(filepath: str, _=Depends(verify_token)):
    ''''''
    return await CodeAgent.analyze_file(filepath)

@router.get("/code/search")
async def search_code(directory: str, pattern: str, _=Depends(verify_token)):
    ''''''
    results = await CodeAgent.search_code(directory, pattern)
    return {"ok": True, "results": results, "count": len(results)}

class GenerateAPIRequest(BaseModel):
    name: str
    fields: list = []

@router.post("/code/generate-api")
async def generate_api(req: GenerateAPIRequest, _=Depends(verify_token)):
    ''"API''"
    code = await CodeAgent.generate_api(req.name, req.fields)
    return {"ok": True, "code": code}

# ===== Trend Agent:  =====
@router.get("/trends")
async def get_trends(platform: Optional[str] = None, _=Depends(verify_token)):
    ''''''
    return await TrendAgent.fetch_trends(platform)

@router.get("/trends/analyze")
async def analyze_trend(keyword: str, _=Depends(verify_token)):
    ''''''
    return await TrendAgent.analyze_trend(keyword)

@router.get("/trends/predict")
async def predict_hot(category: str = '', _=Depends(verify_token)):
    ''''''
    predictions = await TrendAgent.predict_hot(category)
    return {"ok": True, "category": category, "predictions": predictions}

# ===== Vision Agent =====
@router.get("/vision/analyze")
async def analyze_image(url: str, _=Depends(verify_token)):
    ''''''
    return await VisionAgent.analyze_image(image_url=url)

# ===== Multi-Model =====
@router.get("/models")
async def list_models(_=Depends(verify_token)):
    ''''''
    return {"ok": True, "models": await ModelRouter.list_models()}

@router.get("/models/route")
async def route_model(mode: str = "quality", _=Depends(verify_token)):
    ''''''
    try:
        m = ModelMode(mode)
    except ValueError:
        m = ModelMode.QUALITY
    config = ModelRouter.route(m)
    return {"ok": True, "mode": mode, "model": config.model_name, "provider": config.provider}

# ===== WebSocket =====

# ===== Playwright  =====
@router.post("/models/test")
async def test_model_speed(model_id: str, _=Depends(verify_token)):
    ''''''
    from agents.multi_model import ModelRouter
    start = __import__("time").time()
    try:
        resp = await ModelRouter.route(
            prompt=',"hello'',
            model_id=model_id or None
        )
        elapsed = round(__import__("time").time() - start, 2)
        return {"ok": True, "model_id": model_id or "auto", "latency_ms": round(elapsed * 1000), "response": str(resp)[:100]}
    except Exception as e:
        return {"ok": False, "error": str(e)}


@router.post("/models/compare")
async def compare_models(model_ids: list[str], _=Depends(verify_token)):
    ''''''
    from agents.multi_model import ModelRouter
    results = []
    for mid in model_ids[:3]:  # 3
        start = __import__("time").time()
        try:
            resp = await ModelRouter.route(prompt=''hello world'', model_id=mid)
            elapsed = round(__import__("time").time() - start, 2)
            results.append({"model_id": mid, "latency_ms": round(elapsed * 1000), "ok": True})
        except Exception as e:
            results.append({"model_id": mid, "ok": False, "error": str(e)})
    return {"ok": True, "results": results}


@router.post("/models/switch")
async def switch_active_model(model_id: str, _=Depends(verify_token)):
    ''''''
    from state import state
    state._data["active_model"] = model_id
    state._save()
    return {"ok": True, "active_model": model_id}


@router.get("/models/status")
async def model_status(_=Depends(verify_token)):
    ''''''
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
    return {"ok": True, "installed": installed, "note": "pip install playwright && playwright install chromium" if not installed else ''}

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

# =====  =====
@router.post("/collaborate")
async def agent_collaborate(goal: str = Query(...), _=Depends(verify_token)):
    ''"Agent: ->->->''"
    await handle_risk("L2", "Agent", goal[:100])
    result = await agent_collab.execute_all(goal)
    return result

@router.get("/lifeform/status")
async def lifeform_status(_=Depends(verify_token)):
    ''''''
    return DigitalLifeform.get_status()

@router.get("/lifeform/start")
async def lifeform_start(interval: int = 120, _=Depends(verify_token)):
    ''"/''"
    await DigitalLifeform.start_loop(interval)
    return {"ok": True, "interval": interval}

@router.get("/lifeform/stop")
async def lifeform_stop(_=Depends(verify_token)):
    ''''''
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
    return {"ok": True, "message": f": {req.category}/{req.key}"}
@router.post("/broadcast")
async def test_broadcast(message: str = "Friday AI OS ", _=Depends(verify_token)):
    await ws_manager.broadcast("test", {"message": message})
    return {"ok": True, "clients": ws_manager.count()}


# ===== Vision Agent: OCR/// =====
@router.get("/vision/ocr")
async def vision_ocr(image_url: str = Query(...), _=Depends(verify_token)):
    ''"OCR ''"
    return await VisionAgent.ocr_recognize(image_url)

@router.get("/vision/video")
async def vision_video(video_url: str = Query(...), _=Depends(verify_token)):
    ''''''
    return await VisionAgent.analyze_video(video_url=video_url)

@router.get("/vision/objects")
async def vision_objects(image_url: str = Query(...), _=Depends(verify_token)):
    ''''''
    return await VisionAgent.detect_objects(image_url)

@router.get("/vision/faces")
async def vision_faces(image_url: str = Query(...), _=Depends(verify_token)):
    ''''''
    return await VisionAgent.detect_faces(image_url)

@router.post("/vision/upload")
async def vision_upload(url: str = Query(''), file: bytes = None, _=Depends(verify_token)):
    ''"(URL)''"
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
    return {"ok": False, "error": "URL"}







