"""
Friday AI Agent v2.0 — 
:  ·  ·  ·  · 
: pip install websockets pyautogui pillow psutil playwright pytesseract opencv-python
      playwright install chromium
      python friday_agent.py
"""
import asyncio, json, base64, os, sys, io, subprocess, re, time
from pathlib import Path
from datetime import datetime
import socket

# =====  =====
SERVER = os.getenv("FRIDAY_SERVER", "wss://tiktook.eu.cc/agent/advanced/remote/ws")
CLIENT_ID = socket.gethostname()
VISION_ENABLED = True  # 
# ===== Token =====
LOCAL_COMMANDS = {
    # 
    "": "screenshot", "": "screenshot", "": "screenshot",
    # 
    "": "lock", "": "sleep_pc", "": "shutdown", "": "restart",
    "": "volume_up", "": "volume_down", "": "mute",
    "": "brightness_up", "": "brightness_down",
    # 
    "": "copy", "": "paste", "": "select_all", "": "undo",
    "": "save", "": "cut",
    # 
    "": "close_window", "": "switch_window",
    "": "minimize", "": "maximize",
    # 
    "": ("open_app", "notepad"),
    "": ("open_app", "calc"),
    "": ("open_app", "mspaint"),
    "": ("open_app", "chrome"),
    "": ("open_app", "taskmgr"),
    "cmd": ("open_app", "cmd"),
    "": ("open_app", "cmd"),
    # 
    "": "get_time", "": "get_time",
    "": "get_date", "": "get_date",
    "CPU": "get_cpu", "": "get_memory", "": "get_disk",
}

def parse_local_command(text):
    """。(action, params)None"""
    text_lower = text.strip().lower()
    # 
    for keyword, action in LOCAL_COMMANDS.items():
        if keyword in text_lower or keyword in text:
            if isinstance(action, tuple):
                return action[0], {"name": action[1]}
            return action, {}
    
    # : "XXX" -> 
    import re
    open_match = re.match(r's*(.+)', text)
    if open_match:
        app_name = open_match.group(1).strip()
        return "open_app", {"name": app_name}
    
    # : "XXX" / "XXX"
    type_match = re.match(r'(?:||)s*(.+)', text)
    if type_match:
        return "type_text", {"text": type_match.group(1).strip()}
    
    # : "XXX" / "XXX"
    key_match = re.match(r's*(.+?)(?:)?$', text)
    if key_match:
        key_map = {"": "enter", "": "space", "": "backspace", "": "backspace",
                   "": "up", "": "down", "": "left", "": "right",
                   "ESC": "escape", "Tab": "tab", "Win": "win", "F5": "f5"}
        key = key_match.group(1).strip()
        return "press_key", {"key": key_map.get(key, key)}
    
    return None

