閿?""Friday AI OS 閳?WebSocket鐎圭偞妞傞幒銊┾偓浣侯吀閻炲棗娅?
v2: 韫囧啳鐑﹀Λ鈧ù?+ 閼奉亜濮╁〒鍛倞閺傤叀绻?+ 鏉╃偞甯撮弫棰佺瑐闂?+ 濞戝牊浼呴梼鐔峰灙"""
import asyncio
import json
from datetime import datetime
from fastapi import WebSocket
from typing import Dict, Set, Optional

MAX_CONNECTIONS = 100
HEARTBEAT_INTERVAL = 30  # 30s閺冪姵绉烽幁顖氬灟Ping
DISCONNECT_TIMEOUT = 120  # 120s閺冪嚛ong閸掓瑦鏌囧鈧?


class WSManager:
    """WebSocket鏉╃偞甯寸粻锛勬倞閸?""

    def __init__(self):
        self.connections: Dict[str, Dict[str, any]] = {}  # client_id -> {sockets, last_heartbeat}
        self._running = False
        self._heartbeat_task: Optional[asyncio.Task] = None

    def _start_heartbeat(self):
        """閸氼垰濮╅崥搴″酱韫囧啳鐑﹀Λ鈧ù?""
        if self._running:
            return
        self._running = True
        self._heartbeat_task = asyncio.create_task(self._heartbeat_loop())

    async def _heartbeat_loop(self):
        """鐎规碍妞傝箛鍐儲濡偓濞村鎯婇悳?""
        while self._running:
            await asyncio.sleep(HEARTBEAT_INTERVAL)
            now = datetime.now().timestamp()
            dead = []
            for cid, info in self.connections.items():
                for ws in list(info.get("sockets", set())):
                    try:
                        await ws.send_text(json.dumps({"type": "ping"}))
                    except Exception:
                        dead.append((cid, ws))
                    # 濡偓閺屻儲娓堕崥搴＄妇鐠鸿櫕妞傞梻?
                    last = info.get("last_heartbeat", 0)
                    if now - last > DISCONNECT_TIMEOUT:
                        dead.append((cid, ws))
            for cid, ws in dead:
                await self.disconnect(ws, cid)

    async def connect(self, ws: WebSocket, client_id: str = "default"):
        await ws.accept()
        # 鏉╃偞甯撮弫棰佺瑐闂勬劖顥呴弻?
        total = self.count()
        if total >= MAX_CONNECTIONS:
            await ws.send_text(json.dumps({"type": "error", "message": "鏉╃偞甯撮弫鏉垮嚒濠?}))
            await ws.close()
            return

        if client_id not in self.connections:
            self.connections[client_id] = {"sockets": set(), "last_heartbeat": datetime.now().timestamp()}
        self.connections[client_id]["sockets"].add(ws)
        self.connections[client_id]["last_heartbeat"] = datetime.now().timestamp()
        self._start_heartbeat()
        await self.broadcast("system", {"type": "connected", "clients": self.count()})

    async def disconnect(self, ws: WebSocket, client_id: str = "default"):
        info = self.connections.get(client_id)
        if info:
            info["sockets"].discard(ws)
            if not info["sockets"]:
                del self.connections[client_id]

    def count(self) -> int:
        return sum(len(info.get("sockets", set())) for info in self.connections.values())

    async def broadcast(self, event_type: str, data: dict):
        """楠炴寧鎸卞☉鍫熶紖閸掔増澧嶉張澶庣箾閹?""
        message = json.dumps({
            "type": event_type, "data": data,
            "timestamp": datetime.now().isoformat(),
        }, ensure_ascii=False)
        dead = []
        for cid, info in list(self.connections.items()):
            for ws in list(info.get("sockets", set())):
                try:
                    await ws.send_text(message)
                except Exception:
                    dead.append((cid, ws))
        for cid, ws in dead:
            await self.disconnect(ws, cid)

    async def send_to(self, client_id: str, event_type: str, data: dict):
        """閸欐垿鈧胶绮伴幐鍥х暰鐎广垺鍩涚粩?""
        info = self.connections.get(client_id)
        if not info:
            return
        message = json.dumps({
            "type": event_type, "data": data,
            "timestamp": datetime.now().isoformat(),
        }, ensure_ascii=False)
        dead = []
        for ws in list(info["sockets"]):
            try:
                await ws.send_text(message)
            except Exception:
                dead.append(ws)
        for ws in dead:
            await self.disconnect(ws, client_id)

    async def agent_status_update(self, agents: list):
        await self.broadcast("agent_status", {"agents": agents})

    async def task_progress(self, task_id: str, step: int, status: str, detail: str = ""):
        await self.broadcast("task_progress", {"task_id": task_id, "step": step, "status": status, "detail": detail})

    async def trend_alert(self, platform: str, title: str, hot_score: int):
        await self.broadcast("trend_alert", {"platform": platform, "title": title, "hot_score": hot_score})

    async def system_alert(self, level: str, message: str):
        await self.broadcast("system_alert", {"level": level, "message": message})


ws_manager = WSManager()
