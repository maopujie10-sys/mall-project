"""高级AI引擎 — 实时语音打断 / 视频流分析 / 深度研究 / 数据可视化 / 文件导出 / 网页抓取 / 浏览器自动化 / 长上下文"""
import json, os, re, io, base64, asyncio, tempfile, subprocess
from pathlib import Path
from datetime import datetime
from fastapi import APIRouter, Depends, Query, WebSocket, WebSocketDisconnect
from fastapi.responses import StreamingResponse, FileResponse
from pydantic import BaseModel
from auth import verify_token
from config import OPENAI_API_KEY, OPENAI_BASE_URL, DEEPSEEK_API_KEY

router = APIRouter(prefix="/agent/advanced", tags=["AdvancedAI"])
API_KEY = OPENAI_API_KEY or DEEPSEEK_API_KEY
BASE_URL = OPENAI_BASE_URL or "https://api.openai.com/v1"

async def _call_ai(messages, model="gpt-3.5-turbo", max_tokens=1000, temperature=0.7):
    if not API_KEY: return "需要API Key"
    import httpx
    async with httpx.AsyncClient(timeout=120) as c:
        r = await c.post(f"{BASE_URL}/chat/completions",
            headers={"Authorization":f"Bearer {API_KEY}","Content-Type":"application/json"},
            json={"model":model,"messages":messages,"max_tokens":max_tokens,"temperature":temperature})
        if r.status_code == 200:
            return r.json().get("choices",[{}])[0].get("message",{}).get("content","")
        return f"API错误:{r.status_code}"

# ===== 1. 实时语音打断 WebSocket =====
@router.websocket("/voice/live")
async def live_voice(ws: WebSocket):
    """实时语音对话 — 支持打断/情感/自然对话"""
    await ws.accept()
    conversation = []
    current_task = None
    
    async def stream_ai_reply(messages):
        import httpx
        full = ""
        async with httpx.AsyncClient(timeout=60) as c:
            async with c.stream("POST",f"{BASE_URL}/chat/completions",
                headers={"Authorization":f"Bearer {API_KEY}","Content-Type":"application/json"},
                json={"model":"gpt-4o-mini","messages":messages,"stream":True,"temperature":0.8}) as r:
                async for line in r.aiter_lines():
                    if line.startswith("data: "):
                        d = line[6:]
                        if d == "[DONE]": break
                        try:
                            j = json.loads(d)
                            t = j.get("choices",[{}])[0].get("delta",{}).get("content","")
                            if t:
                                full += t
                                await ws.send_json({"type":"token","text":t,"partial":full})
                        except: pass
        return full
    
    try:
        while True:
            data = await ws.receive_json()
            msg_type = data.get("type","")
            
            if msg_type == "ping":
                await ws.send_json({"type":"pong"})
            elif msg_type == "interrupt":
                # 用户打断当前回复
                if current_task and not current_task.done():
                    current_task.cancel()
                await ws.send_json({"type":"interrupted"})
            elif msg_type == "speech":
                text = data.get("text","")
                if not text: continue
                conversation.append({"role":"user","content":text})
                await ws.send_json({"type":"status","text":"思考中..."})
                
                msgs = [{"role":"system","content":"你是Friday AI助手。用自然的口语回复，带适当的情感。可以笑、叹气、惊讶。回复简洁自然，像朋友聊天。不要用markdown。"}]
                msgs.extend(conversation[-15:])
                
                current_task = asyncio.create_task(stream_ai_reply(msgs))
                try:
                    full_reply = await current_task
                    conversation.append({"role":"assistant","content":full_reply})
                    await ws.send_json({"type":"done","full":full_reply})
                except asyncio.CancelledError:
                    await ws.send_json({"type":"interrupted"})
            elif msg_type == "emotion":
                # 客户端检测到的情绪
                await ws.send_json({"type":"status","text":"已感知情绪: "+data.get("emotion","neutral")})
    except WebSocketDisconnect:
        pass

# ===== 2. 实时视频帧分析 =====
class FrameRequest(BaseModel):
    image_base64: str
    context: str = ""

@router.post("/vision/live")
async def live_vision(req: FrameRequest, _=Depends(verify_token)):
    """实时视频帧分析 — 连续帧理解"""
    prompt = "你正在看实时视频流。请用一句话描述画面内容，如果有值得注意的变化请指出。"
    if req.context: prompt = f"之前你看到：{req.context}\n继续观察："
    
    result = await _call_ai([
        {"role":"system","content":"你是实时视频分析AI。简洁描述画面。"},
        {"role":"user","content":[
            {"type":"text","text":prompt},
            {"type":"image_url","image_url":{"url":f"data:image/jpeg;base64,{req.image_base64}"}}
        ]}
    ], model="gpt-4o-mini", max_tokens=200)
    return {"ok":True,"description":result}

# ===== 3. 深度研究 Agent =====
class ResearchRequest(BaseModel):
    topic: str
    depth: int = 2  # 研究深度 1-3

