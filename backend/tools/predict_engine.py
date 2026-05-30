"""棰勬祴寮曟搸 -- 鏃跺簭棰勬祴(閿€閲?娴侀噺/搴撳瓨/寮傚父)"""
import time, json, asyncio
from collections import defaultdict
from typing import List, Dict
from tools.logger import get_logger

logger = get_logger("predict")

class PredictEngine:
    """AI棰勬祴寮曟搸 -- 绉诲姩骞冲潎 + 瓒嬪娍 + 寮傚父妫€娴?""
    _history: Dict[str, List[Dict]] = defaultdict(list)

    @classmethod
    def record(cls, metric: str, value: float, tags: Dict = None):
        """璁板綍鎸囨爣鏁版嵁鐐?""
        cls._history[metric].append({
            "time": time.time(), "value": value, "tags": tags or {}
        })
        # 淇濈暀鏈€杩?000鏉?
        if len(cls._history[metric]) > 1000:
            cls._history[metric] = cls._history[metric][-1000:]

    @classmethod
    def predict(cls, metric: str, horizon: int = 7) -> Dict:
        """棰勬祴鏈潵N涓懆鏈?""
        data = cls._history.get(metric, [])
        if len(data) < 3:
            return {"ok": False, "error": f"鏁版嵁涓嶈冻({len(data)}鐐?, 闇€瑕佽嚦灏?涓暟鎹偣", "predictions": []}

        values = [d["value"] for d in data]

        # Holt-Winters 涓夐噸鎸囨暟骞虫粦
        alpha, beta, gamma = 0.3, 0.1, 0.1  # 骞虫粦绯绘暟
        period = min(7, len(values) // 2)
        if period < 2: period = 2

        # 鍒濆鍖?
        level = values[0]
        trend = (sum(values[period:2*period]) - sum(values[:period])) / (period * period) if len(values) >= 2*period else 0
        seasonals = [values[i] - level for i in range(period)] if len(values) >= period else [0]

        # 鎷熷悎鍘嗗彶
        fitted = []
        for t in range(len(values)):
            s_idx = t % period
            if t == 0:
                fitted.append(values[0])
                continue
            prev_level = level
            level = alpha * (values[t] - seasonals[s_idx]) + (1 - alpha) * (level + trend)
            trend = beta * (level - prev_level) + (1 - beta) * trend
            seasonals[s_idx] = gamma * (values[t] - level) + (1 - gamma) * seasonals[s_idx]
            fitted.append(level + trend + seasonals[s_idx])

        # 棰勬祴
        predictions = []
        last_level = level
        last_trend = trend
        for i in range(horizon):
            s_idx = (len(values) + i) % period
            if s_idx < len(seasonals):
                pred = last_level + last_trend * (i + 1) + seasonals[s_idx]
            else:
                pred = last_level + last_trend * (i + 1)
            last_level = last_level + last_trend
            predictions.append(round(max(0, pred), 2))

        # 瓒嬪娍鐧惧垎姣?
        recent_fit_avg = sum(fitted[-min(5,len(fitted)):]) / min(5,len(fitted)) if fitted else values[-1]
        old_avg = sum(values[:max(1,len(values)//3)]) / max(1,len(values)//3)
        trend = (recent_fit_avg - old_avg) / max(abs(old_avg), 1) * 100
        ma = level

        # 寮傚父妫€娴?
        recent = values[-10:] if len(values) >= 10 else values
        mean = sum(recent) / len(recent)
        std = (sum((v - mean) ** 2 for v in recent) / len(recent)) ** 0.5
        anomalies = [{"index": i, "value": v, "z_score": round((v - mean) / std, 2) if std > 0 else 0}
                     for i, v in enumerate(values[-20:]) if std > 0 and abs(v - mean) > 2 * std]

        return {
            "ok": True, "metric": metric, "horizon": horizon,
            "current": round(values[-1], 2), "mean": round(ma, 2),
            "trend_pct": round(trend, 1), "direction": "up" if trend > 1 else "down" if trend < -1 else "stable",
            "predictions": predictions,
            "anomalies": anomalies[-3:],
            "confidence": "high" if len(data) > 30 else "medium" if len(data) > 10 else "low"
        }

    @classmethod
    def _detect_seasonal(cls, values: List[float], max_period: int = 7) -> List[float]:
        """绠€鍗曞鑺傛€ф娴?""
        if len(values) < 14:
            return []
        for period in range(3, min(max_period + 1, len(values) // 3)):
            segments = []
            for i in range(0, len(values) - period, period):
                segments.append(values[i:i + period])
            if len(segments) >= 2:
                return segments[-1]
        return []

    @classmethod
    def get_stats(cls) -> Dict:
        return {
            "metrics": list(cls._history.keys()),
            "total_points": sum(len(v) for v in cls._history.values())
        }

    @classmethod
    def save(cls):
        """持久化到SQLite"""
        from tools.memory_store import memory_store
        import json
        data = {k: v[-200:] for k, v in cls._history.items()}
        memory_store.set_knowledge("predict_history", json.dumps(data, ensure_ascii=False))

    @classmethod
    def load(cls):
        """从SQLite恢复"""
        from tools.memory_store import memory_store
        import json
        try:
            data = memory_store.get_knowledge("predict_history")
            if data:
                cls._history.update({k: v for k, v in json.loads(data).items()})
            return True
        except:
            return False

predict_engine = PredictEngine()

try:
    PredictEngine.load()
except:
    pass
