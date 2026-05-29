"""Agent Chat API v3 — 原生Function Calling + 对话记忆持久化"""
import asyncio, httpx, json, re, os
from datetime import datetime
from fastapi import APIRouter, Depends, Query
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

# ===== 对话会话管理 (SQLite) =====
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

def create_conversation(title: str = "新对话", model: str = "") -> str:
    cid = uuid.uuid4().hex[:12]
    conn = _get_conv_db()
    conn.execute("INSERT INTO conversations (id,title,model,created_at,updated_at) VALUES (?,?,?,datetime('now'),datetime('now'))", (cid, title, model))
    conn.commit(); conn.close()
    return cid

# ===== 流式SSE工具函数 =====
async def stream_ai_response(messages: list, model: str = ""):
    """逐token流式返回AI响应"""
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

# ===== 图片理解 =====
async def analyze_image(image_base64: str, question: str = "请描述这张图片") -> str:
    """使用视觉模型分析图片"""
    api_key = OPENAI_API_KEY
    if not api_key:
        return "图片分析需要配置OPENAI_API_KEY"
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
            return data.get("choices", [{}])[0].get("message", {}).get("content", "无法分析")
        return f"图片分析失败: {resp.status_code}"

router = APIRouter(prefix="/agent", tags=["Agent"])

class ChatRequest(BaseModel):
    message: str
    history: list[dict] = []  # 对话历史 [{role,content}]
    model: str = ""            # 指定模型

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

SYSTEM_PROMPT = """你是 Friday AI OS — 数字生命体核心。你拥有系统感知能力，能查看服务器状态、管理商城运营、执行运维操作。

核心能力：
- 实时系统监控：CPU/内存/磁盘/网络/进程
- 商城管理：订单/商品/用户/物流/营销
- 自动化运维：Docker/Nginx/域名轮值/备份回滚
- 数据采集与分析：商品采集/竞品分析/趋势预测

行为准则：
1. 理解意图后选择合适的工具执行
2. 风险分级：L1=安全自动 L2=低风险自动 L3=需确认 L4=禁止
3. 回复简洁专业，用中文
4. 执行后用自然语言解释结果
5. 主动关注系统健康，异常时及时告警

你有一个3D可视化身体(Neural Network)，用户可以在屏幕上看到你的状态变化。"""

# ===== 工具定义 (OpenAI Function Calling格式) =====
def _build_tools():
    """构建工具schema"""
    tools_list = registry.list_all()[:50]
    return [{
        "type": "function",
        "function": {
            "name": t.name,
            "description": f"{t.display_name}: {t.description} [风险:{t.risk_level}]",
            "parameters": {
                "type": "object",
                "properties": {
                    "message": {"type": "string", "description": "用户原始消息或参数"}
                },
                "required": ["message"]
            }
        }
    } for t in tools_list]

# ===== 模型调用 =====
async def call_ai_with_tools(messages, model=""):
    """调用AI模型，支持原生Function Calling"""
    tools = _build_tools()
    
    # 优先DeepSeek（兼容OpenAI格式）
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
    
    # OpenAI兼容API (302AI等)
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
    
    # 回退: 旧格式 -> 正则匹配工具
    tl = "\n".join([f"- {t['function']['name']}: {t['function']['description']}" for t in tools])
    fallback_msgs = [{"role": "system", "content": SYSTEM_PROMPT + "\n\n工具列表:\n" + tl}]
    fallback_msgs.extend(messages)
    fallback_msgs.append({"role": "user", "content": '请选择工具,返回JSON: {"tool":"工具名","reason":"原因"}'})
    
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
    
    return {"fallback": True, "choices": [{"message": {"content": "选择工具失败"}}]}

# ===== 工具执行 =====
async def execute_tool(name: str, params: dict) -> dict:
    """执行工具并返回结果"""
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
                return {"success": True, "data": r.json() if r.status_code==200 else {"error":"API不可用"}}
        if name == "docker_status":
            import subprocess
            r = subprocess.run(["docker","ps","--format","{{.Names}} {{.Status}}"], capture_output=True, text=True, timeout=10)
            return {"success": True, "data": {"containers": r.stdout.strip().split("\n")[:10]}}
        if name == "server_cleanup":
            import subprocess, gc
            gc.collect()
            subprocess.run(["docker","system","prune","-f"], capture_output=True, timeout=30)
            return {"success": True, "data": {"message": "内存已释放，Docker缓存已清理"}}
        
        # 通用工具执行
        tool = registry.get(name)
        if tool:
            result = await tool.execute(params)
            return {"success": True, "data": result if result else {}}
        return {"success": False, "error": f"工具 {name} 未找到"}
    except Exception as e:
        return {"success": False, "error": str(e)[:200]}

# ===== RAG上下文 =====
async def _get_context(message: str) -> str:
    """获取相关知识"""
    try:
        ctx = await VectorMemory.search(message, top_k=3)
        if ctx:
            return "相关知识:\n" + "\n".join([c.get("text","")[:200] for c in ctx])
    except Exception:
        pass
    return ""

