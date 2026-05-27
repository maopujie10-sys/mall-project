"""Master Agent — Friday AI OS 总控大脑
职责：任务拆解、Agent调度、上下文管理、长期目标追踪"""
import json
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
    status: str = "pending"  # pending/running/done/failed
    created_at: str = ""
    completed_at: str = ""

class MasterAgent:
    """总控Agent — 接收用户意图，拆解为子任务，分配给各Agent"""

    AGENTS = {
        "code": "代码编写/修复/Bug分析",
        "devops": "服务器/Docker/Nginx/部署",
        "vision": "图片识别/视频分析/OCR",
        "trend": "热点监控/舆情分析/趋势预测",
        "memory": "长期记忆/知识检索/经验学习",
        "heal": "异常检测/自动修复/服务恢复",
    }

    @staticmethod
    def analyze_intent(message: str) -> dict:
        """分析用户意图，决定调用哪些Agent"""
        msg_lower = message.lower()
        agents_needed = []

        # 代码相关
        if any(kw in msg_lower for kw in ["代码","bug","报错","接口","sql","修复","开发","写一个"]):
            agents_needed.append("code")

        # DevOps相关
        if any(kw in msg_lower for kw in ["服务器","docker","nginx","部署","重启","端口","cpu","内存"]):
            agents_needed.append("devops")

        # 视觉相关
        if any(kw in msg_lower for kw in ["图片","视频","识别","ocr","看图","分析图片"]):
            agents_needed.append("vision")

        # 热点相关
        if any(kw in msg_lower for kw in ["热点","抖音","微博","热搜","趋势","舆情"]):
            agents_needed.append("trend")

        # 记忆相关
        if any(kw in msg_lower for kw in ["记忆","记住","上次","之前","历史","学习"]):
            agents_needed.append("memory")

        # 自愈相关
        if any(kw in msg_lower for kw in ["异常","挂了","恢复","自动修复","巡检"]):
            agents_needed.append("heal")

        # 兜底：全能模式
        if not agents_needed:
            agents_needed = ["code", "devops", "memory"]

        return {
            "intent": message[:100],
            "agents": agents_needed,
            "complexity": "high" if len(agents_needed) > 3 else "medium" if len(agents_needed) > 1 else "low",
            "timestamp": datetime.now().isoformat(),
        }

    @staticmethod
    def create_task_plan(goal: str, agents: list) -> list:
        """根据目标和Agent列表生成执行计划"""
        plan = []
        for i, agent in enumerate(agents):
            plan.append({
                "step": i + 1,
                "agent": agent,
                "action": f"{MasterAgent.AGENTS.get(agent, '执行任务')}",
                "status": "pending",
            })
        return plan

    @staticmethod
    def get_agent_status() -> list:
        """获取所有Agent状态"""
        return [
            {"id": "master", "name": "Master Agent", "icon": "🧠", "status": "active", "tasks": 0},
            {"id": "code", "name": "Code Agent", "icon": "💻", "status": "idle", "tasks": 0},
            {"id": "devops", "name": "DevOps Agent", "icon": "⚙️", "status": "active", "tasks": 0},
            {"id": "vision", "name": "Vision Agent", "icon": "👁️", "status": "idle", "tasks": 0},
            {"id": "trend", "name": "Trend Agent", "icon": "📡", "status": "idle", "tasks": 0},
            {"id": "memory", "name": "Memory Agent", "icon": "💾", "status": "active", "tasks": 0},
            {"id": "heal", "name": "Self-Healing Agent", "icon": "🛡️", "status": "idle", "tasks": 0},
        ]
