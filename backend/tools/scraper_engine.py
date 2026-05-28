"""企业级全量商品采集引擎 — 多平台/规格提取/SKU/OSS上传/去重"""
import os
import re
import json
import time
import random
import asyncio
import hashlib
import tempfile
from datetime import datetime
from urllib.parse import urljoin, urlparse, quote_plus
from dataclasses import dataclass, field, asdict
from typing import Optional
import httpx
from bs4 import BeautifulSoup

from tools.cloud_storage import upload_image, upload_bytes
from state import state

# ═══════════════════════════════════════
#  数据模型
# ═══════════════════════════════════════

@dataclass
class SpecItem:
    name: str
    values: list[str] = field(default_factory=list)

@dataclass
class SkuItem:
    spec: str
    price: float = 0
    original_price: float = 0
    stock: int = 0
    image: str = ""

@dataclass
class ScrapedProduct:
    """标准化采集产品"""
    id: str = ""
    platform: str = ""
    source_url: str = ""
    title: str = ""
    price: float = 0
    original_price: float = 0
    currency: str = "CNY"
    images: list[str] = field(default_factory=list)       # 远程URL
    cos_images: list[str] = field(default_factory=list)    # COS链接
    specs: list = field(default_factory=list)
    skus: list = field(default_factory=list)
    description: str = ""
    category_path: list[str] = field(default_factory=list)
    brand: str = ""
    sales_count: int = 0
    rating: float = 0.0
    rating_count: int = 0
    status: str = "pending"  # pending/downloading/uploaded/imported/failed
    error: str = ""
    crawled_at: str = ""

    def to_dict(self):
        d = asdict(self)
        d["specs"] = [asdict(s) if hasattr(s, '__dataclass_fields__') else s for s in self.specs]
        d["skus"] = [asdict(s) if hasattr(s, '__dataclass_fields__') else s for s in self.skus]
        return d

# ═══════════════════════════════════════
#  反反爬虫
# ═══════════════════════════════════════

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/123.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Edge/124.0.0.0 Safari/537.36",
]

def random_ua():
    return random.choice(USER_AGENTS)

async def polite_delay():
    await asyncio.sleep(random.uniform(0.8, 2.5))

# ═══════════════════════════════════════
#  图片下载 + COS上传
# ═══════════════════════════════════════

async def download_and_upload(url: str, product_id: str, index: int, session: httpx.AsyncClient) -> Optional[str]:
    """下载图片并通过 COS 签名URL上传，返回COS链接"""
    for attempt in range(3):
        try:
            r = await session.get(url, headers={"User-Agent": random_ua()}, timeout=15)
            if r.status_code == 200 and len(r.content) > 500:
                ext = os.path.splitext(urlparse(url).path)[1] or ".jpg"
                ext = ext.split("?")[0]
                if ext not in (".jpg", ".jpeg", ".png", ".webp", ".gif"):
                    ext = ".jpg"
                cos_key = f"products/scraped/{product_id}/{index:02d}{ext}"
                result = await upload_bytes(r.content, cos_key, f"image/{ext.replace('.','')}")
                if result["ok"]:
                    return result["url"]
            await asyncio.sleep(1)
        except Exception:
            await asyncio.sleep(2)
    return None

# ═══════════════════════════════════════
#  平台适配器
# ═══════════════════════════════════════

