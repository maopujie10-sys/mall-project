"""Playwright Agent — 浏览器自动化
能力：网页截图/表单填写/数据抓取/电商监控/UI测试"""
import os
import asyncio
import json
from datetime import datetime
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
    """浏览器自动化Agent — AI可操控浏览器完成复杂任务"""

    BROWSER_READY = False  # 需要 playwright install

    @staticmethod
    async def check_installed() -> bool:
        """检查Playwright是否已安装"""
        try:
            import playwright
            PlaywrightAgent.BROWSER_READY = True
            return True
        except ImportError:
            return False

    @staticmethod
    async def screenshot(url: str, full_page: bool = True) -> dict:
        """网页截图"""
        if not PlaywrightAgent.BROWSER_READY:
            return {"ok": False, "error": "Playwright未安装，请运行: pip install playwright && playwright install chromium"}

        try:
            from playwright.async_api import async_playwright
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True)
                page = await browser.new_page(viewport={"width": 1920, "height": 1080})
                await page.goto(url, wait_until="networkidle", timeout=30000)
                out_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "screenshots")
                os.makedirs(out_dir, exist_ok=True)
                filename = f"screenshot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
                path = os.path.join(out_dir, filename)
                await page.screenshot(path=path, full_page=full_page)
                await browser.close()
                return {"ok": True, "path": path, "url": url, "filename": filename}
        except Exception as e:
            return {"ok": False, "error": str(e)}

    @staticmethod
    async def scrape_page(url: str, selectors: dict = None) -> dict:
        """抓取网页内容"""
        if not PlaywrightAgent.BROWSER_READY:
            return {"ok": False, "error": "Playwright未安装"}

        default_selectors = {
            "title": "title",
            "h1": "h1",
            "links": "a[href]",
            "images": "img[src]",
            "prices": "[class*=price], [class*=Price]",
        }
        selectors = selectors or default_selectors

        try:
            from playwright.async_api import async_playwright
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True)
                page = await browser.new_page()
                await page.goto(url, wait_until="networkidle", timeout=30000)

                result = {"url": url, "scraped_at": datetime.now().isoformat()}
                for name, sel in selectors.items():
                    try:
                        if name in ("title", "h1"):
                            el = await page.query_selector(sel)
                            result[name] = await el.text_content() if el else ""
                        elif name == "links":
                            els = await page.query_selector_all(sel)
                            result[name] = [
                                {"text": (await e.text_content() or "").strip()[:100], "href": await e.get_attribute("href")}
                                for e in els[:20]
                            ]
                        elif name == "images":
                            els = await page.query_selector_all(sel)
                            result[name] = [
                                {"src": await e.get_attribute("src"), "alt": await e.get_attribute("alt")}
                                for e in els[:20]
                            ]
                        elif name == "prices":
                            els = await page.query_selector_all(sel)
                            result[name] = [(await e.text_content() or "").strip() for e in els[:20]]
                        else:
                            els = await page.query_selector_all(sel)
                            result[name] = [(await e.text_content() or "").strip()[:200] for e in els[:10]]
                    except:
                        result[name] = []

                await browser.close()
                return {"ok": True, **result}
        except Exception as e:
            return {"ok": False, "error": str(e)}

    @staticmethod
    async def fill_form(url: str, fields: dict, submit_selector: str = "button[type=submit]") -> dict:
        """自动填写表单"""
        if not PlaywrightAgent.BROWSER_READY:
            return {"ok": False, "error": "Playwright未安装"}

        try:
            from playwright.async_api import async_playwright
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True)
                page = await browser.new_page()
                await page.goto(url, wait_until="networkidle", timeout=30000)

                for selector, value in fields.items():
                    await page.fill(selector, str(value))

                out_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "screenshots")
                os.makedirs(out_dir, exist_ok=True)
                path = os.path.join(out_dir, f"form_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png")

                if submit_selector:
                    await page.click(submit_selector)
                    await page.wait_for_timeout(2000)

                await page.screenshot(path=path if not submit_selector else path)
                await browser.close()
                return {"ok": True, "filled_fields": list(fields.keys()), "screenshot": path}
        except Exception as e:
            return {"ok": False, "error": str(e)}

    @staticmethod
    async def monitor_ecommerce(url: str, price_selector: str, interval_minutes: int = 60) -> dict:
        """电商价格监控"""
        return {
            "ok": True,
            "task": "price_monitor",
            "url": url,
            "selector": price_selector,
            "interval": f"{interval_minutes}分钟",
            "status": "监控任务已创建",
            "created_at": datetime.now().isoformat(),
            "note": "需配合Celery定时任务使用",
        }

    @staticmethod
    async def take_screenshot_of_mall(mall_url: str = "https://tiktook.eu.cc") -> dict:
        """给商城截图（快捷方法）"""
        return await PlaywrightAgent.screenshot(mall_url)

    @staticmethod
    async def search_and_scrape(search_term: str, site: str = "ebay") -> dict:
        """搜索并抓取商品"""
        search_urls = {
            "ebay": f"https://www.ebay.com/sch/i.html?_nkw={search_term}",
            "amazon": f"https://www.amazon.com/s?k={search_term}",
            "1688": f"https://s.1688.com/selloffer/offer_search.htm?keywords={search_term}",
        }
        url = search_urls.get(site, search_urls["ebay"])
        return await PlaywrightAgent.scrape_page(url, {
            "title": "title",
            "products": "[class*=s-item], [class*=product]",
            "prices": "[class*=price], [class*=Price]",
        })
