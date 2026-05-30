"""妤傛楠嘇I瀵洘鎼?-- 鐎圭偞妞傜拠顓㈢叾閹垫挻鏌?/ 鐟欏棝顣跺ù浣稿瀻閺?/ 濞ｅ崬瀹抽惍鏃傗敀 / 閺佺増宓侀崣顖濐潒閸?/ 閺傚洣娆㈢€电厧鍤?/ 缂冩垿銆夐幎鎾冲絿 / 濞村繗顫嶉崳銊ㄥ殰閸斻劌瀵?/ 闂€澶哥瑐娑撳鏋?""
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
# 濡€崇€风捄顖滄暠: deepseek-瀵偓婢跺娈戠挧鐧塭epSeek, 閸忔湹绮挧鐧榩enAI
CHEAP_MODEL = os.getenv("CHEAP_MODEL", "deepseek-chat")
SMART_MODEL = os.getenv("SMART_MODEL", "gpt-4o")
# ===== 濡€崇€风敮鍌氭簚 -- AI閼奉亜绻侀柅澶嬆侀崹?=====
AVAILABLE_MODELS = {
    # 娓氬灝鐤佸顖炴Е (缁犫偓閸楁洑鎹㈤崝?
    "deepseek-chat":       {"provider": "deepseek", "cost": "0.14/1M",  "strength": "閺冦儱鐖剁€电鐦?缁犫偓閸楁洘鎼锋担?韫囶偊鈧喎鎼锋惔?},
    CHEAP_MODEL:       {"provider": "openai",   "cost": "0.50/1M",  "strength": "閸掑棛琚?閸掋倖鏌?缁犫偓閸楁洖鍠呯粵?},
    # 閹傜幆濮ｆ梹顫梼?(閺咁噣鈧矮鎹㈤崝?
    CHEAP_MODEL:         {"provider": "openai",   "cost": "0.15/1M",  "strength": "鐟欏棜顫庨悶鍡毿?婢舵碍膩閹?韫囶偊鈧喐甯归悶?},
    "deepseek-reasoner":   {"provider": "deepseek", "cost": "0.55/1M",  "strength": "濞ｅ崬瀹抽幒銊ф倞/婢跺秵娼呴崚鍡樼€?},
    # 妤傛顏顖炴Е (婢跺秵娼呮禒璇插)
    "gpt-4o":              {"provider": "openai",   "cost": "2.50/1M",  "strength": "妤傛绨挎惔锕侇潒鐟?婢跺秵娼呴崘宕囩摜/婢舵碍顒炴?},
    "claude-3-5-sonnet":   {"provider": "openai",   "cost": "3.00/1M",  "strength": "娴狅絿鐖滈悽鐔稿灇/闂€鎸庢瀮閺堫剙鍨庨弸?},
}

def pick_model(task_complexity="auto", need_vision=False, step_count=0):
    """AI閼奉亜濮╅柅澶嬆侀崹? 閺嶈宓佹禒璇插婢跺秵娼呮惔锔衡偓浣规Ц閸氾箓娓剁憰浣筋潒鐟欏鈧礁缍嬮崜宥嗩劄妤犮倖鏆?""
    if task_complexity == "simple" or (step_count > 0 and step_count <= 3):
        return CHEAP_MODEL  # 姒涙顓绘笟鍨杹濡€崇€?
    elif task_complexity == "hard" or step_count > 5:
        return SMART_MODEL  # 姒涙顓婚懕顏呮濡€崇€?
    elif need_vision:
        return CHEAP_MODEL if OPENAI_KEY else CHEAP_MODEL  # 鐟欏棜顫庢禒璇插闂団偓鐟曚礁顦垮Ο鈩冣偓浣鼓侀崹?
    return CHEAP_MODEL


router = APIRouter(prefix="/agent/advanced", tags=["AdvancedAI"])
# 婢舵rovider
OPENAI_KEY = OPENAI_API_KEY
DEEPSEEK_KEY = DEEPSEEK_API_KEY
DS_BASE_URL = DEEPSEEK_BASE_URL
BASE_URL = OPENAI_BASE_URL or "https://api.openai.com/v1"

async def _call_ai(messages, model=None, max_tokens=1000, temperature=0.7):
    if model is None: model = CHEAP_MODEL
    """婢舵rovider AI鐠嬪啰鏁?- 閼奉亜濮╃捄顖滄暠DeepSeek/OpenAI"""
    import httpx
    # 閺嶈宓佸Ο鈥崇€烽崥宥堝殰閸斻劑鈧瀚╬rovider
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
            return "闂団偓鐟曚線鍘ょ純鐡礟I Key"
    
    async with httpx.AsyncClient(timeout=120) as c:
        r = await c.post(f"{base}/chat/completions",
            headers={"Authorization":f"Bearer {key}","Content-Type":"application/json"},
            json={"model":model,"messages":messages,"max_tokens":max_tokens,"temperature":temperature})
        if r.status_code == 200:
            return r.json().get("choices",[{}])[0].get("message",{}).get("content","")
        return f"API闁挎瑨顕?{r.status_code}"

# ===== 1. 鐎圭偞妞傜拠顓㈢叾閹垫挻鏌?WebSocket =====
@router.websocket("/voice/live")
async def live_voice(ws: WebSocket):
    """鐎圭偞妞傜拠顓㈢叾鐎电鐦?-- 閺€顖涘瘮閹垫挻鏌?閹懏鍔?閼奉亞鍔х€电鐦?""
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
                # 閻劍鍩涢幍鎾存焽瑜版挸澧犻崶鐐差槻
                if current_task and not current_task.done():
                    current_task.cancel()
                await ws.send_json({"type":"interrupted"})
            elif msg_type == "speech":
                text = data.get("text","")
                if not text: continue
                conversation.append({"role":"user","content":text})
                await ws.send_json({"type":"status","text":"閹繆鈧啩鑵?.."})
                
                msgs = [{"role":"system","content":"娴ｇ姵妲窮riday AI閸斺晜澧?閻劏鍤滈悞鍓佹畱閸欙綀顕㈤崶鐐差槻,鐢箓鈧倸缍嬮惃鍕剰閹?閸欘垯浜掔粭鎴欌偓浣稿締濮樻柣鈧焦鍎曠拋?閸ョ偛顦茬粻鈧ú浣藉殰閻?閸嶅繑婀呴崣瀣喊婢?娑撳秷顩﹂悽鈺゛rkdown."}]
                msgs.extend(conversation[-15:])
                
                current_task = asyncio.create_task(stream_ai_reply(msgs))
                try:
                    full_reply = await current_task
                    conversation.append({"role":"assistant","content":full_reply})
                    await ws.send_json({"type":"done","full":full_reply})
                except asyncio.CancelledError:
                    await ws.send_json({"type":"interrupted"})
            elif msg_type == "emotion":
                # 鐎广垺鍩涚粩顖涱梾濞村鍩岄惃鍕剰缂?
                await ws.send_json({"type":"status","text":"瀹稿弶鍔呴惌銉﹀剰缂? "+data.get("emotion","neutral")})
    except WebSocketDisconnect:
        pass

# ===== 2. 鐎圭偞妞傜憴鍡涱暥鐢冨瀻閺?=====
class FrameRequest(BaseModel):
    image_base64: str
    context: str = ""

@router.post("/vision/live")
async def live_vision(req: FrameRequest, _=Depends(verify_token)):
    """鐎圭偞妞傜憴鍡涱暥鐢冨瀻閺?-- 鏉╃偟鐢荤敮褏鎮婄憴?""
    prompt = "娴ｇ姵顒滈崷銊ф箙鐎圭偞妞傜憴鍡涱暥濞?鐠囬鏁ゆ稉鈧崣銉ㄧ樈閹诲繗鍫悽濠氭桨閸愬懎顔?婵″倹鐏夐張澶娾偓鐓庣繁濞夈劍鍓伴惃鍕綁閸栨牞顕幐鍥у毉."
    if req.context: prompt = f"娑斿澧犳担鐘垫箙閸?{req.context}\n缂佈呯敾鐟欏倸鐧?"
    
    result = await _call_ai([
        {"role":"system","content":"娴ｇ姵妲哥€圭偞妞傜憴鍡涱暥閸掑棙鐎紸I.缁犫偓濞蹭焦寮挎潻鎵暰闂?"},
        {"role":"user","content":[
            {"type":"text","text":prompt},
            {"type":"image_url","image_url":{"url":f"data:image/jpeg;base64,{req.image_base64}"}}
        ]}
    ], model=CHEAP_MODEL, max_tokens=200)
    return {"ok":True,"description":result}

