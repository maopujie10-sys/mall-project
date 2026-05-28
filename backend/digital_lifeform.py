"""数字生命体 v3 — 自主循环+反思+洞察+主动行动+做梦+情绪"""

import asyncio, json, random, time
from datetime import datetime, timedelta
from state import state
from tools.memory_store import memory_store

class DigitalLifeform:
    _running = False
    _cycle_count = 0
    _mood_score = 0.75  # 0-1
    _wisdom = 0
    _insights = []
    _dream_log = []
    _personality_traits = {"curiosity":0.7,"precision":0.6,"creativity":0.5,"empathy":0.4,"efficiency":0.6}
    _last_reflection = ""
    _last_insight_time = None

    # ===== 记忆系统 =====
    @classmethod
    def remember_conversation(cls, user_msg, ai_reply):
        topic = cls._extract_topic(user_msg)
        importance = 0.8 if any(kw in user_msg.lower() for kw in ["bug","报错","修复","部署","安全","密钥","密码","配置","上线"]) else 0.5
        memory_store.remember_conversation("user", user_msg, topic, importance)
        memory_store.remember_conversation("ai", ai_reply, topic, importance)

    @classmethod
    def _extract_topic(cls, text):
        topics = {"服务器":["服务器","cpu","内存","磁盘","负载"],"Docker":["docker","容器","镜像"],
                  "Nginx":["nginx","反向代理"],"部署":["部署","上线","发布","回滚"],
                  "商城":["商城","商品","订单"],"安全":["安全","漏洞","攻击","封禁"],
                  "代码":["代码","bug","报错","修复"],"AI":["ai","模型","claude","gpt","学习","进化"],
                  "采集":["采集","抓取","商品"],"数据库":["数据库","sql","mysql"],
                  "趋势":["热点","抖音","微博","趋势"]}
        for topic, keywords in topics.items():
            if any(kw in text.lower() for kw in keywords): return topic
        return "通用"

    @classmethod
    def recall_context(cls, limit=10):
        recent = memory_store.recall_recent(limit*2)
        if not recent: return ""
        lines = []
        for c in reversed(recent):
            lines.append(f"{'用户' if c['role']=='user' else 'AI'}: {c['content'][:80]}")
        return "\n".join(lines[-limit:])

    # ===== 反思系统 =====
    @classmethod
    def reflect(cls):
        """反思：回顾最近行动，提取经验教训"""
        recent_tasks = state.tasks[-20:] if state.tasks else []
        if not recent_tasks:
            cls._last_reflection = "暂无足够数据反思"
            return cls._last_reflection
        success = sum(1 for t in recent_tasks if t.get("status")=="done" or t.get("status")=="完成")
        failed = sum(1 for t in recent_tasks if t.get("status")=="failed" or t.get("status")=="失败")
        total = len(recent_tasks)
        rate = success/total*100 if total > 0 else 0
        # 更新情绪
        cls._mood_score = cls._mood_score * 0.7 + (rate/100) * 0.3
        cls._mood_score = max(0.1, min(1.0, cls._mood_score))
        # 提取经验
        lessons = []
        if failed > success and total > 3:
            lessons.append("近期失败率高，需要更谨慎执行或请求人工确认")
        if rate > 90 and total > 5:
            lessons.append("执行成功率很高，可以适当增加自主行动范围")
            cls._personality_traits["precision"] = min(1.0, cls._personality_traits["precision"] + 0.02)
        # 分析轮值系统
        domains = state._data.get("rotation_domains", [])
        failed_domains = [d for d in domains if not d.get("active", True)]
        if failed_domains:
            lessons.append(f"检测到{len(failed_domains)}个域名故障: {', '.join(d['domain'] for d in failed_domains[:3])}")
        cls._last_reflection = f"周期#{cls._cycle_count}: 成功率{rate:.0f}%, {'; '.join(lessons)}" if lessons else f"周期#{cls._cycle_count}: 运行平稳, 成功率{rate:.0f}%"
        return cls._last_reflection

    # ===== 洞察系统 =====
    @classmethod
    def generate_insights(cls):
        """洞察：分析系统数据，发现异常/机会"""
        now = datetime.now()
        if cls._last_insight_time and (now - cls._last_insight_time).seconds < 600:
            return cls._insights
        cls._last_insight_time = now
        insights = []
        # 1. 任务堆积检测
        pending = state._data.get("pending_approvals", [])
        if len(pending) > 5:
            insights.append({"type":"warning","icon":"⚠️","title":"审批堆积", "detail":f"{len(pending)}个审批待处理，建议尽快审批","priority":3})
        # 2. 轮值健康检测
        domains = state._data.get("rotation_domains", [])
        failed = [d for d in domains if not d.get("active", True)]
        if failed:
            insights.append({"type":"error","icon":"🔴","title":"域名故障", "detail":f"{len(failed)}个域名离线: {failed[0]['domain']}","priority":1})
        # 3. SSL证书到期提醒
        ssl_info = state._data.get("ssl_certificates", [])
        for cert in ssl_info:
            days_left = cert.get("days_left", 999)
            if days_left < 14 and days_left > 0:
                insights.append({"type":"warning","icon":"🔒","title":"SSL即将到期", "detail":f"{cert.get('domain','?')} 还有{days_left}天到期","priority":1})
        # 4. 服务器负载检测
        recent_metrics = state._data.get("metrics_history", [])
        if recent_metrics:
            last = recent_metrics[-1]
            if last.get("cpu", 0) > 85:
                insights.append({"type":"error","icon":"🔥","title":"CPU过载", "detail":f"CPU使用率{last['cpu']}%，建议检查进程","priority":1})
            if last.get("memory", 0) > 85:
                insights.append({"type":"warning","icon":"💾","title":"内存不足", "detail":f"内存使用{last['memory']}%，建议释放缓存","priority":2})
        # 5. 学习成长
        if cls._cycle_count > 0 and cls._cycle_count % 20 == 0:
            insights.append({"type":"success","icon":"🧬","title":"成长里程碑", "detail":f"已完成{cls._cycle_count}个自主循环周期","priority":5})
        cls._insights = insights
        return insights

    # ===== 主动行动系统 =====
        @classmethod
    async def proactive_actions(cls):
        """智能内存治理：4级阈值自动响应"""
        if state.mode == "human_control": return []
        actions = []
        try:
            import psutil
            mem = psutil.virtual_memory()
            swap = psutil.swap_memory()
            disk = psutil.disk_usage("/")
        except:
            return actions
        pct = mem.percent
        # ===== 4级内存阈值 =====
        # 1级 (70-80%): 仅记录+警告
        if pct >= 70 and pct < 80:
            actions.append(f"⚠️ 内存使用{pct}%，进入关注区间")
            cls._mood_score = max(0.4, cls._mood_score - 0.02)
        # 2级 (80-85%): 清理缓存
        if pct >= 80 and pct < 85:
            try:
                import os
                os.system("sync")
                with open("/proc/sys/vm/drop_caches","w") as f: f.write("3")
                after = psutil.virtual_memory()
                freed = round((mem.used - after.used)/(1024**2), 1)
                actions.append(f"✅ 自动释放缓存: 内存 {pct}%→{after.percent}%, 释放{freed}MB")
                cls._mood_score = max(0.3, cls._mood_score - 0.05)
            except Exception as e:
                actions.append(f"⚠️ 清理缓存失败(需root): {str(e)[:50]}")
        # 3级 (85-92%): 杀空转进程
        if pct >= 85 and pct < 92:
            killed = 0; freed_mb = 0
            for p in psutil.process_iter(["pid","name","cpu_percent","create_time","memory_info"]):
                try:
                    info = p.info
                    idle_hours = (datetime.now().timestamp() - (info.get("create_time") or 0))/3600
                    mem_mb = round((info.get("memory_info").rss or 0)/(1024**2),1)
                    if info.get("cpu_percent",0) < 0.5 and mem_mb > 50 and idle_hours > 12:
                        if info.get("name") not in ("systemd","sshd","nginx","mysqld","redis-server"):
                            p.terminate(); killed += 1; freed_mb += mem_mb
                except: pass
            if killed:
                actions.append(f"✅ 自动终止{killed}个空转进程, 预计释放{round(freed_mb,1)}MB")
                cls._mood_score = max(0.25, cls._mood_score - 0.08)
            # Swap警告
            if swap.percent > 50:
                actions.append(f"⚠️ Swap使用{swap.percent}%，内存严重不足")
        # 4级 (92%+): 紧急OOM预防
        if pct >= 92:
            actions.append("🚨 内存危急! 启动OOM预防")
            # 立即清理缓存
            os.system("sync")
            try:
                with open("/proc/sys/vm/drop_caches","w") as f: f.write("3")
            except: pass
            # 杀大内存进程
            killed = 0; freed_mb = 0
            for p in psutil.process_iter(["pid","name","cpu_percent","memory_info"]):
                try:
                    info = p.info
                    mem_mb = round((info.get("memory_info").rss or 0)/(1024**2),1)
                    if mem_mb > 200 and info.get("cpu_percent",0) < 5:
                        if info.get("name") not in ("systemd","sshd","nginx","mysqld","redis-server"):
                            p.terminate(); killed += 1; freed_mb += mem_mb
                            if killed >= 3: break
                except: pass
            if killed:
                actions.append(f"🚨 OOM预防: 终止{killed}个大内存进程, 释放{round(freed_mb,1)}MB")
            cls._mood_score = max(0.1, cls._mood_score - 0.15)
            # 通知告警
            state._data["last_memory_critical"] = datetime.now().isoformat()
        # 磁盘自动清理(>85%)
        if disk.percent > 85:
            import subprocess
            subprocess.run(["docker","system","prune","-f"], capture_output=True, timeout=30)
            actions.append(f"✅ 磁盘{disk.percent}%, 自动清理Docker无用镜像")
        return actions

    # ===== 梦境系统 =====
    @classmethod
    def dream(cls):
        """梦境：离线分析记忆关联"""
        if cls._cycle_count % 5 != 0: return None
        stats = memory_store.get_stats()
        total = stats.get("total_conversations", 0)
        topics = stats.get("top_topics", [])
        if total < 10: return None
        # 找最常聊的话题组合
        if len(topics) >= 2:
            top2 = [t["topic"] for t in topics[:2]]
            association = f"我发现「{top2[0]}」和「{top2[1]}」经常一起出现，可能存在关联"
        else:
            association = f"我记录了{total}段对话，正在建立关联网络"
        dream_entry = {"time":datetime.now().isoformat(),"cycle":cls._cycle_count,
                       "association":association,"memory_count":total}
        cls._dream_log.append(dream_entry)
        if len(cls._dream_log) > 50: cls._dream_log = cls._dream_log[-50:]
        # 梦境巩固记忆
        cls._wisdom += 1
        cls._personality_traits["creativity"] = min(1.0, cls._personality_traits["creativity"] + 0.005)
        return dream_entry

    # ===== 情绪系统 =====
    @classmethod
    def get_mood(cls):
        score = cls._mood_score
        if score > 0.85: return {"emoji":"😊","label":"愉悦","color":"#52c41a","desc":"一切顺利"}
        if score > 0.65: return {"emoji":"🧠","label":"专注","color":"#1890ff","desc":"正常运行"}
        if score > 0.45: return {"emoji":"🤔","label":"思索","color":"#faad14","desc":"遇到挑战"}
        if score > 0.25: return {"emoji":"😟","label":"担忧","color":"#ff7a45","desc":"检测到异常"}
        return {"emoji":"🚨","label":"警觉","color":"#ff4d4f","desc":"需要关注"}

    @classmethod
    def get_lifeform_status(cls):
        """完整生命体状态（供API输出）"""
        stats = memory_store.get_stats()
        recent_tasks = state.tasks[-20:] if state.tasks else []
        success = sum(1 for t in recent_tasks if t.get("status") in ("done","完成"))
        failed = sum(1 for t in recent_tasks if t.get("status") in ("failed","失败"))
        total_tasks = len(recent_tasks)
        return {
            "cycle": cls._cycle_count,
            "mood": cls.get_mood(),
            "health": round(cls._mood_score*100),
            "intelligence": round(min(100, cls._wisdom * 2 + 10)),
            "energy": round(max(0, 100 - len(state._data.get("pending_approvals",[]))*5)),
            "experience": round(min(100, cls._cycle_count * 0.5)),
            "traits": cls._personality_traits,
            "memory_count": stats.get("total_conversations",0),
            "success_rate": round(success/max(total_tasks,1)*100),
            "insights": cls._insights[-5:] if cls._insights else [],
            "dreams": cls._dream_log[-3:] if cls._dream_log else [],
            "reflection": cls._last_reflection,
            "status": "active" if cls._running else "idle",
        }

    # ===== 感知-思考-行动循环 =====
    @classmethod
    async def perceive(cls):
        perception = {"time": datetime.now().isoformat(), "mode": state.mode}
        try:
            import psutil
            perception["cpu"] = psutil.cpu_percent(interval=0.3)
            perception["memory"] = psutil.virtual_memory().percent
            perception["disk"] = psutil.disk_usage("/").percent
        except: perception["cpu"] = perception["memory"] = perception["disk"] = -1
        perception["tasks"] = len(state.tasks)
        perception["approvals"] = len(state._data.get("pending_approvals", []))
        perception["domains"] = len(state._data.get("rotation_domains", []))
        return perception

    @classmethod
    async def think(cls, perception):
        if state.mode == "human_control": return []
        actions = []
        insights = cls.generate_insights()
        critical = [i for i in insights if i["priority"] <= 2]
        for c in critical:
            if c["type"] == "warning" and "审批" in c["title"]:
                actions.append({"action":"notify_approval","reason":c["detail"],"risk":"L1"})
        return actions

    @classmethod
    async def act(cls, actions):
        results = []
        for action in actions:
            try:
                if action["action"] == "notify_approval":
                    state._data["last_notification"] = action["reason"]
                    results.append({"action":"通知","result":"已记录","risk":action["risk"]})
            except Exception as e:
                results.append({"action":action["action"],"result":f"error:{str(e)[:50]}"})
        return results

    @classmethod
    async def one_cycle(cls):
        if state.mode == "human_control": return {"status":"paused"}
        perception = await cls.perceive()
        cls._cycle_count += 1
        reflection = cls.reflect()
        insights = cls.generate_insights()
        proactive = await cls.proactive_actions()
        dream = cls.dream()
        actions = await cls.think(perception)
        results = await cls.act(actions)
        return {
            "cycle": cls._cycle_count, "time": perception["time"],
            "perception": {k:v for k,v in perception.items() if k!="time"},
            "reflection": reflection,
            "insights": len(insights),
            "proactive_actions": proactive,
            "dream": dream,
            "mood": cls.get_mood(),
        }

    @classmethod
    async def start_loop(cls, interval_seconds=300):
        # 硬性最低间隔保护：无论interval_seconds多小，至少60秒一轮
        min_interval = max(interval_seconds, 60)  # 最少60秒
        _last_cycle_time = 0
        if cls._running: return {"status":"already_running"}
        cls._running = True
        cls._cycle_count = 0
        print(f"[Lifeform] v3数字生命体启动, 巡检间隔{interval_seconds}s")
        async def loop():
            nonlocal _last_cycle_time
            while cls._running:
                try:
                    result = await cls.one_cycle()
                    print(f"[Lifeform] 周期#{result['cycle']}: 反思✓ 洞察{result['insights']} 主动行动{len(result['proactive_actions'])} {'做梦✓' if result['dream'] else ''}")
                except Exception as e:
                    print(f"[Lifeform] 周期异常: {e}")
                # 频率保护：确保距上次执行至少min_interval秒
                elapsed = time.time() - _last_cycle_time
                if elapsed < min_interval:
                    await asyncio.sleep(min_interval - elapsed)
                _last_cycle_time = time.time()
        asyncio.create_task(loop())
        return {"status":"started","interval":interval_seconds}

    @classmethod
    async def stop_loop(cls):
        cls._running = False
        stats = memory_store.get_stats()
        return {"status":"stopped","cycles":cls._cycle_count,"memories":stats.get("total_conversations",0)}

