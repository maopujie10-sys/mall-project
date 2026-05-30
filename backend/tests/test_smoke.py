"""冒烟测试 -- 快速验证核心功能可用"""
import pytest
import asyncio
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


class TestSmoke:
    """核心功能冒烟测试套件"""
    
    def test_config_loads(self):
        """配置加载正常"""
        from config import config
        assert config is not None

    def test_state_works(self):
        """状态管理正常"""
        from state import state
        assert state is not None
        assert hasattr(state, '_data')

    def test_logger_works(self):
        """日志系统正常"""
        from tools.logger import get_logger
        logger = get_logger("test")
        assert logger is not None

    def test_auth_imports(self):
        """认证模块可导入"""
        from auth import verify_token, create_jwt, verify_jwt
        assert callable(verify_token)

    def test_db_imports(self):
        """数据库模块可导入"""
        from db import db
        assert db is not None

    def test_cache_works(self):
        """缓存系统正常"""
        from tools.cache import cached
        assert callable(cached)

    def test_all_routers_importable(self):
        """所有路由模块可导入无语法错误"""
        import glob
        routers = glob.glob("routers/*.py")
        for r in routers:
            if "__init__" in r:
                continue
            mod_name = "routers." + os.path.splitext(os.path.basename(r))[0]
            try:
                __import__(mod_name)
            except SyntaxError as e:
                pytest.fail(f"语法错误 {mod_name}: {e}")
            except ImportError:
                pass  # 缺少依赖可以接受

    def test_all_tools_importable(self):
        """所有工具模块可导入无语法错误"""
        import glob
        tools = glob.glob("tools/*.py")
        for t in tools:
            if "__init__" in t:
                continue
            mod_name = "tools." + os.path.splitext(os.path.basename(t))[0]
            try:
                __import__(mod_name)
            except SyntaxError as e:
                pytest.fail(f"语法错误 {mod_name}: {e}")
            except ImportError:
                pass

    def test_no_bom_files(self):
        """源文件无BOM编码"""
        import glob
        bom_files = []
        for f in glob.glob("**/*.py", recursive=True):
            with open(f, "rb") as fh:
                if fh.read(3) == b'\xef\xbb\xbf':
                    bom_files.append(f)
        assert len(bom_files) == 0, f"存在BOM文件: {bom_files}"

    def test_key_managers_work(self):
        """API Key管理模块正常"""
        from tools.key_manager import ApiKeyManager
        assert ApiKeyManager is not None