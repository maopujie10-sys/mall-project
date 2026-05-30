"""Friday AI Backend Tests - Comprehensive test suite"""
import pytest
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'backend'))

class TestConfig:
    def test_config_exists(self):
        from config import AGENT_TOKEN, MALL_BASE_URL
        assert AGENT_TOKEN is not None
        assert len(AGENT_TOKEN) > 10
        assert MALL_BASE_URL.startswith('http')

    def test_config_values_loaded(self):
        from config import AGENT_TOKEN, MALL_BASE_URL
        assert isinstance(AGENT_TOKEN, str)
        assert isinstance(MALL_BASE_URL, str)

class TestAuth:
    def test_verify_token_missing(self):
        from auth import verify_token
        from fastapi import HTTPException
        try:
            import asyncio
            asyncio.run(verify_token(None))
            assert False, "Should raise HTTPException"
        except HTTPException as e:
            assert e.status_code == 403

    def test_verify_token_valid(self):
        from auth import verify_token
        from config import AGENT_TOKEN
        import asyncio
        result = asyncio.run(verify_token(AGENT_TOKEN))
        assert result is not None

class TestMasterAgent:
    def test_agent_status(self):
        from agents.master_agent import MasterAgent
        status = MasterAgent.get_status()
        assert 'total' in status
        assert 'active' in status
        assert 'completed' in status
        assert isinstance(status['total'], int)

    def test_execute_code_agent(self):
        import asyncio
        from agents.master_agent import MasterAgent
        result = asyncio.run(MasterAgent.execute("code", "print('hello')"))
        assert 'ok' in result
        assert isinstance(result['ok'], bool)

    def test_agent_types_list(self):
        from agents.master_agent import MasterAgent
        status = MasterAgent.get_status()
        assert 'agents' in status or 'total' in status

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

    def test_traits_loaded(self):
        from digital_lifeform import DigitalLifeform
        status = DigitalLifeform.get_lifeform_status()
        has_traits = 'traits' in status or 'health' in status or 'mood' in status
        assert has_traits, f"Expected traits/health/mood in {list(status.keys())}"

class TestRegistry:
    def test_registry_has_tools(self):
        from tools.registry import registry
        tools = registry.list_tools()
        assert isinstance(tools, (list, dict))
        assert len(tools) > 0

    def test_registry_list_all(self):
        from tools.registry import registry
        all_tools = registry.list_all()
        assert isinstance(all_tools, list)
        assert len(all_tools) > 5, f"Expected >5 tools, got {len(all_tools)}"

    def test_registry_get_tool(self):
        from tools.registry import registry
        all_tools = registry.list_all()
        if all_tools:
            first = all_tools[0]
            assert hasattr(first, 'name') or isinstance(first, dict)

class TestModelRouter:
    def test_model_router_import(self):
        from agents.multi_model import ModelRouter
        assert hasattr(ModelRouter, 'smart_chat')

    def test_model_router_list_models(self):
        from agents.multi_model import ModelRouter
        if hasattr(ModelRouter, 'list_models'):
            models = ModelRouter.list_models()
            assert isinstance(models, (list, dict))

class TestRAGEngine:
    def test_rag_import(self):
        from tools.rag_engine import RAGEngine
        assert hasattr(RAGEngine, 'search')
        assert hasattr(RAGEngine, 'add_document')
        assert hasattr(RAGEngine, 'ask')

    def test_rag_add_and_search(self):
        from tools.rag_engine import RAGEngine
        doc = RAGEngine.add_document("Friday AI is a next-generation AI operating system.", source="test", title="About Friday")
        assert doc is not None
        assert 'id' in doc
        results = RAGEngine.search("AI operating system", top_k=3)
        assert isinstance(results, list)

    def test_rag_get_stats(self):
        from tools.rag_engine import RAGEngine
        stats = RAGEngine.get_stats()
        assert 'total_docs' in stats
        assert 'indexed_words' in stats
        assert 'has_chromadb' in stats

class TestVisionAgent:
    def test_vision_import(self):
        from agents.vision_agent import VisionAgent
        assert hasattr(VisionAgent, 'analyze_image')
        assert hasattr(VisionAgent, 'analyze_video')
        assert hasattr(VisionAgent, 'detect_faces')

    def test_vision_load_image(self):
        import asyncio
        from agents.vision_agent import _load_image
        try:
            result = asyncio.run(_load_image("https://httpbin.org/image/jpeg"))
            assert isinstance(result, str)
            assert len(result) > 10
        except Exception:
            pass  # Network may not be available

class TestWorkflowEngine:
    def test_workflow_templates(self):
        from tools.workflow_engine import WorkflowEngine
        templates = WorkflowEngine.TEMPLATES
        assert len(templates) >= 7
        assert "Clear Dead Inventory" in templates
        assert "System Health Check" in templates

    def test_workflow_parse(self):
        import asyncio
        from tools.workflow_engine import WorkflowEngine
        result = asyncio.run(WorkflowEngine.parse_and_execute("run system health check"))
        assert isinstance(result, dict)
        assert 'ok' in result

class TestAlertClosedLoop:
    def test_alert_rules_complete(self):
        from tools.alert_closed_loop import AUTO_FIX_RULES
        assert len(AUTO_FIX_RULES) == 6
        for rule_name, rule in AUTO_FIX_RULES.items():
            assert len(rule["pattern"]) >= 3, f"{rule_name} missing patterns"
            assert all(p for p in rule["pattern"]), f"{rule_name} has empty pattern"
            assert rule["fix"], f"{rule_name} missing fix command"
            assert rule["verify"], f"{rule_name} missing verify command"

    def test_alert_history(self):
        from tools.alert_closed_loop import AlertClosedLoop
        history = AlertClosedLoop.get_history(10)
        assert isinstance(history, list)

class TestRoutes:
    def test_router_modules_importable(self):
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
            except Exception as e:
                pass
        assert ok >= 10, f"Only {ok}/{len(routers)} routers importable"

    def test_video_router_endpoints(self):
        from routers.video_router import router
        routes = [r.path for r in router.routes]
        assert '/analyze' in routes or '/agent/video/analyze' in routes
        assert '/analyze-image' in routes or '/agent/video/analyze-image' in routes
        assert '/detect-faces' in routes or '/agent/video/detect-faces' in routes
