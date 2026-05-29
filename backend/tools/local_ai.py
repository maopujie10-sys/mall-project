"""本地AI引擎 -- 零API Key依赖,关键词+模板+规则推理
所有LLM依赖模块的兜底方案,确保无API Key时AI依然可用"""
import re, random, time, os
from tools.logger import get_logger

logger = get_logger("local_ai")

class LocalAI:
    """本地推理引擎 -- 不依赖任何外部API"""

    # ===== 意图识别 =====
    INTENTS = {
        "greeting": ["你好","hi","hello","嗨","在吗","早上好","晚上好","下午好"],
        "status": ["状态","怎么样","如何","运行","健康","正常","ok","cpu","内存","磁盘","负载"],
        "order": ["订单","销量","卖了","卖出","成交","交易","收入","营收"],
        "fix": ["修复","修","改","解决","处理","帮忙","修一下","改一下"],
        "restart": ["重启","重载","reload","restart"],
        "deploy": ["部署","上线","发布","更新","升级","deploy"],
        "help": ["帮助","help","能做什么","功能","怎么用","使用"],
        "thanks": ["谢谢","感谢","多谢","thx","thank"],
        "bye": ["再见","拜拜","bye","晚安","下了"],
    }

    # ===== 模板回复库 =====
    REPLIES = {
        "greeting": [
            "你好!我是 Friday AI,有什么可以帮你?",
            "嗨!Friday 在线,随时为你服务 👋",
            "你好呀!今天需要我做什么?",
        ],
        "status_ok": [
            "系统运行正常 ✅ CPU {}% 内存 {}% 磁盘 {}%",
            "一切正常!当前负载平稳,各项指标健康 🟢",
        ],
        "status_warn": [
            "系统负载偏高 ⚠️ CPU {}% 建议检查一下",
            "注意到资源使用较高,需要我帮你排查吗?",
        ],
        "help": [
            "我能帮你:\n📊 查看系统状态\n📦 管理订单/商品\n🔧 运维操作\n📈 数据分析\n💬 智能问答\n\n直接告诉我要做什么就行!",
        ],
        "thanks": ["不客气!随时为你服务 😊", "应该的!还有什么需要吗?"],
        "bye": ["再见!随时找我 👋", "拜拜,有需要随时回来!"],
        "fallback": [
            "我理解你的需求,但需要更具体的信息.能详细说说吗?",
            "这个问题我需要多了解一些背景,可以补充细节吗?",
        ],
    }

    @classmethod
    def detect_intent(cls, text: str) -> tuple:
        """检测意图 -> (意图名, 置信度)"""
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
        """本地推理 -- 不调用任何API"""
        intent, conf = cls.detect_intent(text)

        # 高置信度意图 -> 模板回复
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
                return "重启操作需要人工确认.请在运维面板操作,或告诉我具体要重启哪个服务."

        # 中置信度 -> 提取关键词尝试匹配
        keywords = re.findall(r'[\u4e00-\u9fff]{2,}|[a-zA-Z]{3,}', text)
        if keywords:
            return f"收到!关于「{'/'.join(keywords[:3])}」的问题,我正在处理.需要我深入分析吗?"

        # 低置信度 -> 友好降级
        return random.choice(cls.REPLIES["fallback"])

    @classmethod
    def _get_system_status(cls) -> str:
        """获取系统状态"""
        try:
            import psutil
            cpu = psutil.cpu_percent(interval=0.5)
            mem = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            if cpu > 80 or mem.percent > 90:
                return random.choice(cls.REPLIES["status_warn"]).format(int(cpu), int(mem.percent))
            return random.choice(cls.REPLIES["status_ok"]).format(int(cpu), int(mem.percent))
        except:
            return "系统运行中.安装 psutil 可获取详细指标:pip install psutil"

    @classmethod
    def _get_order_summary(cls) -> str:
        """获取订单摘要"""
        try:
            from state import state
            orders = state._data.get("orders", [])
            if orders:
                today = [o for o in orders if isinstance(o, dict)]
                return f"系统共记录 {len(orders)} 条订单记录.需要详细分析请告诉我具体条件."
            return "目前订单数据为空.采集中心可以帮你导入数据."
        except:
            return "订单数据暂不可用.采集中心可以帮你获取."

    @classmethod
    def smart_reply(cls, text: str, use_llm: bool = True) -> dict:
        """智能回复 -- 本地优先 + LLM增强
        返回 {"content": str, "source": "local"|"llm", "intent": str}
        """
        intent, conf = cls.detect_intent(text)

        # 本地能处理的高置信度意图
        if conf >= 0.5 or intent in ("greeting","thanks","bye","help"):
            return {"content": cls.reason(text), "source": "local", "intent": intent}

        # 尝试LLM增强
        if use_llm:
            try:
                from agents.multi_model import ModelRouter
                resp = ModelRouter.smart_chat(
                    messages=[{"role": "user", "content": text}],
                    mode="fast"
                )
                content = resp.get("content", "")
                if content and "[AI离线]" not in content and "不可用" not in content:
                    return {"content": content, "source": "llm", "intent": intent}
            except:
                pass

        # LLM不可用 -> 本地最佳猜测
        return {"content": cls.reason(text), "source": "local", "intent": intent}

# 全局单例
local_ai = LocalAI()
