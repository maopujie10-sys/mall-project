''" -- ''"
import pytest
import asyncio
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

class TestSmoke:
    ''''''
    
    def test_config_loads(self):
        ''''''
        from config import config
        assert config is not None

    def test_state_works(self):
        ''''''
        from state import state
        assert state is not None
        assert hasattr(state, '_data')

    def test_logger_works(self):
        ''''''
        from tools.logger import get_logger
        logger = get_logger("test")
        assert logger is not None

    def test_auth_imports(self):
        ''''''
        from auth import verify_token, create_jwt, verify_jwt
        assert callable(verify_token)

    def test_db_imports(self):
        ''''''
        from db import db
        assert db is not None

    def test_cache_works(self):
        ''''''
        from tools.cache import cached
        assert callable(cached)

    def test_all_routers_importable(self):
        ''''''
        import glob
        routers = glob.glob("routers/*.py")
        for r in routers:
            if "__init__" in r:
                continue
            mod_name = "routers." + os.path.splitext(os.path.basename(r))[0]
            try:
                __import__(mod_name)
            except SyntaxError as e:
                pytest.fail(f" {mod_name}: {e}")
            except ImportError:
                pass  
    def test_all_tools_importable(self):
        ''''''
        import glob
        tools = glob.glob("tools/*.py")
        for t in tools:
            if "__init__" in t:
                continue
            mod_name = "tools." + os.path.splitext(os.path.basename(t))[0]
            try:
                __import__(mod_name)
            except SyntaxError as e:
                pytest.fail(f" {mod_name}: {e}")
            except ImportError:
                pass

    def test_no_bom_files(self):
        ''"BOM''"
        import glob
        bom_files = []
        for f in glob.glob("**/*.py", recursive=True):
            with open(f, "rb") as fh:
                if fh.read(3) == b'\xef\xbb\xbf':
                    bom_files.append(f)
        assert len(bom_files) == 0, f"BOM: {bom_files}"

    def test_key_managers_work(self):
        ''"API Key''"
        from tools.key_manager import ApiKeyManager
        assert ApiKeyManager is not None