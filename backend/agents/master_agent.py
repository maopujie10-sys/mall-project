"""Master Agent -- Friday AI OS 鎬绘帶澶ц剳
鑱岃矗:浠诲姟鎷嗚В銆丄gent璋冨害銆佷笂涓嬫枃绠＄悊銆侀暱鏈熺洰鏍囪拷韪?
v2: Claude 鐪熷疄AI鎺ㄧ悊 + 鍏抽敭璇嶅厹搴?""
import json
import httpx
import time
from datetime import datetime
from dataclasses import dataclass, field
from typing import Optional

@dataclass
class Task:
    id: str
    goal: str
    steps: list = field(default_factory=list)
    assigned_agent: str = ""
    status: str = "pending"
    created_at: str = ""
    completed_at: str = ""

class MasterAgent:
    """鎬绘帶Agent -- AI鎺ㄧ悊 + 瑙勫垯鍏滃簳鍙屽紩鎿?""

    AGENTS = {
        "code": "浠ｇ爜缂栧啓/淇/Bug鍒嗘瀽",
        "devops": "鏈嶅姟鍣?Docker/Nginx/閮ㄧ讲",
        "vision": "鍥剧墖璇嗗埆/瑙嗛鍒嗘瀽/OCR",
        "trend": "鐑偣鐩戞帶/鑸嗘儏鍒嗘瀽/瓒嬪娍棰勬祴",
        "memory": "闀挎湡璁板繂/鐭ヨ瘑妫€绱?缁忛獙瀛︿範",
        "heal": "寮傚父妫€娴?鑷姩淇/鏈嶅姟鎭㈠",
        "scraper": "鍟嗗搧閲囬泦/鏁版嵁鎶撳彇",
        "mall": "鍟嗗煄绠＄悊/瀹㈡湇/杞€?,
    }

    @staticmethod
    async def analyze_intent(message: str, use_ai: bool = True) -> dict:
        """鍒嗘瀽鐢ㄦ埛鎰忓浘 -- AI鎺ㄧ悊浼樺厛,鍏抽敭璇嶅厹搴?""
        if use_ai:
            ai_result = await MasterAgent._ai_analyze(message)
            if ai_result and ai_result.get("agents"):
                return ai_result

        return MasterAgent._keyword_analyze(message)

    @staticmethod
    async def _ai_analyze(message: str) -> Optional[dict]:
        """璋冪敤 Claude 杩涜娣卞眰鎰忓浘鍒嗘瀽"""
        try:
            from config import CLAUDE_API_KEY, CLAUDE_MODEL
        except Exception:
            return None
        if not CLAUDE_API_KEY:
            return None

        agent_desc = "\n".join([f"- {k}: {v}" for k, v in MasterAgent.AGENTS.items()])
        prompt = f"""浣犳槸 Friday AI OS 鐨勬€绘帶澶ц剳.鍒嗘瀽鐢ㄦ埛娑堟伅,杩斿洖闇€瑕佽皟鐢ㄧ殑Agent鍒楄〃.

鍙敤Agent:
{agent_desc}

鐢ㄦ埛娑堟伅: {message}

