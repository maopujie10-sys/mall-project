"""???? ? ????????????????"""
import sys, os, asyncio

def test_imports():
    """???????????"""
    modules = [
        "main",
        "auth",
        "state",
        "config",
        "tools.ai_client",
        "tools.rate_limiter",
        "tools.logger",
        "tools.workflow_engine",
        "tools.rag_engine",
        "tools.alert_closed_loop",
        "tools.multimodal_engine",
        "routers.agent_chat",
        "routers.alert",
        "routers.workflow_router",
        "routers.voice_router",
    ]
    failed = []
    for mod in modules:
        try:
            __import__(mod)
            print(f"  OK  {mod}")
        except Exception as e:
            failed.append(f"{mod}: {e}")
            print(f"  FAIL {mod}: {e}")
    
    if failed:
        print(f"\n{len(failed)} import failures")
        return False
    print("\nAll {0} modules imported successfully".format(len(modules)))
    return True

def test_config():
    """??????"""
    from config import DEFAULT_TOKEN, TELEGRAM_BOT_TOKEN
    assert DEFAULT_TOKEN, "DEFAULT_TOKEN not set"
    print(f"  OK  DEFAULT_TOKEN: {'SET' if DEFAULT_TOKEN else 'NOT SET'}")
    print(f"  OK  TELEGRAM_BOT_TOKEN: {'SET' if TELEGRAM_BOT_TOKEN else 'NOT SET'}")
    return True

def test_state():
    """??????"""
    from state import state
    test_key = "_smoke_test_" + str(os.getpid())
    state._data[test_key] = "hello"
    assert state._data.get(test_key) == "hello"
    del state._data[test_key]
    print("  OK  state read/write")
    return True

def test_ai_client():
    """??AI???(?????API)"""
    from tools.ai_client import pick_model
    # Test model selection logic
    model = pick_model(task="simple query", steps=1, has_image=False)
    assert model, "No model selected"
    print(f"  OK  pick_model: {model}")
    return True

def test_rate_limiter():
    """?????"""
    from tools.rate_limiter import _get_limit
    limit, window = _get_limit("/agent/chat")
    assert limit > 0
    assert window > 0
    print(f"  OK  rate limit: {limit}/{window}s")
    return True

def test_workflow_templates():
    """???????"""
    from tools.workflow_engine import WorkflowEngine
    assert len(WorkflowEngine.TEMPLATES) >= 6
    print(f"  OK  workflow templates: {len(WorkflowEngine.TEMPLATES)}")
    return True

def test_alert_rules():
    """????????"""
    from tools.alert_closed_loop import AUTO_FIX_RULES
    assert len(AUTO_FIX_RULES) >= 5
    print(f"  OK  alert fix rules: {len(AUTO_FIX_RULES)}")
    return True

def test_multimodal():
    """???????"""
    from tools.multimodal_engine import multimodal_engine
    assert multimodal_engine is not None
    print("  OK  multimodal engine singleton")
    return True

async def main():
    print("=" * 50)
    print("Friday AI OS - Smoke Tests")
    print("=" * 50)
    
    tests = [
        ("Imports", test_imports),
        ("Config", test_config),
        ("State", test_state),
        ("AI Client", test_ai_client),
        ("Rate Limiter", test_rate_limiter),
        ("Workflow Templates", test_workflow_templates),
        ("Alert Rules", test_alert_rules),
        ("Multimodal", test_multimodal),
    ]
    
    passed = 0
    failed = 0
    for name, test_fn in tests:
        print(f"\n[{name}]")
        try:
            if test_fn():
                passed += 1
        except Exception as e:
            print(f"  FAIL: {e}")
            failed += 1
    
    print(f"\n{'=' * 50}")
    print(f"Results: {passed} passed, {failed} failed out of {len(tests)}")
    return failed == 0

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