@router.post("/research")
async def deep_research(req: ResearchRequest, _=Depends(verify_token)):
    """多步自主研究 — 搜索→分析→综合→报告"""
    import httpx
    
    # Step 1: 生成搜索子问题
    questions_prompt = f"将研究主题拆分为{min(req.depth*2,5)}个具体子问题，只返回问题列表，每行一个。\n主题：{req.topic}"
    sub_questions = await _call_ai([{"role":"user","content":questions_prompt}], max_tokens=300)
    questions = [q.strip().lstrip('0123456789.-) ') for q in sub_questions.split('\n') if q.strip()][:5]
    
    # Step 2: 搜索每个子问题
    findings = []
    for q in questions[:req.depth*2]:
        try:
            async with httpx.AsyncClient(timeout=15) as c:
                r = await c.get("https://html.duckduckgo.com/html/",
                    params={"q": q}, headers={"User-Agent":"Mozilla/5.0"})
                # 提取摘要
                snippets = []
                for m in re.finditer(r'class="result__snippet"[^>]*>([^<]+)', r.text):
                    snippets.append(m.group(1).strip())
                summary_text = " ".join(snippets[:3])[:500]
                if summary_text:
                    # Step 3: AI分析每个子问题
                    analysis = await _call_ai([
                        {"role":"user","content":f"子问题：{q}\n搜索结果：{summary_text}\n请用2-3句话总结关键发现。"}
                    ], max_tokens=200)
                    findings.append({"question":q,"sources":len(snippets),"finding":analysis})
        except: findings.append({"question":q,"sources":0,"finding":"搜索失败"})
    
    # Step 4: 综合报告
    findings_text = "\n".join([f"## {f['question']}\n{f['finding']}" for f in findings])
    report = await _call_ai([
        {"role":"system","content":"你是资深研究员。根据以下研究发现，生成一份结构化的研究报告。要有摘要、关键发现、结论。"},
        {"role":"user","content":f"研究主题：{req.topic}\n\n研究发现：\n{findings_text}\n\n请生成完整研究报告。"}
    ], max_tokens=2000)
    
    return {"ok":True,"topic":req.topic,"questions":questions,"findings":findings,"report":report}

# ===== 4. 数据可视化 + CSV分析 =====
class DataAnalyzeRequest(BaseModel):
    csv_data: str = ""
    question: str = "分析数据并给出洞察"

@router.post("/data/analyze")
async def analyze_data(req: DataAnalyzeRequest, _=Depends(verify_token)):
    """上传CSV→AI自动分析→文本+图表数据"""
    if not req.csv_data:
        return {"ok":False,"error":"需要CSV数据"}
    
    # 解析CSV
    import csv as csv_mod
    reader = csv_mod.reader(io.StringIO(req.csv_data[:50000]))
    rows = list(reader)
    if not rows: return {"ok":False,"error":"CSV为空"}
    
    headers = rows[0]
    data_rows = rows[1:21]  # 前20行
    row_count = len(rows) - 1
    col_count = len(headers)
    
    # 基本统计
    stats = {"rows":row_count,"columns":col_count,"headers":headers}
    numeric_cols = []
    for ci, h in enumerate(headers):
        try:
            vals = [float(r[ci]) for r in data_rows if ci < len(r)]
            numeric_cols.append({"name":h,"index":ci,"min":min(vals),"max":max(vals),"avg":round(sum(vals)/len(vals),2),"count":len(vals)})
        except: pass
    
    # AI分析
    preview = "\n".join([",".join(r) for r in [headers]+data_rows[:10]])
    prompt = f"""CSV数据({row_count}行,{col_count}列):
标题: {headers}
统计: {json.dumps(numeric_cols,ensure_ascii=False)}
前10行: {preview[:1000]}

用户问题: {req.question}

请给出：1)数据概览 2)关键洞察 3)异常发现 4)建议。简洁专业。"""
    
    insight = await _call_ai([{"role":"user","content":prompt}], max_tokens=800)
    
    # 生成ECharts配置
    chart_config = None
    if numeric_cols:
        nc = numeric_cols[0]
        chart_config = {
            "type":"bar","title":f"{nc['name']}分布",
            "labels":["min","avg","max"],
            "values":[nc["min"],nc["avg"],nc["max"]],
            "suggestion":"可用更多列做折线图/饼图"
        }
    
    return {"ok":True,"stats":stats,"numeric_columns":numeric_cols,"insight":insight,"chart":chart_config}

# ===== 5. 文件导出 (PDF/Excel/Markdown) =====
class ExportRequest(BaseModel):
    content: str
    format: str = "md"  # md | html | txt
    filename: str = "report"

@router.post("/export")
async def export_file(req: ExportRequest, _=Depends(verify_token)):
    """导出AI生成的内容为文件"""
    export_dir = Path(__file__).parent.parent / "data" / "exports"
    export_dir.mkdir(parents=True, exist_ok=True)
    
    ext_map = {"md":".md","html":".html","txt":".txt","csv":".csv","json":".json"}
    ext = ext_map.get(req.format,".txt")
    fname = f"{req.filename}_{datetime.now().strftime('%Y%m%d_%H%M%S')}{ext}"
    fpath = export_dir / fname
    
    if req.format == "html":
        html_content = f"""<!DOCTYPE html><html><head><meta charset="utf-8"><title>{req.filename}</title>
<style>body{{font-family:Arial;max-width:800px;margin:40px auto;line-height:1.8;color:#333}}
h1{{color:#667eea}} pre{{background:#f5f5f5;padding:12px;border-radius:8px}}</style></head>
<body>{req.content.replace(chr(10),'<br>')}</body></html>"""
        fpath.write_text(html_content, encoding="utf-8")
    else:
        fpath.write_text(req.content, encoding="utf-8")
    
    return {"ok":True,"filename":fname,"path":str(fpath),"size":fpath.stat().st_size,"url":f"/agent/advanced/download/{fname}"}

