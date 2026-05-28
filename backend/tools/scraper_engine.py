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
#  企业级反反爬引擎
# ═══════════════════════════════════════

# 多地区 User-Agent 池
DESKTOP_UAS = [
    # Chrome Win/Mac/Linux
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    # Edge
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36 Edg/124.0.0.0",
    # Firefox
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:125.0) Gecko/20100101 Firefox/125.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:125.0) Gecko/20100101 Firefox/125.0",
    # Safari
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 Safari/605.1.15",
]

MOBILE_UAS = [
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (Linux; Android 14; Pixel 8 Pro) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 14; SM-S24 Ultra) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Mobile Safari/537.36",
]

# Accept-Language 多语言池
ACCEPT_LANGUAGES = [
    "en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7",
    "en-US,en;q=0.9",
    "zh-CN,zh;q=0.9,en;q=0.8",
    "en-GB,en;q=0.9,zh-CN;q=0.8",
]

# Referer 链
REFERERS = [
    "https://www.google.com/",
    "https://www.bing.com/",
    "https://www.google.com/search?q={keyword}",
    "https://search.yahoo.com/search?p={keyword}",
]

# 免费代理池（备用，建议配置付费代理）
FALLBACK_PROXIES = [
    # 格式: "http://ip:port"
]

class AntiScrapEngine:
    """企业级反反爬引擎 — IP轮换/指纹随机/智能延迟/指数退避"""

    def __init__(self, domain: str, use_proxy: bool = False):
        self.domain = domain
        self.use_proxy = use_proxy
        self._request_count = 0
        self._session_requests = 0
        self._last_request_time = 0
        self._proxy_idx = 0
        self._proxies = list(FALLBACK_PROXIES)
        self._ua_idx = 0
        self._cookie_jar = {}
        self._domain_delays = {}  # 每个域名的延迟策略

    def get_headers(self, keyword: str = "") -> dict:
        """生成随机化请求头，模拟真实浏览器指纹"""
        self._ua_idx = (self._ua_idx + 1) % len(DESKTOP_UAS)
        ua = DESKTOP_UAS[self._ua_idx] if random.random() > 0.2 else random.choice(MOBILE_UAS)

        headers = {
            "User-Agent": ua,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": random.choice(ACCEPT_LANGUAGES),
            "Accept-Encoding": "gzip, deflate, br",
            "Cache-Control": "no-cache" if random.random() > 0.7 else "max-age=0",
            "Sec-Ch-Ua": '"Chromium";v="124", "Google Chrome";v="124", "Not-A.Brand";v="99"',
            "Sec-Ch-Ua-Mobile": "?0",
            "Sec-Ch-Ua-Platform": random.choice(['"Windows"', '"macOS"']),
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": random.choice(["none", "cross-site"]),
            "Sec-Fetch-User": "?1",
            "Upgrade-Insecure-Requests": "1",
            "DNT": "1",
        }

        if random.random() > 0.6 and keyword:
            headers["Referer"] = random.choice(REFERERS).format(keyword=quote_plus(keyword))

        return headers

    def get_proxy(self) -> Optional[str]:
        """轮换代理IP"""
        if not self.use_proxy or not self._proxies:
            return None
        self._proxy_idx = (self._proxy_idx + 1) % len(self._proxies)
        return self._proxies[self._proxy_idx]

    def set_proxies(self, proxies: list):
        """设置代理池"""
        self._proxies = proxies
        self._proxy_idx = 0
        self.use_proxy = True

    async def smart_delay(self, is_search: bool = False):
        """智能延迟：模拟人类浏览行为
        - 搜索页：短间隔 0.5-1.5s
        - 详情页：中长间隔 1-3s，偶尔5-8s（模拟阅读）
        """
        if is_search:
            base = random.uniform(0.5, 1.5)
        else:
            # 80% 短间隔，15% 中间隔，5% 长间隔（模拟停下来看商品）
            r = random.random()
            if r < 0.8:
                base = random.uniform(1.0, 3.0)
            elif r < 0.95:
                base = random.uniform(3.0, 6.0)
            else:
                base = random.uniform(6.0, 12.0)

        # 加入微小随机抖动
        jitter = random.uniform(-0.3, 0.3)
        delay = max(0.3, base + jitter)
        await asyncio.sleep(delay)

    async def safe_request(self, session: httpx.AsyncClient, url: str, keyword: str = "",
                           max_retries: int = 3, is_search: bool = False) -> Optional[httpx.Response]:
        """带反反爬保护的安全请求 — 自动重试+指数退避+IP轮换"""
        last_error = None

        for attempt in range(max_retries):
            try:
                headers = self.get_headers(keyword)
                proxy = self.get_proxy()

                r = await session.get(
                    url,
                    headers=headers,
                    proxy=proxy,
                    timeout=25,
                    follow_redirects=True
                )

                # 检测是否被拦截
                if r.status_code == 200:
                    text_lower = r.text[:500].lower()
                    blocked_signals = [
                        "captcha", "robot check", "are you a human",
                        "access denied", "403 forbidden", "blocked",
                        "security check", "verify you are human",
                        "please enable javascript"
                    ]
                    if any(sig in text_lower for sig in blocked_signals):
                        raise Exception(f"被反爬拦截: {self.domain}")

                    # 检测空响应
                    if len(r.text) < 200:
                        raise Exception(f"响应过短({len(r.text)}字节)，疑似拦截")

                    self._request_count += 1
                    self._session_requests += 1
                    return r

                elif r.status_code == 429:
                    # 限流 — 指数退避
                    wait = (2 ** attempt) + random.uniform(1, 5)
                    print(f"[AntiScrap] {self.domain} 429限流，等待 {wait:.1f}s")
                    await asyncio.sleep(wait)
                    continue

                elif r.status_code in (403, 503):
                    # 被封 — 换IP+长等
                    wait = (3 ** attempt) + random.uniform(5, 15)
                    print(f"[AntiScrap] {self.domain} {r.status_code}被封，换IP等待 {wait:.1f}s")
                    await asyncio.sleep(wait)
                    continue

                else:
                    last_error = Exception(f"HTTP {r.status_code}")

            except Exception as e:
                last_error = e
                if attempt < max_retries - 1:
                    wait = (2 ** attempt) + random.uniform(0.5, 2)
                    await asyncio.sleep(wait)

        if last_error:
            print(f"[AntiScrap] {self.domain} 请求失败({max_retries}次重试): {last_error}")
        return None

    async def rotate_session(self, session: httpx.AsyncClient):
        """轮换会话指纹 — 清cookie换身份"""
        session.cookies.clear()
        self._session_requests = 0
        # 随机切换UA池
        self._ua_idx = random.randint(0, len(DESKTOP_UAS) - 1)

    def stats(self) -> dict:
        return {
            "domain": self.domain,
            "requests": self._request_count,
            "session_requests": self._session_requests,
            "proxy_enabled": self.use_proxy,
            "ua_idx": self._ua_idx,
        }

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

