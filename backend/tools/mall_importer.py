"""直接写入Mall数据库 -- 去重/上架/SKU生成/评论"""
import hashlib
import time
import gc
import os
import re
import json
import pymysql
from datetime import datetime
from typing import Optional

# 默认卖家ID(系统中已有9063个商品的老卖家)
DEFAULT_SELLER_ID = "e7a5a8828bd3e591018c05838c120853"
# 默认分类ID(Digital Products,采集商品通用兜底)
DEFAULT_CATEGORY_ID = "ff80808184809ef9018480a468c30000"

DB_CONFIG = {
    "host": "127.0.0.1",
    "port": 3306,
    "user": "root",
    "password": "Root@123",
    "database": "mall",
    "charset": "utf8mb4",
}

_cat_cache = {}  # category_path -> CATEGORY_ID
_pool_conn = None  # 持久连接复用

# Amazon广告跳转链域名(URL带独特追踪参数,无法做URL去重,必须走标题去重)
_AD_TRACKING_DOMAINS = [
    "aax-us-east-retail-direct.amazon.com",
    "aax-events-cell01-cf.us-east.ono.axp.amazon-adsystem.com",
    "amazon-adsystem.com",
]


def _is_ad_tracking_url(url: str) -> bool:
    """判断是否是Amazon广告追踪跳转链"""
    if not url:
        return False
    return any(d in url for d in _AD_TRACKING_DOMAINS)


def _detect_lang(text: str) -> str:
    """检测文本语言, 返回 'en'/'zh'/'mixed'"""
    if not text:
        return "en"
    has_cn = bool(re.search(r'[一-鿿]', text))
    has_en = bool(re.search(r'[a-zA-Z]{3,}', text))
    if has_cn and has_en:
        return "mixed"
    return "zh" if has_cn else "en"


def _translate(text: str, target: str = "cn") -> str:
    """用DeepSeek翻译产品标题, 失败时返回原文"""
    if not text or not text.strip():
        return text

    lang = _detect_lang(text)
    if target == "cn" and lang == "zh":
        return text
    if target == "en" and lang == "en":
        return text

    api_key = os.getenv("DEEPSEEK_API_KEY", "")
    if not api_key:
        return text

    direction = "to Simplified Chinese" if target == "cn" else "to English"
    prompt = (
        f"Translate this e-commerce product title {direction}. "
        "Keep brand names, model numbers, sizes and specs in original form. "
        "Return ONLY the translation, no explanations.\n\n"
        f"Text: {text[:300]}"
    )

    try:
        import httpx
        r = httpx.post(
            "https://api.deepseek.com/v1/chat/completions",
            headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
            json={
                "model": "deepseek-chat",
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": 200,
                "temperature": 0.3,
            },
            timeout=20,
        )
        if r.status_code == 200:
            result = r.json().get("choices", [{}])[0].get("message", {}).get("content", "")
            if result and len(result.strip()) > 1:
                return result.strip()
    except Exception:
        pass
    return text


def _conn():
    global _pool_conn
    try:
        if _pool_conn is not None:
            _pool_conn.ping(reconnect=True)
            return _pool_conn
    except Exception:
        _pool_conn = None
    _pool_conn = pymysql.connect(**DB_CONFIG)
    return _pool_conn


def _reset_pool():
    global _pool_conn
    if _pool_conn:
        try:
            _pool_conn.close()
        except Exception:
            pass
        _pool_conn = None


def _uuid(s: str) -> str:
    return hashlib.md5(s.encode()).hexdigest()[:32]


def _now_ts() -> int:
    return int(time.time() * 1000)


def _ensure_review_table(conn=None):
    """创建评论表(如不存在)"""
    own = conn is None
    if own:
        conn = _conn()
    try:
        cur = conn.cursor()
        cur.execute("""CREATE TABLE IF NOT EXISTS T_MALL_GOODS_REVIEW (
            UUID VARCHAR(32) PRIMARY KEY,
            GOODS_ID VARCHAR(32) NOT NULL,
            REVIEWER VARCHAR(255) DEFAULT '',
            RATING DECIMAL(2,1) DEFAULT 0.0,
            TITLE VARCHAR(500) DEFAULT '',
            BODY TEXT,
            REVIEW_DATE VARCHAR(100) DEFAULT '',
            VERIFIED TINYINT DEFAULT 0,
            CREATE_TIME DATETIME,
            INDEX idx_goods_id (GOODS_ID)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4""")
        conn.commit()
    except Exception:
        pass
    finally:
        if own:
            conn.close()


