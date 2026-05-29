"""情感分析测试"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_positive():
    from tools.sentiment_analyzer import sentiment_analyzer
    r = sentiment_analyzer.analyze("这个商品非常好，品质很棒")
    assert r["sentiment"] == "positive"

def test_negative():
    from tools.sentiment_analyzer import sentiment_analyzer
    r = sentiment_analyzer.analyze("太差了，质量很烂，坑人")
    assert r["sentiment"] == "negative" or r["needs_attention"]

def test_negator():
    from tools.sentiment_analyzer import sentiment_analyzer
    r = sentiment_analyzer.analyze("不是很好")
    assert r["sentiment"] in ("negative", "neutral")

def test_urgent():
    from tools.sentiment_analyzer import sentiment_analyzer
    r = sentiment_analyzer.analyze("赶紧退款，马上处理")
    assert r["urgency"] > 0

def test_neutral():
    from tools.sentiment_analyzer import sentiment_analyzer
    r = sentiment_analyzer.analyze("今天天气不错")
    assert r["sentiment"] in ("neutral", "positive")