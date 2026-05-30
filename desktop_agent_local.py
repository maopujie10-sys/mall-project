"""Desktop Agent v1 -- AI
WebSocket, pyautogui+pynput
: python desktop_agent_local.py --server wss:///ws/desktop --token YOUR_TOKEN
"""
import asyncio
import json
import sys
import os
import base64
import io
import time
import argparse
import traceback
import websockets
from datetime import datetime

# =====  =====
HAS_PYAUTOGUI = HAS_PYNPUT = HAS_PIL = HAS_PYWIN32 = HAS_PYTESSERACT = False

try:
    import pyautogui
    pyautogui.FAILSAFE = True
    pyautogui.PAUSE = 0.1
    HAS_PYAUTOGUI = True
except ImportError:
    print("[DesktopAgent] ⚠️ pyautogui, : pip install pyautogui")

try:
    from pynput import keyboard, mouse
    HAS_PYNPUT = True
except ImportError:
    print("[DesktopAgent] ⚠️ pynput, : pip install pynput")

try:
    from PIL import Image, ImageGrab
    HAS_PIL = True
except ImportError:
    print("[DesktopAgent] ⚠️ Pillow, : pip install Pillow")

try:
    import pytesseract
    HAS_PYTESSERACT = True
except ImportError:
    print("[DesktopAgent] ⚠️ pytesseract, OCR: pip install pytesseract")

try:
    import win32gui, win32con, win32process, win32api
    HAS_PYWIN32 = True
except ImportError:
    print("[DesktopAgent] ⚠️ pywin32, : pip install pywin32")

