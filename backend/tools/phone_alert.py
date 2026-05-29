"""电话告警服务 — 通过语音电话通知紧急事件/v1"""
import json, os
from datetime import datetime
from state import state
from typing import Optional

class PhoneAlert:
    """电话告警服务 — 服务器挂了/订单暴跌 → 直接打电话"""
    
    # 告警级别对应的电话号码（需在.env配置）
    ALERT_PHONES = {
        "P0": os.getenv("ALERT_PHONE_P0", ""),   # 紧急: 老板
        "P1": os.getenv("ALERT_PHONE_P1", ""),   # 重要: 技术主管
        "P2": os.getenv("ALERT_PHONE_P2", ""),   # 一般: 运维
    }

    @staticmethod
    def get_config() -> dict:
        """获取电话告警配置"""
        return {
            "enabled": bool(PhoneAlert.ALERT_PHONES["P0"] or PhoneAlert.ALERT_PHONES["P1"]),
            "phones": {
                "P0": PhoneAlert.ALERT_PHONES["P0"][:3] + "****" + PhoneAlert.ALERT_PHONES["P0"][-4:] if len(PhoneAlert.ALERT_PHONES["P0"]) > 7 else "未配置",
                "P1": PhoneAlert.ALERT_PHONES["P1"][:3] + "****" + PhoneAlert.ALERT_PHONES["P1"][-4:] if len(PhoneAlert.ALERT_PHONES["P1"]) > 7 else "未配置",
                "P2": PhoneAlert.ALERT_PHONES["P2"][:3] + "****" + PhoneAlert.ALERT_PHONES["P2"][-4:] if len(PhoneAlert.ALERT_PHONES["P2"]) > 7 else "未配置",
            },
            "cooldown_minutes": 15,  # 同一事件15分钟内不重复打电话
            "simulate": not bool(PhoneAlert.ALERT_PHONES["P0"]),  # 无真实号码时模拟
        }

    @staticmethod
    async def send_alert(level: str, title: str, message: str, phone: Optional[str] = None) -> dict:
        """发送电话告警"""
        target_phone = phone or PhoneAlert.ALERT_PHONES.get(level, "")
        event_key = f"phone_alert_{title[:30]}"
        last_sent = state._data.get(event_key)
        
        # 防重复：同一事件15分钟内不重复打
        if last_sent:
            from datetime import timedelta
            last = datetime.fromisoformat(last_sent)
            if (datetime.now() - last).seconds < 900:  # 15分钟
                return {"ok": True, "status": "skipped", "reason": "冷却期内不重复拨打"}
        
        simulate = not bool(target_phone)
        call_result = {
            "level": level, "title": title, "message": message,
            "target": target_phone or "模拟号码", "time": datetime.now().isoformat(),
            "status": "simulated" if simulate else "calling", "duration_sec": 15,
        }
        
        if simulate:
            # 模拟电话拨打
            call_result["transcript"] = f"[AI语音] 您好，这里是Friday AI OS告警系统。{title}：{message[:100]}。请尽快处理。"
            call_result["answered"] = True
        else:
            # 真实电话拨打（通过Twilio或第三方API）
            try:
                api_key = os.getenv("VOICE_API_KEY", "")
                if api_key:
                    import httpx
                    async with httpx.AsyncClient(timeout=10) as c:
                        await c.post("https://api.voiceprovider.com/call",
                            json={"phone": target_phone, "message": f"【Friday告警】{title}：{message[:200]}"},
                            headers={"Authorization": f"Bearer {api_key}"})
                    call_result["status"] = "calling"
            except Exception as e:
                call_result["status"] = "failed"
                call_result["error"] = str(e)[:100]
        
        # 记录
        state._data[event_key] = datetime.now().isoformat()
        logs = state._data.setdefault("phone_alert_logs", [])
        logs.insert(0, call_result)
        if len(logs) > 200: logs[:] = logs[:200]
        state._save()
        return {"ok": True, "status": call_result["status"], "call": call_result}

    @staticmethod
    async def check_and_alert() -> dict:
        """自动检查系统状态并触发告警"""
        alerts = []
        try:
            import psutil
            mem = psutil.virtual_memory()
            disk = psutil.disk_usage("/")
            cpu = psutil.cpu_percent(interval=0.5)
            
            # 内存>90% → P0
            if mem.percent > 90:
                r = await PhoneAlert.send_alert("P0", "内存危急", f"内存使用率{mem.percent}%，需要立即处理")
                alerts.append(r)
            # 磁盘>95% → P0
            if disk.percent > 95:
                r = await PhoneAlert.send_alert("P0", "磁盘危急", f"磁盘使用率{disk.percent}%，即将写满")
                alerts.append(r)
            # CPU>95% → P1
            if cpu > 95:
                r = await PhoneAlert.send_alert("P1", "CPU过载", f"CPU使用率{cpu}%，高负载运行")
                alerts.append(r)
            # 磁盘>90% → P2（仅记录）
            if disk.percent > 90 and mem.percent <= 90:
                await PhoneAlert.send_alert("P2", "磁盘告警", f"磁盘使用率{disk.percent}%，建议清理")
        except: pass
        return {"ok": True, "alerts": alerts, "checked_at": datetime.now().isoformat()}

    @staticmethod
    def get_history(limit: int = 20) -> list:
        """告警历史"""
        return state._data.get("phone_alert_logs", [])[:limit]
