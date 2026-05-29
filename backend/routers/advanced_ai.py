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
    """远程电脑控制WebSocket - 本地Agent连接后，AI可操控本地电脑"""
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
                await ws.send_json({"type":"registered","client_id":client_id,"message":"已注册"})
                for cid, cws in connected_remotes.items():
                    try: await cws.send_json({"type":"peer_update","clients":list(connected_remotes.keys())})
                    except: pass
            elif msg_type == "ping":
                await ws.send_json({"type":"pong"})
            elif msg_type == "result":
                target = data.get("target","")
                if target in connected_remotes:
                    try:
                        await connected_remotes[target].send_json({"type":"remote_result","action":data.get("action"),"ok":data.get("ok"),"data":data.get("data"),"screenshot":data.get("screenshot"),"error":data.get("error")})
                    except: pass
            elif msg_type == "screenshot_data":
                target = data.get("target","")
                if target in connected_remotes:
                    try: await connected_remotes[target].send_json({"type":"screenshot_data","base64":data.get("base64","")})
                    except: pass
    except WebSocketDisconnect:
        if client_id:
            connected_remotes.pop(client_id, None)
            for cws in connected_remotes.values():
                try: await cws.send_json({"type":"peer_update","clients":list(connected_remotes.keys())})
                except: pass

@router.get("/remote/clients")
async def list_remote_clients(_=Depends(verify_token)):
    return {"ok":True,"clients":list(connected_remotes.keys()),"count":len(connected_remotes)}

@router.post("/remote/execute")
async def execute_remote(req: dict, _=Depends(verify_token)):
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

# ===== 本地Agent下载 v2.0 =====
async def download_agent_script():
    """下载本地Agent脚本 v2.0 - 人类级电脑操控"""
    script = """"""
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
        print(f"\n[致命错误] {e}")"""
    return {
        "ok": True,
        "version": "2.0",
        "filename": "friday_agent.py",
        "script": script,
        "instructions": "pip install websockets pyautogui pillow psutil playwright pytesseract opencv-python pyperclip && playwright install chromium && python friday_agent.py",
        "capabilities": ["截图+视觉理解","智能元素定位(OCR/图像/坐标)","21种动作","双击/右键/拖拽","快捷键","窗口管理","浏览器自动化","系统命令","自纠错"]
    }


# ===== 人形Agent（升级版）=====
@router.post("/agent/human")
async def human_like_agent(req: dict, _=Depends(verify_token)):
    """人类级电脑操控 - 智能路由: 代码任务直接执行, GUI任务视觉操控, 自动省钱"""
    command = req.get("command","")
    target = req.get("target","server")
    max_cycles = req.get("max_cycles", 8)
    action_log = []
    
    # ===== 第0步: 任务智能分类 =====
    classify_prompt = f"""判断这个任务属于哪一类,只回复一个词:
- "code": 代码/文件/服务器/命令/数据处理 (不需要看屏幕)
- "gui": 操控桌面应用/GUI/浏览器/需要看屏幕
任务: {command}
分类:"""
    
    task_type = (await _call_ai(
        [{"role":"user","content":classify_prompt}],
        model="gpt-3.5-turbo", max_tokens=10, temperature=0
    )).strip().lower()
    
    if "code" in task_type:
        # ===== 代码/服务器任务: 零截图,直接执行 =====
        code_prompt = f"""你是服务器管理AI。完成这个任务,回复JSON:
{{"steps":[{{"action":"run_command|read_file|write_file|search|done","params":{{}},"reason":"为什么"}}],"summary":"总结"}}
可用操作: run_command(执行shell), read_file(读文件), write_file(写文件), search(搜索内容), done(完成)
任务: {command}
JSON:"""
        
        plan = await _call_ai(
            [{"role":"user","content":code_prompt}],
            model="gpt-4o-mini", max_tokens=600, temperature=0.2
        )
        
        steps = []
        try:
            j = json.loads(re.search(r'{[^{}]*"steps"[^{}]*}', plan, re.DOTALL).group())
            steps = j.get("steps",[])
        except: pass
        
        results = []
        for step in steps[:max_cycles]:
            a = step.get("action","")
            p = step.get("params",{})
            action_log.append({"action":a,"params":p,"reason":step.get("reason","")})
            
            try:
                if a == "run_command":
                    r = subprocess.run(p.get("command",""), shell=True, capture_output=True, text=True, timeout=30)
                    results.append(f"[{a}] stdout:{r.stdout[:500]} stderr:{r.stderr[:200]}")
                elif a == "read_file":
                    path = p.get("path","")
                    if os.path.exists(path):
                        with open(path,"r",errors="ignore") as f:
                            results.append(f"[read] {path}: {f.read()[:2000]}")
                    else:
                        results.append(f"[read] {path}: 文件不存在")
                elif a == "write_file":
                    path = p.get("path",""); txt = p.get("content","")
                    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
                    with open(path,"w") as f: f.write(txt)
                    results.append(f"[write] {path}: 已写入{len(txt)}字符")
                elif a == "search":
                    import glob
                    pattern = p.get("pattern","*")
                    found = glob.glob(pattern, recursive=True)[:20]
                    results.append(f"[search] {pattern}: {found}")
                elif a == "done":
                    break
            except Exception as e:
                results.append(f"[{a}] 错误: {str(e)[:200]}")
        
        # 做一次最终总结 (便宜模型)
        summary = await _call_ai([
            {"role":"user","content":f"任务:{command}\n执行结果:\n"+'\n'.join(results)+"\n\n请一句话总结完成情况。"}
        ], model="gpt-3.5-turbo", max_tokens=100, temperature=0)
        
        token_estimate = len(classify_prompt) + len(plan) + len(summary) + 300
        return {
            "ok":True, "completed":True, "mode":"code", "cycles":len(action_log),
            "log":action_log, "results":results, "final_result":summary,
            "token_saved": True, "estimated_tokens": token_estimate,
            "vs_visual_mode": f"省了约{(max_cycles*1500 - token_estimate)//1000}k tokens"
        }
    
    # ===== GUI任务: 视觉操控(优化版) =====
    system_prompt = """你是电脑操控AI。看到截图后回复JSON: {"observation":"看到了什么","thought":"思考","action":"操作名","target":"元素描述(文本:xxx/坐标:x,y)","params":{},"confidence":0.8}