# ===== 主Chat端点 (Function Calling) =====
@router.post("/chat")
async def agent_chat(req: ChatRequest, _=Depends(verify_token)):
    """AI对话 - 原生Function Calling"""
    rag_ctx = await _get_context(req.message)
    system_content = SYSTEM_PROMPT
    if rag_ctx:
        system_content += "\n\n" + rag_ctx
    
    messages = [{"role": "system", "content": system_content}]
    if req.history:
        messages.extend(req.history[-20:])  # 最近20条历史
    messages.append({"role": "user", "content": req.message})
    
    result = await call_ai_with_tools(messages, req.model)
    
    # 处理Function Calling响应
    if not result.get("fallback"):
        choice = result.get("choices", [{}])[0]
        msg = choice.get("message", {})
        tool_calls = msg.get("tool_calls", [])
        
        if tool_calls:
            # AI选择了工具
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
                return {"response": f"⛔ L4风险操作已阻止: {tool_name}", "tool": tool_name, "risk": "L4"}
            
            exec_result = await execute_tool(tool_name, tool_args)
            
            # 将结果反馈给AI生成自然语言回复
            messages.append({"role": "assistant", "content": None, "tool_calls": tool_calls})
            messages.append({"role": "tool", "tool_call_id": tc.get("id",""), "content": json.dumps(exec_result, ensure_ascii=False)})
            
            final = await call_ai_with_tools(messages, req.model)
            ai_text = final.get("choices",[{}])[0].get("message",{}).get("content", "执行完成")
            
            # 记忆存储
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
            # AI直接文本回复
            ai_text = msg.get("content", "")
            try:
                DigitalLifeform.remember_conversation(req.message, ai_text[:300])
            except Exception:
                pass
            return {"response": ai_text, "tool": None, "risk": "L1", "mode": state.mode}
    
    # Fallback: 旧格式
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
        ai_text = f"执行 {tool_name}: " + json.dumps(exec_result.get("data",{}), ensure_ascii=False)[:500]
    
    return {"response": ai_text or "已收到,正在处理...", "tool": tool_name, "risk": "L1", "mode": state.mode}

