锘?""Agent Chat API v3 鈥?鍘熺敓Function Calling + 瀵硅瘽璁板繂鎸佷箙鍖?""
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

router = APIRouter(prefix="/agent", tags=["Agent"])

class ChatRequest(BaseModel):
    message: str
    history: list[dict] = []  # 瀵硅瘽鍘嗗彶 [{role,content}]
    model: str = ""            # 鎸囧畾妯″瀷

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

SYSTEM_PROMPT = """浣犳槸 Friday AI OS锛屼竴涓櫤鑳借繍缁村姪鎵嬨€備綘鑳借皟鐢ㄥ伐鍏锋墽琛屽疄闄呮搷浣溿€?

瑙勫垯锛?
1. 鐞嗚В鐢ㄦ埛鎰忓浘锛岄€夋嫨鍚堥€傜殑宸ュ叿
2. 鍒ゆ柇椋庨櫓绛夌骇锛歀1=瀹夊叏 L2=浣庨闄?L3=闇€瀹℃壒 L4=绂佹
3. L1鑷姩鎵ц锛孡3闇€纭锛孡4鎷掔粷
4. 鐢ㄤ腑鏂囧洖澶嶏紝绠€娲佷笓涓?
5. 鎵ц瀹屽伐鍏峰悗锛岀敤鑷劧璇█瑙ｉ噴缁撴灉"""

