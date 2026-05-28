"""Agent Chat API — AI 对话路由 v2: Claude + DeepSeek + Ollama + 302AI 多模型"""
import asyncio, httpx, json, re, os
from datetime import datetime
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from auth import verify_token
from state import state
from risk import handle_risk
from tools.registry import registry
from digital_lifeform import DigitalLifeform
from tools.vector_memory import VectorMemory
from routers.knowledge_router import get_rag_context
from config import MALL_BASE_URL, CLAUDE_API_KEY, CLAUDE_MODEL, OPENAI_BASE_URL

router = APIRouter(prefix="/agent", tags=["Agent"])

class ChatRequest(BaseModel):
    message: str

class ConfirmRequest(BaseModel):
    taskId: str
    approved: bool

class HandoverRequest(BaseModel):
    reason: str = ""

SYSTEM_PROMPT = """Friday AI OS: server/Docker/Nginx/site/DB/mall/customer/rotation/scraper/virtual/alert/approval/evolution.
Rule: 1)Understand intent 2)Select tool 3)Judge risk 4)L1 auto L3 confirm L4 block. Reply in Chinese."""

# 多模型配置
OLLAMA_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "qwen2.5:7b")
DEEPSEEK_KEY = os.getenv("DEEPSEEK_API_KEY", "")
OPENAI_KEY = os.getenv("OPENAI_API_KEY", "")
_API_URL = OPENAI_BASE_URL or "https://api.openai.com/v1"

# 内置回复引擎（无API Key时使用）
_BUILTIN_RESPONSES = {
    "你好": "✨ 你好！我是 **Friday AI OS** — 你的智能运维助手。\n\n📌 **左侧面板**可查看所有65+工具，点击即可直接执行！",
    "你是谁": "🤖 我是 **Friday AI OS**，集成了 65+ 真实工具的智能运维系统。\n\n💡 直接在左侧点击任意工具即可执行，或在输入框输入指令！",
}

async def _builtin_reply(message: str) -> str:
    """内置回复引擎，不需要任何 API Key"""
    msg = message.lower().strip()
    for keyword, reply in _BUILTIN_RESPONSES.items():
        if keyword in msg:
            return reply
    if any(w in msg for w in ["你好", "hi", "hello", "嗨"]):
        return _BUILTIN_RESPONSES["你好"]
    if any(w in msg for w in ["docker", "容器"]):
        return "🐳 **Docker 管理**\n\n查看容器/日志/重启，点击左侧 `docker` 分类下的工具直接执行！"
    if any(w in msg for w in ["服务", "cpu", "内存", "磁盘", "硬盘"]):
        return "📊 **服务器监控**\n\nCPU/内存/磁盘/进程，点击左侧 `server` 分类下的工具直接执行！"
    if any(w in msg for w in ["商城", "订单", "商品"]):
        return "🏪 **商城管理**（142 接口已整合）\n\n商品/订单/客服/财务/营销，点击左侧工具直接执行！"
    if any(w in msg for w in ["轮值", "域名", "rotation"]):
        return "🌐 **企业级域名轮值**\n\n健康检测/自动切换/SSL，点击左侧 `rotation` 分类下的工具直接执行！"
    if any(w in msg for w in ["nginx", "站点"]):
        return "🔧 **Nginx 管理**\n\n状态/配置/reload，点击左侧 `nginx` 分类下的工具直接执行！"
    if any(w in msg for w in ["ssl", "证书"]):
        return "🔒 **SSL 证书管理**\n\n签发/续签/状态查询，点击左侧 `ssl` 分类下的工具直接执行！"
    if any(w in msg for w in ["安全", "权限", "审批"]):
        return "🛡️ **安全防护系统**\n\n模式切换/审批/急救切断，点击左侧 `security` 分类下的工具直接执行！"
    if any(w in msg for w in ["帮助", "help", "功能", "可以"]):
        return "📋 **可用指令**\n\n输入自然语言指令，或点击左侧 65+ 工具直接执行！"
    return f"收到消息：{message}\n\n当前无 API Key 时使用内置回复引擎。\n如已配置 DeepSeek/302AI/Claude 密钥，自动启用 AI 对话。"

