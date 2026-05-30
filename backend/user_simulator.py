''" -- AI 

: ///
''"
import httpx
from datetime import datetime
from state import state
from config import MALL_BASE_URL


class UserSimulator:
    ''" -- ''"

    @staticmethod
    async def test_homepage() -> dict:
        ''''''
        try:
            async with httpx.AsyncClient(timeout=10,follow_redirects=True) as c:
                r=await c.get(MALL_BASE_URL,headers={"User-Agent":"Friday-AI-Test/1.0"})
                return {"ok":r.status_code<500,"status":r.status_code,"url":MALL_BASE_URL}
        except Exception as e:
            return {"ok":False,"error":str(e)}

    @staticmethod
    async def test_product_list() -> dict:
        ''''''
        try:
            async with httpx.AsyncClient(timeout=10) as c:
                r=await c.get(f"{MALL_BASE_URL}/api/products?page=1&size=5")
                return {"ok":r.status_code<500,"status":r.status_code,"has_data":len(str(r.text))>50}
        except Exception as e:
            return {"ok":False,"error":str(e)}

    @staticmethod
    async def test_login() -> dict:
        ''''''
        try:
            async with httpx.AsyncClient(timeout=10) as c:
                r=await c.post(f"{MALL_BASE_URL}/api/login",json={"username":"test","password":"test"})
                return {"ok":True,"status":r.status_code,"note":''}
        except Exception as e:
            return {"ok":False,"error":str(e)}

    @staticmethod
    async def full_test() -> dict:
        ''''''
        results={}
        for name,fn in [('',UserSimulator.test_homepage),('',UserSimulator.test_product_list),('',UserSimulator.test_login)]:
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