@router.get("/download/{filename}")
async def download_file(filename: str):
    """下载导出文件"""
    fpath = Path(__file__).parent.parent / "data" / "exports" / filename
    if not fpath.exists():
        return {"ok":False,"error":"文件不存在"}
    media_types = {".md":"text/markdown",".html":"text/html",".txt":"text/plain",".csv":"text/csv",".json":"application/json"}
    ext = fpath.suffix
    return FileResponse(fpath, media_type=media_types.get(ext,"application/octet-stream"), filename=filename)

# ===== 6. 网页内容抓取+总结 =====
class ScrapeRequest(BaseModel):
    url: str

@router.post("/scrape")
async def scrape_url(req: ScrapeRequest, _=Depends(verify_token)):
    """抓取网页内容并AI总结"""
    import httpx
    try:
        async with httpx.AsyncClient(timeout=20) as c:
            r = await c.get(req.url, headers={"User-Agent":"Mozilla/5.0"}, follow_redirects=True)
            if r.status_code != 200:
                return {"ok":False,"error":f"HTTP {r.status_code}"}
            
            html = r.text
            # 简易正文提取
            text = re.sub(r'<script[^>]*>.*?</script>','',html,flags=re.DOTALL|re.I)
            text = re.sub(r'<style[^>]*>.*?</style>','',text,flags=re.DOTALL|re.I)
            text = re.sub(r'<[^>]+>',' ',text)
            text = re.sub(r'\s+',' ',text).strip()[:8000]
            
            # AI总结
            summary = await _call_ai([
                {"role":"system","content":"你是网页总结专家。用3-5句话总结核心内容，提取关键信息。"},
                {"role":"user","content":f"URL: {req.url}\n\n内容:\n{text[:5000]}"}
            ], max_tokens=300)
            
            title_match = re.search(r'<title[^>]*>([^<]+)</title>', html, re.I)
            title = title_match.group(1).strip() if title_match else req.url
            
            return {"ok":True,"url":req.url,"title":title,"text_length":len(text),"summary":summary}
    except Exception as e:
        return {"ok":False,"error":str(e)}

# ===== 7. AI浏览器Agent — 自然语言操控浏览器 =====
class BrowserAgentRequest(BaseModel):
    command: str  # 自然语言指令
    headless: bool = True
    max_steps: int = 10

