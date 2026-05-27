"""企业级虚拟数据引擎 — 让商城像真实大平台一样活起来"""
import random
import hashlib
import json
import uuid
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import Optional

# ═══════════════════════════════════════
#  中文真实数据素材库
# ═══════════════════════════════════════

FAMILY_NAMES = ["王","李","张","刘","陈","杨","赵","黄","周","吴","徐","孙","胡","朱","高","林","何","郭","马","罗","梁","宋","郑","谢","韩","唐","冯","于","董","萧"]
GIVEN_NAMES_MALE = ["伟","强","磊","军","勇","杰","涛","明","超","辉","鹏","浩","亮","飞","刚","平","斌","宇","鑫","晨","睿","轩","昊","然","博","文","豪","志","宏","毅"]
GIVEN_NAMES_FEMALE = ["芳","敏","静","丽","婷","雪","玲","艳","娟","霞","秀","英","红","萍","梅","兰","琴","云","花","娜","琳","欣","悦","佳","慧","怡","婉","诗","涵","雅"]

CITIES = ["北京","上海","广州","深圳","杭州","成都","武汉","南京","重庆","苏州","西安","长沙","天津","郑州","东莞","青岛","合肥","佛山","宁波","昆明","沈阳","大连","厦门","福州","温州","南宁","长春","泉州","石家庄","贵阳"]
PROVINCES = ["广东","浙江","江苏","山东","河南","四川","湖北","湖南","福建","安徽","北京","上海","重庆","河北","辽宁","陕西","云南","贵州","广西","山西"]

PRODUCT_CATEGORIES = {
    "手机数码": {
        "品牌": ["Apple","华为","小米","OPPO","vivo","三星","一加","荣耀","realme","魅族"],
        "产品": [{"name":"iPhone 15 Pro Max","price":8999.00},{"name":"华为Mate 60 Pro","price":6999.00},{"name":"小米14 Ultra","price":5999.00},{"name":"OPPO Find X7","price":4599.00},{"name":"vivo X100 Pro","price":4999.00},{"name":"三星S24 Ultra","price":9699.00},{"name":"iPhone 15","price":5999.00},{"name":"荣耀Magic6 Pro","price":5699.00},{"name":"红米K70 Pro","price":3299.00},{"name":"一加12","price":4299.00}]
    },
    "电脑办公": {
        "品牌": ["Apple","联想","华为","戴尔","华硕","惠普","小米","ThinkPad","宏碁","微软"],
        "产品": [{"name":"MacBook Pro 16 M3","price":19999.00},{"name":"ThinkPad X1 Carbon","price":10999.00},{"name":"华为MateBook X Pro","price":8999.00},{"name":"戴尔XPS 15","price":12999.00},{"name":"小米笔记本Pro 16","price":6499.00},{"name":"华硕灵耀14","price":5999.00}]
    },
    "服饰鞋包": {
        "品牌": ["Nike","Adidas","优衣库","ZARA","H&M","李宁","安踏","UR","太平鸟","波司登"],
        "产品": [{"name":"Nike Air Force 1","price":899.00},{"name":"Adidas Ultraboost","price":1299.00},{"name":"优衣库羽绒服","price":599.00},{"name":"李宁篮球鞋","price":699.00},{"name":"ZARA西装外套","price":799.00}]
    },
    "家居电器": {
        "品牌": ["美的","格力","海尔","小米","戴森","松下","飞利浦","苏泊尔","九阳","科沃斯"],
        "产品": [{"name":"戴森V15吸尘器","price":4999.00},{"name":"小米扫地机器人","price":1999.00},{"name":"格力空调1.5匹","price":3499.00},{"name":"美的电饭煲","price":399.00},{"name":"科沃斯擦窗机器人","price":2599.00}]
    },
    "美妆个护": {
        "品牌": ["兰蔻","雅诗兰黛","SK-II","欧莱雅","完美日记","花西子","珀莱雅","自然堂","薇诺娜","资生堂"],
        "产品": [{"name":"兰蔻小黑瓶精华","price":1080.00},{"name":"SK-II神仙水","price":1590.00},{"name":"雅诗兰黛DW粉底液","price":420.00},{"name":"完美日记唇釉","price":59.90},{"name":"花西子散粉","price":149.00}]
    }
}

ORDER_STATUSES = [("已完成","completed"),("待发货","pending"),("已发货","shipped"),("已取消","cancelled"),("退款中","refunding")]
PAY_METHODS = ["微信支付","支付宝","银行卡","USDT","余额支付"]

