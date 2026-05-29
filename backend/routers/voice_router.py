"""语音对话 WebSocket — 实时音频→STT→LLM→TTS"""
import json, base64, asyncio
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, Query
from tools.logger import get_logger

router = APIRouter(prefix="/agent/voice", tags=["Voice"])
logger = get_logger("voice")

@router.websocket("/ws")
async def voice_websocket(ws: WebSocket):
    """实时语音对话WebSocket"""
    await ws.accept()
    logger.info("语音WebSocket已连接")
    
    try:
        while True:
            data = await ws.receive_json()
            msg_type = data.get("type", "")
            
            if msg_type == "ping":
                await ws.send_json({"type": "pong"})
                continue
            
            if msg_type == "voice":
                audio_b64 = data.get("audio_b64", "")
                fmt = data.get("fmt", "webm")
                
                # 状态: 正在处理
                await ws.send_json({"type": "status", "message": "正在识别语音..."})
                
                # 调用AI处理语音消息
                try:
                    from routers.agent_chat import agent_chat, ChatRequest
                    # 将音频作为文本消息处理（浏览器端做STT）
                    text = data.get("text", "")
                    if not text:
                        # 没有文本则用音频base64作为消息
                        text = "[语音消息]"
                    
                    await ws.send_json({"type": "user_text", "text": text})
                    await ws.send_json({"type": "status", "message": "AI思考中..."})
                    
                    result = await agent_chat(ChatRequest(message=text, history=[]))
                    reply = result.get("response", "收到")
                    
                    await ws.send_json({"type": "reply_text", "text": reply})
                    await ws.send_json({"type": "status", "message": "生成语音..."})
                    
                    # 生成TTS音频（使用浏览器端speechSynthesis，这里返回文本即可）
                    await ws.send_json({
                        "type": "voice_reply",
                        "text": reply,
                        "audio_b64": None  # 浏览器端用speechSynthesis朗读
                    })
                    
                except Exception as e:
                    logger.error(f"语音处理错误: {e}")
                    await ws.send_json({"type": "error", "message": f"处理失败: {str(e)}"})
            
            elif msg_type == "text":
                # 纯文本模式
                text = data.get("text", "")
                await ws.send_json({"type": "user_text", "text": text})
                await ws.send_json({"type": "status", "message": "AI思考中..."})
                
                try:
                    from routers.agent_chat import agent_chat, ChatRequest
                    result = await agent_chat(ChatRequest(message=text, history=[]))
                    reply = result.get("response", "收到")
                    await ws.send_json({"type": "reply_text", "text": reply})
                    await ws.send_json({"type": "voice_reply", "text": reply, "audio_b64": None})
                except Exception as e:
                    await ws.send_json({"type": "error", "message": str(e)})
                    
    except WebSocketDisconnect:
        logger.info("语音WebSocket断开")
    except Exception as e:
        logger.error(f"语音WebSocket异常: {e}")
        try:
            await ws.send_json({"type": "error", "message": str(e)})
        except:
            pass