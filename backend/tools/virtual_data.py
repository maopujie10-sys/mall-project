""" -- """
import random
import hashlib
import json
import uuid
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import Optional


FAMILY_NAMES = ['','','','','','','','','','','','','','','','','','','','','','','','','','','','','','']
GIVEN_NAMES_MALE = ['','','','','','','','','','','','','','','','','','','','','','','','','','','','','','']
GIVEN_NAMES_FEMALE = ['','','','','','','','','','','','','','','','','','','','','','','','','','','','','','']

CITIES = ['','','','','','','','','','','','','','','','','','','','','','','','','','','','','','']
PROVINCES = ['','','','','','','','','','','','','','','','','','','','']

PRODUCT_CATEGORIES = {
    '': {
        '': ["Apple",'','',"OPPO","vivo",'','','',"realme",''],
        '': [{"name":"iPhone 15 Pro Max","price":8999.00},{"name":"Mate 60 Pro","price":6999.00},{"name":"14 Ultra","price":5999.00},{"name":"OPPO Find X7","price":4599.00},{"name":"vivo X100 Pro","price":4999.00},{"name":"S24 Ultra","price":9699.00},{"name":"iPhone 15","price":5999.00},{"name":"Magic6 Pro","price":5699.00},{"name":"K70 Pro","price":3299.00},{"name":"12","price":4299.00}]
    },
    '': {
        '': ["Apple",'','','','','','',"ThinkPad",'',''],
        '': [{"name":"MacBook Pro 16 M3","price":19999.00},{"name":"ThinkPad X1 Carbon","price":10999.00},{"name":"MateBook X Pro","price":8999.00},{"name":"XPS 15","price":12999.00},{"name":"Pro 16","price":6499.00},{"name":"14","price":5999.00}]
    },
    '': {
        '': ["Nike","Adidas",'',"ZARA","H&M",'','',"UR",'',''],
        '': [{"name":"Nike Air Force 1","price":899.00},{"name":"Adidas Ultraboost","price":1299.00},{"name":'',"price":599.00},{"name":'',"price":699.00},{"name":"ZARA","price":799.00}]
    },
    '': {
        '': ['','','','','','','','','',''],
        '': [{"name":"V15","price":4999.00},{"name":'',"price":1999.00},{"name":"1.5","price":3499.00},{"name":'',"price":399.00},{"name":'',"price":2599.00}]
    },
    '': {
        '': ['','',"SK-II",'','','','','','',''],
        '': [{"name":'',"price":1080.00},{"name":"SK-II","price":1590.00},{"name":"DW","price":420.00},{"name":'',"price":59.90},{"name":'',"price":149.00}]
    }
}

ORDER_STATUSES = [('',"completed"),('',"pending"),('',"shipped"),('',"cancelled"),('',"refunding")]
PAY_METHODS = ['','','',"USDT",'']

ACTIVITY_TYPES = ['','','','','','','','','','','','','','','']
COMPLAINT_REASONS = ['','','','','','','','']
CUSTOMER_MESSAGES = [
    (",?",''),
    (",?",''),
    (",",''),
    ("?",''),
    ("?",''),
    ("?",''),
    ('',''),
    ('',''),
    ("?",''),
    ('',''),
    ("?",''),
    ("?",''),
]


def random_chinese_name():
    surname = random.choice(FAMILY_NAMES)
    given = random.choice(GIVEN_NAMES_MALE + GIVEN_NAMES_FEMALE)
    if random.random() < 0.3:
        given += random.choice(GIVEN_NAMES_MALE + GIVEN_NAMES_FEMALE)
    return surname + given

def random_phone():
    prefixes = ["138","139","137","136","135","158","159","186","187","188","176","177","150","151","152"]
    return random.choice(prefixes) + ''.join([str(random.randint(0,9)) for _ in range(8)])

def random_email(name="user"):
    domains = ["qq.com","163.com","gmail.com","outlook.com","icloud.com","foxmail.com"]
    return f"{name}{random.randint(100,99999)}@{random.choice(domains)}"

def random_address():
    return f"{random.choice(PROVINCES)}{random.choice(CITIES)}{random.choice(['','','','','','','','','','','',''])}{random.choice(['','','','','',''])}{random.randint(1,300)}"

def random_date(start_days=365, end_days=0):
    start = datetime.now() - timedelta(days=start_days)
    end = datetime.now() - timedelta(days=end_days)
    delta = end - start
    return start + timedelta(seconds=random.randint(0, int(delta.total_seconds())))