class BaseScrapeAdapter:
    """反反爬采集基类 — 所有 HTML 爬虫适配器继承此类"""
    
    def __init__(self, platform_name: str, domain: str):
        self.platform_name = platform_name
        self.anti = AntiScrapEngine(domain)
    
    async def _safe_get(self, session: httpx.AsyncClient, url: str, keyword: str = "", 
                        is_search: bool = False, max_retries: int = 3) -> Optional[httpx.Response]:
        return await self.anti.safe_request(session, url, keyword, max_retries, is_search)
    
    async def _delay(self, is_search: bool = False):
        await self.anti.smart_delay(is_search)
    
    def _parse_price(self, text: str) -> float:
        """通用价格解析 — $19.99 / USD 19.99 / 12,99€ 等"""
        if not text:
            return 0.0
        text = text.strip().replace(",", "").replace(" ", "")
        match = re.search(r'[\d.]+', text)
        if not match:
            return 0.0
        val = float(match.group())
        if any(c in text for c in ['$', 'USD', 'US$']):
            return round(val * 7.2, 2)
        elif any(c in text for c in ['€', 'EUR']):
            return round(val * 7.8, 2)
        elif any(c in text for c in ['£', 'GBP']):
            return round(val * 9.1, 2)
        elif any(c in text for c in ['¥', 'CNY']):
            return val
        return round(val * 7.2, 2)

    def _extract_images(self, soup, base_url: str, max_images: int = 20) -> list[str]:
        """通用图片提取"""
        images = []
        for img in soup.select("img"):
            src = img.get("src", "") or img.get("data-src", "") or img.get("data-original", "")
            if not src:
                continue
            ext = os.path.splitext(urlparse(src).path)[1].lower().split("?")[0]
            if ext not in (".jpg", ".jpeg", ".png", ".webp"):
                continue
            full = urljoin(base_url, src)
            skip_kw = ["sprite", "icon", "logo", "avatar", "badge", "banner", "pixel", "1x1", "tracking"]
            if any(k in full.lower() for k in skip_kw):
                continue
            if full not in images:
                images.append(full)
            if len(images) >= max_images:
                break
        return images

