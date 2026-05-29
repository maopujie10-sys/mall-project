"""AI工作流引擎 — 多步任务自动拆解与执行"""
import asyncio, json, re
from datetime import datetime
from state import state
from tools.registry import registry

class WorkflowEngine:
    workflows = {}

    # 内置模板
    TEMPLATES = {
        "下架": {"steps": [
            {"tool":"product.list","params":{"status":"low_stock"},"desc":"查找低库存商品"},
            {"tool":"product.batch_offline","params":{},"desc":"批量下架","risk":"L3"},
            {"tool":"report.generate","params":{"type":"offline_report"},"desc":"生成下架报告"},
        ]},
        "备份": {"steps": [
            {"tool":"db.backup","params":{},"desc":"备份数据库","risk":"L3"},
            {"tool":"file.archive","params":{"type":"backup"},"desc":"归档备份文件"},
        ]},
        "部署": {"steps": [
            {"tool":"git.pull","params":{},"desc":"拉取最新代码","risk":"L3"},
            {"tool":"docker.build","params":{"service":"all"},"desc":"构建镜像","risk":"L3"},
            {"tool":"docker.deploy","params":{"service":"all"},"desc":"部署服务","risk":"L4"},
        ]},
        "巡检": {"steps": [
            {"tool":"server.status","params":{},"desc":"检查服务器状态"},
            {"tool":"docker.ps","params":{},"desc":"检查Docker容器"},
            {"tool":"nginx.status","params":{},"desc":"检查Nginx状态"},
            {"tool":"db.status","params":{},"desc":"检查数据库状态"},
            {"tool":"rotation.domains","params":{},"desc":"检查域名健康"},
        ]},
        "SSL": {"steps": [
            {"tool":"ssl.status","params":{},"desc":"查询SSL证书状态"},
            {"tool":"ssl.renew","params":{},"desc":"续签到期的证书","risk":"L3"},
        ]},
        "清理": {"steps": [
            {"tool":"docker.prune","params":{},"desc":"清理Docker缓存","risk":"L2"},
            {"tool":"disk.cleanup","params":{"keep_days":7},"desc":"清理旧日志/备份"},
        ]},
        "扩容": {"steps": [
            {"tool":"server.metrics","params":{},"desc":"获取当前负载"},
            {"tool":"docker.scale","params":{"replicas":3},"desc":"扩容服务","risk":"L4"},
        ]},
    }

    @classmethod
    async def parse_and_execute(cls, user_input: str) -> dict:
        """解析用户自然语言输入，拆解为工作流步骤并执行"""
        # 1. 模板匹配
        matched = None
        for keyword, wf in cls.TEMPLATES.items():
            if keyword in user_input:
                matched = {"name": f"{keyword}工作流", "steps": wf["steps"]}
                break
        
        # 2. 如果没有匹配模板，尝试AI生成工作流
        if not matched:
            try:
                from tools.ai_client import call_ai
                tools_list = [{"name": t.name, "desc": t.description, "risk": t.risk_level} 
                             for t in registry.list_all()[:30]]
                ai_prompt = f"""你有以下可用工具: {json.dumps(tools_list,ensure_ascii=False)}
用户想: {user_input}
请生成一个工作流JSON: {{"name":"工作流名","steps":[{{"tool":"工具名","params":{{}},"desc":"步骤描述","risk":"L1-L4"}}]}}
只返回JSON。"""
                ai_plan = await call_ai([{"role":"user","content":ai_prompt}], max_tokens=400, temperature=0.2)
                try:
                    j = json.loads(re.search(r'\{[^{}]*"steps"[^{}]*\}', ai_plan, re.DOTALL).group())
                    matched = j
                except:
                    pass
            
            if not matched:
                return {"ok": False, "error": "未能识别任务类型，请尝试: 部署/备份/巡检/下架/SSL/清理/扩容", 
                        "suggestions": list(cls.TEMPLATES.keys())}
        
        # 3. 创建工作流ID并执行
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
        """查询工作流状态"""
        wf = cls.workflows.get(wf_id)
        if not wf:
            return {"ok": False, "error": "工作流不存在"}
        return {"ok": True, "workflow": wf}