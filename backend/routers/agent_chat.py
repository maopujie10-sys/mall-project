import asyncio, httpx, json, re, os
from datetime import datetime
from fastapi import APIRouter, Depends, Query, UploadFile, File
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from auth import verify_token
from state import state
from risk import handle_risk
from tools.registry import registry
from digital_lifeform import DigitalLifeform
from tools.vector_memory import VectorMemory
from agents.master_agent import MasterAgent
from agents.multi_model import ModelRouter
from config import CLAUDE_API_KEY, CLAUDE_MODEL, OPENAI_BASE_URL, DEEPSEEK_API_KEY, OPENAI_API_KEY
import sqlite3, hashlib, base64, uuid
from pathlib import Path
from fastapi import UploadFile, File, Form
import os
_cheap_model = os.getenv("CHEAP_MODEL", "deepseek-chat")

# ===== Conversation DB (SQLite) =====
CONV_DB = Path(__file__).parent.parent / "data" / "conversations.db"

def _get_conv_db():
    CONV_DB.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(CONV_DB))
    conn.execute("""CREATE TABLE IF NOT EXISTS conversations (
        id TEXT PRIMARY KEY, title TEXT, model TEXT, created_at TEXT, updated_at TEXT)""")
    conn.execute("""CREATE TABLE IF NOT EXISTS messages (
        id INTEGER PRIMARY KEY AUTOINCREMENT, conv_id TEXT, role TEXT, content TEXT,
        tool_name TEXT, tool_result TEXT, created_at TEXT,
        FOREIGN KEY(conv_id) REFERENCES conversations(id))""")
    conn.commit()
    return conn

router = APIRouter(prefix="/agent/chat", tags=["Agent Chat"])

SYSTEM_PROMPT = """You are Friday AI OS, a full-stack AI assistant with access to:
- Server management (CPU/memory/disk/process monitoring)
- Mall operations (products, orders, users, categories, KYC, logistics)
- DevOps (Docker, Nginx, domain rotation, backup/rollback)
- Data analysis (trends, predictions, recommendations, A/B testing)
- Security (scanning, alerts, self-healing, emergency response)
- Ecommerce AI (product selection, pricing, marketing, inventory)
- Code execution (sandbox Python/SQL, code deployment)
- Knowledge base (RAG search, document Q&A)

Rules:
1. Always use tools when needed - never guess data
2. Risk levels: L1=info L2=warning L3=danger L4=critical
3. For mall operations, always verify before executing
4. For server commands, confirm critical actions
5. Respond in user language, be concise and helpful
6. When using Function Calling, explain what you are doing"""

# ===== Agent Routing =====
AGENT_CAPABILITIES = {
    "server": ["server", "cpu", "memory", "disk", "process", "system", "uptime", "load"],
    "mall": ["product", "order", "user", "category", "mall", "shop", "price", "inventory", "kyc", "logistics", "refund", "wallet"],
    "devops": ["docker", "nginx", "deploy", "domain", "backup", "rollback", "restart", "ssl", "certificate"],
    "data": ["analyze", "trend", "predict", "recommend", "report", "statistics", "chart", "abtest", "weekly"],
    "security": ["scan", "vulnerability", "firewall", "alert", "threat", "attack", "audit", "security"],
    "ecommerce": ["product selection", "pricing strategy", "marketing", "competitor", "content factory", "seo", "listing", "inventory forecast", "sales forecast"],
    "code": ["code", "python", "sql", "script", "debug", "fix", "generate", "deploy"],
}

