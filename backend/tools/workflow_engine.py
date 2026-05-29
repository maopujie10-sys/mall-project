"""AI工作流引擎 — 多步任务自动拆解与执行"""
import asyncio, json, re
from datetime import datetime
from state import state
from tools.registry import registry

class WorkflowEngine:
    workflows = {}

    @classmethod
    async def parse_and_execute(cls, user_input: str) -> dict:
        """解析用户自然语言输入，拆解为工作流步骤"""
        # 内置工作流模板
        templates = {
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
        }
        # 智能匹配
        matched = None
        for keyword, wf in templates.items():
            if keyword in user_input:
                matched = {"name": f"{keyword}工作流", "steps": wf["steps"]}
                break
        if not matched:
            return {"ok": False, "error": "未能识别的任务类型", "suggestions": list(templates.keys())}
        # 创建工作流ID
        wf_id = f"wf_{int(datetime.now().timestamp())}"
        cls.workflows[wf_id] = matched
        # 逐步骤执行
        results = []
        for i, step in enumerate(matched["steps"]):
            step_result = {"step": i+1, "name": step["desc"], "tool": step["tool"], "status": "running"}
            try:
                tool_result = await registry.execute(step["tool"], **(step.get("params",{})))
                step_result["status"] = "done" if tool_result.get("ok",False) else "failed"
                step_result["result"] = tool_result.get("result", tool_result.get("error",""))
            except Exception as e:
                step_result["status"] = "failed"
                step_result["error"] = str(e)
            results.append(step_result)
            # 失败则中断
            if step_result["status"] == "failed":
                break
        wf_result = {"id": wf_id, "name": matched["name"], "steps": results,
                     "total": len(matched["steps"]), "completed": sum(1 for r in results if r["status"]=="done"),
                     "failed": sum(1 for r in results if r["status"]=="failed"), "time": datetime.now().isoformat()}
        state.append_data("workflow_history", wf_result, 50)
        return {"ok": True, "workflow": wf_result}