@router.post("/browser/agent")
async def browser_agent(req: BrowserAgentRequest, _=Depends(verify_token)):
    """AI浏览器Agent — 自然语言→步骤拆解→Playwright执行→AI视觉理解"""
    import httpx
    
    # Step 1: AI拆解任务为步骤
    plan_prompt = f"""你是一个浏览器自动化专家。将以下任务拆解为具体的浏览器操作步骤。
返回JSON数组，每步格式: {{"action":"navigate/click/type/wait/screenshot/extract/scroll","target":"选择器或URL","value":"输入值或说明","reason":"为什么这步"}}

任务: {req.command}

规则:
- navigate: 打开URL 
- click: 点击元素(用文本或CSS选择器)
- type: 输入文本(先click再type)
- wait: 等待(秒)
- screenshot: 截图
- extract: 提取页面数据(说明要提取什么)
- scroll: 向下滚动

只返回JSON数组，不要其他内容。最多{req.max_steps}步。"""

    plan_text = await _call_ai([{"role":"user","content":plan_prompt}], max_tokens=800, temperature=0.3)
    
    # 解析步骤
    steps = []
    try:
        json_match = re.search(r'\[.*\]', plan_text, re.DOTALL)
        if json_match:
            steps = json.loads(json_match.group())
    except:
        # Fallback: 简单任务直接执行
        steps = [{"action":"navigate","target":"https://www.google.com/search?q="+req.command.replace(" ","+"),"reason":"搜索"}]
    
    # Step 2: Playwright执行
    results = []
    screenshots = []
    
    try:
        import subprocess, tempfile
        
        script_lines = [
            "from playwright.sync_api import sync_playwright",
            "import json, time",
            "p = sync_playwright().start()",
            f"browser = p.chromium.launch(headless={'True' if req.headless else 'False'})",
            "page = browser.new_page(viewport={'width':1280,'height':900})",
            "page.set_default_timeout(15000)",
            "outputs = []",
        ]
        
        for i, step in enumerate(steps):
            action = step.get("action","")
            target = step.get("target","")
            value = step.get("value","")
            
            if action == "navigate" and target:
                script_lines.append(f"try:\n    page.goto('{target}', wait_until='domcontentloaded')\n    outputs.append({{'step':{i},'action':'navigate','ok':True,'url':page.url}})\nexcept Exception as e:\n    outputs.append({{'step':{i},'action':'navigate','ok':False,'error':str(e)}})")
            
            elif action == "click" and target:
                # Try text content first, then CSS
                script_lines.append(f"try:\n    page.click('text={target}', timeout=5000)\n    outputs.append({{'step':{i},'action':'click','ok':True,'target':'{target}'}})\nexcept:\n    try:\n        page.click('{target}', timeout=5000)\n        outputs.append({{'step':{i},'action':'click','ok':True,'target':'{target}'}})\n    except Exception as e:\n        outputs.append({{'step':{i},'action':'click','ok':False,'error':str(e)}})")
            
            elif action == "type" and target and value:
                script_lines.append(f"try:\n    page.fill('{target}', '{value}', timeout=5000)\n    outputs.append({{'step':{i},'action':'type','ok':True,'value':'{value}'}})\nexcept:\n    try:\n        page.type('{target}', '{value}', delay=50)\n        outputs.append({{'step':{i},'action':'type','ok':True,'value':'{value}'}})\n    except Exception as e:\n        outputs.append({{'step':{i},'action':'type','ok':False,'error':str(e)}})")
            
            elif action == "wait":
                secs = min(float(str(target or value or "1")), 10)
                script_lines.append(f"time.sleep({secs})\noutputs.append({{'step':{i},'action':'wait','ok':True,'seconds':{secs}}})")
            
            elif action == "screenshot":
                script_lines.append(f"try:\n    page.screenshot(path='/tmp/agent_shot_{i}.png', full_page=False)\n    outputs.append({{'step':{i},'action':'screenshot','ok':True,'file':'/tmp/agent_shot_{i}.png'}})\nexcept Exception as e:\n    outputs.append({{'step':{i},'action':'screenshot','ok':False,'error':str(e)}})")
            
            elif action == "extract":
                # 提取页面文本
                script_lines.append(f"try:\n    text = page.inner_text('body')[:3000]\n    title = page.title()\n    outputs.append({{'step':{i},'action':'extract','ok':True,'title':title,'text':text}})\nexcept Exception as e:\n    outputs.append({{'step':{i},'action':'extract','ok':False,'error':str(e)}})")
            
            elif action == "scroll":
                script_lines.append(f"try:\n    page.evaluate('window.scrollBy(0,800)')\n    outputs.append({{'step':{i},'action':'scroll','ok':True}})\nexcept Exception as e:\n    outputs.append({{'step':{i},'action':'scroll','ok':False,'error':str(e)}})")
            
            else:
                script_lines.append(f"outputs.append({{'step':{i},'action':'{action}','ok':False,'error':'未知操作'}})")
        
        script_lines.append("final_screenshot = '/tmp/agent_final.png'")
        script_lines.append("try:\n    page.screenshot(path=final_screenshot, full_page=False)\nexcept:\n    final_screenshot = None")
        script_lines.append("print('RESULTS:', json.dumps(outputs, ensure_ascii=False))")
        script_lines.append("print('FINAL_SCREENSHOT:', final_screenshot or 'none')")
        script_lines.append("browser.close()\np.stop()")
        
        script = "\n".join(script_lines)
        
        with tempfile.NamedTemporaryFile(suffix=".py", mode="w", delete=False) as f:
            f.write(script); tmp = f.name
        
        result = subprocess.run(["python3", tmp], capture_output=True, text=True, timeout=60)
        os.unlink(tmp)
        
        # 解析结果
        for line in result.stdout.split('\n'):
            if line.startswith('RESULTS:'):
                try: results = json.loads(line[8:].strip())
                except: pass
        
        # 读取截图
        for i in range(len(steps)):
            shot_path = f"/tmp/agent_shot_{i}.png"
            if os.path.exists(shot_path):
                try:
                    with open(shot_path, "rb") as f:
                        screenshots.append({"step":i,"base64":base64.b64encode(f.read()).decode()})
                    os.unlink(shot_path)
                except: pass
        
        final_shot_path = "/tmp/agent_final.png"
        final_screenshot = None
        if os.path.exists(final_shot_path):
            try:
                with open(final_shot_path, "rb") as f:
                    final_screenshot = base64.b64encode(f.read()).decode()
                os.unlink(final_shot_path)
            except: pass
        
        # Step 3: AI总结执行结果
        result_summary = json.dumps([{"step":r.get("step"),"action":r.get("action"),"ok":r.get("ok"),"detail":str(r)[:200]} for r in results], ensure_ascii=False)
        summary = await _call_ai([
            {"role":"system","content":"你是浏览器自动化结果分析师。简明总结执行结果，提取关键数据和发现。"},
            {"role":"user","content":f"任务: {req.command}\n步骤计划: {plan_text[:500]}\n执行结果: {result_summary}\n\n请用3-5句话总结完成了什么，提取了哪些关键信息。"}
        ], max_tokens=300)
        
        return {
            "ok": True,
            "command": req.command,
            "plan": steps,
            "results": results,
            "summary": summary,
            "screenshots": screenshots,
            "final_screenshot": final_screenshot,
            "steps_executed": len([r for r in results if r.get("ok")]),
            "steps_total": len(steps)
        }
        
    except subprocess.TimeoutExpired:
        return {"ok": False, "error": "浏览器操作超时(60秒)", "plan": steps}
    except Exception as e:
        return {"ok": False, "error": str(e), "plan": steps}