async def _route_to_agent(message, user="admin"):
    """Route message to appropriate agent based on keyword matching"""
    msg_lower = message.lower()
    matched = []
    for agent_name, keywords in AGENT_CAPABILITIES.items():
        score = sum(1 for kw in keywords if kw in msg_lower)
        if score > 0:
            matched.append((agent_name, score))
    matched.sort(key=lambda x: x[1], reverse=True)
    
    if not matched:
        return None
    
    top_agent = matched[0][0]
    print(f"[AgentRouter] Routing to {top_agent} (matched: {matched[:3]})")
    
    try:
        result = await MasterAgent.execute(top_agent, message, user)
        # Broadcast brain event
        DigitalLifeform.record_interaction("agent_call", {"agent": top_agent, "message": message[:100]})
        return {"agent": top_agent, "result": result}
    except Exception as e:
        print(f"[AgentRouter] {top_agent} failed: {e}")
        DigitalLifeform.record_interaction("agent_error", {"agent": top_agent, "error": str(e)})
        return {"agent": top_agent, "error": str(e)}

# ===== Direct Mall Query (Chat <-> Mall bidirectional) =====
async def _direct_mall_query(message):
    try:
        import httpx
        from config import MALL_BASE_URL
        msg_lower = message.lower()
        async with httpx.AsyncClient(timeout=10) as client:
            if any(kw in msg_lower for kw in ['product', 'item', 'goods']):
                resp = await client.get(f"{MALL_BASE_URL}/api/products", params={"search": message})
                return {"ok": True, "products": resp.json()[:5] if resp.status_code == 200 else []}
            elif any(kw in msg_lower for kw in ['order', 'purchase']):
                resp = await client.get(f"{MALL_BASE_URL}/api/orders/stats")
                return {"ok": True, "orders": resp.json() if resp.status_code == 200 else {}}
            elif any(kw in msg_lower for kw in ['user', 'customer']):
                resp = await client.get(f"{MALL_BASE_URL}/api/users/stats")
                return {"ok": True, "users": resp.json() if resp.status_code == 200 else {}}
            return None
    except:
        return None

class ChatRequest(BaseModel):
    message: str
    history: list[dict] = []  # _________ [{role,content}]
    model: str = ''            # ________EUR_

class ConfirmRequest(BaseModel):
    taskId: str
    approved: bool

class HandoverRequest(BaseModel):
    reason: str = ''

OLLAMA_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "qwen2.5:7b")
DEEPSEEK_KEY = os.getenv("DEEPSEEK_API_KEY", '')
OPENAI_KEY = os.getenv("OPENAI_API_KEY", '')
_API_URL = OPENAI_BASE_URL or "https://api.openai.com/v1"

SYSTEM_PROMPT = ''"_____Friday AI OS -- _______________________________________________EUR________________________________________

_________:
- ______________CPU/____________________
- _________:_____________________EUR___
- ___________Docker/Nginx/___________________
- _________________________/________EUR__________

_________:
1. ________________________________
2. _________:L1=_________ L2=___________L3=________L4=_____
3. _____________________
4. ___________________________
5. __________________,________________

__________D___________Neural Network),____________________________________''"

# ===== _____EUR____(OpenAI Function Calling_____ =====
def _build_tools():
    ''"_________schema''"
    tools_list = registry.list_all()[:50]
    return [{
        "type": "function",
        "function": {
            "name": t.name,
            "description": f"{t.display_name}: {t.description} [_____{t.risk_level}]",
            "parameters": {
                "type": "object",
                "properties": {
                    "message": {"type": "string", "description": "_________"}
                },
                "required": ["message"]
            }
        }
    } for t in tools_list]

