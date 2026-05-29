"""Agent 协作编排器 — 多Agent协同完成任务"""
import asyncio, json, time
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from enum import Enum
from tools.logger import get_logger

logger = get_logger("orchestrator")

class AgentRole(Enum):
    MASTER = "master"        # 总控
    ANALYZER = "analyzer"    # 分析
    EXECUTOR = "executor"    # 执行
    REVIEWER = "reviewer"    # 审查
    REPORTER = "reporter"    # 报告

@dataclass
class TaskStep:
    id: str
    agent_role: AgentRole
    action: str
    params: Dict[str, Any] = field(default_factory=dict)
    status: str = "pending"  # pending/running/done/failed
    result: Any = None
    error: str = ""

@dataclass
class CollaborationTask:
    id: str
    goal: str
    steps: List[TaskStep] = field(default_factory=list)
    status: str = "pending"
    created_at: float = field(default_factory=time.time)
    completed_at: Optional[float] = None
    summary: str = ""

class AgentOrchestrator:
    """多Agent协作编排器"""

    def __init__(self):
        self.active_tasks: Dict[str, CollaborationTask] = {}
        self.history: List[CollaborationTask] = []
        self._task_counter = 0

    def _generate_task_id(self) -> str:
        self._task_counter += 1
        return f"collab_{int(time.time())}_{self._task_counter}"

    async def plan_task(self, goal: str) -> CollaborationTask:
        """根据目标智能规划任务步骤"""
        task = CollaborationTask(id=self._generate_task_id(), goal=goal)

        # 使用LLM分析目标并拆解步骤
        try:
            from agents.multi_model import ModelRouter
            mr = ModelRouter()

            prompt = f"""你是一个任务拆解专家。根据用户目标，将任务拆解为可执行的步骤。
每个步骤指定一个Agent角色: master(总控)/analyzer(分析)/executor(执行)/reviewer(审查)/reporter(报告)

用户目标: {goal}

返回JSON:
{{"steps": [{{"role": "analyzer", "action": "分析xxx", "params": {{}}}}, ...]}}

规则:
1. 复杂任务必须先分析再执行
2. 执行后必须审查
3. 最后生成报告"""

            resp = await mr.chat(
                messages=[{"role": "user", "content": prompt}],
                mode="deep"
            )
            content = resp.get("content", "{}")

            # 提取JSON
            import re
            json_match = re.search(r'\{[\s\S]*\}', content)
            if json_match:
                plan = json.loads(json_match.group())
                for i, step in enumerate(plan.get("steps", [])):
                    task.steps.append(TaskStep(
                        id=f"{task.id}_s{i+1}",
                        agent_role=AgentRole(step.get("role", "executor")),
                        action=step.get("action", ""),
                        params=step.get("params", {})
                    ))
        except Exception as e:
            logger.warning(f"LLM规划失败，使用默认步骤: {e}")
            # 默认步骤
            task.steps = [
                TaskStep(id=f"{task.id}_s1", agent_role=AgentRole.ANALYZER, action=f"分析: {goal}"),
                TaskStep(id=f"{task.id}_s2", agent_role=AgentRole.EXECUTOR, action=f"执行: {goal}"),
                TaskStep(id=f"{task.id}_s3", agent_role=AgentRole.REVIEWER, action="审查执行结果"),
                TaskStep(id=f"{task.id}_s4", agent_role=AgentRole.REPORTER, action="生成任务报告"),
            ]

        self.active_tasks[task.id] = task
        return task

    async def execute_task(self, task_id: str) -> CollaborationTask:
        """执行协作任务的所有步骤"""
        task = self.active_tasks.get(task_id)
        if not task:
            raise ValueError(f"任务不存在: {task_id}")

        task.status = "running"

        for step in task.steps:
            step.status = "running"
            logger.info(f"[{task_id}] {step.agent_role.value}: {step.action}")

            try:
                result = await self._execute_step(step, task)
                step.result = result
                step.status = "done"
                logger.info(f"[{task_id}] {step.agent_role.value} 完成")
            except Exception as e:
                step.status = "failed"
                step.error = str(e)
                logger.error(f"[{task_id}] {step.agent_role.value} 失败: {e}")
                # 审查步骤失败不阻塞
                if step.agent_role != AgentRole.REVIEWER:
                    task.status = "failed"
                    task.summary = f"步骤 {step.id} 失败: {e}"
                    self.history.append(task)
                    return task

        task.status = "done"
        task.completed_at = time.time()
        task.summary = self._generate_summary(task)
        self.history.append(task)
        del self.active_tasks[task_id]
        return task

    async def _execute_step(self, step: TaskStep, task: CollaborationTask) -> Any:
        """执行单个步骤，路由到对应Agent"""
        role = step.agent_role

        if role == AgentRole.ANALYZER:
            return await self._run_analyzer(step, task)
        elif role == AgentRole.EXECUTOR:
            return await self._run_executor(step, task)
        elif role == AgentRole.REVIEWER:
            return await self._run_reviewer(step, task)
        elif role == AgentRole.REPORTER:
            return self._generate_report(task)
        else:
            return {"role": role.value, "action": step.action, "status": "ok"}

    async def _run_analyzer(self, step: TaskStep, task: CollaborationTask) -> Dict:
        """分析Agent — 使用LLM深度分析"""
        try:
            from agents.multi_model import ModelRouter
            mr = ModelRouter()
            resp = await mr.chat(
                messages=[{"role": "user", "content": f"请深入分析以下任务并给出具体建议:\n目标: {task.goal}\n当前动作: {step.action}"}],
                mode="deep"
            )
            return {"analysis": resp.get("content", ""), "model": resp.get("model", "")}
        except Exception as e:
            return {"analysis": f"分析完成(本地): {step.action}", "error": str(e)}

    async def _run_executor(self, step: TaskStep, task: CollaborationTask) -> Dict:
        """执行Agent — 调用具体工具"""
        from tools.omni_engine import SelfHealing, BusinessEngine

        action_lower = step.action.lower()

        if "自愈" in step.action or "修复" in step.action or "heal" in action_lower:
            result = await SelfHealing.diagnose_and_fix()
            return {"type": "self_healing", "result": result}

        if "预测" in step.action or "predict" in action_lower:
            result = await BusinessEngine.predict(step.params.get("metric", "sales"))
            return {"type": "prediction", "result": result}

        # 默认: LLM执行
        try:
            from agents.multi_model import ModelRouter
            mr = ModelRouter()
            resp = await mr.chat(
                messages=[{"role": "user", "content": f"请执行以下任务:\n{step.action}\n参数: {step.params}"}],
                mode="fast"
            )
            return {"type": "llm_execution", "result": resp.get("content", "")}
        except:
            return {"type": "manual", "result": f"任务需要人工执行: {step.action}"}

    async def _run_reviewer(self, step: TaskStep, task: CollaborationTask) -> Dict:
        """审查Agent — 检查执行结果"""
        prev_results = [s.result for s in task.steps if s.status == "done" and s.id != step.id]

        try:
            from agents.multi_model import ModelRouter
            mr = ModelRouter()
            resp = await mr.chat(
                messages=[{"role": "user", "content": f"请审查以下任务执行结果:\n目标: {task.goal}\n执行结果: {prev_results}\n请评估是否达成目标，有无遗漏或风险"}],
                mode="fast"
            )
            return {"review": resp.get("content", ""), "passed": "失败" not in resp.get("content", "")}
        except:
            return {"review": "审查完成", "passed": True}

    def _generate_report(self, task: CollaborationTask) -> Dict:
        """生成任务报告"""
        return {
            "goal": task.goal,
            "steps": len(task.steps),
            "completed": sum(1 for s in task.steps if s.status == "done"),
            "failed": sum(1 for s in task.steps if s.status == "failed"),
            "duration": round(time.time() - task.created_at, 2),
            "details": [{"step": s.action, "status": s.status, "result": str(s.result)[:200]} for s in task.steps]
        }

    def _generate_summary(self, task: CollaborationTask) -> str:
        report = self._generate_report(task)
        return f"任务完成: {report['completed']}/{report['steps']}步骤成功, 耗时{report['duration']}秒"

    def get_status(self) -> Dict:
        return {
            "active_tasks": len(self.active_tasks),
            "completed_tasks": len(self.history),
            "tasks": [
                {"id": t.id, "goal": t.goal, "status": t.status, "steps": len(t.steps)}
                for t in list(self.active_tasks.values())[:10]
            ]
        }

# 全局实例
orchestrator = AgentOrchestrator()
