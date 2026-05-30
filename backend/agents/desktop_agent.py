''"Desktop Control Agent -- 
Agent, AI
''"
import asyncio
import json
import time
from datetime import datetime
from dataclasses import dataclass, field
from typing import Dict, Optional
from fastapi import WebSocket

@dataclass
class DesktopClient:
    ''''''
    agent_id: str
    ws: WebSocket
    connected_at: str = ''
    last_heartbeat: float = 0
    capabilities: dict = field(default_factory=dict)
    pending_commands: dict = field(default_factory=dict)  # cmd_id -> Future

class DesktopControlAgent:
    ''''''

    _clients: Dict[str, DesktopClient] = {}
    _lock = asyncio.Lock()

    # =====  =====

    @classmethod
    async def connect(cls, ws: WebSocket, agent_id: str):
        await ws.accept()
        async with cls._lock:
            cls._clients[agent_id] = DesktopClient(
                agent_id=agent_id, ws=ws,
                connected_at=datetime.now().isoformat(),
                last_heartbeat=time.time()
            )
        print(f"[DesktopControl]  {agent_id}  ({len(cls._clients)})")
        
        await ws.send_text(json.dumps({"type": "get_status"}))

    @classmethod
    async def disconnect(cls, agent_id: str):
        async with cls._lock:
            client = cls._clients.pop(agent_id, None)
        if client:
            print(f"[DesktopControl]  {agent_id}  ({len(cls._clients)})")
            
            for cmd_id, future in client.pending_commands.items():
                if not future.done():
                    future.set_result({"ok": False, "error": "Agent"})

    @classmethod
    async def handle_message(cls, agent_id: str, data: dict):
        ''"Agent''"
        msg_type = data.get("type", '')
        if msg_type == "result":
            cmd_id = data.get("cmd_id", '')
            async with cls._lock:
                client = cls._clients.get(agent_id)
                if client and cmd_id in client.pending_commands:
                    future = client.pending_commands.pop(cmd_id)
                    if not future.done():
                        result = {k: v for k, v in data.items() if k != "type"}
                        future.set_result(result)
        elif msg_type == "status":
            async with cls._lock:
                client = cls._clients.get(agent_id)
                if client:
                    client.capabilities = data.get("capabilities", {})
                    client.last_heartbeat = time.time()
        elif msg_type == "pong":
            async with cls._lock:
                client = cls._clients.get(agent_id)
                if client:
                    client.last_heartbeat = time.time()

    # ===== AI =====

    @classmethod
    async def list_desktops(cls) -> dict:
        ''''''
        desktops = []
        async with cls._lock:
            for aid, c in cls._clients.items():
                desktops.append({
                    "agent_id": aid,
                    "connected_at": c.connected_at,
                    "capabilities": c.capabilities,
                })
        return {"ok": True, "desktops": desktops, "count": len(desktops)}

    @classmethod
    async def execute(cls, action: str, params: dict, agent_id: str = None, timeout: float = 30) -> dict:
        ''"Agent''"
        async with cls._lock:
            if not cls._clients:
                return {"ok": False, "error": "Agent,  desktop_agent_local.py"}
            
            if agent_id and agent_id in cls._clients:
                target = cls._clients[agent_id]
            else:
                target = list(cls._clients.values())[0]  
                if agent_id:
                    return {"ok": False, "error": f"Agent '{agent_id}' , : {list(cls._clients.keys())}"}

            cmd_id = f"cmd_{int(time.time()*1000)}_{action}"
            future = asyncio.get_event_loop().create_future()
            target.pending_commands[cmd_id] = future

        try:
            await target.ws.send_text(json.dumps({"type": "execute", "cmd_id": cmd_id, "action": action, "params": params}, ensure_ascii=False))
            result = await asyncio.wait_for(future, timeout=timeout)
            return result
        except asyncio.TimeoutError:
            async with cls._lock:
                target.pending_commands.pop(cmd_id, None)
            return {"ok": False, "error": f"Agent({timeout}s)"}
        except Exception as e:
            async with cls._lock:
                target.pending_commands.pop(cmd_id, None)
            return {"ok": False, "error": str(e)}

    # ===== (AI Function Calling) =====

    @classmethod
    async def screenshot(cls, agent_id: str = None) -> dict:
        return await cls.execute("screenshot", {}, agent_id)

    @classmethod
    async def click(cls, x: int, y: int, button: str = "left", agent_id: str = None) -> dict:
        return await cls.execute("click", {"x": x, "y": y, "button": button}, agent_id)

    @classmethod
    async def type_text(cls, text: str, agent_id: str = None) -> dict:
        return await cls.execute("type_text", {"text": text}, agent_id)

    @classmethod
    async def press_keys(cls, keys: list, agent_id: str = None) -> dict:
        return await cls.execute("press_keys", {"keys": keys}, agent_id)

    @classmethod
    async def open_app(cls, app_path: str, agent_id: str = None) -> dict:
        return await cls.execute("open_app", {"app_path": app_path}, agent_id)

    @classmethod
    async def open_url(cls, url: str, agent_id: str = None) -> dict:
        return await cls.execute("open_url", {"url": url}, agent_id)

    @classmethod
    async def list_windows(cls, agent_id: str = None) -> dict:
        return await cls.execute("list_windows", {}, agent_id)

    @classmethod
    async def focus_window(cls, title_part: str, agent_id: str = None) -> dict:
        return await cls.execute("focus_window", {"title_part": title_part}, agent_id)

    @classmethod
    async def ocr_screen(cls, region: list = None, agent_id: str = None) -> dict:
        return await cls.execute("ocr_screen", {"region": region}, agent_id)

    @classmethod
    async def move_mouse(cls, x: int, y: int, duration: float = 0.3, agent_id: str = None) -> dict:
        return await cls.execute("move_mouse", {"x": x, "y": y, "duration": duration}, agent_id)

    @classmethod
    async def scroll(cls, amount: int, x: int = None, y: int = None, agent_id: str = None) -> dict:
        return await cls.execute("scroll", {"amount": amount, "x": x, "y": y}, agent_id)

    @classmethod
    async def drag(cls, x1: int, y1: int, x2: int, y2: int, agent_id: str = None) -> dict:
        return await cls.execute("drag", {"x1": x1, "y1": y1, "x2": x2, "y2": y2}, agent_id)

desktop_control = DesktopControlAgent()
