"""
Friday AI 本地智能Agent v2.0 — 人类级电脑操控
能力: 视觉理解 · 智能定位 · 任务拆解 · 自纠错 · 多应用操控
用法: pip install websockets pyautogui pillow psutil playwright pytesseract opencv-python
      playwright install chromium
      python friday_agent.py
"""
import asyncio, json, base64, os, sys, io, subprocess, re, time
from pathlib import Path
from datetime import datetime
import socket

# ===== 配置 =====
SERVER = os.getenv("FRIDAY_SERVER", "wss://tiktook.eu.cc/agent/advanced/remote/ws")
CLIENT_ID = socket.gethostname()
VISION_ENABLED = True  # 是否启用视觉理解（截图发给服务器AI分析）

# ===== 截图 =====
def screenshot_to_base64():
    """截取全屏 → base64"""
    try:
        from PIL import ImageGrab
        img = ImageGrab.grab()
        buf = io.BytesIO()
        img.save(buf, format="PNG", optimize=True)
        return base64.b64encode(buf.getvalue()).decode()
    except Exception as e:
        return None

# ===== 智能元素定位 =====
def find_element(description, screenshot_b64=None):
    """
    智能查找屏幕元素，支持多种方式：
    - "坐标:500,400" → 直接返回坐标
    - "文本:登录" → OCR查找包含"登录"的文字位置
    - "图片:button.png" → 图像模板匹配
    - "区域:左上角" → 返回预设区域坐标
    返回 {"x":int, "y":int, "method":str} 或 None
    """
    if not description:
        return None
    
    desc = str(description).strip()
    
    # 方式1: 直接坐标
    coord_match = re.match(r'坐标[:：]\s*(\d+)\s*[,，]\s*(\d+)', desc)
    if coord_match:
        return {"x": int(coord_match.group(1)), "y": int(coord_match.group(2)), "method": "coordinate"}
    
    # 方式2: OCR文字查找
    text_match = re.match(r'文本[:：]\s*(.+)', desc)
    if text_match:
        target_text = text_match.group(1).strip()
        try:
            import pytesseract
            from PIL import ImageGrab
            import cv2
            import numpy as np
            
            img = ImageGrab.grab()
            img_np = np.array(img)
            # OCR获取所有文字位置
            data = pytesseract.image_to_data(img_np, lang='chi_sim+eng', output_type=pytesseract.Output.DICT)
            for i, text in enumerate(data['text']):
                if target_text in text:
                    x = data['left'][i] + data['width'][i] // 2
                    y = data['top'][i] + data['height'][i] // 2
                    if data['conf'][i] > 30:  # 置信度>30%
                        return {"x": x, "y": y, "method": f"ocr:{text}", "confidence": data['conf'][i]}
        except ImportError:
            pass  # OCR不可用，降级
        except Exception:
            pass
        return None  # 找不到文字
    
    # 方式3: 图像模板匹配
    img_match = re.match(r'图片[:：]\s*(.+)', desc)
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
    
    # 方式4: 语义区域
    area_map = {
        "左上角": (100, 100), "右上角": (1820, 100),
        "左下角": (100, 980), "右下角": (1820, 980),
        "屏幕中央": (960, 540), "开始菜单": (50, 1030),
        "任务栏": (960, 1050), "桌面中心": (960, 540),
        "关闭按钮": (1880, 10), "最小化": (1840, 10),
    }
    for area_name, (ax, ay) in area_map.items():
        if area_name in desc:
            return {"x": ax, "y": ay, "method": f"area:{area_name}"}
    
    return None

# ===== 动作执行 =====
async def execute_action(action, params, ws=None):
    """执行单个操控动作，返回结果"""
    try:
        if action == "screenshot":
            b64 = screenshot_to_base64()
            return {"ok": True, "screenshot": b64, "action": action}
        
        elif action == "click":
            # 智能定位优先
            target_desc = params.get("target", "")
            pos = find_element(target_desc) if target_desc else None
            
            if pos:
                x, y = pos["x"], pos["y"]
            elif "x" in params and "y" in params:
                x, y = params["x"], params["y"]
            else:
                return {"ok": False, "error": "需要坐标或元素描述", "action": action}
            
            import pyautogui
            pyautogui.moveTo(x, y, duration=0.3)  # 人类化移动
            time.sleep(0.1)
            pyautogui.click()
            result = {"ok": True, "action": action, "clicked": [x, y], "method": pos["method"] if pos else "coordinate"}
            # 点击后自动截图验证
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
            # 支持中文输入
            import pyautogui, pyperclip
            try:
                pyperclip.copy(text)
                pyautogui.hotkey('ctrl', 'v')
            except ImportError:
                pyautogui.write(text, interval=0.05)  # 人类化打字速度
            return {"ok": True, "action": action, "typed": text[:50]}
        
        elif action == "press_key":
            key = params.get("key", "")
            import pyautogui
            # 支持组合键
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
            seconds = min(params.get("seconds", 1), 30)  # 最多等30秒
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
            await asyncio.sleep(1.5)  # 等应用启动
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
            # 委托给Playwright执行
            command = params.get("command", "")
            try:
                from playwright.async_api import async_playwright
                async with async_playwright() as p:
                    browser = await p.chromium.launch(headless=False)
                    page = await browser.new_page()
                    # 简化版：让AI先拆步骤
                    await page.goto("https://www.google.com")
                    await page.fill('textarea[name="q"]', command)
                    await page.press('textarea[name="q"]', "Enter")
                    await page.wait_for_load_state("networkidle")
                    text = await page.inner_text("body")
                    await browser.close()
                    return {"ok": True, "action": action, "result": text[:2000]}
            except ImportError:
                return {"ok": False, "error": "Playwright未安装", "action": action}
        
        else:
            return {"ok": False, "error": f"未知操作: {action}", "action": action}
    
    except Exception as e:
        return {"ok": False, "error": str(e), "action": action}