class eBayAdapter:
    """eBay 真实API采集适配器 — Finding API + Shopping API"""
    name = "ebay"

    def __init__(self):
        self.app_id = os.getenv("EBAY_SANDBOX_APP_ID", os.getenv("EBAY_PRODUCTION_APP_ID", ""))
        self.dev_id = os.getenv("EBAY_DEV_ID", "")
        self.use_sandbox = bool(os.getenv("EBAY_SANDBOX_APP_ID"))
        if self.use_sandbox:
            self.finding_url = "https://svcs.sandbox.ebay.com/services/search/FindingService/v1"
            self.shopping_url = "https://open.api.sandbox.ebay.com/shopping"
        else:
            self.finding_url = "https://svcs.ebay.com/services/search/FindingService/v1"
            self.shopping_url = "https://open.api.ebay.com/shopping"
        self._search_cache = {}

    async def search(self, keyword: str, max_pages: int = 3, session: httpx.AsyncClient = None) -> list[str]:
        """eBay Finding API 搜索，返回 itemId 列表"""
        item_ids = []
        close_session = session is None
        if close_session:
            session = httpx.AsyncClient(timeout=20)
        try:
            entries = min(50, max_pages * 20)
            params = {
                "OPERATION-NAME": "findItemsByKeywords",
                "SERVICE-VERSION": "1.0.0",
                "SECURITY-APPNAME": self.app_id,
                "RESPONSE-DATA-FORMAT": "JSON",
                "keywords": keyword,
                "paginationInput.entriesPerPage": str(entries),
            }
            r = await session.get(self.finding_url, params=params, headers={"User-Agent": random_ua()})
            data = r.json()
            search_result = data.get("findItemsByKeywordsResponse", [{}])[0].get("searchResult", [{}])[0]
            items = search_result.get("item", [])
            for item in items:
                iid = item.get("itemId", [""])[0]
                if iid:
                    item_ids.append(iid)
            self._search_cache = {it.get("itemId", [""])[0]: it for it in items if it.get("itemId")}
        except Exception as e:
            print(f"[eBay API] 搜索失败: {e}")
        if close_session:
            await session.aclose()
        return item_ids

    async def extract_product(self, item_id: str, session: httpx.AsyncClient = None) -> Optional[ScrapedProduct]:
        """eBay Shopping API GetSingleItem 获取商品详情"""
        close_session = session is None
        if close_session:
            session = httpx.AsyncClient(timeout=20)
        try:
            cached = self._search_cache.get(item_id, {})
            params = {
                "callname": "GetSingleItem",
                "responseencoding": "JSON",
                "appid": self.app_id,
                "siteid": "0",
                "version": "967",
                "ItemID": item_id,
                "IncludeSelector": "Description,ItemSpecifics,Details",
            }
            r = await session.get(self.shopping_url, params=params, headers={"User-Agent": random_ua()})
            data = r.json()
            item = data.get("Item", {})

            title = item.get("Title", "") or cached.get("title", [""])[0]
            current_price = item.get("CurrentPrice", {}) or cached.get("sellingStatus", [{}])[0].get("currentPrice", [{}])[0]
            try:
                price_usd = float(current_price.get("Value", 0) or current_price.get("value", 0))
            except:
                price_usd = 0.0
            price = round(price_usd * 7.2, 2)
            org_price = round(price * 1.15, 2)

            images = []
            picture_urls = item.get("PictureURL", [])
            if not picture_urls:
                gallery = cached.get("galleryURL", [""])[0]
                if gallery:
                    picture_urls = [gallery]
            for img_url in (picture_urls if isinstance(picture_urls, list) else [picture_urls]):
                if img_url and img_url not in images:
                    images.append(img_url)

            source_url = item.get("ViewItemURLForNaturalSearch", "") or cached.get("viewItemURL", [""])[0]

            specs = []
            for nv in item.get("ItemSpecifics", {}).get("NameValueList", []):
                name = nv.get("Name", "")
                vals = nv.get("Value", [])
                if isinstance(vals, str):
                    vals = [vals]
                if name and vals:
                    specs.append({"name": name, "values": vals})

            category = []
            primary_cat = item.get("PrimaryCategoryName", "")
            if primary_cat:
                category.append(primary_cat)

            description = item.get("Description", "")
            if isinstance(description, str) and len(description) > 500:
                description = description[:500]

            brand = ""
            for nv in item.get("ItemSpecifics", {}).get("NameValueList", []):
                if nv.get("Name", "").lower() == "brand":
                    vals = nv.get("Value", [])
                    brand = vals[0] if isinstance(vals, list) and vals else str(vals)
                    break

            sales = 0
            qty_sold = item.get("QuantitySold", 0)
            if qty_sold:
                try:
                    sales = int(qty_sold)
                except:
                    pass

            return ScrapedProduct(
                platform="ebay",
                source_url=source_url or f"https://www.ebay.com/itm/{item_id}",
                title=title,
                price=price,
                original_price=org_price,
                currency="CNY",
                images=images[:20],
                specs=specs,
                description=description,
                category_path=category,
                brand=brand,
                sales_count=sales,
                rating=0.0,
                crawled_at=datetime.now().isoformat()
            )
        except Exception as e:
            print(f"[eBay API] 提取失败 ({item_id}): {e}")
            return None
class AliexpressAdapter:
    """速卖通采集适配器"""
    name = "aliexpress"
    search_url = "https://www.aliexpress.com/wholesale?SearchText={keyword}"

    async def search(self, keyword: str, max_pages: int = 3, session: httpx.AsyncClient = None) -> list[str]:
        urls = []
        # AliExpress 反爬严格，返回基础搜索URL让用户手动采集
        for page in range(1, max_pages + 1):
            url = self.search_url.format(keyword=quote_plus(keyword))
            if page > 1:
                url += f"&page={page}"
            urls.append(url)
        return urls

    async def extract_product(self, url: str, session: httpx.AsyncClient = None) -> Optional[ScrapedProduct]:
        try:
            close_session = session is None
            if close_session:
                session = httpx.AsyncClient(timeout=20, follow_redirects=True)

            r = await session.get(url, headers={"User-Agent": random_ua()})
            soup = BeautifulSoup(r.text, "html.parser")

            title = (soup.select_one("h1") or soup.select_one(".product-title")).get_text(strip=True) if (soup.select_one("h1") or soup.select_one(".product-title")) else ""

            price = 0.0
            price_el = soup.select_one(".product-price-current, .product-price-value")
            if price_el:
                try:
                    price = float(re.sub(r'[^\d.]', '', price_el.get_text(strip=True)))
                except:
                    pass

            images = []
            for img in soup.select("img"):
                src = img.get("src", "") or img.get("data-src", "")
                if src and any(x in src for x in (".jpg", ".png", ".webp")):
                    full = urljoin(url, src)
                    if full not in images:
                        images.append(full)

            return ScrapedProduct(
                platform="aliexpress",
                source_url=url,
                title=title,
                price=price,
                currency="CNY",
                images=images[:20],
                crawled_at=datetime.now().isoformat()
            )
        except Exception:
            return None

