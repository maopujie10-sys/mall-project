''" v4 -- AI: AI+++''"
import asyncio, json, random, time, httpx, os
from datetime import datetime, timedelta
from state import state
from tools.memory_store import memory_store
from tools.omni_engine import PredictEngine, SmartPricing, SelfHealing, KnowledgeGraph, BusinessEngine
from tools.logger import get_logger

logger = get_logger("lifeform")

# AI
DEEPSEEK_KEY = os.getenv("DEEPSEEK_API_KEY", '')
OPENAI_KEY = os.getenv("OPENAI_API_KEY", '')
_API_URL = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")

class DigitalLifeform:
    ''"v4: AI''"
    _running = False
    _cycle_count = 0
    _mood_score = 0.75
    _wisdom = 0
    _insights = []
    _dream_log = []
    _personality = {"curiosity":0.7,"precision":0.6,"creativity":0.5,"empathy":0.4,"efficiency":0.6}
    _action_history = []  # (action, result, success)
    _last_cycle_time = 0

    # =====  =====
    @classmethod
    async def _execute_action(cls, action_name: str, params: dict = None) -> dict:
        ''''''
        try:
            if action_name == "check_system_health":
                import psutil
                cpu = psutil.cpu_percent(interval=0.3)
                mem = psutil.virtual_memory()
                disk = psutil.disk_usage("/")
                return {"cpu": f"{cpu}%", "memory": f"{mem.percent}%", "disk": f"{disk.percent}%",
                        "ok": cpu < 90 and mem.percent < 90 and disk.percent < 90}

            if action_name == "restart_docker_container":
                name = (params or {}).get("container", '')
                if not name: return {"ok": False, "error": ''}
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
                    return {"ok": True, "action": "Tomcat"}
                return {"ok": True, "status": ''}

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
                msg = (params or {}).get("message", '')
                try:
                    from tools.alert_push import push_alert
                    await push_alert('', msg, "P2")
                    return {"ok": True, "sent": True}
                except Exception:
                    return {"ok": False, "error": ''}

            return {"ok": False, "error": f": {action_name}"}
        except Exception as e:
            return {"ok": False, "error": str(e)[:200]}

    # ===== AI =====
    @classmethod
    async def _ai_reason(cls, prompt: str) -> str:
        ''"AI''"
        if DEEPSEEK_KEY:
            try:
                async with httpx.AsyncClient(timeout=30) as c:
                    r = await c.post("https://api.deepseek.com/v1/chat/completions",
                        headers={"Authorization": f"Bearer {DEEPSEEK_KEY}"},
                        json={"model":"deepseek-chat","messages":[
                            {"role":"system","content":"Friday,AI..JSON: {\"action\":\"\",\"reason\":\"\",\"urgency\":1-5}"},
                            {"role":"user","content": prompt}
                        ],"temperature":0.3,"max_tokens":200})
                    if r.status_code == 200:
                        return r.json()["choices"][0]["message"]["content"]
            except Exception:
                pass
        return ''

    # =====  =====
    @classmethod
    async def perceive(cls) -> dict:
        ''''''
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
            return {"error": ''}

    # =====  =====
    @classmethod
    async def think(cls, perception: dict) -> list:
        ''"AI:  -> ''"
        if state.mode == "human_control":
            return []

        
        actions = []

        # 1. CPU -> 
        cpu = perception.get("cpu", 0)
        if cpu > 85:
            actions.append({"action": "check_system_health", "reason": f"CPU={cpu}%,", "urgency": 4})
            await cls.push_alert("CPU", f"CPU{cpu}%,", "warning")

        # 2.  -> 
        mem = perception.get("memory", 0)
        if mem > 85:
            actions.append({"action": "clean_docker_cache", "reason": f"={mem}%", "urgency": 5})
            await cls.push_alert('', f"{mem}%,", "warning")

        # 3.  -> 
        disk = perception.get("disk", 0)
        if disk > 90:
            actions.append({"action": "clean_docker_cache", "reason": f"={disk}%", "urgency": 5})
            await cls.push_alert('', f"{disk}%,", "critical")

        # 4. 
        if cls._cycle_count % 6 == 0:  # 6(30)
            actions.append({"action": "check_rotation_domains", "reason": '', "urgency": 2})

        # 5. Tomcat
        if cls._cycle_count % 12 == 0:  
            actions.append({"action": "check_tomcat", "reason": "Tomcat", "urgency": 2})

        # 6. 
        if perception.get("tasks_pending", 0) > 5:
            actions.append({"action": "send_alert", "params": {"message": f": {perception['tasks_pending']}"}, "reason": '', "urgency": 3})

        # 7. 
        if cls._cycle_count % 15 == 0:  # 30
            import subprocess
            try:
                r = subprocess.run(["pgrep","-f","full_scrape.py"], capture_output=True, text=True)
                if not r.stdout.strip():
                    await cls.push_alert('', ",", "warning")
            except: pass

        # 8. 
        if cls._cycle_count % 10 == 0:
            for metric in ["cpu", "memory", "disk"]:
                pred = PredictEngine.predict(metric)
                if pred.get("will_exceed"):
                    await cls.push_alert(
                        f": {metric}",
                        f"{metric}{pred['eta_minutes']} ({pred['current']}% {pred['trend']})",
                        "warning"
                    )

        # 9. AI(API Key)
        if (DEEPSEEK_KEY or OPENAI_KEY) and cls._cycle_count % 3 == 0:
            try:
                prompt = f''":
