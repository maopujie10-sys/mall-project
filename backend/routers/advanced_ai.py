"""__AI__ -- ______ / _____ / ____ / _____ / ____ / ____ / ______ / ____"""
import json, os, re, io, base64, asyncio, tempfile, subprocess
from pathlib import Path
from datetime import datetime
from fastapi import APIRouter, Depends, Query, WebSocket, WebSocketDisconnect
from fastapi.responses import StreamingResponse, FileResponse
from pydantic import BaseModel
from auth import verify_token
from config import OPENAI_API_KEY, OPENAI_BASE_URL, DEEPSEEK_API_KEY
import os
DEEPSEEK_BASE_URL = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com/v1")
# ____: deepseek-____DeepSeek, ____OpenAI
CHEAP_MODEL = os.getenv("CHEAP_MODEL", "deepseek-chat")
SMART_MODEL = os.getenv("SMART_MODEL", "gpt-4o")
# ===== ____ -- AI_____ =====
AVAILABLE_MODELS = {
    # ____ (____)
    "deepseek-chat":       {"provider": "deepseek", "cost": "0.14/1M",  "strength": "____/____, ____"},
    CHEAP_MODEL:       {"provider": "openai",   "cost": "0.50/1M",  "strength": "__/__/____"},
    # _____ (____)
    CHEAP_MODEL:         {"provider": "openai",   "cost": "0.15/1M",  "strength": "____/___, ____"},
    "deepseek-reasoner":   {"provider": "deepseek", "cost": "0.55/1M",  "strength": "____/____"},
    # ____ (____)
    "gpt-4o":              {"provider": "openai",   "cost": "2.50/1M",  "strength": "_____/____/___"},
    "claude-3-5-sonnet":   {"provider": "openai",   "cost": "3.00/1M",  "strength": "____/_____"},
}
def pick_model(task_complexity="auto", need_vision=False, step_count=0):
    """AI_____: ____________________"""
    if task_complexity == "simple" or (step_count > 0 and step_count <= 3):
        return CHEAP_MODEL  # _________
    elif task_complexity == "hard" or step_count > 5:
        return SMART_MODEL  # _________
    elif need_vision:
        return CHEAP_MODEL if OPENAI_KEY else CHEAP_MODEL  # _______EUR____CEUR____
    return CHEAP_MODEL


router = APIRouter(prefix="/agent/advanced", tags=["AdvancedAI"])
# __rovider
OPENAI_KEY = OPENAI_API_KEY
DEEPSEEK_KEY = DEEPSEEK_API_KEY
DS_BASE_URL = DEEPSEEK_BASE_URL
BASE_URL = OPENAI_BASE_URL or "https://api.openai.com/v1"

async def _call_ai(messages, model=None, max_tokens=1000, temperature=0.7):
    if model is None: model = CHEAP_MODEL
    """__rovider AI___ - ______DeepSeek/OpenAI"""
    import httpx
    # ___________EUR__provider
    if model.startswith("deepseek"):
        key = DEEPSEEK_KEY
        base = DS_BASE_URL
    else:
        key = OPENAI_KEY
        base = BASE_URL
    
    if not key:
        if OPENAI_KEY:
            key = OPENAI_KEY; base = BASE_URL
        elif DEEPSEEK_KEY:
            key = DEEPSEEK_KEY; base = DS_BASE_URL
        else:
            return "_EUR_____PI Key"
    
    async with httpx.AsyncClient(timeout=120) as c:
        r = await c.post(f"{base}/chat/completions",
            headers={"Authorization":f"Bearer {key}","Content-Type":"application/json"},
            json={"model":model,"messages":messages,"max_tokens":max_tokens,"temperature":temperature})
        if r.status_code == 200:
            return r.json().get("choices",[{}])[0].get("message",{}).get("content","")
        return f"API___:{r.status_code}"

# ===== 1. _________ WebSocket =====
@router.websocket("/voice/live")
async def live_voice(ws: WebSocket):
    """_________ -- ______/___/______"""
    await ws.accept()
    conversation = []
    current_task = None
    
    async def stream_ai_reply(messages):
        import httpx
        full = ""
        async with httpx.AsyncClient(timeout=60) as c:
            async with c.stream("POST",f"{BASE_URL}/chat/completions",
                headers={"Authorization":f"Bearer {API_KEY}","Content-Type":"application/json"},
                json={"model":CHEAP_MODEL,"messages":messages,"stream":True,"temperature":0.8}) as r:
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
                # ____________
                if current_task and not current_task.done():
                    current_task.cancel()
                await ws.send_json({"type":"interrupted"})
            elif msg_type == "speech":
                text = data.get("text","")
                if not text: continue
                conversation.append({"role":"user","content":text})
                await ws.send_json({"type":"status","text":"__EUR__..."})
                
                msgs = [{"role":"system","content":"___Friday AI___.____________,__EUR____________EUR____EUR________EUR__________________arkdown."}]
                msgs.extend(conversation[-15:])
                
                current_task = asyncio.create_task(stream_ai_reply(msgs))
                try:
                    full_reply = await current_task
                    conversation.append({"role":"assistant","content":full_reply})
                    await ws.send_json({"type":"done","full":full_reply})
                except asyncio.CancelledError:
                    await ws.send_json({"type":"interrupted"})
            elif msg_type == "emotion":
                # ______________
                await ws.send_json({"type":"status","text":"________ "+data.get("emotion","neutral")})
    except WebSocketDisconnect:
        pass