def random_price(base=1000, spread=0.5):
    return round(random.uniform(base * (1-spread), base * (1+spread)), 2)

def gen_uuid():
    return str(uuid.uuid4()).replace("-",'')[:32]


class UserGenerator:
    ''" -- ''"

    @staticmethod
    def generate(count=1000) -> list[dict]:
        users = []
        for i in range(count):
            name = random_chinese_name()
            phone = random_phone()
            uid = gen_uuid()
            created = random_date(365, 1)
            login_days = random.randint(1, 300)
            balance = round(random.uniform(0, 500000), 2) if random.random() < 0.3 else round(random.uniform(0, 5000), 2)
            kyc_level = random.choices([0,1,2,3], weights=[40,30,20,10])[0]
            users.append({
                "uuid": uid,
                "username": f"user_{phone[-8:]}",
                "real_name": name,
                "phone": phone,
                "email": random_email(name.lower().replace('','')),
                "password": hashlib.sha256(f"Test@{phone[-4:]}".encode()).hexdigest(),
                "balance": balance,
                "status": 1 if random.random() < 0.95 else 0,
                "kyc_level": kyc_level,
                "avatar": f"https://api.dicebear.com/7.x/avataaars/svg?seed={name}",
                "created_at": created.strftime("%Y-%m-%d %H:%M:%S"),
                "last_login": (created + timedelta(hours=random.randint(1,48))).strftime("%Y-%m-%d %H:%M:%S"),
                "login_count": login_days,
                "invite_code": hashlib.md5(uid.encode()).hexdigest()[:8],
                "recom_code": f"REC{random.randint(10000,99999)}" if random.random() < 0.2 else '',
                "source": random.choice(["web","h5","android","ios","invite"]),
            })
        return users