def _find_category(category_path: list[str], subcat_name: str = "", conn=None) -> str:
    """尝试从品类路径匹配系统分类,失败返回默认分类"""
    if not category_path and not subcat_name:
        return DEFAULT_CATEGORY_ID

    cache_key = subcat_name or "|".join(category_path)
    if cache_key in _cat_cache:
        return _cat_cache[cache_key]

    own = conn is None
    if own:
        conn = _conn()
    try:
        cur = conn.cursor()
        # 1) 优先精确匹配子品类名
        if subcat_name:
            cur.execute(
                """SELECT c.UUID FROM T_MALL_CATEGORY c
                   JOIN T_MALL_CATEGORY_LANG cl ON c.UUID = cl.CATEGORY_ID
                   WHERE cl.NAME = %s AND c.TYPE=1 AND c.STATUS=1 AND cl.LANG='en'
                   LIMIT 1""",
                (subcat_name,)
            )
            row = cur.fetchone()
            if row:
                _cat_cache[cache_key] = row[0]
                return row[0]
        # 2) 模糊匹配品类路径
        for cat_name in reversed(category_path):
            cur.execute(
                """SELECT c.UUID FROM T_MALL_CATEGORY c
                   JOIN T_MALL_CATEGORY_LANG cl ON c.UUID = cl.CATEGORY_ID
                   WHERE cl.NAME LIKE %s AND c.TYPE=1 AND c.STATUS=1 AND cl.LANG='en'
                   LIMIT 1""",
                (f"%{cat_name}%",)
            )
            row = cur.fetchone()
            if row:
                _cat_cache[cache_key] = row[0]
                return row[0]
    except Exception:
        pass
    finally:
        if own:
            conn.close()

    _cat_cache[cache_key] = DEFAULT_CATEGORY_ID
    return DEFAULT_CATEGORY_ID


def check_duplicate(title: str, source_url: str = "", conn=None) -> Optional[str]:
    """检查重复 -- URL精确匹配或标题模糊匹配,返回已存在的GOODS_ID"""
    own = conn is None
    if own:
        conn = _conn()
    try:
        cur = conn.cursor()
        # URL去重(跳过广告追踪链,它们URL不唯一)
        if source_url and not _is_ad_tracking_url(source_url):
            cur.execute(
                "SELECT UUID FROM T_MALL_SYSTEM_GOODS WHERE LINK = %s LIMIT 1",
                (source_url,)
            )
            row = cur.fetchone()
            if row:
                return row[0]

        short_title = title[:60]
        cur.execute(
            """SELECT sg.UUID FROM T_MALL_SYSTEM_GOODS_LANG sgl
               JOIN T_MALL_SYSTEM_GOODS sg ON sgl.GOODS_ID = sg.UUID
               WHERE sgl.NAME LIKE %s LIMIT 1""",
            (f"%{short_title}%",)
        )
        row = cur.fetchone()
        if row:
            return row[0]
    except Exception:
        pass
    finally:
        if own:
            conn.close()
    return None


