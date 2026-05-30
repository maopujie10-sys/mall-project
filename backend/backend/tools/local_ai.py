''"AI -- API Key,++
LLM,API KeyAI''"
import re, random, time, os
from tools.logger import get_logger

logger = get_logger("local_ai")

class LocalAI:
    ''" -- API''"

    # =====  =====
    INTENTS = {
        "greeting": ['',"hi","hello",'','','','',''],
        "status": ['','','','','','',"ok","cpu",'','',''],
        "order": ['','','','','','','',''],
        "fix": ['','','','','','','',''],
        "restart": ['','',"reload","restart"],
        "deploy": ['','','','','',"deploy"],
        "help": ['',"help",'','','',''],
        "thanks": ['','','',"thx","thank"],
        "bye": ['','',"bye",'',''],
    }

    # =====  =====
    REPLIES = {
        "greeting": [
            "! Friday AI,?",
            "!Friday , ",
            "!?",
        ],
        "status_ok": [
            "  CPU {}%  {}%  {}%",
            "!, ",
        ],
        "status_warn": [
            "  CPU {}% ",
            ",?",
        ],
        "help": [
            ":\n \n /\n \n \n \n\n!",
        ],
        "thanks": ["! ", "!?"],
        "bye": ["! ", ",!"],
        "fallback": [
            ",.?",
            ",?",
        ],
    }

    @classmethod
    def detect_intent(cls, text: str) -> tuple:
        ''" -> (, )''"
        text_lower = text.lower().strip()
        best_intent, best_score = "unknown", 0

        for intent, keywords in cls.INTENTS.items():
            score = sum(1 for kw in keywords if kw in text_lower)
            if score > best_score:
                best_intent, best_score = intent, score

        confidence = min(1.0, best_score / 3)
        return best_intent, confidence

    @classmethod
    def reason(cls, text: str) -> str:
        ''" -- API''"
        intent, conf = cls.detect_intent(text)

        #  -> 
        if conf >= 0.3:
            if intent == "greeting":
                return random.choice(cls.REPLIES["greeting"])
            elif intent == "thanks":
                return random.choice(cls.REPLIES["thanks"])
            elif intent == "bye":
                return random.choice(cls.REPLIES["bye"])
            elif intent == "help":
                return random.choice(cls.REPLIES["help"])
            elif intent == "status":
                return cls._get_system_status()
            elif intent == "order":
                return cls._get_order_summary()
            elif intent == "restart":
                return ".,."

        #  -> 
        keywords = re.findall(r'[\u4e00-\u9fff]{2,}|[a-zA-Z]{3,}', text)
        if keywords:
            return f"!{'/'.join(keywords[:3])},.?"

        #  -> 
        return random.choice(cls.REPLIES["fallback"])

    @classmethod
    def _get_system_status(cls) -> str:
        ''''''
        try:
            import psutil
            cpu = psutil.cpu_percent(interval=0.5)
            mem = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            if cpu > 80 or mem.percent > 90:
                return random.choice(cls.REPLIES["status_warn"]).format(int(cpu), int(mem.percent))
            return random.choice(cls.REPLIES["status_ok"]).format(int(cpu), int(mem.percent))
        except:
            return ". psutil :pip install psutil"

    @classmethod
    def _get_order_summary(cls) -> str:
        ''''''
        try:
            from state import state
            orders = state._data.get("orders", [])
            if orders:
                today = [o for o in orders if isinstance(o, dict)]
                return f" {len(orders)} .."
            return ".."
        except:
            return ".."

    @classmethod
    def smart_reply(cls, text: str, use_llm: bool = True) -> dict:
        ''" --  + LLM
         {"content": str, "source": "local"|"llm", "intent": str}
        ''"
        intent, conf = cls.detect_intent(text)

        
        if conf >= 0.5 or intent in ("greeting","thanks","bye","help"):
            return {"content": cls.reason(text), "source": "local", "intent": intent}

        # LLM
        if use_llm:
            try:
                from agents.multi_model import ModelRouter
                resp = ModelRouter.smart_chat(
                    messages=[{"role": "user", "content": text}],
                    mode="fast"
                )
                content = resp.get("content", '')
                if content and "[AI]" not in content and '' not in content:
                    return {"content": content, "source": "llm", "intent": intent}
            except:
                pass

        # LLM -> 
        return {"content": cls.reason(text), "source": "local", "intent": intent}

local_ai = LocalAI()
