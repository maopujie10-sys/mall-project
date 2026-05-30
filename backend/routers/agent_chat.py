"""Agent Chat API v3 -- 閸樼喓鏁揊unction Calling + 鐎电鐦界拋鏉跨箓閹镐椒绠欓崠?""
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
from config import CLAUDE_API_KEY, CLAUDE_MODEL, OPENAI_BASE_URL, DEEPSEEK_API_KEY, OPENAI_API_KEY
import sqlite3, hashlib, base64, uuid
from pathlib import Path
from fastapi import UploadFile, File, Form
import os
_cheap_model = os.getenv("CHEAP_MODEL", "deepseek-chat")

# ===== 鐎电鐦芥导姘崇樈缁狅紕鎮?(SQLite) =====
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
    conn.commit(); return conn

def save_message(conv_id: str, role: str, content: str, tool_name: str = None, tool_result: str = None):
    conn = _get_conv_db()
    conn.execute("INSERT INTO messages (conv_id,role,content,tool_name,tool_result,created_at) VALUES (?,?,?,?,?,datetime('now'))",
                 (conv_id, role, content, tool_name, tool_result))
    conn.execute("UPDATE conversations SET updated_at=datetime('now') WHERE id=?", (conv_id,))
    conn.commit(); conn.close()

def load_history(conv_id: str, limit: int = 50) -> list:
    conn = _get_conv_db()
    rows = conn.execute("SELECT role,content FROM messages WHERE conv_id=? ORDER BY id ASC LIMIT ?", (conv_id, limit)).fetchall()
    conn.close()
    return [{"role": r[0], "content": r[1]} for r in rows]

def list_conversations(limit: int = 30) -> list:
    conn = _get_conv_db()
    rows = conn.execute("SELECT id,title,model,created_at,updated_at FROM conversations ORDER BY updated_at DESC LIMIT ?", (limit,)).fetchall()
    conn.close()
    return [{"id": r[0], "title": r[1], "model": r[2], "created_at": r[3], "updated_at": r[4]} for r in rows]

def create_conversation(title: str = "閺傛澘顕拠?, model: str = "") -> str:
    cid = uuid.uuid4().hex[:12]
    conn = _get_conv_db()
    conn.execute("INSERT INTO conversations (id,title,model,created_at,updated_at) VALUES (?,?,?,datetime('now'),datetime('now'))", (cid, title, model))
    conn.commit(); conn.close()
    return cid

# ===== 濞翠礁绱SE瀹搞儱鍙块崙鑺ユ殶 =====
async def stream_ai_response(messages: list, model: str = ""):
    """闁仭oken濞翠礁绱℃潻鏂挎礀AI閸濆秴绨?""
    api_key = OPENAI_API_KEY or DEEPSEEK_API_KEY
    base_url = OPENAI_BASE_URL or "https://api.openai.com/v1"
    model_name = model or "gpt-3.5-turbo"
    
    async with httpx.AsyncClient(timeout=120.0) as client:
        async with client.stream("POST", f"{base_url}/chat/completions",
            headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
            json={"model": model_name, "messages": messages, "stream": True, "temperature": 0.7}
        ) as response:
            full_text = ""
            async for line in response.aiter_lines():
                if line.startswith("data: "):
                    data = line[6:]
                    if data == "[DONE]":
                        break
                    try:
                        chunk = json.loads(data)
                        delta = chunk.get("choices", [{}])[0].get("delta", {})
                        token = delta.get("content", "")
                        if token:
                            full_text += token
                            yield f"data: {json.dumps({'token': token, 'full': full_text})}\n\n"
                    except:
                        pass
            yield f"data: {json.dumps({'done': True, 'full': full_text})}\n\n"

