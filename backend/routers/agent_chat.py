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

@router.post("/handover")
async def agent_handover(req: HandoverRequest, _=Depends(verify_token)):
    state.mode = "human_control"
    return {"ok": True, "mode": "human_control", "reason": req.reason}