ACTIVITY_TYPES = ["登录","浏览商品","搜索","加入购物车","下单","支付","充值","提现","签到","分享","评价","收藏","关注商家","领取优惠券","参与活动"]
COMPLAINT_REASONS = ["物流太慢","商品与描述不符","质量问题","发错货","客服态度差","不想要了","重复下单","地址填错"]
CUSTOMER_MESSAGES = [
    ("你好，这个什么时候发货？","发货咨询"),
    ("我已经付款了，能改地址吗？","订单修改"),
    ("收到的商品有划痕，我要退货","质量问题"),
    ("优惠券怎么用不了？","优惠券问题"),
    ("退款什么时候到账？","退款咨询"),
    ("这个能便宜点吗？","价格咨询"),
    ("帮我查下物流到哪了","物流查询"),
    ("颜色和图片不一样啊","商品问题"),
    ("怎么注册不了账号？","账户问题"),
    ("有没有免息分期","支付问题"),
    ("好评返现有吗？","活动咨询"),
    ("可以开发票吗？","发票问题"),
]

# ═══════════════════════════════════════
#  生成器函数
# ═══════════════════════════════════════

def random_chinese_name():
    surname = random.choice(FAMILY_NAMES)
    given = random.choice(GIVEN_NAMES_MALE + GIVEN_NAMES_FEMALE)
    if random.random() < 0.3:
        given += random.choice(GIVEN_NAMES_MALE + GIVEN_NAMES_FEMALE)
    return surname + given

def random_phone():
    prefixes = ["138","139","137","136","135","158","159","186","187","188","176","177","150","151","152"]
    return random.choice(prefixes) + "".join([str(random.randint(0,9)) for _ in range(8)])

def random_email(name="user"):
    domains = ["qq.com","163.com","gmail.com","outlook.com","icloud.com","foxmail.com"]
    return f"{name}{random.randint(100,99999)}@{random.choice(domains)}"

def random_address():
    return f"{random.choice(PROVINCES)}省{random.choice(CITIES)}市{random.choice(['朝阳区','海淀区','天河区','浦东新区','福田区','南山区','鼓楼区','西湖区','锦江区','武侯区','雁塔区','洪山区'])}{random.choice(['建设路','中山路','人民路','解放路','和平路','长安街'])}{random.randint(1,300)}号"

def random_date(start_days=365, end_days=0):
    start = datetime.now() - timedelta(days=start_days)
    end = datetime.now() - timedelta(days=end_days)
    delta = end - start
    return start + timedelta(seconds=random.randint(0, int(delta.total_seconds())))

def random_price(base=1000, spread=0.5):
    return round(random.uniform(base * (1-spread), base * (1+spread)), 2)

def gen_uuid():
    return str(uuid.uuid4()).replace("-","")[:32]

# ═══════════════════════════════════════
#  数据生成器
# ═══════════════════════════════════════

class UserGenerator:
    """用户数据生成 — 真实中文用户"""

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
                "email": random_email(name.lower().replace(" ","")),
                "password": hashlib.sha256(f"Test@{phone[-4:]}".encode()).hexdigest(),
                "balance": balance,
                "status": 1 if random.random() < 0.95 else 0,
                "kyc_level": kyc_level,
                "avatar": f"https://api.dicebear.com/7.x/avataaars/svg?seed={name}",
                "created_at": created.strftime("%Y-%m-%d %H:%M:%S"),
                "last_login": (created + timedelta(hours=random.randint(1,48))).strftime("%Y-%m-%d %H:%M:%S"),
                "login_count": login_days,
                "invite_code": hashlib.md5(uid.encode()).hexdigest()[:8],
                "recom_code": f"REC{random.randint(10000,99999)}" if random.random() < 0.2 else "",
                "source": random.choice(["web","h5","android","ios","invite"]),
            })
        return users

class ProductGenerator:
    """商品数据生成 — 多品类真实商品"""

    @staticmethod
    def generate(count=500) -> list[dict]:
        products = []
        for i in range(count):
            cat_name = random.choice(list(PRODUCT_CATEGORIES.keys()))
            cat = PRODUCT_CATEGORIES[cat_name]
            brand = random.choice(cat["品牌"])
            base = random.choice(cat["产品"])
            pid = gen_uuid()
            price = base["price"]
            stock = random.choices([0,random.randint(1,50),random.randint(50,500),random.randint(500,5000)], weights=[5,30,45,20])[0]
            sales = random.randint(stock//2 if stock < 100 else 0, stock * 5) if stock > 0 else 0
            products.append({
                "uuid": pid,
                "title": f"[{brand}] {base['name']} {random.choice(['旗舰版','Pro','Max','Plus','标准版','尊享版'])}",
                "brand": brand,
                "category": cat_name,
                "price": price + random.uniform(-200, 200),
                "original_price": price * (1 + random.uniform(0.1, 0.5)),
                "stock": stock,
                "sales": sales,
                "rating": round(random.uniform(3.5, 5.0), 1),
                "rating_count": random.randint(10, sales//2) if sales > 20 else random.randint(1, 10),
                "images": [f"https://picsum.photos/seed/{pid}{j}/800/800" for j in range(1,random.randint(3,6))],
                "description": f"<p>{brand}正品{base['name']}，品质保证，全国联保。</p><p>支持7天无理由退换，免费包邮。</p>",
                "status": 1 if stock > 0 and random.random() < 0.9 else 0,
                "is_hot": sales > 500,
                "is_new": random.random() < 0.15,
                "created_at": random_date(180, 1).strftime("%Y-%m-%d %H:%M:%S"),
            })
        return products

class OrderGenerator:
    """订单/交易数据生成"""

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
                "paid_at": (created + timedelta(minutes=random.randint(1,30))).strftime("%Y-%m-%d %H:%M:%S") if status_en != "cancelled" else "",
            })
        return orders