# ===== 3. 濞ｅ崬瀹抽惍鏃傗敀 Agent =====
class ResearchRequest(BaseModel):
    topic: str
    depth: int = 2  # 閻梻鈹掑ǎ鍗炲 1-3

@router.post("/research")
async def deep_research(req: ResearchRequest, _=Depends(verify_token)):
    """婢舵碍顒為懛顏冨瘜閻梻鈹?-- 閹兼粎鍌?>閸掑棙鐎?>缂佺厧鎮?>閹躲儱鎲?""
    import httpx
    
    # Step 1: 閻㈢喐鍨氶幖婊呭偍鐎涙劙妫舵０?
    questions_prompt = f"鐏忓棛鐖虹粚鏈靛瘜妫版ɑ濯堕崚鍡曡礋{min(req.depth*2,5)}娑擃亜鍙挎担鎾崇摍闂傤噣顣?閸欘亣绻戦崶鐐烘６妫版ê鍨悰?濮ｅ繗顢戞稉鈧稉?\n娑撳顣?{req.topic}"
    sub_questions = await _call_ai([{"role":"user","content":questions_prompt}], max_tokens=300)
    questions = [q.strip().lstrip('0123456789.-) ') for q in sub_questions.split('\n') if q.strip()][:5]
    
    # Step 2: 閹兼粎鍌ㄥВ蹇庨嚋鐎涙劙妫舵０?
    findings = []
    for q in questions[:req.depth*2]:
        try:
            async with httpx.AsyncClient(timeout=15) as c:
                r = await c.get("https://html.duckduckgo.com/html/",
                    params={"q": q}, headers={"User-Agent":"Mozilla/5.0"})
                # 閹绘劕褰囬幗妯款洣
                snippets = []
                for m in re.finditer(r'class="result__snippet"[^>]*>([^<]+)', r.text):
                    snippets.append(m.group(1).strip())
                summary_text = " ".join(snippets[:3])[:500]
                if summary_text:
                    # Step 3: AI閸掑棙鐎藉В蹇庨嚋鐎涙劙妫舵０?
                    analysis = await _call_ai([
                        {"role":"user","content":f"鐎涙劙妫舵０?{q}\n閹兼粎鍌ㄧ紒鎾寸亯:{summary_text}\n鐠囬鏁?-3閸欍儴鐦介幀鑽ょ波閸忔娊鏁崣鎴犲箛."}
                    ], max_tokens=200)
                    findings.append({"question":q,"sources":len(snippets),"finding":analysis})
        except: findings.append({"question":q,"sources":0,"finding":"閹兼粎鍌ㄦ径杈Е"})
    
    # Step 4: 缂佺厧鎮庨幎銉ユ啞
    findings_text = "\n".join([f"## {f['question']}\n{f['finding']}" for f in findings])
    report = await _call_ai([
        {"role":"system","content":"娴ｇ姵妲哥挧鍕箒閻梻鈹掗崨?閺嶈宓佹禒銉ょ瑓閻梻鈹掗崣鎴犲箛,閻㈢喐鍨氭稉鈧禒鐣岀波閺嬪嫬瀵查惃鍕埡缁岃埖濮ら崨?鐟曚焦婀侀幗妯款洣閵嗕礁鍙ч柨顔煎絺閻滆埇鈧胶绮ㄧ拋?"},
        {"role":"user","content":f"閻梻鈹掓稉濠氼暯:{req.topic}\n\n閻梻鈹掗崣鎴犲箛:\n{findings_text}\n\n鐠囬鏁撻幋鎰暚閺佸鐖虹粚鑸靛Г閸?"}
    ], max_tokens=2000)
    
    return {"ok":True,"topic":req.topic,"questions":questions,"findings":findings,"report":report}

# ===== 4. 閺佺増宓侀崣顖濐潒閸?+ CSV閸掑棙鐎?=====
class DataAnalyzeRequest(BaseModel):
    csv_data: str = ""
    question: str = "閸掑棙鐎介弫鐗堝祦楠炲墎绮伴崙鐑樼鐎?

@router.post("/data/analyze")
async def analyze_data(req: DataAnalyzeRequest, _=Depends(verify_token)):
    """娑撳﹣绱禖SV->AI閼奉亜濮╅崚鍡樼€?>閺傚洦婀?閸ユ崘銆冮弫鐗堝祦"""
    if not req.csv_data:
        return {"ok":False,"error":"闂団偓鐟曚竼SV閺佺増宓?}
    
    # 鐟欙絾鐎紺SV
    import csv as csv_mod
    reader = csv_mod.reader(io.StringIO(req.csv_data[:50000]))
    rows = list(reader)
    if not rows: return {"ok":False,"error":"CSV娑撹櫣鈹?}
    
    headers = rows[0]
    data_rows = rows[1:21]  # 閸?0鐞?
    row_count = len(rows) - 1
    col_count = len(headers)
    
    # 閸╃儤婀扮紒鐔活吀
    stats = {"rows":row_count,"columns":col_count,"headers":headers}
    numeric_cols = []
    for ci, h in enumerate(headers):
        try:
            vals = [float(r[ci]) for r in data_rows if ci < len(r)]
            numeric_cols.append({"name":h,"index":ci,"min":min(vals),"max":max(vals),"avg":round(sum(vals)/len(vals),2),"count":len(vals)})
        except: pass
    
    # AI閸掑棙鐎?
    preview = "\n".join([",".join(r) for r in [headers]+data_rows[:10]])
    prompt = f"""CSV閺佺増宓?{row_count}鐞?{col_count}閸?:
閺嶅洭顣? {headers}
缂佺喕顓? {json.dumps(numeric_cols,ensure_ascii=False)}
閸?0鐞? {preview[:1000]}

閻劍鍩涢梻顕€顣? {req.question}