操作: click|double_click|type_text|press_key|scroll|move|wait|open_app|close_window|switch_window|select_all|copy|paste|undo|save|run_command|done|fail
原则: 用target描述元素(如"文本:登录"), 操作后验证, 卡住换策略。"""
    
    cycle = 0
    last_screenshot = None
    last_action = None  # 避免重复截图
    
    while cycle < max_cycles:
        cycle += 1
        
        # 只在必要时截图 (连续打字/按键后不需要)
        need_screenshot = last_action not in ("type_text","press_key","wait")
        
        screenshot_b64 = None
        if need_screenshot or cycle == 1:
            if target == "server":
                try:
                    script = "from playwright.sync_api import sync_playwright\np = sync_playwright().start()\nbrowser = p.chromium.launch(headless=True)\npage = browser.new_page(viewport={'width':1024,'height':768})\ntry:\n    page.screenshot(path='/tmp/human_shot.png')\nexcept:\n    page.goto('about:blank')\n    page.screenshot(path='/tmp/human_shot.png')\nbrowser.close()\np.stop()"
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
                try:
                    ws = connected_remotes[target]
                    await ws.send_json({"type":"execute","action":"screenshot","params":{}})
                    for _ in range(30):
                        try:
                            data = await asyncio.wait_for(ws.receive_json(), timeout=3.0)
                            if data.get("type") == "result" and data.get("screenshot"):
                                screenshot_b64 = data.get("screenshot"); break
                        except: break
                except: pass
        
        if not screenshot_b64 and cycle == 1:
            return {"ok":False,"error":"无法获取屏幕截图","cycle":cycle}
        if not screenshot_b64:
            action_log.append({"cycle":cycle,"error":"截图失败"}); break
        
        last_screenshot = screenshot_b64
        
        # 模型选择: 前3步用gpt-4o-mini(便宜10倍), 卡住了才用gpt-4o
        use_model = "gpt-4o-mini" if cycle <= 3 else "gpt-4o"
        user_prompt = f"任务: {command}\n第{cycle}/{max_cycles}步。\n之前操作: {json.dumps(action_log[-3:],ensure_ascii=False)}\n分析截图,用target描述元素。"
        
        ai_response = await _call_ai([
            {"role":"system","content":system_prompt},
            {"role":"user","content":[{"type":"text","text":user_prompt},{"type":"image_url","image_url":{"url":f"data:image/png;base64,{screenshot_b64}","detail":"low"}}]}  # low detail = 更便宜
        ], model=use_model, max_tokens=300, temperature=0.3)
        
        decision = {}
        try:
            json_match = re.search(r'\{[^{}]*"action"[^{}]*\}', ai_response, re.DOTALL)
            if json_match: decision = json.loads(json_match.group())
        except: pass
        
        if not decision:
            action_log.append({"cycle":cycle,"error":"解析失败"}); continue
        
        action = decision.get("action","screenshot")
        params = decision.get("params",{})
        last_action = action
        
        action_log.append({"cycle":cycle,"observation":decision.get("observation","")[:80],"thought":decision.get("thought","")[:80],"action":action,"target":decision.get("target","")})
        
        if action == "done":
            return {"ok":True,"completed":True,"mode":"gui","cycles":cycle,"log":action_log,"result":params.get("summary",""),"screenshot":last_screenshot,"model":"gpt-4o-mini","estimated_tokens":cycle*500}
        if action == "fail":
            return {"ok":False,"error":params.get("reason","任务失败"),"mode":"gui","cycles":cycle,"log":action_log}
        
        if target == "server":
            try:
                script = f"from playwright.sync_api import sync_playwright\np = sync_playwright().start()\nbrowser = p.chromium.launch(headless=True)\npage = browser.new_page(viewport={{'width':1024,'height':768}})\ntry:\n"
                if action == "click": script += f"    page.mouse.click({params.get('x',512)},{params.get('y',384)})\n"
                elif action == "double_click": script += f"    page.mouse.dblclick({params.get('x',512)},{params.get('y',384)})\n"
                elif action == "type_text": script += f"    page.keyboard.type('{params.get('text','')}', delay=30)\n"
                elif action == "scroll": script += f"    page.mouse.wheel(0,{params.get('amount',-300)})\n"
                elif action == "press_key": script += f"    page.keyboard.press('{params.get('key','enter')}')\n"
                elif action == "run_command": script += f"    import subprocess; subprocess.run('{params.get('command','')}',shell=True)\n"
                else: script += f"    page.keyboard.press('{params.get('key','enter')}')\n"
                script += "    page.screenshot(path='/tmp/human_shot.png')\nexcept Exception as e:\n    print(f'ERROR: {e}')\nbrowser.close()\np.stop()"
                with tempfile.NamedTemporaryFile(suffix=".py",mode="w",delete=False) as f:
                    f.write(script); tmp = f.name
                subprocess.run(["python3",tmp],capture_output=True,text=True,timeout=20)
                os.unlink(tmp)
            except Exception as e:
                action_log[-1]["error"] = str(e)[:100]
        elif target in connected_remotes:
            try:
                ws = connected_remotes[target]
                await ws.send_json({"type":"execute","action":action,"params":params,"task_id":str(cycle)})
                action_log[-1]["remote"] = target
            except Exception as e:
                action_log[-1]["error"] = str(e)[:100]
    
    return {"ok":False,"error":"达到最大循环次数","mode":"gui","cycles":cycle,"log":action_log,"screenshot":last_screenshot,"estimated_tokens":cycle*500}

@router.post("/agent/quick")
async def quick_agent_action(req: dict, _=Depends(verify_token)):
    client_id = req.get("client_id","")
    action = req.get("action","")
    params = req.get("params",{})
    actions_help = {"screenshot":"截取屏幕","open_url":"打开网址","click":"单击","double_click":"双击","right_click":"右键","type_text":"输入文字","press_key":"按键","run_command":"运行命令","get_info":"系统信息","open_app":"打开应用","scroll":"滚轮","move_mouse":"移动鼠标","close_window":"关闭窗口","switch_window":"切换窗口","select_all":"全选","copy":"复制","paste":"粘贴","undo":"撤销","save":"保存","browser_task":"浏览器任务"}
    if not client_id: return {"ok":False,"error":"请指定client_id","available_clients":list(connected_remotes.keys()),"actions":actions_help}
    if client_id not in connected_remotes: return {"ok":False,"error":f"客户端 {client_id} 未连接","available":list(connected_remotes.keys())}
    if action == "screenshot":
        ws = connected_remotes[client_id]
        await ws.send_json({"type":"execute","action":"screenshot","params":{}})
        for _ in range(20):
            try:
                data = await asyncio.wait_for(ws.receive_json(), timeout=3.0)
                if data.get("type") == "result" and data.get("screenshot"): return {"ok":True,"action":action,"screenshot":data.get("screenshot")}
            except: break
        return {"ok":False,"error":"截图超时"}
    return await execute_remote(req, _)

@router.get("/agent/actions")
async def list_actions(_=Depends(verify_token)):
    return {"ok":True,"actions":{"screenshot":"截取屏幕","open_url":"打开网址","click":"单击","double_click":"双击","right_click":"右键","type_text":"输入文字","press_key":"按键","run_command":"运行系统命令","get_info":"系统信息","open_app":"打开应用","scroll":"滚轮","move_mouse":"移动鼠标","drag":"拖拽","wait":"等待","close_window":"关闭窗口","switch_window":"切换窗口","select_all":"全选","copy":"复制","paste":"粘贴","undo":"撤销","save":"保存","browser_task":"AI浏览器任务"}}

# ===== 统一浏览器Agent =====
@router.post("/browser/unified")
async def unified_browser(req: dict, _=Depends(verify_token)):
    command = req.get("command","")
    target = req.get("target","server")
    if target == "server" or target in list(connected_remotes.keys()):
        if target != "server":
            if target not in connected_remotes: return {"ok":False,"error":f"客户端 {target} 未连接"}
            ws = connected_remotes[target]
            await ws.send_json({"type":"execute","action":"browser_task","params":{"command":command}})
            return {"ok":True,"sent_to":target,"command":command}
        else:
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