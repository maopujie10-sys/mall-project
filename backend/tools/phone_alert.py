""" -- /v1"""
import json, os
from datetime import datetime
from state import state
from typing import Optional

class PhoneAlert:
    ''" -- / -> ''"
    
    # (.env)
    ALERT_PHONES = {
        "P0": os.getenv("ALERT_PHONE_P0", ''),   # : 
        "P1": os.getenv("ALERT_PHONE_P1", ''),   # : 
        "P2": os.getenv("ALERT_PHONE_P2", ''),   # : 
    }

    @staticmethod
    def get_config() -> dict:
        ''''''
        return {
            "enabled": bool(PhoneAlert.ALERT_PHONES["P0"] or PhoneAlert.ALERT_PHONES["P1"]),
            "phones": {
                "P0": PhoneAlert.ALERT_PHONES["P0"][:3] + "****" + PhoneAlert.ALERT_PHONES["P0"][-4:] if len(PhoneAlert.ALERT_PHONES["P0"]) > 7 else '',
                "P1": PhoneAlert.ALERT_PHONES["P1"][:3] + "****" + PhoneAlert.ALERT_PHONES["P1"][-4:] if len(PhoneAlert.ALERT_PHONES["P1"]) > 7 else '',
                "P2": PhoneAlert.ALERT_PHONES["P2"][:3] + "****" + PhoneAlert.ALERT_PHONES["P2"][-4:] if len(PhoneAlert.ALERT_PHONES["P2"]) > 7 else '',
            },
            "cooldown_minutes": 15,  # 15
            "simulate": not bool(PhoneAlert.ALERT_PHONES["P0"]),  
        }

    @staticmethod
    async def send_alert(level: str, title: str, message: str, phone: Optional[str] = None) -> dict:
        ''''''
        target_phone = phone or PhoneAlert.ALERT_PHONES.get(level, '')
        event_key = f"phone_alert_{title[:30]}"
        last_sent = state._data.get(event_key)
        
        # :15
        if last_sent:
            from datetime import timedelta
            last = datetime.fromisoformat(last_sent)
            if (datetime.now() - last).seconds < 900:  # 15
                return {"ok": True, "status": "skipped", "reason": ''}
        
        simulate = not bool(target_phone)
        call_result = {
            "level": level, "title": title, "message": message,
            "target": target_phone or '', "time": datetime.now().isoformat(),
            "status": "simulated" if simulate else "calling", "duration_sec": 15,
        }
        
        if simulate:
            
            call_result["transcript"] = f"[AI] ,Friday AI OS.{title}:{message[:100]}.."
            call_result["answered"] = True
        else:
            # (TwilioAPI)
            try:
                api_key = os.getenv("VOICE_API_KEY", '')
                if api_key:
                    import httpx
                    async with httpx.AsyncClient(timeout=10) as c:
                        await c.post("https://api.voiceprovider.com/call",
                            json={"phone": target_phone, "message": f"Friday{title}:{message[:200]}"},
                            headers={"Authorization": f"Bearer {api_key}"})
                    call_result["status"] = "calling"
            except Exception as e:
                call_result["status"] = "failed"
                call_result["error"] = str(e)[:100]
        
        
        state._data[event_key] = datetime.now().isoformat()
        logs = state._data.setdefault("phone_alert_logs", [])
        logs.insert(0, call_result)
        if len(logs) > 200: logs[:] = logs[:200]
        state._save()
        return {"ok": True, "status": call_result["status"], "call": call_result}

    @staticmethod
    async def check_and_alert() -> dict:
        ''''''
        alerts = []
        try:
            import psutil
            mem = psutil.virtual_memory()
            disk = psutil.disk_usage("/")
            cpu = psutil.cpu_percent(interval=0.5)
            
            # >90% -> P0
            if mem.percent > 90:
                r = await PhoneAlert.send_alert("P0", '', f"{mem.percent}%,")
                alerts.append(r)
            # >95% -> P0
            if disk.percent > 95:
                r = await PhoneAlert.send_alert("P0", '', f"{disk.percent}%,")
                alerts.append(r)
            # CPU>95% -> P1
            if cpu > 95:
                r = await PhoneAlert.send_alert("P1", "CPU", f"CPU{cpu}%,")
                alerts.append(r)
            # >90% -> P2()
            if disk.percent > 90 and mem.percent <= 90:
                await PhoneAlert.send_alert("P2", '', f"{disk.percent}%,")
        except: pass
        return {"ok": True, "alerts": alerts, "checked_at": datetime.now().isoformat()}

    @staticmethod
    def get_history(limit: int = 20) -> list:
        ''''''
        return state._data.get("phone_alert_logs", [])[:limit]


def _save_phone():
    from tools.memory_store import memory_store
    import json
    try:
        data = {"calls": getattr(PhoneAlert,"_call_log",[])[-100:], "alerts": getattr(PhoneAlert,"_alert_history",[])[-50:]}
        memory_store.set_knowledge("phone_data", '', json.dumps(data, ensure_ascii=False, default=str))
    except: pass
def _load_phone():
    from tools.memory_store import memory_store
    import json
    try:
        raw = memory_store.get_knowledge("phone_data")
        if raw and isinstance(raw,list) and raw:
            d = json.loads(raw[0][2] if isinstance(raw[0],tuple) else str(raw[0]))
            if hasattr(PhoneAlert,"_call_log"): PhoneAlert._call_log = d.get("calls",[])
    except: pass
try: _load_phone()
except: pass

class WeChatAlert:
    ''" -- /Telegram''"

    @staticmethod
    async def send(title: str, detail: str, level: str = "P2") -> dict:
        ''''''
        bot_token = os.getenv("TELEGRAM_BOT_TOKEN", '')
        chat_id = os.getenv("TELEGRAM_CHAT_ID", '')
        if bot_token and chat_id:
            try:
                import httpx
                msg = f"[{level}] {title}\n{detail}"
                async with httpx.AsyncClient(timeout=10) as c:
                    await c.post(f"https://api.telegram.org/bot{bot_token}/sendMessage",
                        json={"chat_id": chat_id, "text": msg[:1000]})
                return {"ok": True, "channel": "telegram"}
            except:
                return {"ok": False, "error": ''}
        return {"ok": True, "channel": "simulated", "message": f"[{level}] {title}: {detail[:100]}"}