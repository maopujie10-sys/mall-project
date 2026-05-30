"""楂樼骇AI寮曟搸 -- 瀹炴椂璇煶鎵撴柇 / 瑙嗛娴佸垎鏋?/ 娣卞害鐮旂┒ / 鏁版嵁鍙鍖?/ 鏂囦欢瀵煎嚭 / 缃戦〉鎶撳彇 / 娴忚鍣ㄨ嚜鍔ㄥ寲 / 闀夸笂涓嬫枃"""
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
# 妯″瀷璺敱: deepseek-寮€澶寸殑璧癉eepSeek, 鍏朵粬璧癘penAI
CHEAP_MODEL = os.getenv("CHEAP_MODEL", "deepseek-chat")
SMART_MODEL = os.getenv("SMART_MODEL", "gpt-4o")
# ===== 妯″瀷甯傚満 -- AI鑷繁閫夋ā鍨?=====
AVAILABLE_MODELS = {
    # 渚垮疁姊槦 (绠€鍗曚换鍔?
    "deepseek-chat":       {"provider": "deepseek", "cost": "0.14/1M",  "strength": "鏃ュ父瀵硅瘽/绠€鍗曟搷浣?蹇€熷搷搴?},
    CHEAP_MODEL:       {"provider": "openai",   "cost": "0.50/1M",  "strength": "鍒嗙被/鍒ゆ柇/绠€鍗曞喅绛?},
    # 鎬т环姣旀闃?(鏅€氫换鍔?
    CHEAP_MODEL:         {"provider": "openai",   "cost": "0.15/1M",  "strength": "瑙嗚鐞嗚В/澶氭ā鎬?蹇€熸帹鐞?},
    "deepseek-reasoner":   {"provider": "deepseek", "cost": "0.55/1M",  "strength": "娣卞害鎺ㄧ悊/澶嶆潅鍒嗘瀽"},
    # 楂樼姊槦 (澶嶆潅浠诲姟)
    "gpt-4o":              {"provider": "openai",   "cost": "2.50/1M",  "strength": "楂樼簿搴﹁瑙?澶嶆潅鍐崇瓥/澶氭楠?},
    "claude-3-5-sonnet":   {"provider": "openai",   "cost": "3.00/1M",  "strength": "浠ｇ爜鐢熸垚/闀挎枃鏈垎鏋?},
}

def pick_model(task_complexity="auto", need_vision=False, step_count=0):
    """AI鑷姩閫夋ā鍨? 鏍规嵁浠诲姟澶嶆潅搴︺€佹槸鍚﹂渶瑕佽瑙夈€佸綋鍓嶆楠ゆ暟"""
    if task_complexity == "simple" or (step_count > 0 and step_count <= 3):
        return CHEAP_MODEL  # 榛樿渚垮疁妯″瀷
    elif task_complexity == "hard" or step_count > 5:
        return SMART_MODEL  # 榛樿鑱槑妯″瀷
    elif need_vision:
        return CHEAP_MODEL if OPENAI_KEY else CHEAP_MODEL  # 瑙嗚浠诲姟闇€瑕佸妯℃€佹ā鍨?
    return CHEAP_MODEL


router = APIRouter(prefix="/agent/advanced", tags=["AdvancedAI"])
# 澶歱rovider
OPENAI_KEY = OPENAI_API_KEY
DEEPSEEK_KEY = DEEPSEEK_API_KEY
DS_BASE_URL = DEEPSEEK_BASE_URL
BASE_URL = OPENAI_BASE_URL or "https://api.openai.com/v1"

async def _call_ai(messages, model=None, max_tokens=1000, temperature=0.7):
    if model is None: model = CHEAP_MODEL
    """澶歱rovider AI璋冪敤 - 鑷姩璺敱DeepSeek/OpenAI"""
    import httpx
    # 鏍规嵁妯″瀷鍚嶈嚜鍔ㄩ€夋嫨provider
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
            return "闇€瑕侀厤缃瓵PI Key"
    
    async with httpx.AsyncClient(timeout=120) as c:
        r = await c.post(f"{base}/chat/completions",
            headers={"Authorization":f"Bearer {key}","Content-Type":"application/json"},
            json={"model":model,"messages":messages,"max_tokens":max_tokens,"temperature":temperature})
        if r.status_code == 200:
            return r.json().get("choices",[{}])[0].get("message",{}).get("content","")
        return f"API閿欒:{r.status_code}"

# ===== 1. 瀹炴椂璇煶鎵撴柇 WebSocket =====
@router.websocket("/voice/live")
async def live_voice(ws: WebSocket):
    """瀹炴椂璇煶瀵硅瘽 -- 鏀寔鎵撴柇/鎯呮劅/鑷劧瀵硅瘽"""
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
                # 鐢ㄦ埛鎵撴柇褰撳墠鍥炲
                if current_task and not current_task.done():
                    current_task.cancel()
                await ws.send_json({"type":"interrupted"})
            elif msg_type == "speech":
                text = data.get("text","")
                if not text: continue
                conversation.append({"role":"user","content":text})
                await ws.send_json({"type":"status","text":"鎬濊€冧腑..."})
                
                msgs = [{"role":"system","content":"浣犳槸Friday AI鍔╂墜.鐢ㄨ嚜鐒剁殑鍙ｈ鍥炲,甯﹂€傚綋鐨勬儏鎰?鍙互绗戙€佸徆姘斻€佹儕璁?鍥炲绠€娲佽嚜鐒?鍍忔湅鍙嬭亰澶?涓嶈鐢╩arkdown."}]
                msgs.extend(conversation[-15:])
                
                current_task = asyncio.create_task(stream_ai_reply(msgs))
                try:
                    full_reply = await current_task
                    conversation.append({"role":"assistant","content":full_reply})
                    await ws.send_json({"type":"done","full":full_reply})
                except asyncio.CancelledError:
                    await ws.send_json({"type":"interrupted"})
            elif msg_type == "emotion":
                # 瀹㈡埛绔娴嬪埌鐨勬儏缁?
                await ws.send_json({"type":"status","text":"宸叉劅鐭ユ儏缁? "+data.get("emotion","neutral")})
    except WebSocketDisconnect:
        pass

# ===== 2. 瀹炴椂瑙嗛甯у垎鏋?=====
class FrameRequest(BaseModel):
    image_base64: str
    context: str = ""

@router.post("/vision/live")
async def live_vision(req: FrameRequest, _=Depends(verify_token)):
    """瀹炴椂瑙嗛甯у垎鏋?-- 杩炵画甯х悊瑙?""
    prompt = "浣犳鍦ㄧ湅瀹炴椂瑙嗛娴?璇风敤涓€鍙ヨ瘽鎻忚堪鐢婚潰鍐呭,濡傛灉鏈夊€煎緱娉ㄦ剰鐨勫彉鍖栬鎸囧嚭."
    if req.context: prompt = f"涔嬪墠浣犵湅鍒?{req.context}\n缁х画瑙傚療:"
    
    result = await _call_ai([
        {"role":"system","content":"浣犳槸瀹炴椂瑙嗛鍒嗘瀽AI.绠€娲佹弿杩扮敾闈?"},
        {"role":"user","content":[
            {"type":"text","text":prompt},
            {"type":"image_url","image_url":{"url":f"data:image/jpeg;base64,{req.image_base64}"}}
        ]}
    ], model=CHEAP_MODEL, max_tokens=200)
    return {"ok":True,"description":result}

# ===== 3. 娣卞害鐮旂┒ Agent =====
class ResearchRequest(BaseModel):
    topic: str
    depth: int = 2  # 鐮旂┒娣卞害 1-3

@router.post("/research")
async def deep_research(req: ResearchRequest, _=Depends(verify_token)):
    """澶氭鑷富鐮旂┒ -- 鎼滅储->鍒嗘瀽->缁煎悎->鎶ュ憡"""
    import httpx
    
    # Step 1: 鐢熸垚鎼滅储瀛愰棶棰?
    questions_prompt = f"灏嗙爺绌朵富棰樻媶鍒嗕负{min(req.depth*2,5)}涓叿浣撳瓙闂,鍙繑鍥為棶棰樺垪琛?姣忚涓€涓?\n涓婚:{req.topic}"
    sub_questions = await _call_ai([{"role":"user","content":questions_prompt}], max_tokens=300)
    questions = [q.strip().lstrip('0123456789.-) ') for q in sub_questions.split('\n') if q.strip()][:5]
    
    # Step 2: 鎼滅储姣忎釜瀛愰棶棰?
    findings = []
    for q in questions[:req.depth*2]:
        try:
            async with httpx.AsyncClient(timeout=15) as c:
                r = await c.get("https://html.duckduckgo.com/html/",
                    params={"q": q}, headers={"User-Agent":"Mozilla/5.0"})
                # 鎻愬彇鎽樿
                snippets = []
                for m in re.finditer(r'class="result__snippet"[^>]*>([^<]+)', r.text):
                    snippets.append(m.group(1).strip())
                summary_text = " ".join(snippets[:3])[:500]
                if summary_text:
                    # Step 3: AI鍒嗘瀽姣忎釜瀛愰棶棰?
                    analysis = await _call_ai([
                        {"role":"user","content":f"瀛愰棶棰?{q}\n鎼滅储缁撴灉:{summary_text}\n璇风敤2-3鍙ヨ瘽鎬荤粨鍏抽敭鍙戠幇."}
                    ], max_tokens=200)
                    findings.append({"question":q,"sources":len(snippets),"finding":analysis})
        except: findings.append({"question":q,"sources":0,"finding":"鎼滅储澶辫触"})
    
    # Step 4: 缁煎悎鎶ュ憡
    findings_text = "\n".join([f"## {f['question']}\n{f['finding']}" for f in findings])
    report = await _call_ai([
        {"role":"system","content":"浣犳槸璧勬繁鐮旂┒鍛?鏍规嵁浠ヤ笅鐮旂┒鍙戠幇,鐢熸垚涓€浠界粨鏋勫寲鐨勭爺绌舵姤鍛?瑕佹湁鎽樿銆佸叧閿彂鐜般€佺粨璁?"},
        {"role":"user","content":f"鐮旂┒涓婚:{req.topic}\n\n鐮旂┒鍙戠幇:\n{findings_text}\n\n璇风敓鎴愬畬鏁寸爺绌舵姤鍛?"}
    ], max_tokens=2000)
    
    return {"ok":True,"topic":req.topic,"questions":questions,"findings":findings,"report":report}

# ===== 4. 鏁版嵁鍙鍖?+ CSV鍒嗘瀽 =====
class DataAnalyzeRequest(BaseModel):
    csv_data: str = ""
    question: str = "鍒嗘瀽鏁版嵁骞剁粰鍑烘礊瀵?

@router.post("/data/analyze")
async def analyze_data(req: DataAnalyzeRequest, _=Depends(verify_token)):
    """涓婁紶CSV->AI鑷姩鍒嗘瀽->鏂囨湰+鍥捐〃鏁版嵁"""
    if not req.csv_data:
        return {"ok":False,"error":"闇€瑕丆SV鏁版嵁"}
    
    # 瑙ｆ瀽CSV
    import csv as csv_mod
    reader = csv_mod.reader(io.StringIO(req.csv_data[:50000]))
    rows = list(reader)
    if not rows: return {"ok":False,"error":"CSV涓虹┖"}
    
    headers = rows[0]
    data_rows = rows[1:21]  # 鍓?0琛?
    row_count = len(rows) - 1
    col_count = len(headers)
    
    # 鍩烘湰缁熻
    stats = {"rows":row_count,"columns":col_count,"headers":headers}
    numeric_cols = []
    for ci, h in enumerate(headers):
        try:
            vals = [float(r[ci]) for r in data_rows if ci < len(r)]
            numeric_cols.append({"name":h,"index":ci,"min":min(vals),"max":max(vals),"avg":round(sum(vals)/len(vals),2),"count":len(vals)})
        except: pass
    
    # AI鍒嗘瀽
    preview = "\n".join([",".join(r) for r in [headers]+data_rows[:10]])
    prompt = f"""CSV鏁版嵁({row_count}琛?{col_count}鍒?:
鏍囬: {headers}
缁熻: {json.dumps(numeric_cols,ensure_ascii=False)}
鍓?0琛? {preview[:1000]}

鐢ㄦ埛闂: {req.question}

璇风粰鍑?1)鏁版嵁姒傝 2)鍏抽敭娲炲療 3)寮傚父鍙戠幇 4)寤鸿.绠€娲佷笓涓?"""
    
    insight = await _call_ai([{"role":"user","content":prompt}], max_tokens=800)
    
    # 鐢熸垚ECharts閰嶇疆
    chart_config = None
    if numeric_cols:
        nc = numeric_cols[0]
        chart_config = {
            "type":"bar","title":f"{nc['name']}鍒嗗竷",
            "labels":["min","avg","max"],
            "values":[nc["min"],nc["avg"],nc["max"]],
            "suggestion":"鍙敤鏇村鍒楀仛鎶樼嚎鍥?楗煎浘"
        }
    
    return {"ok":True,"stats":stats,"numeric_columns":numeric_cols,"insight":insight,"chart":chart_config}

# ===== 5. 鏂囦欢瀵煎嚭 (PDF/Excel/Markdown) =====
class ExportRequest(BaseModel):
    content: str
    format: str = "md"  # md | html | txt
    filename: str = "report"

@router.post("/export")
async def export_file(req: ExportRequest, _=Depends(verify_token)):
    """瀵煎嚭AI鐢熸垚鐨勫唴瀹逛负鏂囦欢"""
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
    """涓嬭浇瀵煎嚭鏂囦欢"""
    fpath = Path(__file__).parent.parent / "data" / "exports" / filename
    if not fpath.exists():
        return {"ok":False,"error":"鏂囦欢涓嶅瓨鍦?}
    media_types = {".md":"text/markdown",".html":"text/html",".txt":"text/plain",".csv":"text/csv",".json":"application/json"}
    ext = fpath.suffix
    return FileResponse(fpath, media_type=media_types.get(ext,"application/octet-stream"), filename=filename)

# ===== 6. 缃戦〉鍐呭鎶撳彇+鎬荤粨 =====
class ScrapeRequest(BaseModel):
    url: str

@router.post("/scrape")
async def scrape_url(req: ScrapeRequest, _=Depends(verify_token)):
    """鎶撳彇缃戦〉鍐呭骞禔I鎬荤粨"""
    import httpx
    try:
        async with httpx.AsyncClient(timeout=20) as c:
            r = await c.get(req.url, headers={"User-Agent":"Mozilla/5.0"}, follow_redirects=True)
            if r.status_code != 200:
                return {"ok":False,"error":f"HTTP {r.status_code}"}
            
            html = r.text
            # 绠€鏄撴鏂囨彁鍙?
            text = re.sub(r'<script[^>]*>.*?</script>','',html,flags=re.DOTALL|re.I)
            text = re.sub(r'<style[^>]*>.*?</style>','',text,flags=re.DOTALL|re.I)
            text = re.sub(r'<[^>]+>',' ',text)
            text = re.sub(r'\s+',' ',text).strip()[:8000]
            
            # AI鎬荤粨
            summary = await _call_ai([
                {"role":"system","content":"浣犳槸缃戦〉鎬荤粨涓撳.鐢?-5鍙ヨ瘽鎬荤粨鏍稿績鍐呭,鎻愬彇鍏抽敭淇℃伅."},
                {"role":"user","content":f"URL: {req.url}\n\n鍐呭:\n{text[:5000]}"}
            ], max_tokens=300)
            
            title_match = re.search(r'<title[^>]*>([^<]+)</title>', html, re.I)
            title = title_match.group(1).strip() if title_match else req.url
            
            return {"ok":True,"url":req.url,"title":title,"text_length":len(text),"summary":summary}
    except Exception as e:
        return {"ok":False,"error":str(e)}

# ===== 7. AI娴忚鍣ˋgent -- 鑷劧璇█鎿嶆帶娴忚鍣?=====
class BrowserAgentRequest(BaseModel):
    command: str  # 鑷劧璇█鎸囦护
    headless: bool = True
    max_steps: int = 10

@router.post("/browser/agent")
async def browser_agent(req: BrowserAgentRequest, _=Depends(verify_token)):
    """AI娴忚鍣ˋgent -- 鑷劧璇█->姝ラ鎷嗚В->Playwright鎵ц->AI瑙嗚鐞嗚В"""
    import httpx
    
    # Step 1: AI鎷嗚В浠诲姟涓烘楠?
    plan_prompt = f"""浣犳槸涓€涓祻瑙堝櫒鑷姩鍖栦笓瀹?灏嗕互涓嬩换鍔℃媶瑙ｄ负鍏蜂綋鐨勬祻瑙堝櫒鎿嶄綔姝ラ.
杩斿洖JSON鏁扮粍,姣忔鏍煎紡: {{"action":"navigate/click/type/wait/screenshot/extract/scroll","target":"閫夋嫨鍣ㄦ垨URL","value":"杈撳叆鍊兼垨璇存槑","reason":"涓轰粈涔堣繖姝?}}

浠诲姟: {req.command}

瑙勫垯:
- navigate: 鎵撳紑URL 
- click: 鐐瑰嚮鍏冪礌(鐢ㄦ枃鏈垨CSS閫夋嫨鍣?
- type: 杈撳叆鏂囨湰(鍏坈lick鍐峵ype)
- wait: 绛夊緟(绉?
- screenshot: 鎴浘
- extract: 鎻愬彇椤甸潰鏁版嵁(璇存槑瑕佹彁鍙栦粈涔?
- scroll: 鍚戜笅婊氬姩

鍙繑鍥濲SON鏁扮粍,涓嶈鍏朵粬鍐呭.鏈€澶歿req.max_steps}姝?"""

    plan_text = await _call_ai([{"role":"user","content":plan_prompt}], max_tokens=800, temperature=0.3)
    
    # 瑙ｆ瀽姝ラ
    steps = []
    try:
        json_match = re.search(r'\[.*\]', plan_text, re.DOTALL)
        if json_match:
            steps = json.loads(json_match.group())
    except:
        # Fallback: 绠€鍗曚换鍔＄洿鎺ユ墽琛?
        steps = [{"action":"navigate","target":"https://www.google.com/search?q="+req.command.replace(" ","+"),"reason":"鎼滅储"}]
    
    # Step 2: Playwright鎵ц
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
                # 鎻愬彇椤甸潰鏂囨湰
                script_lines.append(f"try:\n    text = page.inner_text('body')[:3000]\n    title = page.title()\n    outputs.append({{'step':{i},'action':'extract','ok':True,'title':title,'text':text}})\nexcept Exception as e:\n    outputs.append({{'step':{i},'action':'extract','ok':False,'error':str(e)}})")
            
            elif action == "scroll":
                script_lines.append(f"try:\n    page.evaluate('window.scrollBy(0,800)')\n    outputs.append({{'step':{i},'action':'scroll','ok':True}})\nexcept Exception as e:\n    outputs.append({{'step':{i},'action':'scroll','ok':False,'error':str(e)}})")
            
            else:
                script_lines.append(f"outputs.append({{'step':{i},'action':'{action}','ok':False,'error':'鏈煡鎿嶄綔'}})")
        
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
        
        # 瑙ｆ瀽缁撴灉
        for line in result.stdout.split('\n'):
            if line.startswith('RESULTS:'):
                try: results = json.loads(line[8:].strip())
                except: pass
        
        # 璇诲彇鎴浘
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
        
        # Step 3: AI鎬荤粨鎵ц缁撴灉
        result_summary = json.dumps([{"step":r.get("step"),"action":r.get("action"),"ok":r.get("ok"),"detail":str(r)[:200]} for r in results], ensure_ascii=False)
        summary = await _call_ai([
            {"role":"system","content":"浣犳槸娴忚鍣ㄨ嚜鍔ㄥ寲缁撴灉鍒嗘瀽甯?绠€鏄庢€荤粨鎵ц缁撴灉,鎻愬彇鍏抽敭鏁版嵁鍜屽彂鐜?"},
            {"role":"user","content":f"浠诲姟: {req.command}\n姝ラ璁″垝: {plan_text[:500]}\n鎵ц缁撴灉: {result_summary}\n\n璇风敤3-5鍙ヨ瘽鎬荤粨瀹屾垚浜嗕粈涔?鎻愬彇浜嗗摢浜涘叧閿俊鎭?"}
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
        return {"ok": False, "error": "娴忚鍣ㄦ搷浣滆秴鏃?60绉?", "plan": steps}
    except Exception as e:
        return {"ok": False, "error": str(e), "plan": steps}

# ===== 娴忚鍣ˋgent蹇嵎浠诲姟 =====
@router.post("/browser/quick")
async def browser_quick(req: dict, _=Depends(verify_token)):
    """蹇嵎娴忚鍣ㄤ换鍔?-- 绔炲搧閲囬泦/鍟嗗搧鎴浘/椤甸潰鐩戞帶"""
    task_type = req.get("type","")
    url = req.get("url","")
    selector = req.get("selector","")
    
    commands = {
        "screenshot": f"鎵撳紑 {url} 骞舵埅鍥?,
        "prices": f"鎵撳紑 {url} 鎻愬彇鎵€鏈変环鏍间俊鎭?,
        "products": f"鎵撳紑 {url} 鎻愬彇鍟嗗搧鍒楄〃(鍚嶇О+浠锋牸+閾炬帴)",
        "monitor": f"鎵撳紑 {url} 鎴浘骞舵彁鍙栭〉闈富瑕佸彉鍖?,
        "login_check": f"鎵撳紑 {url} 妫€鏌ユ槸鍚﹂渶瑕佺櫥褰?,
    }
    
    cmd = commands.get(task_type, req.get("command", f"鎵撳紑 {url}"))
    req_obj = BrowserAgentRequest(command=cmd, headless=True, max_steps=8)
    return await browser_agent(req_obj, _)
# ===== 8. 闀夸笂涓嬫枃璁板繂鍘嬬缉 =====
class MemoryRequest(BaseModel):
    conversation_id: str = ""

@router.post("/memory/compress")
async def compress_memory(req: MemoryRequest, _=Depends(verify_token)):
    """鍘嬬缉闀垮璇濅负鎽樿 -- 绐佺牬涓婁笅鏂囬檺鍒?""
    try:
        from routers.agent_chat import _cdb
        c = _cdb()
        msgs = c.execute("SELECT role,content FROM msgs WHERE cid=? ORDER BY id",(req.conversation_id,)).fetchall()
        c.close()
        
        if len(msgs) < 20:
            return {"ok":True,"compressed":False,"message":"瀵硅瘽杈冪煭,鏃犻渶鍘嬬缉"}
        
        full_text = "\n".join([f"{r[0]}: {r[1][:200]}" for r in msgs])
        summary = await _call_ai([
            {"role":"system","content":"浣犳槸瀵硅瘽鎽樿涓撳.灏嗕互涓嬮暱瀵硅瘽鍘嬬缉涓虹畝娲佹憳瑕?淇濈暀鍏抽敭淇℃伅銆佸喅绛栥€佸緟鍔炰簨椤?"},
            {"role":"user","content":f"瀵硅瘽({len(msgs)}鏉℃秷鎭?:\n{full_text[:4000]}\n\n璇风敓鎴愭憳瑕?涓嶈秴杩?00瀛?."}
        ], max_tokens=400)
        
        return {"ok":True,"compressed":True,"original_messages":len(msgs),"summary":summary}
    except Exception as e:
        return {"ok":False,"error":str(e)}



# ===== 8.5 杩滅▼鐢佃剳鎺у埗 WebSocket =====
connected_remotes = {}  # {client_id: websocket}

@router.websocket("/remote/ws")
async def remote_control_ws(ws: WebSocket):
    """杩滅▼鐢佃剳鎺у埗WebSocket - 鏈湴Agent杩炴帴鍚?AI鍙搷鎺ф湰鍦扮數鑴?""
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
                await ws.send_json({"type":"registered","client_id":client_id,"message":"宸叉敞鍐?})
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
        return {"ok":False,"error":f"瀹㈡埛绔?{client_id} 鏈繛鎺?,"available":list(connected_remotes.keys())}
    try:
        ws = connected_remotes[client_id]
        await ws.send_json({"type":"execute","action":action,"params":params})
        return {"ok":True,"sent":action,"to":client_id}
    except Exception as e:
        connected_remotes.pop(client_id, None)
        return {"ok":False,"error":str(e)}

# ===== 鏈湴Agent涓嬭浇 v2.0 =====
async def download_agent_script():
    """涓嬭浇鏈湴Agent鑴氭湰 v2.0 - 浜虹被绾х數鑴戞搷鎺?""
    script = '''
Friday AI 鏈湴鏅鸿兘Agent v2.0 -- 浜虹被绾х數鑴戞搷鎺?
鑳藉姏: 瑙嗚鐞嗚В - 鏅鸿兘瀹氫綅 - 浠诲姟鎷嗚В - 鑷籂閿?- 澶氬簲鐢ㄦ搷鎺?
鐢ㄦ硶: pip install websockets pyautogui pillow psutil playwright pytesseract opencv-python
      playwright install chromium
      python friday_agent.py
import asyncio, json, base64, os, sys, io, subprocess, re, time
from pathlib import Path
from datetime import datetime
import socket

# ===== 閰嶇疆 =====
SERVER = os.getenv("FRIDAY_SERVER", "wss://tiktook.eu.cc/agent/advanced/remote/ws")
CLIENT_ID = socket.gethostname()
VISION_ENABLED = True  # 鏄惁鍚敤瑙嗚鐞嗚В(鎴浘鍙戠粰鏈嶅姟鍣ˋI鍒嗘瀽)

# ===== 鎴浘 =====
def screenshot_to_base64():
    """鎴彇鍏ㄥ睆 -> base64"""
    try:
        from PIL import ImageGrab
        img = ImageGrab.grab()
        buf = io.BytesIO()
        img.save(buf, format="PNG", optimize=True)
        return base64.b64encode(buf.getvalue()).decode()
    except Exception as e:
        return None

# ===== 鏅鸿兘鍏冪礌瀹氫綅 =====
def find_element(description, screenshot_b64=None):
    """
    鏅鸿兘鏌ユ壘灞忓箷鍏冪礌,鏀寔澶氱鏂瑰紡:
    - "鍧愭爣:500,400" -> 鐩存帴杩斿洖鍧愭爣
    - "鏂囨湰:鐧诲綍" -> OCR鏌ユ壘鍖呭惈"鐧诲綍"鐨勬枃瀛椾綅缃?
    - "鍥剧墖:button.png" -> 鍥惧儚妯℃澘鍖归厤
    - "鍖哄煙:宸︿笂瑙? -> 杩斿洖棰勮鍖哄煙鍧愭爣
    杩斿洖 {"x":int, "y":int, "method":str} 鎴?None
    """
    if not description:
        return None
    
    desc = str(description).strip()
    
    # 鏂瑰紡1: 鐩存帴鍧愭爣
    coord_match = re.match(r'鍧愭爣[::]\s*(\d+)\s*[,,]\s*(\d+)', desc)
    if coord_match:
        return {"x": int(coord_match.group(1)), "y": int(coord_match.group(2)), "method": "coordinate"}
    
    # 鏂瑰紡2: OCR鏂囧瓧鏌ユ壘
    text_match = re.match(r'鏂囨湰[::]\s*(.+)', desc)
    if text_match:
        target_text = text_match.group(1).strip()
        try:
            import pytesseract
            from PIL import ImageGrab
            import cv2
            import numpy as np
            
            img = ImageGrab.grab()
            img_np = np.array(img)
            # OCR鑾峰彇鎵€鏈夋枃瀛椾綅缃?
            data = pytesseract.image_to_data(img_np, lang='chi_sim+eng', output_type=pytesseract.Output.DICT)
            for i, text in enumerate(data['text']):
                if target_text in text:
                    x = data['left'][i] + data['width'][i] // 2
                    y = data['top'][i] + data['height'][i] // 2
                    if data['conf'][i] > 30:  # 缃俊搴?30%
                        return {"x": x, "y": y, "method": f"ocr:{text}", "confidence": data['conf'][i]}
        except ImportError:
            pass  # OCR涓嶅彲鐢?闄嶇骇
        except Exception:
            pass
        return None  # 鎵句笉鍒版枃瀛?
    
    # 鏂瑰紡3: 鍥惧儚妯℃澘鍖归厤
    img_match = re.match(r'鍥剧墖[::]\s*(.+)', desc)
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
    
    # 鏂瑰紡4: 璇箟鍖哄煙
    area_map = {
        "宸︿笂瑙?: (100, 100), "鍙充笂瑙?: (1820, 100),
        "宸︿笅瑙?: (100, 980), "鍙充笅瑙?: (1820, 980),
        "灞忓箷涓ぎ": (960, 540), "寮€濮嬭彍鍗?: (50, 1030),
        "浠诲姟鏍?: (960, 1050), "妗岄潰涓績": (960, 540),
        "鍏抽棴鎸夐挳": (1880, 10), "鏈€灏忓寲": (1840, 10),
    }
    for area_name, (ax, ay) in area_map.items():
        if area_name in desc:
            return {"x": ax, "y": ay, "method": f"area:{area_name}"}
    
    return None

# ===== 鍔ㄤ綔鎵ц =====
async def execute_action(action, params, ws=None):
    """鎵ц鍗曚釜鎿嶆帶鍔ㄤ綔,杩斿洖缁撴灉"""
    try:
        if action == "screenshot":
            b64 = screenshot_to_base64()
            return {"ok": True, "screenshot": b64, "action": action}
        
        elif action == "click":
            # 鏅鸿兘瀹氫綅浼樺厛
            target_desc = params.get("target", "")
            pos = find_element(target_desc) if target_desc else None
            
            if pos:
                x, y = pos["x"], pos["y"]
            elif "x" in params and "y" in params:
                x, y = params["x"], params["y"]
            else:
                return {"ok": False, "error": "闇€瑕佸潗鏍囨垨鍏冪礌鎻忚堪", "action": action}
            
            import pyautogui
            pyautogui.moveTo(x, y, duration=0.3)  # 浜虹被鍖栫Щ鍔?
            time.sleep(0.1)
            pyautogui.click()
            result = {"ok": True, "action": action, "clicked": [x, y], "method": pos["method"] if pos else "coordinate"}
            # 鐐瑰嚮鍚庤嚜鍔ㄦ埅鍥鹃獙璇?
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
            # 鏀寔涓枃杈撳叆
            import pyautogui, pyperclip
            try:
                pyperclip.copy(text)
                pyautogui.hotkey('ctrl', 'v')
            except ImportError:
                pyautogui.write(text, interval=0.05)  # 浜虹被鍖栨墦瀛楅€熷害
            return {"ok": True, "action": action, "typed": text[:50]}
        
        elif action == "press_key":
            key = params.get("key", "")
            import pyautogui
            # 鏀寔缁勫悎閿?
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
            seconds = min(params.get("seconds", 1), 30)  # 鏈€澶氱瓑30绉?
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
            await asyncio.sleep(1.5)  # 绛夊簲鐢ㄥ惎鍔?
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
            # 濮旀墭缁橮laywright鎵ц
            command = params.get("command", "")
            try:
                from playwright.async_api import async_playwright
                async with async_playwright() as p:
                    browser = await p.chromium.launch(headless=False)
                    page = await browser.new_page()
                    # 绠€鍖栫増:璁〢I鍏堟媶姝ラ
                    await page.goto("https://www.google.com")
                    await page.fill('textarea[name="q"]', command)
                    await page.press('textarea[name="q"]', "Enter")
                    await page.wait_for_load_state("networkidle")
                    text = await page.inner_text("body")
                    await browser.close()
                    return {"ok": True, "action": action, "result": text[:2000]}
            except ImportError:
                return {"ok": False, "error": "Playwright鏈畨瑁?, "action": action}
        
        else:
            return {"ok": False, "error": f"鏈煡鎿嶄綔: {action}", "action": action}
    
    except Exception as e:
        return {"ok": False, "error": str(e), "action": action}

# ===== 涓诲惊鐜?=====
async def main():
    import websockets
    print(f"\n{'='*60}")
    print(f"  Friday AI 鏈湴 Agent v2.0")
    print(f"  瀹㈡埛绔疘D: {CLIENT_ID}")
    print(f"  鏈嶅姟鍣?   {SERVER}")
    print(f"  瑙嗚鐞嗚В: {'鉁?鍚敤' if VISION_ENABLED else '鉂?鍏抽棴'}")
    print(f"{'='*60}\n")
    
    # 妫€鏌ヤ緷璧?
    deps_ok = True
    try:
        import pyautogui
        print(f"  鉁?pyautogui {pyautogui.__version__ if hasattr(pyautogui,'__version__') else 'OK'}")
    except ImportError:
        print(f"  鉂?pyautogui 鏈畨瑁?)
        deps_ok = False
    try:
        import PIL
        print(f"  鉁?Pillow OK")
    except ImportError:
        print(f"  鉂?Pillow 鏈畨瑁?)
        deps_ok = False
    try:
        import pytesseract
        print(f"  鉁?pytesseract OK (鏂囧瓧璇嗗埆)")
    except ImportError:
        print(f"  鈿狅笍  pytesseract 鏈畨瑁?(鏂囧瓧鏌ユ壘闄嶇骇)")
    try:
        import cv2
        print(f"  鉁?OpenCV OK (鍥惧儚鍖归厤)")
    except ImportError:
        print(f"  鈿狅笍  OpenCV 鏈畨瑁?(鍥惧儚鍖归厤闄嶇骇)")
    
    if not deps_ok:
        print(f"\n  璇峰畨瑁呯己澶变緷璧? pip install pyautogui pillow\n")
    
    while True:
        try:
            print(f"[杩炴帴] 姝ｅ湪杩炴帴 {SERVER} ...")
            async with websockets.connect(SERVER, ping_interval=20, ping_timeout=10) as ws:
                # 娉ㄥ唽
                await ws.send(json.dumps({
                    "type": "register",
                    "client_id": CLIENT_ID,
                    "hostname": CLIENT_ID,
                    "version": "2.0",
                    "capabilities": ["screenshot", "click", "type", "scroll", "ocr", "vision"]
                }))
                print(f"[娉ㄥ唽] 鉁?宸叉敞鍐屽埌鏈嶅姟鍣?)
                
                # 蹇冭烦
                async def heartbeat():
                    while True:
                        await asyncio.sleep(25)
                        try:
                            await ws.send(json.dumps({"type": "ping"}))
                        except:
                            break
                asyncio.create_task(heartbeat())
                
                # 鎸囦护寰幆
                async for msg in ws:
                    data = json.loads(msg)
                    msg_type = data.get("type", "")
                    
                    if msg_type == "execute":
                        action = data.get("action", "")
                        params = data.get("params", {})
                        task_id = data.get("task_id", "")
                        print(f"\n[鎵ц] {action} | {str(params)[:80]}")
                        
                        result = await execute_action(action, params, ws)
                        
                        # 杩斿洖缁撴灉
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
                        
                        status = "鉁? if result.get("ok") else "鉂?
                        print(f"[缁撴灉] {status} {str(result)[:120]}")
                    
                    elif msg_type == "vision_request":
                        # 鏈嶅姟鍣ㄨ姹傛埅鍥剧敤浜嶢I瑙嗚鍒嗘瀽
                        shot = screenshot_to_base64()
                        await ws.send(json.dumps({
                            "type": "vision_response",
                            "screenshot": shot,
                            "task_id": data.get("task_id", "")
                        }))
                    
                    elif msg_type == "pong":
                        pass  # 蹇冭烦鍝嶅簲
                    
                    elif msg_type == "registered":
                        print(f"[鏈嶅姟鍣╙ {data.get('message', 'OK')}")
                    
                    else:
                        print(f"[鏈煡娑堟伅] {msg_type}")
        
        except websockets.exceptions.ConnectionClosed:
            print(f"[鏂紑] 杩炴帴鍏抽棴,5绉掑悗閲嶈繛...")
        except Exception as e:
            print(f"[閿欒] {str(e)[:200]}, 5绉掑悗閲嶈繛...")
        
        await asyncio.sleep(5)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print(f"\n[閫€鍑篯 Agent宸插仠姝?)
    except Exception as e:
        print(f"\n[鑷村懡閿欒] {e}")'''
    return {
        "ok": True,
        "version": "2.0",
        "filename": "friday_agent.py",
        "script": script,
        "instructions": "pip install websockets pyautogui pillow psutil playwright pytesseract opencv-python pyperclip && playwright install chromium && python friday_agent.py",
        "capabilities": ["鎴浘+瑙嗚鐞嗚В","鏅鸿兘鍏冪礌瀹氫綅(OCR/鍥惧儚/鍧愭爣)","21绉嶅姩浣?,"鍙屽嚮/鍙抽敭/鎷栨嫿","蹇嵎閿?,"绐楀彛绠＄悊","娴忚鍣ㄨ嚜鍔ㄥ寲","绯荤粺鍛戒护","鑷籂閿?]
    }


# ===== 浜哄舰Agent(鍗囩骇鐗?=====
@router.post("/agent/human")
async def human_like_agent(req: dict, _=Depends(verify_token)):
    """浜虹被绾х數鑴戞搷鎺?- 鏅鸿兘璺敱: 浠ｇ爜浠诲姟鐩存帴鎵ц, GUI浠诲姟瑙嗚鎿嶆帶, 鑷姩鐪侀挶"""
    command = req.get("command","")
    target = req.get("target","server")
    max_cycles = req.get("max_cycles", 8)
    action_log = []
    
    # ===== 绗?姝? 浠诲姟鏅鸿兘鍒嗙被 =====
    classify_prompt = f"""鍒ゆ柇杩欎釜浠诲姟灞炰簬鍝竴绫?鍙洖澶嶄竴涓瘝:
- "code": 浠ｇ爜/鏂囦欢/鏈嶅姟鍣?鍛戒护/鏁版嵁澶勭悊 (涓嶉渶瑕佺湅灞忓箷)
- "gui": 鎿嶆帶妗岄潰搴旂敤/GUI/娴忚鍣?闇€瑕佺湅灞忓箷
浠诲姟: {command}
鍒嗙被:"""
    
    task_type = (await _call_ai(
        [{"role":"user","content":classify_prompt}],
        model=CHEAP_MODEL, max_tokens=10, temperature=0
    )).strip().lower()
    
    if "code" in task_type:
        # ===== 浠ｇ爜/鏈嶅姟鍣ㄤ换鍔? 闆舵埅鍥?鐩存帴鎵ц =====
        code_prompt = f"""浣犳槸鏈嶅姟鍣ㄧ鐞咥I.瀹屾垚杩欎釜浠诲姟,鍥炲JSON:
{{"steps":[{{"action":"run_command|read_file|write_file|search|done","params":{{}},"reason":"涓轰粈涔?}}],"summary":"鎬荤粨"}}
鍙敤鎿嶄綔: run_command(鎵цshell), read_file(璇绘枃浠?, write_file(鍐欐枃浠?, search(鎼滅储鍐呭), done(瀹屾垚)
浠诲姟: {command}
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
                        results.append(f"[read] {path}: 鏂囦欢涓嶅瓨鍦?)
                elif a == "write_file":
                    path = p.get("path",""); txt = p.get("content","")
                    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
                    with open(path,"w") as f: f.write(txt)
                    results.append(f"[write] {path}: 宸插啓鍏len(txt)}瀛楃")
                elif a == "search":
                    import glob
                    pattern = p.get("pattern","*")
                    found = glob.glob(pattern, recursive=True)[:20]
                    results.append(f"[search] {pattern}: {found}")
                elif a == "done":
                    break
            except Exception as e:
                results.append(f"[{a}] 閿欒: {str(e)[:200]}")
        
        # 鍋氫竴娆℃渶缁堟€荤粨 (渚垮疁妯″瀷)
        summary = await _call_ai([
            {"role":"user","content":f"浠诲姟:{command}\n鎵ц缁撴灉:\n"+'\n'.join(results)+"\n\n璇蜂竴鍙ヨ瘽鎬荤粨瀹屾垚鎯呭喌."}
        ], model=CHEAP_MODEL, max_tokens=100, temperature=0)
        
        token_estimate = len(classify_prompt) + len(plan) + len(summary) + 300
        return {
            "ok":True, "completed":True, "mode":"code", "cycles":len(action_log),
            "log":action_log, "results":results, "final_result":summary,
            "token_saved": True, "estimated_tokens": token_estimate,
            "vs_visual_mode": f"鐪佷簡绾(max_cycles*1500 - token_estimate)//1000}k tokens"
        }
    
    # ===== GUI浠诲姟: 瑙嗚鎿嶆帶(浼樺寲鐗? =====
    system_prompt = """浣犳槸鐢佃剳鎿嶆帶AI.鐪嬪埌鎴浘鍚庡洖澶岼SON: {"observation":"鐪嬪埌浜嗕粈涔?,"thought":"鎬濊€?,"action":"鎿嶄綔鍚?,"target":"鍏冪礌鎻忚堪(鏂囨湰:xxx/鍧愭爣:x,y)","params":{},"confidence":0.8}
鎿嶄綔: click|double_click|type_text|press_key|scroll|move|wait|open_app|close_window|switch_window|select_all|copy|paste|undo|save|run_command|done|fail
鍘熷垯: 鐢╰arget鎻忚堪鍏冪礌(濡?鏂囨湰:鐧诲綍"), 鎿嶄綔鍚庨獙璇? 鍗′綇鎹㈢瓥鐣?"""
    
    cycle = 0
    last_screenshot = None
    last_action = None  # 閬垮厤閲嶅鎴浘
    
    while cycle < max_cycles:
        cycle += 1
        
        # 鍙湪蹇呰鏃舵埅鍥?(杩炵画鎵撳瓧/鎸夐敭鍚庝笉闇€瑕?
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
            return {"ok":False,"error":"鏃犳硶鑾峰彇灞忓箷鎴浘","cycle":cycle}
        if not screenshot_b64:
            action_log.append({"cycle":cycle,"error":"鎴浘澶辫触"}); break
        
        last_screenshot = screenshot_b64
        
        # 妯″瀷閫夋嫨: 鍓?姝ョ敤CHEAP_MODEL(榛樿deepseek-chat), 鍗′綇浜嗙敤SMART_MODEL
        use_model = pick_model(need_vision=True, step_count=cycle)
        user_prompt = f"浠诲姟: {command}\n绗瑊cycle}/{max_cycles}姝?\n涔嬪墠鎿嶄綔: {json.dumps(action_log[-3:],ensure_ascii=False)}\n鍒嗘瀽鎴浘,鐢╰arget鎻忚堪鍏冪礌."
        
        ai_response = await _call_ai([
            {"role":"system","content":system_prompt},
            {"role":"user","content":[{"type":"text","text":user_prompt},{"type":"image_url","image_url":{"url":f"data:image/png;base64,{screenshot_b64}","detail":"low"}}]}  # low detail = 鏇翠究瀹?
        ], model=use_model, max_tokens=300, temperature=0.3)
        
        decision = {}
        try:
            json_match = re.search(r'\{[^{}]*"action"[^{}]*\}', ai_response, re.DOTALL)
            if json_match: decision = json.loads(json_match.group())
        except: pass
        
        if not decision:
            action_log.append({"cycle":cycle,"error":"瑙ｆ瀽澶辫触"}); continue
        
        action = decision.get("action","screenshot")
        params = decision.get("params",{})
        last_action = action
        
        action_log.append({"cycle":cycle,"observation":decision.get("observation","")[:80],"thought":decision.get("thought","")[:80],"action":action,"target":decision.get("target","")})
        
        if action == "done":
            return {"ok":True,"completed":True,"mode":"gui","cycles":cycle,"log":action_log,"result":params.get("summary",""),"screenshot":last_screenshot,"model":CHEAP_MODEL,"estimated_tokens":cycle*500}
        if action == "fail":
            return {"ok":False,"error":params.get("reason","浠诲姟澶辫触"),"mode":"gui","cycles":cycle,"log":action_log}
        
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
    
    return {"ok":False,"error":"杈惧埌鏈€澶у惊鐜鏁?,"mode":"gui","cycles":cycle,"log":action_log,"screenshot":last_screenshot,"estimated_tokens":cycle*500}

@router.post("/agent/quick")
async def quick_agent_action(req: dict, _=Depends(verify_token)):
    client_id = req.get("client_id","")
    action = req.get("action","")
    params = req.get("params",{})
    actions_help = {"screenshot":"鎴彇灞忓箷","open_url":"鎵撳紑缃戝潃","click":"鍗曞嚮","double_click":"鍙屽嚮","right_click":"鍙抽敭","type_text":"杈撳叆鏂囧瓧","press_key":"鎸夐敭","run_command":"杩愯鍛戒护","get_info":"绯荤粺淇℃伅","open_app":"鎵撳紑搴旂敤","scroll":"婊氳疆","move_mouse":"绉诲姩榧犳爣","close_window":"鍏抽棴绐楀彛","switch_window":"鍒囨崲绐楀彛","select_all":"鍏ㄩ€?,"copy":"澶嶅埗","paste":"绮樿创","undo":"鎾ら攢","save":"淇濆瓨","browser_task":"娴忚鍣ㄤ换鍔?}
    if not client_id: return {"ok":False,"error":"璇锋寚瀹歝lient_id","available_clients":list(connected_remotes.keys()),"actions":actions_help}
    if client_id not in connected_remotes: return {"ok":False,"error":f"瀹㈡埛绔?{client_id} 鏈繛鎺?,"available":list(connected_remotes.keys())}
    if action == "screenshot":
        ws = connected_remotes[client_id]
        await ws.send_json({"type":"execute","action":"screenshot","params":{}})
        for _ in range(20):
            try:
                data = await asyncio.wait_for(ws.receive_json(), timeout=3.0)
                if data.get("type") == "result" and data.get("screenshot"): return {"ok":True,"action":action,"screenshot":data.get("screenshot")}
            except: break
        return {"ok":False,"error":"鎴浘瓒呮椂"}
    return await execute_remote(req, _)

@router.get("/agent/actions")
async def list_actions(_=Depends(verify_token)):
    return {"ok":True,"actions":{"screenshot":"鎴彇灞忓箷","open_url":"鎵撳紑缃戝潃","click":"鍗曞嚮","double_click":"鍙屽嚮","right_click":"鍙抽敭","type_text":"杈撳叆鏂囧瓧","press_key":"鎸夐敭","run_command":"杩愯绯荤粺鍛戒护","get_info":"绯荤粺淇℃伅","open_app":"鎵撳紑搴旂敤","scroll":"婊氳疆","move_mouse":"绉诲姩榧犳爣","drag":"鎷栨嫿","wait":"绛夊緟","close_window":"鍏抽棴绐楀彛","switch_window":"鍒囨崲绐楀彛","select_all":"鍏ㄩ€?,"copy":"澶嶅埗","paste":"绮樿创","undo":"鎾ら攢","save":"淇濆瓨","browser_task":"AI娴忚鍣ㄤ换鍔?}}

# ===== 缁熶竴娴忚鍣ˋgent =====
@router.post("/browser/unified")
async def unified_browser(req: dict, _=Depends(verify_token)):
    command = req.get("command","")
    target = req.get("target","server")
    if target == "server" or target in list(connected_remotes.keys()):
        if target != "server":
            if target not in connected_remotes: return {"ok":False,"error":f"瀹㈡埛绔?{target} 鏈繛鎺?}
            ws = connected_remotes[target]
            await ws.send_json({"type":"execute","action":"browser_task","params":{"command":command}})
            return {"ok":True,"sent_to":target,"command":command}
        else:
            req_obj = BrowserAgentRequest(command=command, headless=True, max_steps=10)
            return await browser_agent(req_obj, _)
    return {"ok":False,"error":"鏈煡鐩爣","available_targets":["server"]+list(connected_remotes.keys())}



# ===== 8.7 妯″瀷甯傚満API =====
@router.get("/models")
async def list_models(_=Depends(verify_token)):
    """鍒楀嚭鎵€鏈夊彲鐢ˋI妯″瀷鍙婁环鏍?""
    available = {}
    for name, info in AVAILABLE_MODELS.items():
        key = DEEPSEEK_KEY if info["provider"] == "deepseek" else OPENAI_KEY
        available[name] = {**info, "available": bool(key)}
    return {
        "ok": True,
        "models": available,
        "current_cheap": CHEAP_MODEL,
        "current_smart": SMART_MODEL,
        "config_hint": "鐜鍙橀噺: CHEAP_MODEL / SMART_MODEL / DEEPSEEK_API_KEY / OPENAI_API_KEY"
    }

@router.post("/models/test")
async def test_model(req: dict, _=Depends(verify_token)):
    """娴嬭瘯鎸囧畾妯″瀷鏄惁鍙敤"""
    model = req.get("model", CHEAP_MODEL)
    try:
        result = await _call_ai([{"role":"user","content":"鍥炲OK"}], model=model, max_tokens=10, temperature=0)
        return {"ok": True, "model": model, "response": result[:50], "status": "鍙敤" if "OK" in result else "寮傚父"}
    except Exception as e:
        return {"ok": False, "model": model, "error": str(e)[:200]}

# ===== 9. AI閫氱煡鎺ㄩ€?=====
@router.post("/notify")
async def send_notification(req: dict, _=Depends(verify_token)):
    """鎺ㄩ€侀€氱煡鍒版墍鏈夎繛鎺ョ殑瀹㈡埛绔?""
    title = req.get("title","Friday AI")
    body = req.get("body","")
    url = req.get("url","/ai/")
    
    # 閫氳繃WebSocket骞挎挱閫氱煡
    try:
        from routers.ws_router import manager
        await manager.broadcast(json.dumps({
            "type":"notification",
            "title":title,"body":body,"url":url,"time":datetime.now().isoformat()
        }))
        return {"ok":True,"message":"閫氱煡宸插箍鎾?}
    except Exception as e:
        return {"ok":False,"error":str(e)}

@router.post("/agent/human/correct")
async def human_agent_correct(command: str = "", target: str = "server", _=Depends(verify_token)):
    """人形Agent自纠错"""
    try:
        from agents.multi_model import ModelRouter
        resp = ModelRouter.smart_chat(messages=[{"role":"user","content":f"操作失败: {command}。分析原因给修正指令,只返回命令。"}], mode="smart")
        corrected = resp.get("content","") if isinstance(resp,dict) else str(resp)
        import subprocess, shlex
        result = subprocess.run(corrected.strip().split(), capture_output=True, text=True, timeout=60)
        return {"ok":True,"corrected":corrected.strip(),"stdout":result.stdout[:2000]}
    except Exception as e:
        return {"ok":False,"error":str(e)}