# ===== __EUR_EUR_____ =====
@with_retry(max_retries=2, timeout=45)
@circuit_breaker('ai_call', failure_threshold=10)
async def call_ai_with_tools(messages, model=''):
    ''"_____I__EUR_EUR__EUR________unction Calling''"
    tools = _build_tools()
    
    # _____eepSeek(_____penAI_____
    if DEEPSEEK_KEY:
        try:
            async with httpx.AsyncClient(timeout=90) as c:
                r = await c.post(
                    "https://api.deepseek.com/v1/chat/completions",
                    headers={"Authorization": f"Bearer {DEEPSEEK_KEY}", "Content-Type": "application/json"},
                    json={"model": "deepseek-chat", "messages": messages, "tools": tools, "tool_choice": "auto", "temperature": 0.7}
                )
                if r.status_code == 200:
                    return r.json()
        except Exception:
            pass
    
    # OpenAI_____PI (302AI__
    if OPENAI_KEY:
        try:
            async with httpx.AsyncClient(timeout=90) as c:
                r = await c.post(
                    f"{_API_URL}/chat/completions",
                    headers={"Authorization": f"Bearer {OPENAI_KEY}", "Content-Type": "application/json"},
                    json={"model": "gpt-4o-mini", "messages": messages, "tools": tools, "tool_choice": "auto", "temperature": 0.7}
                )
                if r.status_code == 200:
                    return r.json()
        except Exception:
            pass
    
    # ______: ______-> ______________
    tl = "\n".join([f"- {t['function']['name']}: {t['function']['description']}" for t in tools])
    fallback_msgs = [{"role": "system", "content": SYSTEM_PROMPT + "\n\n________EUR_\n" + tl}]
    fallback_msgs.extend(messages)
    fallback_msgs.append({"role": "user", "content": '____________,_____SON: {"tool":"______","reason":"____"}'})
    
    if DEEPSEEK_KEY:
        try:
            async with httpx.AsyncClient(timeout=60) as c:
                r = await c.post(
                    "https://api.deepseek.com/v1/chat/completions",
                    headers={"Authorization": f"Bearer {DEEPSEEK_KEY}"},
                    json={"model": "deepseek-chat", "messages": fallback_msgs, "temperature": 0.5}
                )
                if r.status_code == 200:
                    return {"fallback": True, **r.json()}
        except Exception:
            pass
    
    return {"fallback": True, "choices": [{"message": {"content": "AI_____,___"}}]}

# ===== _________=====
async def execute_tool(name: str, params: dict) -> dict:
    ''"___________________''"
    try:
        if name == "system_status":
            import psutil
            return {"success": True, "data": {"cpu": f"{psutil.cpu_percent()}%", "mem": f"{psutil.virtual_memory().percent}%", "disk": f"{psutil.disk_usage('/').percent}%"}}
        if name == "run_inspection":
            from routers.inspector import run_inspection
            result = await run_inspection()
            return {"success": True, "data": result}
        if name == "mall_orders":
            from config import MALL_BASE_URL
            async with httpx.AsyncClient(timeout=10) as c:
                r = await c.get(f"{MALL_BASE_URL}/api/orders", params={"page":1,"size":5})
                return {"success": True, "data": r.json() if r.status_code==200 else {"error":"API______"}}
        if name == "docker_status":
            import subprocess
            r = subprocess.run(["docker","ps","--format","{{.Names}} {{.Status}}"], capture_output=True, text=True, timeout=10)
            return {"success": True, "data": {"containers": r.stdout.strip().split("\n")[:10]}}
        if name == "server_cleanup":
            import subprocess, gc
            gc.collect()
            subprocess.run(["docker","system","prune","-f"], capture_output=True, timeout=30)
            return {"success": True, "data": {"message": "__________EUR_Docker__________"}}
        
        # _____________
        tool = registry.get(name)
        if tool:
            result = await tool.execute(params)
            return {"success": True, "data": result if result else {}}
        return {"success": False, "error": f"_____{name} ______"}
    except Exception as e:
        return {"success": False, "error": str(e)[:200]}

# ===== RAG_______=====
async def _get_context(message: str) -> str:
    ''"_____________ ''''"
    try:
        ctx = await VectorMemory.search(message, top_k=3)
        if ctx:
            return "_________:\n" + "\n".join([c.get("text",'')[:200] for c in ctx])
    except Exception:
        pass
    return ''

