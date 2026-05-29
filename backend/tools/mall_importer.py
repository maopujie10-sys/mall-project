"""直接写入Mall数据库 — 去重/上架/SKU生成"""
import hashlib
import time
import pymysql
from datetime import datetime
from typing import Optional

# 默认卖家ID（系统中已有9063个商品的老卖家）
DEFAULT_SELLER_ID = "e7a5a8828bd3e591018c05838c120853"
# 默认分类ID（Digital Products，采集商品通用兜底）
DEFAULT_CATEGORY_ID = "ff80808184809ef9018480a468c30000"

DB_CONFIG = {
    "host": "127.0.0.1",
    "port": 3306,
    "user": "root",
    "password": "Root@123",
    "database": "mall",
    "charset": "utf8mb4",
}

_cat_cache = {}  # category_path → CATEGORY_ID


def _conn():
    return pymysql.connect(**DB_CONFIG)


def _uuid(s: str) -> str:
    return hashlib.md5(s.encode()).hexdigest()[:32]


def _now_ts() -> int:
    return int(time.time() * 1000)


def _find_category(category_path: list[str]) -> str:
    """尝试从品类路径匹配系统分类，失败返回默认分类"""
    if not category_path:
        return DEFAULT_CATEGORY_ID

    cache_key = "|".join(category_path)
    if cache_key in _cat_cache:
        return _cat_cache[cache_key]

    conn = _conn()
    try:
        cur = conn.cursor()
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
        conn.close()

    _cat_cache[cache_key] = DEFAULT_CATEGORY_ID
    return DEFAULT_CATEGORY_ID


def check_duplicate(title: str, source_url: str = "") -> Optional[str]:
    """检查重复 — 按标题模糊匹配或URL精确匹配，返回已存在的GOODS_ID"""
    conn = _conn()
    try:
        cur = conn.cursor()
        # 按URL去重（从LINK字段）
        if source_url:
            cur.execute(
                "SELECT UUID FROM T_MALL_SYSTEM_GOODS WHERE LINK = %s LIMIT 1",
                (source_url,)
            )
            row = cur.fetchone()
            if row:
                return row[0]

        # 按标题模糊匹配
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
        conn.close()
    return None


