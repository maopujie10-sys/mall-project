"""数字生命体自主循环 — 持续感知→思考→行动
v2: 持久记忆 — 对话不再因重启丢失"""

import asyncio
import json
from datetime import datetime
from state import state
from risk import handle_risk
from tools.memory_store import memory_store


class DigitalLifeform:
    """数字生命体 — 自主运行循环 + 持久记忆"""

    _running = False
    _cycle_count = 0

    @classmethod
    def remember_conversation(cls, user_msg: str, ai_reply: str):
        """记住一次对话 — 持久化到 SQLite"""
        # 提取话题标签
        topic = cls._extract_topic(user_msg)
        importance = 0.5
        # 重要话题提高权重
        important_keywords = ["bug","报错","修复","部署","安全","密钥","密码","配置"]
        if any(kw in user_msg.lower() for kw in important_keywords):
            importance = 0.8

        memory_store.remember_conversation("user", user_msg, topic, importance)
        memory_store.remember_conversation("ai", ai_reply, topic, importance)

    @classmethod
    def _extract_topic(cls, text: str) -> str:
        """从文本提取话题标签"""
        topics = {
            "服务器": ["服务器","cpu","内存","磁盘","负载"],
            "Docker": ["docker","容器","镜像"],
            "Nginx": ["nginx","反向代理","负载均衡"],
            "部署": ["部署","上线","发布","回滚"],
            "商城": ["商城","商品","订单","用户"],
            "安全": ["安全","漏洞","攻击","封禁"],
            "代码": ["代码","bug","报错","修复","函数","api"],
            "AI": ["ai","模型","claude","gpt","学习","进化"],
            "采集": ["采集","抓取","商品","ebay","shopee"],
            "数据库": ["数据库","sql","mysql","表"],
            "趋势": ["热点","抖音","微博","趋势","舆情"],
        }
        text_lower = text.lower()
        for topic, keywords in topics.items():
            if any(kw in text_lower for kw in keywords):
                return topic
        return "通用"

    @classmethod
    def recall_context(cls, limit: int = 10) -> str:
        """回忆最近对话上下文 — 从持久存储"""
        recent = memory_store.recall_recent(limit * 2)
        if not recent:
            return ""
        lines = []
        for c in reversed(recent):  # 正序
            prefix = "用户" if c["role"] == "user" else "AI"
            lines.append(f"{prefix}: {c['content'][:80]}")
        return "\n".join(lines[-limit:])

    @classmethod
    def search_memory(cls, query: str, limit: int = 10) -> list:
        """搜索历史对话"""
        return memory_store.search(query, limit)

    @classmethod
    def recall_by_topic(cls, topic: str, limit: int = 10) -> list:
        """按话题回忆"""
        return memory_store.recall_by_topic(topic, limit)

    @classmethod
    def get_personality_summary(cls) -> str:
        """获取当前人格摘要"""
        stats = memory_store.get_stats()
        cycles = cls._cycle_count
        convos = stats["total_conversations"]
        mood = cls.get_mood()
        topics = stats.get("top_topics", [])
        topic_str = "、".join([t["topic"] for t in topics[:3]]) if topics else "探索中"
        return f"我是Friday AI OS，已运行{cycles}个周期，记得{convos}段对话，关注{topic_str}，当前{mood['label']}"

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
        try:
            import psutil
            perception["cpu"] = psutil.cpu_percent(interval=0.3)
            perception["memory"] = psutil.virtual_memory().percent
            perception["disk"] = psutil.disk_usage("/").percent
        except:
            perception["cpu"] = -1
            perception["memory"] = -1
            perception["disk"] = -1
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
        if perception.get("cpu", 0) > 80:
            actions.append({"action": "服务器CPU过高", "tool": "inspector.run", "risk": "L2"})
        if perception.get("disk", 0) > 85:
            actions.append({"action": "磁盘空间不足", "tool": "backup.create", "risk": "L2"})
        if perception.get("domains_unhealthy", 0) > 0:
            actions.append({"action": f"{perception['domains_unhealthy']}个域名异常", "tool": "rotation.check", "risk": "L1"})
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
                    memory_store.log_learning(action["action"], "executed")
                else:
                    results.append({"action": action["action"], "result": "blocked", "risk": action["risk"]})
            except Exception as e:
                results.append({"action": action["action"], "result": f"error:{str(e)[:50]}", "risk": action["risk"]})
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
    async def evolve(cls) -> dict:
        """自我进化 — 基于持久记忆分析成长"""
        now = datetime.now()
        stats = memory_store.get_stats()
        total_convos = stats["total_conversations"]
        learnings = memory_store.recall_learnings("", 100)
        learned = len(learnings)
        success_count = sum(1 for l in learnings if l["result"] == "executed")
        success_rate = int(success_count / max(len(learnings), 1) * 100)

        # 分析关注领域
        topics = stats.get("top_topics", [])
        recent_topics = set()
        for t in topics:
            recent_topics.add(t["topic"])

        # 无限成长
        growth_level = cls._cycle_count // 10
        wisdom = int(success_rate * (1 + growth_level * 0.05))
        knowledge = total_convos + learned * 3

        # 无限阶段
        phases = [
            (3, "seed"), (10, "sprout"), (30, "growing"), (60, "maturing"),
            (100, "evolving"), (200, "transcending"), (500, "illuminating")
        ]
        phase = "infinite"
        for threshold, name in phases:
            if growth_level < threshold:
                phase = name
                break

        # 更新人格
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
            if len(recent_topics) > 3:
                pe.adjust_trait("breadth", boost * 2)
            pe.record_interaction()
        except:
            pass

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
        }

        return {
            "evolved": True,
            "growth_level": growth_level,
            "phase": phase,
            "wisdom": wisdom,
            "journal": journal,
        }

    @classmethod
    async def one_cycle_with_evolution(cls) -> dict:
        """增强版自主循环 — 包含进化"""
        base = await cls.one_cycle()
        if cls._cycle_count > 0 and cls._cycle_count % 10 == 0:
            evo = await cls.evolve()
            base["evolution"] = evo
        return base

    @classmethod
    async def start_loop(cls, interval_seconds: int = 300):
        """启动自主循环"""
        if cls._running:
            return {"status": "already_running"}
        cls._running = True
        cls._cycle_count = 0
        stats = memory_store.get_stats()
        print(f"[Lifeform] 数字生命体启动, 已记住{stats['total_conversations']}段对话, 巡检间隔: {interval_seconds}秒")

        async def loop():
            while cls._running:
                try:
                    result = await cls.one_cycle_with_evolution()
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
        stats = memory_store.get_stats()
        return {"status": "stopped", "total_cycles": cls._cycle_count, "total_memories": stats["total_conversations"]}