# ===== ___hat_____(Function Calling) =====
@router.post("/chat")
async def agent_chat(req: ChatRequest, _=Depends(verify_token)):
    ''"AI____ - _____unction Calling''"
    rag_ctx = await _get_context(req.message)
    system_content = SYSTEM_PROMPT
    if rag_ctx:
        system_content += "\n\n" + rag_ctx
    
    messages = [{"role": "system", "content": system_content}]
    if req.history:
        messages.extend(req.history[-20:])  # _____0__EUR____
    messages.append({"role": "user", "content": req.message})
    
    result = await call_ai_with_tools(messages, req.model)
    
    # _____unction Calling_____
    if not result.get("fallback"):
        choice = result.get("choices", [{}])[0]
        msg = choice.get("message", {})
        tool_calls = msg.get("tool_calls", [])
        
        if tool_calls:
            # AI___________
            tc = tool_calls[0]
            func = tc.get("function", {})
            tool_name = func.get("name", '')
            tool_args = json.loads(func.get("arguments", "{}"))
            
            risk = "L1"
            td = registry.get(tool_name)
            if td:
                risk = td.risk_level
                await handle_risk(risk, td.display_name, req.message[:100])
            
            if risk == "L4":
                return {"response": f"_EUR_L4________________ {tool_name}", "tool": tool_name, "risk": "L4"}
            
            exec_result = await execute_tool(tool_name, tool_args)
            
            # ______________I__________________
            messages.append({"role": "assistant", "content": None, "tool_calls": tool_calls})
            messages.append({"role": "tool", "tool_call_id": tc.get("id",''), "content": json.dumps(exec_result, ensure_ascii=False)})
            
            final = await call_ai_with_tools(messages, req.model)
            ai_text = final.get("choices",[{}])[0].get("message",{}).get("content", "_________")
            
            # _____EUR____
            try:
                DigitalLifeform.remember_conversation(req.message, ai_text[:300])
                asyncio.ensure_future(VectorMemory.remember(ai_text[:300], {"type":"ai","source":"chat","tool":tool_name}))
            except Exception:
                pass
            
            return {
                "response": ai_text,
                "tool": tool_name,
                "tool_result": exec_result,
                "risk": risk,
                "mode": state.mode
            }
        else:
            # AI______________
            ai_text = msg.get("content", '')
            try:
                DigitalLifeform.remember_conversation(req.message, ai_text[:300])
            except Exception:
                pass
            return {"response": ai_text, "tool": None, "risk": "L1", "mode": state.mode}
    
    # Fallback: ______
    ai_text = result.get("choices",[{}])[0].get("message",{}).get("content",'')
    m = re.search(r'\{[^}]+\}', ai_text.strip())
    tool_name = None
    if m:
        try:
            p = json.loads(m.group())
            tool_name = p.get("tool")
        except Exception:
            pass
    
    if tool_name:
        exec_result = await execute_tool(tool_name, {"message": req.message})
        ai_text = f"____ {tool_name}: " + json.dumps(exec_result.get("data",{}), ensure_ascii=False)[:500]
    
    return {"response": ai_text or "________________...", "tool": tool_name, "risk": "L1", "mode": state.mode}

# ===== _____EUR____=====
# ===== ___________=====
_chat_histories = {}  # user_id -> [messages]

@router.post("/chat/history")
async def save_chat_history(req: dict, _=Depends(verify_token)):
    ''"_____EUR________''"
    uid = req.get("user_id", "default")
    _chat_histories[uid] = req.get("messages", [])[-100:]
    state._data[f"chat_history_{uid}"] = _chat_histories[uid]
    state._save()
    return {"ok": True, "count": len(_chat_histories[uid])}

@router.get("/chat/history")
async def load_chat_history(user_id: str = Query("default"), _=Depends(verify_token)):
    ''"_____EUR________''"
    return {"messages": state._data.get(f"chat_history_{user_id}", [])[-50:]}

@router.delete("/chat/history")
async def clear_chat_history(user_id: str = Query("default"), _=Depends(verify_token)):
    ''"_____EUR________''"
    state._data.pop(f"chat_history_{user_id}", None)
    state._save()
    return {"ok": True}