async def execute_local_command(action, params):
    """TokenAI"""
    import pyautogui, time
    
    if action == "screenshot":
        return {"ok": True, "screenshot": screenshot_to_base64()}
    
    elif action == "lock":
        if os.name == 'nt': subprocess.run("rundll32.exe user32.dll,LockWorkStation", shell=True)
        else: subprocess.run(["xdg-screensaver", "lock"])
        return {"ok": True, "done": "locked"}
    
    elif action == "sleep_pc":
        if os.name == 'nt': subprocess.run("rundll32.exe powrprof.dll,SetSuspendState 0,1,0", shell=True)
        else: subprocess.run(["systemctl", "suspend"])
        return {"ok": True, "done": "sleeping"}
    
    elif action == "shutdown":
        if os.name == 'nt': subprocess.run("shutdown /s /t 5", shell=True)
        else: subprocess.run(["shutdown", "-h", "+1"])
        return {"ok": True, "done": "shutting down"}
    
    elif action == "restart":
        if os.name == 'nt': subprocess.run("shutdown /r /t 5", shell=True)
        else: subprocess.run(["shutdown", "-r", "+1"])
        return {"ok": True, "done": "restarting"}
    
    elif action == "volume_up":
        pyautogui.press("volumeup")
        return {"ok": True, "done": "volume_up"}
    
    elif action == "volume_down":
        pyautogui.press("volumedown")
        return {"ok": True, "done": "volume_down"}
    
    elif action == "mute":
        pyautogui.press("volumemute")
        return {"ok": True, "done": "muted"}
    
    elif action in ("copy","paste","select_all","undo","save","cut"):
        key_map = {"copy": ("ctrl","c"), "paste": ("ctrl","v"), "select_all": ("ctrl","a"),
                   "undo": ("ctrl","z"), "save": ("ctrl","s"), "cut": ("ctrl","x")}
        pyautogui.hotkey(*key_map[action])
        return {"ok": True, "done": action}
    
    elif action == "close_window":
        pyautogui.hotkey("alt", "f4")
        return {"ok": True, "done": "closed"}
    
    elif action == "switch_window":
        pyautogui.hotkey("alt", "tab")
        return {"ok": True, "done": "switched"}
    
    elif action == "minimize":
        pyautogui.hotkey("win", "down")
        return {"ok": True, "done": "minimized"}
    
    elif action == "maximize":
        pyautogui.hotkey("win", "up")
        return {"ok": True, "done": "maximized"}
    
    elif action == "open_app":
        app = params.get("name", "")
        if os.name == 'nt':
            subprocess.Popen(app, shell=True)
        else:
            subprocess.Popen([app])
        time.sleep(0.5)
        return {"ok": True, "done": f"opened {app}"}
    
    elif action == "get_time":
        from datetime import datetime
        return {"ok": True, "time": datetime.now().strftime("%H:%M:%S")}
    
    elif action == "get_date":
        from datetime import datetime
        return {"ok": True, "date": datetime.now().strftime("%Y-%m-%d %A")}
    
    elif action == "get_cpu":
        import psutil
        return {"ok": True, "cpu": f"{psutil.cpu_percent()}%"}
    
    elif action == "get_memory":
        import psutil
        return {"ok": True, "memory": f"{psutil.virtual_memory().percent}%"}
    
    elif action == "get_disk":
        import psutil
        return {"ok": True, "disk": f"{psutil.disk_usage('/').percent}%"}
    
    elif action in ("brightness_up","brightness_down"):
        # Windows
        if os.name == 'nt':
            import screen_brightness_control as sbc
            try:
                current = sbc.get_brightness()[0]
                new = min(100, current + 10) if action == "brightness_up" else max(0, current - 10)
                sbc.set_brightness(new)
                return {"ok": True, "brightness": new}
            except: pass
        return {"ok": False, "error": " screen-brightness-control"}
    
    return {"ok": False, "error": f": {action}"}

AI

# =====  =====
def screenshot_to_base64():
    """ → base64"""
    try:
        from PIL import ImageGrab
        img = ImageGrab.grab()
        buf = io.BytesIO()
        img.save(buf, format="PNG", optimize=True)
        return base64.b64encode(buf.getvalue()).decode()
    except Exception as e:
        return None

# =====  =====
def find_element(description, screenshot_b64=None):
    """
    
    - ":500,400" → 
    - ":" → OCR""
    - ":button.png" → 
    - ":" → 
     {"x":int, "y":int, "method":str}  None
    """
    if not description:
        return None
    
    desc = str(description).strip()
    
    # 1: 
    coord_match = re.match(r'[:]\s*(\d+)\s*[,]\s*(\d+)', desc)
    if coord_match:
        return {"x": int(coord_match.group(1)), "y": int(coord_match.group(2)), "method": "coordinate"}
    
    # 2: OCR
    text_match = re.match(r'[:]\s*(.+)', desc)
    if text_match:
        target_text = text_match.group(1).strip()
        try:
            import pytesseract
            from PIL import ImageGrab
            import cv2
            import numpy as np
            
            img = ImageGrab.grab()
            img_np = np.array(img)
            # OCR
            data = pytesseract.image_to_data(img_np, lang='chi_sim+eng', output_type=pytesseract.Output.DICT)
            for i, text in enumerate(data['text']):
                if target_text in text:
                    x = data['left'][i] + data['width'][i] // 2
                    y = data['top'][i] + data['height'][i] // 2
                    if data['conf'][i] > 30:  # >30%
                        return {"x": x, "y": y, "method": f"ocr:{text}", "confidence": data['conf'][i]}
        except ImportError:
            pass  # OCR
        except Exception:
            pass
        return None  # 
    
    # 3: 
    img_match = re.match(r'[:]\s*(.+)', desc)
    if img_match:
        template_path = img_match.group(1).strip()
        try:
            import pyautogui
            location = pyautogui.locateOnScreen(template_path, confidence=0.8)
            if location:
                center = pyautogui.center(location)
                return {"x": center.x, "y": center.y, "method": f"template:{template_path}"}
        except Exception:
            pass
        return None
    
    # 4: 
    area_map = {
        "": (100, 100), "": (1820, 100),
        "": (100, 980), "": (1820, 980),
        "": (960, 540), "": (50, 1030),
        "": (960, 1050), "": (960, 540),
        "": (1880, 10), "": (1840, 10),
    }
    for area_name, (ax, ay) in area_map.items():
        if area_name in desc:
            return {"x": ax, "y": ay, "method": f"area:{area_name}"}
    
    return None

