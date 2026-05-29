"""Key管理测试"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_key_manager_init():
    from tools.key_manager import KeyManager
    km = KeyManager()
    assert km is not None
    templates = km.get_templates()
    assert len(templates) >= 4

def test_key_crud():
    from tools.key_manager import KeyManager
    km = KeyManager()
    r = km.add_key("test_openai", "sk-test123", "openai", "OpenAI测试")
    assert r is True
    keys = km.list_keys()
    assert any(k["name"] == "test_openai" for k in keys)
    km.delete_key("test_openai")

def test_get_active_key():
    from tools.key_manager import KeyManager
    km = KeyManager()
    key = km.get_active_key("openai")
    assert key is None or isinstance(key, str)

def test_toggle_key():
    from tools.key_manager import KeyManager
    km = KeyManager()
    km.add_key("toggle_test", "sk-test", "openai", "测试")
    r = km.set_active("toggle_test", True)
    assert r is True
    km.delete_key("toggle_test")