# ===== 2. ___________=====
class FrameRequest(BaseModel):
    image_base64: str
    context: str = ""

@router.post("/vision/live")
async def live_vision(req: FrameRequest, _=Depends(verify_token)):
    """___________-- _______"""
    prompt = "__________________EUR____________,_____EUR______________."
    if req.context: prompt = f"________{req.context}\n______:"
    
    result = await _call_ai([
        {"role":"system","content":"____________AI._EUR_______"},
        {"role":"user","content":[
            {"type":"text","text":prompt},
            {"type":"image_url","image_url":{"url":f"data:image/jpeg;base64,{req.image_base64}"}}
        ]}
    ], model=CHEAP_MODEL, max_tokens=200)
    return {"ok":True,"description":result}

# ===== 3. ______ Agent =====
class ResearchRequest(BaseModel):
    topic: str
    depth: int = 2  # ______ 1-3

@router.post("/research")
async def deep_research(req: ResearchRequest, _=Depends(verify_token)):
    """______ -- __->__->__->__"""
    import httpx
    
    # Step 1: ___________
    questions_prompt = f"____________{min(req.depth*2,5)}_________,_______________EUR__\n___:{req.topic}"
    sub_questions = await _call_ai([{"role":"user","content":questions_prompt}], max_tokens=300)
    questions = [q.strip().lstrip('0123456789.-) ') for q in sub_questions.split('\n') if q.strip()][:5]
    
    # Step 2: ___________
    findings = []
    for q in questions[:req.depth*2]:
        try:
            async with httpx.AsyncClient(timeout=15) as c:
                r = await c.get("https://html.duckduckgo.com/html/",
                    params={"q": q}, headers={"User-Agent":"Mozilla/5.0"})
                # ______
                snippets = []
                for m in re.finditer(r'class="result__snippet"[^>]*>([^<]+)', r.text):
                    snippets.append(m.group(1).strip())
                summary_text = " ".join(snippets[:3])[:500]
                if summary_text:
                    # Step 3: AI___________
                    analysis = await _call_ai([
                        {"role":"user","content":f"_____{q}\n______:{summary_text}\n___2-3____________."}
                    ], max_tokens=200)
                    findings.append({"question":q,"sources":len(snippets),"finding":analysis})
        except: findings.append({"question":q,"sources":0,"finding":"______"})
    
    # Step 4: ______
    findings_text = "\n".join([f"## {f['question']}\n{f['finding']}" for f in findings])
    report = await _call_ai([
        {"role":"system","content":"_______________________,____EUR____________________________EUR___"},
        {"role":"user","content":f"______:{req.topic}\n\n______:\n{findings_text}\n\n_____________"}
    ], max_tokens=2000)
    
    return {"ok":True,"topic":req.topic,"questions":questions,"findings":findings,"report":report}

# ===== 4. ________+ CSV___ =====
class DataAnalyzeRequest(BaseModel):
    csv_data: str = ""
    question: str = "_____________"

@router.post("/data/analyze")
async def analyze_data(req: DataAnalyzeRequest, _=Depends(verify_token)):
    """__CSV->AI____->__+____"""
    if not req.csv_data:
        return {"ok":False,"error":"_EUR__SV___"}
    
    # ___CSV
    import csv as csv_mod
    reader = csv_mod.reader(io.StringIO(req.csv_data[:50000]))
    rows = list(reader)
    if not rows: return {"ok":False,"error":"CSV___"}
    
    headers = rows[0]
    data_rows = rows[1:21]  # __0__
    row_count = len(rows) - 1
    col_count = len(headers)
    
    # ______
    stats = {"rows":row_count,"columns":col_count,"headers":headers}
    numeric_cols = []
    for ci, h in enumerate(headers):
        try:
            vals = [float(r[ci]) for r in data_rows if ci < len(r)]
            numeric_cols.append({"name":h,"index":ci,"min":min(vals),"max":max(vals),"avg":round(sum(vals)/len(vals),2),"count":len(vals)})
        except: pass
    
    # AI___
    preview = "\n".join([",".join(r) for r in [headers]+data_rows[:10]])
    prompt = "CSV__ [" + str(row_count) + "_ " + str(col_count) + "_]:\n" + \
        "__: " + str(headers) + "\n" + \
        "__: " + json.dumps(numeric_cols,ensure_ascii=False) + "\n" + \
        "_10_: " + preview[:1000] + "\n\n" + \
        "____: " + req.question + "\n\n" + \
        "___: 1 ____ 2 ____ 3 ____ 4 __.____"
    
    insight = await _call_ai([{"role":"user","content":prompt}], max_tokens=800)
    
    # ___ECharts___
    chart_config = None
    if numeric_cols:
        nc = numeric_cols[0]
        chart_config = {
            "type":"bar","title":f"{nc['name']}___",
            "labels":["min","avg","max"],
            "values":[nc["min"],nc["avg"],nc["max"]],
            "suggestion":"_________________"
        }
    
    return {"ok":True,"stats":stats,"numeric_columns":numeric_cols,"insight":insight,"chart":chart_config}

