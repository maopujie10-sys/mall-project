"""Friday AI OS — WebSocket实时推送管理器
v2: 心跳检测 + 自动清理断连 + 连接数上限 + 消息队列"""
import asyncio
import json
from datetime import datetime
from fastapi import WebSocket
from typing import Dict, Set, Optional

MAX_CONNECTIONS = 100
HEARTBEAT_INTERVAL = 30  # 30s无消息则Ping
DISCONNECT_TIMEOUT = 120  # 120s无Pong则断开


class WSManager:
    """WebSocket连接管理器"""

    def __init__(self):
        self.connections: Dict[str, Dict[str, any]] = {}  # client_id -> {sockets, last_heartbeat}
        self._running = False
        self._heartbeat_task: Optional[asyncio.Task] = None

    def _start_heartbeat(self):
        """启动后台心跳检测"""
        if self._running:
            return
        self._running = True
        self._heartbeat_task = asyncio.create_task(self._heartbeat_loop())

    async def _heartbeat_loop(self):
        """定时心跳检测循环"""
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
                    # 检查最后心跳时间
                    last = info.get("last_heartbeat", 0)
                    if now - last > DISCONNECT_TIMEOUT:
                        dead.append((cid, ws))
            for cid, ws in dead:
                await self.disconnect(ws, cid)

    async def connect(self, ws: WebSocket, client_id: str = "default"):
        await ws.accept()
        # 连接数上限检查
        total = self.count()
        if total >= MAX_CONNECTIONS:
            await ws.send_text(json.dumps({"type": "error", "message": "连接数已满"}))
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
        """广播消息到所有连接"""
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
        """发送给指定客户端"""
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
