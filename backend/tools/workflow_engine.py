"""AI Workflow Engine - Template-based and AI-generated workflow execution"""
import asyncio, json, re
from datetime import datetime
from state import state
from tools.registry import registry

class WorkflowEngine:
    workflows = {}

    TEMPLATES = {
        "Clear Dead Inventory": {"steps": [
            {"tool":"product.list","params":{"status":"low_stock"},"desc":"Find low-stock products"},
            {"tool":"product.batch_offline","params":{},"desc":"Batch offline dead products","risk":"L3"},
            {"tool":"report.generate","params":{"type":"offline_report"},"desc":"Generate offline report"},
        ]},
        "Daily Backup Routine": {"steps": [
            {"tool":"db.backup","params":{},"desc":"Backup database","risk":"L3"},
            {"tool":"file.archive","params":{"type":"backup"},"desc":"Archive backup files"},
        ]},
        "Deploy Pipeline": {"steps": [
            {"tool":"git.pull","params":{},"desc":"Pull latest code","risk":"L3"},
            {"tool":"docker.build","params":{"service":"all"},"desc":"Build Docker images","risk":"L3"},
            {"tool":"docker.deploy","params":{"service":"all"},"desc":"Deploy services","risk":"L4"},
        ]},
        "System Health Check": {"steps": [
            {"tool":"server.status","params":{},"desc":"Check server status"},
            {"tool":"docker.ps","params":{},"desc":"Check Docker containers"},
            {"tool":"nginx.status","params":{},"desc":"Check Nginx status"},
            {"tool":"db.status","params":{},"desc":"Check database status"},
            {"tool":"rotation.domains","params":{},"desc":"Check domain rotation"},
        ]},
        "SSL Certificate Renewal": {"steps": [
            {"tool":"ssl.status","params":{},"desc":"Check SSL status"},
            {"tool":"ssl.renew","params":{},"desc":"Renew SSL certificate","risk":"L3"},
        ]},
        "System Cleanup": {"steps": [
            {"tool":"docker.prune","params":{},"desc":"Prune Docker resources","risk":"L2"},
            {"tool":"disk.cleanup","params":{"keep_days":7},"desc":"Clean old temp files"},
        ]},
        "Auto Scale Up": {"steps": [
            {"tool":"server.metrics","params":{},"desc":"Get server metrics"},
            {"tool":"docker.scale","params":{"replicas":3},"desc":"Scale to 3 replicas","risk":"L4"},
        ]},
    }

    @classmethod
    async def parse_and_execute(cls, user_input: str) -> dict:
        """Parse user intent and execute matching workflow template"""
        # 1. Match template by keyword
        matched = None
        for keyword, wf in cls.TEMPLATES.items():
            if keyword.lower() in user_input.lower():
                matched = {"name": keyword, "steps": wf["steps"]}
                break
        
        # 2. No match - try AI plan generation
        if not matched:
            try:
                from tools.ai_client import call_ai
                tools_list = [{"name": t.name, "desc": t.description, "risk": t.risk_level} 
                             for t in registry.list_all()[:30]]
                ai_prompt = f"""Available tools: {json.dumps(tools_list, ensure_ascii=False)}
User request: {user_input}
Generate a JSON workflow plan: {{"name":"plan name","steps":[{{"tool":"tool_name","params":{{}},"desc":"step desc","risk":"L1-L4"}}]}}
Output ONLY the JSON."""
                ai_plan = await call_ai([{"role":"user","content":ai_prompt}], max_tokens=400, temperature=0.2)
                try:
                    j = json.loads(re.search(r'\{[^{}]*"steps"[^{}]*\}', ai_plan, re.DOTALL).group())
                    matched = j
                except:
                    pass
            except:
                pass

            if not matched:
                return {"ok": False, "error": "No matching workflow found",
                        "suggestions": list(cls.TEMPLATES.keys())}
        
        # 3. Execute steps
        wf_id = f"wf_{int(datetime.now().timestamp())}"
        cls.workflows[wf_id] = matched
        
        results = []
        for i, step in enumerate(matched["steps"]):
            step_result = {"step": i+1, "name": step["desc"], "tool": step["tool"], "status": "running"}
            try:
                tool_result = await registry.execute(step["tool"], **(step.get("params", {})))
                step_result["status"] = "done" if tool_result.get("ok", False) else "failed"
                step_result["result"] = tool_result.get("result", tool_result.get("error", ""))
            except Exception as e:
                step_result["status"] = "failed"
                step_result["error"] = str(e)[:200]
            results.append(step_result)
            
            if step_result["status"] == "failed":
                break
        
        wf_result = {
            "id": wf_id, "name": matched["name"], "steps": results,
            "total": len(matched["steps"]),
            "completed": sum(1 for r in results if r["status"] == "done"),
            "failed": sum(1 for r in results if r["status"] == "failed"),
            "time": datetime.now().isoformat()
        }
        state.append_data("workflow_history", wf_result, 50)
        return {"ok": True, "workflow": wf_result}
    
    @classmethod
    def get_status(cls, wf_id: str) -> dict:
        """Get workflow execution status"""
        wf = cls.workflows.get(wf_id)
        if not wf:
            return {"ok": False, "error": "Workflow not found"}
        return {"ok": True, "workflow": wf}
