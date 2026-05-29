锘?""Dashboard WebSocket 鈥?瀹炴椂鎺ㄩ€佺郴缁熸寚鏍?鍛婅+璁㈠崟+鐢熷懡浣撶姸鎬?""
import asyncio, json
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from websocket_manager import ws_manager
from tools.logger import get_logger

logger = get_logger("ws_dashboard")
router = APIRouter()


@router.websocket("/ws/dashboard")
async def dashboard_websocket(ws: WebSocket):
    """Dashboard瀹炴椂鏁版嵁WebSocket"""
    client_id = f"dashboard_{id(ws)}"
    await ws_manager.connect(ws, client_id)

    # 棣栨鎺ㄩ€佸叏閲忔暟鎹?
    await ws_manager.push_system_metrics()

    try:
        while True:
            try:
                # 鎺ユ敹瀹㈡埛绔秷鎭紙蹇冭烦/ping锛?
                data = await asyncio.wait_for(ws.receive_text(), timeout=60)
                msg = json.loads(data) if data else {}
                msg_type = msg.get("type", "")

                if msg_type == "ping":
                    await ws.send_text(json.dumps({"type": "pong"}))
                elif msg_type == "get_metrics":
                    await ws_manager.push_system_metrics()
                elif msg_type == "get_lifeform":
                    await ws_manager.push_lifeform_status()

            except asyncio.TimeoutError:
                # 瓒呮椂涔熸帹閫佷竴娆℃暟鎹?
                await ws_manager.push_system_metrics()
                await ws.send_text(json.dumps({"type": "ping"}))

    except WebSocketDisconnect:
        pass
    except Exception as e:
        logger.info(f"Dashboard WS寮傚父: {e}")
    finally:
        await ws_manager.disconnect(ws, client_id)


@router.websocket("/ws/alerts")
async def alerts_websocket(ws: WebSocket):
    """鍛婅瀹炴椂鎺ㄩ€乄ebSocket"""
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
    """WebSocket杩炴帴缁熻"""
    return {"ok": True, "connections": ws_manager.count()}