# ===== 浏览器Agent快捷任务 =====
@router.post("/browser/quick")
async def browser_quick(req: dict, _=Depends(verify_token)):
    """快捷浏览器任务 — 竞品采集/商品截图/页面监控"""
    task_type = req.get("type","")
    url = req.get("url","")
    selector = req.get("selector","")
    
    commands = {
        "screenshot": f"打开 {url} 并截图",
        "prices": f"打开 {url} 提取所有价格信息",
        "products": f"打开 {url} 提取商品列表(名称+价格+链接)",
        "monitor": f"打开 {url} 截图并提取页面主要变化",
        "login_check": f"打开 {url} 检查是否需要登录",
    }
    
    cmd = commands.get(task_type, req.get("command", f"打开 {url}"))
    req_obj = BrowserAgentRequest(command=cmd, headless=True, max_steps=8)
    return await browser_agent(req_obj, _)
# ===== 8. 长上下文记忆压缩 =====
class MemoryRequest(BaseModel):
    conversation_id: str = ""

@router.post("/memory/compress")
async def compress_memory(req: MemoryRequest, _=Depends(verify_token)):
    """压缩长对话为摘要 — 突破上下文限制"""
    try:
        from routers.agent_chat import _cdb
        c = _cdb()
        msgs = c.execute("SELECT role,content FROM msgs WHERE cid=? ORDER BY id",(req.conversation_id,)).fetchall()
        c.close()
        
        if len(msgs) < 20:
            return {"ok":True,"compressed":False,"message":"对话较短，无需压缩"}
        
        full_text = "\n".join([f"{r[0]}: {r[1][:200]}" for r in msgs])
        summary = await _call_ai([
            {"role":"system","content":"你是对话摘要专家。将以下长对话压缩为简洁摘要，保留关键信息、决策、待办事项。"},
            {"role":"user","content":f"对话({len(msgs)}条消息):\n{full_text[:4000]}\n\n请生成摘要(不超过300字)。"}
        ], max_tokens=400)
        
        return {"ok":True,"compressed":True,"original_messages":len(msgs),"summary":summary}
    except Exception as e:
        return {"ok":False,"error":str(e)}


# ===== 8.5 远程电脑控制 WebSocket =====
connected_remotes = {}  # {client_id: websocket}

@router.websocket("/remote/ws")
async def remote_control_ws(ws: WebSocket):
    """远程电脑控制WebSocket — 本地Agent连接后，AI可操控本地电脑"""
    await ws.accept()
    client_id = None
    
    try:
        while True:
            data = await ws.receive_json()
            msg_type = data.get("type","")
            
            if msg_type == "register":
                client_id = data.get("client_id","unknown")
                hostname = data.get("hostname","")
                connected_remotes[client_id] = ws
                await ws.send_json({"type":"registered","client_id":client_id})
                # 广播新连接
                for cid, cws in connected_remotes.items():
                    try: await cws.send_json({"type":"peer_update","clients":list(connected_remotes.keys())})
                    except: pass
            
            elif msg_type == "ping":
                await ws.send_json({"type":"pong"})
            
            elif msg_type == "result":
                # 客户端执行结果回传
                target = data.get("target","")
                if target in connected_remotes:
                    try:
                        await connected_remotes[target].send_json({
                            "type":"remote_result",
                            "action":data.get("action"),
                            "ok":data.get("ok"),
                            "data":data.get("data"),
                            "screenshot":data.get("screenshot"),
                            "error":data.get("error")
                        })
                    except: pass
            
            elif msg_type == "screenshot":
                # 截图回传
                target = data.get("target","")
                if target in connected_remotes:
                    try:
                        await connected_remotes[target].send_json({
                            "type":"screenshot_data",
                            "base64":data.get("base64","")
                        })
                    except: pass
                    
    except WebSocketDisconnect:
        if client_id:
            connected_remotes.pop(client_id, None)
            for cws in connected_remotes.values():
                try: await cws.send_json({"type":"peer_update","clients":list(connected_remotes.keys())})
                except: pass

@router.get("/remote/clients")
async def list_remote_clients(_=Depends(verify_token)):
    """列出已连接的远程电脑"""
    return {"ok":True,"clients":list(connected_remotes.keys()),"count":len(connected_remotes)}

@router.post("/remote/execute")
async def execute_remote(req: dict, _=Depends(verify_token)):
    """向远程电脑发送控制指令"""
    client_id = req.get("client_id","")
    action = req.get("action","")
    params = req.get("params",{})
    
    if client_id not in connected_remotes:
        return {"ok":False,"error":f"客户端 {client_id} 未连接","available":list(connected_remotes.keys())}
    
    try:
        ws = connected_remotes[client_id]
        await ws.send_json({"type":"execute","action":action,"params":params})
        return {"ok":True,"sent":action,"to":client_id}
    except Exception as e:
        connected_remotes.pop(client_id, None)
        return {"ok":False,"error":str(e)}

