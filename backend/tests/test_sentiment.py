''''''
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_positive():
    from tools.sentiment_analyzer import sentiment_analyzer
    r = sentiment_analyzer.analyze(",")
    assert r["sentiment"] == "positive"

def test_negative():
    from tools.sentiment_analyzer import sentiment_analyzer
    r = sentiment_analyzer.analyze(",")
    assert r["sentiment"] == "negative" or r["needs_attention"]

def test_negator():
    from tools.sentiment_analyzer import sentiment_analyzer
    r = sentiment_analyzer.analyze('')
    assert r["sentiment"] in ("negative", "neutral")

def test_urgent():
    from tools.sentiment_analyzer import sentiment_analyzer
    r = sentiment_analyzer.analyze(",")
    assert r["urgency"] > 0

def test_neutral():
    from tools.sentiment_analyzer import sentiment_analyzer
    r = sentiment_analyzer.analyze('')
    assert r["sentiment"] in ("neutral", "positive")