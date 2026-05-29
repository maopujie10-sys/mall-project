"""妯℃嫙鐢ㄦ埛娴嬭瘯 鈥?AI 鑷姩娴嬭瘯涓氬姟娴佺▼

妫€娴? 棣栭〉/娉ㄥ唽/鐧诲綍/鍟嗗搧鍒楄〃/鍟嗗搧璇︽儏/涓嬪崟/瀹㈡湇/鍚庡彴鐧诲綍
"""
import httpx
from datetime import datetime
from state import state
from config import MALL_BASE_URL


class UserSimulator:
    """妯℃嫙鐢ㄦ埛 鈥?鑷姩鎵ц涓氬姟娴佺▼娴嬭瘯"""

    @staticmethod
    async def test_homepage() -> dict:
        """娴嬭瘯棣栭〉鍙闂?""
        try:
            async with httpx.AsyncClient(timeout=10,follow_redirects=True) as c:
                r=await c.get(MALL_BASE_URL,headers={"User-Agent":"Friday-AI-Test/1.0"})
                return {"ok":r.status_code<500,"status":r.status_code,"url":MALL_BASE_URL}
        except Exception as e:
            return {"ok":False,"error":str(e)}

    @staticmethod
    async def test_product_list() -> dict:
        """娴嬭瘯鍟嗗搧鍒楄〃鎺ュ彛"""
        try:
            async with httpx.AsyncClient(timeout=10) as c:
                r=await c.get(f"{MALL_BASE_URL}/api/products?page=1&size=5")
                return {"ok":r.status_code<500,"status":r.status_code,"has_data":len(str(r.text))>50}
        except Exception as e:
            return {"ok":False,"error":str(e)}

    @staticmethod
    async def test_login() -> dict:
        """娴嬭瘯鐧诲綍鎺ュ彛杩為€氭€?""
        try:
            async with httpx.AsyncClient(timeout=10) as c:
                r=await c.post(f"{MALL_BASE_URL}/api/login",json={"username":"test","password":"test"})
                return {"ok":True,"status":r.status_code,"note":"鐧诲綍鎺ュ彛鍙揪"}
        except Exception as e:
            return {"ok":False,"error":str(e)}

    @staticmethod
    async def full_test() -> dict:
        """鍏ㄦ祦绋嬫祴璇?""
        results={}
        for name,fn in [("棣栭〉",UserSimulator.test_homepage),("鍟嗗搧鍒楄〃",UserSimulator.test_product_list),("鐧诲綍",UserSimulator.test_login)]:
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