def import_product(product: dict, seller_id: str = DEFAULT_SELLER_ID) -> dict:
    """导入单个采集商品到Mall数据库 — 直接上架

    写入表: T_MALL_SYSTEM_GOODS, T_MALL_SYSTEM_GOODS_LANG,
            T_MALL_SELLER_GOODS, T_MALL_GOODS_SKU
    """
    title = product.get("title", "").strip()
    if not title:
        return {"ok": False, "error": "标题为空"}

    source_url = product.get("source_url", "")
    goods_id = _uuid(source_url or title)

    # 去重
    existing = check_duplicate(title, source_url)
    if existing:
        return {"ok": False, "error": "商品已存在", "duplicate": True, "existing_id": existing}

    price = float(product.get("price", 0) or 0)
    cos_images = product.get("cos_images", []) or []
    description = product.get("description", "") or title
    brand = product.get("brand", "")
    category_path = product.get("category_path", []) or []
    platform = product.get("platform", "")
    rating = float(product.get("rating", 0) or 0)
    rating_count = int(product.get("rating_count", 0) or 0)
    sales_count = int(product.get("sales_count", 0) or 0)

    category_id = _find_category(category_path)
    now_ts = _now_ts()
    now_dt = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    conn = _conn()
    try:
        cur = conn.cursor()

        # 1. T_MALL_SYSTEM_GOODS
        img_fields = []
        img_values = []
        for i, url in enumerate(cos_images[:10]):
            img_fields.append(f"IMG_URL_{i+1}")
            img_values.append(url)

        cur.execute(f"""INSERT INTO T_MALL_SYSTEM_GOODS
            (UUID, SYSTEM_PRICE, CATEGORY_ID, IS_SHELF, CREATE_TIME, UP_TIME,
             LINK, {', '.join(img_fields)})
            VALUES (%s, %s, %s, 1, %s, %s, %s, {', '.join(['%s']*len(img_values))})
        """, [goods_id, price, category_id, now_dt, now_ts, source_url] + img_values)

        # 2. T_MALL_SYSTEM_GOODS_LANG
        lang_id = _uuid(f"{goods_id}_cn")
        cur.execute("""INSERT INTO T_MALL_SYSTEM_GOODS_LANG
            (UUID, GOODS_ID, LANG, NAME, DES)
            VALUES (%s, %s, 'cn', %s, %s)
            ON DUPLICATE KEY UPDATE NAME=%s, DES=%s""",
            (lang_id, goods_id, title, description[:8000], title, description[:8000]))

        lang_id_en = _uuid(f"{goods_id}_en")
        cur.execute("""INSERT INTO T_MALL_SYSTEM_GOODS_LANG
            (UUID, GOODS_ID, LANG, NAME, DES)
            VALUES (%s, %s, 'en', %s, %s)
            ON DUPLICATE KEY UPDATE NAME=%s, DES=%s""",
            (lang_id_en, goods_id, title, description[:8000], title, description[:8000]))

        # 3. T_MALL_SELLER_GOODS — 直接上架
        sg_id = _uuid(f"{goods_id}_seller")
        rec_time = now_ts
        new_time = now_ts
        sell_price = price * 1.3  # 市场价+30%

        cur.execute("""INSERT INTO T_MALL_SELLER_GOODS
            (UUID, SELLER_ID, CATEGORY_ID, GOODS_ID, SELLING_PRICE, SYSTEM_PRICE,
             IS_SHELF, IS_VALID, SYSTEM_REC_TIME, SYSTEM_NEW_TIME, CREATE_TIME,
             UP_TIME, FIRST_SHELF_TIME, SECONDARY_CATEGORY_ID)
            VALUES (%s, %s, %s, %s, %s, %s, 1, 1, %s, %s, %s, %s, %s, '0')""",
            (sg_id, seller_id, category_id, goods_id, sell_price, price,
             rec_time, new_time, now_dt, now_ts, now_ts))

        # 4. T_MALL_GOODS_SKU — 默认SKU
        sku_id = _uuid(f"{goods_id}_sku_default")
        sku_pic = cos_images[0] if cos_images else ""
        sku_data = f"平台:{platform}"
        if brand:
            sku_data = f"{sku_data}|品牌:{brand}"
        if rating > 0:
            sku_data = f"{sku_data}|评分:{rating}"
        if sales_count > 0:
            sku_data = f"{sku_data}|销量:{sales_count}"

        cur.execute("""INSERT INTO T_MALL_GOODS_SKU
            (ID, GOOD_ID, PRICE, PIC, SP_DATA, SALE, DELETED)
            VALUES (%s, %s, %s, %s, %s, %s, 0)""",
            (sku_id, goods_id, price, sku_pic, sku_data[:500], 999))

        # 插入多SKU（如果有采集到的变体规格）
        skus = product.get("skus", []) or []
        for i, sku in enumerate(skus[:20]):
            if isinstance(sku, dict):
                sku_price = float(sku.get("price", price) or price)
                sku_spec = sku.get("spec", "") or sku.get("name", "")
                sku_img = sku.get("image", "") or (cos_images[i+1] if i+1 < len(cos_images) else "")
                sku_data_detail = f"规格:{sku_spec}|{sku_data}"[:500]
                mu_sku_id = _uuid(f"{goods_id}_sku_{i}")
                cur.execute("""INSERT INTO T_MALL_GOODS_SKU
                    (ID, GOOD_ID, PRICE, PIC, SP_DATA, SALE, DELETED)
                    VALUES (%s, %s, %s, %s, %s, %s, 0)""",
                    (mu_sku_id, goods_id, sku_price, sku_img, sku_data_detail, 999))

        conn.commit()
        return {
            "ok": True,
            "goods_id": goods_id,
            "seller_goods_id": sg_id,
            "title": title[:50],
            "price": price,
            "category_id": category_id,
            "images_count": len(cos_images),
            "skus_count": 1 + min(len(skus), 20),
        }

    except Exception as e:
        conn.rollback()
        return {"ok": False, "error": str(e), "goods_id": goods_id}
    finally:
        conn.close()


def import_batch(products: list[dict], seller_id: str = DEFAULT_SELLER_ID) -> dict:
    """批量导入 — 自动去重"""
    imported = []
    skipped = []
    failed = []

    for p in products:
        result = import_product(p, seller_id)
        if result.get("ok"):
            imported.append(result)
        elif result.get("duplicate"):
            skipped.append(result)
        else:
            failed.append(result)

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