# ===== 本地Agent下载 =====
@router.get("/remote/agent-script")
async def download_agent_script():
    """下载本地电脑Agent脚本"""
    script = '''"""
Friday AI 本地控制Agent — 运行在你的电脑上，让AI操控你的桌面
用法: pip install playwright pyautogui websockets pillow
      python friday_agent.py
"""
import asyncio, json, base64, os, sys, io, subprocess, re
from pathlib import Path
from datetime import datetime

SERVER = "wss://tiktook.eu.cc/agent/advanced/remote/ws"  # 改成你的服务器地址
import socket
CLIENT_ID = socket.gethostname()

def screenshot_to_base64():
    """截取屏幕"""
    try:
        from PIL import ImageGrab
        img = ImageGrab.grab()
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        return base64.b64encode(buf.getvalue()).decode()
    except:
        return None

async def execute_action(action, params):
    """执行控制指令"""
    try:
        if action == "screenshot":
            b64 = screenshot_to_base64()
            return {"ok":True,"screenshot":b64}
        
        elif action == "open_url":
            url = params.get("url","")
            import webbrowser
            webbrowser.open(url)
            return {"ok":True,"opened":url}
        
        elif action == "click":
            x, y = params.get("x",0), params.get("y",0)
            import pyautogui
            pyautogui.click(x, y)
            return {"ok":True,"clicked":[x,y]}
        
        elif action == "type_text":
            text = params.get("text","")
            import pyautogui
            pyautogui.write(text, interval=0.05)
            return {"ok":True,"typed":text}
        
        elif action == "press_key":
            key = params.get("key","enter")
            import pyautogui
            pyautogui.press(key)
            return {"ok":True,"key":key}
        
        elif action == "run_command":
            cmd = params.get("command","")
            r = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
            return {"ok":True,"stdout":r.stdout[:2000],"stderr":r.stderr[:1000]}
        
        elif action == "get_info":
            import platform, psutil
            return {"ok":True,"hostname":socket.gethostname(),"os":platform.system(),
                    "cpu":psutil.cpu_percent(),"memory":psutil.virtual_memory().percent,
                    "disk":psutil.disk_usage('/').percent}
        
        elif action == "open_app":
            app = params.get("name","")
            import subprocess
            if os.name == 'nt':
                subprocess.Popen(app, shell=True)
            else:
                subprocess.Popen([app])
            return {"ok":True,"opened":app}
        
        elif action == "scroll":
            amount = params.get("amount", -500)
            import pyautogui
            pyautogui.scroll(amount)
            return {"ok":True,"scrolled":amount}
        
        elif action == "move_mouse":
            x, y = params.get("x",0), params.get("y",0)
            import pyautogui
            pyautogui.moveTo(x, y, duration=0.5)
            return {"ok":True,"moved_to":[x,y]}
        
        else:
            return {"ok":False,"error":f"未知操作: {action}"}
    except Exception as e:
        return {"ok":False,"error":str(e)}

async def main():
    import websockets
    print(f"[Friday Agent] 启动中... 客户端ID: {CLIENT_ID}")
    print(f"[Friday Agent] 服务器: {SERVER}")
    
    while True:
        try:
            async with websockets.connect(SERVER) as ws:
                await ws.send(json.dumps({"type":"register","client_id":CLIENT_ID,"hostname":CLIENT_ID}))
                print(f"[Friday Agent] ✅ 已连接")
                
                async def heartbeat():
                    while True:
                        await asyncio.sleep(25)
                        try: await ws.send(json.dumps({"type":"ping"}))
                        except: break
                
                asyncio.create_task(heartbeat())
                
                async for msg in ws:
                    data = json.loads(msg)
                    if data.get("type") == "execute":
                        action = data.get("action","")
                        params = data.get("params",{})
                        print(f"[执行] {action} {params}")
                        result = await execute_action(action, params)
                        # 执行后自动截图
                        if action != "screenshot":
                            shot = screenshot_to_base64()
                            if shot: result["screenshot"] = shot
                        await ws.send(json.dumps({
                            "type":"result","target":CLIENT_ID,
                            "action":action,"ok":result.get("ok",False),
                            "data":json.dumps(result,ensure_ascii=False),
                            "screenshot":result.get("screenshot"),
                            "error":result.get("error")
                        }))
        except Exception as e:
            print(f"[Friday Agent] 断开: {e}, 3秒后重连...")
            await asyncio.sleep(3)

if __name__ == "__main__":
    asyncio.run(main())
'''
    return {
        "ok":True,
        "filename":"friday_agent.py",
        "script":script,
        "instructions":"pip install websockets pyautogui pillow psutil playwright && python friday_agent.py",
        "usage":"运行后在你的电脑上，AI就可以：截图/打开网页/点击/打字/按键/运行命令/打开应用/滚动/移动鼠标"
    }


