"""Friday AI OS — WebSocket实时推送管理器"""
import asyncio
import json
from datetime import datetime
from fastapi import WebSocket
from typing import Dict, Set

class WSManager:
    """WebSocket连接管理器"""

    def __init__(self):
        self.connections: Dict[str, Set[WebSocket]] = {}
        self._running = False

    async def connect(self, ws: WebSocket, client_id: str = "default"):
        await ws.accept()
        if client_id not in self.connections:
            self.connections[client_id] = set()
        self.connections[client_id].add(ws)
        await self.broadcast("system", {"type": "connected", "clients": self.count()})

    async def disconnect(self, ws: WebSocket, client_id: str = "default"):
        if client_id in self.connections:
            self.connections[client_id].discard(ws)
            if not self.connections[client_id]:
                del self.connections[client_id]

    def count(self) -> int:
        return sum(len(s) for s in self.connections.values())

    async def broadcast(self, event_type: str, data: dict):
        """广播消息到所有连接"""
        message = json.dumps({
            "type": event_type,
            "data": data,
            "timestamp": datetime.now().isoformat(),
        }, ensure_ascii=False)
        dead = []
        for cid, sockets in self.connections.items():
            for ws in list(sockets):
                try:
                    await ws.send_text(message)
                except:
                    dead.append((cid, ws))
        for cid, ws in dead:
            await self.disconnect(ws, cid)

    async def send_to(self, client_id: str, event_type: str, data: dict):
        """发送给指定客户端"""
        if client_id not in self.connections:
            return
        message = json.dumps({
            "type": event_type,
            "data": data,
            "timestamp": datetime.now().isoformat(),
        }, ensure_ascii=False)
        dead = []
        for ws in list(self.connections[client_id]):
            try:
                await ws.send_text(message)
            except:
                dead.append(ws)
        for ws in dead:
            await self.disconnect(ws, client_id)

    async def agent_status_update(self, agents: list):
        """推送Agent状态更新"""
        await self.broadcast("agent_status", {"agents": agents})

    async def task_progress(self, task_id: str, step: int, status: str, detail: str = ""):
        """推送任务进度"""
        await self.broadcast("task_progress", {
            "task_id": task_id,
            "step": step,
            "status": status,
            "detail": detail,
        })

    async def trend_alert(self, platform: str, title: str, hot_score: int):
        """推送热点预警"""
        await self.broadcast("trend_alert", {
            "platform": platform,
            "title": title,
            "hot_score": hot_score,
        })

    async def system_alert(self, level: str, message: str):
        """推送系统告警"""
        await self.broadcast("system_alert", {
            "level": level,
            "message": message,
        })

# 全局单例
ws_manager = WSManager()