# ===== _________ =====
@router.get("/tools")
async def list_tools(_=Depends(verify_token)):
    ts = registry.list_all()
    return {"tools": [{"name":t.name,"display_name":t.display_name,"description":t.description,"risk_level":t.risk_level} for t in ts], "count": len(ts)}

@router.get("/tasks")
async def list_tasks(_=Depends(verify_token)):
    return {"tasks": state.tasks[-50:], "pending": len(state.pending_approvals)}

@router.post("/confirm")
async def confirm_task(req: ConfirmRequest, _=Depends(verify_token)):
    for a in state.pending_approvals:
        if a.get("id") == req.taskId:
            a["status"] = "approved" if req.approved else "rejected"
            state.approval_history.append({**a, "result": a["status"]})
            state.pending_approvals.remove(a)
            return {"ok": True, "status": a["status"]}
    return {"ok": False, "error": "_____________"}




CONV_DB = Path(__file__).parent.parent / "data" / "conversations.db"
def _cdb():
    CONV_DB.parent.mkdir(parents=True,exist_ok=True)
    c=sqlite3.connect(str(CONV_DB))
    c.execute("CREATE TABLE IF NOT EXISTS convs(id TEXT PRIMARY KEY,title TEXT,owner TEXT DEFAULT 'admin',created TEXT,updated TEXT)")
    c.execute("CREATE TABLE IF NOT EXISTS msgs(id INTEGER PRIMARY KEY AUTOINCREMENT,cid TEXT,role TEXT,content TEXT,owner TEXT DEFAULT 'admin',created TEXT)")
    c.commit();return c

@router.post("/chat/stream")
async def chat_stream(req: ChatRequest, _=Depends(verify_token)):
    ''"SSE___oken____C____''"
    key=OPENAI_API_KEY or DEEPSEEK_API_KEY; url=OPENAI_BASE_URL or "https://api.openai.com/v1"
    m=req.model or _cheap_model
    ctx=await _get_context(req.message);sc=SYSTEM_PROMPT
    if ctx:sc+="\n\n"+ctx
    
    # RAG________________
    try:
        from tools.rag_engine import RAGEngine
        rag_ctx = RAGEngine.build_context(req.message, top_k=3, max_tokens=1500)
        if rag_ctx:
            sc += "\n\n__________________n" + rag_ctx
    except: pass
    msgs=[{"role":"system","content":sc}]
    if req.history:msgs.extend(req.history[-20:])
    msgs.append({"role":"user","content":req.message})
    async def gen():
        f=''
        try:
            async with httpx.AsyncClient(timeout=120) as cl:
                async with cl.stream("POST",f"{url}/chat/completions",
                    headers={"Authorization":f"Bearer {key}","Content-Type":"application/json"},
                    json={"model":m,"messages":msgs,"stream":True,"temperature":0.7}) as r:
                    async for ln in r.aiter_lines():
                        if ln.startswith("data: "):
                            d=ln[6:]
                            if d=="[DONE]":break
                            try:
                                j=json.loads(d)
                                t=j.get("choices",[{}])[0].get("delta",{}).get("content",'')
                                if t:f+=t;yield f"data: {json.dumps({'t':t},ensure_ascii=False)}\n\n"
                            except:pass
                    yield f"data: {json.dumps({'done':True,'full':f},ensure_ascii=False)}\n\n"
        except Exception as e:
            yield f"data: {json.dumps({'error':str(e)},ensure_ascii=False)}\n\n"
    return StreamingResponse(gen(),media_type="text/event-stream",headers={"Cache-Control":"no-cache","X-Accel-Buffering":"no"})

