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

SYSTEM_PROMPT = """Friday AI OS - Claude: server/Docker/Nginx/site/DB/mall/customer/rotation/scraper/virtual/alert/approval/evolution.
Rule: 1)Understand intent 2)Select tool 3)Judge risk 4)L1 auto L3 confirm L4 block. Reply in Chinese."""

async def call_ai(messages, model=None):
    model = model or CLAUDE_MODEL
    if CLAUDE_API_KEY and "claude" in model.lower():
        try:
            async with httpx.AsyncClient(timeout=30) as c:
                r = await c.post("https://api.anthropic.com/v1/messages",
                    headers={"x-api-key":CLAUDE_API_KEY,"anthropic-version":"2023-06-01","content-type":"application/json"},
                    json={"model":model,"max_tokens":1024,"system":messages[0]["content"],"messages":[m for m in messages if m["role"]!="system"]})
                if r.status_code==200:
                    return r.json()["content"][0]["text"]
        except Exception as e:
            print(f"[AI] Claude fail: {e}")
    ds_key = os.getenv("DEEPSEEK_API_KEY","")
    if ds_key:
        try:
            async with httpx.AsyncClient(timeout=30) as c:
                r = await c.post("https://api.deepseek.com/v1/chat/completions",
                    headers={"Authorization":f"Bearer {ds_key}","Content-Type":"application/json"},
                    json={"model":"deepseek-chat","messages":messages,"max_tokens":1024})
                if r.status_code==200:
                    return r.json()["choices"][0]["message"]["content"]
        except: pass
    return None

async def execute_tool(tool_name, params=None):
    params = params or {}
    res = {"tool":tool_name,"success":False,"data":None,"error":""}
    try:
        if tool_name=="server.status":
            import psutil as _ps
            res["data"]={"cpu":f"{_ps.cpu_percent(0.3)}%","mem":f"{_ps.virtual_memory().percent}%","disk":f"{_ps.disk_usage('/').percent}%"}
            res["success"]=True
        elif tool_name=="docker.list":
            from executor import execute
            r=await execute("docker ps --format '{{.Names}}: {{.Status}}' 2>/dev/null || echo no-docker")
            res["data"]={"containers":r["stdout"].strip()};res["success"]=True
        elif tool_name=="nginx.status":
            from executor import execute
            r=await execute("pgrep -a nginx 2>/dev/null || echo unknown")
            res["data"]={"nginx":r["stdout"][:200]};res["success"]=True
        elif tool_name=="site.check":
            u=params.get("url",MALL_BASE_URL)
            async with httpx.AsyncClient(timeout=10,follow_redirects=True) as c:
                r=await c.get(u if "http" in u else f"https://{u}")
                res["data"]={"url":u,"status":r.status_code,"ok":r.status_code<500};res["success"]=True
        elif tool_name=="backup.list":
            from routers.rollback_center import _load_backups
            bu=_load_backups();res["data"]={"backups":bu[-10:],"count":len(bu)};res["success"]=True
        elif tool_name=="system.mode":
            res["data"]={"mode":state.mode,"pending":len(state.pending_approvals)};res["success"]=True
        elif tool_name=="rotation.check":
            ds=state._data.get("rotation_domains",[])
            res["data"]={"domains":[d["domain"] for d in ds[:10]],"count":len(ds)};res["success"]=True
        elif tool_name=="mall.products":
            async with httpx.AsyncClient(timeout=10) as c:
                r=await c.get(f"{MALL_BASE_URL}/api/products?page=1&size=10")
                res["data"]=r.json() if r.status_code<500 else {};res["success"]=r.status_code<500
        elif tool_name=="evolution.report":
            from tools.evolution import EvolutionEngine
            res["data"]=EvolutionEngine.evolve_report();res["success"]=True
        elif tool_name=="mallbrain.scan":
            from tools.autopilot_mall import MallBrain
            ps=await MallBrain.scan_products()
            res["data"]={"total":len(ps),"hot":sum(1 for p in ps if p.status=="hot"),"dead":sum(1 for p in ps if p.status=="dead")};res["success"]=True
        elif tool_name=="inspector.run":
            async with httpx.AsyncClient(timeout=10) as c:
                r=await c.get(f"{MALL_BASE_URL}/agent/health")
                res["data"]={"mall":"ok" if r.status_code==200 else "down"};res["success"]=True
        elif "playwright" in tool_name:
            from agents.playwright_agent import PlaywrightAgent
            if tool_name == "playwright.screenshot":
                er=await PlaywrightAgent.screenshot(params.get("url",MALL_BASE_URL))
                res["data"]=er;res["success"]=er.get("ok",False)
            elif tool_name == "playwright.scrape":
                er=await PlaywrightAgent.scrape_page(params.get("url",MALL_BASE_URL))
                res["data"]=er;res["success"]=er.get("ok",False)
            elif tool_name == "playwright.search":
                er=await PlaywrightAgent.search_and_scrape(params.get("keyword",""),params.get("site","ebay"))
                res["data"]=er;res["success"]=er.get("ok",False)
            elif tool_name == "playwright.form":
                res["data"]={"status":"pending_approval"};res["success"]=True
        else:
            res["data"]={"mode":state.mode,"tasks":len(state.tasks)};res["success"]=True
    except Exception as e:
        res["error"]=str(e)
    return res

