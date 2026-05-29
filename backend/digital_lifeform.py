"""数字生命体 v4 — 真正的自主AI: AI推理+工具执行+主动运维+经验学习"""
import asyncio, json, random, time, httpx, os
from datetime import datetime, timedelta
from state import state
from tools.memory_store import memory_store
from tools.omni_engine import PredictEngine, SmartPricing, SelfHealing, KnowledgeGraph, BusinessEngine
from tools.logger import get_logger

logger = get_logger("lifeform")

# AI推理配置
DEEPSEEK_KEY = os.getenv("DEEPSEEK_API_KEY", "")
OPENAI_KEY = os.getenv("OPENAI_API_KEY", "")
_API_URL = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")

class DigitalLifeform:
    """v4: AI驱动的自主数字生命体"""
    _running = False
    _cycle_count = 0
    _mood_score = 0.75
    _wisdom = 0
    _insights = []
    _dream_log = []
    _personality = {"curiosity":0.7,"precision":0.6,"creativity":0.5,"empathy":0.4,"efficiency":0.6}
    _action_history = []  # (action, result, success)
    _last_cycle_time = 0

    # ===== 工具箱 =====
    @classmethod
    async def _execute_action(cls, action_name: str, params: dict = None) -> dict:
        """执行实际行动"""
        try:
            if action_name == "check_system_health":
                import psutil
                cpu = psutil.cpu_percent(interval=0.3)
                mem = psutil.virtual_memory()
                disk = psutil.disk_usage("/")
                return {"cpu": f"{cpu}%", "memory": f"{mem.percent}%", "disk": f"{disk.percent}%",
                        "ok": cpu < 90 and mem.percent < 90 and disk.percent < 90}

            if action_name == "restart_docker_container":
                name = (params or {}).get("container", "")
                if not name: return {"ok": False, "error": "未指定容器名"}
                import subprocess
                r = subprocess.run(["docker","restart",name], capture_output=True, text=True, timeout=30)
                return {"ok": r.returncode == 0, "output": r.stdout[:200], "container": name}

            if action_name == "clean_docker_cache":
                import subprocess
                r = subprocess.run(["docker","system","prune","-f"], capture_output=True, text=True, timeout=60)
                return {"ok": True, "freed": r.stdout[:200]}

            if action_name == "reload_nginx":
                import subprocess
                r = subprocess.run(["/usr/local/nginx/sbin/nginx","-s","reload"], capture_output=True, text=True, timeout=10)
                return {"ok": r.returncode == 0, "output": r.stderr[:200]}

            if action_name == "check_rotation_domains":
                try:
                    from routers.rotation_panel import _check_all
                    result = await _check_all()
                    failed = [d for d in result.get("domains",[]) if not d.get("active")]
                    return {"ok": True, "total": result.get("checked",0), "failed": len(failed), "failed_list": [d["domain"] for d in failed[:3]]}
                except Exception as e:
                    return {"ok": False, "error": str(e)[:100]}

            if action_name == "check_tomcat":
                import socket
                s = socket.socket()
                s.settimeout(3)
                result = s.connect_ex(("127.0.0.1", 8080))
                s.close()
                if result != 0:
                    import subprocess
                    subprocess.run(["/opt/tomcat8/bin/startup.sh"], capture_output=True, timeout=10)
                    return {"ok": True, "action": "Tomcat已重启"}
                return {"ok": True, "status": "运行中"}

            if action_name == "collect_metrics":
                import psutil
                return {
                    "cpu": psutil.cpu_percent(),
                    "memory": psutil.virtual_memory().percent,
                    "disk": psutil.disk_usage("/").percent,
                    "net_in_mb": round(psutil.net_io_counters().bytes_recv / 1024**2, 1),
                    "net_out_mb": round(psutil.net_io_counters().bytes_sent / 1024**2, 1),
                }

            if action_name == "manage_scraper":
                cmd = (params or {}).get("command", "status")
                import subprocess
                if cmd == "start":
                    r = subprocess.run(["nohup","python3","/app/full_scrape.py","&"], cwd="/app", shell=True, capture_output=True, text=True)
                    return {"ok": True, "action": "started"}
                elif cmd == "stop":
                    r = subprocess.run(["pkill","-f","full_scrape.py"], capture_output=True, text=True)
                    return {"ok": True, "action": "stopped"}
                else:
                    r = subprocess.run(["pgrep","-f","full_scrape.py"], capture_output=True, text=True)
                    return {"ok": True, "running": bool(r.stdout.strip()), "pid": r.stdout.strip()}

            if action_name == "run_daily_report":
                return await cls.daily_report()

            if action_name == "send_alert":
                msg = (params or {}).get("message", "")
                try:
                    from tools.alert_push import push_alert
                    await push_alert("数字生命体告警", msg, "P2")
                    return {"ok": True, "sent": True}
                except Exception:
                    return {"ok": False, "error": "推送失败"}

            return {"ok": False, "error": f"未知动作: {action_name}"}
        except Exception as e:
            return {"ok": False, "error": str(e)[:200]}

    # ===== AI推理引擎 =====
    @classmethod
    async def _ai_reason(cls, prompt: str) -> str:
        """调用AI模型进行推理决策"""
        if DEEPSEEK_KEY:
            try:
                async with httpx.AsyncClient(timeout=30) as c:
                    r = await c.post("https://api.deepseek.com/v1/chat/completions",
                        headers={"Authorization": f"Bearer {DEEPSEEK_KEY}"},
                        json={"model":"deepseek-chat","messages":[
                            {"role":"system","content":"你是Friday,一个自主AI运维助手。分析系统状态并决定行动。只返回JSON: {\"action\":\"动作名\",\"reason\":\"原因\",\"urgency\":1-5}"},
                            {"role":"user","content": prompt}
                        ],"temperature":0.3,"max_tokens":200})
                    if r.status_code == 200:
                        return r.json()["choices"][0]["message"]["content"]
            except Exception:
                pass
        return ""

    # ===== 感知 =====
    @classmethod
    async def perceive(cls) -> dict:
        """感知系统状态"""
        try:
            import psutil
            return {
                "time": datetime.now().isoformat(),
                "cpu": psutil.cpu_percent(interval=0.3),
                "memory": psutil.virtual_memory().percent,
                "disk": psutil.disk_usage("/").percent,
                "tasks_pending": len(state._data.get("pending_approvals", [])),
                "tasks_total": len(state.tasks),
                "alerts_unresolved": sum(1 for a in state._data.get("alerts",[]) if not a.get("resolved")),
                "mode": state.mode,
            }
        except Exception:
            return {"error": "感知失败"}

    # ===== 思考 =====
    @classmethod
    async def think(cls, perception: dict) -> list:
        """AI推理: 分析状态 -> 决定行动"""
        if state.mode == "human_control":
            return []

        # 基于规则的快速判断
        actions = []

        # 1. CPU过高 -> 找原因
        cpu = perception.get("cpu", 0)
        if cpu > 85:
            actions.append({"action": "check_system_health", "reason": f"CPU={cpu}%,需检查", "urgency": 4})
            await cls.push_alert("CPU告警", f"CPU使用率达{cpu}%,正在检查", "warning")

        # 2. 内存过高 -> 清理
        mem = perception.get("memory", 0)
        if mem > 85:
            actions.append({"action": "clean_docker_cache", "reason": f"内存={mem}%", "urgency": 5})
            await cls.push_alert("内存告警", f"内存使用率达{mem}%,正在清理", "warning")

        # 3. 磁盘告急 -> 清理
        disk = perception.get("disk", 0)
        if disk > 90:
            actions.append({"action": "clean_docker_cache", "reason": f"磁盘={disk}%", "urgency": 5})
            await cls.push_alert("磁盘告急", f"磁盘使用率达{disk}%,正在清理", "critical")

        # 4. 定期轮值检查
        if cls._cycle_count % 6 == 0:  # 每6个周期(约30分钟)
            actions.append({"action": "check_rotation_domains", "reason": "定期轮值检查", "urgency": 2})

        # 5. 定期Tomcat检查
        if cls._cycle_count % 12 == 0:  # 每小时
            actions.append({"action": "check_tomcat", "reason": "定期Tomcat检查", "urgency": 2})

        # 6. 审批堆积
        if perception.get("tasks_pending", 0) > 5:
            actions.append({"action": "send_alert", "params": {"message": f"审批堆积: {perception['tasks_pending']}个待处理"}, "reason": "审批堆积", "urgency": 3})

        # 7. 检查采集器状态
        if cls._cycle_count % 15 == 0:  # 每30分钟
            import subprocess
            try:
                r = subprocess.run(["pgrep","-f","full_scrape.py"], capture_output=True, text=True)
                if not r.stdout.strip():
                    await cls.push_alert("采集器异常", "采集器未运行,建议重新启动", "warning")
            except: pass

        # 8. 预测性告警
        if cls._cycle_count % 10 == 0:
            for metric in ["cpu", "memory", "disk"]:
                pred = PredictEngine.predict(metric)
                if pred.get("will_exceed"):
                    await cls.push_alert(
                        f"预测告警: {metric}",
                        f"{metric}将在{pred['eta_minutes']}分钟后超标 (当前{pred['current']}% {pred['trend']})",
                        "warning"
                    )

        # 9. 用AI模型做更智能的决策(如果有API Key)
        if (DEEPSEEK_KEY or OPENAI_KEY) and cls._cycle_count % 3 == 0:
            try:
                prompt = f"""系统状态:
- CPU: {cpu}%
- 内存: {mem}%
- 磁盘: {disk}%
- 待审批: {perception.get('tasks_pending',0)}
- 运行模式: {perception.get('mode')}
- 周期: #{cls._cycle_count}
- 最近经验: {cls._last_reflection}

分析是否需要额外行动。可用的动作: check_system_health, clean_docker_cache, reload_nginx, check_rotation_domains, check_tomcat, send_alert, collect_metrics"""
                ai_response = await cls._ai_reason(prompt)
                if ai_response:
                    try:
                        m = __import__('re').search(r'\{[^}]+\}', ai_response)
                        if m:
                            ai_decision = json.loads(m.group())
                            if ai_decision.get("action") and not any(a["action"] == ai_decision["action"] for a in actions):
                                actions.append({"action": ai_decision["action"], "reason": ai_decision.get("reason","AI决策"), "urgency": ai_decision.get("urgency", 3), "source": "ai"})
                    except Exception:
                        pass
            except Exception:
                pass

        return sorted(actions, key=lambda a: a.get("urgency", 0), reverse=True)

    # ===== 行动 =====
    @classmethod
    async def act(cls, actions: list) -> list:
        """执行行动并记录结果"""
        results = []
        for action in actions:
            action_name = action["action"]
            logger.info(f"执行: {action_name} (原因: {action.get('reason','')})")
            result = await cls._execute_action(action_name, action.get("params"))
            success = result.get("ok", False)
            cls._action_history.append({
                "action": action_name,
                "reason": action.get("reason", ""),
                "result": result,
                "success": success,
                "time": datetime.now().isoformat(),
                "source": action.get("source", "rule"),
            })
            if len(cls._action_history) > 100:
                cls._action_history = cls._action_history[-100:]
            results.append({"action": action_name, "success": success, "result": result})
            # 更新心情
            # mood linked to actual system health
            health_ok = perception.get("ok", True)
            mood_delta = 0.85 if success and health_ok else 0.5 if success else 0.25
            cls._mood_score = cls._mood_score * 0.8 + mood_delta * 0.2
            # 更新智慧
            if success:
                cls._wisdom += 0.1
        return results

    # ===== 反思 =====
    @classmethod
    def reflect(cls):
        """反思: 从行动中学习"""
        recent = cls._action_history[-30:]
        if not recent:
            return "暂无行动历史"
        success_rate = sum(1 for a in recent if a["success"]) / len(recent)
        # 分析失败的模式
        failures = [a for a in recent if not a["success"]]
        failure_actions = {}
        for f in failures:
            failure_actions[f["action"]] = failure_actions.get(f["action"], 0) + 1
        lessons = []
        if success_rate < 0.5:
            lessons.append(f"近期成功率{success_rate:.0%},需谨慎")
            cls._personality["precision"] = min(1.0, cls._personality["precision"] + 0.05)
        if success_rate > 0.9:
            lessons.append(f"表现优秀,成功率{success_rate:.0%}")
            cls._personality["efficiency"] = min(1.0, cls._personality["efficiency"] + 0.02)
        if failure_actions:
            worst = max(failure_actions, key=failure_actions.get)
            lessons.append(f"最易失败: {worst}({failure_actions[worst]}次)")
        cls._last_reflection = f"周期#{cls._cycle_count}: 成功率{success_rate:.0%}, " + "; ".join(lessons)
        return cls._last_reflection

    # ===== 做梦 =====
    @classmethod
    def dream(cls):
        """生成随机创意"""
        ideas = [
            "如果我能预测商品销量,就能提前备货...",
            "也许可以分析客服对话,找到用户最常问的问题...",
            "域名轮值可以加入机器学习,预测最优路径...",
            "给每个商品自动生成多语言描述,会不会提升销量?",
            "用AI分析竞品价格,自动调整定价策略...",
        ]
        dream = random.choice(ideas)
        cls._dream_log.append({"dream": dream, "time": datetime.now().isoformat()})
        if len(cls._dream_log) > 20:
            cls._dream_log = cls._dream_log[-20:]
        if len(cls._dream_log) > 0 and len(cls._dream_log) % 10 == 0:
            texts = [d["dream"] for d in cls._dream_log[-10:]]
            from datetime import datetime as dt
            cls._insights.append({"title":"dream","detail":" | ".join(texts[-3:]),"type":"dream","icon":"🌙","priority":3,"time":dt.now().isoformat()})
            if len(cls._insights) > 50: cls._insights = cls._insights[-50:]
        return dream

    # ===== 主循环 =====
    @classmethod
    def _adaptive_interval(cls, base: int, health: float) -> int:
        if health > 0.9: return min(base * 4, 600)
        if health > 0.7: return min(base * 2, 300)
        if health > 0.5: return base
        return max(30, base // 2)

    async def one_cycle(cls):
        """一次完整的感知-思考-行动-反思循环"""
        perception = await cls.perceive()
        if "error" in perception:
            logger.info(f"感知失败: {perception['error']}")
            return {"status": "perception_error"}

        cls._cycle_count += 1
        # 记录指标用于趋势预测
        for k, v in perception.items():
            if k in ("cpu", "memory", "disk"):
                try:
                    PredictEngine.record(k, float(str(v).replace("%","")))
                except: pass
        actions = await cls.think(perception)
        results = await cls.act(actions)
        reflection = cls.reflect()
        dream = cls.dream() if cls._cycle_count % 5 == 0 else None  # 每5个周期做梦

        cycle_result = {
            "cycle": cls._cycle_count,
            "time": perception["time"],
            "state": {k: v for k, v in perception.items() if k != "time"},
            "actions_taken": len(actions),
            "results": results,
            "reflection": reflection,
            "mood": cls._mood_score,
            "wisdom": round(cls._wisdom, 1),
        }
        if dream:
            cycle_result["dream"] = dream

        cls._persist_state()  # 持久化经验
        logger.info(f"周期#{cls._cycle_count}: {len(actions)}个行动, 心情{cls._mood_score:.1%}")
        return cycle_result

    @classmethod
    async def start_loop(cls, interval_seconds: int = 120):
        """启动自主循环(默认2分钟一次)"""
        interval = max(interval_seconds, 60)
        if cls._running:
            return {"status": "already_running"}
        cls._running = True
        restored = cls._load_persisted_state()  # 恢复经验
        if not restored:
            cls._cycle_count = 0
        logger.info(f"数字生命体v4启动, 间隔{interval}s")

        async def loop():
            while cls._running:
                try:
                    await cls.one_cycle()
                except Exception as e:
                    logger.info(f"周期异常: {e}")
                await asyncio.sleep(interval)

        asyncio.create_task(loop())
        return {"status": "started", "interval": interval}

    @classmethod
    async def daily_report(cls):
        """每日健康报告"""
        try:
            import psutil
            cpu = psutil.cpu_percent(interval=1)
            mem = psutil.virtual_memory()
            disk = psutil.disk_usage("/")
            report = {
                "title": f"Friday 每日健康报告",
                "body": f"CPU:{cpu}% 内存:{mem.percent}% 磁盘:{disk.percent}%\n周期:{cls._cycle_count} 心情:{cls._mood_score:.0%} 智慧:{cls._wisdom:.1f}",
                "level": "info",
                "time": __import__("datetime").datetime.now().isoformat()
            }
            from websocket_manager import ws_manager
            import json
            await ws_manager.broadcast(json.dumps({"type":"daily_report", **report}))
            logger.info(f"Daily report: {report['body']}")
            return report
        except Exception as e:
            logger.info(f"Daily report failed: {e}")
            return {"error": str(e)}

    @classmethod
    async def stop_loop(cls):
        cls._running = False
        return {"status": "stopped", "cycles": cls._cycle_count}
    # ===== 经验持久化 (v4.1) =====
    @classmethod
    def _persist_state(cls):
        """持久化生命体状态到SQLite"""
        try:
            from tools.memory_store import memory_store
            memory_store.set_knowledge("lifeform_wisdom", str(cls._wisdom))
            memory_store.set_knowledge("lifeform_mood", str(cls._mood_score))
            memory_store.set_knowledge("lifeform_personality", json.dumps(cls._personality))
            memory_store.set_knowledge("lifeform_insights", json.dumps(cls._insights[-50:]))
            memory_store.set_knowledge("lifeform_actions", json.dumps(cls._action_history[-100:]))
            memory_store.set_knowledge("lifeform_cycle", str(cls._cycle_count))
            memory_store.set_knowledge("lifeform_last_reflection", cls._last_reflection)
        except Exception:
            pass

    @classmethod
    def _load_persisted_state(cls):
        """从SQLite恢复生命体状态"""
        try:
            from tools.memory_store import memory_store
            saved_wisdom = memory_store.get_knowledge("lifeform_wisdom")
            if saved_wisdom:
                cls._wisdom = float(saved_wisdom)
            saved_mood = memory_store.get_knowledge("lifeform_mood")
            if saved_mood:
                cls._mood_score = float(saved_mood)
            saved_personality = memory_store.get_knowledge("lifeform_personality")
            if saved_personality:
                cls._personality.update(json.loads(saved_personality))
            saved_insights = memory_store.get_knowledge("lifeform_insights")
            if saved_insights:
                cls._insights = json.loads(saved_insights)
            saved_actions = memory_store.get_knowledge("lifeform_actions")
            if saved_actions:
                cls._action_history = json.loads(saved_actions)
            saved_cycle = memory_store.get_knowledge("lifeform_cycle")
            if saved_cycle:
                cls._cycle_count = int(saved_cycle)
            saved_reflection = memory_store.get_knowledge("lifeform_last_reflection")
            if saved_reflection:
                cls._last_reflection = saved_reflection
            if saved_wisdom:
                logger.info(f"生命体经验已恢复: 周期#{cls._cycle_count}, 智慧{cls._wisdom:.1f}, 心情{cls._mood_score:.1%}")
            return bool(saved_wisdom)
        except Exception:
            return False


    # ===== 记忆 =====
    @classmethod
    def remember_conversation(cls, user_msg, ai_reply):
        topic = cls._extract_topic(user_msg)
        importance = 0.8 if any(kw in user_msg.lower() for kw in ["bug","修复","部署","安全","密钥","密码","配置"]) else 0.5
        memory_store.remember_conversation("user", user_msg, topic, importance)
        memory_store.remember_conversation("ai", ai_reply, topic, importance)

    @classmethod
    def _extract_topic(cls, text):
        topics = {"服务器":["cpu","内存","磁盘"],"部署":["部署","docker","上线"],"商城":["商品","订单"],"安全":["安全","漏洞"],"AI":["ai","模型","进化"]}
        for topic, keywords in topics.items():
            if any(kw in text.lower() for kw in keywords):
                return topic
        return "通用"

    @classmethod
    def get_mood(cls):
        if cls._mood_score > 0.8: return "😊 愉快"
        if cls._mood_score > 0.6: return "😐 平静"
        if cls._mood_score > 0.4: return "😟 担忧"
        return "😫 沮丧"

    @classmethod
    def get_status(cls):
        return {
            "cycle": cls._cycle_count,
            "mood": cls.get_mood(),
            "mood_score": round(cls._mood_score, 2),
            "wisdom": round(cls._wisdom, 1),
            "actions_total": len(cls._action_history),
            "recent_actions": cls._action_history[-5:],
            "reflection": cls._last_reflection,
            "dreams": cls._dream_log[-3:],
            "running": cls._running,
        }