# ===== 5. ______ (PDF/Excel/Markdown) =====
class ExportRequest(BaseModel):
    content: str
    format: str = "md"  # md | html | txt
    filename: str = "report"

@router.post("/export")
async def export_file(req: ExportRequest, _=Depends(verify_token)):
    """___AI____________"""
    export_dir = Path(__file__).parent.parent / "data" / "exports"
    export_dir.mkdir(parents=True, exist_ok=True)
    
    ext_map = {"md":".md","html":".html","txt":".txt","csv":".csv","json":".json"}
    ext = ext_map.get(req.format,".txt")
    fname = f"{req.filename}_{datetime.now().strftime('%Y%m%d_%H%M%S')}{ext}"
    fpath = export_dir / fname
    
    if req.format == "html":
        html_content = "<!DOCTYPE html><html><head><meta charset=\"utf-8\"><title>" + req.filename + "</title>\n" + \
        "<style>body{font-family:Arial;max-width:800px;margin:40px auto;line-height:1.8;color:#333}\n" + \
        "h1{color:#667eea} pre{background:#f5f5f5;padding:12px;border-radius:8px}</style></head>\n" + \
        "<body>" + req.content.replace(chr(10),'<br>') + "</body></html>"
        fpath.write_text(html_content, encoding="utf-8")
    else:
        fpath.write_text(req.content, encoding="utf-8")
    
    return {"ok":True,"filename":fname,"path":str(fpath),"size":fpath.stat().st_size,"url":f"/agent/advanced/download/{fname}"}

@router.get("/download/{filename}")
async def download_file(filename: str):
    """_________"""
    fpath = Path(__file__).parent.parent / "data" / "exports" / filename
    if not fpath.exists():
        return {"ok":False,"error":"_______"}
    media_types = {".md":"text/markdown",".html":"text/html",".txt":"text/plain",".csv":"text/csv",".json":"application/json"}
    ext = fpath.suffix
    return FileResponse(fpath, media_type=media_types.get(ext,"application/octet-stream"), filename=filename)

# ===== 6. __>______+___ =====
class ScrapeRequest(BaseModel):
    url: str

@router.post("/scrape")
async def scrape_url(req: ScrapeRequest, _=Depends(verify_token)):
    """_____>_____I___"""
    import httpx
    try:
        async with httpx.AsyncClient(timeout=20) as c:
            r = await c.get(req.url, headers={"User-Agent":"Mozilla/5.0"}, follow_redirects=True)
            if r.status_code != 200:
                return {"ok":False,"error":f"HTTP {r.status_code}"}
            
            html = r.text
            # _EUR________
            text = re.sub(r'<script[^>]*>.*_</script>','',html,flags=re.DOTALL|re.I)
            text = re.sub(r'<style[^>]*>.*_</style>','',text,flags=re.DOTALL|re.I)
            text = re.sub(r'<[^>]+>',' ',text)
            text = re.sub(r'\s+',' ',text).strip()[:8000]
            
            # AI___
            summary = await _call_ai([
                {"role":"system","content":"_____>______.__-5____________,_______C_."},
                {"role":"user","content":f"URL: {req.url}\n\n___:\n{text[:5000]}"}
            ], max_tokens=300)
            
            title_match = re.search(r'<title[^>]*>([^<]+)</title>', html, re.I)
            title = title_match.group(1).strip() if title_match else req.url
            
            return {"ok":True,"url":req.url,"title":title,"text_length":len(text),"summary":summary}
    except Exception as e:
        return {"ok":False,"error":str(e)}

# ===== 7. AI_____gent -- ______________=====
class BrowserAgentRequest(BaseModel):
    command: str  # _________
    headless: bool = True
    max_steps: int = 10