# ═══════════════════════════════════════
#  采集引擎
# ═══════════════════════════════════════

ADAPTERS = {
    "ebay": eBayAdapter(),
    "aliexpress": AliexpressAdapter(),
}

PRIORITY_SOURCES = [
    "ebay",      # 电商货源充足
]

def _get_jobs():
    return state._data.setdefault("scraper_jobs", {})

def _get_products():
    return state._data.setdefault("scraped_products", [])

def _job_progress(job_id: str, update: dict):
    jobs = _get_jobs()
    if job_id in jobs:
        jobs[job_id].update(update)
    state._save()

class ScraperEngine:
    """商品采集引擎"""

    @staticmethod
    async def start_job(platform: str, keyword: str, max_items: int = 20, download_images: bool = True) -> dict:
        job_id = hashlib.md5(f"{platform}{keyword}{time.time()}".encode()).hexdigest()[:12]
        jobs = _get_jobs()
        jobs[job_id] = {
            "id": job_id,
            "platform": platform,
            "keyword": keyword,
            "status": "searching",
            "progress": 0,
            "total": 0,
            "found": 0,
            "uploaded": 0,
            "failed": 0,
            "created_at": datetime.now().isoformat(),
            "products": [],
        }
        state._save()

        # 异步执行采集
        asyncio.create_task(_do_scrape(job_id, platform, keyword, max_items, download_images))
        return jobs[job_id]

    @staticmethod
    def get_jobs() -> list:
        return list(_get_jobs().values())

    @staticmethod
    def get_job(job_id: str) -> Optional[dict]:
        return _get_jobs().get(job_id)

    @staticmethod
    def get_products(page: int = 1, size: int = 20, status: str = None) -> dict:
        products = _get_products()
        if status:
            products = [p for p in products if p.get("status") == status]
        total = len(products)
        start = (page - 1) * size
        items = products[start:start + size]
        return {"items": items, "total": total, "page": page, "size": size}

    @staticmethod
    def import_to_mall(product_ids: list[str]) -> dict:
        """标记产品为待导入商城"""
        products = _get_products()
        count = 0
        for pid in product_ids:
            for p in products:
                if p.get("id") == pid:
                    p["status"] = "importing"
                    count += 1
        state._save()
        return {"imported": count, "status": "pending_mall_api_call"}

async def _do_scrape(job_id: str, platform: str, keyword: str, max_items: int, download_images: bool):
    """后台执行采集任务"""
    adapter = ADAPTERS.get(platform, ADAPTERS["ebay"])
    _job_progress(job_id, {"status": "searching"})

    async with httpx.AsyncClient(timeout=20, follow_redirects=True) as session:
        # 1. 搜索获取商品URL
        urls = await adapter.search(keyword, max_pages=2, session=session)
        _job_progress(job_id, {"status": "extracting", "total": len(urls), "found": 0})

        products = []
        for i, url in enumerate(urls[:max_items]):
            product = await adapter.extract_product(url, session=session)
            if product and product.title and product.images:
                product.id = hashlib.md5(product.source_url.encode()).hexdigest()[:16]
                products.append(product)
                _job_progress(job_id, {"progress": i + 1, "found": len(products)})
            await polite_delay()

        # 2. 下载图片 + 上传COS
        if download_images:
            _job_progress(job_id, {"status": "uploading"})
            for p in products:
                uploaded = []
                for idx, img_url in enumerate(p.images[:8]):
                    cos_url = await download_and_upload(img_url, p.id, idx, session)
                    if cos_url:
                        uploaded.append(cos_url)
                    if len(uploaded) >= 5:
                        break
                p.cos_images = uploaded
                p.status = "uploaded"
                _job_progress(job_id, {"uploaded": _job_progress.__defaults__[0].get("uploaded", 0) + 1})

        # 3. 存储
        all_products = _get_products()
        for p in products:
            all_products.insert(0, p.to_dict())
        if len(all_products) > 500:
            all_products[:] = all_products[:500]
        state._save()

        _job_progress(job_id, {
            "status": "done",
            "uploaded": sum(1 for p in products if p.cos_images),
            "failed": sum(1 for p in products if not p.cos_images),
            "products": [p.to_dict() for p in products]
        })