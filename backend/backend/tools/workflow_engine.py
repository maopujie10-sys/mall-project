''"AI -- ''"
import asyncio, json, re
from datetime import datetime
from state import state
from tools.registry import registry

class WorkflowEngine:
    workflows = {}

    
    TEMPLATES = {
        '': {"steps": [
            {"tool":"product.list","params":{"status":"low_stock"},"desc":''},
            {"tool":"product.batch_offline","params":{},"desc":'',"risk":"L3"},
            {"tool":"report.generate","params":{"type":"offline_report"},"desc":''},
        ]},
        '': {"steps": [
            {"tool":"db.backup","params":{},"desc":'',"risk":"L3"},
            {"tool":"file.archive","params":{"type":"backup"},"desc":''},
        ]},
        '': {"steps": [
            {"tool":"git.pull","params":{},"desc":'',"risk":"L3"},
            {"tool":"docker.build","params":{"service":"all"},"desc":'',"risk":"L3"},
            {"tool":"docker.deploy","params":{"service":"all"},"desc":'',"risk":"L4"},
        ]},
        '': {"steps": [
            {"tool":"server.status","params":{},"desc":''},
            {"tool":"docker.ps","params":{},"desc":"Docker"},
            {"tool":"nginx.status","params":{},"desc":"Nginx"},
            {"tool":"db.status","params":{},"desc":''},
            {"tool":"rotation.domains","params":{},"desc":''},
        ]},
        "SSL": {"steps": [
            {"tool":"ssl.status","params":{},"desc":"SSL"},
            {"tool":"ssl.renew","params":{},"desc":'',"risk":"L3"},
        ]},
        '': {"steps": [
            {"tool":"docker.prune","params":{},"desc":"Docker","risk":"L2"},
            {"tool":"disk.cleanup","params":{"keep_days":7},"desc":"/"},
        ]},
        '': {"steps": [
            {"tool":"server.metrics","params":{},"desc":''},
            {"tool":"docker.scale","params":{"replicas":3},"desc":'',"risk":"L4"},
        ]},
    }

    @classmethod
    async def parse_and_execute(cls, user_input: str) -> dict:
        ''",''"
        # 1. 
        matched = None
        for keyword, wf in cls.TEMPLATES.items():
            if keyword in user_input:
                matched = {"name": f"{keyword}", "steps": wf["steps"]}
                break
        
        # 2. ,AI
        if not matched:
            try:
                from tools.ai_client import call_ai
                tools_list = [{"name": t.name, "desc": t.description, "risk": t.risk_level} 
                             for t in registry.list_all()[:30]]
                ai_prompt = f''": {json.dumps(tools_list,ensure_ascii=False)}
: {user_input}
JSON: {{"name":'',"steps":[{{"tool":'',"params":{{}},"desc":'',"risk":"L1-L4"}}]}}
JSON.''"
                ai_plan = await call_ai([{"role":"user","content":ai_prompt}], max_tokens=400, temperature=0.2)
                try:
                    j = json.loads(re.search(r'\{[^{}]*"steps"[^{}]*\}', ai_plan, re.DOTALL).group())
                    matched = j
                except:
                    pass
            except:
                pass

            if not matched:
                return {"ok": False, "error": ",: ////SSL//", 
                        "suggestions": list(cls.TEMPLATES.keys())}
        
        # 3. ID
        wf_id = f"wf_{int(datetime.now().timestamp())}"
        cls.workflows[wf_id] = matched
        
        results = []
        for i, step in enumerate(matched["steps"]):
            step_result = {"step": i+1, "name": step["desc"], "tool": step["tool"], "status": "running"}
            try:
                tool_result = await registry.execute(step["tool"], **(step.get("params", {})))
                step_result["status"] = "done" if tool_result.get("ok", False) else "failed"
                step_result["result"] = tool_result.get("result", tool_result.get("error", ''))
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
        ''''''
        wf = cls.workflows.get(wf_id)
        if not wf:
            return {"ok": False, "error": ''}
        return {"ok": True, "workflow": wf}