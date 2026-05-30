"""Friday AI Backend Tests - Full Test Suite"""
import pytest
import sys, os, json, asyncio
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'backend'))

# ============================================================
# Config Tests
# ============================================================
class TestConfig:
    def test_config_exists(self):
        from config import AGENT_TOKEN, MALL_BASE_URL
        assert AGENT_TOKEN is not None
        assert len(AGENT_TOKEN) > 10
        assert MALL_BASE_URL.startswith('http')

    def test_config_types(self):
        from config import AGENT_TOKEN, MALL_BASE_URL
        assert isinstance(AGENT_TOKEN, str)
        assert isinstance(MALL_BASE_URL, str)

# ============================================================
# Auth Tests
# ============================================================
class TestAuth:
    def test_verify_token_missing(self):
        from auth import verify_token
        from fastapi import HTTPException
        with pytest.raises(HTTPException) as exc:
            asyncio.run(verify_token(None))
        assert exc.value.status_code == 403

    def test_verify_token_valid(self):
        from auth import verify_token
        from config import AGENT_TOKEN
        result = asyncio.run(verify_token(AGENT_TOKEN))
        assert result is not None

# ============================================================
# Master Agent Tests
# ============================================================
class TestMasterAgent:
    def test_get_status(self):
        from agents.master_agent import MasterAgent
        status = MasterAgent.get_status()
        assert 'total' in status
        assert 'active' in status
        assert isinstance(status['total'], int)

    def test_execute_code(self):
        from agents.master_agent import MasterAgent
        result = asyncio.run(MasterAgent.execute("code", "print('test')"))
        assert isinstance(result, dict)
        assert 'ok' in result

    def test_execute_invalid_type(self):
        from agents.master_agent import MasterAgent
        result = asyncio.run(MasterAgent.execute("nonexistent", "test"))
        assert isinstance(result, dict)

# ============================================================
# Digital Lifeform Tests
# ============================================================
class TestDigitalLifeform:
    def test_get_status(self):
        from digital_lifeform import DigitalLifeform
        status = DigitalLifeform.get_lifeform_status()
        assert status is not None
        assert isinstance(status, dict)

    def test_record_interaction(self):
        from digital_lifeform import DigitalLifeform
        result = DigitalLifeform.record_interaction("test_user", "hello")
        assert result is not None

# ============================================================
# Registry Tests
# ============================================================
class TestRegistry:
    def test_list_tools(self):
        from tools.registry import registry
        tools = registry.list_tools()
        assert isinstance(tools, (list, dict))
        assert len(tools) > 0

    def test_list_all_returns_list(self):
        from tools.registry import registry
        all_tools = registry.list_all()
        assert isinstance(all_tools, list)
        assert len(all_tools) > 5

    def test_tools_have_required_attrs(self):
        from tools.registry import registry
        all_tools = registry.list_all()
        for t in all_tools[:10]:
            assert hasattr(t, 'name'), f"Tool missing name: {t}"

# ============================================================
# Model Router Tests
# ============================================================
class TestModelRouter:
    def test_import(self):
        from agents.multi_model import ModelRouter
        assert hasattr(ModelRouter, 'smart_chat')

    def test_get_key(self):
        from agents.multi_model import ModelRouter
        key = ModelRouter.get_key("openai")
        assert key is not None
        assert isinstance(key, str)

# ============================================================
# RAG Engine Tests
# ============================================================
class TestRAGEngine:
    def test_add_document(self):
        from tools.rag_engine import RAGEngine
        doc = RAGEngine.add_document(
            "Friday AI is an AI operating system for server management.",
            source="test", title="About Friday"
        )
        assert doc is not None
        assert 'id' in doc

    def test_search(self):
        from tools.rag_engine import RAGEngine
        results = RAGEngine.search("AI operating system", top_k=3)
        assert isinstance(results, list)

    def test_get_stats(self):
        from tools.rag_engine import RAGEngine
        stats = RAGEngine.get_stats()
        assert 'total_docs' in stats
        assert 'indexed_words' in stats
        assert 'has_chromadb' in stats

    def test_add_multiple_docs(self):
        from tools.rag_engine import RAGEngine
        docs = ["Server monitoring", "Docker deployment", "Nginx config"]
        for i, d in enumerate(docs):
            r = RAGEngine.add_document(d, source="test", title=f"Doc {i}")
            assert r is not None

# ============================================================
# Vision Agent Tests
# ============================================================
class TestVisionAgent:
    def test_import(self):
        from agents.vision_agent import VisionAgent
        assert hasattr(VisionAgent, 'analyze_image')
        assert hasattr(VisionAgent, 'analyze_video')
        assert hasattr(VisionAgent, 'detect_faces')

    def test_analyze_image_requires_url(self):
        import asyncio
        from agents.vision_agent import VisionAgent
        result = asyncio.run(VisionAgent.analyze_image(image_url=""))
        assert isinstance(result, dict)

# ============================================================
# Workflow Engine Tests
# ============================================================
class TestWorkflowEngine:
    def test_templates_exist(self):
        from tools.workflow_engine import WorkflowEngine
        assert len(WorkflowEngine.TEMPLATES) >= 7

    def test_template_names_not_empty(self):
        from tools.workflow_engine import WorkflowEngine
        for name in WorkflowEngine.TEMPLATES:
            assert name and name.strip(), f"Empty template name found"
            assert name != "''"

    def test_parse_execute_returns_dict(self):
        from tools.workflow_engine import WorkflowEngine
        result = asyncio.run(WorkflowEngine.parse_and_execute("system health check"))
        assert isinstance(result, dict)
        assert 'ok' in result