def import_product(product: dict, seller_id: str = DEFAULT_SELLER_ID, subcat_name: str = "", conn=None) -> dict:
    """导入单个采集商品到Mall数据库 -- 直接上架

    写入表: T_MALL_SYSTEM_GOODS, T_MALL_SYSTEM_GOODS_LANG,
            T_MALL_SELLER_GOODS, T_MALL_GOODS_SKU, T_MALL_GOODS_REVIEW
    """
    title = product.get("title", "").strip()
    if not title:
        return {"ok": False, "error": "标题为空"}

    source_url = product.get("source_url", "")
    goods_id = _uuid(source_url or title)

    # 去重
    existing = check_duplicate(title, source_url, conn=conn)
    if existing:
        return {"ok": False, "error": "商品已存在", "duplicate": True, "existing_id": existing}

    price = float(product.get("price", 0) or 0)
    org_price = float(product.get("original_price", 0) or 0)
    cos_images = product.get("cos_images", []) or []
    description = product.get("description", "") or title
    brand = product.get("brand", "")
    category_path = product.get("category_path", []) or []
    platform = product.get("platform", "")
    rating = float(product.get("rating", 0) or 0)
    rating_count = int(product.get("rating_count", 0) or 0)
    sales_count = int(product.get("sales_count", 0) or 0)
    skus = product.get("skus", []) or []
    specs = product.get("specs", []) or []
    reviews = product.get("reviews", []) or []

    category_id = _find_category(category_path, subcat_name, conn=conn)
    now_ts = _now_ts()
    now_dt = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    own = conn is None
    if own:
        conn = _conn()
    try:
        cur = conn.cursor()

        # 1. T_MALL_SYSTEM_GOODS
        img_fields = []
        img_values = []
        for i, img_url in enumerate(cos_images[:10]):
            img_fields.append(f"IMG_URL_{i+1}")
            img_values.append(img_url)

        cur.execute(f"""INSERT INTO T_MALL_SYSTEM_GOODS
            (UUID, SYSTEM_PRICE, CATEGORY_ID, IS_SHELF, CREATE_TIME, UP_TIME,
             LINK, {', '.join(img_fields)})
            VALUES (%s, %s, %s, 1, %s, %s, %s, {', '.join(['%s']*len(img_values))})
        """, [goods_id, price, category_id, now_dt, now_ts, source_url] + img_values)

        # 2. T_MALL_SYSTEM_GOODS_LANG -- 统一存英文(平台前端自动多语言适配)
        desc_text = description[:8000] if description else title

        # 标题含中文则清理为纯英文
        en_title = title
        lang = _detect_lang(title)
        if lang in ("zh", "mixed"):
            en_title = _translate(title, "en")

        lang_id_en = _uuid(f"{goods_id}_en")
        cur.execute("""INSERT INTO T_MALL_SYSTEM_GOODS_LANG
            (UUID, GOODS_ID, LANG, NAME, DES)
            VALUES (%s, %s, 'en', %s, %s)
            ON DUPLICATE KEY UPDATE NAME=%s, DES=%s""",
            (lang_id_en, goods_id, en_title, desc_text, en_title, desc_text))

        lang_id = _uuid(f"{goods_id}_cn")
        cur.execute("""INSERT INTO T_MALL_SYSTEM_GOODS_LANG
            (UUID, GOODS_ID, LANG, NAME, DES)
            VALUES (%s, %s, 'cn', %s, %s)
            ON DUPLICATE KEY UPDATE NAME=%s, DES=%s""",
            (lang_id, goods_id, en_title, desc_text, en_title, desc_text))

        # 3. T_MALL_SELLER_GOODS -- 直接上架
        sg_id = _uuid(f"{goods_id}_seller")
        rec_time = now_ts
        new_time = now_ts
        sell_price = round(price * 1.3, 2)

        cur.execute("""INSERT INTO T_MALL_SELLER_GOODS
            (UUID, SELLER_ID, CATEGORY_ID, GOODS_ID, SELLING_PRICE, SYSTEM_PRICE,
             IS_SHELF, IS_VALID, SYSTEM_REC_TIME, SYSTEM_NEW_TIME, CREATE_TIME,
             UP_TIME, FIRST_SHELF_TIME, SECONDARY_CATEGORY_ID)
            VALUES (%s, %s, %s, %s, %s, %s, 1, 1, %s, %s, %s, %s, %s, '0')""",
            (sg_id, seller_id, category_id, goods_id, sell_price, price,
             rec_time, new_time, now_dt, now_ts, now_ts))

        # 4. T_MALL_GOODS_SKU -- 多SKU(从采集的规格生成)
        sku_data_base = f"平台:{platform}"
        if brand:
            sku_data_base += f"|品牌:{brand}"
        if rating > 0:
            sku_data_base += f"|评分:{rating}"
        if rating_count > 0:
            sku_data_base += f"|{rating_count}评"
        if sales_count > 0:
            sku_data_base += f"|销量:{sales_count}"

        sku_count = 0
        if skus:
            for i, sku in enumerate(skus[:20]):
                if isinstance(sku, dict):
                    sku_price = float(sku.get("price", price) or price)
                    sku_spec = sku.get("spec", "")
                    sku_spec_name = sku.get("spec_name", "")
                    sku_img = sku.get("image", "") or (cos_images[0] if cos_images else "")
                    sku_data = f"{sku_data_base}|规格:{sku_spec_name}:{sku_spec}"[:500]
                    mu_sku_id = _uuid(f"{goods_id}_sku_{i}")
                    cur.execute("""INSERT INTO T_MALL_GOODS_SKU
                        (ID, GOOD_ID, PRICE, PIC, SP_DATA, SALE, DELETED)
                        VALUES (%s, %s, %s, %s, %s, %s, 0)
                        ON DUPLICATE KEY UPDATE PRICE=%s, SP_DATA=%s""",
                        (mu_sku_id, goods_id, sku_price, sku_img, sku_data, 999,
                         sku_price, sku_data))
                    sku_count += 1

        if sku_count == 0:
            # 默认SKU
            sku_id = _uuid(f"{goods_id}_sku_default")
            sku_pic = cos_images[0] if cos_images else ""
            cur.execute("""INSERT INTO T_MALL_GOODS_SKU
                (ID, GOOD_ID, PRICE, PIC, SP_DATA, SALE, DELETED)
                VALUES (%s, %s, %s, %s, %s, %s, 0)""",
                (sku_id, goods_id, price, sku_pic, sku_data_base[:500], 999))
            sku_count = 1

        # 5. 写入评论
        review_count = 0
        for rev in reviews:
            if isinstance(rev, dict) and rev.get("body"):
                try:
                    rev_id = _uuid(f"{goods_id}_rev_{rev.get('reviewer','')}_{rev.get('body','')[:30]}")
                    rev_rating = float(rev.get("rating", 0) or 0)
                    cur.execute("""INSERT IGNORE INTO T_MALL_GOODS_REVIEW
                        (UUID, GOODS_ID, REVIEWER, RATING, TITLE, BODY, REVIEW_DATE, VERIFIED, CREATE_TIME)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)""",
                        (rev_id, goods_id,
                         rev.get("reviewer", "")[:255],
                         rev_rating,
                         rev.get("title", "")[:500],
                         rev.get("body", "")[:5000],
                         rev.get("date", "")[:100],
                         1 if rev.get("verified") else 0,
                         now_dt))
                    review_count += 1
                except Exception:
                    continue

        conn.commit()

        result = {
            "ok": True,
            "goods_id": goods_id,
            "seller_goods_id": sg_id,
            "title": title[:50],
            "price": price,
            "category_id": category_id,
            "images_count": len(cos_images),
            "skus_count": sku_count,
            "reviews_count": review_count,
        }
        if own:
            conn.close()
        return result

    except Exception as e:
        conn.rollback()
        if own:
            conn.close()
        return {"ok": False, "error": str(e), "goods_id": goods_id}


def import_batch(products: list[dict], seller_id: str = DEFAULT_SELLER_ID, subcat_name: str = "") -> dict:
    """批量导入 -- 复用单连接,导完触发GC"""
    imported = []
    skipped = []
    failed = []

    conn = _conn()
    try:
        for p in products:
            result = import_product(p, seller_id, subcat_name, conn=conn)
            if result.get("ok"):
                imported.append(result)
            elif result.get("duplicate"):
                skipped.append(result)
            else:
                failed.append(result)
    finally:
        conn.close()
        _reset_pool()

    # 每批导完触发一次GC
    gc.collect()

    return {
        "total": len(products),
        "imported": len(imported),
        "skipped_duplicate": len(skipped),
        "failed": len(failed),
        "details": {
            "imported": imported[:10],
            "skipped": skipped[:5],
            "failed": failed[:5],
        },
    }