# =====  =====
async def execute_action(action, params, ws=None):
    """"""
    try:
        if action == "screenshot":
            b64 = screenshot_to_base64()
            return {"ok": True, "screenshot": b64, "action": action}
        
        elif action == "click":
            # 
            target_desc = params.get("target", "")
            pos = find_element(target_desc) if target_desc else None
            
            if pos:
                x, y = pos["x"], pos["y"]
            elif "x" in params and "y" in params:
                x, y = params["x"], params["y"]
            else:
                return {"ok": False, "error": "", "action": action}
            
            import pyautogui
            pyautogui.moveTo(x, y, duration=0.3)  # 
            time.sleep(0.1)
            pyautogui.click()
            result = {"ok": True, "action": action, "clicked": [x, y], "method": pos["method"] if pos else "coordinate"}
            # 
            if VISION_ENABLED:
                result["screenshot_after"] = screenshot_to_base64()
            return result
        
        elif action == "double_click":
            pos = find_element(params.get("target", "")) if params.get("target") else None
            x = pos["x"] if pos else params.get("x", 0)
            y = pos["y"] if pos else params.get("y", 0)
            import pyautogui
            pyautogui.moveTo(x, y, duration=0.3)
            pyautogui.doubleClick()
            return {"ok": True, "action": action, "clicked": [x, y]}
        
        elif action == "right_click":
            pos = find_element(params.get("target", "")) if params.get("target") else None
            x = pos["x"] if pos else params.get("x", 0)
            y = pos["y"] if pos else params.get("y", 0)
            import pyautogui
            pyautogui.moveTo(x, y, duration=0.3)
            pyautogui.rightClick()
            return {"ok": True, "action": action, "clicked": [x, y]}
        
        elif action == "type_text":
            text = params.get("text", "")
            # 
            import pyautogui, pyperclip
            try:
                pyperclip.copy(text)
                pyautogui.hotkey('ctrl', 'v')
            except ImportError:
                pyautogui.write(text, interval=0.05)  # 
            return {"ok": True, "action": action, "typed": text[:50]}
        
        elif action == "press_key":
            key = params.get("key", "")
            import pyautogui
            # 
            if "+" in key:
                keys = [k.strip() for k in key.split("+")]
                pyautogui.hotkey(*keys)
            else:
                pyautogui.press(key)
            return {"ok": True, "action": action, "key": key}
        
        elif action == "scroll":
            amount = params.get("amount", -500)
            import pyautogui
            pyautogui.scroll(amount)
            return {"ok": True, "action": action, "scrolled": amount}
        
        elif action == "move_mouse":
            pos = find_element(params.get("target", "")) if params.get("target") else None
            x = pos["x"] if pos else params.get("x", 960)
            y = pos["y"] if pos else params.get("y", 540)
            import pyautogui
            pyautogui.moveTo(x, y, duration=0.5)
            return {"ok": True, "action": action, "moved_to": [x, y]}
        
        elif action == "drag":
            x1, y1 = params.get("x1", 0), params.get("y1", 0)
            x2, y2 = params.get("x2", 0), params.get("y2", 0)
            import pyautogui
            pyautogui.moveTo(x1, y1, duration=0.3)
            pyautogui.drag(x2-x1, y2-y1, duration=0.5)
            return {"ok": True, "action": action, "dragged": [x1,y1,x2,y2]}
        
        elif action == "wait":
            seconds = min(params.get("seconds", 1), 30)  # 30
            await asyncio.sleep(seconds)
            return {"ok": True, "action": action, "waited": seconds}
        
        elif action == "run_command":
            cmd = params.get("command", "")
            r = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
            return {"ok": True, "action": action, "stdout": r.stdout[:3000], "stderr": r.stderr[:1000], "code": r.returncode}
        
        elif action == "get_info":
            import platform, psutil
            return {"ok": True, "action": action,
                    "hostname": socket.gethostname(), "os": platform.system(),
                    "cpu": psutil.cpu_percent(), "memory": psutil.virtual_memory().percent,
                    "disk": psutil.disk_usage('/').percent, "screen": pyautogui.size() if 'pyautogui' in dir() else None}
        
        elif action == "open_app":
            app = params.get("name", "")
            if os.name == 'nt':
                subprocess.Popen(app, shell=True)
            else:
                subprocess.Popen([app])
            await asyncio.sleep(1.5)  # 
            result = {"ok": True, "action": action, "opened": app}
            if VISION_ENABLED:
                result["screenshot_after"] = screenshot_to_base64()
            return result
        
        elif action == "close_window":
            import pyautogui
            pyautogui.hotkey('alt', 'f4')
            return {"ok": True, "action": action}
        
        elif action == "switch_window":
            import pyautogui
            pyautogui.hotkey('alt', 'tab')
            return {"ok": True, "action": action}
        
        elif action == "select_all":
            import pyautogui
            pyautogui.hotkey('ctrl', 'a')
            return {"ok": True, "action": action}
        
        elif action == "copy":
            import pyautogui
            pyautogui.hotkey('ctrl', 'c')
            return {"ok": True, "action": action}
        
        elif action == "paste":
            import pyautogui
            pyautogui.hotkey('ctrl', 'v')
            return {"ok": True, "action": action}
        
        elif action == "undo":
            import pyautogui
            pyautogui.hotkey('ctrl', 'z')
            return {"ok": True, "action": action}
        
        elif action == "save":
            import pyautogui
            pyautogui.hotkey('ctrl', 's')
            return {"ok": True, "action": action}
        
        elif action == "browser_task":
            # Playwright
            command = params.get("command", "")
            try:
                from playwright.async_api import async_playwright
                async with async_playwright() as p:
                    browser = await p.chromium.launch(headless=False)
                    page = await browser.new_page()
                    # AI
                    await page.goto("https://www.google.com")
                    await page.fill('textarea[name="q"]', command)
                    await page.press('textarea[name="q"]', "Enter")
                    await page.wait_for_load_state("networkidle")
                    text = await page.inner_text("body")
                    await browser.close()
                    return {"ok": True, "action": action, "result": text[:2000]}
            except ImportError:
                return {"ok": False, "error": "Playwright", "action": action}
        
        else:
            return {"ok": False, "error": f": {action}", "action": action}
    
    except Exception as e:
        return {"ok": False, "error": str(e), "action": action}