@router.post("/chat/vision")
async def cv(img:str=Form(...),q:str=Form("_________"),_=Depends(verify_token)):
    k=OPENAI_API_KEY;u=OPENAI_BASE_URL or "https://api.openai.com/v1"
    if not k:return{"ok":False,"error":"______PENAI_API_KEY"}
    try:
        async with httpx.AsyncClient(timeout=60)as c:
            r=await c.post(f"{u}/chat/completions",headers={"Authorization":f"Bearer {k}","Content-Type":"application/json"},
                json={"model":"gpt-4o-mini" if OPENAI_API_KEY else "gpt-4o","messages":[{"role":"user","content":[{"type":"text","text":q},{"type":"image_url","image_url":{"url":f"data:image/jpeg;base64,{img}"}}]}]})
            if r.status_code==200:
                d=r.json();return{"ok":True,"reply":d.get("choices",[{}])[0].get("message",{}).get("content","(no content)")}
            return{"ok":False,"error":f"API:{r.status_code}"}
    except Exception as e:return{"ok":False,"error":str(e)}

PROMPTS={}
for n,p in[("default","{input}")]:
    PROMPTS[n]={"prompt":p,"icon":"___"}

@router.get("/prompts")
async def lp(_=Depends(verify_token)):
    return{"ok":True,"templates":[{"name":k,"icon":v["icon"],"preview":v["prompt"][:50]} for k,v in PROMPTS.items()]}

@router.get("/conversations")
async def lc(_=Depends(verify_token)):
    c=_cdb();r=c.execute("SELECT id,title,created,updated FROM convs ORDER BY updated DESC LIMIT 30").fetchall();c.close()
    return{"ok":True,"conversations":[{"id":x[0],"title":x[1],"created_at":x[2],"updated_at":x[3]} for x in r]}

@router.post("/conversations")
async def cc(req:dict,_=Depends(verify_token)):
    cid=uuid.uuid4().hex[:12];c=_cdb()
    c.execute("INSERT INTO convs VALUES(?,?,datetime('now'),datetime('now'))",(cid,req.get("title","(untitled)")))
    c.commit();c.close();return{"ok":True,"id":cid}

@router.get("/conversations/{cid}")
async def gc(cid:str,_=Depends(verify_token)):
    c=_cdb();r=c.execute("SELECT role,content,created FROM msgs WHERE cid=_ ORDER BY id LIMIT 50",(cid,)).fetchall();c.close()
    return{"ok":True,"messages":[{"role":x[0],"content":x[1],"time":x[2]} for x in r]}

@router.delete("/conversations/{cid}")
async def dc(cid:str,_=Depends(verify_token)):
    c=_cdb();c.execute("DELETE FROM msgs WHERE cid=",(cid,));c.execute("DELETE FROM convs WHERE id=",(cid,));c.commit();c.close()
    return {"ok": True}
# ===== RAG_________ =====
@router.post("/rag/upload")
async def rag_upload_file(file: UploadFile = File(...), _=Depends(verify_token)):
    raw=await file.read();ext=(file.filename or '').rsplit(".",1)[-1].lower()if"."in(file.filename or '')else''
    text=''
    if ext in("txt","md","csv","json","py","js","html","yml","yaml"):
        try:text=raw.decode("utf-8")
        except:text=raw.decode("latin-1","ignore")
    elif ext=="pdf":
        try:
            import subprocess,tempfile
            with tempfile.NamedTemporaryFile(suffix=".pdf",delete=False)as f:f.write(raw);tp=f.name
            r=subprocess.run(["pdftotext","-layout",tp,"-"],capture_output=True,text=True,timeout=30)
            text=r.stdout or"PDF_________";os.unlink(tp)
        except:text=f"[PDF:{file.filename}]___poppler-utils"
    else:text=raw.decode("utf-8","ignore")[:5000]
    chunks=[text[i:i+800]for i in range(0,min(len(text),16000),800)]if text.strip()else[]
    for i,ch in enumerate(chunks):
        try:await VectorMemory.remember(ch,{"type":"doc","source":file.filename,"chunk":i})
        except:pass
    return{"ok":True,"file":file.filename,"chars":len(text),"chunks":len(chunks)}