class DesktopAgent:
    """Agent -- ,"""

    def __init__(self, server_url: str, token: str):
        self.server_url = server_url
        self.token = token
        self.ws = None
        self.running = False
        self.agent_id = f"desktop_{os.uname().nodename if hasattr(os, 'uname') else os.environ.get('COMPUTERNAME', 'unknown')}"

    # =====  =====

    def screenshot_base64(self) -> dict:
        """,base64"""
        if not HAS_PIL:
            return {"ok": False, "error": "Pillow"}
        try:
            img = ImageGrab.grab()
            buf = io.BytesIO()
            img.save(buf, format="PNG", optimize=True)
            b64 = base64.b64encode(buf.getvalue()).decode()
            return {"ok": True, "image": b64, "size": list(img.size), "format": "png"}
        except Exception as e:
            return {"ok": False, "error": str(e)}

    def click(self, x: int, y: int, button: str = "left", clicks: int = 1) -> dict:
        """"""
        if not HAS_PYAUTOGUI:
            return {"ok": False, "error": "pyautogui"}
        try:
            pyautogui.click(x, y, button=button, clicks=clicks)
            return {"ok": True, "x": x, "y": y, "button": button, "clicks": clicks}
        except Exception as e:
            return {"ok": False, "error": str(e)}

    def move_mouse(self, x: int, y: int, duration: float = 0.3, human_like: bool = True) -> dict:
        """()"""
        if not HAS_PYAUTOGUI:
            return {"ok": False, "error": "pyautogui"}
        try:
            if human_like:
                import random
                steps = int(duration * 30)
                start_x, start_y = pyautogui.position()
                for i in range(steps):
                    t = i / steps
                    # 
                    cx1 = start_x + (x - start_x) * 0.3 + random.randint(-50, 50)
                    cy1 = start_y + (y - start_y) * 0.3 + random.randint(-50, 50)
                    cx2 = start_x + (x - start_x) * 0.7 + random.randint(-30, 30)
                    cy2 = start_y + (y - start_y) * 0.7 + random.randint(-30, 30)
                    px = (1-t)**3 * start_x + 3*(1-t)**2*t * cx1 + 3*(1-t)*t**2 * cx2 + t**3 * x
                    py = (1-t)**3 * start_y + 3*(1-t)**2*t * cy1 + 3*(1-t)*t**2 * cy2 + t**3 * y
                    pyautogui.moveTo(px, py)
                    time.sleep(duration / steps * random.uniform(0.5, 1.5))
            else:
                pyautogui.moveTo(x, y, duration=duration)
            return {"ok": True, "x": x, "y": y}
        except Exception as e:
            return {"ok": False, "error": str(e)}

    def type_text(self, text: str, interval: float = 0.05) -> dict:
        """"""
        if not HAS_PYAUTOGUI:
            return {"ok": False, "error": "pyautogui"}
        try:
            pyautogui.typewrite(text, interval=interval)
            return {"ok": True, "text": text, "chars": len(text)}
        except Exception as e:
            return {"ok": False, "error": str(e)}

    def press_keys(self, keys: list) -> dict:
        """,  ["ctrl","c"]"""
        if not HAS_PYAUTOGUI:
            return {"ok": False, "error": "pyautogui"}
        try:
            pyautogui.hotkey(*keys)
            return {"ok": True, "keys": keys}
        except Exception as e:
            return {"ok": False, "error": str(e)}

    def scroll(self, amount: int, x: int = None, y: int = None) -> dict:
        """,,"""
        if not HAS_PYAUTOGUI:
            return {"ok": False, "error": "pyautogui"}
        try:
            if x is not None and y is not None:
                pyautogui.moveTo(x, y, duration=0.1)
            pyautogui.scroll(amount)
            return {"ok": True, "amount": amount}
        except Exception as e:
            return {"ok": False, "error": str(e)}

    def get_screen_size(self) -> dict:
        """"""
        if not HAS_PYAUTOGUI:
            return {"ok": False, "error": "pyautogui"}
        sz = pyautogui.size()
        return {"ok": True, "width": sz.width, "height": sz.height}

    def get_mouse_position(self) -> dict:
        """"""
        if not HAS_PYAUTOGUI:
            return {"ok": False, "error": "pyautogui"}
        pos = pyautogui.position()
        return {"ok": True, "x": pos.x, "y": pos.y}

    def drag(self, x1: int, y1: int, x2: int, y2: int, duration: float = 0.5) -> dict:
        """"""
        if not HAS_PYAUTOGUI:
            return {"ok": False, "error": "pyautogui"}
        try:
            pyautogui.moveTo(x1, y1, duration=0.2)
            pyautogui.drag(x2-x1, y2-y1, duration=duration)
            return {"ok": True, "from": [x1, y1], "to": [x2, y2]}
        except Exception as e:
            return {"ok": False, "error": str(e)}

    # =====  =====

    def open_app(self, app_path: str) -> dict:
        """"""
        try:
            os.startfile(app_path)
            return {"ok": True, "app": app_path}
        except Exception as e:
            return {"ok": False, "error": str(e)}

    def open_url(self, url: str) -> dict:
        """URL"""
        import webbrowser
        try:
            webbrowser.open(url)
            return {"ok": True, "url": url}
        except Exception as e:
            return {"ok": False, "error": str(e)}

    def list_windows(self) -> dict:
        """"""
        if not HAS_PYWIN32:
            return {"ok": False, "error": "pywin32"}
        try:
            windows = []
            def callback(hwnd, _):
                if win32gui.IsWindowVisible(hwnd):
                    title = win32gui.GetWindowText(hwnd)
                    if title and len(title) > 1:
                        rect = win32gui.GetWindowRect(hwnd)
                        windows.append({"hwnd": hwnd, "title": title, "rect": list(rect)})
            win32gui.EnumWindows(callback, None)
            return {"ok": True, "windows": windows[:30], "total": len(windows)}
        except Exception as e:
            return {"ok": False, "error": str(e)}

    def focus_window(self, title_part: str) -> dict:
        """"""
        if not HAS_PYWIN32:
            return {"ok": False, "error": "pywin32"}
        try:
            def callback(hwnd, result):
                if win32gui.IsWindowVisible(hwnd):
                    t = win32gui.GetWindowText(hwnd)
                    if title_part.lower() in t.lower():
                        result.append(hwnd)
            found = []
            win32gui.EnumWindows(callback, found)
            if found:
                win32gui.SetForegroundWindow(found[0])
                title = win32gui.GetWindowText(found[0])
                return {"ok": True, "title": title, "hwnd": found[0]}
            return {"ok": False, "error": f"'{title_part}'"}
        except Exception as e:
            return {"ok": False, "error": str(e)}

    def resize_window(self, title_part: str, width: int, height: int) -> dict:
        """"""
        if not HAS_PYWIN32:
            return {"ok": False, "error": "pywin32"}
        try:
            def callback(hwnd, result):
                if win32gui.IsWindowVisible(hwnd):
                    t = win32gui.GetWindowText(hwnd)
                    if title_part.lower() in t.lower():
                        result.append(hwnd)
            found = []
            win32gui.EnumWindows(callback, found)
            if found:
                win32gui.MoveWindow(found[0], 0, 0, width, height, True)
                return {"ok": True, "hwnd": found[0], "width": width, "height": height}
            return {"ok": False, "error": f"'{title_part}'"}
        except Exception as e:
            return {"ok": False, "error": str(e)}

    # ===== OCR =====

    def ocr_screen(self, region: list = None) -> dict:
        """+OCR"""
        if not HAS_PIL:
            return {"ok": False, "error": "Pillow"}
        if not HAS_PYTESSERACT:
            return {"ok": False, "error": "pytesseract,Tesseract-OCR: https://github.com/UB-Mannheim/tesseract/wiki"}
        try:
            img = ImageGrab.grab(bbox=tuple(region) if region else None)
            text = pytesseract.image_to_string(img, lang='chi_sim+eng')
            return {"ok": True, "text": text.strip(), "lines": len(text.strip().split(chr(10)))}
        except Exception as e:
            return {"ok": False, "error": str(e)}

    def locate_on_screen(self, image_path: str, confidence: float = 0.8) -> dict:
        """"""
        if not HAS_PYAUTOGUI:
            return {"ok": False, "error": "pyautogui"}
        try:
            loc = pyautogui.locateOnScreen(image_path, confidence=confidence)
            if loc:
                center = pyautogui.center(loc)
                return {"ok": True, "x": center.x, "y": center.y, "rect": [loc.left, loc.top, loc.width, loc.height]}
            return {"ok": False, "error": ""}
        except Exception as e:
            return {"ok": False, "error": str(e)}

    # =====  =====

    COMMANDS = {
        "screenshot": lambda self, p: self.screenshot_base64(),
        "click": lambda self, p: self.click(p["x"], p["y"], p.get("button", "left"), p.get("clicks", 1)),
        "move_mouse": lambda self, p: self.move_mouse(p["x"], p["y"], p.get("duration", 0.3), p.get("human_like", True)),
        "type_text": lambda self, p: self.type_text(p["text"], p.get("interval", 0.05)),
        "press_keys": lambda self, p: self.press_keys(p["keys"]),
        "scroll": lambda self, p: self.scroll(p["amount"], p.get("x"), p.get("y")),
        "screen_size": lambda self, p: self.get_screen_size(),
        "mouse_position": lambda self, p: self.get_mouse_position(),
        "drag": lambda self, p: self.drag(p["x1"], p["y1"], p["x2"], p["y2"], p.get("duration", 0.5)),
        "open_app": lambda self, p: self.open_app(p["app_path"]),
        "open_url": lambda self, p: self.open_url(p["url"]),
        "list_windows": lambda self, p: self.list_windows(),
        "focus_window": lambda self, p: self.focus_window(p["title_part"]),
        "resize_window": lambda self, p: self.resize_window(p["title_part"], p["width"], p["height"]),
        "ocr_screen": lambda self, p: self.ocr_screen(p.get("region")),
        "locate_image": lambda self, p: self.locate_on_screen(p["image_path"], p.get("confidence", 0.8)),
    }

    def execute(self, action: str, params: dict) -> dict:
        if action not in self.COMMANDS:
            return {"ok": False, "error": f": {action}, : {list(self.COMMANDS.keys())}"}
        try:
            return self.COMMANDS[action](self, params)
        except Exception as e:
            return {"ok": False, "error": str(e), "traceback": traceback.format_exc()}

    # ===== WebSocket =====

    async def connect(self):
        """WebSocket"""
        headers = {"Authorization": f"Bearer {self.token}", "X-Agent-Id": self.agent_id}
        retry_count = 0
        while self.running:
            try:
                self.ws = await websockets.connect(self.server_url, extra_headers=headers, ping_interval=30, ping_timeout=10)
                print(f"[DesktopAgent] ✅  {self.server_url} | Agent: {self.agent_id}")
                retry_count = 0
                await self._message_loop()
            except (websockets.ConnectionClosed, OSError) as e:
                retry_count += 1
                wait = min(retry_count * 5, 60)
                print(f"[DesktopAgent] ⚠️ , {wait}s... ({e})")
                await asyncio.sleep(wait)
            except Exception as e:
                retry_count += 1
                wait = min(retry_count * 5, 60)
                print(f"[DesktopAgent] ❌ : {e}, {wait}s...")
                await asyncio.sleep(wait)

    async def _message_loop(self):
        """"""
        async for raw in self.ws:
            try:
                msg = json.loads(raw)
                msg_type = msg.get("type", "")
                if msg_type == "ping":
                    await self.ws.send(json.dumps({"type": "pong", "agent_id": self.agent_id}))
                elif msg_type == "execute":
                    cmd_id = msg.get("cmd_id", "")
                    action = msg.get("action", "")
                    params = msg.get("params", {})
                    print(f"[DesktopAgent] : {action} {json.dumps(params, ensure_ascii=False)[:100]}")
                    result = self.execute(action, params)
                    result["cmd_id"] = cmd_id
                    result["agent_id"] = self.agent_id
                    await self.ws.send(json.dumps({"type": "result", **result}, ensure_ascii=False, default=str))
                elif msg_type == "get_status":
                    await self.ws.send(json.dumps({
                        "type": "status",
                        "agent_id": self.agent_id,
                        "capabilities": {
                            "pyautogui": HAS_PYAUTOGUI,
                            "pynput": HAS_PYNPUT,
                            "pillow": HAS_PIL,
                            "pywin32": HAS_PYWIN32,
                            "pytesseract": HAS_PYTESSERACT,
                        },
                        "screen_size": self.get_screen_size() if HAS_PYAUTOGUI else {"error": "pyautogui"},
                    }, ensure_ascii=False, default=str))
            except json.JSONDecodeError:
                pass
            except Exception as e:
                print(f"[DesktopAgent] : {e}")

    async def run(self):
        """Agent"""
        self.running = True
        print(f"[DesktopAgent] 🚀 ... Agent: {self.agent_id}")
        print(f"[DesktopAgent] : pyautogui={HAS_PYAUTOGUI} pillow={HAS_PIL} pywin32={HAS_PYWIN32} pytesseract={HAS_PYTESSERACT}")
        await self.connect()

    def stop(self):
        self.running = False

async def main():
    parser = argparse.ArgumentParser(description="Friday AI Agent")
    parser.add_argument("--server", required=True, help="WebSocket, : wss://tiktook.eu.cc/ws/desktop")
    parser.add_argument("--token", required=True, help="Token")
    args = parser.parse_args()

    agent = DesktopAgent(args.server, args.token)
    try:
        await agent.run()
    except KeyboardInterrupt:
        print("\n[DesktopAgent] 🛑 ")
    finally:
        agent.stop()

if __name__ == "__main__":
    asyncio.run(main())