# =====  =====
async def main():
    import websockets
    print(f"\n{'='*60}")
    print(f"  Friday AI  Agent v2.0")
    print(f"  ID: {CLIENT_ID}")
    print(f"  :   {SERVER}")
    print(f"  : {'✅ ' if VISION_ENABLED else '❌ '}")
    print(f"{'='*60}\n")
    
    # 
    deps_ok = True
    try:
        import pyautogui
        print(f"  ✅ pyautogui {pyautogui.__version__ if hasattr(pyautogui,'__version__') else 'OK'}")
    except ImportError:
        print(f"  ❌ pyautogui ")
        deps_ok = False
    try:
        import PIL
        print(f"  ✅ Pillow OK")
    except ImportError:
        print(f"  ❌ Pillow ")
        deps_ok = False
    try:
        import pytesseract
        print(f"  ✅ pytesseract OK ()")
    except ImportError:
        print(f"  ⚠️  pytesseract  ()")
    try:
        import cv2
        print(f"  ✅ OpenCV OK ()")
    except ImportError:
        print(f"  ⚠️  OpenCV  ()")
    
    if not deps_ok:
        print(f"\n  : pip install pyautogui pillow\n")
    
    while True:
        try:
            print(f"[]  {SERVER} ...")
            async with websockets.connect(SERVER, ping_interval=20, ping_timeout=10) as ws:
                # 
                await ws.send(json.dumps({
                    "type": "register",
                    "client_id": CLIENT_ID,
                    "hostname": CLIENT_ID,
                    "version": "2.0",
                    "capabilities": ["screenshot", "click", "type", "scroll", "ocr", "vision"]
                }))
                print(f"[] ✅ ")
                
                # 
                async def heartbeat():
                    while True:
                        await asyncio.sleep(25)
                        try:
                            await ws.send(json.dumps({"type": "ping"}))
                        except:
                            break
                asyncio.create_task(heartbeat())
                
                # 
                async for msg in ws:
                    data = json.loads(msg)
                    msg_type = data.get("type", "")
                    
                    if msg_type == "execute":
                        action = data.get("action", "")
                        params = data.get("params", {})
                        task_id = data.get("task_id", "")
                        print(f"\n[] {action} | {str(params)[:80]}")
                        
                        # Token
                        local_result = parse_local_command(action) if not params or not any(params.values()) else None
                        if local_result:
                            local_action, local_params = local_result
                            result = await execute_local_command(local_action, local_params)
                            await ws.send(json.dumps({"type":"result","task_id":task_id,"action":action,"ok":result.get("ok",False),"data":result,"screenshot":result.get("screenshot"),"local":True},ensure_ascii=False))
                            print(f"[Token] {action} -> {local_action} \u2705")
                            continue
                        
                        result = await execute_action(action, params, ws)
                        
                        # 
                        response = {
                            "type": "result",
                            "task_id": task_id,
                            "action": action,
                            "ok": result.get("ok", False),
                            "data": result,
                            "screenshot": result.get("screenshot_after") or result.get("screenshot"),
                            "error": result.get("error")
                        }
                        await ws.send(json.dumps(response, ensure_ascii=False))
                        
                        status = "✅" if result.get("ok") else "❌"
                        print(f"[] {status} {str(result)[:120]}")
                    
                    elif msg_type == "vision_request":
                        # AI
                        shot = screenshot_to_base64()
                        await ws.send(json.dumps({
                            "type": "vision_response",
                            "screenshot": shot,
                            "task_id": data.get("task_id", "")
                        }))
                    
                    elif msg_type == "pong":
                        pass  # 
                    
                    elif msg_type == "registered":
                        print(f"[] {data.get('message', 'OK')}")
                    
                    else:
                        print(f"[] {msg_type}")
                    
                    elif msg_type == "nl_command":
                        #  -> Token
                        text = data.get("text","")
                        local_result = parse_local_command(text)
                        if local_result:
                            local_action, local_params = local_result
                            result = await execute_local_command(local_action, local_params)
                            await ws.send(json.dumps({"type":"nl_result","original":text,"action":local_action,"ok":result.get("ok",False),"data":result,"screenshot":result.get("screenshot"),"local":True,"zero_token":True},ensure_ascii=False))
                            print(f"[NL] \"{text}\" -> {local_action} ✅ (Token)")
                        else:
                            await ws.send(json.dumps({"type":"nl_result","original":text,"local":False,"message":"AI"},ensure_ascii=False))
        
        except websockets.exceptions.ConnectionClosed:
            print(f"[] 5...")
        except Exception as e:
            print(f"[] {str(e)[:200]}, 5...")
        
        await asyncio.sleep(5)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print(f"\n[] Agent")
    except Exception as e:
        print(f"\n[] {e}")