# ============================================================
# Alert Closed Loop Tests
# ============================================================
class TestAlertClosedLoop:
    def test_rules_complete(self):
        from tools.alert_closed_loop import AUTO_FIX_RULES
        assert len(AUTO_FIX_RULES) == 6
        for name, rule in AUTO_FIX_RULES.items():
            assert len(rule["pattern"]) >= 3, f"{name}: < 3 patterns"
            assert all(p and p.strip() for p in rule["pattern"]), f"{name}: empty pattern"
            assert rule["fix"], f"{name}: no fix command"
            assert rule["verify"], f"{name}: no verify command"
            assert rule["max_retries"] >= 1, f"{name}: invalid max_retries"

    def test_history(self):
        from tools.alert_closed_loop import AlertClosedLoop
        history = AlertClosedLoop.get_history(10)
        assert isinstance(history, list)

    def test_detect_and_fix_no_match(self):
        from tools.alert_closed_loop import AlertClosedLoop
        result = asyncio.run(AlertClosedLoop.detect_and_fix(
            "random_message_that_doesnt_match_any_rule", "", auto_fix=True
        ))
        assert result["matched_rule"] is None
        assert result["fix_attempted"] is False

# ============================================================
# Plugin Router Tests
# ============================================================
class TestPluginRouter:
    def test_marketplace_not_empty(self):
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'backend'))
        # Verify marketplace entries have names
        content = open(os.path.join(os.path.dirname(__file__), '..', '..', 'backend', 'routers', 'plugin_router.py'), 'r', encoding='utf-8').read()
        assert '"name":"Server Monitor"' in content
        assert '"name":"Docker Manager"' in content
        assert '"name":"Mall Brain AI"' in content

    def test_marketplace_count(self):
        import re
        content = open(os.path.join(os.path.dirname(__file__), '..', '..', 'backend', 'routers', 'plugin_router.py'), 'r', encoding='utf-8').read()
        names = re.findall(r'"name":"([^"]+)"', content)
        marketplace_names = [n for n in names if n and n.strip() and ',' not in n]
        assert len(marketplace_names) >= 20, f"Only {len(marketplace_names)} plugin names found"

# ============================================================
# Routes Tests
# ============================================================
class TestRoutes:
    def test_all_routers_importable(self):
        routers = [
            'routers.agent_chat', 'routers.advanced_ai', 'routers.friday_router',
            'routers.lifeform_router', 'routers.server_panel', 'routers.mall_tools',
            'routers.rotation_panel', 'routers.plugin_router', 'routers.voice_router',
            'routers.rag_router', 'routers.workflow_router', 'routers.collab_router',
            'routers.brain_router', 'routers.video_router',
        ]
        ok = 0
        for r in routers:
            try:
                mod = __import__(r, fromlist=['router'])
                if hasattr(mod, 'router'):
                    ok += 1
            except Exception:
                pass
        assert ok >= 10, f"Only {ok}/14 routers importable"

    def test_video_router_endpoints(self):
        from routers.video_router import router
        paths = [r.path for r in router.routes if hasattr(r, 'path')]
        assert '/analyze' in paths
        assert '/analyze-image' in paths
        assert '/detect-faces' in paths

    def test_voice_router_endpoints(self):
        from routers.voice_router import router
        paths = [r.path for r in router.routes if hasattr(r, 'path')]
        assert '/tts' in paths
        assert '/stt' in paths
        assert '/ws' in paths

    def test_rag_router_endpoints(self):
        from routers.rag_router import router
        paths = [r.path for r in router.routes if hasattr(r, 'path')]
        assert '/ingest' in paths
        assert '/ask' in paths
        assert '/stats' in paths
        assert '/ingest-file' in paths or any('ingest-file' in p for p in paths)

    def test_workflow_router_endpoints(self):
        from routers.workflow_router import router
        paths = [r.path for r in router.routes if hasattr(r, 'path')]
        assert '/save' in paths
        assert '/list' in paths
        assert '/execute' in paths
        assert '/templates' in paths

# ============================================================
# Edge Cases / Error Handling
# ============================================================
class TestEdgeCases:
    def test_rag_empty_query(self):
        from tools.rag_engine import RAGEngine
        results = RAGEngine.search("", top_k=5)
        assert isinstance(results, list)

    def test_workflow_empty_input(self):
        from tools.workflow_engine import WorkflowEngine
        result = asyncio.run(WorkflowEngine.parse_and_execute(""))
        assert isinstance(result, dict)

    def test_alert_empty_input(self):
        from tools.alert_closed_loop import AlertClosedLoop
        result = asyncio.run(AlertClosedLoop.detect_and_fix("", "", auto_fix=True))
        assert result["matched_rule"] is None

    def test_registry_empty_execute(self):
        from tools.registry import registry
        try:
            result = asyncio.run(registry.execute("nonexistent_tool_xyz"))
            assert isinstance(result, dict)
        except Exception:
            pass  # Expected to fail for nonexistent tool
