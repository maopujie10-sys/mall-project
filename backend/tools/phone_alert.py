锘?""鐢佃瘽鍛婅鏈嶅姟 鈥?閫氳繃璇煶鐢佃瘽閫氱煡绱ф€ヤ簨浠?v1"""
import json, os
from datetime import datetime
from state import state
from typing import Optional

class PhoneAlert:
    """鐢佃瘽鍛婅鏈嶅姟 鈥?鏈嶅姟鍣ㄦ寕浜?璁㈠崟鏆磋穼 鈫?鐩存帴鎵撶數璇?""
    
    # 鍛婅绾у埆瀵瑰簲鐨勭數璇濆彿鐮侊紙闇€鍦?env閰嶇疆锛?
    ALERT_PHONES = {
        "P0": os.getenv("ALERT_PHONE_P0", ""),   # 绱ф€? 鑰佹澘
        "P1": os.getenv("ALERT_PHONE_P1", ""),   # 閲嶈: 鎶€鏈富绠?
        "P2": os.getenv("ALERT_PHONE_P2", ""),   # 涓€鑸? 杩愮淮
    }

    @staticmethod
    def get_config() -> dict:
        """鑾峰彇鐢佃瘽鍛婅閰嶇疆"""
        return {
            "enabled": bool(PhoneAlert.ALERT_PHONES["P0"] or PhoneAlert.ALERT_PHONES["P1"]),
            "phones": {
                "P0": PhoneAlert.ALERT_PHONES["P0"][:3] + "****" + PhoneAlert.ALERT_PHONES["P0"][-4:] if len(PhoneAlert.ALERT_PHONES["P0"]) > 7 else "鏈厤缃?,
                "P1": PhoneAlert.ALERT_PHONES["P1"][:3] + "****" + PhoneAlert.ALERT_PHONES["P1"][-4:] if len(PhoneAlert.ALERT_PHONES["P1"]) > 7 else "鏈厤缃?,
                "P2": PhoneAlert.ALERT_PHONES["P2"][:3] + "****" + PhoneAlert.ALERT_PHONES["P2"][-4:] if len(PhoneAlert.ALERT_PHONES["P2"]) > 7 else "鏈厤缃?,
            },
            "cooldown_minutes": 15,  # 鍚屼竴浜嬩欢15鍒嗛挓鍐呬笉閲嶅鎵撶數璇?
            "simulate": not bool(PhoneAlert.ALERT_PHONES["P0"]),  # 鏃犵湡瀹炲彿鐮佹椂妯℃嫙
        }

    @staticmethod
    async def send_alert(level: str, title: str, message: str, phone: Optional[str] = None) -> dict:
        """鍙戦€佺數璇濆憡璀?""
        target_phone = phone or PhoneAlert.ALERT_PHONES.get(level, "")
        event_key = f"phone_alert_{title[:30]}"
        last_sent = state._data.get(event_key)
        
        # 闃查噸澶嶏細鍚屼竴浜嬩欢15鍒嗛挓鍐呬笉閲嶅鎵?
        if last_sent:
            from datetime import timedelta
            last = datetime.fromisoformat(last_sent)
            if (datetime.now() - last).seconds < 900:  # 15鍒嗛挓
                return {"ok": True, "status": "skipped", "reason": "鍐峰嵈鏈熷唴涓嶉噸澶嶆嫧鎵?}
        
        simulate = not bool(target_phone)
        call_result = {
            "level": level, "title": title, "message": message,
            "target": target_phone or "妯℃嫙鍙风爜", "time": datetime.now().isoformat(),
            "status": "simulated" if simulate else "calling", "duration_sec": 15,
        }
        
        if simulate:
            # 妯℃嫙鐢佃瘽鎷ㄦ墦
            call_result["transcript"] = f"[AI璇煶] 鎮ㄥソ锛岃繖閲屾槸Friday AI OS鍛婅绯荤粺銆倇title}锛歿message[:100]}銆傝灏藉揩澶勭悊銆?
            call_result["answered"] = True
        else:
            # 鐪熷疄鐢佃瘽鎷ㄦ墦锛堥€氳繃Twilio鎴栫涓夋柟API锛?
            try:
                api_key = os.getenv("VOICE_API_KEY", "")
                if api_key:
                    import httpx
                    async with httpx.AsyncClient(timeout=10) as c:
                        await c.post("https://api.voiceprovider.com/call",
                            json={"phone": target_phone, "message": f"銆怓riday鍛婅銆憑title}锛歿message[:200]}"},
                            headers={"Authorization": f"Bearer {api_key}"})
                    call_result["status"] = "calling"
            except Exception as e:
                call_result["status"] = "failed"
                call_result["error"] = str(e)[:100]
        
        # 璁板綍
        state._data[event_key] = datetime.now().isoformat()
        logs = state._data.setdefault("phone_alert_logs", [])
        logs.insert(0, call_result)
        if len(logs) > 200: logs[:] = logs[:200]
        state._save()
        return {"ok": True, "status": call_result["status"], "call": call_result}

    @staticmethod
    async def check_and_alert() -> dict:
        """鑷姩妫€鏌ョ郴缁熺姸鎬佸苟瑙﹀彂鍛婅"""
        alerts = []
        try:
            import psutil
            mem = psutil.virtual_memory()
            disk = psutil.disk_usage("/")
            cpu = psutil.cpu_percent(interval=0.5)
            
            # 鍐呭瓨>90% 鈫?P0
            if mem.percent > 90:
                r = await PhoneAlert.send_alert("P0", "鍐呭瓨鍗辨€?, f"鍐呭瓨浣跨敤鐜噞mem.percent}%锛岄渶瑕佺珛鍗冲鐞?)
                alerts.append(r)
            # 纾佺洏>95% 鈫?P0
            if disk.percent > 95:
                r = await PhoneAlert.send_alert("P0", "纾佺洏鍗辨€?, f"纾佺洏浣跨敤鐜噞disk.percent}%锛屽嵆灏嗗啓婊?)
                alerts.append(r)
            # CPU>95% 鈫?P1
            if cpu > 95:
                r = await PhoneAlert.send_alert("P1", "CPU杩囪浇", f"CPU浣跨敤鐜噞cpu}%锛岄珮璐熻浇杩愯")
                alerts.append(r)
            # 纾佺洏>90% 鈫?P2锛堜粎璁板綍锛?
            if disk.percent > 90 and mem.percent <= 90:
                await PhoneAlert.send_alert("P2", "纾佺洏鍛婅", f"纾佺洏浣跨敤鐜噞disk.percent}%锛屽缓璁竻鐞?)
        except: pass
        return {"ok": True, "alerts": alerts, "checked_at": datetime.now().isoformat()}

    @staticmethod
    def get_history(limit: int = 20) -> list:
        """鍛婅鍘嗗彶"""
        return state._data.get("phone_alert_logs", [])[:limit]
