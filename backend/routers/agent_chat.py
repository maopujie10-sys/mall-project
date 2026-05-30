"""Agent Chat API v3 -- 闂佸憡顭囬崰鎾诲极閹诲nction Calling + 闁诲海鏁搁、濠囨儊閻ｅ本濯奸柡澶庢硶缁犳捇鏌熼梹鎰樂缂佺姵鐟╁畷?""
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

# ===== 闁诲海鏁搁、濠囨儊閼恒儱顕辨慨妯虹－濡牏绱掗悪鍛？闁?(SQLite) =====
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

def create_conversation(title: str = "闂佸搫鍊瑰姗€顢氶鐐珰?, model: str = "") -> str:
    cid = uuid.uuid4().hex[:12]
    conn = _get_conv_db()
    conn.execute("INSERT INTO conversations (id,title,model,created_at,updated_at) VALUES (?,?,?,datetime('now'),datetime('now'))", (cid, title, model))
    conn.commit(); conn.close()
    return cid

# ===== 濠电偟绻濈粈浣烘椤℃┎E閻庤鎮堕崕閬嶅矗閸ф绀勯柤鎭掑劜濞?=====
async def stream_ai_response(messages: list, model: str = ""):
    """闂備緡鍋呮禒鐠穔en濠电偟绻濈粈浣烘閳╁啯浜ら柡鍌涘缁€鈧珹I闂佸憡绻傜粔瀵歌姳?""
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