class AliExpressAdapter(BaseScrapeAdapter):
    """AliExpress 速卖通 — 反反爬增强版"""
    name = "aliexpress"
    
    def __init__(self):
        super().__init__("aliexpress", "aliexpress.com")
    
    async def search(self, keyword: str, max_pages: int = 3, session: httpx.AsyncClient = None) -> list[str]:
        urls = []
        close_session = session is None
        if close_session:
            session = httpx.AsyncClient(timeout=25, follow_redirects=True)
        
        for page in range(1, min(max_pages + 1, 5)):
            url = f"https://www.aliexpress.com/wholesale?SearchText={quote_plus(keyword)}&page={page}"
            r = await self._safe_get(session, url, keyword, is_search=True)
            if not r:
                continue
            
            soup = BeautifulSoup(r.text, "html.parser")
            for link in soup.select("a[href*='/item/']"):
                href = link.get("href", "")
                if "/item/" in href:
                    full = urljoin("https://www.aliexpress.com", href.split("?")[0])
                    if full not in urls:
                        urls.append(full)
            await self._delay(is_search=True)
        
        if close_session:
            await session.aclose()
        return urls
    
    async def extract_product(self, url: str, session: httpx.AsyncClient = None) -> Optional[ScrapedProduct]:
        close_session = session is None
        if close_session:
            session = httpx.AsyncClient(timeout=25, follow_redirects=True)
        
        try:
            r = await self._safe_get(session, url, max_retries=2)
            if not r:
                return None
            
            soup = BeautifulSoup(r.text, "html.parser")
            
            title = ""
            title_el = soup.select_one("h1") or soup.select_one("[class*='title']")
            if title_el:
                title = title_el.get_text(strip=True)
            
            price = 0.0
            price_el = soup.select_one("[class*='price-current']") or soup.select_one("[class*='product-price']") or soup.select_one("[class*='Price']")
            if price_el:
                price = self._parse_price(price_el.get_text(strip=True))
            
            org_price = 0.0
            org_el = soup.select_one("[class*='price-original']") or soup.select_one("[class*='was-price']")
            if org_el:
                org_price = self._parse_price(org_el.get_text(strip=True))
            
            images = self._extract_images(soup, url)
            
            sales = 0
            sold_el = soup.select_one("[class*='sold']") or soup.select_one("[class*='order-num']")
            if sold_el:
                nums = re.findall(r'\d[\d,]*', sold_el.get_text())
                if nums:
                    sales = int(nums[0].replace(",", ""))
            
            return ScrapedProduct(
                platform="aliexpress", source_url=url, title=title,
                price=price, original_price=org_price, currency="CNY",
                images=images, sales_count=sales, crawled_at=datetime.now().isoformat()
            )
        except Exception:
            return None