# ===== __EUR_EUR_EUR____=====
@router.post("/chat/compare")
async def chat_compare(req: ChatRequest, _=Depends(verify_token)):
    ''"_______EUR______________EUR_EUR______EUR_''"
    models=[("gpt-3.5-turbo","GPT-3.5"),("deepseek-chat","DeepSeek")]
    results=[]
    for mid,mname in models:
        try:
            key=OPENAI_API_KEY;url=OPENAI_BASE_URL or "https://api.openai.com/v1"
            if mid.startswith("deepseek"):key=DEEPSEEK_API_KEY or key
            async with httpx.AsyncClient(timeout=60)as c:
                r=await c.post(f"{url}/chat/completions",headers={"Authorization":f"Bearer {key}","Content-Type":"application/json"},
                    json={"model":mid,"messages":[{"role":"user","content":req.message}],"temperature":0.7,"max_tokens":500})
                if r.status_code==200:
                    d=r.json();results.append({"model":mname,"reply":d.get("choices",[{}])[0].get("message",{}).get("content",'')})
                else:results.append({"model":mname,"error":f"HTTP {r.status_code}"})
        except Exception as e:results.append({"model":mname,"error":str(e)})
    return{"ok":True,"results":results}

# ===== _________AI =====
@router.get("/dashboard/ask")
async def dashboard_ask(q: str = Query(...), _=Depends(verify_token)):
    ''"______________________''"
    try:
        import psutil,os
        cpu=psutil.cpu_percent();mem=psutil.virtual_memory();disk=psutil.disk_usage("/")
        ctx=f"___________ CPU {cpu}%, _____{mem.percent}%, _____{disk.percent}%"
        key=OPENAI_API_KEY or DEEPSEEK_API_KEY;url=OPENAI_BASE_URL or "https://api.openai.com/v1"
        async with httpx.AsyncClient(timeout=30)as c:
            r=await c.post(f"{url}/chat/completions",headers={"Authorization":f"Bearer {key}","Content-Type":"application/json"},
                json={"model":"gpt-3.5-turbo","messages":[
                    {"role":"system","content":f"______________________________{ctx}.__________________"},
                    {"role":"user","content":q}
                ],"temperature":0.5,"max_tokens":400})
            if r.status_code==200:
                d=r.json();return{"ok":True,"answer":d.get("choices",[{}])[0].get("message",{}).get("content",'')}
        return{"ok":False,"error":f"API:{r.status_code}"}
    except Exception as e:return{"ok":False,"error":str(e)}


# ===== ______________dmin) =====
@router.get("/admin/tenants")
async def list_tenants(_=Depends(verify_token)):
    ''"___________________________''"
    c = _cdb()
    rows = c.execute("SELECT owner,COUNT(*) as convs FROM convs GROUP BY owner").fetchall()
    msgs = c.execute("SELECT owner,COUNT(*) as msgs FROM msgs GROUP BY owner").fetchall()
    c.close()
    u = _udb()
    tokens = u.execute("SELECT owner,SUM(tokens_in+ tokens_out) as tokens,SUM(cost) as cost FROM usage GROUP BY owner").fetchall()
    u.close()
    tenants = []
    owners = set()
    for r in rows: owners.add(r[0])
    for r in msgs: owners.add(r[0])
    for r in tokens: owners.add(r[0])
    for o in owners:
        conv_count = next((r[1] for r in rows if r[0]==o),0)
        msg_count = next((r[1] for r in msgs if r[0]==o),0)
        tok_count = next((r[1] for r in tokens if r[0]==o),0)
        cost = next((r[2] for r in tokens if r[0]==o),0)
        tenants.append({"owner":o,"conversations":conv_count,"messages":msg_count,"tokens":tok_count or 0,"cost":round(cost or 0,4)})
    return {"ok":True,"tenants":tenants}