# ===== 8.6 像人一样的AI Agent — 视觉循环: 看→想→做→再看 =====
@router.post("/agent/human")
async def human_like_agent(req: dict, _=Depends(verify_token)):
    """像人一样操控电脑 — 视觉理解→决策→操作→验证 循环"""
    command = req.get("command","")
    target = req.get("target","server")  # server | remote_client_id
    max_cycles = req.get("max_cycles", 10)
    
    action_log = []
    final_result = ""
    
    # 系统提示词 — 让AI像人一样思考
    system_prompt = """你是一个能操控电脑的AI Agent。你可以看到屏幕截图，你需要完成任务。

每次我给你一张截图，你回复一个JSON:
{
  "observation": "你看到了什么(一句话)",
  "thought": "你的思考过程(下一步该做什么)",
  "action": "screenshot|click|type|scroll|open|press|done|fail",
  "params": {"x": 数字, "y": 数字, "text": "文字", "url": "网址", "key": "按键"},
  "confidence": 0.0-1.0
}

可用操作:
- screenshot: 再看一次屏幕
- click: 点击坐标 (params: x, y)
- type: 输入文字 (params: text)
- scroll: 滚动 (params: amount, 正数向上)
- open: 打开网址 (params: url)  
- press: 按键 (params: key, 如 enter/tab/escape)
- done: 任务完成 (params: summary 总结)
- fail: 任务无法完成 (params: reason)

坐标范围: x: 0-1280, y: 0-900。谨慎精确。如果卡住了尝试其他方法。"""

    cycle = 0
    last_screenshot = None
    
    while cycle < max_cycles:
        cycle += 1
        
        # Step 1: 截图
        screenshot_b64 = None
        if target == "server":
            try:
                script = f"""
from playwright.sync_api import sync_playwright
p = sync_playwright().start()
browser = p.chromium.launch(headless=True)
page = browser.new_page(viewport={{'width':1280,'height':900}})
try:
    # 尝试重用已有页面
    page.screenshot(path='/tmp/human_shot.png')
except:
    page.goto('about:blank')
    page.screenshot(path='/tmp/human_shot.png')
browser.close()
p.stop()
print('OK')
"""
                with tempfile.NamedTemporaryFile(suffix=".py",mode="w",delete=False) as f:
                    f.write(script); tmp = f.name
                subprocess.run(["python3",tmp],capture_output=True,text=True,timeout=15)
                os.unlink(tmp)
                if os.path.exists("/tmp/human_shot.png"):
                    with open("/tmp/human_shot.png","rb") as f:
                        screenshot_b64 = base64.b64encode(f.read()).decode()
                    os.unlink("/tmp/human_shot.png")
            except: pass
        elif target in connected_remotes:
            # 请求远程截图
            ws = connected_remotes[target]
            await ws.send_json({"type":"execute","action":"screenshot","params":{}})
            # 等待截图返回
            for _ in range(30):
                try:
                    data = await asyncio.wait_for(ws.receive_json(), timeout=3.0)
                    if data.get("type") == "screenshot_data":
                        screenshot_b64 = data.get("base64")
                        break
                    elif data.get("type") == "result" and data.get("action") == "screenshot":
                        screenshot_b64 = data.get("screenshot")
                        break
                except: break
        
        if not screenshot_b64 and cycle == 1:
            return {"ok":False,"error":"无法获取屏幕截图","cycle":cycle}
        if not screenshot_b64:
            action_log.append({"cycle":cycle,"action":"screenshot","error":"截图失败"})
            break
        
        last_screenshot = screenshot_b64
        
        # Step 2: AI视觉理解 + 决策
        user_prompt = f"任务: {command}\n这是第{cycle}次观察。\n之前操作: {json.dumps(action_log[-5:],ensure_ascii=False)}\n请分析截图并决定下一步。"
        
        ai_response = await _call_ai([
            {"role":"system","content":system_prompt},
            {"role":"user","content":[
                {"type":"text","text":user_prompt},
                {"type":"image_url","image_url":{"url":f"data:image/png;base64,{screenshot_b64}","detail":"high"}}
            ]}
        ], model="gpt-4o", max_tokens=500, temperature=0.3)
        
        # Step 3: 解析AI决策
        decision = {}
        try:
            json_match = re.search(r'\{[^{}]*"action"[^{}]*\}', ai_response, re.DOTALL)
            if json_match:
                decision = json.loads(json_match.group())
        except: pass
        
        if not decision:
            action_log.append({"cycle":cycle,"ai_response":ai_response[:200],"error":"AI响应解析失败"})
            continue
        
        action = decision.get("action","screenshot")
        params = decision.get("params",{})
        observation = decision.get("observation","")
        thought = decision.get("thought","")
        
        action_log.append({
            "cycle":cycle,
            "observation":observation,
            "thought":thought,
            "action":action,
            "params":params
        })
        
        # Step 4: 执行操作
        if action == "done":
            final_result = params.get("summary",observation)
            return {"ok":True,"completed":True,"cycles":cycle,"log":action_log,"result":final_result,"screenshot":last_screenshot}
        
        if action == "fail":
            return {"ok":False,"error":params.get("reason","任务失败"),"cycles":cycle,"log":action_log}
        
        if target == "server":
            # 服务器Playwright执行
            try:
                script = f"""
from playwright.sync_api import sync_playwright
p = sync_playwright().start()
browser = p.chromium.launch(headless=True)
page = browser.new_page(viewport={{'width':1280,'height':900}})
try:
"""
                if action == "click":
                    script += f"    page.mouse.click({params.get('x',640)},{params.get('y',450)})\n"
                elif action == "type":
                    script += f"    page.keyboard.type('{params.get('text','')}', delay=50)\n"
                elif action == "scroll":
                    script += f"    page.mouse.wheel(0,{params.get('amount',-300)})\n"
                elif action == "press":
                    script += f"    page.keyboard.press('{params.get('key','enter')}')\n"
                elif action == "open" and params.get("url"):
                    script += f"    page.goto('{params.get('url')}',wait_until='domcontentloaded')\n"
                else:
                    script += f"    page.keyboard.press('{params.get('key','enter')}')\n"
                
                script += """    page.screenshot(path='/tmp/human_shot.png')
except Exception as e:
    print(f'ERROR: {e}')
browser.close()
p.stop()
print('OK')
"""
                with tempfile.NamedTemporaryFile(suffix=".py",mode="w",delete=False) as f:
                    f.write(script); tmp = f.name
                subprocess.run(["python3",tmp],capture_output=True,text=True,timeout=20)
                os.unlink(tmp)
            except Exception as e:
                action_log[-1]["error"] = str(e)
        
        elif target in connected_remotes:
            # 远程电脑执行
            try:
                ws = connected_remotes[target]
                remote_action = action
                if action == "open": remote_action = "open_url"
                await ws.send_json({"type":"execute","action":remote_action,"params":params})
                action_log[-1]["remote"] = target
            except Exception as e:
                action_log[-1]["error"] = str(e)
    
    return {"ok":False,"error":"达到最大循环次数","cycles":cycle,"log":action_log,"partial_result":final_result,"screenshot":last_screenshot}

