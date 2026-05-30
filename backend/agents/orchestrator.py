''"Agent  Agent''"
import asyncio, json
from typing import Dict, List
from tools.logger import get_logger

logger = get_logger("orchestrator")

class AgentOrchestrator:
    ''"Agent''"

    _agent_registry = {
        "code": "code_agent", "devops": "devops_agent", "github": "github_agent",
        "vision": "vision_agent", "trend": "trend_agent", "memory": "memory_agent",
        "playwright": "playwright_agent", "self_heal": "self_healing_agent"
    }

    @classmethod
    async def execute_pipeline(cls, steps: List[Dict]) -> Dict:
        ''": [{agent, action, params}, ...]''"
        results = []
        context = {}
        for i, step in enumerate(steps):
            agent_name = step.get("agent", '')
            action = step.get("action", '')
            params = step.get("params", {})
            params["_context"] = context
            try:
                agent_module = __import__(f"agents.{cls._agent_registry.get(agent_name, agent_name)}", fromlist=[''])
                if hasattr(agent_module, action):
                    result = await getattr(agent_module, action)(**params)
                elif hasattr(agent_module, "execute"):
                    result = await agent_module.execute(action, params)
                else:
                    result = {"error": f"Agent {agent_name}  {action} "}
                results.append({"step": i+1, "agent": agent_name, "ok": True, "result": result})
                context[f"step_{i+1}"] = result
            except Exception as e:
                results.append({"step": i+1, "agent": agent_name, "ok": False, "error": str(e)})
                break
        return {"ok": True, "total_steps": len(steps), "completed": len([r for r in results if r.get("ok")]), "results": results}

    @classmethod
    async def plan_and_execute(cls, task: str) -> Dict:
        ''"AI+''"
        from agents.multi_model import ModelRouter
        plan_prompt = f''"Agent: code(), devops(), github(GitHub), vision(), trend(), playwright(), self_heal()
: {task}
JSON: [{{"agent":"agent","action":'',"params":{{}}}}]''"
        resp = ModelRouter.smart_chat(messages=[{"role":"user","content":plan_prompt}], mode="fast")
        try:
            plan_text = resp.get("content","[]") if isinstance(resp,dict) else "[]"
            steps = json.loads(plan_text) if isinstance(plan_text, str) else plan_text
            if not isinstance(steps, list): steps = []
        except:
            steps = []
        if not steps:
            return {"ok": False, "error": '', "plan": plan_text if 'plan_text' in dir() else ''}
        result = await cls.execute_pipeline(steps)
        result["plan"] = steps
        return result

orchestrator = AgentOrchestrator()