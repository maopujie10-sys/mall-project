''"Dashboard WebSocket -- +++''"
import asyncio, json
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from websocket_manager import ws_manager
from tools.logger import get_logger

logger = get_logger("ws_dashboard")
router = APIRouter()


@router.websocket("/ws/dashboard")
async def dashboard_websocket(ws: WebSocket):
    ''"DashboardWebSocket''"
    client_id = f"dashboard_{id(ws)}"
    await ws_manager.connect(ws, client_id)

    
    await ws_manager.push_system_metrics()

    try:
        while True:
            try:
                # (/ping)
                data = await asyncio.wait_for(ws.receive_text(), timeout=60)
                msg = json.loads(data) if data else {}
                msg_type = msg.get("type", '')

                if msg_type == "ping":
                    await ws.send_text(json.dumps({"type": "pong"}))
                elif msg_type == "get_metrics":
                    await ws_manager.push_system_metrics()
                elif msg_type == "get_lifeform":
                    await ws_manager.push_lifeform_status()

            except asyncio.TimeoutError:
                
                await ws_manager.push_system_metrics()
                await ws.send_text(json.dumps({"type": "ping"}))

    except WebSocketDisconnect:
        pass
    except Exception as e:
        logger.info(f"Dashboard WS: {e}")
    finally:
        await ws_manager.disconnect(ws, client_id)


@router.websocket("/ws/alerts")
async def alerts_websocket(ws: WebSocket):
    ''"WebSocket''"
    client_id = f"alerts_{id(ws)}"
    await ws_manager.connect(ws, client_id)

    try:
        while True:
            try:
                data = await asyncio.wait_for(ws.receive_text(), timeout=60)
                if data and json.loads(data).get("type") == "ping":
                    await ws.send_text(json.dumps({"type": "pong"}))
            except asyncio.TimeoutError:
                await ws.send_text(json.dumps({"type": "ping"}))
    except WebSocketDisconnect:
        pass
    finally:
        await ws_manager.disconnect(ws, client_id)


@router.get("/ws/stats")
async def ws_stats():
    ''"WebSocket''"
    return {"ok": True, "connections": ws_manager.count()}

# ===== Desktop Control WebSocket =====

@router.websocket("/ws/desktop")
async def desktop_websocket(ws: WebSocket):
    ''"WebSocket -- desktop_agent_local.py''"
    from agents.desktop_agent import desktop_control
    agent_id = ws.headers.get("x-agent-id", f"desktop_{id(ws)}")
    token = ws.headers.get("authorization", '').replace("Bearer ", '')
    from auth import verify_token_raw
    if not verify_token_raw(token):
        await ws.accept()
        await ws.send_text(json.dumps({"type": "error", "message": ''}))
        await ws.close()
        return
    await desktop_control.connect(ws, agent_id)
    try:
        while True:
            try:
                data = await asyncio.wait_for(ws.receive_text(), timeout=60)
                msg = json.loads(data) if data else {}
                await desktop_control.handle_message(agent_id, msg)
            except asyncio.TimeoutError:
                await ws.send_text(json.dumps({"type": "ping"}))
    except WebSocketDisconnect:
        pass
    except Exception as e:
        logger.info(f"Desktop WS: {e}")
    finally:
        await desktop_control.disconnect(agent_id)