async def call_ai(messages, model=None):
    """模型选择优先级：Ollama > DeepSeek > 302AI(OpenAI兼容) > Claude"""
    model = model or CLAUDE_MODEL
    results = []
    # 1. Ollama 本地模型
    try:
        async with httpx.AsyncClient(timeout=60) as c:
            ollama_messages = []
            for m in messages:
                if m["role"] == "system":
                    ollama_messages.append({"role": "system", "content": m["content"]})
                else:
                    ollama_messages.append({"role": "user", "content": m["content"]})
            r = await c.post(f"{OLLAMA_URL}/api/chat",
                json={"model": OLLAMA_MODEL, "messages": ollama_messages, "stream": False})
            if r.status_code == 200:
                text = r.json().get("message", {}).get("content", "")
                if text:
                    print(f"[AI] Ollama ({OLLAMA_MODEL}) 回复成功")
                    return text
    except Exception as e:
        results.append(f"Ollama: {str(e)[:50]}")

    # 2. DeepSeek
    if DEEPSEEK_KEY:
        try:
            async with httpx.AsyncClient(timeout=30) as c:
                r = await c.post("https://api.deepseek.com/v1/chat/completions",
                    headers={"Authorization": f"Bearer {DEEPSEEK_KEY}", "Content-Type": "application/json"},
                    json={"model": "deepseek-chat", "messages": messages, "max_tokens": 1024})
                if r.status_code == 200:
                    print("[AI] DeepSeek 回复成功")
                    return r.json()["choices"][0]["message"]["content"]
        except Exception as e:
            results.append(f"DeepSeek: {str(e)[:50]}")

    # 3. Claude
    if CLAUDE_API_KEY:
        try:
            async with httpx.AsyncClient(timeout=30) as c:
                r = await c.post("https://api.anthropic.com/v1/messages",
                    headers={"x-api-key": CLAUDE_API_KEY, "anthropic-version": "2023-06-01", "content-type": "application/json"},
                    json={"model": model, "max_tokens": 1024, "system": messages[0]["content"],
                          "messages": [m for m in messages if m["role"] != "system"]})
                if r.status_code == 200:
                    print("[AI] Claude 回复成功")
                    return r.json()["content"][0]["text"]
        except Exception as e:
            results.append(f"Claude: {str(e)[:50]}")

    # 4. 302AI / OpenAI 兼容接口
    if OPENAI_KEY:
        try:
            async with httpx.AsyncClient(timeout=30) as c:
                r = await c.post(f"{_API_URL}/chat/completions",
                    headers={"Authorization": f"Bearer {OPENAI_KEY}", "Content-Type": "application/json"},
                    json={"model": "gpt-4o-mini", "messages": messages, "max_tokens": 1024})
                if r.status_code == 200:
                    print("[AI] OpenAI/302AI 回复成功")
                    return r.json()["choices"][0]["message"]["content"]
        except Exception as e:
            results.append(f"OpenAI: {str(e)[:50]}")

    if results:
        print(f"[AI] 所有模型均失败: {'; '.join(results)}")
    return None

async def execute_tool(tool_name, params=None):
    """统一通过 registry 执行所有工具"""
    from tools.registry import registry as _reg
    params = params or {}
    result = await _reg.execute(tool_name, **params)
    return {
        "tool": tool_name,
        "success": result.get("ok", False),
        "data": result.get("result"),
        "error": result.get("error", ""),
    }

async def _match(msg):
    """关键词匹配工具"""
    msg = msg.lower()
    tools = registry.list_all()
    # VECMEM: search vector memory for relevant context
    _vec = await VectorMemory.semantic_search(msg, 5) or []
    _mctx = ""
    if _vec:
        _mctx = chr(10).join(['[H#'+str(i+1)+'] '+m.get('text','')[:200] for i,m in enumerate(_vec)])
    _rctx = ""
    try:
        _rc = await get_rag_context(q=msg, max_chars=1500, _=None)
        if _rc and _rc.get('context'): _rctx = _rc['context'][:1500]
    except: pass
    _extra = ""
    if _mctx: _extra += chr(10)+chr(91)+chr(72)+chr(105)+chr(115)+chr(116)+chr(111)+chr(114)+chr(121)+chr(77)+chr(101)+chr(109)+chr(93)+chr(10) + _mctx
    if _rctx: _extra += chr(10)+chr(91)+chr(75)+chr(110)+chr(111)+chr(119)+chr(108)+chr(101)+chr(100)+chr(103)+chr(101)+chr(66)+chr(97)+chr(115)+chr(101)+chr(93)+chr(10) + _rctx
    for t in tools:
        if t.name and t.name.lower() in msg:
            return t.name, t.risk_level
    if any(w in msg for w in ["服务", "内存", "cpu"]):
        return "server.metrics", "L1"
    if any(w in msg for w in ["轮值", "域名"]):
        return "rotation.domains", "L1"
    return "chat.respond", "L1"

@router.get("/models/status")
async def model_status():
    """AI模型状态查询"""
    status = {"ollama": False, "deepseek": bool(DEEPSEEK_KEY), "claude": bool(CLAUDE_API_KEY), "openai": bool(OPENAI_KEY)}
    try:
        async with httpx.AsyncClient(timeout=3) as c:
            r = await c.get(f"{OLLAMA_URL}/api/tags")
            if r.status_code == 200:
                models = r.json().get("models", [])
                status["ollama"] = True
                status["ollama_models"] = [m["name"] for m in models]
    except:
        pass
    return {"ok": True, "engines": status}

