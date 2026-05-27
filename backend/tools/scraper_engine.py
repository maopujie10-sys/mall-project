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
    """eBay 采集适配器"""
    name = "ebay"
    search_url = "https://www.ebay.com/sch/i.html?_nkw={keyword}&_ipg=60"

    async def search(self, keyword: str, max_pages: int = 3, session: httpx.AsyncClient = None) -> list[str]:
        urls = []
        close_session = session is None
        if close_session:
            session = httpx.AsyncClient(timeout=20, follow_redirects=True)

        for page in range(1, max_pages + 1):
            url = self.search_url.format(keyword=quote_plus(keyword))
            if page > 1:
                url += f"&_pgn={page}"
            try:
                r = await session.get(url, headers={"User-Agent": random_ua()})
                soup = BeautifulSoup(r.text, "html.parser")
                for link in soup.select("a.s-item__link"):
                    href = link.get("href", "")
                    if "/itm/" in href and href not in urls:
                        urls.append(href)
                        if len(urls) >= 50:
                            break
                await polite_delay()
            except Exception:
                continue
            if len(urls) >= 50:
                break

        return urls

    async def extract_product(self, url: str, session: httpx.AsyncClient = None) -> Optional[ScrapedProduct]:
        try:
            close_session = session is None
            if close_session:
                session = httpx.AsyncClient(timeout=20, follow_redirects=True)

            r = await session.get(url, headers={"User-Agent": random_ua()})
            soup = BeautifulSoup(r.text, "html.parser")

            # 标题
            title = ""
            title_el = soup.select_one("h1.it-ttl") or soup.select_one("h1.x-item-title__mainTitle span")
            if title_el:
                title = title_el.get_text(strip=True)

            # 价格
            price = 0.0
            price_el = soup.select_one(".x-price-primary span.ux-textspans") or soup.select_one("span.ux-textspans")
            if price_el:
                price_text = price_el.get_text(strip=True).replace("US $", "").replace(",", "")
                try:
                    price = float(price_text) * 7.2
                except:
                    pass

            # 原价
            org_price = 0.0
            org_el = soup.select_one(".x-price-approx__price span.ux-textspans") or soup.select_one("span.ux-textspans--STRIKETHROUGH")
            if org_el:
                org_text = org_el.get_text(strip=True).replace("US $", "").replace(",", "")
                try:
                    org_price = float(org_text) * 7.2
                except:
                    org_price = price * 1.3

            # 图片
            images = []
            for img in soup.select("img"):
                src = img.get("src", "") or img.get("data-src", "")
                if src and any(x in src.lower() for x in (".jpg", ".png", ".webp", "img.ebay", "i.ebayimg")):
                    full = urljoin(url, src)
                    if full not in images and "sprite" not in full and "icon" not in full:
                        images.append(full)

            # 规格 - eBay比较难提取，靠item specifics
            specs = []
            for row in soup.select("div.ux-layout-section__row"):
                label_el = row.select_one(".ux-labels-values__labels")
                val_el = row.select_one(".ux-labels-values__values")
                if label_el and val_el:
                    name = label_el.get_text(strip=True).rstrip(":")
                    vals = [v.strip() for v in val_el.get_text(strip=True).split(",") if v.strip()]
                    if name and vals:
                        specs.append({"name": name, "values": vals})

            # 分类
            category = []
            for cat in soup.select("nav.breadcrumbs a, li.breadcrumb a"):
                cat_text = cat.get_text(strip=True)
                if cat_text and cat_text not in ("eBay", "Home"):
                    category.append(cat_text)

            # 销量/评价
            sales = 0
            rating = 0.0
            sold_el = soup.select_one(".d-item-condition span, .vi-qtyS-hot-red")
            if sold_el:
                nums = re.findall(r'\d+', sold_el.get_text())
                if nums:
                    sales = int(nums[0])

            return ScrapedProduct(
                platform="ebay",
                source_url=url,
                title=title,
                price=price,
                original_price=org_price,
                currency="CNY",
                images=images[:20],
                specs=specs,
                category_path=category,
                brand="",
                sales_count=sales,
                rating=rating,
                crawled_at=datetime.now().isoformat()
            )
        except Exception as e:
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