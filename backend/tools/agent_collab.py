"""Agent -- +Agent+"""
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
    created_at: str = ''
    completed_at: str = ''

class AgentCollaboration:
    ''"Agent''"
    
    AGENT_CAPABILITIES = {
        "trend": ['', '', '', ''],
        "scraper": ['', '', ''],
        "vision": ['', "OCR", ''],
        "code": ['', "Bug", "API"],
        "devops": ['', '', "Nginx"],
        "heal": ['', '', ''],
        "memory": ['', '', ''],
    }
    
    @classmethod
    async def analyze_and_delegate(cls, goal: str) -> CollaborationTask:
        ''''''
        task_id = f"collab_{datetime.now().strftime('%H%M%S')}"
        task = CollaborationTask(
            id=task_id, title=goal,
            created_at=datetime.now().isoformat()
        )
        
        # Agent
        goal_lower = goal.lower()
        assigned = []
        
        for agent, capabilities in cls.AGENT_CAPABILITIES.items():
            for cap in capabilities:
                if any(w in goal_lower for w in cap.lower().split()):
                    if agent not in assigned:
                        assigned.append(agent)
                        task.assigned_agents[agent] = cap
        
        # ,trend+memory
        if not assigned:
            assigned = ["trend", "memory"]
            task.assigned_agents = {"trend": '', "memory": ''}
        
        
        task.subtasks = [
            {"id": f"{task_id}_s{i+1}", "agent": agent, "action": cap, "status": "pending"}
            for i, (agent, cap) in enumerate(task.assigned_agents.items())
        ]
        
        logger.info(f": {goal} -> {len(task.subtasks)}, {len(assigned)}Agent")
        return task
    
    @classmethod
    async def execute_subtask(cls, task: CollaborationTask, subtask_id: str) -> dict:
        ''''''
        for st in task.subtasks:
            if st["id"] == subtask_id:
                st["status"] = "running"
                agent = st["agent"]
                try:
                    # Agent
                    if agent == "trend":
                        from agents.trend_agent import TrendAgent
                        result = await TrendAgent.analyze(task.title)
                    elif agent == "scraper":
                        from tools.scraper_engine import ScraperEngine
                        result = {"products": len(ScraperEngine.get_products()["items"])}
                    elif agent == "vision":
                        result = {"status": "Vision Agent"}
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
                        result = {"context": [c.get("text",'')[:200] for c in ctx]}
                    else:
                        result = {"status": "unknown_agent"}
                    
                    task.results[agent] = {"success": True, "data": result}
                    st["status"] = "done"
                    return {"ok": True, "agent": agent, "result": result}
                except Exception as e:
                    task.results[agent] = {"success": False, "error": str(e)[:200]}
                    st["status"] = "failed"
                    return {"ok": False, "agent": agent, "error": str(e)[:200]}
        return {"ok": False, "error": ''}
    
    @classmethod
    async def execute_all(cls, goal: str) -> dict:
        ''":->->->''"
        task = await cls.analyze_and_delegate(goal)
        task.status = "running"
        
        
        tasks = [cls.execute_subtask(task, st["id"]) for st in task.subtasks]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        
        success_count = sum(1 for r in results if isinstance(r, dict) and r.get("ok"))
        task.status = "done"
        task.completed_at = datetime.now().isoformat()
        
        summary = f"## \n"
        summary += f"****: {goal}\n"
        summary += f"**Agent**: {', '.join(task.assigned_agents.keys())}\n"
        summary += f"****: {success_count}/{len(task.subtasks)} \n\n"
        for agent, result in task.results.items():
            status = "" if result.get("success") else ""
            summary += f"- {status} **{agent}**: {json.dumps(result, ensure_ascii=False)[:100]}\n"
        
        logger.info(f": {goal} -> {success_count}/{len(task.subtasks)}")
        return {"ok": True, "task": task.__dict__, "summary": summary, "success_rate": f"{success_count}/{len(task.subtasks)}"}


agent_collab = AgentCollaboration()