# ===== 閸ュ墽澧栭悶鍡毿?=====
async def analyze_image(image_base64: str, question: str = "鐠囬攱寮挎潻鎷岀箹瀵姴娴橀悧?) -> str:
    """娴ｈ法鏁ょ憴鍡氼潕濡€崇€烽崚鍡樼€介崶鍓у"""
    api_key = OPENAI_API_KEY
    if not api_key:
        return "閸ュ墽澧栭崚鍡樼€介棁鈧憰渚€鍘ょ純鐢嘝ENAI_API_KEY"
    base_url = OPENAI_BASE_URL or "https://api.openai.com/v1"
    async with httpx.AsyncClient(timeout=60.0) as client:
        resp = await client.post(f"{base_url}/chat/completions",
            headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
            json={"model": "gpt-4o-mini", "messages": [{"role": "user", "content": [
                {"type": "text", "text": question},
                {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image_base64}"}}
            ]}]})
        if resp.status_code == 200:
            data = resp.json()
            return data.get("choices", [{}])[0].get("message", {}).get("content", "閺冪姵纭堕崚鍡樼€?)
        return f"閸ュ墽澧栭崚鍡樼€芥径杈Е: {resp.status_code}"

router = APIRouter(prefix="/agent", tags=["Agent"])

class ChatRequest(BaseModel):
    message: str
    history: list[dict] = []  # 鐎电鐦介崢鍡楀蕉 [{role,content}]
    model: str = ""            # 閹稿洤鐣惧Ο鈥崇€?

class ConfirmRequest(BaseModel):
    taskId: str
    approved: bool

class HandoverRequest(BaseModel):
    reason: str = ""

OLLAMA_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "qwen2.5:7b")
DEEPSEEK_KEY = os.getenv("DEEPSEEK_API_KEY", "")
OPENAI_KEY = os.getenv("OPENAI_API_KEY", "")
_API_URL = OPENAI_BASE_URL or "https://api.openai.com/v1"

SYSTEM_PROMPT = """娴ｇ姵妲?Friday AI OS -- 閺佹澘鐡ч悽鐔锋嚒娴ｆ挻鐗宠箛?娴ｇ姵瀚㈤張澶岄兇缂佺喐鍔呴惌銉ㄥ厴閸?閼宠姤鐓￠惇瀣箛閸斺€虫珤閻樿埖鈧降鈧胶顓搁悶鍡楁櫌閸╁氦绻嶉拃銉ｂ偓浣瑰⒔鐞涘矁绻嶇紒瀛樻惙娴?

閺嶇绺鹃懗钘夊:
- 鐎圭偞妞傜化鑽ょ埠閻╂垶甯?CPU/閸愬懎鐡?绾句胶娲?缂冩垹绮?鏉╂稓鈻?
- 閸熷棗鐓勭粻锛勬倞:鐠併垹宕?閸熷棗鎼?閻劍鍩?閻椻晜绁?閽€銉╂敘
- 閼奉亜濮╅崠鏍箥缂?Docker/Nginx/閸╃喎鎮曟潪顔尖偓?婢跺洣鍞ら崶鐐寸泊
- 閺佺増宓侀柌鍥肠娑撳骸鍨庨弸?閸熷棗鎼ч柌鍥肠/缁旂偛鎼ч崚鍡樼€?鐡掑濞嶆０鍕ゴ

鐞涘奔璐熼崙鍡楀灟:
1. 閻炲棜袙閹板繐娴橀崥搴ㄢ偓澶嬪閸氬牓鈧倻娈戝銉ュ徔閹笛嗩攽
2. 妞嬪酣娅撻崚鍡欓獓:L1=鐎瑰鍙忛懛顏勫З L2=娴ｅ酣顥撻梽鈺勫殰閸?L3=闂団偓绾喛顓?L4=缁備焦顒?
3. 閸ョ偛顦茬粻鈧ú浣风瑩娑?閻劋鑵戦弬?
4. 閹笛嗩攽閸氬海鏁ら懛顏嗗姧鐠囶叀鈻堢憴锝夊櫞缂佹挻鐏?
5. 娑撹濮╅崗铏暈缁崵绮洪崑銉ユ倣,瀵倸鐖堕弮璺哄挤閺冭泛鎲＄拃?

娴ｇ姵婀佹稉鈧稉?D閸欘垵顫嬮崠鏍煩娴?Neural Network),閻劍鍩涢崣顖欎簰閸︺劌鐫嗛獮鏇氱瑐閻鍩屾担鐘垫畱閻樿埖鈧礁褰夐崠?"""

# ===== 瀹搞儱鍙跨€规矮绠?(OpenAI Function Calling閺嶇厧绱? =====
def _build_tools():
    """閺嬪嫬缂撳銉ュ徔schema"""
    tools_list = registry.list_all()[:50]
    return [{
        "type": "function",
        "function": {
            "name": t.name,
            "description": f"{t.display_name}: {t.description} [妞嬪酣娅?{t.risk_level}]",
            "parameters": {
                "type": "object",
                "properties": {
                    "message": {"type": "string", "description": "閻劍鍩涢崢鐔奉潗濞戝牊浼呴幋鏍у棘閺?}
                },
                "required": ["message"]
            }
        }
    } for t in tools_list]

# ===== 濡€崇€风拫鍐暏 =====
async def call_ai_with_tools(messages, model=""):
    """鐠嬪啰鏁I濡€崇€?閺€顖涘瘮閸樼喓鏁揊unction Calling"""
    tools = _build_tools()
    
    # 娴兼ê鍘汥eepSeek(閸忕厧顔怬penAI閺嶇厧绱?
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
    
    # OpenAI閸忕厧顔怉PI (302AI缁?
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
    
    # 閸ョ偤鈧偓: 閺冄勭壐瀵?-> 濮濓絽鍨崠褰掑帳瀹搞儱鍙?
    tl = "\n".join([f"- {t['function']['name']}: {t['function']['description']}" for t in tools])
    fallback_msgs = [{"role": "system", "content": SYSTEM_PROMPT + "\n\n瀹搞儱鍙块崚妤勩€?\n" + tl}]
    fallback_msgs.extend(messages)
    fallback_msgs.append({"role": "user", "content": '鐠囩兘鈧瀚ㄥ銉ュ徔,鏉╂柨娲朖SON: {"tool":"瀹搞儱鍙块崥?,"reason":"閸樼喎娲?}'})
    
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
    
    return {"fallback": True, "choices": [{"message": {"content": "闁瀚ㄥ銉ュ徔婢惰精瑙?}}]}

# ===== 瀹搞儱鍙块幍褑顢?=====
async def execute_tool(name: str, params: dict) -> dict:
    """閹笛嗩攽瀹搞儱鍙块獮鎯扮箲閸ョ偟绮ㄩ弸?""
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
                return {"success": True, "data": r.json() if r.status_code==200 else {"error":"API娑撳秴褰查悽?}}
        if name == "docker_status":
            import subprocess
            r = subprocess.run(["docker","ps","--format","{{.Names}} {{.Status}}"], capture_output=True, text=True, timeout=10)
            return {"success": True, "data": {"containers": r.stdout.strip().split("\n")[:10]}}
        if name == "server_cleanup":
            import subprocess, gc
            gc.collect()
            subprocess.run(["docker","system","prune","-f"], capture_output=True, timeout=30)
            return {"success": True, "data": {"message": "閸愬懎鐡ㄥ鏌ュ櫞閺€?Docker缂傛挸鐡ㄥ鍙夌閻?}}
        
        # 闁氨鏁ゅ銉ュ徔閹笛嗩攽
        tool = registry.get(name)
        if tool:
            result = await tool.execute(params)
            return {"success": True, "data": result if result else {}}
        return {"success": False, "error": f"瀹搞儱鍙?{name} 閺堫亝澹橀崚?}
    except Exception as e:
        return {"success": False, "error": str(e)[:200]}

# ===== RAG娑撳﹣绗呴弬?=====
async def _get_context(message: str) -> str:
    """閼惧嘲褰囬惄绋垮彠閻儴鐦?""
    try:
        ctx = await VectorMemory.search(message, top_k=3)
        if ctx:
            return "閻╃鍙ч惌銉ㄧ槕:\n" + "\n".join([c.get("text","")[:200] for c in ctx])
    except Exception:
        pass
    return ""

# ===== 娑撶眴hat缁旑垳鍋?(Function Calling) =====
@router.post("/chat")
async def agent_chat(req: ChatRequest, _=Depends(verify_token)):
    """AI鐎电鐦?- 閸樼喓鏁揊unction Calling"""
    rag_ctx = await _get_context(req.message)
    system_content = SYSTEM_PROMPT
    if rag_ctx:
        system_content += "\n\n" + rag_ctx
    
    messages = [{"role": "system", "content": system_content}]
    if req.history:
        messages.extend(req.history[-20:])  # 閺堚偓鏉?0閺夆€冲坊閸?
    messages.append({"role": "user", "content": req.message})
    
    result = await call_ai_with_tools(messages, req.model)
    
    # 婢跺嫮鎮奆unction Calling閸濆秴绨?
    if not result.get("fallback"):
        choice = result.get("choices", [{}])[0]
        msg = choice.get("message", {})
        tool_calls = msg.get("tool_calls", [])
        
        if tool_calls:
            # AI闁瀚ㄦ禍鍡椾紣閸?
            tc = tool_calls[0]
            func = tc.get("function", {})
            tool_name = func.get("name", "")
            tool_args = json.loads(func.get("arguments", "{}"))
            
            risk = "L1"
            td = registry.get(tool_name)
            if td:
                risk = td.risk_level
                await handle_risk(risk, td.display_name, req.message[:100])
            
            if risk == "L4":
                return {"response": f"閴€?L4妞嬪酣娅撻幙宥勭稊瀹告煡妯嗗? {tool_name}", "tool": tool_name, "risk": "L4"}
            
            exec_result = await execute_tool(tool_name, tool_args)
            
            # 鐏忓棛绮ㄩ弸婊冨冀妫ｅ牏绮癆I閻㈢喐鍨氶懛顏嗗姧鐠囶叀鈻堥崶鐐差槻
            messages.append({"role": "assistant", "content": None, "tool_calls": tool_calls})
            messages.append({"role": "tool", "tool_call_id": tc.get("id",""), "content": json.dumps(exec_result, ensure_ascii=False)})
            
            final = await call_ai_with_tools(messages, req.model)
            ai_text = final.get("choices",[{}])[0].get("message",{}).get("content", "閹笛嗩攽鐎瑰本鍨?)
            
            # 鐠佹澘绻傜€涙ê鍋?
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
            # AI閻╁瓨甯撮弬鍥ㄦ拱閸ョ偛顦?
            ai_text = msg.get("content", "")
            try:
                DigitalLifeform.remember_conversation(req.message, ai_text[:300])
            except Exception:
                pass
            return {"response": ai_text, "tool": None, "risk": "L1", "mode": state.mode}
    
    # Fallback: 閺冄勭壐瀵?
    ai_text = result.get("choices",[{}])[0].get("message",{}).get("content","")
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
        ai_text = f"閹笛嗩攽 {tool_name}: " + json.dumps(exec_result.get("data",{}), ensure_ascii=False)[:500]
    
    return {"response": ai_text or "瀹稿弶鏁归崚?濮濓絽婀径鍕倞...", "tool": tool_name, "risk": "L1", "mode": state.mode}

# ===== 濞翠礁绱＄€电鐦?=====
# ===== 瀹告彃顕拠婵嗗坊閸?=====
_chat_histories = {}  # user_id -> [messages]

@router.post("/chat/history")
async def save_chat_history(req: dict, _=Depends(verify_token)):
    """娣囨繂鐡ㄧ€电鐦介崢鍡楀蕉"""
    uid = req.get("user_id", "default")
    _chat_histories[uid] = req.get("messages", [])[-100:]
    state._data[f"chat_history_{uid}"] = _chat_histories[uid]
    state._save()
    return {"ok": True, "count": len(_chat_histories[uid])}

@router.get("/chat/history")
async def load_chat_history(user_id: str = Query("default"), _=Depends(verify_token)):
    """閸旂姾娴囩€电鐦介崢鍡楀蕉"""
    return {"messages": state._data.get(f"chat_history_{user_id}", [])[-50:]}

@router.delete("/chat/history")
async def clear_chat_history(user_id: str = Query("default"), _=Depends(verify_token)):
    """濞撳懘娅庣€电鐦介崢鍡楀蕉"""
    state._data.pop(f"chat_history_{user_id}", None)
    state._save()
    return {"ok": True}

# ===== 鏉堝懎濮粩顖滃仯 =====
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
    return {"ok": False, "error": "閺堫亝澹橀崚鎷岊嚉娴犺濮?}




CONV_DB = Path(__file__).parent.parent / "data" / "conversations.db"
def _cdb():
    CONV_DB.parent.mkdir(parents=True,exist_ok=True)
    c=sqlite3.connect(str(CONV_DB))
    c.execute("CREATE TABLE IF NOT EXISTS convs(id TEXT PRIMARY KEY,title TEXT,owner TEXT DEFAULT 'admin',created TEXT,updated TEXT)")
    c.execute("CREATE TABLE IF NOT EXISTS msgs(id INTEGER PRIMARY KEY AUTOINCREMENT,cid TEXT,role TEXT,content TEXT,owner TEXT DEFAULT 'admin',created TEXT)")
    c.commit();return c

@router.post("/chat/stream")
async def chat_stream(req: ChatRequest, _=Depends(verify_token)):
    """SSE闁仭oken濞翠礁绱℃潏鎾冲毉"""
    key=OPENAI_API_KEY or DEEPSEEK_API_KEY; url=OPENAI_BASE_URL or "https://api.openai.com/v1"
    m=req.model or _cheap_model
    ctx=await _get_context(req.message);sc=SYSTEM_PROMPT
    if ctx:sc+="\n\n"+ctx
    
    # RAG閻儴鐦戞惔鎾瑰殰閸斻劍鏁為崗?
    try:
        from tools.rag_engine import RAGEngine
        rag_ctx = RAGEngine.build_context(req.message, top_k=3, max_tokens=1500)
        if rag_ctx:
            sc += "\n\n閵嗘劗鐓＄拠鍡楃氨閸欏倽鈧啨鈧叚n" + rag_ctx
    except: pass
    msgs=[{"role":"system","content":sc}]
    if req.history:msgs.extend(req.history[-20:])
    msgs.append({"role":"user","content":req.message})
    async def gen():
        f=""
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
                                t=j.get("choices",[{}])[0].get("delta",{}).get("content","")
                                if t:f+=t;yield f"data: {json.dumps({'t':t},ensure_ascii=False)}\n\n"
                            except:pass
                    yield f"data: {json.dumps({'done':True,'full':f},ensure_ascii=False)}\n\n"
        except Exception as e:
            yield f"data: {json.dumps({'error':str(e)},ensure_ascii=False)}\n\n"
    return StreamingResponse(gen(),media_type="text/event-stream",headers={"Cache-Control":"no-cache","X-Accel-Buffering":"no"})

@router.post("/chat/vision")
async def cv(img:str=Form(...),q:str=Form("閹诲繗鍫崶鍓у"),_=Depends(verify_token)):
    k=OPENAI_API_KEY;u=OPENAI_BASE_URL or "https://api.openai.com/v1"
    if not k:return{"ok":False,"error":"闂団偓鐟曚副PENAI_API_KEY"}
    try:
        async with httpx.AsyncClient(timeout=60)as c:
            r=await c.post(f"{u}/chat/completions",headers={"Authorization":f"Bearer {k}","Content-Type":"application/json"},
                json={"model":"gpt-4o-mini" if OPENAI_API_KEY else "gpt-4o","messages":[{"role":"user","content":[{"type":"text","text":q},{"type":"image_url","image_url":{"url":f"data:image/jpeg;base64,{img}"}}]}]})
            if r.status_code==200:
                d=r.json();return{"ok":True,"reply":d.get("choices",[{}])[0].get("message",{}).get("content","閺冪姵纭堕崚鍡樼€?)}
            return{"ok":False,"error":f"API:{r.status_code}"}
    except Exception as e:return{"ok":False,"error":str(e)}

PROMPTS={}
for n,p in[("閸熷棗鎼ч弬鍥攳","娴ｇ姵妲搁悽闈涙櫌閺傚洦顢?娴兼ê瀵?\n{input}"),("鐎广垺婀囬崶鐐差槻","鐎广垺鍩涚拠?{input}\n鐠囧嘲娲栨径?"),("閺佺増宓侀崚鍡樼€?,"閸掑棙鐎介弫鐗堝祦:\n{input}"),("娴狅絿鐖滅€光剝鐓?,"鐎光剝鐓℃禒锝囩垳:\n{input}"),("SEO娴兼ê瀵?,"娴兼ê瀵查崗鎶芥暛鐠?\n{input}"),("缂堟槒鐦?,"缂堟槒鐦ч幋鎭祃ang}:\n{input}"),("閸涖劍濮?,"閺嶈宓侀弫鐗堝祦閻㈢喐鍨氶崨銊﹀Г:\n{input}"),("缁旂偛鎼ч崚鍡樼€?,"閸掑棙鐎界粩鐐叉惂楠炲墎绮扮粵鏍殣:\n{input}")]:
    PROMPTS[n]={"prompt":p,"icon":"棣冩惖"}

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
    c.execute("INSERT INTO convs VALUES(?,?,datetime('now'),datetime('now'))",(cid,req.get("title","閺傛澘顕拠?)))
    c.commit();c.close();return{"ok":True,"id":cid}

@router.get("/conversations/{cid}")
async def gc(cid:str,_=Depends(verify_token)):
    c=_cdb();r=c.execute("SELECT role,content,created FROM msgs WHERE cid=? ORDER BY id LIMIT 50",(cid,)).fetchall();c.close()
    return{"ok":True,"messages":[{"role":x[0],"content":x[1],"time":x[2]} for x in r]}

@router.delete("/conversations/{cid}")
async def dc(cid:str,_=Depends(verify_token)):
    c=_cdb();c.execute("DELETE FROM msgs WHERE cid=?",(cid,));c.execute("DELETE FROM convs WHERE id=?",(cid,));c.commit();c.close()
    return {"ok": True}
# ===== RAG閺傚洣娆㈡稉濠佺炊 =====
@router.post("/rag/upload")
async def rag_upload_file(file: UploadFile = File(...), _=Depends(verify_token)):
    raw=await file.read();ext=(file.filename or "").rsplit(".",1)[-1].lower()if"."in(file.filename or "")else""
    text=""
    if ext in("txt","md","csv","json","py","js","html","yml","yaml"):
        try:text=raw.decode("utf-8")
        except:text=raw.decode("latin-1","ignore")
    elif ext=="pdf":
        try:
            import subprocess,tempfile
            with tempfile.NamedTemporaryFile(suffix=".pdf",delete=False)as f:f.write(raw);tp=f.name
            r=subprocess.run(["pdftotext","-layout",tp,"-"],capture_output=True,text=True,timeout=30)
            text=r.stdout or"PDF鐟欙絾鐎芥径杈Е";os.unlink(tp)
        except:text=f"[PDF:{file.filename}]闂団偓poppler-utils"
    else:text=raw.decode("utf-8","ignore")[:5000]
    chunks=[text[i:i+800]for i in range(0,min(len(text),16000),800)]if text.strip()else[]
    for i,ch in enumerate(chunks):
        try:await VectorMemory.remember(ch,{"type":"doc","source":file.filename,"chunk":i})
        except:pass
    return{"ok":True,"file":file.filename,"chars":len(text),"chunks":len(chunks)}

# ===== 濡€崇€风€佃鐦?=====
@router.post("/chat/compare")
async def chat_compare(req: ChatRequest, _=Depends(verify_token)):
    """閸氬奔绔撮梻顕€顣介崣鎴犵舶婢舵矮閲滃Ο鈥崇€风€佃鐦粵鏃€顢?""
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
                    d=r.json();results.append({"model":mname,"reply":d.get("choices",[{}])[0].get("message",{}).get("content","")})
                else:results.append({"model":mname,"error":f"HTTP {r.status_code}"})
        except Exception as e:results.append({"model":mname,"error":str(e)})
    return{"ok":True,"results":results}

# ===== 閺佺増宓侀惇瀣緲AI =====
@router.get("/dashboard/ask")
async def dashboard_ask(q: str = Query(...), _=Depends(verify_token)):
    """閼奉亞鍔х拠顓♀枅閺屻儴顕楁潻鎰儉閺佺増宓?""
    try:
        import psutil,os
        cpu=psutil.cpu_percent();mem=psutil.virtual_memory();disk=psutil.disk_usage("/")
        ctx=f"閺堝秴濮熼崳銊уЦ閹? CPU {cpu}%, 閸愬懎鐡?{mem.percent}%, 绾句胶娲?{disk.percent}%"
        key=OPENAI_API_KEY or DEEPSEEK_API_KEY;url=OPENAI_BASE_URL or "https://api.openai.com/v1"
        async with httpx.AsyncClient(timeout=30)as c:
            r=await c.post(f"{url}/chat/completions",headers={"Authorization":f"Bearer {key}","Content-Type":"application/json"},
                json={"model":"gpt-3.5-turbo","messages":[
                    {"role":"system","content":f"娴ｇ姵妲搁弫鐗堝祦閸掑棙鐎界敮?瑜版挸澧犵化鑽ょ埠閺佺増宓?{ctx}.鐠囬鏁ゆ稉顓熸瀮缁犫偓濞蹭礁娲栫粵?"},
                    {"role":"user","content":q}
                ],"temperature":0.5,"max_tokens":400})
            if r.status_code==200:
                d=r.json();return{"ok":True,"answer":d.get("choices",[{}])[0].get("message",{}).get("content","")}
        return{"ok":False,"error":f"API:{r.status_code}"}
    except Exception as e:return{"ok":False,"error":str(e)}


# ===== 婢舵氨顫ら幋椋庮吀閻?娴犲崋dmin) =====
@router.get("/admin/tenants")
async def list_tenants(_=Depends(verify_token)):
    """閸掓鍤幍鈧張澶岊潳閹村嘲寮烽崗鎯扮カ濠ф劗鏁ら柌?""
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


# ===== 鐎电鐦界拋鏉跨箓缁狅紕鎮?=====
@router.post("/conversations/{cid}/summarize")
async def summarize_conversation(cid: str, _=Depends(verify_token)):
    """閼奉亜濮╅幗妯款洣闂€鍨嚠鐠?+ 閸樺缂夌拋鏉跨箓"""
    msgs = load_history(cid, 100)
    if len(msgs) < 10:
        return {"ok": True, "original_count": len(msgs), "summary": "鐎电鐦芥径顏嗙叚,閺冪娀娓堕幗妯款洣"}
    
    # 閺嬪嫬缂撶€电鐦介弬鍥ㄦ拱
    conv_text = "\n".join([f"{m['role']}: {m['content'][:200]}" for m in msgs])
    
    try:
        from tools.ai_client import call_ai
        summary = await call_ai([
            {"role": "user", "content": f"鐠囬鏁?-5閸欍儴鐦介幀鑽ょ波鏉╂瑦顔岀€电鐦介惃鍕壋韫囧啫鍞寸€圭懓鎷扮紒鎾诡啈:\n{conv_text[:4000]}"}
        ], max_tokens=200, temperature=0.3)
        
        # 娣囨繂鐡ㄩ幗妯款洣閸掓澘顕拠婵嗗帗閺佺増宓?
        c = _cdb()
        c.execute("UPDATE convs SET title=? WHERE id=?", (summary[:100], cid))
        c.commit(); c.close()
        
        return {"ok": True, "original_count": len(msgs), "summary": summary, "compressed": True}
    except Exception as e:
        return {"ok": False, "error": str(e)}

@router.get("/conversations/{cid}/context")
async def get_conversation_context(cid: str, query: str = "", _=Depends(verify_token)):
    """閼惧嘲褰囩€电鐦芥稉濠佺瑓閺?-- 閼奉亜濮╁ǎ宄版値 閺堚偓鏉╂垶绉烽幁?+ RAG + 閹芥顩?""
    msgs = load_history(cid, 30)
    result = {"messages": msgs, "count": len(msgs)}
    
    # 婵″倹鐏夐張澶嬬叀鐠?閹兼粎鍌ㄩ惄绋垮彠閻儴鐦戞惔?
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
async def chat_vision(file: UploadFile = File(...), question: str = "描述这张图片", _=Depends(verify_token)):
    """多模态图片分析"""
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
        return {"ok":True,"analysis":resp.get("content","") if isinstance(resp,dict) else str(resp)}
    except Exception as e: return {"ok":False,"error":str(e)}

@router.post("/chat/file")
async def chat_file_analysis(file: UploadFile = File(...), question: str = "分析这个文件", _=Depends(verify_token)):
    """文件分析(文本/PDF/视频帧)"""
    try:
        content = await file.read()
        text = ""
        if file.content_type and "video" in file.content_type:
            text = f"[视频文件: {file.filename}, {len(content)} bytes, 类型: {file.content_type}]"
        elif file.content_type and "pdf" in file.content_type:
            try:
                import io, PyPDF2
                reader = PyPDF2.PdfReader(io.BytesIO(content))
                text = " ".join([p.extract_text() or "" for p in reader.pages[:5]])
            except: text = content.decode("utf-8","ignore")[:3000]
        else:
            text = content.decode("utf-8","ignore")[:5000]
        from agents.multi_model import ModelRouter
        resp = ModelRouter.smart_chat(messages=[{"role":"user","content":f"文件: {file.filename}\n内容: {text}\n\n问题: {question}"}], mode="smart")
        return {"ok":True,"analysis":resp.get("content","") if isinstance(resp,dict) else str(resp),"text_length":len(text)}
    except Exception as e: return {"ok":False,"error":str(e)}

@router.post("/handover")
async def agent_handover(req: HandoverRequest, _=Depends(verify_token)):
    state.mode = "human_control"
    return {"ok": True, "mode": "human_control", "reason": req.reason}