- CPU: {cpu}%
- : {mem}%
- : {disk}%
- : {perception.get('tasks_pending',0)}
- : {perception.get('mode')}
- : #{cls._cycle_count}
- : {cls._last_reflection}

.: check_system_health, clean_docker_cache, reload_nginx, check_rotation_domains, check_tomcat, send_alert, collect_metrics''"
                ai_response = await cls._ai_reason(prompt)
                if ai_response:
                    try:
                        m = __import__('re').search(r'\{[^}]+\}', ai_response)
                        if m:
                            ai_decision = json.loads(m.group())
                            if ai_decision.get("action") and not any(a["action"] == ai_decision["action"] for a in actions):
                                actions.append({"action": ai_decision["action"], "reason": ai_decision.get("reason","AI"), "urgency": ai_decision.get("urgency", 3), "source": "ai"})
                    except Exception:
                        pass
            except Exception:
                pass

        return sorted(actions, key=lambda a: a.get("urgency", 0), reverse=True)

    # =====  =====
    @classmethod
    async def act(cls, actions: list) -> list:
        ''''''
        results = []
        for action in actions:
            action_name = action["action"]
            logger.info(f": {action_name} (: {action.get('reason','')})")
            result = await cls._execute_action(action_name, action.get("params"))
            success = result.get("ok", False)
            cls._action_history.append({
                "action": action_name,
                "reason": action.get("reason", ''),
                "result": result,
                "success": success,
                "time": datetime.now().isoformat(),
                "source": action.get("source", "rule"),
            })
            if len(cls._action_history) > 100:
                cls._action_history = cls._action_history[-100:]
            results.append({"action": action_name, "success": success, "result": result})
            
            # mood linked to actual system health
            health_ok = perception.get("ok", True)
            mood_delta = 0.85 if success and health_ok else 0.5 if success else 0.25
            cls._mood_score = cls._mood_score * 0.8 + mood_delta * 0.2
            
            if success:
                cls._wisdom += 0.1
        return results

    # =====  =====
    @classmethod
    def reflect(cls):
        ''": ''"
        recent = cls._action_history[-30:]
        if not recent:
            return ''
        success_rate = sum(1 for a in recent if a["success"]) / len(recent)
        
        failures = [a for a in recent if not a["success"]]
        failure_actions = {}
        for f in failures:
            failure_actions[f["action"]] = failure_actions.get(f["action"], 0) + 1
        lessons = []
        if success_rate < 0.5:
            lessons.append(f"{success_rate:.0%},")
            cls._personality["precision"] = min(1.0, cls._personality["precision"] + 0.05)
        if success_rate > 0.9:
            lessons.append(f",{success_rate:.0%}")
            cls._personality["efficiency"] = min(1.0, cls._personality["efficiency"] + 0.02)
        if failure_actions:
            worst = max(failure_actions, key=failure_actions.get)
            lessons.append(f": {worst}({failure_actions[worst]})")
        cls._last_reflection = f"#{cls._cycle_count}: {success_rate:.0%}, " + "; ".join(lessons)
        return cls._last_reflection

    # =====  =====
    @classmethod
    def dream(cls):
        ''''''
        ideas = [
            ",...",
            ",...",
            ",...",
            ",?",
            "AI,...",
        ]
        dream = random.choice(ideas)
        cls._dream_log.append({"dream": dream, "time": datetime.now().isoformat()})
        if len(cls._dream_log) > 20:
            cls._dream_log = cls._dream_log[-20:]
        if len(cls._dream_log) > 0 and len(cls._dream_log) % 10 == 0:
            texts = [d["dream"] for d in cls._dream_log[-10:]]
            from datetime import datetime as dt
            cls._insights.append({"title":"dream","detail":" | ".join(texts[-3:]),"type":"dream","icon":"","priority":3,"time":dt.now().isoformat()})
            if len(cls._insights) > 50: cls._insights = cls._insights[-50:]
        return dream

    # ===== API  =====
    @classmethod
    def get_lifeform_status(cls) -> dict:
        return {
            "running": cls._running,
            "cycle": cls._cycle_count,
            "mood": round(cls._mood_score, 2),
            "health": round(max(0.1, 1.0 - cls._mood_score * 0.3), 2),
            "energy": round(max(0.1, cls._mood_score * 0.9), 2),
            "wisdom": round(cls._wisdom, 1),
            "experience": round(min(1.0, cls._cycle_count / 100), 2),
            "personality": cls._personality,
            "insights_count": len(cls._insights),
            "dream_count": len(cls._dream_log),
            "last_reflection": getattr(cls, "_last_reflection", ''),
        }

    @classmethod
    def get_mood(cls) -> dict:
        moods = [(0.8, ''), (0.6, ''), (0.4, ''), (0.2, '')]
        label = next((m[1] for m in moods if cls._mood_score >= m[0]), '')
        return {"score": round(cls._mood_score, 2), "label": label, "wisdom": round(cls._wisdom, 1)}

    @classmethod
    def generate_insights(cls) -> list:
        return cls._insights[-10:] if cls._insights else [{"title": '', "detail": '', "type": "system", "icon": "", "priority": 1, "time": datetime.now().isoformat()}]

    # =====  =====
    @classmethod
    def _adaptive_interval(cls, base: int, health: float) -> int:
        if health > 0.9: return min(base * 4, 600)
        if health > 0.7: return min(base * 2, 300)
        if health > 0.5: return base
        return max(30, base // 2)

    async def one_cycle(cls):
        ''"---''"
        perception = await cls.perceive()
        if "error" in perception:
            logger.info(f": {perception['error']}")
            return {"status": "perception_error"}

        cls._cycle_count += 1
        
        for k, v in perception.items():
            if k in ("cpu", "memory", "disk"):
                try:
                    PredictEngine.record(k, float(str(v).replace("%",'')))
                except: pass
        actions = await cls.think(perception)
        results = await cls.act(actions)
        reflection = cls.reflect()
        dream = cls.dream() if cls._cycle_count % 5 == 0 else None  # 5

        cycle_result = {
            "cycle": cls._cycle_count,
            "time": perception["time"],
            "state": {k: v for k, v in perception.items() if k != "time"},
            "actions_taken": len(actions),
            "results": results,
            "reflection": reflection,
            "mood": cls._mood_score,
            "health": round(max(0.1, 1.0 - cls._mood_score * 0.3), 2),
            "energy": round(max(0.1, cls._mood_score * 0.9), 2),
            "wisdom": round(cls._wisdom, 1),
            "experience": round(min(1.0, cls._cycle_count / 100), 2),
        }
        if dream:
            cycle_result["dream"] = dream

        cls._persist_state()  
        logger.info(f"#{cls._cycle_count}: {len(actions)}, {cls._mood_score:.1%}")
        return cycle_result

    @classmethod
    async def start_loop(cls, interval_seconds: int = 120):
        ''"(2)''"
        interval = max(interval_seconds, 60)
        if cls._running:
            return {"status": "already_running"}
        cls._running = True
        restored = cls._load_persisted_state()  
        if not restored:
            cls._cycle_count = 0
        logger.info(f"v4, {interval}s")

        async def loop():
            while cls._running:
                try:
                    await cls.one_cycle()
                except Exception as e:
                    logger.info(f": {e}")
                await asyncio.sleep(interval)

        asyncio.create_task(loop())
        return {"status": "started", "interval": interval}

    @classmethod
    async def daily_report(cls):
        ''''''
        try:
            import psutil
            cpu = psutil.cpu_percent(interval=1)
            mem = psutil.virtual_memory()
            disk = psutil.disk_usage("/")
            report = {
                "title": f"Friday ",
                "body": f"CPU:{cpu}% :{mem.percent}% :{disk.percent}%\n:{cls._cycle_count} :{cls._mood_score:.0%} :{cls._wisdom:.1f}",
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
    # =====  (v4.1) =====
    @classmethod
    def _persist_state(cls):
        ''"SQLite''"
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
        ''"SQLite''"
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
                logger.info(f": #{cls._cycle_count}, {cls._wisdom:.1f}, {cls._mood_score:.1%}")
            return bool(saved_wisdom)
        except Exception:
            return False


    # =====  =====
    @classmethod
    def remember_conversation(cls, user_msg, ai_reply):
        topic = cls._extract_topic(user_msg)
        importance = 0.8 if any(kw in user_msg.lower() for kw in ["bug",'','','','','','']) else 0.5
        memory_store.remember_conversation("user", user_msg, topic, importance)
        memory_store.remember_conversation("ai", ai_reply, topic, importance)

    @classmethod
    def _extract_topic(cls, text):
        topics = {'':["cpu",'',''],'':['',"docker",''],'':['',''],'':['',''],"AI":["ai",'','']}
        for topic, keywords in topics.items():
            if any(kw in text.lower() for kw in keywords):
                return topic
        return ''

    @classmethod
    def get_mood(cls):
        if cls._mood_score > 0.8: return " "
        if cls._mood_score > 0.6: return " "
        if cls._mood_score > 0.4: return " "
        return " "

    @classmethod
    def get_status(cls):
        return {
            "cycle": cls._cycle_count,
            "mood": cls.get_mood(),
            "mood_score": round(cls._mood_score, 2),
            "health": round(max(0.1, 1.0 - cls._mood_score * 0.3), 2),
            "energy": round(max(0.1, cls._mood_score * 0.9), 2),
            "wisdom": round(cls._wisdom, 1),
            "experience": round(min(1.0, cls._cycle_count / 100), 2),
            "actions_total": len(cls._action_history),
            "recent_actions": cls._action_history[-5:],
            "reflection": cls._last_reflection,
            "dreams": cls._dream_log[-3:],
            "running": cls._running,
        }