# ===== 远程电脑快速操控 =====
@router.post("/agent/quick")
async def quick_agent_action(req: dict, _=Depends(verify_token)):
    """快速操控远程电脑 — 单个动作"""
    client_id = req.get("client_id","")
    action = req.get("action","")
    params = req.get("params",{})
    
    actions_help = {
        "screenshot":"截取屏幕",
        "open_url":"打开网址(params.url)",
        "click":"点击坐标(params.x,params.y)",
        "type_text":"输入文字(params.text)",
        "press_key":"按键(params.key: enter/tab/escape/win)",
        "run_command":"运行命令(params.command)",
        "get_info":"获取系统信息",
        "open_app":"打开应用(params.name: chrome/excel/word)",
        "scroll":"滚轮(params.amount: 正数向上)",
        "move_mouse":"移动鼠标(params.x,params.y)",
        "browser_task":"浏览器任务(params.command: 自然语言)"
    }
    
    if not client_id:
        return {"ok":False,"error":"请指定client_id","available_clients":list(connected_remotes.keys()),"actions":actions_help}
    
    if client_id not in connected_remotes:
        return {"ok":False,"error":f"客户端 {client_id} 未连接","available":list(connected_remotes.keys())}
    
    if action == "screenshot":
        # 专门处理截图（需要等回传）
        ws = connected_remotes[client_id]
        await ws.send_json({"type":"execute","action":"screenshot","params":{}})
        for _ in range(20):
            try:
                data = await asyncio.wait_for(ws.receive_json(), timeout=3.0)
                if data.get("type") == "result" and data.get("screenshot"):
                    return {"ok":True,"action":action,"screenshot":data.get("screenshot")}
            except: break
        return {"ok":False,"error":"截图超时"}
    
    return await execute_remote(req, _)

@router.get("/agent/actions")
async def list_actions(_=Depends(verify_token)):
    """列出所有可用的远程操控动作"""
    return {"ok":True,"actions":{
        "screenshot":"截取屏幕",
        "open_url":"打开网址",
        "click":"点击坐标",
        "type_text":"输入文字",
        "press_key":"按键(enter/tab/escape/win/r)",
        "run_command":"运行系统命令",
        "get_info":"获取系统信息(CPU/内存/磁盘)",
        "open_app":"打开应用(chrome/excel/word/notepad)",
        "scroll":"滚轮滚动",
        "move_mouse":"移动鼠标到坐标",
        "browser_task":"AI浏览器任务(自然语言)"
    }}

# ===== 统一浏览器Agent(支持远程) =====
@router.post("/browser/unified")
async def unified_browser(req: dict, _=Depends(verify_token)):
    """统一浏览器Agent — 自动选择服务器或远程电脑执行"""
    command = req.get("command","")
    target = req.get("target","server")  # server | {client_id}
    
    if target == "server" or target in list(connected_remotes.keys()):
        if target != "server":
            # 发给远程电脑
            if target not in connected_remotes:
                return {"ok":False,"error":f"客户端 {target} 未连接"}
            ws = connected_remotes[target]
            await ws.send_json({"type":"execute","action":"browser_task","params":{"command":command}})
            return {"ok":True,"sent_to":target,"command":command}
        else:
            # 服务器Playwright
            req_obj = BrowserAgentRequest(command=command, headless=True, max_steps=10)
            return await browser_agent(req_obj, _)
    
    return {"ok":False,"error":"未知目标","available_targets":["server"]+list(connected_remotes.keys())}

# ===== 9. AI通知推送 =====
@router.post("/notify")
async def send_notification(req: dict, _=Depends(verify_token)):
    """推送通知到所有连接的客户端"""
    title = req.get("title","Friday AI")
    body = req.get("body","")
    url = req.get("url","/ai/")
    
    # 通过WebSocket广播通知
    try:
        from routers.ws_router import manager
        await manager.broadcast(json.dumps({
            "type":"notification",
            "title":title,"body":body,"url":url,"time":datetime.now().isoformat()
        }))
        return {"ok":True,"message":"通知已广播"}
    except Exception as e:
        return {"ok":False,"error":str(e)}