class AmazonAdapter(BaseScrapeAdapter):
    """Amazon 全球站 — 反反爬增强版"""
    name = "amazon"
    
    def __init__(self):
        super().__init__("amazon", "amazon.com")
    
    async def search(self, keyword: str, max_pages: int = 3, session: httpx.AsyncClient = None) -> list[str]:
        urls = []
        close_session = session is None
        if close_session:
            session = httpx.AsyncClient(timeout=25, follow_redirects=True)
        
        for page in range(1, min(max_pages + 1, 5)):
            url = f"https://www.amazon.com/s?k={quote_plus(keyword)}&page={page}"
            r = await self._safe_get(session, url, keyword, is_search=True)
            if not r:
                continue
            
            soup = BeautifulSoup(r.text, "html.parser")
            for link in soup.select("a[href*='/dp/'], a[href*='/gp/product/']"):
                href = link.get("href", "")
                if "/dp/" in href or "/gp/product/" in href:
                    full = urljoin("https://www.amazon.com", href.split("/ref=")[0])
                    if full not in urls:
                        urls.append(full)
            await self._delay(is_search=True)
        
        if close_session:
            await session.aclose()
        return urls
    
    async def extract_product(self, url: str, session: httpx.AsyncClient = None) -> Optional[ScrapedProduct]:
        close_session = session is None
        if close_session:
            session = httpx.AsyncClient(timeout=25, follow_redirects=True)
        
        try:
            r = await self._safe_get(session, url, max_retries=2)
            if not r:
                return None
            
            soup = BeautifulSoup(r.text, "html.parser")
            
            title = ""
            title_el = soup.select_one("#productTitle")
            if title_el:
                title = title_el.get_text(strip=True)
            
            price = 0.0
            price_el = (soup.select_one(".a-price .a-offscreen") or 
                       soup.select_one("#priceblock_ourprice") or
                       soup.select_one(".a-price-whole"))
            if price_el:
                price = self._parse_price(price_el.get_text(strip=True))
            
            org_price = 0.0
            org_el = soup.select_one(".basisPrice .a-offscreen") or soup.select_one("#listPrice")
            if org_el:
                org_price = self._parse_price(org_el.get_text(strip=True))
            
            images = self._extract_images(soup, url)
            # Amazon 特色: data-old-hires
            for img in soup.select("img[data-old-hires]"):
                hires = img.get("data-old-hires", "")
                if hires and hires not in images:
                    images.insert(0, hires)
            
            brand = ""
            brand_el = soup.select_one("#bylineInfo")
            if brand_el:
                brand = brand_el.get_text(strip=True).replace("Brand:", "").replace("品牌:", "").strip()
            
            rating = 0.0
            rating_el = soup.select_one("#acrPopover .a-icon-alt") or soup.select_one("[data-hook='rating-out-of-text']")
            if rating_el:
                nums = re.findall(r'[\d.]+', rating_el.get_text(strip=True))
                if nums:
                    rating = float(nums[0])
            
            return ScrapedProduct(
                platform="amazon", source_url=url, title=title, brand=brand,
                price=price, original_price=org_price, currency="CNY",
                images=images, rating=rating, crawled_at=datetime.now().isoformat()
            )
        except Exception:
            return None


class WishAdapter(BaseScrapeAdapter):
    """Wish 全球站 — 反反爬增强版"""
    name = "wish"
    
    def __init__(self):
        super().__init__("wish", "wish.com")
    
    async def search(self, keyword: str, max_pages: int = 3, session: httpx.AsyncClient = None) -> list[str]:
        urls = []
        close_session = session is None
        if close_session:
            session = httpx.AsyncClient(timeout=25, follow_redirects=True)
        
        for page in range(1, min(max_pages + 1, 5)):
            url = f"https://www.wish.com/search/{quote_plus(keyword)}?page={page}"
            r = await self._safe_get(session, url, keyword, is_search=True)
            if not r:
                continue
            
            soup = BeautifulSoup(r.text, "html.parser")
            for link in soup.select("a[href*='/product/'], a[href*='/c/']"):
                href = link.get("href", "")
                if "/product/" in href or "/c/" in href:
                    full = urljoin("https://www.wish.com", href)
                    if full not in urls:
                        urls.append(full)
            await self._delay(is_search=True)
        
        if close_session:
            await session.aclose()
        return urls
    
    async def extract_product(self, url: str, session: httpx.AsyncClient = None) -> Optional[ScrapedProduct]:
        close_session = session is None
        if close_session:
            session = httpx.AsyncClient(timeout=25, follow_redirects=True)
        
        try:
            r = await self._safe_get(session, url, max_retries=2)
            if not r:
                return None
            
            soup = BeautifulSoup(r.text, "html.parser")
            
            title = ""
            title_el = soup.select_one("[class*='ProductName']") or soup.select_one("h1")
            if title_el:
                title = title_el.get_text(strip=True)
            
            price = 0.0
            price_el = soup.select_one("[class*='Price']") or soup.select_one("[class*='price']")
            if price_el:
                price = self._parse_price(price_el.get_text(strip=True))
            
            images = self._extract_images(soup, url)
            
            return ScrapedProduct(
                platform="wish", source_url=url, title=title,
                price=price, currency="CNY", images=images,
                crawled_at=datetime.now().isoformat()
            )
        except Exception:
            return None