@router.post("/browser/agent")
async def browser_agent(req: BrowserAgentRequest, _=Depends(verify_token)):
    """AI_____gent -- ______->______->Playwright___->AI______"""
    import httpx
    
    # Step 1: AI___________
    plan_prompt = "Browser agent plan for: " + req.command + " (max steps: " + str(req.max_steps) + ")"

    plan_text = await _call_ai([{"role":"user","content":plan_prompt}], max_tokens=800, temperature=0.3)
    
    # ______
    steps = []
    try:
        json_match = re.search(r'\[.*\]', plan_text, re.DOTALL)
        if json_match:
            steps = json.loads(json_match.group())
    except:
        # Fallback: _EUR___________
        steps = [{"action":"navigate","target":"https://www.google.com/search?q="+req.command.replace(" ","+"),"reason":"___"}]
    
    # Step 2: Playwright___
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
                # _________
                script_lines.append(f"try:\n    text = page.inner_text('body')[:3000]\n    title = page.title()\n    outputs.append({{'step':{i},'action':'extract','ok':True,'title':title,'text':text}})\nexcept Exception as e:\n    outputs.append({{'step':{i},'action':'extract','ok':False,'error':str(e)}})")
            
            elif action == "scroll":
                script_lines.append(f"try:\n    page.evaluate('window.scrollBy(0,800)')\n    outputs.append({{'step':{i},'action':'scroll','ok':True}})\nexcept Exception as e:\n    outputs.append({{'step':{i},'action':'scroll','ok':False,'error':str(e)}})")
            
            else:
                script_lines.append(f"outputs.append({{'step':{i},'action':'{action}','ok':False,'error':'______'}})")
        
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
        
        # ______
        for line in result.stdout.split('\n'):
            if line.startswith('RESULTS:'):
                try: results = json.loads(line[8:].strip())
                except: pass
        
        # ______
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
        
        # Step 3: AI_________
        result_summary = json.dumps([{"step":r.get("step"),"action":r.get("action"),"ok":r.get("ok"),"detail":str(r)[:200]} for r in results], ensure_ascii=False)
        summary = await _call_ai([
            {"role":"system","content":"_____________________EUR__EUR________,_____________"},
            {"role":"user","content":f"___: {req.command}\n______: {plan_text[:500]}\n______: {result_summary}\n\n___3-5___________________________"}
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
        return {"ok": False, "error": "___________60_", "plan": steps}
    except Exception as e:
        return {"ok": False, "error": str(e), "plan": steps}

# ===== _____gent______ =====
@router.post("/browser/quick")
async def browser_quick(req: dict, _=Depends(verify_token)):
    """___________-- ______/______/______"""
    task_type = req.get("type","")
    url = req.get("url","")
    selector = req.get("selector","")
    
    commands = {
        "screenshot": f"___ {url} ____",
        "prices": f"___ {url} ____EUR_______",
        "products": f"___ {url} _________(___+___+___)",
        "monitor": f"___ {url} ________>_______",
        "login_check": f"___ {url} _EUR__________",
    }
    
    cmd = commands.get(task_type, req.get("command", f"___ {url}"))
    req_obj = BrowserAgentRequest(command=cmd, headless=True, max_steps=8)
    return await browser_agent(req_obj, _)
# ===== 8. ____________ =====
class MemoryRequest(BaseModel):
    conversation_id: str = ""

@router.post("/memory/compress")
async def compress_memory(req: MemoryRequest, _=Depends(verify_token)):
    """____________ -- __________"""
    try:
        from routers.agent_chat import _cdb
        c = _cdb()
        msgs = c.execute("SELECT role,content FROM msgs WHERE cid=_ ORDER BY id",(req.conversation_id,)).fetchall()
        c.close()
        
        if len(msgs) < 20:
            return {"ok":True,"compressed":False,"message":"______,______"}
        
        full_text = "\n".join([f"{r[0]}: {r[1][:200]}" for r in msgs])
        summary = await _call_ai([
            {"role":"system","content":"____________.___________________________C______EUR______"},
            {"role":"user","content":f"___({len(msgs)}_C___:\n{full_text[:4000]}\n\n_____________00__."}
        ], max_tokens=400)
        
        return {"ok":True,"compressed":True,"original_messages":len(msgs),"summary":summary}
    except Exception as e:
        return {"ok":False,"error":str(e)}



# ===== 8.5 _________ WebSocket =====
connected_remotes = {}  # {client_id: websocket}

@router.websocket("/remote/ws")
async def remote_control_ws(ws: WebSocket):
    """_________WebSocket - ___Agent_____AI__________"""
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
                await ws.send_json({"type":"registered","client_id":client_id,"message":"____"})
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
        return {"ok":False,"error":f"_____{client_id} ____","available":list(connected_remotes.keys())}
    try:
        ws = connected_remotes[client_id]
        await ws.send_json({"type":"execute","action":action,"params":params})
        return {"ok":True,"sent":action,"to":client_id}
    except Exception as e:
        connected_remotes.pop(client_id, None)
        return {"ok":False,"error":str(e)}

# ===== ___Agent___ v2.0 =====
async def download_agent_script():
    """______Agent___ v2.0 - __________"""
    script = '''
Friday AI ______Agent v2.0 -- ___________
___: ______ - ______ - ______ - _____- ________
___: pip install websockets pyautogui pillow psutil playwright pytesseract opencv-python
      playwright install chromium
      python friday_agent.py
import asyncio, json, base64, os, sys, io, subprocess, re, time
from pathlib import Path
from datetime import datetime
import socket

# ===== ___ =====
SERVER = os.getenv("FRIDAY_SERVER", "wss://tiktook.eu.cc/agent/advanced/remote/ws")
CLIENT_ID = socket.gethostname()
VISION_ENABLED = True  # ____________(___________I___)

# ===== ___ =====
def screenshot_to_base64():
    """______ -> base64"""
    try:
        from PIL import ImageGrab
        img = ImageGrab.grab()
        buf = io.BytesIO()
        img.save(buf, format="PNG", optimize=True)
        return base64.b64encode(buf.getvalue()).decode()
    except Exception as e:
        return None

# ===== _________ =====
def find_element(description, screenshot_b64=None):
    """
    ____________,_________:
    - "___:500,400" -> _________
    - "___:___" -> OCR______"___"________
    - "___:button.png" -> ____C____
    - "___:_____ -> ____________"
    ___ {"x":int, "y":int, "method":str} __None
    """
    if not description:
        return None
    
    desc = str(description).strip()
    
    # ___1: ______
    coord_match = re.match(r'___[::]\s*(\d+)\s*[,,]\s*(\d+)', desc)
    if coord_match:
        return {"x": int(coord_match.group(1)), "y": int(coord_match.group(2)), "method": "coordinate"}
    
    # ___2: OCR______
    text_match = re.match(r'___[::]\s*(.+)', desc)
    if text_match:
        target_text = text_match.group(1).strip()
        try:
            import pytesseract
            from PIL import ImageGrab
            import cv2
            import numpy as np
            
            img = ImageGrab.grab()
            img_np = np.array(img)
            # OCR____EUR________
            data = pytesseract.image_to_data(img_np, lang='chi_sim+eng', output_type=pytesseract.Output.DICT)
            for i, text in enumerate(data['text']):
                if target_text in text:
                    x = data['left'][i] + data['width'][i] // 2
                    y = data['top'][i] + data['height'][i] // 2
                    if data['conf'][i] > 30:  # _____30%
                        return {"x": x, "y": y, "method": f"ocr:{text}", "confidence": data['conf'][i]}
        except ImportError:
            pass  # OCR________
        except Exception:
            pass
        return None  # ________
    
    # ___3: ____C____
    img_match = re.match(r'___[::]\s*(.+)', desc)
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
    
    # ___4: ______
    area_map = {
        "_____: (100, 100), "_____: (1820, 100),
        "_____: (100, 980), "_____: (1820, 980),
        "______": (960, 540), "_EUR_____: (50, 1030),"
        "_____: (960, 1050), "______": (960, 540),"
        "______": (1880, 10), "_EUR___": (1840, 10),
    }
    for area_name, (ax, ay) in area_map.items():
        if area_name in desc:
            return {"x": ax, "y": ay, "method": f"area:{area_name}"}
    
    return None

# ===== ______ =====
async def execute_action(action, params, ws=None):
    """____________,______"""
    try:
        if action == "screenshot":
            b64 = screenshot_to_base64()
            return {"ok": True, "screenshot": b64, "action": action}
        
        elif action == "click":
            # _________
            target_desc = params.get("target", "")
            pos = find_element(target_desc) if target_desc else None
            
            if pos:
                x, y = pos["x"], pos["y"]
            elif "x" in params and "y" in params:
                x, y = params["x"], params["y"]
            else:
                return {"ok": False, "error": "_EUR____________", "action": action}
            
            import pyautogui
            pyautogui.moveTo(x, y, duration=0.3)  # ________
            time.sleep(0.1)
            pyautogui.click()
            result = {"ok": True, "action": action, "clicked": [x, y], "method": pos["method"] if pos else "coordinate"}
            # ______________
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
            # _________
            import pyautogui, pyperclip
            try:
                pyperclip.copy(text)
                pyautogui.hotkey('ctrl', 'v')
            except ImportError:
                pyautogui.write(text, interval=0.05)  # ________EUR__
            return {"ok": True, "action": action, "typed": text[:50]}
        
        elif action == "press_key":
            key = params.get("key", "")
            import pyautogui
            # ________
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
            seconds = min(params.get("seconds", 1), 30)  # _EUR___30__
            await asyncio.sleep(seconds)
            return {"ok": True, "action": action, "waited": seconds}
        
        elif action == "run_command":
            ALLOWED_COMMANDS = {
                "uptime": ["uptime"], "df": ["df", "-h"], "free": ["free", "-m"],
                "ps": ["ps", "aux"], "who": ["who"], "hostname": ["hostname"],
                "uname": ["uname", "-a"], "date": ["date"], "w": ["w"],
            }
            cmd_name = params.get("command", "").strip().split()[0] if params.get("command", "") else ""
            if cmd_name not in ALLOWED_COMMANDS:
                return {"ok": False, "action": action, "error": f"不允许的命令: {cmd_name}"}
            r = subprocess.run(ALLOWED_COMMANDS[cmd_name], capture_output=True, text=True, timeout=30)
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
            await asyncio.sleep(1.5)  # ________
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
            # _____laywright___
            command = params.get("command", "")
            try:
                from playwright.async_api import async_playwright
                async with async_playwright() as p:
                    browser = await p.chromium.launch(headless=False)
                    page = await browser.new_page()
                    # _EUR___:__I______
                    await page.goto("https://www.google.com")
                    await page.fill('textarea[name="q"]', command)
                    await page.press('textarea[name="q"]', "Enter")
                    await page.wait_for_load_state("networkidle")
                    text = await page.inner_text("body")
                    await browser.close()
                    return {"ok": True, "action": action, "result": text[:2000]}
            except ImportError:
                return {"ok": False, "error": "Playwright_____, "action": action}"
        
        else:
            return {"ok": False, "error": f"______: {action}", "action": action}
    
    except Exception as e:
        return {"ok": False, "error": str(e), "action": action}

# ===== _____=====
async def main():
    import websockets
    print(f"\n{'='*60}")
    print(f"  Friday AI ___ Agent v2.0")
    print(f"  _____D: {CLIENT_ID}")
    print(f"  _____   {SERVER}")
    print(f"  ______: {'_____' if VISION_ENABLED else '_____'}")
    print(f"{'='*60}\n")
    
    # _EUR_____
    deps_ok = True
    try:
        import pyautogui
        print(f"  __pyautogui {pyautogui.__version__ if hasattr(pyautogui,'__version__') else 'OK'}")
    except ImportError:
        print(f"  __pyautogui _____)"
        deps_ok = False
    try:
        import PIL
        print(f"  __Pillow OK")
    except ImportError:
        print(f"  __Pillow _____)"
        deps_ok = False
    try:
        import pytesseract
        print(f"  __pytesseract OK (______)")
    except ImportError:
        print(f"  ___  pytesseract _____(_________)")
    try:
        import cv2
        print(f"  __OpenCV OK (______)")
    except ImportError:
        print(f"  ___  OpenCV _____(_________)")
    
    if not deps_ok:
        print(f"\n  ___________ pip install pyautogui pillow\n")
    
    while True:
        try:
            print(f"[___] ______ {SERVER} ...")
            async with websockets.connect(SERVER, ping_interval=20, ping_timeout=10) as ws:
                # ___
                await ws.send(json.dumps({
                    "type": "register",
                    "client_id": CLIENT_ID,
                    "hostname": CLIENT_ID,
                    "version": "2.0",
                    "capabilities": ["screenshot", "click", "type", "scroll", "ocr", "vision"]
                }))
                print(f"[___] _____________)"
                
                # ___
                async def heartbeat():
                    while True:
                        await asyncio.sleep(25)
                        try:
                            await ws.send(json.dumps({"type": "ping"}))
                        except:
                            break
                asyncio.create_task(heartbeat())
                
                # ______
                async for msg in ws:
                    data = json.loads(msg)
                    msg_type = data.get("type", "")
                    
                    if msg_type == "execute":
                        action = data.get("action", "")
                        params = data.get("params", {})
                        task_id = data.get("task_id", "")
                        print(f"\n[___] {action} | {str(params)[:80]}")
                        
                        result = await execute_action(action, params, ws)
                        
                        # ______
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
                        
                        status = "__ if result.get("ok") else "__
                        print(f"[___] {status} {str(result)[:120]}")
                    
                    elif msg_type == "vision_request":
                        # ______________I______
                        shot = screenshot_to_base64()
                        await ws.send(json.dumps({
                            "type": "vision_response",
                            "screenshot": shot,
                            "task_id": data.get("task_id", "")
                        }))
                    
                    elif msg_type == "pong":
                        pass  # ______
                    
                    elif msg_type == "registered":
                        print(f"[_____ {data.get('message', 'OK')}")
                    
                    else:
                        print(f"[______] {msg_type}")
        
        except websockets.exceptions.ConnectionClosed:
            print(f"[___] ______,5______...")
        except Exception as e:
            print(f"[___] {str(e)[:200]}, 5______...")
        
        await asyncio.sleep(5)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print(f"\n[_EUR__ Agent_____)"
    except Exception as e:
        print(f"\n[______] {e}")'''
    return {
        "ok": True,
        "version": "2.0",
        "filename": "friday_agent.py",
        "script": script,
        "instructions": "pip install websockets pyautogui pillow psutil playwright pytesseract opencv-python pyperclip && playwright install chromium && python friday_agent.py",
        "capabilities": ["___+______","_________(OCR/___/___)","21____","___/___/___","____","______","_________","______","____"]
    }


# ===== ___Agent(_____=====
@router.post("/agent/human")
async def human_like_agent(req: dict, _=Depends(verify_token)):
    """___________- ______: ____________, GUI_________, ______"""
    command = req.get("command","")
    target = req.get("target","server")
    max_cycles = req.get("max_cycles", 8)
    action_log = []
    
    # ===== ____ _________ =====
    classify_prompt = f"""__________________________:
- "code": ___/___/________/______ (_________)
- "gui": _________/GUI/______EUR______
___: {command}
___:"""
    
    task_type = (await _call_ai(
        [{"role":"user","content":classify_prompt}],
        model=CHEAP_MODEL, max_tokens=10, temperature=0
    )).strip().lower()
    
    if "code" in task_type:
        # ===== ___/________ ___________ =====
        code_prompt = f"""___________I._________,___JSON:
{{"steps":[{{"action":"run_command|read_file|write_file|search|done","params":{{}},"reason":"____"}}],"summary":"___"}}
______: run_command(___shell), read_file(_____, write_file(_____, search(______), done(___)
___: {command}
JSON:"""
        
        plan = await _call_ai(
            [{"role":"user","content":code_prompt}],
            model=CHEAP_MODEL, max_tokens=600, temperature=0.2
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
                        results.append("[read] " + path + ": (file not found)")
                elif a == "write_file":
                    path = p.get("path",""); txt = p.get("content","")
                    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
                    with open(path,"w") as f: f.write(txt)
                    results.append("[write] " + path + ": " + str(len(txt)) + " chars")
                elif a == "search":
                    import glob
                    pattern = p.get("pattern","*")
                    found = glob.glob(pattern, recursive=True)[:20]
                    results.append(f"[search] {pattern}: {found}")
                elif a == "done":
                    break
            except Exception as e:
                results.append(f"[{a}] ___: {str(e)[:200]}")
        
        # ____C___EUR__ (______)
        summary = await _call_ai([
            {"role":"user","content":f"___:{command}\n______:\n"+'\n'.join(results)+"\n\n_______________."}
        ], model=CHEAP_MODEL, max_tokens=100, temperature=0)
        
        token_estimate = len(classify_prompt) + len(plan) + len(summary) + 300
        return {
            "ok":True, "completed":True, "mode":"code", "cycles":len(action_log),
            "log":action_log, "results":results, "final_result":summary,
            "token_saved": True, "estimated_tokens": token_estimate,
            "vs_visual_mode": "(saved " + str((max_cycles*1500 - token_estimate)//1000) + "k tokens)"
        }
    
    # ===== GUI___: ______(_____ =====
    system_prompt = """_________AI.___________SON: {"observation":"_______",thought":"__EUR",action":"____",target":"______(___:xxx/___:x,y)","params":{},"confidence":0.8}
___: click|double_click|type_text|press_key|scroll|move|wait|open_app|close_window|switch_window|select_all|copy|paste|undo|save|run_command|done|fail
___: __arget______(_____:___"), ________ _______"""
    
    cycle = 0
    last_screenshot = None
    last_action = None  # _________
    
    while cycle < max_cycles:
        cycle += 1
        
        # ___________(______/_______EUR__
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
            return {"ok":False,"error":"____________","cycle":cycle}
        if not screenshot_b64:
            action_log.append({"cycle":cycle,"error":"______"}); break
        
        last_screenshot = screenshot_b64
        
        # ______: _____CHEAP_MODEL(___deepseek-chat), ______SMART_MODEL
        use_model = pick_model(need_vision=True, step_count=cycle)
        user_prompt = "cmd: " + command + "\n(cycle " + str(cycle) + "/" + str(max_cycles) + ")\nhistory: " + json.dumps(action_log[-3:],ensure_ascii=False) + "\n(respond with target action)"
        
        ai_response = await _call_ai([
            {"role":"system","content":system_prompt},
            {"role":"user","content":[{"type":"text","text":user_prompt},{"type":"image_url","image_url":{"url":f"data:image/png;base64,{screenshot_b64}","detail":"low"}}]}  # low detail = _____
        ], model=use_model, max_tokens=300, temperature=0.3)
        
        decision = {}
        try:
            json_match = re.search(r'\{[^{}]*"action"[^{}]*\}', ai_response, re.DOTALL)
            if json_match: decision = json.loads(json_match.group())
        except: pass
        
        if not decision:
            action_log.append({"cycle":cycle,"error":"______"}); continue
        
        action = decision.get("action","screenshot")
        params = decision.get("params",{})
        last_action = action
        
        action_log.append({"cycle":cycle,"observation":decision.get("observation","")[:80],"thought":decision.get("thought","")[:80],"action":action,"target":decision.get("target","")})
        
        if action == "done":
            return {"ok":True,"completed":True,"mode":"gui","cycles":cycle,"log":action_log,"result":params.get("summary",""),"screenshot":last_screenshot,"model":CHEAP_MODEL,"estimated_tokens":cycle*500}
        if action == "fail":
            return {"ok":False,"error":params.get("reason","______"),"mode":"gui","cycles":cycle,"log":action_log}
        
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
    
    return {"ok":False,"error":"(GUI mode failed)","mode":"gui","cycles":cycle,"log":action_log,"screenshot":last_screenshot,"estimated_tokens":cycle*500}

@router.post("/agent/quick")
async def quick_agent_action(req: dict, _=Depends(verify_token)):
    client_id = req.get("client_id","")
    action = req.get("action","")
    params = req.get("params",{})
    actions_help = {"screenshot":"______","open_url":"______","click":"___","double_click":"___","right_click":"___","type_text":"______","press_key":"___","run_command":"______","get_info":"____C_","open_app":"______","scroll":"___","move_mouse":"______","close_window":"______","switch_window":"______","select_all":"__EUR","copy":"___","paste":"___","undo":"___","save":"___","browser_task":"_______"}
    if not client_id: return {"ok":False,"error":"_____lient_id","available_clients":list(connected_remotes.keys()),"actions":actions_help}
    if client_id not in connected_remotes: return {"ok":False,"error":f"_____{client_id} ____","available":list(connected_remotes.keys())}
    if action == "screenshot":
        ws = connected_remotes[client_id]
        await ws.send_json({"type":"execute","action":"screenshot","params":{}})
        for _ in range(20):
            try:
                data = await asyncio.wait_for(ws.receive_json(), timeout=3.0)
                if data.get("type") == "result" and data.get("screenshot"): return {"ok":True,"action":action,"screenshot":data.get("screenshot")}
            except: break
        return {"ok":False,"error":"______"}
    return await execute_remote(req, _)

@router.get("/agent/actions")
async def list_actions(_=Depends(verify_token)):
    return {"ok":True,"actions":{"screenshot":"______","open_url":"______","click":"___","double_click":"___","right_click":"___","type_text":"______","press_key":"___","run_command":"_________","get_info":"____C_","open_app":"______","scroll":"___","move_mouse":"______","drag":"___","wait":"___","close_window":"______","switch_window":"______","select_all":"__EUR","copy":"___","paste":"___","undo":"___","save":"___","browser_task":"AI_______"}}

# ===== ________gent =====
@router.post("/browser/unified")
async def unified_browser(req: dict, _=Depends(verify_token)):
    command = req.get("command","")
    target = req.get("target","server")
    if target == "server" or target in list(connected_remotes.keys()):
        if target != "server":
            if target not in connected_remotes: return {"ok":False,"error":f"_____{target} ____"}
            ws = connected_remotes[target]
            await ws.send_json({"type":"execute","action":"browser_task","params":{"command":command}})
            return {"ok":True,"sent_to":target,"command":command}
        else:
            req_obj = BrowserAgentRequest(command=command, headless=True, max_steps=10)
            return await browser_agent(req_obj, _)
    return {"ok":False,"error":"______","available_targets":["server"]+list(connected_remotes.keys())}



# ===== 8.7 ______API =====
@router.get("/models")
async def list_models(_=Depends(verify_token)):
    """____EUR_____I_______"""
    available = {}
    for name, info in AVAILABLE_MODELS.items():
        key = DEEPSEEK_KEY if info["provider"] == "deepseek" else OPENAI_KEY
        available[name] = {**info, "available": bool(key)}
    return {
        "ok": True,
        "models": available,
        "current_cheap": CHEAP_MODEL,
        "current_smart": SMART_MODEL,
        "config_hint": "______: CHEAP_MODEL / SMART_MODEL / DEEPSEEK_API_KEY / OPENAI_API_KEY"
    }

@router.post("/models/test")
async def test_model(req: dict, _=Depends(verify_token)):
    """_______________"""
    model = req.get("model", CHEAP_MODEL)
    try:
        result = await _call_ai([{"role":"user","content":"___OK"}], model=model, max_tokens=10, temperature=0)
        return {"ok": True, "model": model, "response": result[:50], "status": "___" if "OK" in result else "___"}
    except Exception as e:
        return {"ok": False, "model": model, "error": str(e)[:200]}

# ===== 9. AI_____EUR_=====
@router.post("/notify")
async def send_notification(req: dict, _=Depends(verify_token)):
    """__EUR_EUR_______________"""
    title = req.get("title","Friday AI")
    body = req.get("body","")
    url = req.get("url","/ai/")
    
    # ___WebSocket______
    try:
        from routers.ws_router import manager
        await manager.broadcast(json.dumps({
            "type":"notification",
            "title":title,"body":body,"url":url,"time":datetime.now().isoformat()
        }))
        return {"ok":True,"message":"_______"}
    except Exception as e:
        return {"ok":False,"error":str(e)}

@router.post("/agent/human/correct")
async def human_agent_correct(command: str = "", target: str = "server", _=Depends(verify_token)):
    """__Agent___"""
    try:
        from agents.multi_model import ModelRouter
        resp = ModelRouter.smart_chat(messages=[{"role":"user","content":f"____: {command}__________,______"}], mode="smart")
        corrected = resp.get("content","") if isinstance(resp,dict) else str(resp)
        import subprocess, shlex
        result = subprocess.run(corrected.strip().split(), capture_output=True, text=True, timeout=60)
        return {"ok":True,"corrected":corrected.strip(),"stdout":result.stdout[:2000]}
    except Exception as e:
        return {"ok":False,"error":str(e)}
