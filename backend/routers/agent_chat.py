"""Agent Chat API 閳?婢舵碍膩閸ㄥ娅ら懗鍊熺熅閻?v2: Claude + DeepSeek + Ollama 娑撳绱╅幙?""
import httpx, json, re, os
from datetime import datetime
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from auth import verify_token
from state import state
from risk import handle_risk
from tools.registry import registry
from digital_lifeform import DigitalLifeform
from config import MALL_BASE_URL, CLAUDE_API_KEY, CLAUDE_MODEL

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

# ===== 濡€崇€风捄顖滄暠 =====
OLLAMA_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "qwen2.5:7b")
DEEPSEEK_KEY = os.getenv("DEEPSEEK_API_KEY", "")
OPENAI_KEY = os.getenv("OPENAI_API_KEY", "")

async def call_ai(messages, model=None):
    """婢舵碍膩閸ㄥ娅ら懗鍊熺熅閻? Ollama > DeepSeek > Claude > OpenAI (all keys empty = keyword fallback)"""
    # 所有AI密钥为空时返回None，让主逻辑走关键词匹配
    if not any([os.getenv("DEEPSEEK_API_KEY"), os.getenv("OPENAI_API_KEY"), CLAUDE_API_KEY]):
        try:
            async with httpx.AsyncClient(timeout=5) as c:
                r = await c.get(f"{OLLAMA_URL}/api/tags")
                if r.status_code != 200:
                    return None  # Ollama也不可用，走关键词匹配
        except:
            return None  # 所有AI不可用
    """婢舵碍膩閸ㄥ娅ら懗鍊熺熅閻? Ollama > DeepSeek > Claude > OpenAI"""
    model = model or CLAUDE_MODEL
    results = []

    # 1. Ollama 本地模型(免费优先)
    try:
        async with httpx.AsyncClient(timeout=60) as c:
            # 閺嬪嫬缂?Ollama 閺嶇厧绱￠惃鍕Х閹?            ollama_messages = []
            for m in messages:
                if m["role"] == "system":
                    ollama_messages.append({"role": "system", "content": m["content"]})
                else:
                    ollama_messages.append({"role": "user", "content": m["content"]})
            r = await c.post(f"{OLLAMA_URL}/api/chat",
                json={"model": OLLAMA_MODEL, "messages": ollama_messages, "stream": False})
            if r.status_code == 200:
                data = r.json()
                text = data.get("message", {}).get("content", "")
                if text:
                    print(f"[AI] Ollama ({OLLAMA_MODEL}) 閸濆秴绨查幋鎰")
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
                    print("[AI] DeepSeek 閸濆秴绨查幋鎰")
                    return r.json()["choices"][0]["message"]["content"]
        except Exception as e:
            results.append(f"DeepSeek: {str(e)[:50]}")

    # 3. Claude
    if CLAUDE_API_KEY and "claude" in model.lower():
        try:
            async with httpx.AsyncClient(timeout=30) as c:
                r = await c.post("https://api.anthropic.com/v1/messages",
                    headers={"x-api-key": CLAUDE_API_KEY, "anthropic-version": "2023-06-01", "content-type": "application/json"},
                    json={"model": model, "max_tokens": 1024, "system": messages[0]["content"],
                          "messages": [m for m in messages if m["role"] != "system"]})
                if r.status_code == 200:
                    print("[AI] Claude 閸濆秴绨查幋鎰")
                    return r.json()["content"][0]["text"]
        except Exception as e:
            results.append(f"Claude: {str(e)[:50]}")

    # 4. OpenAI
    if OPENAI_KEY:
        try:
            async with httpx.AsyncClient(timeout=30) as c:
                r = await c.post("https://api.openai.com/v1/chat/completions",
                    headers={"Authorization": f"Bearer {OPENAI_KEY}", "Content-Type": "application/json"},
                    json={"model": "gpt-4o-mini", "messages": messages, "max_tokens": 1024})
                if r.status_code == 200:
                    print("[AI] OpenAI 閸濆秴绨查幋鎰")
                    return r.json()["choices"][0]["message"]["content"]
        except Exception as e:
            results.append(f"OpenAI: {str(e)[:50]}")

    if results:
        print(f"[AI] 閹碘偓閺堝膩閸ㄥ銇戠拹? {'; '.join(results)}")
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

@router.get("/models/status")
async def model_status():
    """濡偓閺屻儱鎮囧Ο鈥崇€烽崣顖滄暏閻樿埖鈧?""
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
    return {"ok": True, "engines": status, "current": OLLAMA_MODEL if status["ollama"] else ("deepseek" if status["deepseek"] else ("claude" if status["claude"] else "keyword"))}

