"""全能引擎 — 预测告警 + 智能定价 + 自修复 + 知识图谱"""
import json, os, time
from datetime import datetime, timedelta
from collections import defaultdict
from tools.logger import get_logger

logger = get_logger("engine")

class PredictEngine:
    """预测引擎 — 基于历史趋势的智能告警"""
    _history = defaultdict(list)  # {metric: [(timestamp, value), ...]}
    _max_history = 1000

    @classmethod
    def record(cls, metric: str, value: float):
        cls._history[metric].append((time.time(), value))
        if len(cls._history[metric]) > cls._max_history:
            cls._history[metric] = cls._history[metric][-cls._max_history:]

    @classmethod
    def predict(cls, metric: str, minutes_ahead: int = 30) -> dict:
        """预测未来趋势，返回是否可能超标"""
        data = cls._history.get(metric, [])
        if len(data) < 10:
            return {"predictable": False, "reason": "数据不足"}
        recent = data[-20:]
        values = [v for _, v in recent]
        avg = sum(values) / len(values)
        trend = (values[-1] - values[0]) / max(len(values), 1)
        predicted = values[-1] + trend * (minutes_ahead / 2)  # 假设2分钟一个数据点
        threshold = {"cpu": 85, "memory": 85, "disk": 90}.get(metric, 80)
        return {
            "predictable": True,
            "current": values[-1],
            "predicted": round(predicted, 1),
            "trend": "up" if trend > 0.5 else "down" if trend < -0.5 else "stable",
            "will_exceed": predicted > threshold,
            "eta_minutes": round((threshold - values[-1]) / trend * 2) if trend > 0 else None
        }

class SmartPricing:
    """智能定价 — 竞品监控+自动调价"""
    _rules = []
    _price_history = {}

    @classmethod
    def load_rules(cls):
        """从state加载定价规则"""
        try:
            from state import state
            cls._rules = state._data.get("pricing_rules", [])
        except: pass

    @classmethod
    def analyze_competitor(cls, product_id: str, our_price: float, competitor_prices: list) -> dict:
        """分析竞品价格，建议调整"""
        if not competitor_prices:
            return {"action": "hold", "reason": "无竞品数据"}
        avg_comp = sum(competitor_prices) / len(competitor_prices)
        min_comp = min(competitor_prices)
        if our_price > avg_comp * 1.15:
            return {"action": "lower", "suggested": round(avg_comp * 0.95, 2),
                    "reason": f"高于均价15% (均价{avg_comp})"}
        if our_price < min_comp * 0.85:
            return {"action": "raise", "suggested": round(min_comp * 0.95, 2),
                    "reason": f"远低于最低价 (最低{min_comp})"}
        return {"action": "hold", "reason": f"价格合理 (均价{avg_comp})"}

class SelfHealing:
    """自修复引擎"""
    _failure_count = defaultdict(int)
    _last_restart = {}

    @classmethod
    def record_failure(cls, endpoint: str):
        cls._failure_count[endpoint] += 1
        cls._failure_count[f"total_{int(time.time()/300)}"] += 1  # 5分钟窗口

    @classmethod
    def should_heal(cls, endpoint: str) -> bool:
        """判断是否需要自愈"""
        count = cls._failure_count.get(endpoint, 0)
        total_5min = cls._failure_count.get(f"total_{int(time.time()/300)}", 0)
        if count >= 5 and time.time() - cls._last_restart.get(endpoint, 0) > 600:
            return True
        if total_5min >= 20:
            return True
        return False

    @classmethod
    async def heal(cls, endpoint: str = "all") -> dict:
        """执行自愈动作"""
        import subprocess
        results = []
        if endpoint == "all" or "docker" in endpoint:
            r = subprocess.run(["docker", "restart", "mall-ai-agent"],
                             capture_output=True, text=True, timeout=30)
            results.append({"action": "restart_container", "ok": r.returncode==0})
        cls._last_restart[endpoint] = time.time()
        cls._failure_count[endpoint] = 0
        return {"healed": True, "results": results}

class KnowledgeGraph:
    """知识图谱 — 关联商品/用户/订单/域名"""
    _nodes = {}
    _edges = []

    @classmethod
    def add_node(cls, node_type: str, node_id: str, properties: dict = None):
        key = f"{node_type}:{node_id}"
        cls._nodes[key] = {"type": node_type, "id": node_id, "props": properties or {}}

    @classmethod
    def add_edge(cls, from_type: str, from_id: str, to_type: str, to_id: str, relation: str):
        cls._edges.append({"from": f"{from_type}:{from_id}", "to": f"{to_type}:{to_id}", "relation": relation})

    @classmethod
    def query(cls, node_type: str, node_id: str = None, relation: str = None) -> list:
        """查询关联节点"""
        results = []
        prefix = f"{node_type}:{node_id}" if node_id else node_type
        for edge in cls._edges:
            if edge["from"].startswith(prefix):
                if not relation or edge["relation"] == relation:
                    to_node = cls._nodes.get(edge["to"])
                    if to_node:
                        results.append({"node": to_node, "relation": edge["relation"]})
            if edge["to"].startswith(prefix):
                if not relation or edge["relation"] == relation:
                    from_node = cls._nodes.get(edge["from"])
                    if from_node:
                        results.append({"node": from_node, "relation": edge["relation"] + "_reverse"})
        return results

class BusinessEngine:
    """业务增长引擎 — 数据驱动的运营建议"""
    
    @classmethod
    def analyze_sales(cls, orders: list) -> dict:
        """分析销售数据，推荐爆品"""
        if not orders: return {"top_products": [], "trending": [], "suggestion": "暂无订单数据"}
        product_sales = defaultdict(lambda: {"count": 0, "revenue": 0})
        for o in orders:
            pid = o.get("product_id", o.get("goods_id", "unknown"))
            price = float(o.get("price", o.get("amount", 0)))
            product_sales[pid]["count"] += 1
            product_sales[pid]["revenue"] += price
        ranked = sorted(product_sales.items(), key=lambda x: x[1]["revenue"], reverse=True)[:10]
        top = [{"product_id": pid, "sales": d["count"], "revenue": round(d["revenue"], 2)} for pid, d in ranked]
        suggestion = "热门商品推荐: " + ", ".join([p["product_id"] for p in top[:3]])
        return {"top_products": top, "suggestion": suggestion}