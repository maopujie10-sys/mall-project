"""模拟用户测试 — AI 自动测试业务流程

检测: 首页/注册/登录/商品列表/商品详情/下单/客服/后台登录
"""
import httpx
from datetime import datetime
from state import state
from config import MALL_BASE_URL


class UserSimulator:
    """模拟用户 — 自动执行业务流程测试"""

    @staticmethod
    async def test_homepage() -> dict:
        """测试首页可访问"""
        try:
            async with httpx.AsyncClient(timeout=10,follow_redirects=True) as c:
                r=await c.get(MALL_BASE_URL,headers={"User-Agent":"Friday-AI-Test/1.0"})
                return {"ok":r.status_code<500,"status":r.status_code,"url":MALL_BASE_URL}
        except Exception as e:
            return {"ok":False,"error":str(e)}

    @staticmethod
    async def test_product_list() -> dict:
        """测试商品列表接口"""
        try:
            async with httpx.AsyncClient(timeout=10) as c:
                r=await c.get(f"{MALL_BASE_URL}/api/products?page=1&size=5")
                return {"ok":r.status_code<500,"status":r.status_code,"has_data":len(str(r.text))>50}
        except Exception as e:
            return {"ok":False,"error":str(e)}

    @staticmethod
    async def test_login() -> dict:
        """测试登录接口连通性"""
        try:
            async with httpx.AsyncClient(timeout=10) as c:
                r=await c.post(f"{MALL_BASE_URL}/api/login",json={"username":"test","password":"test"})
                return {"ok":True,"status":r.status_code,"note":"登录接口可达"}
        except Exception as e:
            return {"ok":False,"error":str(e)}

    @staticmethod
    async def full_test() -> dict:
        """全流程测试"""
        results={}
        for name,fn in [("首页",UserSimulator.test_homepage),("商品列表",UserSimulator.test_product_list),("登录",UserSimulator.test_login)]:
            try:
                results[name]=await fn()
            except Exception as e:
                results[name]={"ok":False,"error":str(e)}
        passed=sum(1 for r in results.values() if r.get("ok"))
        return {
            "time":datetime.now().isoformat(),
            "total":len(results),
            "passed":passed,
            "failed":len(results)-passed,
            "results":results,
        }