INTENT_RULES=[
    (["server","cpu","mem","disk"],"server.status","L1"),
    (["docker","container"],"docker.list","L1"),
    (["nginx"],"nginx.status","L1"),
    (["site","check","down"],"site.check","L1"),
    (["mode","system"],"system.mode","L1"),
    (["backup"],"backup.list","L1"),
    (["rotation","domain"],"rotation.check","L1"),
    (["product","mall"],"mall.products","L1"),
    (["evolution","success"],"evolution.report","L1"),
    (["scan","health","hot","dead"],"mallbrain.scan","L1"),
    (["inspect","patrol"],"inspector.run","L1"),
]

def _match(msg):
    m=msg.lower()
    for kw,t,r in INTENT_RULES:
        for k in kw:
            if k in m: return t,r
    return "server.status","L1"

@router.post("/chat")
async def agent_chat(req: ChatRequest, _=Depends(verify_token)):
    tools=registry.list_all()
    tl="\n".join([f"- {t.name}: {t.display_name} [{t.risk_level}]" for t in tools[:50]])
    msgs=[{"role":"system","content":SYSTEM_PROMPT+"\n\nTools:\n"+tl},{"role":"user","content":f"User: {req.message}\nReply JSON: {{\"intent\":\"...\",\"tool\":\"...\",\"reasoning\":\"...\",\"risk\":\"L1\"}}"}]
    ai=await call_ai(msgs)
    tn,risk=None,"L1"
    intent=req.message[:50];reason=""
    if ai:
        try:
            m=re.search(r'\{[^}]+\}',ai.strip())
            if m:
                p=json.loads(m.group())
                tn=p.get("tool");risk=p.get("risk","L1");intent=p.get("intent",intent);reason=p.get("reasoning","")
        except: pass
    if not tn: tn,risk=_match(req.message)
    td=registry.get(tn);disp=td.display_name if td else tn
    rr=await handle_risk(risk,disp,req.message[:100])
    steps=[{"step":1,"name":f"Intent: {intent}","status":"done"},{"step":2,"name":f"Tool: {disp}","status":"done"},{"step":3,"name":f"Risk: {risk}","status":"done"}]
    if risk=="L4":
        return {"task_id":f"t{len(state.tasks)+1}","response":f"BLOCKED L4\n\n{intent}\n\nRisk L4 - manual takeover forced.","steps":steps+[{"step":4,"name":"Blocked","status":"failed"}],"risk_level":"L4","mode":state.mode}
    if risk=="L3":
        state.add_approval(f"t{len(state.tasks)+1}","L3",disp,req.message[:200])
        return {"task_id":f"t{len(state.tasks)+1}","response":f"APPROVAL NEEDED\n\n{intent}\n\nTool: {disp}\nRisk: L3\n\nSubmitted for approval.","steps":steps+[{"step":4,"name":"Wait approval","status":"pending"}],"risk_level":"L3","need_confirm":True,"mode":state.mode}
    steps.append({"step":4,"name":f"Run: {disp}","status":"running"})
    er=await execute_tool(tn,{"message":req.message})
    if er["success"]:
        steps.append({"step":5,"name":"Done","status":"done"})
        ds=json.dumps(er.get("data",{}),ensure_ascii=False,indent=2)[:1000]
        resp=f"**{disp}** Done\n\n```\n{ds}\n```"
        if reason: resp=reason+"\n\n"+resp
    else:
        steps.append({"step":5,"name":"Failed","status":"failed"})
        resp=f"**{disp}** Failed\n\n{er.get('error','unknown')}"
    state.add_task(name=disp,risk=risk,status="done" if er["success"] else "failed")
    # save dialogue memory to digital lifeform
    try:
        DigitalLifeform.remember_conversation(req.message, resp[:300])
    except: pass
    return {"task_id":f"t{len(state.tasks)}","response":resp,"steps":steps,"risk_level":risk,"mode":state.mode}

@router.get("/tools")
async def list_tools(_=Depends(verify_token)):
    ts=registry.list_all()
    return {"tools":[{"name":t.name,"display_name":t.display_name,"description":t.description,"risk_level":t.risk_level,"category":t.category} for t in ts],"count":len(ts)}

@router.get("/tasks")
async def list_tasks(_=Depends(verify_token)):
    await handle_risk("L1","tasks")
    return {"tasks":state.tasks[-50:],"count":len(state.tasks)}

@router.get("/tasks/{task_id}")
async def task_detail(task_id:str,_=Depends(verify_token)):
    for t in state.tasks:
        if t["id"]==task_id: return t
    return {"error":"not found"}

@router.post("/confirm")
async def confirm_task(req:ConfirmRequest,_=Depends(verify_token)):
    r=state.decide_approval(req.taskId,req.approved)
    return {"result":"ok" if r else "not found","detail":r}

@router.post("/handover")
async def handover(req:HandoverRequest,_=Depends(verify_token)):
    state.mode="human_control"
    state.add_emergency("human_control",req.reason or "user takeover")
    return {"mode":"human_control"}

@router.post("/resume")
async def resume_ai(_=Depends(verify_token)):
    state.mode="ai_control"
    state.add_emergency("ai_control","resume AI")
    return {"mode":"ai_control"}