杩斿洖绾疛SON(涓嶈markdown鍖呰９):
{{"intent": "绠€鐭剰鍥炬弿杩?, "agents": ["agent1","agent2"], "complexity": "low/medium/high", "reasoning": "鎺ㄧ悊渚濇嵁"}}"""

        try:
            async with httpx.AsyncClient(timeout=20) as c:
                r = await c.post(
                    "https://api.anthropic.com/v1/messages",
                    headers={
                        "x-api-key": CLAUDE_API_KEY,
                        "anthropic-version": "2023-06-01",
                        "content-type": "application/json",
                    },
                    json={
                        "model": CLAUDE_MODEL,
                        "max_tokens": 300,
                        "messages": [{"role": "user", "content": prompt}],
                    },
                )
                if r.status_code == 200:
                    data = r.json()
                    text = data["content"][0]["text"]
                    # 鎻愬彇JSON
                    start = text.find("{")
                    end = text.rfind("}") + 1
                    if start >= 0 and end > start:
                        result = json.loads(text[start:end])
                        result["timestamp"] = datetime.now().isoformat()
                        result["engine"] = "claude"
                        return result
        except Exception:
            pass
        return None

    @staticmethod
    def _keyword_analyze(message: str) -> dict:
        """鍏抽敭璇嶅尮閰?-- AI涓嶅彲鐢ㄦ椂鐨勫厹搴曟柟妗?""
        msg_lower = message.lower()
        agents_needed = []

        rules = [
            (["浠ｇ爜","bug","鎶ラ敊","鎺ュ彛","sql","淇","寮€鍙?,"鍐欎竴涓?,"鍑芥暟","绫?], "code"),
            (["鏈嶅姟鍣?,"docker","nginx","閮ㄧ讲","閲嶅惎","绔彛","cpu","鍐呭瓨","纾佺洏"], "devops"),
            (["鍥剧墖","瑙嗛","璇嗗埆","ocr","鐪嬪浘","鍒嗘瀽鍥剧墖","鎷嶇収","浜鸿劯"], "vision"),
            (["鐑偣","鎶栭煶","寰崥","鐑悳","瓒嬪娍","鑸嗘儏","b绔?], "trend"),
            (["璁板繂","璁颁綇","涓婃","涔嬪墠","鍘嗗彶","瀛︿範","鏃ヨ"], "memory"),
            (["寮傚父","鎸備簡","鎭㈠","鑷姩淇","宸℃","鍋ュ悍"], "heal"),
            (["閲囬泦","鎶撳彇","鍟嗗搧","涓婃灦","ebay","shopee"], "scraper"),
            (["鍟嗗煄","瀹㈡湇","杞€?,"璁㈠崟","鐢ㄦ埛"], "mall"),
        ]

        for keywords, agent in rules:
            if any(kw in msg_lower for kw in keywords):
                agents_needed.append(agent)

        if not agents_needed:
            agents_needed = ["code", "devops", "memory"]

        return {
            "intent": message[:100],
            "agents": agents_needed,
            "complexity": "high" if len(agents_needed) > 3 else "medium" if len(agents_needed) > 1 else "low",
            "timestamp": datetime.now().isoformat(),
            "engine": "keyword",
        }

    @staticmethod
    def create_task_plan(goal: str, agents: list) -> list:
        """鏍规嵁鐩爣鍜孉gent鍒楄〃鐢熸垚鎵ц璁″垝"""
        plan = []
        for i, agent in enumerate(agents):
            plan.append({
                "step": i + 1,
                "agent": agent,
                "action": f"{MasterAgent.AGENTS.get(agent, '鎵ц浠诲姟')}",
                "status": "pending",
            })
        return plan

    @staticmethod
    async def create_ai_plan(goal: str, agents: list) -> list:
        """浣跨敤Claude鐢熸垚鏅鸿兘鎵ц璁″垝"""
        try:
            from config import CLAUDE_API_KEY, CLAUDE_MODEL
            if not CLAUDE_API_KEY:
                return MasterAgent.create_task_plan(goal, agents)

            agent_list = ", ".join(agents)
            prompt = f"""涓轰互涓嬬洰鏍囩敓鎴愭墽琛岃鍒?
鐩爣: {goal}
鍙敤Agent: {agent_list}

杩斿洖JSON鏁扮粍(涓嶈markdown鍖呰９):
[{{"step": 1, "agent": "agent鍚?, "action": "鍏蜂綋鎿嶄綔", "detail": "璇︾粏璇存槑"}}]"""

            async with httpx.AsyncClient(timeout=20) as c:
                r = await c.post(
                    "https://api.anthropic.com/v1/messages",
                    headers={
                        "x-api-key": CLAUDE_API_KEY,
                        "anthropic-version": "2023-06-01",
                        "content-type": "application/json",
                    },
                    json={
                        "model": CLAUDE_MODEL,
                        "max_tokens": 600,
                        "messages": [{"role": "user", "content": prompt}],
                    },
                )
                if r.status_code == 200:
                    data = r.json()
                    text = data["content"][0]["text"]
                    start = text.find("[")
                    end = text.rfind("]") + 1
                    if start >= 0 and end > start:
                        plan = json.loads(text[start:end])
                        for step in plan:
                            step["status"] = "pending"
                        return plan
        except Exception:
            pass
        return MasterAgent.create_task_plan(goal, agents)

    @staticmethod
    def get_agent_status() -> list:
        """鑾峰彇鎵€鏈堿gent鐘舵€?""
        return [
            {"id": "master", "name": "Master Agent", "icon": "馃", "status": "active", "engine": "claude+keyword", "tasks": 0},
            {"id": "code", "name": "Code Agent", "icon": "馃捇", "status": "idle", "tasks": 0},
            {"id": "devops", "name": "DevOps Agent", "icon": "鈿欙笍", "status": "active", "tasks": 0},
            {"id": "vision", "name": "Vision Agent", "icon": "馃憗锔?, "status": "idle", "tasks": 0},
            {"id": "trend", "name": "Trend Agent", "icon": "馃摗", "status": "idle", "tasks": 0},
            {"id": "memory", "name": "Memory Agent", "icon": "馃捑", "status": "active", "tasks": 0},
            {"id": "heal", "name": "Self-Healing Agent", "icon": "馃洝锔?, "status": "idle", "tasks": 0},
            {"id": "scraper", "name": "Scraper Agent", "icon": "馃暦锔?, "status": "idle", "tasks": 0},
        ]

    @classmethod
    async def collaborate(cls, task: str) -> dict:
        """多Agent协作"""
        from agents.orchestrator import AgentOrchestrator
        return await AgentOrchestrator.plan_and_execute(task)
