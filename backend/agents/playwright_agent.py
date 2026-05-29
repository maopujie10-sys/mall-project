锘?""Playwright Agent 鈥?娴忚鍣ㄨ嚜鍔ㄥ寲
v2: 娴忚鍣ㄥ疄渚嬫睜 + 鎴浘鑷姩娓呯悊 + 骞跺彂鎺у埗"""
import os, asyncio, json, time
from datetime import datetime, timedelta
from dataclasses import dataclass
from typing import Optional

@dataclass
class BrowserTask:
    id: str
    action: str
    url: str
    status: str = "pending"
    result: dict = None
    screenshot_path: str = ""


class PlaywrightAgent:
    """娴忚鍣ㄨ嚜鍔ㄥ寲Agent 鈥?澶嶇敤娴忚鍣ㄥ疄渚?""

    BROWSER_READY = False
    _browser = None
    _context = None
    _semaphore = asyncio.Semaphore(2)  # 鏈€澶?涓苟鍙戞祻瑙堝櫒鎿嶄綔
    SCREENSHOT_DIR = os.path.join(os.getenv("APP_DATA_DIR", os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")), "screenshots")
    SCREENSHOT_MAX_AGE_HOURS = 1  # 鎴浘淇濈暀1灏忔椂

    @staticmethod
    async def _get_browser():
        """鑾峰彇鎴栧垱寤烘祻瑙堝櫒瀹炰緥锛堝鐢級"""
        if PlaywrightAgent._browser is not None:
            try:
                # 妫€鏌ユ祻瑙堝櫒鏄惁杩樻椿鐫€
                contexts = PlaywrightAgent._browser.contexts
                if len(contexts) > 0:
                    return PlaywrightAgent._browser
            except Exception:
                PlaywrightAgent._browser = None
                PlaywrightAgent._context = None

        try:
            from playwright.async_api import async_playwright
            p = await async_playwright().start()
            PlaywrightAgent._browser = await p.chromium.launch(headless=True)
            PlaywrightAgent._context = await PlaywrightAgent._browser.new_context(
                viewport={"width": 1920, "height": 1080}
            )
            PlaywrightAgent.BROWSER_READY = True
        except Exception:
            PlaywrightAgent.BROWSER_READY = False
        return PlaywrightAgent._browser

    @staticmethod
    async def _cleanup_old_screenshots():
        """鑷姩娓呯悊杩囨湡鎴浘"""
        try:
            if not os.path.exists(PlaywrightAgent.SCREENSHOT_DIR):
                return
            cutoff = datetime.now() - timedelta(hours=PlaywrightAgent.SCREENSHOT_MAX_AGE_HOURS)
            count = 0
            for f in os.listdir(PlaywrightAgent.SCREENSHOT_DIR):
                fpath = os.path.join(PlaywrightAgent.SCREENSHOT_DIR, f)
                if os.path.isfile(fpath):
                    mtime = datetime.fromtimestamp(os.path.getmtime(fpath))
                    if mtime < cutoff:
                        os.remove(fpath)
                        count += 1
            if count:
                print(f"[Playwright] 娓呯悊浜?{count} 涓繃鏈熸埅鍥?)
        except Exception:
            pass

    @staticmethod
    async def check_installed() -> bool:
        try:
            import playwright
            PlaywrightAgent.BROWSER_READY = True
            return True
        except ImportError:
            return False

    @staticmethod
    async def screenshot(url: str, full_page: bool = True) -> dict:
        """缃戦〉鎴浘锛堝鐢ㄦ祻瑙堝櫒瀹炰緥锛?""
        async with PlaywrightAgent._semaphore:
            browser = await PlaywrightAgent._get_browser()
            if not browser:
                return {"ok": False, "error": "Playwright鏈畨瑁咃紝璇疯繍琛? pip install playwright && playwright install chromium"}

            await PlaywrightAgent._cleanup_old_screenshots()
            try:
                os.makedirs(PlaywrightAgent.SCREENSHOT_DIR, exist_ok=True)
                page = await PlaywrightAgent._context.new_page()
                await page.goto(url, wait_until="networkidle", timeout=30000)
                filename = f"screenshot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
                path = os.path.join(PlaywrightAgent.SCREENSHOT_DIR, filename)
                await page.screenshot(path=path, full_page=full_page)
                await page.close()
                return {"ok": True, "path": path, "url": url, "filename": filename}
            except Exception as e:
                return {"ok": False, "error": str(e)}

    @staticmethod
    async def scrape_page(url: str, selectors: dict = None) -> dict:
        """鎶撳彇缃戦〉鍐呭锛堝鐢ㄦ祻瑙堝櫒瀹炰緥锛?""
        async with PlaywrightAgent._semaphore:
            browser = await PlaywrightAgent._get_browser()
            if not browser:
                return {"ok": False, "error": "Playwright鏈畨瑁?}

            default_selectors = {
                "title": "title", "h1": "h1", "links": "a[href]",
                "images": "img[src]", "prices": "[class*=price], [class*=Price]",
            }
            selectors = selectors or default_selectors
            try:
                page = await PlaywrightAgent._context.new_page()
                await page.goto(url, wait_until="networkidle", timeout=30000)
                result = {"url": url, "scraped_at": datetime.now().isoformat()}
                for name, sel in selectors.items():
                    try:
                        els = await page.query_selector_all(sel)
                        items = []
                        for el in els[:20]:
                            text = await el.inner_text()
                            items.append(text.strip()[:200])
                        result[name] = items[:10]
                    except Exception:
                        result[name] = []
                await page.close()
                return {"ok": True, "result": result}
            except Exception as e:
                return {"ok": False, "error": str(e)}

    @staticmethod
    async def search_and_scrape(keyword: str, site: str = "ebay") -> dict:
        """鎼滅储鍟嗗搧锛堝鐢ㄦ祻瑙堝櫒瀹炰緥锛?""
        search_urls = {
            "ebay": f"https://www.ebay.com/sch/i.html?_nkw={keyword}",
            "amazon": f"https://www.amazon.com/s?k={keyword}",
        }
        url = search_urls.get(site, search_urls["ebay"])
        result = await PlaywrightAgent.scrape_page(url, {
            "title": "title", "prices": "[class*=price], [class*=Price]",
            "links": "a[href]", "images": "img[src]",
        })
        return result