class WalletActivityGenerator:
    """钱包/资金流水生成"""

    @staticmethod
    def generate(users: list, count=3000) -> list[dict]:
        txns = []
        types = ["充值","提现","交易买入","交易卖出","退款","奖励","手续费","转账收款","转账付款","平台赠送","签到奖励","返佣"]
        for i in range(count):
            user = random.choice(users)
            txn_type = random.choice(types)
            created = random_date(90, 0)
            amount = round(random.uniform(10, 50000), 2) if txn_type in ("充值","提现","交易买入") else round(random.uniform(0.1, 500), 2)
            txns.append({
                "uuid": gen_uuid(),
                "user_id": user["uuid"],
                "type": txn_type,
                "amount": amount,
                "balance_after": round(random.uniform(100, 100000), 2),
                "status": "success" if random.random() < 0.95 else "failed",
                "created_at": created.strftime("%Y-%m-%d %H:%M:%S"),
                "remark": f"{user['real_name']} {txn_type} {amount}元",
            })
        return txns

class KlineGenerator:
    """K线行情数据生成 — 让交易图表有真实波动"""

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
    """客服消息生成"""

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
                "reply": f"您好，{msg_pair[1]}已收到，我们会尽快处理。" if random.random() < 0.7 else "",
                "created_at": created.strftime("%Y-%m-%d %H:%M:%S"),
                "replied_at": reply_time.strftime("%Y-%m-%d %H:%M:%S"),
            })
        return messages

class SigninGenerator:
    """签到记录生成"""

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
    """Banner/公告/资讯生成"""

    @staticmethod
    def generate(count=30) -> list[dict]:
        titles = [
            "🎉 平台周年庆，全场8折起！",
            "🔥 新用户注册即送100元体验金",
            "📢 系统升级维护公告",
            "💎 VIP会员权益全新升级",
            "🎁 邀请好友，双方各得50元",
            "🏆 交易大赛火热进行中",
            "📱 APP新版本已上线",
            "🛡️ 关于账户安全的温馨提示",
            "🚀 新币上线：SHIB/USDT交易对开放",
            "💹 行情分析：BTC突破关键阻力位",
            "🎊 国庆特惠，全场满减",
            "📊 2025年度交易报告已生成",
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

# ═══════════════════════════════════════
#  虚拟数据主引擎
# ═══════════════════════════════════════

class VirtualDataEngine:
    """统一虚拟数据引擎"""

    @staticmethod
    def generate_all(scale="small") -> dict:
        """一键生成全平台虚拟数据

        scale: small(1000用户/500商品), medium(5000/2000), large(20000/5000)
        """
        configs = {
            "small": {"users": 1000, "products": 500, "orders": 2000, "txns": 3000, "msgs": 500, "signins": 3000},
            "medium": {"users": 5000, "products": 2000, "orders": 8000, "txns": 12000, "msgs": 2000, "signins": 12000},
            "large": {"users": 20000, "products": 5000, "orders": 30000, "txns": 50000, "msgs": 8000, "signins": 50000},
            "huge": {"users": 50000, "products": 10000, "orders": 100000, "txns": 200000, "msgs": 20000, "signins": 200000},
        }

        cfg = configs.get(scale, configs["small"])
        result = {"scale": scale, "generated_at": datetime.now().isoformat(), "data": {}}

        # 用户
        users = UserGenerator.generate(cfg["users"])
        result["data"]["users"] = users

        # 商品
        products = ProductGenerator.generate(cfg["products"])
        result["data"]["products"] = products

        # 订单
        result["data"]["orders"] = OrderGenerator.generate(users, products, cfg["orders"])

        # 钱包流水
        result["data"]["wallet_txns"] = WalletActivityGenerator.generate(users, cfg["txns"])

        # K线数据
        result["data"]["klines"] = KlineGenerator.generate(days=90)

        # 客服消息
        result["data"]["customer_messages"] = CustomerServiceGenerator.generate(users, cfg["msgs"])

        # 签到记录
        result["data"]["signin_records"] = SigninGenerator.generate(users, cfg["signins"])

        # 内容
        result["data"]["content"] = ContentGenerator.generate(30)

        # 统计
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
        """生成实时活动日志 — 模拟平台有人正在使用"""
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
        """仪表盘实时统计数据"""
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