# ===== 闂佹悶鍎辨晶鑺ユ櫠閺嶎厽鍋犻柛鈩冾嚧?=====
async def analyze_image(image_base64: str, question: str = "闁荤姴娲弨鍗烆嚕閹稿孩浜ら柟宄扮灱缁犲湱鈧鍠氭慨鏉懨瑰鈧幃?) -> str:
    """婵炶揪缍€濞夋洟寮妶鍥ㄥ枂闁糕剝鍑瑰鏇熶繆椤栨せ鍋撳畷鍥ｅ亾閻戣棄绀嗛柛鈩冾焽閳ь兛绮欏畷鍫曞礈瑜嶉。?""
    api_key = OPENAI_API_KEY
    if not api_key:
        return "闂佹悶鍎辨晶鑺ユ櫠閺嶎厼绀嗛柛鈩冾焽閳ь兛绮欏Λ渚€鍩€椤掑倹鍟哄〒姘ｅ亾闁告ǜ鍊楃槐鏃堟偨閸㈡欢NAI_API_KEY"
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
            return data.get("choices", [{}])[0].get("message", {}).get("content", "闂佸搫鍟版慨鐢垫兜閸洖绀嗛柛鈩冾焽閳?)
        return f"闂佹悶鍎辨晶鑺ユ櫠閺嶎厼绀嗛柛鈩冾焽閳ь剝濮ゅ鍕綇椤愩儛? {resp.status_code}"

router = APIRouter(prefix="/agent", tags=["Agent"])

class ChatRequest(BaseModel):
    message: str
    history: list[dict] = []  # 闁诲海鏁搁、濠囨儊娴犲鍌ㄩ柛鈩冾殔閽?[{role,content}]
    model: str = ""            # 闂佸湱顭堝ú銈夋偩閹灛鐔煎灳瀹曞洠鍋?

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

SYSTEM_PROMPT = """婵炶揪绲挎慨闈浳?Friday AI OS -- 闂佽桨鐒﹀姗€鎮鸿閹粙鎮㈤柨瀣婵炶揪绲鹃幐濠氭偋鐎圭姷鐤€?婵炶揪绲挎慨鐢碘偓姘ュ灲瀵灚寰勫畝鍕帣缂傚倷鑳堕崰鎰板礉閸涘瓨鍎楅柕澶堝妼閸樻挳鏌?闂佺厧鐤囨慨銈夋偂閿熺姵鍎戦悗锝庡亝缁犳盯鏌涢弬琛″亾閾忣偆褰滈梺缁橆焾閸╂牠鍩€椤戝潡妾烽柍褜鍏涢懗鍫曨敇閹间焦鍋犻柛鈩冾殕濞呭矂鏌涢埡浣瑰攭缂佽绉归幏鍐Ψ閿濆倸浜惧ù锝囨嚀閳锋棃鎮跺☉妯肩劮缂佽绉剁槐鎺斺偓娑櫳戦幆娆徝?

闂佸搫绉堕…鍫㈢紦妤ｅ啯鍤勯柦妯侯槸椤?
- 闁诲骸婀遍崑鐐差渻閸屾粌瀵查柤濮愬€楅崺鐘绘煟閳哄倸鐏﹂悽?CPU/闂佸憡鍔曢幊搴ㄦ偤?缂佹儳褰為懗璺好?缂傚倸鍟崹鍦垝?闁哄鏅滅粙鎾诲煝?
- 闂佸摜鍠庡Λ妤呮偂閸曨厾涓嶉柨娑樺閸?闁荤姳闄嶉崹鐟扮暦?闂佸摜鍠庡Λ妤呭箹?闂佹椿娼块崝宥夊春?闂佺粯銇涢弲婊呯矈?闂佽В鍋撻柕澶嗘櫆閺?
- 闂佺厧顨庢禍婊勬叏閳哄懎绀岄柡宥庡墰缁犮儳绱?Docker/Nginx/闂佺硶鏅濋崰搴ㄥ箖閺囩喐濮滄い鏂跨毞閸?婵犮垼娉涘ú锝夊船閵堝鐐婇柣鎰嚟濞?
- 闂佽桨鑳舵晶妤€鐣垫笟鈧弻宀勫炊椤掍浇鍋佹繛鎴炴尭妤犳悂宕规惔銊ュ嚑?闂佸摜鍠庡Λ妤呭箹瑜旈弻宀勫炊椤掍浇鍋?缂備焦姊婚崑娑㈠箹瑜斿畷姘跺幢濡皷鍋?闁烩剝甯掗鍛箾瀹ュ棴绱ｉ柛鏇ㄥ墰閵?

闁荤偞绋戞總鏃傛嫻閻旂厧绀勯柛鈩冾殔閻?
1. 闂佽崵鍋涘Λ婊嗩暰闂佽婢樼换鎰瑰鈧畷銉︽償閵娿垹浜惧璺侯儏椤忋儵鏌涘顒傚ⅵ闁逞屽墮閸婅鈻撻幋婵愬晠闁靛鍎卞鏃堟煙缁楁稑妫弨?
2. 婵＄偛顑呴柊锝呪枍閹捐绀嗛柛鈩冪懇閻?L1=闁诲海鎳撻ˇ顖炲矗韫囨稒鍤婃い蹇撳琚?L2=婵炶揪绲介柊锝壦夐幘缁樷挃闁冲搫瀚▓浼存煕?L3=闂傚倸娲犻崑鎾剁棯椤撗冩灕妞?L4=缂備礁鍊烽悞锕傤敆?
3. 闂佹悶鍎抽崑娑⑺囬懠顒備笉闁逞屽墮鐓ゅù锝夘棑閻熲晛鈽?闂佹椿娼块崝瀣嚈閹达箑妫?
4. 闂佸湱鐟抽崱鈺傛杸闂佸憡鑹惧ù鐑藉极閵堝鍤婃い蹇撴婵囨偣閸ヨ泛寮ㄩ柍璇茬墢閹叉挳鏁愭径濠冪彽缂傚倷鐒﹂幐濠氭倶?
5. 婵炴垶鎹侀褎鎱ㄩ埡鍛闁惧浚鍋呴弳鍫㈢磼椤栨繂鍚圭紒顔芥そ瀹曟垿濡烽妷锕€鈧?閻庢鍠栭崐鎼佹偉閸洖绫嶉悹鍝勬惈閹搞倝鏌￠崘顓熺【闁硅绱曢幏?

婵炶揪绲挎慨闈涳耿娴ｅ湱鈻旈柍褜鍓氱粙?D闂佸憡鐟崹鐢革綖鐎ｎ喖绀岄柡宥庡墴閻撯晛霉?Neural Network),闂佹椿娼块崝宥夊春濞戙垹鐭楁い鏍ㄧ懁缁ㄤ即鏌涢敂鍝勫闁活偄妫濋悰顕€寮村杈╂啰闂佹椿浜滈鍛村春鐏炵偓濯撮柣妯虹仛閻ｉ亶鏌ｅΟ鍨厫闁逞屽厸缁€浣姐亹婢舵劕绀?"""

# ===== 閻庤鎮堕崕閬嶅矗鐠恒劉鍋撶憴鍕叝缂?(OpenAI Function Calling闂佸搫绉堕崢褏妲? =====
def _build_tools():
    """闂佸搫顑呯€氼剛绱撻幘鎰佸晠闁靛鍎卞鏀昪hema"""
    tools_list = registry.list_all()[:50]
    return [{
        "type": "function",
        "function": {
            "name": t.name,
            "description": f"{t.display_name}: {t.description} [婵＄偛顑呴柊锝呪枍?{t.risk_level}]",
            "parameters": {
                "type": "object",
                "properties": {
                    "message": {"type": "string", "description": "闂佹椿娼块崝宥夊春濞戙垹鍌ㄩ柣鏂款殠濞兼绻涢幋婵堝濞寸厧鎳橀獮瀣冀瑜嶅Λ姗€鏌?}
                },
                "required": ["message"]
            }
        }
    } for t in tools_list]

# ===== 濠碘槅鍨埀顒€纾埀顒勵棑閹奉偊宕橀鍛 =====
async def call_ai_with_tools(messages, model=""):
    """闁荤姴顑呴崯浼村极椤ヮ湉濠碘槅鍨埀顒€纾埀?闂佽　鍋撴い鏍ㄧ☉閻︻噣鏌涘Ο鐓庢灁闁轰焦寮穟nction Calling"""
    tools = _build_tools()
    
    # 婵炴潙鍚嬮敋闁告ɑ楗眅epSeek(闂佺绻掗崢褔顢欓幀鐞緀nAI闂佸搫绉堕崢褏妲?
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
    
    # OpenAI闂佺绻掗崢褔顢欓幀濉扞 (302AI缂?
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
    
    # 闂佹悶鍎抽崑銈夊焵椤戣棄浜? 闂佸搫鍞查崟顓烆棔閻?-> 濠殿喗绻愮徊浠嬪垂椤栫偛绀岀憸鐗堝笒鐢磭鈧鎮堕崕閬嶅矗?
    tl = "\n".join([f"- {t['function']['name']}: {t['function']['description']}" for t in tools])
    fallback_msgs = [{"role": "system", "content": SYSTEM_PROMPT + "\n\n閻庤鎮堕崕閬嶅矗閸ф绀嗘俊銈呭閳?\n" + tl}]
    fallback_msgs.extend(messages)
    fallback_msgs.append({"role": "user", "content": '闁荤姴娲ㄩ崗姗€鍩€椤掆偓椤︽壆鈧哎鍔岄蹇涘Ψ閵夈儱绶?闁哄鏅滈弻銊ッ洪張鏈N: {"tool":"閻庤鎮堕崕閬嶅矗閸ф瑙?,"reason":"闂佸憡顭囬崰搴∶?}'})
    
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
    
    return {"fallback": True, "choices": [{"message": {"content": "闂備緡鍋勯ˇ鎵偓姘ュ妼椤斿繘濡烽妷銉ョ樊婵犮垺鍎肩划鍓ф喆?}}]}

# ===== 閻庤鎮堕崕閬嶅矗閸ф绠ョ憸鎴︺€?=====
async def execute_tool(name: str, params: dict) -> dict:
    """闂佸湱鐟抽崱鈺傛杸閻庤鎮堕崕閬嶅矗閸ф宓侀柟顖涘缁犳煡鏌涢妷褍浠х紒顔哄姂瀵?""
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
                return {"success": True, "data": r.json() if r.status_code==200 else {"error":"API婵炴垶鎸哥粔纾嬨亹閺屻儲鍋?}}
        if name == "docker_status":
            import subprocess
            r = subprocess.run(["docker","ps","--format","{{.Names}} {{.Status}}"], capture_output=True, text=True, timeout=10)
            return {"success": True, "data": {"containers": r.stdout.strip().split("\n")[:10]}}
        if name == "server_cleanup":
            import subprocess, gc
            gc.collect()
            subprocess.run(["docker","system","prune","-f"], capture_output=True, timeout=30)
            return {"success": True, "data": {"message": "闂佸憡鍔曢幊搴ㄦ偤閵娿儺鍟呴柡灞诲劚濞呯偤鏌￠埀?Docker缂傚倸鍊归幐鎼佹偤閵娿儺鍟呴柛娆忣槺椤忔悂鏌?}}
        
        # 闂備緡鍋呭銊╁极閵堝拋鍟呴柕澶堝劚瀵版棃鏌熺粭娑樻－閺€?
        tool = registry.get(name)
        if tool:
            result = await tool.execute(params)
            return {"success": True, "data": result if result else {}}
        return {"success": False, "error": f"閻庤鎮堕崕閬嶅矗?{name} 闂佸搫鐗滄禍婵囩珶濮椻偓瀹?}
    except Exception as e:
        return {"success": False, "error": str(e)[:200]}

# ===== RAG婵炴垶鎸搁敃锝囩箔閸涙潙妫?=====
async def _get_context(message: str) -> str:
    """闂佸吋鍎抽崲鑼躲亹閸ヮ剚鍎庣紒瀣仢瑜扮娀鏌ｉ婊冨姤闁?""
    try:
        ctx = await VectorMemory.search(message, top_k=3)
        if ctx:
            return "闂佺儵鏅濋…鍫ュ矗瑜旈幆宀勫Ψ閵娧勵潥:\n" + "\n".join([c.get("text","")[:200] for c in ctx])
    except Exception:
        pass
    return ""

# ===== 婵炴垶鎸鹃惇纾哸t缂備焦妫忛崹鎶藉磻?(Function Calling) =====
@router.post("/chat")
async def agent_chat(req: ChatRequest, _=Depends(verify_token)):
    """AI闁诲海鏁搁、濠囨儊?- 闂佸憡顭囬崰鎾诲极閹诲nction Calling"""
    rag_ctx = await _get_context(req.message)
    system_content = SYSTEM_PROMPT
    if rag_ctx:
        system_content += "\n\n" + rag_ctx
    
    messages = [{"role": "system", "content": system_content}]
    if req.history:
        messages.extend(req.history[-20:])  # 闂佸搫鐗冮崑鎾诲级?0闂佸搫顦埀顒€鍟块崸濠囨煕?
    messages.append({"role": "user", "content": req.message})
    
    result = await call_ai_with_tools(messages, req.model)
    
    # 婵犮垼娉涚€氼噣骞冩總鍞榥ction Calling闂佸憡绻傜粔瀵歌姳?
    if not result.get("fallback"):
        choice = result.get("choices", [{}])[0]
        msg = choice.get("message", {})
        tool_calls = msg.get("tool_calls", [])
        
        if tool_calls:
            # AI闂備緡鍋勯ˇ鎵偓姘ュ妽缁傚秹宕卞鍓х煑闂?
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
                return {"response": f"闂佺补鍋?L4婵＄偛顑呴柊锝呪枍閹捐绠肩€广儱瀚粙濠勨偓鐟版啞閻撯€澄熼崱妤婃桨? {tool_name}", "tool": tool_name, "risk": "L4"}
            
            exec_result = await execute_tool(tool_name, tool_args)
            
            # 闁诲繐绻愬Λ娑氬垝閵娾晛鍑犳繝濠傚暙閸愨偓婵☆偓绲介悧蹇曞垝閻у捄闂佹眹鍨婚崰鎰板垂濮樿埖鍤婃い蹇撴婵囨偣閸ヨ泛寮ㄩ柍璇茬墦瀹曞爼鎮欏顔叫?
            messages.append({"role": "assistant", "content": None, "tool_calls": tool_calls})
            messages.append({"role": "tool", "tool_call_id": tc.get("id",""), "content": json.dumps(exec_result, ensure_ascii=False)})
            
            final = await call_ai_with_tools(messages, req.model)
            ai_text = final.get("choices",[{}])[0].get("message",{}).get("content", "闂佸湱鐟抽崱鈺傛杸闁诲海鎳撻張顒勫垂?)
            
            # 闁荤姳鐒﹀妯兼崲閸屾壕鍋撳☉娅亪宕?
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
            # AI闂佺儵鏅涢悺銊ф暜閹绢喖妫橀柛銉ｅ妽閹烽亶鏌涢妷褍浠滄い?
            ai_text = msg.get("content", "")
            try:
                DigitalLifeform.remember_conversation(req.message, ai_text[:300])
            except Exception:
                pass
            return {"response": ai_text, "tool": None, "risk": "L1", "mode": state.mode}
    
    # Fallback: 闂佸搫鍞查崟顓烆棔閻?
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
        ai_text = f"闂佸湱鐟抽崱鈺傛杸 {tool_name}: " + json.dumps(exec_result.get("data",{}), ensure_ascii=False)[:500]
    
    return {"response": ai_text or "閻庡湱顭堝鍫曞极瑜版帒绀?濠殿喗绻愮徊钘夛耿椤忓懎绶為柛鏇ㄥ幗閸?..", "tool": tool_name, "risk": "L1", "mode": state.mode}

# ===== 濠电偟绻濈粈浣烘閿涘嫧鍋撻悽娈挎敯闁?=====
# ===== 閻庣懓鎲¤ぐ鍐敋椤旂偓瀚氭繝闈涙閸у﹪鏌?=====
_chat_histories = {}  # user_id -> [messages]

@router.post("/chat/history")
async def save_chat_history(req: dict, _=Depends(verify_token)):
    """婵烇絽娲︾换鍌炴偤閵娧€鍋撻悽娈挎敯闁伙缚绮欏畷銏ゅ幢濡も偓閽?""
    uid = req.get("user_id", "default")
    _chat_histories[uid] = req.get("messages", [])[-100:]
    state._data[f"chat_history_{uid}"] = _chat_histories[uid]
    state._save()
    return {"ok": True, "count": len(_chat_histories[uid])}

@router.get("/chat/history")
async def load_chat_history(user_id: str = Query("default"), _=Depends(verify_token)):
    """闂佸憡姊绘慨鎯归崶鈹惧亾閻㈡鏀伴柣锔跨矙瀹曘垽宕卞Δ鈧拺?""
    return {"messages": state._data.get(f"chat_history_{user_id}", [])[-50:]}

@router.delete("/chat/history")
async def clear_chat_history(user_id: str = Query("default"), _=Depends(verify_token)):
    """濠电偞鎸搁幊妯衡枍鎼达絺鍋撻悽娈挎敯闁伙缚绮欏畷銏ゅ幢濡も偓閽?""
    state._data.pop(f"chat_history_{user_id}", None)
    state._save()
    return {"ok": True}

# ===== 闁哄鐗嗛幊搴㈡叏椤忓棛鍗氭い鏍ㄧ矊娴?=====
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
    return {"ok": False, "error": "闂佸搫鐗滄禍婵囩珶濮椻偓瀹曟岸骞忓畝濠傛畽婵炲濮鹃褎鎱?}




CONV_DB = Path(__file__).parent.parent / "data" / "conversations.db"
def _cdb():
    CONV_DB.parent.mkdir(parents=True,exist_ok=True)
    c=sqlite3.connect(str(CONV_DB))
    c.execute("CREATE TABLE IF NOT EXISTS convs(id TEXT PRIMARY KEY,title TEXT,owner TEXT DEFAULT 'admin',created TEXT,updated TEXT)")
    c.execute("CREATE TABLE IF NOT EXISTS msgs(id INTEGER PRIMARY KEY AUTOINCREMENT,cid TEXT,role TEXT,content TEXT,owner TEXT DEFAULT 'admin',created TEXT)")
    c.commit();return c

@router.post("/chat/stream")
async def chat_stream(req: ChatRequest, _=Depends(verify_token)):
    """SSE闂備緡鍋呮禒鐠穔en濠电偟绻濈粈浣烘閳╁啯缍囬柟鎯у暱濮?""
    key=OPENAI_API_KEY or DEEPSEEK_API_KEY; url=OPENAI_BASE_URL or "https://api.openai.com/v1"
    m=req.model or _cheap_model
    ctx=await _get_context(req.message);sc=SYSTEM_PROMPT
    if ctx:sc+="\n\n"+ctx
    
    # RAG闂佹椿鍘归崕鎾儊閹寸偞鍎熼柟鍓ф嚀濞堜即鏌涢弬璇插闁轰胶鍋ゅ畷?
    try:
        from tools.rag_engine import RAGEngine
        rag_ctx = RAGEngine.build_context(req.message, top_k=3, max_tokens=1500)
        if rag_ctx:
            sc += "\n\n闂侀潧妫欓崝妤呮偂閿涘嫭瀚氶柛鈩冾殘濮樸劑鏌涘▎蹇撯偓浠嬪焵椤掆偓閸熴劑鍩€椤掍礁褰媙" + rag_ctx
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
async def cv(img:str=Form(...),q:str=Form("闂佺顕х换妤呭醇椤忓牆鐐婇柛鎾楀喚鏆?),_=Depends(verify_token)):
    k=OPENAI_API_KEY;u=OPENAI_BASE_URL or "https://api.openai.com/v1"
    if not k:return{"ok":False,"error":"闂傚倸娲犻崑鎾绘偡閺囨艾澹嘝ENAI_API_KEY"}
    try:
        async with httpx.AsyncClient(timeout=60)as c:
            r=await c.post(f"{u}/chat/completions",headers={"Authorization":f"Bearer {k}","Content-Type":"application/json"},
                json={"model":"gpt-4o-mini" if OPENAI_API_KEY else "gpt-4o","messages":[{"role":"user","content":[{"type":"text","text":q},{"type":"image_url","image_url":{"url":f"data:image/jpeg;base64,{img}"}}]}]})
            if r.status_code==200:
                d=r.json();return{"ok":True,"reply":d.get("choices",[{}])[0].get("message",{}).get("content","闂佸搫鍟版慨鐢垫兜閸洖绀嗛柛鈩冾焽閳?)}
            return{"ok":False,"error":f"API:{r.status_code}"}
    except Exception as e:return{"ok":False,"error":str(e)}

PROMPTS={}
for n,p in[("闂佸摜鍠庡Λ妤呭箹瑜斿顒勫炊椤垶鏁?,"婵炶揪绲挎慨闈浳ｉ幖浣瑰仺闂傚牊绋掑▍宀勬煛閸屾碍澶勬い?婵炴潙鍚嬮敋閻?\n{input}"),("闁诲骸绠嶉崹鍝勶耿閸ヮ剙鐐婇柣鎰▕濡?,"闁诲骸绠嶉崹娲春濞戞碍瀚?{input}\n闁荤姴娲ら崲鎻捗洪弽銊ョ窞?"),("闂佽桨鑳舵晶妤€鐣垫笟鈧畷姘跺幢濡皷鍋?,"闂佸憡甯掑Λ娆撴倵娴犲鏋侀柣妤€鐗嗙粊?\n{input}"),("婵炲濯寸徊鍧楁偉濠婂應鍋撻崗澶婂⒉闁?,"闁诲骸鍘滈崜婵嬫偂閳╁啰顩烽柨婵嗘川閸?\n{input}"),("SEO婵炴潙鍚嬮敋閻?,"婵炴潙鍚嬮敋閻庡灚鐓″畷妤呭箮閼恒儲娈柣?\n{input}"),("缂傚倸鐗婂Σ鎺楁儊?,"缂傚倸鐗婂Σ鎺楁儊瑜旈獮瀣箒缁佸儭ng}:\n{input}"),("闂佸憡绋忛崝宥嗘叏?,"闂佸搫绉烽～澶婄暤娓氣偓瀵偊鎮ч崼婵堛偊闂佹眹鍨婚崰鎰板垂濮樿泛宸濋柕濠忕畱琚?\n{input}"),("缂備焦姊婚崑娑㈠箹瑜斿畷姘跺幢濡皷鍋?,"闂佸憡甯掑Λ娆撴倵閻ｅ瞼鍗氶柣鎰级閹倹顨ラ悙鎻掝暢缂侇喗澹嗙划鐢稿冀椤愶絾顓?\n{input}")]:
    PROMPTS[n]={"prompt":p,"icon":"濡絽鍟幆?}

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
    c.execute("INSERT INTO convs VALUES(?,?,datetime('now'),datetime('now'))",(cid,req.get("title","闂佸搫鍊瑰姗€顢氶鐐珰?)))
    c.commit();c.close();return{"ok":True,"id":cid}

@router.get("/conversations/{cid}")
async def gc(cid:str,_=Depends(verify_token)):
    c=_cdb();r=c.execute("SELECT role,content,created FROM msgs WHERE cid=? ORDER BY id LIMIT 50",(cid,)).fetchall();c.close()
    return{"ok":True,"messages":[{"role":x[0],"content":x[1],"time":x[2]} for x in r]}

@router.delete("/conversations/{cid}")
async def dc(cid:str,_=Depends(verify_token)):
    c=_cdb();c.execute("DELETE FROM msgs WHERE cid=?",(cid,));c.execute("DELETE FROM convs WHERE id=?",(cid,));c.commit();c.close()
    return {"ok": True}
# ===== RAG闂佸搫鍊稿ú锝呪枎閵忥紕鈻斿┑鐘辫兌閻?=====
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
            text=r.stdout or"PDF闁荤喐鐟辩徊楣冩倵閼恒儱绶為弶鍫亯琚?;os.unlink(tp)
        except:text=f"[PDF:{file.filename}]闂傚倸娲犻崑鎼峯ppler-utils"
    else:text=raw.decode("utf-8","ignore")[:5000]
    chunks=[text[i:i+800]for i in range(0,min(len(text),16000),800)]if text.strip()else[]
    for i,ch in enumerate(chunks):
        try:await VectorMemory.remember(ch,{"type":"doc","source":file.filename,"chunk":i})
        except:pass
    return{"ok":True,"file":file.filename,"chars":len(text),"chunks":len(chunks)}

# ===== 濠碘槅鍨埀顒€纾埀顒勵棑閳ь兛绲婚～澶愭儊?=====
@router.post("/chat/compare")
async def chat_compare(req: ChatRequest, _=Depends(verify_token)):
    """闂佸憡鑹炬總鏃傜博閹绢喗鈷掓い鏇楀亾妞わ絼绮欏畷锝夊箣閻樹絻鍩楁繝銏ｅ煐閻噣鏌屽鍏剧喖鍨惧畷鍥ｅ亾妞嬪簶鍋撴担鍐炬綈闁伙富鍠氱划鐢稿籍閳ь剟銆?""
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

# ===== 闂佽桨鑳舵晶妤€鐣垫笟鈧幆鍥┾偓锝庡亝缁剁潪I =====
@router.get("/dashboard/ask")
async def dashboard_ask(q: str = Query(...), _=Depends(verify_token)):
    """闂佺厧顨庢禍鐐哄礉瑜忛幏鐘活敇閳锯偓閺嬪懘鏌＄仦璇插姤妞ゆ洘顨嗗濠氬箛椤栨稑鍓﹂梺杞拌兌婢ф鐣?""
    try:
        import psutil,os
        cpu=psutil.cpu_percent();mem=psutil.virtual_memory();disk=psutil.disk_usage("/")
        ctx=f"闂佸搫鐗嗙粔瀛樻叏閻旂厧闂柕濞у唭锕傛煙? CPU {cpu}%, 闂佸憡鍔曢幊搴ㄦ偤?{mem.percent}%, 缂佹儳褰為懗璺好?{disk.percent}%"
        key=OPENAI_API_KEY or DEEPSEEK_API_KEY;url=OPENAI_BASE_URL or "https://api.openai.com/v1"
        async with httpx.AsyncClient(timeout=30)as c:
            r=await c.post(f"{url}/chat/completions",headers={"Authorization":f"Bearer {key}","Content-Type":"application/json"},
                json={"model":"gpt-3.5-turbo","messages":[
                    {"role":"system","content":f"婵炶揪绲挎慨闈浳ｉ幖浣告瀬闁绘鐗嗙粊锕傛煕閹烘垶顥為柣搴ｆ櫕閺?閻熸粎澧楅幐鍛婃櫠閻橀潧瀵查柤濮愬€楅崺鐘绘煛娴ｅ搫顣肩€?{ctx}.闁荤姴娲ˉ鎾诲极閵堝棛鈻旀い鎾跺枑閻庮喚绱掗悩顐壕濠电偠寮撶粈浣该洪弽顐ら┏?"},
                    {"role":"user","content":q}
                ],"temperature":0.5,"max_tokens":400})
            if r.status_code==200:
                d=r.json();return{"ok":True,"answer":d.get("choices",[{}])[0].get("message",{}).get("content","")}
        return{"ok":False,"error":f"API:{r.status_code}"}
    except Exception as e:return{"ok":False,"error":str(e)}


# ===== 婵犮垼鍩栧銊╋綖閵堝绠ｅ瀣瘨閸氣偓闂?婵炲濮村畷濯巑in) =====
@router.get("/admin/tenants")
async def list_tenants(_=Depends(verify_token)):
    """闂佸憡甯楅〃鍛村吹椤撱垹绠ラ柍褜鍓熷鍨緞瀹€濠冨尃闂佽娼欓崲鎻掝嚕閻戣棄绀傞柟顖涘閵堫偅绻濊閸旀寮妶澶嬬厒?""
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


# ===== 闁诲海鏁搁、濠囨儊閻ｅ本濯奸柡澶庢硶缁犳挾绱掗悪鍛？闁?=====
@router.post("/conversations/{cid}/summarize")
async def summarize_conversation(cid: str, _=Depends(verify_token)):
    """闂佺厧顨庢禍婊勬叏閳哄懎绠烘俊顖涱儥濞诧綁姊婚埀顒勫垂椤曞懎娈搁柣?+ 闂佸憡锚椤戝洨绱撴径灞惧闁哄娉曠粻?""
    msgs = load_history(cid, 100)
    if len(msgs) < 10:
        return {"ok": True, "original_count": len(msgs), "summary": "闁诲海鏁搁、濠囨儊閼恒儱绶炴い蹇撴閸?闂佸搫鍟版繛鈧繛鎾崇埣楠炴螣濞嗙偓鐭?}
    
    # 闂佸搫顑呯€氼剛绱撻幘鍨涘亾閻㈡鏀伴柣锔跨矙瀵剟宕堕妸锔藉
    conv_text = "\n".join([f"{m['role']}: {m['content'][:200]}" for m in msgs])
    
    try:
        from tools.ai_client import call_ai
        summary = await call_ai([
            {"role": "user", "content": f"闁荤姴娲ˉ鎾诲极?-5闂佸憡鐟ｉ崕鎾儊娴犲绠戦柤濮愬€楀▔銏ゅ级閳哄倻鎳勬い鏂跨灱閳ь剛鏁搁、濠囨儊娴犲鍎嶉柛鏇ㄥ墰婢瑰鐓崶褍鏆欓柛鐐差嚟閳ь剙婀遍幊鎾诲箯閹殿喚纾奸柟鎹愵嚃閸?\n{conv_text[:4000]}"}
        ], max_tokens=200, temperature=0.3)
        
        # 婵烇絽娲︾换鍌炴偤閵娾晛绠烘俊顖涱儥濞诧綁鏌涢幒鎾寸凡妞ゆ洦鍠氶幏鐘测攽閸℃绗氶梺杞拌兌婢ф鐣?
        c = _cdb()
        c.execute("UPDATE convs SET title=? WHERE id=?", (summary[:100], cid))
        c.commit(); c.close()
        
        return {"ok": True, "original_count": len(msgs), "summary": summary, "compressed": True}
    except Exception as e:
        return {"ok": False, "error": str(e)}

@router.get("/conversations/{cid}/context")
async def get_conversation_context(cid: str, query: str = "", _=Depends(verify_token)):
    """闂佸吋鍎抽崲鑼躲亹閸モ斁鍋撻悽娈挎敯闁伙箒濮ょ粙澶嬬節娴ｈ櫣鎲梺?-- 闂佺厧顨庢禍婊勬叏閳轰脊搴＄暋閻楀牆鈧?闂佸搫鐗冮崑鎾诲级閳哄倸鐏︾紒澶屽厴楠?+ RAG + 闂佺濮ら…鍫ャ€?""
    msgs = load_history(cid, 30)
    result = {"messages": msgs, "count": len(msgs)}
    
    # 婵犵鈧啿鈧綊鎮樻径鎰珘濠㈣泛顑囬崣鈧柣?闂佺懓鍚嬬划搴ㄥ磼閵娾晜鍎庣紒瀣仢瑜扮娀鏌ｉ婊冨姤闁伙附鍨堕幆?
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
async def chat_vision(file: UploadFile = File(...), question: str = "閹诲繗鍫潻娆忕炊閸ュ墽澧?, _=Depends(verify_token)):
    """婢舵碍膩閹礁娴橀悧鍥у瀻閺?""
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
async def chat_file_analysis(file: UploadFile = File(...), question: str = "閸掑棙鐎芥潻娆庨嚋閺傚洣娆?, _=Depends(verify_token)):
    """閺傚洣娆㈤崚鍡樼€?閺傚洦婀?PDF/鐟欏棝顣剁敮?"""
    try:
        content = await file.read()
        text = ""
        if file.content_type and "video" in file.content_type:
            text = f"[鐟欏棝顣堕弬鍥︽: {file.filename}, {len(content)} bytes, 缁鐎? {file.content_type}]"
        elif file.content_type and "pdf" in file.content_type:
            try:
                import io, PyPDF2
                reader = PyPDF2.PdfReader(io.BytesIO(content))
                text = " ".join([p.extract_text() or "" for p in reader.pages[:5]])
            except: text = content.decode("utf-8","ignore")[:3000]
        else:
            text = content.decode("utf-8","ignore")[:5000]
        from agents.multi_model import ModelRouter
        resp = ModelRouter.smart_chat(messages=[{"role":"user","content":f"閺傚洣娆? {file.filename}\n閸愬懎顔? {text}\n\n闂傤噣顣? {question}"}], mode="smart")
        return {"ok":True,"analysis":resp.get("content","") if isinstance(resp,dict) else str(resp),"text_length":len(text)}
    except Exception as e: return {"ok":False,"error":str(e)}

@router.post("/handover")
async def agent_handover(req: HandoverRequest, _=Depends(verify_token)):
    state.mode = "human_control"
    return {"ok": True, "mode": "human_control", "reason": req.reason}

# === 对话记忆 ===
_conversations = {}

def get_conversation_context(conv_id: str, max_tokens: int = 4000) -> str:
    msgs = _conversations.get(conv_id, [])[-20:]
    ctx = []
    total = 0
    for m in reversed(msgs):
        chunk = "{0}: {1}".format(m["role"], m["content"][:500])
        total += len(chunk)
        if total > max_tokens: break
        ctx.insert(0, chunk)
    return "\n".join(ctx)

@router.post("/chat/memory")
async def chat_with_memory(req: ChatRequest, conv_id: str = "default", _=Depends(verify_token)):
    context = get_conversation_context(conv_id)
    messages = []
    if context: messages.append({"role":"system","content":"历史对话:\n"+context})
    for m in req.messages: messages.append({"role":m.role,"content":m.content})
    _conversations.setdefault(conv_id, []).append({"role":"user","content":req.messages[-1].content[:500]})
    try:
        from agents.multi_model import ModelRouter
        resp = ModelRouter.smart_chat(messages=messages, mode="smart")
        reply = resp.get("content","") if isinstance(resp,dict) else str(resp)
        _conversations.setdefault(conv_id, []).append({"role":"assistant","content":reply[:500]})
        if len(_conversations.get(conv_id,[])) > 50:
            _conversations[conv_id] = _conversations[conv_id][-40:]
        return {"ok":True,"reply":reply,"conv_id":conv_id,"count":len(_conversations.get(conv_id,[]))}
    except Exception as e: return {"ok":False,"error":str(e)}

@router.get("/chat/conversations")
async def list_conversations(_=Depends(verify_token)):
    return {"ok":True,"conversations":[{"id":k,"messages":len(v)} for k,v in _conversations.items()]}