@router.post("/chat")
async def agent_chat(req: ChatRequest, _=Depends(verify_token)):
    tools = registry.list_all()
    tl = "\n".join([f"- {t.name}: {t.display_name} [{t.risk_level}]" for t in tools[:50]])
    msgs = [
        {"role": "system", "content": SYSTEM_PROMPT + "\n\nTools:\n" + tl},
        {"role": "user", "content": f"User: {req.message}\nReply JSON: {{\"intent\":\"...\",\"tool\":\"...\",\"reasoning\":\"...\",\"risk\":\"L1\"}}"}
    ]
    ai = await call_ai(msgs)
    tn, risk = None, "L1"
    intent = req.message[:50]; reason = ""
    if ai:
        try:
            m = re.search(r'\{[^}]+\}', ai.strip())
            if m:
                p = json.loads(m.group())
                tn = p.get("tool"); risk = p.get("risk", "L1")
                intent = p.get("intent", intent); reason = p.get("reasoning", "")
        except:
            pass
    if not tn: tn, risk = _match(req.message)
    td = registry.get(tn); disp = td.display_name if td else tn
    rr = await handle_risk(risk, disp, req.message[:100])
    steps = [
        {"step": 1, "name": f"Intent: {intent}", "status": "done"},
        {"step": 2, "name": f"Tool: {disp}", "status": "done"},
        {"step": 3, "name": f"Risk: {risk}", "status": "done"},
    ]
    if risk == "L4":
        return {"task_id": f"t{len(state.tasks)+1}", "response": f"BLOCKED L4\n\n{intent}\n\nRisk L4 - manual takeover forced.",
                "steps": steps + [{"step": 4, "name": "Blocked", "status": "failed"}], "risk_level": "L4", "mode": state.mode}
    if risk == "L3":
        state.add_approval(f"t{len(state.tasks)+1}", "L3", disp, req.message[:200])
        return {"task_id": f"t{len(state.tasks)+1}", "response": f"APPROVAL NEEDED\n\n{intent}\n\nTool: {disp}\nRisk: L3\n\nSubmitted for approval.",
                "steps": steps + [{"step": 4, "name": "Wait approval", "status": "pending"}], "risk_level": "L3", "need_confirm": True, "mode": state.mode}
    steps.append({"step": 4, "name": f"Run: {disp}", "status": "running"})
    er = await execute_tool(tn, {"message": req.message})
    if er["success"]:
        steps.append({"step": 5, "name": "Done", "status": "done"})
        ds = json.dumps(er.get("data", {}), ensure_ascii=False, indent=2)[:1000]
        resp = f"**{disp}** Done\n\n```\n{ds}\n```"
        if reason: resp = reason + "\n\n" + resp
    else:
        steps.append({"step": 5, "name": "Failed", "status": "failed"})
        resp = f"**{disp}** Failed\n\n{er.get('error', 'unknown')}"
    state.add_task(name=disp, risk=risk, status="done" if er["success"] else "failed")
    # 閹镐椒绠欓崠鏍ь嚠鐠囨繆顔囪箛?    try:
        DigitalLifeform.remember_conversation(req.message, resp[:300])
    try:
        from tools.vector_memory import vector_memory
        vector_memory.remember("用户: " + req.message[:300], {"role": "user", "tool": tn})
        vector_memory.remember("AI: " + resp[:300], {"role": "ai", "tool": tn})
    except: pass
    except:
        pass
    return {"task_id": f"t{len(state.tasks)}", "response": resp, "steps": steps, "risk_level": risk, "mode": state.mode}

@router.get("/tools")
async def list_tools(_=Depends(verify_token)):
    ts = registry.list_all()
    return {"tools": [{"name": t.name, "display_name": t.display_name, "description": t.description,
                       "risk_level": t.risk_level, "category": t.category} for t in ts], "count": len(ts)}

@router.get("/tasks")
async def list_tasks(_=Depends(verify_token)):
    return {"tasks": state.tasks[-50:], "pending": len(state.pending_approvals)}

@router.post("/confirm")
async def confirm_task(req: ConfirmRequest, _=Depends(verify_token)):
    for a in state.pending_approvals:
        if a.get("id") == req.taskId:
            if req.approved:
                a["status"] = "approved"
                state.approval_history.append({**a, "result": "approved"})
                state.pending_approvals.remove(a)
                return {"ok": True, "status": "approved"}
            else:
                a["status"] = "rejected"
                state.approval_history.append({**a, "result": "rejected"})
                state.pending_approvals.remove(a)
                return {"ok": True, "status": "rejected"}
    return {"ok": False, "error": "Task not found"}

@router.post("/handover")
async def agent_handover(req: HandoverRequest, _=Depends(verify_token)):
    state.mode = "human_control"
    return {"ok": True, "mode": "human_control", "reason": req.reason}


