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

# ===== 7. 浏览器自动化 =====
class BrowserRequest(BaseModel):
    action: str = "screenshot"  # screenshot | search | extract
    url: str = ""
    selector: str = ""

@router.post("/browser")
async def browser_action(req: BrowserRequest, _=Depends(verify_token)):
    """Playwright浏览器自动化"""
    try:
        import subprocess, tempfile
        
        script = ""
        if req.action == "screenshot":
            script = f"""
from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    page.goto("{req.url}", timeout=15000)
    page.screenshot(path="/tmp/screenshot.png", full_page=True)
    browser.close()
print("OK:screenshot")
"""
        elif req.action == "search":
            query = req.url or "test"
            script = f"""
from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    page.goto("https://www.google.com/search?q={query}", timeout=15000)
    results = page.query_selector_all(".g")
    for i,r in enumerate(results[:5]):
        title = r.query_selector("h3")
        link = r.query_selector("a")
        if title and link:
            print(f"{{i+1}}. {{title.inner_text()}} - {{link.get_attribute('href')}}")
    browser.close()
"""
        else: return {"ok":False,"error":"未知操作"}
        
        with tempfile.NamedTemporaryFile(suffix=".py",mode="w",delete=False) as f:
            f.write(script); tmp = f.name
        
        result = subprocess.run(["python3",tmp],capture_output=True,text=True,timeout=30)
        os.unlink(tmp)
        
        if req.action == "screenshot" and os.path.exists("/tmp/screenshot.png"):
            with open("/tmp/screenshot.png","rb") as f:
                b64 = base64.b64encode(f.read()).decode()
            return {"ok":True,"action":req.action,"screenshot_base64":b64}
        
        return {"ok":True,"action":req.action,"output":result.stdout[:2000],"error":result.stderr[:500]}
    except Exception as e:
        return {"ok":False,"error":str(e)}

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