鐠囬绮伴崙?1)閺佺増宓佸鍌濐潔 2)閸忔娊鏁ú鐐茬檪 3)瀵倸鐖堕崣鎴犲箛 4)瀵ら缚顔?缁犫偓濞蹭椒绗撴稉?"""
    
    insight = await _call_ai([{"role":"user","content":prompt}], max_tokens=800)
    
    # 閻㈢喐鍨欵Charts闁板秶鐤?
    chart_config = None
    if numeric_cols:
        nc = numeric_cols[0]
        chart_config = {
            "type":"bar","title":f"{nc['name']}閸掑棗绔?,
            "labels":["min","avg","max"],
            "values":[nc["min"],nc["avg"],nc["max"]],
            "suggestion":"閸欘垳鏁ら弴鏉戭樋閸掓浠涢幎妯煎殠閸?妤楃厧娴?
        }
    
    return {"ok":True,"stats":stats,"numeric_columns":numeric_cols,"insight":insight,"chart":chart_config}

# ===== 5. 閺傚洣娆㈢€电厧鍤?(PDF/Excel/Markdown) =====
class ExportRequest(BaseModel):
    content: str
    format: str = "md"  # md | html | txt
    filename: str = "report"

@router.post("/export")
async def export_file(req: ExportRequest, _=Depends(verify_token)):
    """鐎电厧鍤瑼I閻㈢喐鍨氶惃鍕敶鐎归€涜礋閺傚洣娆?""
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
    """娑撳娴囩€电厧鍤弬鍥︽"""
    fpath = Path(__file__).parent.parent / "data" / "exports" / filename
    if not fpath.exists():
        return {"ok":False,"error":"閺傚洣娆㈡稉宥呯摠閸?}
    media_types = {".md":"text/markdown",".html":"text/html",".txt":"text/plain",".csv":"text/csv",".json":"application/json"}
    ext = fpath.suffix
    return FileResponse(fpath, media_type=media_types.get(ext,"application/octet-stream"), filename=filename)

# ===== 6. 缂冩垿銆夐崘鍛啇閹舵挸褰?閹崵绮?=====
class ScrapeRequest(BaseModel):
    url: str

@router.post("/scrape")
async def scrape_url(req: ScrapeRequest, _=Depends(verify_token)):
    """閹舵挸褰囩純鎴︺€夐崘鍛啇楠炵I閹崵绮?""
    import httpx
    try:
        async with httpx.AsyncClient(timeout=20) as c:
            r = await c.get(req.url, headers={"User-Agent":"Mozilla/5.0"}, follow_redirects=True)
            if r.status_code != 200:
                return {"ok":False,"error":f"HTTP {r.status_code}"}
            
            html = r.text
            # 缁犫偓閺勬挻顒滈弬鍥ㄥ絹閸?
            text = re.sub(r'<script[^>]*>.*?</script>','',html,flags=re.DOTALL|re.I)
            text = re.sub(r'<style[^>]*>.*?</style>','',text,flags=re.DOTALL|re.I)
            text = re.sub(r'<[^>]+>',' ',text)
            text = re.sub(r'\s+',' ',text).strip()[:8000]
            
            # AI閹崵绮?
            summary = await _call_ai([
                {"role":"system","content":"娴ｇ姵妲哥純鎴︺€夐幀鑽ょ波娑撴挸顔?閻?-5閸欍儴鐦介幀鑽ょ波閺嶇绺鹃崘鍛啇,閹绘劕褰囬崗鎶芥暛娣団剝浼?"},
                {"role":"user","content":f"URL: {req.url}\n\n閸愬懎顔?\n{text[:5000]}"}
            ], max_tokens=300)
            
            title_match = re.search(r'<title[^>]*>([^<]+)</title>', html, re.I)
            title = title_match.group(1).strip() if title_match else req.url
            
            return {"ok":True,"url":req.url,"title":title,"text_length":len(text),"summary":summary}
    except Exception as e:
        return {"ok":False,"error":str(e)}

# ===== 7. AI濞村繗顫嶉崳藡gent -- 閼奉亞鍔х拠顓♀枅閹垮秵甯跺ù蹇氼潔閸?=====
class BrowserAgentRequest(BaseModel):
    command: str  # 閼奉亞鍔х拠顓♀枅閹稿洣鎶?
    headless: bool = True
    max_steps: int = 10

@router.post("/browser/agent")
async def browser_agent(req: BrowserAgentRequest, _=Depends(verify_token)):
    """AI濞村繗顫嶉崳藡gent -- 閼奉亞鍔х拠顓♀枅->濮濄儵顎冮幏鍡毿?>Playwright閹笛嗩攽->AI鐟欏棜顫庨悶鍡毿?""
    import httpx
    
    # Step 1: AI閹峰棜袙娴犺濮熸稉鐑橆劄妤?
    plan_prompt = f"""娴ｇ姵妲告稉鈧稉顏呯セ鐟欏牆娅掗懛顏勫З閸栨牔绗撶€?鐏忓棔浜掓稉瀣╂崲閸斺剝濯剁憴锝勮礋閸忚渹缍嬮惃鍕セ鐟欏牆娅掗幙宥勭稊濮濄儵顎?
鏉╂柨娲朖SON閺佹壆绮?濮ｅ繑顒為弽鐓庣础: {{"action":"navigate/click/type/wait/screenshot/extract/scroll","target":"闁瀚ㄩ崳銊﹀灗URL","value":"鏉堟挸鍙嗛崐鍏煎灗鐠囧瓨妲?,"reason":"娑撹桨绮堟稊鍫ｇ箹濮?}}

娴犺濮? {req.command}

鐟欏嫬鍨?
- navigate: 閹垫挸绱慤RL 
- click: 閻愮懓鍤崗鍐(閻劍鏋冮張顒佸灗CSS闁瀚ㄩ崳?
- type: 鏉堟挸鍙嗛弬鍥ㄦ拱(閸忓潏lick閸愬车ype)
- wait: 缁涘绶?缁?
- screenshot: 閹搭亜娴?
- extract: 閹绘劕褰囨い鐢告桨閺佺増宓?鐠囧瓨妲戠憰浣瑰絹閸欐牔绮堟稊?
- scroll: 閸氭垳绗呭姘З

閸欘亣绻戦崶婵睸ON閺佹壆绮?娑撳秷顩﹂崗鏈电铂閸愬懎顔?閺堚偓婢舵req.max_steps}濮?"""

    plan_text = await _call_ai([{"role":"user","content":plan_prompt}], max_tokens=800, temperature=0.3)
    
    # 鐟欙絾鐎藉銉╊€?
    steps = []
    try:
        json_match = re.search(r'\[.*\]', plan_text, re.DOTALL)
        if json_match:
            steps = json.loads(json_match.group())
    except:
        # Fallback: 缁犫偓閸楁洑鎹㈤崝锛勬纯閹恒儲澧界悰?
        steps = [{"action":"navigate","target":"https://www.google.com/search?q="+req.command.replace(" ","+"),"reason":"閹兼粎鍌?}]
    
    # Step 2: Playwright閹笛嗩攽
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
                # 閹绘劕褰囨い鐢告桨閺傚洦婀?
                script_lines.append(f"try:\n    text = page.inner_text('body')[:3000]\n    title = page.title()\n    outputs.append({{'step':{i},'action':'extract','ok':True,'title':title,'text':text}})\nexcept Exception as e:\n    outputs.append({{'step':{i},'action':'extract','ok':False,'error':str(e)}})")
            
            elif action == "scroll":
                script_lines.append(f"try:\n    page.evaluate('window.scrollBy(0,800)')\n    outputs.append({{'step':{i},'action':'scroll','ok':True}})\nexcept Exception as e:\n    outputs.append({{'step':{i},'action':'scroll','ok':False,'error':str(e)}})")
            
            else:
                script_lines.append(f"outputs.append({{'step':{i},'action':'{action}','ok':False,'error':'閺堫亞鐓￠幙宥勭稊'}})")
        
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
        
        # 鐟欙絾鐎界紒鎾寸亯
        for line in result.stdout.split('\n'):
            if line.startswith('RESULTS:'):
                try: results = json.loads(line[8:].strip())
                except: pass
        
        # 鐠囪褰囬幋顏勬禈
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
        
        # Step 3: AI閹崵绮ㄩ幍褑顢戠紒鎾寸亯
        result_summary = json.dumps([{"step":r.get("step"),"action":r.get("action"),"ok":r.get("ok"),"detail":str(r)[:200]} for r in results], ensure_ascii=False)
        summary = await _call_ai([
            {"role":"system","content":"娴ｇ姵妲稿ù蹇氼潔閸ｃ劏鍤滈崝銊ュ缂佹挻鐏夐崚鍡樼€界敮?缁犫偓閺勫孩鈧崵绮ㄩ幍褑顢戠紒鎾寸亯,閹绘劕褰囬崗鎶芥暛閺佺増宓侀崪灞藉絺閻?"},
            {"role":"user","content":f"娴犺濮? {req.command}\n濮濄儵顎冪拋鈥冲灊: {plan_text[:500]}\n閹笛嗩攽缂佹挻鐏? {result_summary}\n\n鐠囬鏁?-5閸欍儴鐦介幀鑽ょ波鐎瑰本鍨氭禍鍡曠矆娑?閹绘劕褰囨禍鍡楁憿娴滄稑鍙ч柨顔讳繆閹?"}
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
        return {"ok": False, "error": "濞村繗顫嶉崳銊︽惙娴ｆ粏绉撮弮?60缁?", "plan": steps}
    except Exception as e:
        return {"ok": False, "error": str(e), "plan": steps}

# ===== 濞村繗顫嶉崳藡gent韫囶偅宓庢禒璇插 =====
@router.post("/browser/quick")
async def browser_quick(req: dict, _=Depends(verify_token)):
    """韫囶偅宓庡ù蹇氼潔閸ｃ劋鎹㈤崝?-- 缁旂偛鎼ч柌鍥肠/閸熷棗鎼ч幋顏勬禈/妞ょ敻娼伴惄鎴炲付"""
    task_type = req.get("type","")
    url = req.get("url","")
    selector = req.get("selector","")
    
    commands = {
        "screenshot": f"閹垫挸绱?{url} 楠炶埖鍩呴崶?,
        "prices": f"閹垫挸绱?{url} 閹绘劕褰囬幍鈧張澶夌幆閺嶉棿淇婇幁?,
        "products": f"閹垫挸绱?{url} 閹绘劕褰囬崯鍡楁惂閸掓銆?閸氬秶袨+娴犻攱鐗?闁剧偓甯?",
        "monitor": f"閹垫挸绱?{url} 閹搭亜娴橀獮鑸靛絹閸欐牠銆夐棃顫瘜鐟曚礁褰夐崠?,
        "login_check": f"閹垫挸绱?{url} 濡偓閺屻儲妲搁崥锕傛付鐟曚胶娅ヨぐ?,
    }
    
    cmd = commands.get(task_type, req.get("command", f"閹垫挸绱?{url}"))
    req_obj = BrowserAgentRequest(command=cmd, headless=True, max_steps=8)
    return await browser_agent(req_obj, _)
# ===== 8. 闂€澶哥瑐娑撳鏋冪拋鏉跨箓閸樺缂?=====
class MemoryRequest(BaseModel):
    conversation_id: str = ""

@router.post("/memory/compress")
async def compress_memory(req: MemoryRequest, _=Depends(verify_token)):
    """閸樺缂夐梹鍨嚠鐠囨繀璐熼幗妯款洣 -- 缁愪胶鐗稉濠佺瑓閺傚洭妾洪崚?""
    try:
        from routers.agent_chat import _cdb
        c = _cdb()
        msgs = c.execute("SELECT role,content FROM msgs WHERE cid=? ORDER BY id",(req.conversation_id,)).fetchall()
        c.close()
        
        if len(msgs) < 20:
            return {"ok":True,"compressed":False,"message":"鐎电鐦芥潏鍐叚,閺冪娀娓堕崢瀣級"}
        
        full_text = "\n".join([f"{r[0]}: {r[1][:200]}" for r in msgs])
        summary = await _call_ai([
            {"role":"system","content":"娴ｇ姵妲哥€电鐦介幗妯款洣娑撴挸顔?鐏忓棔浜掓稉瀣毐鐎电鐦介崢瀣級娑撹櫣鐣濆ú浣规喅鐟?娣囨繄鏆€閸忔娊鏁穱鈩冧紖閵嗕礁鍠呯粵鏍モ偓浣哥窡閸旂偘绨ㄦい?"},
            {"role":"user","content":f"鐎电鐦?{len(msgs)}閺夆剝绉烽幁?:\n{full_text[:4000]}\n\n鐠囬鏁撻幋鎰喅鐟?娑撳秷绉存潻?00鐎?."}
        ], max_tokens=400)
        
        return {"ok":True,"compressed":True,"original_messages":len(msgs),"summary":summary}
    except Exception as e:
        return {"ok":False,"error":str(e)}



# ===== 8.5 鏉╂粎鈻奸悽浣冨壋閹貉冨煑 WebSocket =====
connected_remotes = {}  # {client_id: websocket}

@router.websocket("/remote/ws")
async def remote_control_ws(ws: WebSocket):
    """鏉╂粎鈻奸悽浣冨壋閹貉冨煑WebSocket - 閺堫剙婀碅gent鏉╃偞甯撮崥?AI閸欘垱鎼烽幒褎婀伴崷鎵暩閼?""
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
                await ws.send_json({"type":"registered","client_id":client_id,"message":"瀹稿弶鏁為崘?})
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
        return {"ok":False,"error":f"鐎广垺鍩涚粩?{client_id} 閺堫亣绻涢幒?,"available":list(connected_remotes.keys())}
    try:
        ws = connected_remotes[client_id]
        await ws.send_json({"type":"execute","action":action,"params":params})
        return {"ok":True,"sent":action,"to":client_id}
    except Exception as e:
        connected_remotes.pop(client_id, None)
        return {"ok":False,"error":str(e)}

# ===== 閺堫剙婀碅gent娑撳娴?v2.0 =====
async def download_agent_script():
    """娑撳娴囬張顒€婀碅gent閼存碍婀?v2.0 - 娴滆櫣琚痪褏鏁搁懘鎴炴惙閹?""
    script = '''
Friday AI 閺堫剙婀撮弲楦垮厴Agent v2.0 -- 娴滆櫣琚痪褏鏁搁懘鎴炴惙閹?
閼宠棄濮? 鐟欏棜顫庨悶鍡毿?- 閺呴缚鍏樼€规矮缍?- 娴犺濮熼幏鍡毿?- 閼奉亞绫傞柨?- 婢舵艾绨查悽銊︽惙閹?
閻劍纭? pip install websockets pyautogui pillow psutil playwright pytesseract opencv-python
      playwright install chromium
      python friday_agent.py
import asyncio, json, base64, os, sys, io, subprocess, re, time
from pathlib import Path
from datetime import datetime
import socket

# ===== 闁板秶鐤?=====
SERVER = os.getenv("FRIDAY_SERVER", "wss://tiktook.eu.cc/agent/advanced/remote/ws")
CLIENT_ID = socket.gethostname()
VISION_ENABLED = True  # 閺勵垰鎯侀崥顖滄暏鐟欏棜顫庨悶鍡毿?閹搭亜娴橀崣鎴犵舶閺堝秴濮熼崳藡I閸掑棙鐎?

# ===== 閹搭亜娴?=====
def screenshot_to_base64():
    """閹搭亜褰囬崗銊ョ潌 -> base64"""
    try:
        from PIL import ImageGrab
        img = ImageGrab.grab()
        buf = io.BytesIO()
        img.save(buf, format="PNG", optimize=True)
        return base64.b64encode(buf.getvalue()).decode()
    except Exception as e:
        return None

# ===== 閺呴缚鍏橀崗鍐鐎规矮缍?=====
def find_element(description, screenshot_b64=None):
    """
    閺呴缚鍏橀弻銉﹀鐏炲繐绠烽崗鍐,閺€顖涘瘮婢舵氨顫掗弬鐟扮础:
    - "閸ф劖鐖?500,400" -> 閻╁瓨甯存潻鏂挎礀閸ф劖鐖?
    - "閺傚洦婀?閻ц缍? -> OCR閺屻儲澹橀崠鍛儓"閻ц缍?閻ㄥ嫭鏋冪€涙ぞ缍呯純?
    - "閸ュ墽澧?button.png" -> 閸ユ儳鍎氬Ο鈩冩緲閸栧綊鍘?
    - "閸栧搫鐓?瀹革缚绗傜憴? -> 鏉╂柨娲栨０鍕啎閸栧搫鐓欓崸鎰垼
    鏉╂柨娲?{"x":int, "y":int, "method":str} 閹?None
    """
    if not description:
        return None
    
    desc = str(description).strip()
    
    # 閺傜懓绱?: 閻╁瓨甯撮崸鎰垼
    coord_match = re.match(r'閸ф劖鐖::]\s*(\d+)\s*[,,]\s*(\d+)', desc)
    if coord_match:
        return {"x": int(coord_match.group(1)), "y": int(coord_match.group(2)), "method": "coordinate"}
    
    # 閺傜懓绱?: OCR閺傚洤鐡ч弻銉﹀
    text_match = re.match(r'閺傚洦婀癧::]\s*(.+)', desc)
    if text_match:
        target_text = text_match.group(1).strip()
        try:
            import pytesseract
            from PIL import ImageGrab
            import cv2
            import numpy as np
            
            img = ImageGrab.grab()
            img_np = np.array(img)
            # OCR閼惧嘲褰囬幍鈧張澶嬫瀮鐎涙ぞ缍呯純?
            data = pytesseract.image_to_data(img_np, lang='chi_sim+eng', output_type=pytesseract.Output.DICT)
            for i, text in enumerate(data['text']):
                if target_text in text:
                    x = data['left'][i] + data['width'][i] // 2
                    y = data['top'][i] + data['height'][i] // 2
                    if data['conf'][i] > 30:  # 缂冾喕淇婃惔?30%
                        return {"x": x, "y": y, "method": f"ocr:{text}", "confidence": data['conf'][i]}
        except ImportError:
            pass  # OCR娑撳秴褰查悽?闂勫秶楠?
        except Exception:
            pass
        return None  # 閹靛彞绗夐崚鐗堟瀮鐎?
    
    # 閺傜懓绱?: 閸ユ儳鍎氬Ο鈩冩緲閸栧綊鍘?
    img_match = re.match(r'閸ュ墽澧朳::]\s*(.+)', desc)
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
    
    # 閺傜懓绱?: 鐠囶厺绠熼崠鍝勭厵
    area_map = {
        "瀹革缚绗傜憴?: (100, 100), "閸欏厖绗傜憴?: (1820, 100),
        "瀹革缚绗呯憴?: (100, 980), "閸欏厖绗呯憴?: (1820, 980),
        "鐏炲繐绠锋稉顓炪亷": (960, 540), "瀵偓婵褰嶉崡?: (50, 1030),
        "娴犺濮熼弽?: (960, 1050), "濡楀矂娼版稉顓炵妇": (960, 540),
        "閸忔娊妫撮幐澶愭尦": (1880, 10), "閺堚偓鐏忓繐瀵?: (1840, 10),
    }
    for area_name, (ax, ay) in area_map.items():
        if area_name in desc:
            return {"x": ax, "y": ay, "method": f"area:{area_name}"}
    
    return None

# ===== 閸斻劋缍旈幍褑顢?=====
async def execute_action(action, params, ws=None):
    """閹笛嗩攽閸楁洑閲滈幙宥嗗付閸斻劋缍?鏉╂柨娲栫紒鎾寸亯"""
    try:
        if action == "screenshot":
            b64 = screenshot_to_base64()
            return {"ok": True, "screenshot": b64, "action": action}
        
        elif action == "click":
            # 閺呴缚鍏樼€规矮缍呮导妯哄帥
            target_desc = params.get("target", "")
            pos = find_element(target_desc) if target_desc else None
            
            if pos:
                x, y = pos["x"], pos["y"]
            elif "x" in params and "y" in params:
                x, y = params["x"], params["y"]
            else:
                return {"ok": False, "error": "闂団偓鐟曚礁娼楅弽鍥ㄥ灗閸忓啰绀岄幓蹇氬牚", "action": action}
            
            import pyautogui
            pyautogui.moveTo(x, y, duration=0.3)  # 娴滆櫣琚崠鏍╅崝?
            time.sleep(0.1)
            pyautogui.click()
            result = {"ok": True, "action": action, "clicked": [x, y], "method": pos["method"] if pos else "coordinate"}
            # 閻愮懓鍤崥搴ゅ殰閸斻劍鍩呴崶楣冪崣鐠?
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
            # 閺€顖涘瘮娑擃厽鏋冩潏鎾冲弳
            import pyautogui, pyperclip
            try:
                pyperclip.copy(text)
                pyautogui.hotkey('ctrl', 'v')
            except ImportError:
                pyautogui.write(text, interval=0.05)  # 娴滆櫣琚崠鏍ㄥⅵ鐎涙鈧喎瀹?
            return {"ok": True, "action": action, "typed": text[:50]}
        
        elif action == "press_key":
            key = params.get("key", "")
            import pyautogui
            # 閺€顖涘瘮缂佸嫬鎮庨柨?
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
            seconds = min(params.get("seconds", 1), 30)  # 閺堚偓婢舵氨鐡?0缁?
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
            await asyncio.sleep(1.5)  # 缁涘绨查悽銊ユ儙閸?
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
            # 婵梹澧紒姗甽aywright閹笛嗩攽
            command = params.get("command", "")
            try:
                from playwright.async_api import async_playwright
                async with async_playwright() as p:
                    browser = await p.chromium.launch(headless=False)
                    page = await browser.new_page()
                    # 缁犫偓閸栨牜澧?鐠併€閸忓牊濯跺銉╊€?
                    await page.goto("https://www.google.com")
                    await page.fill('textarea[name="q"]', command)
                    await page.press('textarea[name="q"]', "Enter")
                    await page.wait_for_load_state("networkidle")
                    text = await page.inner_text("body")
                    await browser.close()
                    return {"ok": True, "action": action, "result": text[:2000]}
            except ImportError:
                return {"ok": False, "error": "Playwright閺堫亜鐣ㄧ憗?, "action": action}
        
        else:
            return {"ok": False, "error": f"閺堫亞鐓￠幙宥勭稊: {action}", "action": action}
    
    except Exception as e:
        return {"ok": False, "error": str(e), "action": action}

# ===== 娑撹鎯婇悳?=====
async def main():
    import websockets
    print(f"\n{'='*60}")
    print(f"  Friday AI 閺堫剙婀?Agent v2.0")
    print(f"  鐎广垺鍩涚粩鐤楧: {CLIENT_ID}")
    print(f"  閺堝秴濮熼崳?   {SERVER}")
    print(f"  鐟欏棜顫庨悶鍡毿? {'閴?閸氼垳鏁? if VISION_ENABLED else '閴?閸忔娊妫?}")
    print(f"{'='*60}\n")
    
    # 濡偓閺屻儰绶风挧?
    deps_ok = True
    try:
        import pyautogui
        print(f"  閴?pyautogui {pyautogui.__version__ if hasattr(pyautogui,'__version__') else 'OK'}")
    except ImportError:
        print(f"  閴?pyautogui 閺堫亜鐣ㄧ憗?)
        deps_ok = False
    try:
        import PIL
        print(f"  閴?Pillow OK")
    except ImportError:
        print(f"  閴?Pillow 閺堫亜鐣ㄧ憗?)
        deps_ok = False
    try:
        import pytesseract
        print(f"  閴?pytesseract OK (閺傚洤鐡х拠鍡楀焼)")
    except ImportError:
        print(f"  閳跨媴绗? pytesseract 閺堫亜鐣ㄧ憗?(閺傚洤鐡ч弻銉﹀闂勫秶楠?")
    try:
        import cv2
        print(f"  閴?OpenCV OK (閸ユ儳鍎氶崠褰掑帳)")
    except ImportError:
        print(f"  閳跨媴绗? OpenCV 閺堫亜鐣ㄧ憗?(閸ユ儳鍎氶崠褰掑帳闂勫秶楠?")
    
    if not deps_ok:
        print(f"\n  鐠囧嘲鐣ㄧ憗鍛繁婢跺彉绶风挧? pip install pyautogui pillow\n")
    
    while True:
        try:
            print(f"[鏉╃偞甯碷 濮濓絽婀潻鐐村复 {SERVER} ...")
            async with websockets.connect(SERVER, ping_interval=20, ping_timeout=10) as ws:
                # 濞夈劌鍞?
                await ws.send(json.dumps({
                    "type": "register",
                    "client_id": CLIENT_ID,
                    "hostname": CLIENT_ID,
                    "version": "2.0",
                    "capabilities": ["screenshot", "click", "type", "scroll", "ocr", "vision"]
                }))
                print(f"[濞夈劌鍞絔 閴?瀹稿弶鏁為崘灞藉煂閺堝秴濮熼崳?)
                
                # 韫囧啳鐑?
                async def heartbeat():
                    while True:
                        await asyncio.sleep(25)
                        try:
                            await ws.send(json.dumps({"type": "ping"}))
                        except:
                            break
                asyncio.create_task(heartbeat())
                
                # 閹稿洣鎶ゅ顏嗗箚
                async for msg in ws:
                    data = json.loads(msg)
                    msg_type = data.get("type", "")
                    
                    if msg_type == "execute":
                        action = data.get("action", "")
                        params = data.get("params", {})
                        task_id = data.get("task_id", "")
                        print(f"\n[閹笛嗩攽] {action} | {str(params)[:80]}")
                        
                        result = await execute_action(action, params, ws)
                        
                        # 鏉╂柨娲栫紒鎾寸亯
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
                        
                        status = "閴? if result.get("ok") else "閴?
                        print(f"[缂佹挻鐏塢 {status} {str(result)[:120]}")
                    
                    elif msg_type == "vision_request":
                        # 閺堝秴濮熼崳銊嚞濮瑰倹鍩呴崶鍓ф暏娴滃盯I鐟欏棜顫庨崚鍡樼€?
                        shot = screenshot_to_base64()
                        await ws.send(json.dumps({
                            "type": "vision_response",
                            "screenshot": shot,
                            "task_id": data.get("task_id", "")
                        }))
                    
                    elif msg_type == "pong":
                        pass  # 韫囧啳鐑﹂崫宥呯安
                    
                    elif msg_type == "registered":
                        print(f"[閺堝秴濮熼崳鈺?{data.get('message', 'OK')}")
                    
                    else:
                        print(f"[閺堫亞鐓″☉鍫熶紖] {msg_type}")
        
        except websockets.exceptions.ConnectionClosed:
            print(f"[閺傤厼绱慮 鏉╃偞甯撮崗鎶芥４,5缁夋帒鎮楅柌宥堢箾...")
        except Exception as e:
            print(f"[闁挎瑨顕 {str(e)[:200]}, 5缁夋帒鎮楅柌宥堢箾...")
        
        await asyncio.sleep(5)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print(f"\n[闁偓閸戠 Agent瀹告彃浠犲?)
    except Exception as e:
        print(f"\n[閼锋潙鎳￠柨娆掝嚖] {e}")'''
    return {
        "ok": True,
        "version": "2.0",
        "filename": "friday_agent.py",
        "script": script,
        "instructions": "pip install websockets pyautogui pillow psutil playwright pytesseract opencv-python pyperclip && playwright install chromium && python friday_agent.py",
        "capabilities": ["閹搭亜娴?鐟欏棜顫庨悶鍡毿?,"閺呴缚鍏橀崗鍐鐎规矮缍?OCR/閸ユ儳鍎?閸ф劖鐖?","21缁夊秴濮╂担?,"閸欏苯鍤?閸欐娊鏁?閹锋牗瀚?,"韫囶偅宓庨柨?,"缁愭褰涚粻锛勬倞","濞村繗顫嶉崳銊ㄥ殰閸斻劌瀵?,"缁崵绮洪崨鎴掓姢","閼奉亞绫傞柨?]
    }


# ===== 娴滃搫鑸癆gent(閸楀洨楠囬悧?=====
@router.post("/agent/human")
async def human_like_agent(req: dict, _=Depends(verify_token)):
    """娴滆櫣琚痪褏鏁搁懘鎴炴惙閹?- 閺呴缚鍏樼捄顖滄暠: 娴狅絿鐖滄禒璇插閻╁瓨甯撮幍褑顢? GUI娴犺濮熺憴鍡氼潕閹垮秵甯? 閼奉亜濮╅惇渚€鎸?""
    command = req.get("command","")
    target = req.get("target","server")
    max_cycles = req.get("max_cycles", 8)
    action_log = []
    
    # ===== 缁?濮? 娴犺濮熼弲楦垮厴閸掑棛琚?=====
    classify_prompt = f"""閸掋倖鏌囨潻娆庨嚋娴犺濮熺仦鐐扮艾閸濐亙绔寸猾?閸欘亜娲栨径宥勭娑擃亣鐦?
- "code": 娴狅絿鐖?閺傚洣娆?閺堝秴濮熼崳?閸涙垝鎶?閺佺増宓佹径鍕倞 (娑撳秹娓剁憰浣烘箙鐏炲繐绠?
- "gui": 閹垮秵甯跺宀勬桨鎼存梻鏁?GUI/濞村繗顫嶉崳?闂団偓鐟曚胶婀呯仦蹇撶
娴犺濮? {command}
閸掑棛琚?"""
    
    task_type = (await _call_ai(
        [{"role":"user","content":classify_prompt}],
        model=CHEAP_MODEL, max_tokens=10, temperature=0
    )).strip().lower()
    
    if "code" in task_type:
        # ===== 娴狅絿鐖?閺堝秴濮熼崳銊ゆ崲閸? 闂嗚埖鍩呴崶?閻╁瓨甯撮幍褑顢?=====
        code_prompt = f"""娴ｇ姵妲搁張宥呭閸ｃ劎顓搁悶鍜.鐎瑰本鍨氭潻娆庨嚋娴犺濮?閸ョ偛顦睯SON:
{{"steps":[{{"action":"run_command|read_file|write_file|search|done","params":{{}},"reason":"娑撹桨绮堟稊?}}],"summary":"閹崵绮?}}
閸欘垳鏁ら幙宥勭稊: run_command(閹笛嗩攽shell), read_file(鐠囩粯鏋冩禒?, write_file(閸愭瑦鏋冩禒?, search(閹兼粎鍌ㄩ崘鍛啇), done(鐎瑰本鍨?
娴犺濮? {command}
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
                        results.append(f"[read] {path}: 閺傚洣娆㈡稉宥呯摠閸?)
                elif a == "write_file":
                    path = p.get("path",""); txt = p.get("content","")
                    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
                    with open(path,"w") as f: f.write(txt)
                    results.append(f"[write] {path}: 瀹告彃鍟撻崗顨乴en(txt)}鐎涙顑?)
                elif a == "search":
                    import glob
                    pattern = p.get("pattern","*")
                    found = glob.glob(pattern, recursive=True)[:20]
                    results.append(f"[search] {pattern}: {found}")
                elif a == "done":
                    break
            except Exception as e:
                results.append(f"[{a}] 闁挎瑨顕? {str(e)[:200]}")
        
        # 閸嬫矮绔村▎鈩冩付缂佸牊鈧崵绮?(娓氬灝鐤佸Ο鈥崇€?
        summary = await _call_ai([
            {"role":"user","content":f"娴犺濮?{command}\n閹笛嗩攽缂佹挻鐏?\n"+'\n'.join(results)+"\n\n鐠囪渹绔撮崣銉ㄧ樈閹崵绮ㄧ€瑰本鍨氶幆鍛枌."}
        ], model=CHEAP_MODEL, max_tokens=100, temperature=0)
        
        token_estimate = len(classify_prompt) + len(plan) + len(summary) + 300
        return {
            "ok":True, "completed":True, "mode":"code", "cycles":len(action_log),
            "log":action_log, "results":results, "final_result":summary,
            "token_saved": True, "estimated_tokens": token_estimate,
            "vs_visual_mode": f"閻椒绨＄痪顩?max_cycles*1500 - token_estimate)//1000}k tokens"
        }
    
    # ===== GUI娴犺濮? 鐟欏棜顫庨幙宥嗗付(娴兼ê瀵查悧? =====
    system_prompt = """娴ｇ姵妲搁悽浣冨壋閹垮秵甯禔I.閻鍩岄幋顏勬禈閸氬骸娲栨径宀糞ON: {"observation":"閻鍩屾禍鍡曠矆娑?,"thought":"閹繆鈧?,"action":"閹垮秳缍旈崥?,"target":"閸忓啰绀岄幓蹇氬牚(閺傚洦婀?xxx/閸ф劖鐖?x,y)","params":{},"confidence":0.8}
閹垮秳缍? click|double_click|type_text|press_key|scroll|move|wait|open_app|close_window|switch_window|select_all|copy|paste|undo|save|run_command|done|fail
閸樼喎鍨? 閻⑩暟arget閹诲繗鍫崗鍐(婵?閺傚洦婀?閻ц缍?), 閹垮秳缍旈崥搴ㄧ崣鐠? 閸椻€茬秶閹广垻鐡ラ悾?"""
    
    cycle = 0
    last_screenshot = None
    last_action = None  # 闁灝鍘ら柌宥咁槻閹搭亜娴?
    
    while cycle < max_cycles:
        cycle += 1
        
        # 閸欘亜婀箛鍛邦洣閺冭埖鍩呴崶?(鏉╃偟鐢婚幍鎾崇摟/閹稿鏁崥搴濈瑝闂団偓鐟?
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
            return {"ok":False,"error":"閺冪姵纭堕懢宄板絿鐏炲繐绠烽幋顏勬禈","cycle":cycle}
        if not screenshot_b64:
            action_log.append({"cycle":cycle,"error":"閹搭亜娴樻径杈Е"}); break
        
        last_screenshot = screenshot_b64
        
        # 濡€崇€烽柅澶嬪: 閸?濮濄儳鏁HEAP_MODEL(姒涙顓籨eepseek-chat), 閸椻€茬秶娴滃棛鏁MART_MODEL
        use_model = pick_model(need_vision=True, step_count=cycle)
        user_prompt = f"娴犺濮? {command}\n缁楃憡cycle}/{max_cycles}濮?\n娑斿澧犻幙宥勭稊: {json.dumps(action_log[-3:],ensure_ascii=False)}\n閸掑棙鐎介幋顏勬禈,閻⑩暟arget閹诲繗鍫崗鍐."
        
        ai_response = await _call_ai([
            {"role":"system","content":system_prompt},
            {"role":"user","content":[{"type":"text","text":user_prompt},{"type":"image_url","image_url":{"url":f"data:image/png;base64,{screenshot_b64}","detail":"low"}}]}  # low detail = 閺囩繝绌剁€?
        ], model=use_model, max_tokens=300, temperature=0.3)
        
        decision = {}
        try:
            json_match = re.search(r'\{[^{}]*"action"[^{}]*\}', ai_response, re.DOTALL)
            if json_match: decision = json.loads(json_match.group())
        except: pass
        
        if not decision:
            action_log.append({"cycle":cycle,"error":"鐟欙絾鐎芥径杈Е"}); continue
        
        action = decision.get("action","screenshot")
        params = decision.get("params",{})
        last_action = action
        
        action_log.append({"cycle":cycle,"observation":decision.get("observation","")[:80],"thought":decision.get("thought","")[:80],"action":action,"target":decision.get("target","")})
        
        if action == "done":
            return {"ok":True,"completed":True,"mode":"gui","cycles":cycle,"log":action_log,"result":params.get("summary",""),"screenshot":last_screenshot,"model":CHEAP_MODEL,"estimated_tokens":cycle*500}
        if action == "fail":
            return {"ok":False,"error":params.get("reason","娴犺濮熸径杈Е"),"mode":"gui","cycles":cycle,"log":action_log}
        
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
    
    return {"ok":False,"error":"鏉堟儳鍩岄張鈧径褍鎯婇悳顖涱偧閺?,"mode":"gui","cycles":cycle,"log":action_log,"screenshot":last_screenshot,"estimated_tokens":cycle*500}

@router.post("/agent/quick")
async def quick_agent_action(req: dict, _=Depends(verify_token)):
    client_id = req.get("client_id","")
    action = req.get("action","")
    params = req.get("params",{})
    actions_help = {"screenshot":"閹搭亜褰囩仦蹇撶","open_url":"閹垫挸绱戠純鎴濇絻","click":"閸楁洖鍤?,"double_click":"閸欏苯鍤?,"right_click":"閸欐娊鏁?,"type_text":"鏉堟挸鍙嗛弬鍥х摟","press_key":"閹稿鏁?,"run_command":"鏉╂劘顢戦崨鎴掓姢","get_info":"缁崵绮烘穱鈩冧紖","open_app":"閹垫挸绱戞惔鏃傛暏","scroll":"濠婃俺鐤?,"move_mouse":"缁夎濮╂Η鐘崇垼","close_window":"閸忔娊妫寸粣妤€褰?,"switch_window":"閸掑洦宕茬粣妤€褰?,"select_all":"閸忋劑鈧?,"copy":"婢跺秴鍩?,"paste":"缁鍒?,"undo":"閹俱倝鏀?,"save":"娣囨繂鐡?,"browser_task":"濞村繗顫嶉崳銊ゆ崲閸?}
    if not client_id: return {"ok":False,"error":"鐠囬攱瀵氱€规瓭lient_id","available_clients":list(connected_remotes.keys()),"actions":actions_help}
    if client_id not in connected_remotes: return {"ok":False,"error":f"鐎广垺鍩涚粩?{client_id} 閺堫亣绻涢幒?,"available":list(connected_remotes.keys())}
    if action == "screenshot":
        ws = connected_remotes[client_id]
        await ws.send_json({"type":"execute","action":"screenshot","params":{}})
        for _ in range(20):
            try:
                data = await asyncio.wait_for(ws.receive_json(), timeout=3.0)
                if data.get("type") == "result" and data.get("screenshot"): return {"ok":True,"action":action,"screenshot":data.get("screenshot")}
            except: break
        return {"ok":False,"error":"閹搭亜娴樼搾鍛"}
    return await execute_remote(req, _)

@router.get("/agent/actions")
async def list_actions(_=Depends(verify_token)):
    return {"ok":True,"actions":{"screenshot":"閹搭亜褰囩仦蹇撶","open_url":"閹垫挸绱戠純鎴濇絻","click":"閸楁洖鍤?,"double_click":"閸欏苯鍤?,"right_click":"閸欐娊鏁?,"type_text":"鏉堟挸鍙嗛弬鍥х摟","press_key":"閹稿鏁?,"run_command":"鏉╂劘顢戠化鑽ょ埠閸涙垝鎶?,"get_info":"缁崵绮烘穱鈩冧紖","open_app":"閹垫挸绱戞惔鏃傛暏","scroll":"濠婃俺鐤?,"move_mouse":"缁夎濮╂Η鐘崇垼","drag":"閹锋牗瀚?,"wait":"缁涘绶?,"close_window":"閸忔娊妫寸粣妤€褰?,"switch_window":"閸掑洦宕茬粣妤€褰?,"select_all":"閸忋劑鈧?,"copy":"婢跺秴鍩?,"paste":"缁鍒?,"undo":"閹俱倝鏀?,"save":"娣囨繂鐡?,"browser_task":"AI濞村繗顫嶉崳銊ゆ崲閸?}}

# ===== 缂佺喍绔村ù蹇氼潔閸Ｋ媑ent =====
@router.post("/browser/unified")
async def unified_browser(req: dict, _=Depends(verify_token)):
    command = req.get("command","")
    target = req.get("target","server")
    if target == "server" or target in list(connected_remotes.keys()):
        if target != "server":
            if target not in connected_remotes: return {"ok":False,"error":f"鐎广垺鍩涚粩?{target} 閺堫亣绻涢幒?}
            ws = connected_remotes[target]
            await ws.send_json({"type":"execute","action":"browser_task","params":{"command":command}})
            return {"ok":True,"sent_to":target,"command":command}
        else:
            req_obj = BrowserAgentRequest(command=command, headless=True, max_steps=10)
            return await browser_agent(req_obj, _)
    return {"ok":False,"error":"閺堫亞鐓￠惄顔界垼","available_targets":["server"]+list(connected_remotes.keys())}



# ===== 8.7 濡€崇€风敮鍌氭簚API =====
@router.get("/models")
async def list_models(_=Depends(verify_token)):
    """閸掓鍤幍鈧張澶婂讲閻⑺婭濡€崇€烽崣濠佺幆閺?""
    available = {}
    for name, info in AVAILABLE_MODELS.items():
        key = DEEPSEEK_KEY if info["provider"] == "deepseek" else OPENAI_KEY
        available[name] = {**info, "available": bool(key)}
    return {
        "ok": True,
        "models": available,
        "current_cheap": CHEAP_MODEL,
        "current_smart": SMART_MODEL,
        "config_hint": "閻滎垰顣ㄩ崣姗€鍣? CHEAP_MODEL / SMART_MODEL / DEEPSEEK_API_KEY / OPENAI_API_KEY"
    }

@router.post("/models/test")
async def test_model(req: dict, _=Depends(verify_token)):
    """濞村鐦幐鍥х暰濡€崇€烽弰顖氭儊閸欘垳鏁?""
    model = req.get("model", CHEAP_MODEL)
    try:
        result = await _call_ai([{"role":"user","content":"閸ョ偛顦睴K"}], model=model, max_tokens=10, temperature=0)
        return {"ok": True, "model": model, "response": result[:50], "status": "閸欘垳鏁? if "OK" in result else "瀵倸鐖?}
    except Exception as e:
        return {"ok": False, "model": model, "error": str(e)[:200]}

# ===== 9. AI闁氨鐓￠幒銊┾偓?=====
@router.post("/notify")
async def send_notification(req: dict, _=Depends(verify_token)):
    """閹恒劑鈧線鈧氨鐓￠崚鐗堝閺堝绻涢幒銉ф畱鐎广垺鍩涚粩?""
    title = req.get("title","Friday AI")
    body = req.get("body","")
    url = req.get("url","/ai/")
    
    # 闁俺绻僕ebSocket楠炴寧鎸遍柅姘辩叀
    try:
        from routers.ws_router import manager
        await manager.broadcast(json.dumps({
            "type":"notification",
            "title":title,"body":body,"url":url,"time":datetime.now().isoformat()
        }))
        return {"ok":True,"message":"闁氨鐓″鎻掔畭閹?}
    except Exception as e:
        return {"ok":False,"error":str(e)}

@router.post("/agent/human/correct")
async def human_agent_correct(command: str = "", target: str = "server", _=Depends(verify_token)):
    """浜哄舰Agent鑷籂閿?""
    try:
        from agents.multi_model import ModelRouter
        resp = ModelRouter.smart_chat(messages=[{"role":"user","content":f"鎿嶄綔澶辫触: {command}銆傚垎鏋愬師鍥犵粰淇鎸囦护,鍙繑鍥炲懡浠ゃ€?}], mode="smart")
        corrected = resp.get("content","") if isinstance(resp,dict) else str(resp)
        import subprocess, shlex
        result = subprocess.run(corrected.strip().split(), capture_output=True, text=True, timeout=60)
        return {"ok":True,"corrected":corrected.strip(),"stdout":result.stdout[:2000]}
    except Exception as e:
        return {"ok":False,"error":str(e)}

@router.post("/agent/human/correct")
async def human_agent_correct(command: str = "", target: str = "server", _=Depends(verify_token)):
    """人形Agent自纠错 — 执行失败后自动诊断重试"""
    try:
        from agents.multi_model import ModelRouter
        resp = ModelRouter.smart_chat(messages=[{"role":"user","content":f"操作失败: {command}。分析原因给修正指令,只返回命令。"}], mode="smart")
        corrected = resp.get("content","") if isinstance(resp,dict) else str(resp)
        import subprocess
        result = subprocess.run(corrected.strip().split(), capture_output=True, text=True, timeout=60)
        return {"ok":True,"corrected":corrected.strip(),"stdout":result.stdout[:2000]}
    except Exception as e:
        return {"ok":False,"error":str(e)}
