"""AI视频通话 API — WebRTC信令 + AI实时分析"""
import json, base64, asyncio
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from auth import verify_token
from tools.logger import get_logger

router = APIRouter(prefix="/agent/video", tags=["Video"])
logger = get_logger("video_call")

# 活跃通话房间
active_rooms: dict[str, dict] = {}

@router.websocket("/ws/{room_id}")
async def video_call_ws(ws: WebSocket, room_id: str, token: str = ""):
    """WebRTC信令 + AI实时帧分析"""
    if not token or not verify_token:
        await ws.accept()
        await ws.send_text(json.dumps({"type": "error", "message": "认证失败"}))
        await ws.close()
        return

    await ws.accept()
    if room_id not in active_rooms:
        active_rooms[room_id] = {"participants": [], "ai_analysis": []}
    active_rooms[room_id]["participants"].append(ws)

    try:
        while True:
            data = await asyncio.wait_for(ws.receive_text(), timeout=120)
            msg = json.loads(data)
            msg_type = msg.get("type", "")

            if msg_type == "offer" or msg_type == "answer" or msg_type == "ice-candidate":
                # 转发WebRTC信令给房间内其他人
                for peer in active_rooms.get(room_id, {}).get("participants", []):
                    if peer != ws:
                        try:
                            await peer.send_text(json.dumps(msg))
                        except:
                            pass

            elif msg_type == "analyze_frame":
                # AI分析视频帧(表情/情绪/动作)
                frame_b64 = msg.get("frame", "")
                if frame_b64:
                    try:
                        import httpx
                        from agents.multi_model import ModelRouter
                        resp = ModelRouter.smart_chat(messages=[{
                            "role": "user", "content": [
                                {"type": "text", "text": "分析这张人脸图片: 描述面部表情、情绪状态、是否在说话。用中文简短回复不超过30字。"},
                                {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{frame_b64}"}}
                            ]
                        }])
                        analysis = resp.get("content", "") if isinstance(resp, dict) else str(resp)
                        await ws.send_text(json.dumps({"type": "ai_analysis", "analysis": analysis, "ts": msg.get("ts", 0)}))
                    except Exception as e:
                        logger.info(f"帧分析失败: {e}")

            elif msg_type == "ai_avatar":
                # AI虚拟形象对话(3D智能体说话)
                text = msg.get("text", "")
                if text:
                    from agents.multi_model import ModelRouter
                    resp = ModelRouter.smart_chat(messages=[{"role": "user", "content": text}])
                    reply = resp.get("content", "") if isinstance(resp, dict) else str(resp)
                    await ws.send_text(json.dumps({"type": "ai_reply", "reply": reply, "ts": msg.get("ts", 0)}))

    except WebSocketDisconnect:
        pass
    except Exception as e:
        logger.info(f"视频通话异常: {e}")
    finally:
        if room_id in active_rooms:
            room = active_rooms[room_id]
            if ws in room.get("participants", []):
                room["participants"].remove(ws)
            if not room["participants"]:
                del active_rooms[room_id]