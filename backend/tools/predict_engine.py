"""预测引擎 -- 时序预测(销量/流量/库存/异常)"""
import time, json, asyncio
from collections import defaultdict
from typing import List, Dict
from tools.logger import get_logger

logger = get_logger("predict")

class PredictEngine:
    """AI预测引擎 -- 移动平均 + 趋势 + 异常检测"""
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

        # Holt-Winters 三重指数平滑
        alpha, beta, gamma = 0.3, 0.1, 0.1  # 平滑系数
        period = min(7, len(values) // 2)
        if period < 2: period = 2

        # 初始化
        level = values[0]
        trend = (sum(values[period:2*period]) - sum(values[:period])) / (period * period) if len(values) >= 2*period else 0
        seasonals = [values[i] - level for i in range(period)] if len(values) >= period else [0]

        # 拟合历史
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

        # 预测
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

        # 趋势百分比
        recent_fit_avg = sum(fitted[-min(5,len(fitted)):]) / min(5,len(fitted)) if fitted else values[-1]
        old_avg = sum(values[:max(1,len(values)//3)]) / max(1,len(values)//3)
        trend = (recent_fit_avg - old_avg) / max(abs(old_avg), 1) * 100
        ma = level

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

    @classmethod
    def forecast_sales(cls, days: int = 7) -> Dict:
        '''销量预测 — 移动平均+趋势'''
        sales_data = cls._history.get('sales', [])
        if len(sales_data) < 3:
            return {'ok': False, 'error': '数据不足'}
        recent = sales_data[-14:]
        avg = sum(recent) / len(recent)
        trend = (sum(recent[-3:])/3) / (sum(recent[:3])/3) if len(recent)>=6 else 1.0
        forecast = [round(avg * (trend**i), 0) for i in range(1, days+1)]
        return {'ok': True, 'forecast': forecast, 'avg': round(avg,1), 'trend': round(trend,2)}

    @classmethod
    def detect_anomaly(cls, metric: str = 'sales') -> Dict:
        '''异常检测 — 3-sigma'''
        data = cls._history.get(metric, [])
        if len(data) < 10: return {'ok': False}
        avg = sum(data)/len(data); std = (sum((x-avg)**2 for x in data)/len(data))**0.5
        latest = data[-1]; z = (latest-avg)/std if std>0 else 0
        return {'ok': True, 'latest': latest, 'avg': round(avg,1), 'z_score': round(z,2), 'anomaly': abs(z)>2.5}

predict_engine = PredictEngine()

try:
    PredictEngine.load()
except:
    pass