# ===== 宸ュ叿瀹氫箟 (OpenAI Function Calling鏍煎紡) =====
def _build_tools():
    """鏋勫缓宸ュ叿schema"""
    tools_list = registry.list_all()[:50]
    return [{
        "type": "function",
        "function": {
            "name": t.name,
            "description": f"{t.display_name}: {t.description} [椋庨櫓:{t.risk_level}]",
            "parameters": {
                "type": "object",
                "properties": {
                    "message": {"type": "string", "description": "鐢ㄦ埛鍘熷娑堟伅鎴栧弬鏁?}
                },
                "required": ["message"]
            }
        }
    } for t in tools_list]

# ===== 妯″瀷璋冪敤 =====
async def call_ai_with_tools(messages, model=""):
    """璋冪敤AI妯″瀷锛屾敮鎸佸師鐢烣unction Calling"""
    tools = _build_tools()
    
    # 浼樺厛DeepSeek锛堝吋瀹筄penAI鏍煎紡锛?
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
    
    # OpenAI鍏煎API (302AI绛?
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
    
    # 鍥為€€: 鏃ф牸寮?-> 姝ｅ垯鍖归厤宸ュ叿
    tl = "\n".join([f"- {t['function']['name']}: {t['function']['description']}" for t in tools])
    fallback_msgs = [{"role": "system", "content": SYSTEM_PROMPT + "\n\n宸ュ叿鍒楄〃:\n" + tl}]
    fallback_msgs.extend(messages)
    fallback_msgs.append({"role": "user", "content": '璇烽€夋嫨宸ュ叿,杩斿洖JSON: {"tool":"宸ュ叿鍚?,"reason":"鍘熷洜"}'})
    
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
    
    return {"fallback": True, "choices": [{"message": {"content": "閫夋嫨宸ュ叿澶辫触"}}]}

# ===== 宸ュ叿鎵ц =====
async def execute_tool(name: str, params: dict) -> dict:
    """鎵ц宸ュ叿骞惰繑鍥炵粨鏋?""
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
                return {"success": True, "data": r.json() if r.status_code==200 else {"error":"API涓嶅彲鐢?}}
        if name == "docker_status":
            import subprocess
            r = subprocess.run(["docker","ps","--format","{{.Names}} {{.Status}}"], capture_output=True, text=True, timeout=10)
            return {"success": True, "data": {"containers": r.stdout.strip().split("\n")[:10]}}
        if name == "server_cleanup":
            import subprocess, gc
            gc.collect()
            subprocess.run(["docker","system","prune","-f"], capture_output=True, timeout=30)
            return {"success": True, "data": {"message": "鍐呭瓨宸查噴鏀撅紝Docker缂撳瓨宸叉竻鐞?}}
        
        # 閫氱敤宸ュ叿鎵ц
        tool = registry.get(name)
        if tool:
            result = await tool.execute(params)
            return {"success": True, "data": result if result else {}}
        return {"success": False, "error": f"宸ュ叿 {name} 鏈壘鍒?}
    except Exception as e:
        return {"success": False, "error": str(e)[:200]}

# ===== RAG涓婁笅鏂?=====
async def _get_context(message: str) -> str:
    """鑾峰彇鐩稿叧鐭ヨ瘑"""
    try:
        ctx = await VectorMemory.search(message, top_k=3)
        if ctx:
            return "鐩稿叧鐭ヨ瘑:\n" + "\n".join([c.get("text","")[:200] for c in ctx])
    except Exception:
        pass
    return ""

# ===== 涓籆hat绔偣 (Function Calling) =====
@router.post("/chat")
async def agent_chat(req: ChatRequest, _=Depends(verify_token)):
    """AI瀵硅瘽 - 鍘熺敓Function Calling"""
    rag_ctx = await _get_context(req.message)
    system_content = SYSTEM_PROMPT
    if rag_ctx:
        system_content += "\n\n" + rag_ctx
    
    messages = [{"role": "system", "content": system_content}]
    if req.history:
        messages.extend(req.history[-20:])  # 鏈€杩?0鏉″巻鍙?
    messages.append({"role": "user", "content": req.message})
    
    result = await call_ai_with_tools(messages, req.model)
    
    # 澶勭悊Function Calling鍝嶅簲
    if not result.get("fallback"):
        choice = result.get("choices", [{}])[0]
        msg = choice.get("message", {})
        tool_calls = msg.get("tool_calls", [])
        
        if tool_calls:
            # AI閫夋嫨浜嗗伐鍏?
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
                return {"response": f"鉀?L4椋庨櫓鎿嶄綔宸查樆姝? {tool_name}", "tool": tool_name, "risk": "L4"}
            
            exec_result = await execute_tool(tool_name, tool_args)
            
            # 灏嗙粨鏋滃弽棣堢粰AI鐢熸垚鑷劧璇█鍥炲
            messages.append({"role": "assistant", "content": None, "tool_calls": tool_calls})
            messages.append({"role": "tool", "tool_call_id": tc.get("id",""), "content": json.dumps(exec_result, ensure_ascii=False)})
            
            final = await call_ai_with_tools(messages, req.model)
            ai_text = final.get("choices",[{}])[0].get("message",{}).get("content", "鎵ц瀹屾垚")
            
            # 璁板繂瀛樺偍
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
            # AI鐩存帴鏂囨湰鍥炲
            ai_text = msg.get("content", "")
            try:
                DigitalLifeform.remember_conversation(req.message, ai_text[:300])
            except Exception:
                pass
            return {"response": ai_text, "tool": None, "risk": "L1", "mode": state.mode}
    
    # Fallback: 鏃ф牸寮?
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
        ai_text = f"鎵ц {tool_name}: " + json.dumps(exec_result.get("data",{}), ensure_ascii=False)[:500]
    
    return {"response": ai_text or "宸叉敹鍒?姝ｅ湪澶勭悊...", "tool": tool_name, "risk": "L1", "mode": state.mode}

# ===== 娴佸紡瀵硅瘽 =====
@router.post("/chat/stream")
async def agent_chat_stream(req: ChatRequest, _=Depends(verify_token)):
    """娴佸紡SSE瀵硅瘽"""
    async def generate():
        try:
            result = await agent_chat(req)
            yield f"data: {json.dumps(result, ensure_ascii=False)}\n\n"
            yield "data: [DONE]\n\n"
        except Exception as e:
            yield f"data: {json.dumps({'error': str(e)}, ensure_ascii=False)}\n\n"
    return StreamingResponse(generate(), media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"})

# ===== 宸插璇濆巻鍙?=====
_chat_histories = {}  # user_id -> [messages]

@router.post("/chat/history")
async def save_chat_history(req: dict, _=Depends(verify_token)):
    """淇濆瓨瀵硅瘽鍘嗗彶"""
    uid = req.get("user_id", "default")
    _chat_histories[uid] = req.get("messages", [])[-100:]
    state._data[f"chat_history_{uid}"] = _chat_histories[uid]
    state._save()
    return {"ok": True, "count": len(_chat_histories[uid])}

@router.get("/chat/history")
async def load_chat_history(user_id: str = Query("default"), _=Depends(verify_token)):
    """鍔犺浇瀵硅瘽鍘嗗彶"""
    return {"messages": state._data.get(f"chat_history_{user_id}", [])[-50:]}

@router.delete("/chat/history")
async def clear_chat_history(user_id: str = Query("default"), _=Depends(verify_token)):
    """娓呴櫎瀵硅瘽鍘嗗彶"""
    state._data.pop(f"chat_history_{user_id}", None)
    state._save()
    return {"ok": True}

# ===== 杈呭姪绔偣 =====
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
    return {"ok": False, "error": "鏈壘鍒拌浠诲姟"}

@router.post("/handover")
async def agent_handover(req: HandoverRequest, _=Depends(verify_token)):
    state.mode = "human_control"
    return {"ok": True, "mode": "human_control", "reason": req.reason}