class ProductGenerator:
    ''" -- ''"

    @staticmethod
    def generate(count=500) -> list[dict]:
        products = []
        for i in range(count):
            cat_name = random.choice(list(PRODUCT_CATEGORIES.keys()))
            cat = PRODUCT_CATEGORIES[cat_name]
            brand = random.choice(cat[''])
            base = random.choice(cat[''])
            pid = gen_uuid()
            price = base["price"]
            stock = random.choices([0,random.randint(1,50),random.randint(50,500),random.randint(500,5000)], weights=[5,30,45,20])[0]
            sales = random.randint(stock//2 if stock < 100 else 0, stock * 5) if stock > 0 else 0
            products.append({
                "uuid": pid,
                "title": f"[{brand}] {base['name']} {random.choice(['','Pro','Max','Plus','',''])}",
                "brand": brand,
                "category": cat_name,
                "price": price + random.uniform(-200, 200),
                "original_price": price * (1 + random.uniform(0.1, 0.5)),
                "stock": stock,
                "sales": sales,
                "rating": round(random.uniform(3.5, 5.0), 1),
                "rating_count": random.randint(10, sales//2) if sales > 20 else random.randint(1, 10),
                "images": [f"https://picsum.photos/seed/{pid}{j}/800/800" for j in range(1,random.randint(3,6))],
                "description": f"<p>{brand}{base['name']},.</p><p>7,.</p>",
                "status": 1 if stock > 0 and random.random() < 0.9 else 0,
                "is_hot": sales > 500,
                "is_new": random.random() < 0.15,
                "created_at": random_date(180, 1).strftime("%Y-%m-%d %H:%M:%S"),
            })
        return products

class OrderGenerator:
    ''"/''"

    @staticmethod
    def generate(users: list, products: list, count=2000) -> list[dict]:
        orders = []
        for i in range(count):
            user = random.choice(users)
            product = random.choice(products)
            status, status_en = random.choice(ORDER_STATUSES)
            amount = round(random.uniform(product["price"]*0.8, product["price"]), 2)
            created = random_date(90, 0)
            orders.append({
                "uuid": gen_uuid(),
                "order_no": f"ORD{created.strftime('%Y%m%d%H%M%S')}{random.randint(1000,9999)}",
                "user_id": user["uuid"],
                "user_name": user["real_name"],
                "product_title": product["title"],
                "product_id": product["uuid"],
                "quantity": random.choices([1,1,1,1,2,3,5], weights=[50,20,10,5,3,2,1])[0],
                "amount": amount,
                "pay_method": random.choice(PAY_METHODS),
                "status": status_en,
                "status_cn": status,
                "created_at": created.strftime("%Y-%m-%d %H:%M:%S"),
                "paid_at": (created + timedelta(minutes=random.randint(1,30))).strftime("%Y-%m-%d %H:%M:%S") if status_en != "cancelled" else '',
            })
        return orders

class WalletActivityGenerator:
    ''"/''"

    @staticmethod
    def generate(users: list, count=3000) -> list[dict]:
        txns = []
        types = ['','','','','','','','','','','','']
        for i in range(count):
            user = random.choice(users)
            txn_type = random.choice(types)
            created = random_date(90, 0)
            amount = round(random.uniform(10, 50000), 2) if txn_type in ('','','') else round(random.uniform(0.1, 500), 2)
            txns.append({
                "uuid": gen_uuid(),
                "user_id": user["uuid"],
                "type": txn_type,
                "amount": amount,
                "balance_after": round(random.uniform(100, 100000), 2),
                "status": "success" if random.random() < 0.95 else "failed",
                "created_at": created.strftime("%Y-%m-%d %H:%M:%S"),
                "remark": f"{user['real_name']} {txn_type} {amount}",
            })
        return txns

class KlineGenerator:
    ''"K -- ''"

    @staticmethod
    def generate(symbols=None, days=90) -> dict:
        if symbols is None:
            symbols = ["BTC/USDT","ETH/USDT","BNB/USDT","XRP/USDT","ADA/USDT","DOGE/USDT","SOL/USDT","DOT/USDT"]
        result = {}
        for sym in symbols:
            candles = []
            base = random.uniform(0.1, 50000)
            for d in range(days * 24):  # hourly candles
                t = datetime.now() - timedelta(hours=days*24 - d)
                change = random.uniform(-0.03, 0.03)
                close = base * (1 + change)
                high = max(base, close) * (1 + random.uniform(0, 0.02))
                low = min(base, close) * (1 - random.uniform(0, 0.02))
                volume = random.uniform(100, 100000)
                candles.append({
                    "time": t.strftime("%Y-%m-%d %H:%M:%S"),
                    "open": round(base, 4),
                    "high": round(high, 4),
                    "low": round(low, 4),
                    "close": round(close, 4),
                    "volume": round(volume, 2),
                })
                base = close
            result[sym] = candles
        return result

class CustomerServiceGenerator:
    ''''''

    @staticmethod
    def generate(users: list, count=500) -> list[dict]:
        messages = []
        for i in range(count):
            user = random.choice(users)
            msg_pair = random.choice(CUSTOMER_MESSAGES)
            created = random_date(30, 0)
            reply_time = created + timedelta(minutes=random.randint(1, 60))
            messages.append({
                "uuid": gen_uuid(),
                "user_id": user["uuid"],
                "user_name": user["real_name"],
                "message": msg_pair[0],
                "category": msg_pair[1],
                "is_read": random.random() < 0.8,
                "replied": random.random() < 0.7,
                "reply": f",{msg_pair[1]},." if random.random() < 0.7 else '',
                "created_at": created.strftime("%Y-%m-%d %H:%M:%S"),
                "replied_at": reply_time.strftime("%Y-%m-%d %H:%M:%S"),
            })
        return messages

class SigninGenerator:
    ''''''

    @staticmethod
    def generate(users: list, count=3000) -> list[dict]:
        records = []
        for i in range(count):
            user = random.choice(users)
            created = random_date(365, 0)
            records.append({
                "uuid": gen_uuid(),
                "user_id": user["uuid"],
                "day": random.randint(1, 365),
                "reward": round(random.uniform(0.1, 10), 2),
                "created_at": created.strftime("%Y-%m-%d %H:%M:%S"),
            })
        return records

class ContentGenerator:
    ''"Banner//''"

    @staticmethod
    def generate(count=30) -> list[dict]:
        titles = [
            " ,8!",
            " 100",
            " ",
            " VIP",
            " ,50",
            " ",
            " APP",
            " ",
            " :SHIB/USDT",
            " :BTC",
            " ,",
            " 2025",
        ]
        contents = []
        for i in range(min(count, len(titles))):
            contents.append({
                "uuid": gen_uuid(),
                "title": titles[i % len(titles)],
                "type": random.choice(["banner","announcement","news","activity"]),
                "status": 1,
                "sort": i + 1,
                "created_at": random_date(60, 0).strftime("%Y-%m-%d %H:%M:%S"),
                "image": f"https://picsum.photos/seed/banner{i}/1920/600",
            })
        return contents


class VirtualDataEngine:
    ''''''

    @staticmethod
    def generate_all(scale="small") -> dict:
        ''"

        scale: small(1000/500), medium(5000/2000), large(20000/5000)
        ''"
        configs = {
            "small": {"users": 1000, "products": 500, "orders": 2000, "txns": 3000, "msgs": 500, "signins": 3000},
            "medium": {"users": 5000, "products": 2000, "orders": 8000, "txns": 12000, "msgs": 2000, "signins": 12000},
            "large": {"users": 20000, "products": 5000, "orders": 30000, "txns": 50000, "msgs": 8000, "signins": 50000},
            "huge": {"users": 50000, "products": 10000, "orders": 100000, "txns": 200000, "msgs": 20000, "signins": 200000},
        }

        cfg = configs.get(scale, configs["small"])
        result = {"scale": scale, "generated_at": datetime.now().isoformat(), "data": {}}

        
        users = UserGenerator.generate(cfg["users"])
        result["data"]["users"] = users

        
        products = ProductGenerator.generate(cfg["products"])
        result["data"]["products"] = products

        
        result["data"]["orders"] = OrderGenerator.generate(users, products, cfg["orders"])

        
        result["data"]["wallet_txns"] = WalletActivityGenerator.generate(users, cfg["txns"])

        # K
        result["data"]["klines"] = KlineGenerator.generate(days=90)

        
        result["data"]["customer_messages"] = CustomerServiceGenerator.generate(users, cfg["msgs"])

        
        result["data"]["signin_records"] = SigninGenerator.generate(users, cfg["signins"])

        
        result["data"]["content"] = ContentGenerator.generate(30)

        
        result["stats"] = {
            "total_users": len(users),
            "total_products": len(products),
            "total_orders": len(result["data"]["orders"]),
            "total_txns": len(result["data"]["wallet_txns"]),
            "total_klines": sum(len(v) for v in result["data"]["klines"].values()),
            "total_messages": len(result["data"]["customer_messages"]),
            "total_signins": len(result["data"]["signin_records"]),
            "total_records": sum(len(v) if isinstance(v, list) else 0 for v in result["data"].values()),
        }

        return result

    @staticmethod
    def generate_realtime_activity(count=20) -> list[dict]:
        ''" -- ''"
        users = random.sample(list(range(10001, 11001)), min(count, 1000))
        activities = []
        now = datetime.now()
        for i in range(count):
            uid = random.choice(users)
            activity = random.choice(ACTIVITY_TYPES)
            activities.append({
                "user_id": f"USER{uid:08d}",
                "activity": activity,
                "ip": f"{random.randint(10,223)}.{random.randint(0,255)}.{random.randint(0,255)}.{random.randint(1,254)}",
                "device": random.choice(["iPhone 15","Samsung S24","Xiaomi 14","PC Windows","MacBook","iPad","Huawei P60","OPPO Find"]),
                "location": random.choice(CITIES),
                "time": (now - timedelta(seconds=random.randint(0, 300))).strftime("%H:%M:%S"),
            })
        return sorted(activities, key=lambda x: x["time"], reverse=True)

    @staticmethod
    def get_dashboard_stats() -> dict:
        ''''''
        now = datetime.now()
        return {
            "today": {
                "new_users": random.randint(20, 200),
                "orders": random.randint(30, 500),
                "revenue": round(random.uniform(5000, 200000), 2),
                "active_users": random.randint(100, 3000),
                "signins": random.randint(50, 800),
                "messages": random.randint(10, 100),
            },
            "total": {
                "users": random.randint(10000, 50000),
                "products": random.randint(2000, 10000),
                "orders": random.randint(50000, 200000),
                "volume_24h": round(random.uniform(100000, 5000000), 2),
            },
            "online_now": random.randint(50, 500),
            "updated_at": now.strftime("%Y-%m-%d %H:%M:%S"),
        }

def _save_virtual():
    from tools.memory_store import memory_store
    import json
    try:
        data = {"users": getattr(VirtualDataGenerator,"_generated_users",0) if hasattr(VirtualDataGenerator,"_generated_users") else 0}
        memory_store.set_knowledge("virtual_state", '', json.dumps(data))
    except: pass
def _load_virtual():
    from tools.memory_store import memory_store
    import json
    try:
        raw = memory_store.get_knowledge("virtual_state")
        if raw and isinstance(raw,list) and raw:
            d = json.loads(raw[0][2] if isinstance(raw[0],tuple) else str(raw[0]))
            if hasattr(VirtualDataGenerator,"_generated_users"): VirtualDataGenerator._generated_users = d.get("users",0)
    except: pass
try: _load_virtual()
except: pass