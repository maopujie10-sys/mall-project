"""鐩存帴鍐欏叆Mall鏁版嵁搴?鈥?鍘婚噸/涓婃灦/SKU鐢熸垚/璇勮"""
import hashlib
import time
import gc
import pymysql
from datetime import datetime
from typing import Optional

# 榛樿鍗栧ID锛堢郴缁熶腑宸叉湁9063涓晢鍝佺殑鑰佸崠瀹讹級
DEFAULT_SELLER_ID = "e7a5a8828bd3e591018c05838c120853"
# 榛樿鍒嗙被ID锛圖igital Products锛岄噰闆嗗晢鍝侀€氱敤鍏滃簳锛?
DEFAULT_CATEGORY_ID = "ff80808184809ef9018480a468c30000"

DB_CONFIG = {
    "host": "127.0.0.1",
    "port": 3306,
    "user": "root",
    "password": "Root@123",
    "database": "mall",
    "charset": "utf8mb4",
}

_cat_cache = {}  # category_path 鈫?CATEGORY_ID


def _conn():
    return pymysql.connect(**DB_CONFIG)


def _uuid(s: str) -> str:
    return hashlib.md5(s.encode()).hexdigest()[:32]


def _now_ts() -> int:
    return int(time.time() * 1000)


def _ensure_review_table():
    """鍒涘缓璇勮琛紙濡備笉瀛樺湪锛?""
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
        conn.close()


def _find_category(category_path: list[str], subcat_name: str = "") -> str:
    """灏濊瘯浠庡搧绫昏矾寰勫尮閰嶇郴缁熷垎绫伙紝澶辫触杩斿洖榛樿鍒嗙被"""
    if not category_path and not subcat_name:
        return DEFAULT_CATEGORY_ID

    cache_key = subcat_name or "|".join(category_path)
    if cache_key in _cat_cache:
        return _cat_cache[cache_key]

    conn = _conn()
    try:
        cur = conn.cursor()
        # 1) 浼樺厛绮剧‘鍖归厤瀛愬搧绫诲悕
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
        # 2) 妯＄硦鍖归厤鍝佺被璺緞
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
    """妫€鏌ラ噸澶?鈥?鎸夋爣棰樻ā绯婂尮閰嶆垨URL绮剧‘鍖归厤锛岃繑鍥炲凡瀛樺湪鐨凣OODS_ID"""
    conn = _conn()
    try:
        cur = conn.cursor()
        if source_url:
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
        conn.close()
    return None


def import_product(product: dict, seller_id: str = DEFAULT_SELLER_ID, subcat_name: str = "") -> dict:
    """瀵煎叆鍗曚釜閲囬泦鍟嗗搧鍒癕all鏁版嵁搴?鈥?鐩存帴涓婃灦

    鍐欏叆琛? T_MALL_SYSTEM_GOODS, T_MALL_SYSTEM_GOODS_LANG,
            T_MALL_SELLER_GOODS, T_MALL_GOODS_SKU, T_MALL_GOODS_REVIEW
    """
    title = product.get("title", "").strip()
    if not title:
        return {"ok": False, "error": "鏍囬涓虹┖"}

    source_url = product.get("source_url", "")
    goods_id = _uuid(source_url or title)

    # 鍘婚噸
    existing = check_duplicate(title, source_url)
    if existing:
        return {"ok": False, "error": "鍟嗗搧宸插瓨鍦?, "duplicate": True, "existing_id": existing}

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

    category_id = _find_category(category_path, subcat_name)
    now_ts = _now_ts()
    now_dt = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

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

        # 2. T_MALL_SYSTEM_GOODS_LANG 鈥?鏍囬+鎻忚堪锛堜腑鑻辨枃锛?
        lang_id = _uuid(f"{goods_id}_cn")
        desc_text = description[:8000]
        cur.execute("""INSERT INTO T_MALL_SYSTEM_GOODS_LANG
            (UUID, GOODS_ID, LANG, NAME, DES)
            VALUES (%s, %s, 'cn', %s, %s)
            ON DUPLICATE KEY UPDATE NAME=%s, DES=%s""",
            (lang_id, goods_id, title, desc_text, title, desc_text))

        lang_id_en = _uuid(f"{goods_id}_en")
        cur.execute("""INSERT INTO T_MALL_SYSTEM_GOODS_LANG
            (UUID, GOODS_ID, LANG, NAME, DES)
            VALUES (%s, %s, 'en', %s, %s)
            ON DUPLICATE KEY UPDATE NAME=%s, DES=%s""",
            (lang_id_en, goods_id, title, desc_text, title, desc_text))

        # 3. T_MALL_SELLER_GOODS 鈥?鐩存帴涓婃灦
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

        # 4. T_MALL_GOODS_SKU 鈥?澶歋KU锛堜粠閲囬泦鐨勮鏍肩敓鎴愶級
        sku_data_base = f"骞冲彴:{platform}"
        if brand:
            sku_data_base += f"|鍝佺墝:{brand}"
        if rating > 0:
            sku_data_base += f"|璇勫垎:{rating}"
        if rating_count > 0:
            sku_data_base += f"|{rating_count}璇?
        if sales_count > 0:
            sku_data_base += f"|閿€閲?{sales_count}"

        sku_count = 0
        if skus:
            for i, sku in enumerate(skus[:20]):
                if isinstance(sku, dict):
                    sku_price = float(sku.get("price", price) or price)
                    sku_spec = sku.get("spec", "")
                    sku_spec_name = sku.get("spec_name", "")
                    sku_img = sku.get("image", "") or (cos_images[0] if cos_images else "")
                    sku_data = f"{sku_data_base}|瑙勬牸:{sku_spec_name}:{sku_spec}"[:500]
                    mu_sku_id = _uuid(f"{goods_id}_sku_{i}")
                    cur.execute("""INSERT INTO T_MALL_GOODS_SKU
                        (ID, GOOD_ID, PRICE, PIC, SP_DATA, SALE, DELETED)
                        VALUES (%s, %s, %s, %s, %s, %s, 0)
                        ON DUPLICATE KEY UPDATE PRICE=%s, SP_DATA=%s""",
                        (mu_sku_id, goods_id, sku_price, sku_img, sku_data, 999,
                         sku_price, sku_data))
                    sku_count += 1

        if sku_count == 0:
            # 榛樿SKU
            sku_id = _uuid(f"{goods_id}_sku_default")
            sku_pic = cos_images[0] if cos_images else ""
            cur.execute("""INSERT INTO T_MALL_GOODS_SKU
                (ID, GOOD_ID, PRICE, PIC, SP_DATA, SALE, DELETED)
                VALUES (%s, %s, %s, %s, %s, %s, 0)""",
                (sku_id, goods_id, price, sku_pic, sku_data_base[:500], 999))
            sku_count = 1

        # 5. 鍐欏叆璇勮
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
        conn.close()
        return result

    except Exception as e:
        conn.rollback()
        conn.close()
        return {"ok": False, "error": str(e), "goods_id": goods_id}


def import_batch(products: list[dict], seller_id: str = DEFAULT_SELLER_ID, subcat_name: str = "") -> dict:
    """鎵归噺瀵煎叆 鈥?鑷姩鍘婚噸锛屽瀹岃Е鍙慓C"""
    imported = []
    skipped = []
    failed = []

    for p in products:
        result = import_product(p, seller_id, subcat_name)
        if result.get("ok"):
            imported.append(result)
        elif result.get("duplicate"):
            skipped.append(result)
        else:
            failed.append(result)

    # 姣忔壒瀵煎畬瑙﹀彂涓€娆C
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