class ShopeeAdapter(BaseScrapeAdapter):
    """Shopee 虾皮 — 反反爬增强版"""
    name = "shopee"
    
    def __init__(self):
        super().__init__("shopee", "shopee.com")
    
    async def search(self, keyword: str, max_pages: int = 3, session: httpx.AsyncClient = None) -> list[str]:
        urls = []
        close_session = session is None
        if close_session:
            session = httpx.AsyncClient(timeout=25, follow_redirects=True)
        
        for page in range(0, min(max_pages, 5)):
            url = f"https://shopee.com/api/v4/search/search_items?by=relevancy&keyword={quote_plus(keyword)}&limit=50&newest={page * 50}"
            r = await self._safe_get(session, url, keyword, is_search=True)
            if not r:
                continue
            
            try:
                data = r.json()
                items = data.get("items", [])
                for item in items:
                    item_basic = item.get("item_basic", {})
                    shopid = item_basic.get("shopid", "")
                    itemid = item_basic.get("itemid", "")
                    if shopid and itemid:
                        product_url = f"https://shopee.com/product/{shopid}/{itemid}"
                        if product_url not in urls:
                            urls.append(product_url)
            except:
                pass
            await self._delay(is_search=True)
        
        if close_session:
            await session.aclose()
        return urls
    
    async def extract_product(self, url: str, session: httpx.AsyncClient = None) -> Optional[ScrapedProduct]:
        close_session = session is None
        if close_session:
            session = httpx.AsyncClient(timeout=25, follow_redirects=True)
        
        try:
            # Shopee API 获取商品详情
            match = re.search(r'/product/(\d+)/(\d+)', url)
            if match:
                shopid, itemid = match.group(1), match.group(2)
                api_url = f"https://shopee.com/api/v4/item/get?itemid={itemid}&shopid={shopid}"
                r = await self._safe_get(session, api_url, max_retries=2)
                if r:
                    data = r.json().get("data", {})
                    title = data.get("name", "")
                    price_raw = data.get("price", 0)
                    price = round(float(price_raw) / 100000 * 0.2, 2) if price_raw else 0.0  # Shopee价格单位
                    images = []
                    for img in data.get("images", []):
                        img_url = f"https://cf.shopee.com/file/{img}"
                        images.append(img_url)
                    
                    sales = data.get("historical_sold", 0) or data.get("sold", 0)
                    
                    return ScrapedProduct(
                        platform="shopee", source_url=url, title=title,
                        price=price, currency="CNY", images=images[:20],
                        sales_count=sales, crawled_at=datetime.now().isoformat()
                    )
            
            # 降级：HTML爬取
            r = await self._safe_get(session, url, max_retries=2)
            if not r:
                return None
            soup = BeautifulSoup(r.text, "html.parser")
            title_el = soup.select_one("h1") or soup.select_one("[class*='title']")
            title = title_el.get_text(strip=True) if title_el else ""
            images = self._extract_images(soup, url)
            
            return ScrapedProduct(
                platform="shopee", source_url=url, title=title,
                currency="CNY", images=images, crawled_at=datetime.now().isoformat()
            )
        except Exception:
            return None


class LazadaAdapter(BaseScrapeAdapter):
    """Lazada 来赞达 — 反反爬增强版"""
    name = "lazada"
    
    def __init__(self):
        super().__init__("lazada", "lazada.com")
    
    async def search(self, keyword: str, max_pages: int = 3, session: httpx.AsyncClient = None) -> list[str]:
        urls = []
        close_session = session is None
        if close_session:
            session = httpx.AsyncClient(timeout=25, follow_redirects=True)
        
        for page in range(1, min(max_pages + 1, 5)):
            url = f"https://www.lazada.com/catalog/?q={quote_plus(keyword)}&page={page}"
            r = await self._safe_get(session, url, keyword, is_search=True)
            if not r:
                continue
            
            soup = BeautifulSoup(r.text, "html.parser")
            for link in soup.select("a[href*='-i']"):
                href = link.get("href", "")
                if "-i" in href and "lazada" in href:
                    full = urljoin("https://www.lazada.com", href)
                    if full not in urls:
                        urls.append(full)
            await self._delay(is_search=True)
        
        if close_session:
            await session.aclose()
        return urls
    
    async def extract_product(self, url: str, session: httpx.AsyncClient = None) -> Optional[ScrapedProduct]:
        close_session = session is None
        if close_session:
            session = httpx.AsyncClient(timeout=25, follow_redirects=True)
        
        try:
            r = await self._safe_get(session, url, max_retries=2)
            if not r:
                return None
            
            soup = BeautifulSoup(r.text, "html.parser")
            
            title = ""
            title_el = soup.select_one("[class*='pdp-product-title']") or soup.select_one("h1")
            if title_el:
                title = title_el.get_text(strip=True)
            
            price = 0.0
            price_el = soup.select_one("[class*='pdp-price']") or soup.select_one("[class*='price']")
            if price_el:
                price = self._parse_price(price_el.get_text(strip=True))
            
            images = self._extract_images(soup, url)
            
            brand = ""
            brand_el = soup.select_one("[class*='pdp-brand']") or soup.select_one("[class*='brand']")
            if brand_el:
                brand = brand_el.get_text(strip=True)
            
            return ScrapedProduct(
                platform="lazada", source_url=url, title=title, brand=brand,
                price=price, currency="CNY", images=images,
                crawled_at=datetime.now().isoformat()
            )
        except Exception:
            return None