@router.post("/chat")
async def agent_chat(req: ChatRequest, _=Depends(verify_token)):
    """AI对话主入口"""
    tools = registry.list_all()
    tl = "\n".join([f"- {t.name}: {t.display_name} [{t.risk_level}]" for t in tools[:50]])
    msgs = [
        {"role": "system", "content": SYSTEM_PROMPT + "\n\nTools:\n" + tl},
        {"role": "user", "content": f"User: {req.message}\nReply JSON: {\"intent\":\"...\",\"tool\":\"...\",\"reasoning\":\"...\",\"risk\":\"L1\"}"}
    ]
    ai = await call_ai(msgs)
    tn, risk = None, "L1"
    intent = req.message[:50]
    reason = ""
    if ai:
        try:
            m = re.search(r'\{[^}]+\}', ai.strip())
            if m:
                p = json.loads(m.group())
                tn = p.get("tool")
                risk = p.get("risk", "L1")
                intent = p.get("intent", intent)
                reason = p.get("reasoning", "")
        except:
            pass
    if not tn:
        tn, risk = await _match(req.message)
    td = registry.get(tn)
    disp = td.display_name if td else tn
    await handle_risk(risk, disp, req.message[:100])
    steps = [
        {"step": 1, "name": f"意图: {intent}", "status": "done"},
        {"step": 2, "name": f"工具: {disp}", "status": "done"},
        {"step": 3, "name": f"风险: {risk}", "status": "done"},
    ]
    if risk == "L4":
        return {"task_id": f"t{len(state.tasks)+1}", "response": f"⛔ 已阻止 L4 风险操作\n\n{intent}\n\n需要人工接管。",
                "steps": steps + [{"step": 4, "name": "已阻止", "status": "failed"}], "risk_level": "L4", "mode": state.mode}
    if risk == "L3":
        state.add_approval(f"t{len(state.tasks)+1}", "L3", disp, req.message[:200])
        return {"task_id": f"t{len(state.tasks)+1}", "response": f"✅ 已提交审批\n\n{intent}\n\n工具: {disp}\n风险: L3，等待审批。",
                "steps": steps + [{"step": 4, "name": "等待审批", "status": "pending"}], "risk_level": "L3", "need_confirm": True, "mode": state.mode}
    steps.append({"step": 4, "name": f"执行: {disp}", "status": "running"})
    er = await execute_tool(tn, {"message": req.message})
    if er["success"]:
        steps.append({"step": 5, "name": "完成", "status": "done"})
        ds = json.dumps(er.get("data", {}), ensure_ascii=False, indent=2)[:1000]
        resp = f"**{disp}** 执行成功\n\n```\n{ds}\n```"
        if reason:
            resp = reason + "\n\n" + resp
    else:
        steps.append({"step": 5, "name": "失败", "status": "failed"})
        resp = f"**{disp}** 执行失败\n\n{er.get('error', '未知错误')}"
    state.add_task(name=disp, risk=risk, status="done" if er["success"] else "failed")
    try:
        DigitalLifeform.remember_conversation(req.message, resp[:300])
    except:
        pass
    try:
        asyncio.ensure_future(VectorMemory.remember(resp[:300], {'type':'ai','source':'chat'}))
    except:
        pass
    try:
        from tools.vector_memory import vector_memory
        vector_memory.remember("用户: " + req.message[:300], {"role": "user", "tool": tn})
        vector_memory.remember("AI: " + resp[:300], {"role": "ai", "tool": tn})
    except:
        pass
    return {"task_id": f"t{len(state.tasks)}", "response": resp, "steps": steps, "risk_level": risk, "mode": state.mode}


@router.get("/tools")
async def list_tools(_=Depends(verify_token)):
    """列出所有可用工具"""
    ts = registry.list_all()
    return {"tools": [{"name": t.name, "display_name": t.display_name, "description": t.description,
                       "risk_level": t.risk_level, "category": t.category} for t in ts], "count": len(ts)}

@router.get("/tasks")
async def list_tasks(_=Depends(verify_token)):
    """列出任务和待审批"""
    return {"tasks": state.tasks[-50:], "pending": len(state.pending_approvals)}

@router.post("/confirm")
async def confirm_task(req: ConfirmRequest, _=Depends(verify_token)):
    """审批确认/拒绝"""
    for a in state.pending_approvals:
        if a.get("id") == req.taskId:
            a["status"] = "approved" if req.approved else "rejected"
            state.approval_history.append({**a, "result": a["status"]})
            state.pending_approvals.remove(a)
            return {"ok": True, "status": a["status"]}
    return {"ok": False, "error": "未找到该任务"}

@router.post("/handover")
async def agent_handover(req: HandoverRequest, _=Depends(verify_token)):
    """交还人工控制"""
    state.mode = "human_control"
    return {"ok": True, "mode": "human_control", "reason": req.reason}