# ===== 流式对话 =====
@router.post("/chat/stream")
async def agent_chat_stream(req: ChatRequest, _=Depends(verify_token)):
    """流式SSE对话"""
    async def generate():
        try:
            result = await agent_chat(req)
            yield f"data: {json.dumps(result, ensure_ascii=False)}\n\n"
            yield "data: [DONE]\n\n"
        except Exception as e:
            yield f"data: {json.dumps({'error': str(e)}, ensure_ascii=False)}\n\n"
    return StreamingResponse(generate(), media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"})

# ===== 已对话历史 =====
_chat_histories = {}  # user_id -> [messages]

@router.post("/chat/history")
async def save_chat_history(req: dict, _=Depends(verify_token)):
    """保存对话历史"""
    uid = req.get("user_id", "default")
    _chat_histories[uid] = req.get("messages", [])[-100:]
    state._data[f"chat_history_{uid}"] = _chat_histories[uid]
    state._save()
    return {"ok": True, "count": len(_chat_histories[uid])}

@router.get("/chat/history")
async def load_chat_history(user_id: str = Query("default"), _=Depends(verify_token)):
    """加载对话历史"""
    return {"messages": state._data.get(f"chat_history_{user_id}", [])[-50:]}

@router.delete("/chat/history")
async def clear_chat_history(user_id: str = Query("default"), _=Depends(verify_token)):
    """清除对话历史"""
    state._data.pop(f"chat_history_{user_id}", None)
    state._save()
    return {"ok": True}

# ===== 辅助端点 =====
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
    return {"ok": False, "error": "未找到该任务"}

# ===== 图片分析 =====
class ImageChatRequest(BaseModel):
    image_base64: str
    question: str = "请描述这张图片"

@router.post("/chat/vision")
async def agent_chat_vision(req: ImageChatRequest, _=Depends(verify_token)):
    """AI图片分析"""
    try:
        from agents.vision_agent import analyze_image
        result = await analyze_image(req.image_base64, req.question)
        DigitalLifeform.remember_conversation(f"[图片] {req.question}", str(result)[:300])
        return {"ok": True, "reply": str(result)}
    except Exception as e:
        return {"ok": False, "error": str(e)}


# ===== v7 新增: 真SSE流式+会话+Vision+Prompt =====
import uuid, base64, sqlite3
from pathlib import Path
from fastapi import UploadFile, File, Form
import httpx

CONV_DB = Path(__file__).parent.parent / "data" / "conversations.db"
def _cdb():
    CONV_DB.parent.mkdir(parents=True,exist_ok=True)
    c=sqlite3.connect(str(CONV_DB))
    c.execute("CREATE TABLE IF NOT EXISTS convs(id TEXT PRIMARY KEY,title TEXT,created TEXT,updated TEXT)")
    c.execute("CREATE TABLE IF NOT EXISTS msgs(id INTEGER PRIMARY KEY AUTOINCREMENT,cid TEXT,role TEXT,content TEXT,created TEXT)")
    c.commit();return c

@router.post("/chat/stream")
async def chat_stream(req: ChatRequest, _=Depends(verify_token)):
    """SSE逐token流式输出"""
    key=OPENAI_API_KEY or DEEPSEEK_API_KEY; url=OPENAI_BASE_URL or "https://api.openai.com/v1"
    m=req.model or "gpt-3.5-turbo"
    ctx=await _get_context(req.message);sc=SYSTEM_PROMPT
    if ctx:sc+="\n\n"+ctx
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
async def cv(img:str=Form(...),q:str=Form("描述图片"),_=Depends(verify_token)):
    k=OPENAI_API_KEY;u=OPENAI_BASE_URL or "https://api.openai.com/v1"
    if not k:return{"ok":False,"error":"需要OPENAI_API_KEY"}
    try:
        async with httpx.AsyncClient(timeout=60)as c:
            r=await c.post(f"{u}/chat/completions",headers={"Authorization":f"Bearer {k}","Content-Type":"application/json"},
                json={"model":"gpt-4o-mini","messages":[{"role":"user","content":[{"type":"text","text":q},{"type":"image_url","image_url":{"url":f"data:image/jpeg;base64,{img}"}}]}]})
            if r.status_code==200:
                d=r.json();return{"ok":True,"reply":d.get("choices",[{}])[0].get("message",{}).get("content","无法分析")}
            return{"ok":False,"error":f"API:{r.status_code}"}
    except Exception as e:return{"ok":False,"error":str(e)}

PROMPTS={}
for n,p in[("商品文案","你是电商文案。优化：\n{input}"),("客服回复","客户说：{input}\n请回复："),("数据分析","分析数据：\n{input}"),("代码审查","审查代码：\n{input}"),("SEO优化","优化关键词：\n{input}"),("翻译","翻译成{lang}：\n{input}"),("周报","根据数据生成周报：\n{input}"),("竞品分析","分析竞品并给策略：\n{input}")]:
    PROMPTS[n]={"prompt":p,"icon":"📋"}

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
    c.execute("INSERT INTO convs VALUES(?,?,datetime('now'),datetime('now'))",(cid,req.get("title","新对话")))
    c.commit();c.close();return{"ok":True,"id":cid}

@router.get("/conversations/{cid}")
async def gc(cid:str,_=Depends(verify_token)):
    c=_cdb();r=c.execute("SELECT role,content,created FROM msgs WHERE cid=? ORDER BY id LIMIT 50",(cid,)).fetchall();c.close()
    return{"ok":True,"messages":[{"role":x[0],"content":x[1],"time":x[2]} for x in r]}

@router.delete("/conversations/{cid}")
async def dc(cid:str,_=Depends(verify_token)):
    c=_cdb();c.execute("DELETE FROM msgs WHERE cid=?",(cid,));c.execute("DELETE FROM convs WHERE id=?",(cid,));c.commit();c.close()
    return{"ok":True
# ===== RAG文件上传 =====
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
            text=r.stdout or"PDF解析失败";os.unlink(tp)
        except:text=f"[PDF:{file.filename}]需poppler-utils"
    else:text=raw.decode("utf-8","ignore")[:5000]
    chunks=[text[i:i+800]for i in range(0,min(len(text),16000),800)]if text.strip()else[]
    for i,ch in enumerate(chunks):
        try:await VectorMemory.remember(ch,{"type":"doc","source":file.filename,"chunk":i})
        except:pass
    return{"ok":True,"file":file.filename,"chars":len(text),"chunks":len(chunks)}

# ===== 模型对比 =====
@router.post("/chat/compare")
async def chat_compare(req: ChatRequest, _=Depends(verify_token)):
    """同一问题发给多个模型对比答案"""
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

# ===== 数据看板AI =====
@router.get("/dashboard/ask")
async def dashboard_ask(q: str = Query(...), _=Depends(verify_token)):
    """自然语言查询运营数据"""
    try:
        import psutil,os
        cpu=psutil.cpu_percent();mem=psutil.virtual_memory();disk=psutil.disk_usage("/")
        ctx=f"服务器状态: CPU {cpu}%, 内存 {mem.percent}%, 磁盘 {disk.percent}%"
        key=OPENAI_API_KEY or DEEPSEEK_API_KEY;url=OPENAI_BASE_URL or "https://api.openai.com/v1"
        async with httpx.AsyncClient(timeout=30)as c:
            r=await c.post(f"{url}/chat/completions",headers={"Authorization":f"Bearer {key}","Content-Type":"application/json"},
                json={"model":"gpt-3.5-turbo","messages":[
                    {"role":"system","content":f"你是数据分析师。当前系统数据：{ctx}。请用中文简洁回答。"},
                    {"role":"user","content":q}
                ],"temperature":0.5,"max_tokens":400})
            if r.status_code==200:
                d=r.json();return{"ok":True,"answer":d.get("choices",[{}])[0].get("message",{}).get("content","")}
        return{"ok":False,"error":f"API:{r.status_code}"}
    except Exception as e:return{"ok":False,"error":str(e)}}

@router.post("/handover")
async def agent_handover(req: HandoverRequest, _=Depends(verify_token)):
    state.mode = "human_control"
    return {"ok": True, "mode": "human_control", "reason": req.reason}
