''''''
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_record_and_predict():
    from tools.predict_engine import predict_engine
    for i in range(20):
        predict_engine.record("test_metric", 100 + i * 2)
    result = predict_engine.predict("test_metric", horizon=3)
    assert result["ok"] is True
    assert len(result["predictions"]) == 3
    assert result["confidence"] in ("low", "medium", "high")

def test_insufficient_data():
    from tools.predict_engine import predict_engine
    result = predict_engine.predict("nonexistent", horizon=3)
    assert result["ok"] is False

def test_anomaly_detection():
    from tools.predict_engine import predict_engine
    for i in range(30):
        predict_engine.record("stable", 100 + (i % 3))
    predict_engine.record("stable", 500)  # spike
    result = predict_engine.predict("stable", horizon=3)
    assert result["ok"] is True

def test_seasonal():
    from tools.predict_engine import predict_engine
    for i in range(50):
        val = 100 + 20 * (1 if i % 7 < 3 else -1)
        predict_engine.record("seasonal_test", val)
    result = predict_engine.predict("seasonal_test", horizon=7)
    assert len(result["predictions"]) == 7

def test_get_stats():
    from tools.predict_engine import predict_engine
    stats = predict_engine.get_stats()
    assert "metrics" in stats
    assert "total_points" in stats