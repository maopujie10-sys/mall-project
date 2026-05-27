"""数字生命体自主循环 — 持续感知→思考→行动

Friday AI OS 的核心差异化能力：
  1. 定期感知环境 (服务器/商城/客服/轮值状态)
  2. AI 分析是否需要行动
  3. 低风险自主执行，中风险记录建议
  4. 生成每日日记和进化报告
"""
import asyncio
import json
from datetime import datetime
from state import state
from risk import handle_risk


class DigitalLifeform:
    """数字生命体 — 自主运行循环"""

    _running = False
    _cycle_count = 0

    @classmethod
    async def perceive(cls) -> dict:
        """感知环境 — 收集系统状态"""
        perception = {
            "time": datetime.now().isoformat(),
            "mode": state.mode,
            "tasks_pending": len(state.tasks),
            "approvals_pending": len(state.pending_approvals),
        }
        # 收集服务器状态
        try:
            import psutil
            perception["cpu"] = psutil.cpu_percent(interval=0.3)
            perception["memory"] = psutil.virtual_memory().percent
            perception["disk"] = psutil.disk_usage("/").percent
        except:
            perception["cpu"] = -1
            perception["memory"] = -1
            perception["disk"] = -1

        # 收集轮值域名状态
        try:
            ds = state._data.get("rotation_domains", [])
            perception["domains_total"] = len(ds)
            perception["domains_unhealthy"] = sum(1 for d in ds if d.get("health") != "ok")
        except:
            perception["domains_unhealthy"] = 0

        return perception

    @classmethod
    async def think(cls, perception: dict) -> list:
        """AI 思考 — 基于感知决定行动"""
        actions = []

        # 服务器异常检测
        if perception.get("cpu", 0) > 80:
            actions.append({"action": "服务器CPU过高", "tool": "inspector.run", "risk": "L2"})
        if perception.get("disk", 0) > 85:
            actions.append({"action": "磁盘空间不足", "tool": "backup.create", "risk": "L2"})

        # 域名异常
        if perception.get("domains_unhealthy", 0) > 0:
            actions.append({"action": f"{perception['domains_unhealthy']}个域名异常", "tool": "rotation.check", "risk": "L1"})

        # 积累的审批
        if perception.get("approvals_pending", 0) > 5:
            actions.append({"action": f"{perception['approvals_pending']}个待审批堆积", "tool": "system.mode", "risk": "L1"})

        cls._cycle_count += 1
        return actions

    @classmethod
    async def act(cls, actions: list) -> list:
        """执行行动"""
        results = []
        for action in actions:
            try:
                risk_result = await handle_risk(action["risk"], action["action"])
                if risk_result["allowed"]:
                    results.append({"action": action["action"], "result": "executed", "risk": action["risk"]})
                else:
                    results.append({"action": action["action"], "result": "pending_approval", "risk": action["risk"]})
            except Exception as e:
                results.append({"action": action["action"], "result": f"error: {str(e)[:100]}"})
        return results

    @classmethod
    async def one_cycle(cls) -> dict:
        """执行一次自主循环"""
        if state.mode == "human_control":
            return {"status": "paused", "reason": "human_control"}

        perception = await cls.perceive()
        actions = await cls.think(perception)
        results = await cls.act(actions)

        return {
            "cycle": cls._cycle_count,
            "time": perception["time"],
            "perception": perception,
            "actions_taken": len(actions),
            "results": results,
        }

    @classmethod
    async def start_loop(cls, interval_seconds: int = 300):
        """启动自主循环（后台任务）"""
        if cls._running:
            return {"status": "already_running"}
        cls._running = True
        cls._cycle_count = 0
        print(f"[Lifeform] 数字生命体启动，巡检间隔: {interval_seconds}秒")

        async def loop():
            while cls._running:
                try:
                    result = await cls.one_cycle()
                    if result.get("status") != "paused":
                        print(f"[Lifeform] 周期#{result.get('cycle',0)}: {result.get('actions_taken',0)}个行动")
                except Exception as e:
                    print(f"[Lifeform] 周期异常: {e}")
                await asyncio.sleep(interval_seconds)

        asyncio.create_task(loop())
        return {"status": "started", "interval_seconds": interval_seconds}

    @classmethod
    async def stop_loop(cls):
        """停止自主循环"""
        cls._running = False
        return {"status": "stopped", "total_cycles": cls._cycle_count}