# ═══════════════════════════════════════
#  采集引擎


class TikTokShopAdapter(BaseScrapeAdapter):
    """TikTok Shop 海外抖音电商 — 反反爬增强版"""
    name = "tiktok"

    def __init__(self):
        super().__init__("tiktok", "tiktok.com")

    async def search(self, keyword: str, max_pages: int = 3, session: httpx.AsyncClient = None) -> list[str]:
        urls = []
        close_session = session is None
        if close_session:
            session = httpx.AsyncClient(timeout=25, follow_redirects=True)

        for page in range(1, min(max_pages + 1, 5)):
            url = f"https://www.tiktok.com/search?q={quote_plus(keyword)}"
            r = await self._safe_get(session, url, keyword, is_search=True)
            if not r:
                continue

            soup = BeautifulSoup(r.text, "html.parser")
            for link in soup.select("a[href*='/product/'], a[href*='tiktok.com/@']"):
                href = link.get("href", "")
                full = urljoin("https://www.tiktok.com", href)
                if full not in urls and "tiktok.com" in full:
                    urls.append(full)

            await self._delay(is_search=True)

        if close_session:
            await session.aclose()
        return urls

    async def extract_product(self, url: str, session: httpx.AsyncClient = None) -> Optional[ScrapedProduct]:
        close_session = session is None
        if close_session:
            session = httpx.AsyncClient(timeout=25, follow_redirects=True)

        try:
            r = await self._safe_get(session, url, max_retries=2)
            if not r:
                return None

            soup = BeautifulSoup(r.text, "html.parser")

            title = ""
            title_el = soup.select_one("h1") or soup.select_one("[class*='title']")
            if title_el:
                title = title_el.get_text(strip=True)

            price = 0.0
            price_el = soup.select_one("[class*='price']")
            if price_el:
                price = self._parse_price(price_el.get_text(strip=True))

            images = self._extract_images(soup, url)

            sales = 0
            sold_el = soup.select_one("[class*='sold']")
            if sold_el:
                nums = re.findall(r'[\d,]+', sold_el.get_text())
                if nums:
                    sales = int(nums[0].replace(",", ""))

            return ScrapedProduct(
                platform="tiktok", source_url=url, title=title,
                price=price, currency="CNY", images=images,
                sales_count=sales, crawled_at=datetime.now().isoformat()
            )
        except Exception:
            return None


# ═══════════════════════════════════════
#  采集引擎
# ═══════════════════════════════════════

ADAPTERS = {
    "ebay": eBayAdapter(),           # 官方API
    "aliexpress": AliExpressAdapter(), # 反反爬
    "amazon": AmazonAdapter(),        # 反反爬
    "wish": WishAdapter(),            # 反反爬
    "shopee": ShopeeAdapter(),        # 反反爬(API优先)
    "lazada": LazadaAdapter(),        # 反反爬
    "tiktok": TikTokShopAdapter(),    # 反反爬
}

PRIORITY_SOURCES = [
    "ebay",      # 官方API — 稳定首选
    "shopee",    # API+爬虫双模 — 东南亚货源王
    "aliexpress", # 反反爬 — 中国直发全球
    "amazon",    # 反反爬 — 全球最大
    "wish",      # 反反爬 — 低价爆款
    "lazada",    # 反反爬 — 东南亚老二
    "tiktok",   # 反反爬 — 海外抖音电商新贵
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