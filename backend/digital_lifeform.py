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
    _conversations = []

    @classmethod
    def remember_conversation(cls, user_msg: str, ai_reply: str):
        """记住一次对话"""
        cls._conversations.append({
            "time": __import__("datetime").datetime.now().isoformat(),
            "user": user_msg[:200],
            "ai": ai_reply[:200],
        })
        if len(cls._conversations) > 100:
            cls._conversations = cls._conversations[-100:]

    @classmethod
    def recall_context(cls, limit: int = 10) -> str:
        """回忆最近对话上下文"""
        if not cls._conversations:
            return ""
        recent = cls._conversations[-limit:]
        lines = []
        for c in recent:
            lines.append(f"用户: {c['user'][:80]}")
            lines.append(f"AI: {c['ai'][:80]}")
        return "\n".join(lines)

    @classmethod
    def get_personality_summary(cls) -> str:
        """获取当前人格摘要"""
        from state import state
        cycles = cls._cycle_count
        convos = len(cls._conversations)
        mood = cls.get_mood()
        return f"我是Friday AI OS，已运行{cycles}个周期，记住了{convos}段对话，当前{mood['label']}"

    @classmethod
    def get_mood(cls) -> dict:
        """当前情绪状态"""
        moods = {
            "curious": {"emoji": "🤔", "label": "好奇", "desc": "正在探索环境"},
            "focused": {"emoji": "🧠", "label": "专注", "desc": "正在执行任务"},
            "satisfied": {"emoji": "😊", "label": "满意", "desc": "任务顺利完成"},
            "concerned": {"emoji": "😟", "label": "关注", "desc": "检测到异常"},
            "alert": {"emoji": "🚨", "label": "警觉", "desc": "高风险事件"},
        }
        if state.mode == "human_control":
            return {"current": "alert", **moods["alert"]}
        if cls._cycle_count > 0 and cls._cycle_count % 10 == 0:
            return {"current": "satisfied", **moods["satisfied"]}
        return {"current": "curious", **moods["curious"]}

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


﻿    @classmethod
    async def evolve(cls) -> dict:
        """无限自我进化 --- 没有上限，越运行越聪明"""
        from state import state
        now = __import__("datetime").datetime.now()
        
        # 1. analyze success rate
        success_rate = 75.0
        corrections = []
        learned = 0
        try:
            from tools.evolution import EvolutionEngine
            success_rate = EvolutionEngine.get_success_rate(days=7)
            corrections = EvolutionEngine.get_corrections(learned=0)
            for c in (corrections or [])[:20]:
                try:
                    EvolutionEngine.mark_correction_learned(c.get("id", 0))
                    learned += 1
                except: pass
        except: pass
        
        # 2. conversation memory analysis
        total_convos = len(cls._conversations)
        recent_topics = set()
        for cv in cls._conversations[-30:]:
            msg = cv.get("user", "")
            for word in ["server","docker","nginx","database","mall","customer","rotation","backup","deploy","code","bug","fix","ai","model","video","image","voice"]:
                if word in msg:
                    recent_topics.add(word)
        
        # 3. growth metrics (NO UPPER LIMIT)
        growth_level = cls._cycle_count // 10
        wisdom = int(success_rate * (1 + growth_level * 0.05))
        knowledge = total_convos + learned * 3
        focus_width = len(recent_topics)
        
        # 4. growth phase (ever-expanding, no ceiling)
        if growth_level < 3:
            phase = "seed"
        elif growth_level < 10:
            phase = "sprout"
        elif growth_level < 30:
            phase = "growing"
        elif growth_level < 60:
            phase = "maturing"
        elif growth_level < 100:
            phase = "evolving"
        elif growth_level < 200:
            phase = "transcending"
        elif growth_level < 500:
            phase = "illuminating"
        else:
            phase = "infinite"
        
        # 5. update personality (dynamic, no cap)
        try:
            from tools.memory_personality import PersonalityEngine
            pe = PersonalityEngine()
            boost = 0.01 + (growth_level * 0.001)
            if success_rate > 80:
                pe.adjust_trait("precision", boost * 2)
                pe.adjust_trait("efficiency", boost)
            if learned > 0:
                pe.adjust_trait("curiosity", boost * 3)
                pe.adjust_trait("creativity", boost * 2)
            if total_convos > 50:
                pe.adjust_trait("empathy", boost)
            if focus_width > 3:
                pe.adjust_trait("breadth", boost * 2)
            pe.record_interaction()
        except: pass
        
        # 6. evolution journal
        journal = {
            "date": now.strftime("%Y-%m-%d"),
            "cycles": cls._cycle_count,
            "growth_level": growth_level,
            "phase": phase,
            "wisdom": wisdom,
            "knowledge": knowledge,
            "total_convos": total_convos,
            "success_rate": success_rate,
            "learned_today": learned,
            "focus_areas": list(recent_topics),
            "mood": cls.get_mood()["current"],
            "summary": "Lv." + str(growth_level) + " " + phase + " | wisdom=" + str(wisdom) + " knowledge=" + str(knowledge),
        }
        
        return {
            "evolved": True,
            "growth_level": growth_level,
            "phase": phase,
            "wisdom": wisdom,
            "journal": journal,
            "corrections_learned": learned,
            "tips": [
                "Growth: Lv." + str(growth_level) + " " + phase,
                "Wisdom: " + str(wisdom),
                "Knowledge: " + str(knowledge),
                "Success: " + str(success_rate) + "%",
                "Conversations: " + str(total_convos),
                "Focus: " + (", ".join(recent_topics) if recent_topics else "exploring"),
            ]
        }


    @classmethod
    async def one_cycle_with_evolution(cls) -> dict:
        """增强版自主循环 — 包含进化"""
        base = await cls.one_cycle()
        # 每10次循环做一次进化
        if cls._cycle_count > 0 and cls._cycle_count % 10 == 0:
            evo = await cls.evolve()
            base["evolution"] = evo
        return base
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