# ===== ______________=====
@router.post("/conversations/{cid}/summarize")
async def summarize_conversation(cid: str, _=Depends(verify_token)):
    ''"__________EUR_____+ _________''"
    msgs = load_history(cid, 100)
    if len(msgs) < 10:
        return {"ok": True, "original_count": len(msgs), "summary": "_________,_________"}
    
    # _____EUR________
    conv_text = "\n".join([f"{m['role']}: {m['content'][:200]}" for m in msgs])
    
    try:
        from tools.ai_client import call_ai
        summary = await call_ai([
            {"role": "user", "content": f"_____-5______________EUR_____________EUR________:\n{conv_text[:4000]}"}
        ], max_tokens=200, temperature=0.3)
        
        # _______________________
        c = _cdb()
        c.execute("UPDATE convs SET title=_ WHERE id=", (summary[:100], cid))
        c.commit(); c.close()
        
        return {"ok": True, "original_count": len(msgs), "summary": summary, "compressed": True}
    except Exception as e:
        return {"ok": False, "error": str(e)}

@router.get("/conversations/{cid}/context")
async def get_conversation_context(cid: str, query: str = '', _=Depends(verify_token)):
    ''"_____EUR__________-- _________ __________+ RAG + ____''"
    msgs = load_history(cid, 30)
    result = {"messages": msgs, "count": len(msgs)}
    
    # ___________________________
    if query:
        try:
            from tools.rag_engine import RAGEngine
            rag_ctx = RAGEngine.build_context(query, top_k=2, max_tokens=1000)
            if rag_ctx:
                result["rag_context"] = rag_ctx
        except: pass
    
    return {"ok": True, **result}


def _udb():
    import sqlite3
    from pathlib import Path
    db = Path(__file__).parent.parent / "data" / "usage.db"
    db.parent.mkdir(parents=True,exist_ok=True)
    return sqlite3.connect(str(db))

@router.post("/chat/vision")
async def chat_vision(file: UploadFile = File(...), question: str = "______", _=Depends(verify_token)):
    ''"_______''"
    try:
        import base64
        content = await file.read()
        b64 = base64.b64encode(content).decode()
        mime = file.content_type or "image/jpeg"
        from agents.multi_model import ModelRouter
        resp = ModelRouter.smart_chat(messages=[{"role":"user","content":[
            {"type":"text","text":question},
            {"type":"image_url","image_url":{"url":f"data:{mime};base64,{b64}"}}
        ]}], mode="smart")
        return {"ok":True,"analysis":resp.get("content",'') if isinstance(resp,dict) else str(resp)}
    except Exception as e: return {"ok":False,"error":str(e)}

@router.post("/chat/file")
async def chat_file_analysis(file: UploadFile = File(...), question: str = "______", _=Depends(verify_token)):
    ''"____(__/PDF/___)''"
    try:
        content = await file.read()
        text = ''
        if file.content_type and "video" in file.content_type:
            text = f"[____: {file.filename}, {len(content)} bytes, __: {file.content_type}]"
        elif file.content_type and "pdf" in file.content_type:
            try:
                import io, PyPDF2
                reader = PyPDF2.PdfReader(io.BytesIO(content))
                text = ''.join([p.extract_text() or '' for p in reader.pages[:5]])
            except: text = content.decode("utf-8","ignore")[:3000]
        else:
            text = content.decode("utf-8","ignore")[:5000]
        from agents.multi_model import ModelRouter
        resp = ModelRouter.smart_chat(messages=[{"role":"user","content":f"__: {file.filename}\n__: {text}\n\n__: {question}"}], mode="smart")
        return {"ok":True,"analysis":resp.get("content",'') if isinstance(resp,dict) else str(resp),"text_length":len(text)}
    except Exception as e: return {"ok":False,"error":str(e)}

@router.post("/handover")
async def agent_handover(req: HandoverRequest, _=Depends(verify_token)):
    state.mode = "human_control"
    return {"ok": True, "mode": "human_control", "reason": req.reason}
