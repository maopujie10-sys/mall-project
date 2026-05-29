"""多Agent协作协议 — 任务拆解+Agent调度+结果汇总"""
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
    """多Agent协作引擎"""
    
    AGENT_CAPABILITIES = {
        "trend": ["竞品分析", "热点监控", "趋势预测", "舆情分析"],
        "scraper": ["商品采集", "数据抓取", "价格监控"],
        "vision": ["图片分析", "OCR识别", "视频处理"],
        "code": ["代码生成", "Bug修复", "API开发"],
        "devops": ["部署检查", "容器管理", "Nginx配置"],
        "heal": ["异常检测", "自动修复", "服务恢复"],
        "memory": ["知识检索", "经验学习", "上下文提供"],
    }
    
    @classmethod
    async def analyze_and_delegate(cls, goal: str) -> CollaborationTask:
        """分析目标并拆解为子任务"""
        task_id = f"collab_{datetime.now().strftime('%H%M%S')}"
        task = CollaborationTask(
            id=task_id, title=goal,
            created_at=datetime.now().isoformat()
        )
        
        # 基于关键词匹配Agent
        goal_lower = goal.lower()
        assigned = []
        
        for agent, capabilities in cls.AGENT_CAPABILITIES.items():
            for cap in capabilities:
                if any(w in goal_lower for w in cap.lower().split()):
                    if agent not in assigned:
                        assigned.append(agent)
                        task.assigned_agents[agent] = cap
        
        # 如果没有匹配，默认用trend+memory
        if not assigned:
            assigned = ["trend", "memory"]
            task.assigned_agents = {"trend": "信息采集", "memory": "知识补充"}
        
        # 生成子任务
        task.subtasks = [
            {"id": f"{task_id}_s{i+1}", "agent": agent, "action": cap, "status": "pending"}
            for i, (agent, cap) in enumerate(task.assigned_agents.items())
        ]
        
        logger.info(f"协作任务创建: {goal} -> {len(task.subtasks)}个子任务, {len(assigned)}个Agent")
        return task
    
    @classmethod
    async def execute_subtask(cls, task: CollaborationTask, subtask_id: str) -> dict:
        """执行单个子任务"""
        for st in task.subtasks:
            if st["id"] == subtask_id:
                st["status"] = "running"
                agent = st["agent"]
                try:
                    # 调度到对应Agent
                    if agent == "trend":
                        from agents.trend_agent import TrendAgent
                        result = await TrendAgent.analyze(task.title)
                    elif agent == "scraper":
                        from tools.scraper_engine import ScraperEngine
                        result = {"products": len(ScraperEngine.get_products()["items"])}
                    elif agent == "vision":
                        result = {"status": "Vision Agent已就绪"}
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
        return {"ok": False, "error": "子任务不存在"}
    
    @classmethod
    async def execute_all(cls, goal: str) -> dict:
        """完整协作流程：分析->拆解->并行执行->汇总"""
        task = await cls.analyze_and_delegate(goal)
        task.status = "running"
        
        # 并行执行所有子任务
        tasks = [cls.execute_subtask(task, st["id"]) for st in task.subtasks]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # 汇总结果
        success_count = sum(1 for r in results if isinstance(r, dict) and r.get("ok"))
        task.status = "done"
        task.completed_at = datetime.now().isoformat()
        
        summary = f"## 协作任务完成\n"
        summary += f"**目标**: {goal}\n"
        summary += f"**Agent**: {', '.join(task.assigned_agents.keys())}\n"
        summary += f"**结果**: {success_count}/{len(task.subtasks)} 成功\n\n"
        for agent, result in task.results.items():
            status = "✅" if result.get("success") else "❌"
            summary += f"- {status} **{agent}**: {json.dumps(result, ensure_ascii=False)[:100]}\n"
        
        logger.info(f"协作完成: {goal} -> {success_count}/{len(task.subtasks)}")
        return {"ok": True, "task": task.__dict__, "summary": summary, "success_rate": f"{success_count}/{len(task.subtasks)}"}

# 全局实例
agent_collab = AgentCollaboration()
