锘?""澶欰gent鍗忎綔鍗忚 鈥?浠诲姟鎷嗚В+Agent璋冨害+缁撴灉姹囨€?""
import json, asyncio
from datetime import datetime
from dataclasses import dataclass, field
from tools.logger import get_logger

logger = get_logger("agent_collab")

@dataclass
class CollaborationTask:
    id: str
    title: str
    subtasks: list = field(default_factory=list)
    assigned_agents: dict = field(default_factory=dict)
    results: dict = field(default_factory=dict)
    status: str = "pending"
    created_at: str = ""
    completed_at: str = ""

class AgentCollaboration:
    """澶欰gent鍗忎綔寮曟搸"""
    
    AGENT_CAPABILITIES = {
        "trend": ["绔炲搧鍒嗘瀽", "鐑偣鐩戞帶", "瓒嬪娍棰勬祴", "鑸嗘儏鍒嗘瀽"],
        "scraper": ["鍟嗗搧閲囬泦", "鏁版嵁鎶撳彇", "浠锋牸鐩戞帶"],
        "vision": ["鍥剧墖鍒嗘瀽", "OCR璇嗗埆", "瑙嗛澶勭悊"],
        "code": ["浠ｇ爜鐢熸垚", "Bug淇", "API寮€鍙?],
        "devops": ["閮ㄧ讲妫€鏌?, "瀹瑰櫒绠＄悊", "Nginx閰嶇疆"],
        "heal": ["寮傚父妫€娴?, "鑷姩淇", "鏈嶅姟鎭㈠"],
        "memory": ["鐭ヨ瘑妫€绱?, "缁忛獙瀛︿範", "涓婁笅鏂囨彁渚?],
    }
    
    @classmethod
    async def analyze_and_delegate(cls, goal: str) -> CollaborationTask:
        """鍒嗘瀽鐩爣骞舵媶瑙ｄ负瀛愪换鍔?""
        task_id = f"collab_{datetime.now().strftime('%H%M%S')}"
        task = CollaborationTask(
            id=task_id, title=goal,
            created_at=datetime.now().isoformat()
        )
        
        # 鍩轰簬鍏抽敭璇嶅尮閰岮gent
        goal_lower = goal.lower()
        assigned = []
        
        for agent, capabilities in cls.AGENT_CAPABILITIES.items():
            for cap in capabilities:
                if any(w in goal_lower for w in cap.lower().split()):
                    if agent not in assigned:
                        assigned.append(agent)
                        task.assigned_agents[agent] = cap
        
        # 濡傛灉娌℃湁鍖归厤锛岄粯璁ょ敤trend+memory
        if not assigned:
            assigned = ["trend", "memory"]
            task.assigned_agents = {"trend": "淇℃伅閲囬泦", "memory": "鐭ヨ瘑琛ュ厖"}
        
        # 鐢熸垚瀛愪换鍔?
        task.subtasks = [
            {"id": f"{task_id}_s{i+1}", "agent": agent, "action": cap, "status": "pending"}
            for i, (agent, cap) in enumerate(task.assigned_agents.items())
        ]
        
        logger.info(f"鍗忎綔浠诲姟鍒涘缓: {goal} -> {len(task.subtasks)}涓瓙浠诲姟, {len(assigned)}涓狝gent")
        return task
    
    @classmethod
    async def execute_subtask(cls, task: CollaborationTask, subtask_id: str) -> dict:
        """鎵ц鍗曚釜瀛愪换鍔?""
        for st in task.subtasks:
            if st["id"] == subtask_id:
                st["status"] = "running"
                agent = st["agent"]
                try:
                    # 璋冨害鍒板搴擜gent
                    if agent == "trend":
                        from agents.trend_agent import TrendAgent
                        result = await TrendAgent.analyze(task.title)
                    elif agent == "scraper":
                        from tools.scraper_engine import ScraperEngine
                        result = {"products": len(ScraperEngine.get_products()["items"])}
                    elif agent == "vision":
                        result = {"status": "Vision Agent宸插氨缁?}
                    elif agent == "code":
                        from agents.code_agent import CodeAgent
                        result = await CodeAgent.analyze(task.title)
                    elif agent == "devops":
                        from agents.devops_agent import DevOpsAgent
                        result = await DevOpsAgent.inspect()
                    elif agent == "heal":
                        from agents.self_healing_agent import SelfHealingAgent
                        result = await SelfHealingAgent.run_patrol()
                    elif agent == "memory":
                        from tools.vector_memory import VectorMemory
                        ctx = await VectorMemory.search(task.title, top_k=3)
                        result = {"context": [c.get("text","")[:200] for c in ctx]}
                    else:
                        result = {"status": "unknown_agent"}
                    
                    task.results[agent] = {"success": True, "data": result}
                    st["status"] = "done"
                    return {"ok": True, "agent": agent, "result": result}
                except Exception as e:
                    task.results[agent] = {"success": False, "error": str(e)[:200]}
                    st["status"] = "failed"
                    return {"ok": False, "agent": agent, "error": str(e)[:200]}
        return {"ok": False, "error": "瀛愪换鍔′笉瀛樺湪"}
    
    @classmethod
    async def execute_all(cls, goal: str) -> dict:
        """瀹屾暣鍗忎綔娴佺▼锛氬垎鏋?>鎷嗚В->骞惰鎵ц->姹囨€?""
        task = await cls.analyze_and_delegate(goal)
        task.status = "running"
        
        # 骞惰鎵ц鎵€鏈夊瓙浠诲姟
        tasks = [cls.execute_subtask(task, st["id"]) for st in task.subtasks]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # 姹囨€荤粨鏋?
        success_count = sum(1 for r in results if isinstance(r, dict) and r.get("ok"))
        task.status = "done"
        task.completed_at = datetime.now().isoformat()
        
        summary = f"## 鍗忎綔浠诲姟瀹屾垚\n"
        summary += f"**鐩爣**: {goal}\n"
        summary += f"**Agent**: {', '.join(task.assigned_agents.keys())}\n"
        summary += f"**缁撴灉**: {success_count}/{len(task.subtasks)} 鎴愬姛\n\n"
        for agent, result in task.results.items():
            status = "鉁? if result.get("success") else "鉂?
            summary += f"- {status} **{agent}**: {json.dumps(result, ensure_ascii=False)[:100]}\n"
        
        logger.info(f"鍗忎綔瀹屾垚: {goal} -> {success_count}/{len(task.subtasks)}")
        return {"ok": True, "task": task.__dict__, "summary": summary, "success_rate": f"{success_count}/{len(task.subtasks)}"}

# 鍏ㄥ眬瀹炰緥
agent_collab = AgentCollaboration()
