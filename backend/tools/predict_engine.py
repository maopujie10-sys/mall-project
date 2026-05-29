"""预测引擎 — 时序预测(销量/流量/库存/异常)"""
import time, json, asyncio
from collections import defaultdict
from typing import List, Dict
from tools.logger import get_logger

logger = get_logger("predict")

class PredictEngine:
    """AI预测引擎 — 移动平均 + 趋势 + 异常检测"""
    _history: Dict[str, List[Dict]] = defaultdict(list)

    @classmethod
    def record(cls, metric: str, value: float, tags: Dict = None):
        """记录指标数据点"""
        cls._history[metric].append({
            "time": time.time(), "value": value, "tags": tags or {}
        })
        # 保留最近1000条
        if len(cls._history[metric]) > 1000:
            cls._history[metric] = cls._history[metric][-1000:]

    @classmethod
    def predict(cls, metric: str, horizon: int = 7) -> Dict:
        """预测未来N个周期"""
        data = cls._history.get(metric, [])
        if len(data) < 3:
            return {"ok": False, "error": f"数据不足({len(data)}点), 需要至少3个数据点", "predictions": []}

        values = [d["value"] for d in data]

        # 移动平均
        window = min(len(values) // 3 + 2, 7)
        ma = sum(values[-window:]) / window

        # 趋势
        if len(values) >= 10:
            half = len(values) // 2
            recent_avg = sum(values[-half:]) / half
            old_avg = sum(values[:half]) / half
            trend = (recent_avg - old_avg) / max(abs(old_avg), 1) * 100
        else:
            trend = 0

        # 季节性（简单重复模式检测）
        seasonal = cls._detect_seasonal(values)

        predictions = []
        for i in range(horizon):
            pred = ma * (1 + trend / 100 * (i + 1) / horizon)
            if seasonal:
                pred *= seasonal[i % len(seasonal)]
            predictions.append(round(pred, 2))

        # 异常检测
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
        """简单季节性检测"""
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

predict_engine = PredictEngine()