# ===== 主循环 =====
async def main():
    import websockets
    print(f"\n{'='*60}")
    print(f"  Friday AI 本地 Agent v2.0")
    print(f"  客户端ID: {CLIENT_ID}")
    print(f"  服务器:   {SERVER}")
    print(f"  视觉理解: {'✅ 启用' if VISION_ENABLED else '❌ 关闭'}")
    print(f"{'='*60}\n")
    
    # 检查依赖
    deps_ok = True
    try:
        import pyautogui
        print(f"  ✅ pyautogui {pyautogui.__version__ if hasattr(pyautogui,'__version__') else 'OK'}")
    except ImportError:
        print(f"  ❌ pyautogui 未安装")
        deps_ok = False
    try:
        import PIL
        print(f"  ✅ Pillow OK")
    except ImportError:
        print(f"  ❌ Pillow 未安装")
        deps_ok = False
    try:
        import pytesseract
        print(f"  ✅ pytesseract OK (文字识别)")
    except ImportError:
        print(f"  ⚠️  pytesseract 未安装 (文字查找降级)")
    try:
        import cv2
        print(f"  ✅ OpenCV OK (图像匹配)")
    except ImportError:
        print(f"  ⚠️  OpenCV 未安装 (图像匹配降级)")
    
    if not deps_ok:
        print(f"\n  请安装缺失依赖: pip install pyautogui pillow\n")
    
    while True:
        try:
            print(f"[连接] 正在连接 {SERVER} ...")
            async with websockets.connect(SERVER, ping_interval=20, ping_timeout=10) as ws:
                # 注册
                await ws.send(json.dumps({
                    "type": "register",
                    "client_id": CLIENT_ID,
                    "hostname": CLIENT_ID,
                    "version": "2.0",
                    "capabilities": ["screenshot", "click", "type", "scroll", "ocr", "vision"]
                }))
                print(f"[注册] ✅ 已注册到服务器")
                
                # 心跳
                async def heartbeat():
                    while True:
                        await asyncio.sleep(25)
                        try:
                            await ws.send(json.dumps({"type": "ping"}))
                        except:
                            break
                asyncio.create_task(heartbeat())
                
                # 指令循环
                async for msg in ws:
                    data = json.loads(msg)
                    msg_type = data.get("type", "")
                    
                    if msg_type == "execute":
                        action = data.get("action", "")
                        params = data.get("params", {})
                        task_id = data.get("task_id", "")
                        print(f"\n[执行] {action} | {str(params)[:80]}")
                        
                        result = await execute_action(action, params, ws)
                        
                        # 返回结果
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
                        print(f"[结果] {status} {str(result)[:120]}")
                    
                    elif msg_type == "vision_request":
                        # 服务器请求截图用于AI视觉分析
                        shot = screenshot_to_base64()
                        await ws.send(json.dumps({
                            "type": "vision_response",
                            "screenshot": shot,
                            "task_id": data.get("task_id", "")
                        }))
                    
                    elif msg_type == "pong":
                        pass  # 心跳响应
                    
                    elif msg_type == "registered":
                        print(f"[服务器] {data.get('message', 'OK')}")
                    
                    else:
                        print(f"[未知消息] {msg_type}")
        
        except websockets.exceptions.ConnectionClosed:
            print(f"[断开] 连接关闭，5秒后重连...")
        except Exception as e:
            print(f"[错误] {str(e)[:200]}, 5秒后重连...")
        
        await asyncio.sleep(5)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print(f"\n[退出] Agent已停止")
    except Exception as e:
        print(f"\n[致命错误] {e}")