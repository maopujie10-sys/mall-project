"""浼佷笟绾ц櫄鎷熸暟鎹紩鎿?鈥?璁╁晢鍩庡儚鐪熷疄澶у钩鍙颁竴鏍锋椿璧锋潵"""
import random
import hashlib
import json
import uuid
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import Optional

# 鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺?#  涓枃鐪熷疄鏁版嵁绱犳潗搴?# 鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺?
FAMILY_NAMES = ["鐜?,"鏉?,"寮?,"鍒?,"闄?,"鏉?,"璧?,"榛?,"鍛?,"鍚?,"寰?,"瀛?,"鑳?,"鏈?,"楂?,"鏋?,"浣?,"閮?,"椹?,"缃?,"姊?,"瀹?,"閮?,"璋?,"闊?,"鍞?,"鍐?,"浜?,"钁?,"钀?]
GIVEN_NAMES_MALE = ["浼?,"寮?,"纾?,"鍐?,"鍕?,"鏉?,"娑?,"鏄?,"瓒?,"杈?,"楣?,"娴?,"浜?,"椋?,"鍒?,"骞?,"鏂?,"瀹?,"閼?,"鏅?,"鐫?,"杞?,"鏄?,"鐒?,"鍗?,"鏂?,"璞?,"蹇?,"瀹?,"姣?]
GIVEN_NAMES_FEMALE = ["鑺?,"鏁?,"闈?,"涓?,"濠?,"闆?,"鐜?,"鑹?,"濞?,"闇?,"绉€","鑻?,"绾?,"钀?,"姊?,"鍏?,"鐞?,"浜?,"鑺?,"濞?,"鐞?,"娆?,"鎮?,"浣?,"鎱?,"鎬?,"濠?,"璇?,"娑?,"闆?]

CITIES = ["鍖椾含","涓婃捣","骞垮窞","娣卞湷","鏉窞","鎴愰兘","姝︽眽","鍗椾含","閲嶅簡","鑻忓窞","瑗垮畨","闀挎矙","澶╂触","閮戝窞","涓滆帪","闈掑矝","鍚堣偉","浣涘北","瀹佹尝","鏄嗘槑","娌堥槼","澶ц繛","鍘﹂棬","绂忓窞","娓╁窞","鍗楀畞","闀挎槬","娉夊窞","鐭冲搴?,"璐甸槼"]
PROVINCES = ["骞夸笢","娴欐睙","姹熻嫃","灞变笢","娌冲崡","鍥涘窛","婀栧寳","婀栧崡","绂忓缓","瀹夊窘","鍖椾含","涓婃捣","閲嶅簡","娌冲寳","杈藉畞","闄曡タ","浜戝崡","璐靛窞","骞胯タ","灞辫タ"]

PRODUCT_CATEGORIES = {
    "鎵嬫満鏁扮爜": {
        "鍝佺墝": ["Apple","鍗庝负","灏忕背","OPPO","vivo","涓夋槦","涓€鍔?,"鑽ｈ€€","realme","榄呮棌"],
        "浜у搧": [{"name":"iPhone 15 Pro Max","price":8999.00},{"name":"鍗庝负Mate 60 Pro","price":6999.00},{"name":"灏忕背14 Ultra","price":5999.00},{"name":"OPPO Find X7","price":4599.00},{"name":"vivo X100 Pro","price":4999.00},{"name":"涓夋槦S24 Ultra","price":9699.00},{"name":"iPhone 15","price":5999.00},{"name":"鑽ｈ€€Magic6 Pro","price":5699.00},{"name":"绾㈢背K70 Pro","price":3299.00},{"name":"涓€鍔?2","price":4299.00}]
    },
    "鐢佃剳鍔炲叕": {
        "鍝佺墝": ["Apple","鑱旀兂","鍗庝负","鎴村皵","鍗庣","鎯犳櫘","灏忕背","ThinkPad","瀹忕","寰蒋"],
        "浜у搧": [{"name":"MacBook Pro 16 M3","price":19999.00},{"name":"ThinkPad X1 Carbon","price":10999.00},{"name":"鍗庝负MateBook X Pro","price":8999.00},{"name":"鎴村皵XPS 15","price":12999.00},{"name":"灏忕背绗旇鏈琍ro 16","price":6499.00},{"name":"鍗庣鐏佃€€14","price":5999.00}]
    },
    "鏈嶉グ闉嬪寘": {
        "鍝佺墝": ["Nike","Adidas","浼樿。搴?,"ZARA","H&M","鏉庡畞","瀹夎笍","UR","澶钩楦?,"娉㈠徃鐧?],
        "浜у搧": [{"name":"Nike Air Force 1","price":899.00},{"name":"Adidas Ultraboost","price":1299.00},{"name":"浼樿。搴撶窘缁掓湇","price":599.00},{"name":"鏉庡畞绡悆闉?,"price":699.00},{"name":"ZARA瑗胯澶栧","price":799.00}]
    },
    "瀹跺眳鐢靛櫒": {
        "鍝佺墝": ["缇庣殑","鏍煎姏","娴峰皵","灏忕背","鎴存．","鏉句笅","椋炲埄娴?,"鑻忔硦灏?,"涔濋槼","绉戞矁鏂?],
        "浜у搧": [{"name":"鎴存．V15鍚稿皹鍣?,"price":4999.00},{"name":"灏忕背鎵湴鏈哄櫒浜?,"price":1999.00},{"name":"鏍煎姏绌鸿皟1.5鍖?,"price":3499.00},{"name":"缇庣殑鐢甸キ鐓?,"price":399.00},{"name":"绉戞矁鏂摝绐楁満鍣ㄤ汉","price":2599.00}]
    },
    "缇庡涓姢": {
        "鍝佺墝": ["鍏拌敾","闆呰瘲鍏伴粵","SK-II","娆ц幈闆?,"瀹岀編鏃ヨ","鑺辫タ瀛?,"鐝€鑾遍泤","鑷劧鍫?,"钖囪濞?,"璧勭敓鍫?],
        "浜у搧": [{"name":"鍏拌敾灏忛粦鐡剁簿鍗?,"price":1080.00},{"name":"SK-II绁炰粰姘?,"price":1590.00},{"name":"闆呰瘲鍏伴粵DW绮夊簳娑?,"price":420.00},{"name":"瀹岀編鏃ヨ鍞囬噳","price":59.90},{"name":"鑺辫タ瀛愭暎绮?,"price":149.00}]
    }
}

ORDER_STATUSES = [("宸插畬鎴?,"completed"),("寰呭彂璐?,"pending"),("宸插彂璐?,"shipped"),("宸插彇娑?,"cancelled"),("閫€娆句腑","refunding")]
PAY_METHODS = ["寰俊鏀粯","鏀粯瀹?,"閾惰鍗?,"USDT","浣欓鏀粯"]

ACTIVITY_TYPES = ["鐧诲綍","娴忚鍟嗗搧","鎼滅储","鍔犲叆璐墿杞?,"涓嬪崟","鏀粯","鍏呭€?,"鎻愮幇","绛惧埌","鍒嗕韩","璇勪环","鏀惰棌","鍏虫敞鍟嗗","棰嗗彇浼樻儬鍒?,"鍙備笌娲诲姩"]
COMPLAINT_REASONS = ["鐗╂祦澶參","鍟嗗搧涓庢弿杩颁笉绗?,"璐ㄩ噺闂","鍙戦敊璐?,"瀹㈡湇鎬佸害宸?,"涓嶆兂瑕佷簡","閲嶅涓嬪崟","鍦板潃濉敊"]
CUSTOMER_MESSAGES = [
    ("浣犲ソ锛岃繖涓粈涔堟椂鍊欏彂璐э紵","鍙戣揣鍜ㄨ"),
    ("鎴戝凡缁忎粯娆句簡锛岃兘鏀瑰湴鍧€鍚楋紵","璁㈠崟淇敼"),
    ("鏀跺埌鐨勫晢鍝佹湁鍒掔棔锛屾垜瑕侀€€璐?,"璐ㄩ噺闂"),
    ("浼樻儬鍒告€庝箞鐢ㄤ笉浜嗭紵","浼樻儬鍒搁棶棰?),
    ("閫€娆句粈涔堟椂鍊欏埌璐︼紵","閫€娆惧挩璇?),
    ("杩欎釜鑳戒究瀹滅偣鍚楋紵","浠锋牸鍜ㄨ"),
    ("甯垜鏌ヤ笅鐗╂祦鍒板摢浜?,"鐗╂祦鏌ヨ"),
    ("棰滆壊鍜屽浘鐗囦笉涓€鏍峰晩","鍟嗗搧闂"),
    ("鎬庝箞娉ㄥ唽涓嶄簡璐﹀彿锛?,"璐︽埛闂"),
    ("鏈夋病鏈夊厤鎭垎鏈?,"鏀粯闂"),
    ("濂借瘎杩旂幇鏈夊悧锛?,"娲诲姩鍜ㄨ"),
    ("鍙互寮€鍙戠エ鍚楋紵","鍙戠エ闂"),
]

# 鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺?#  鐢熸垚鍣ㄥ嚱鏁?# 鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺?
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
    return f"{random.choice(PROVINCES)}鐪亄random.choice(CITIES)}甯倇random.choice(['鏈濋槼鍖?,'娴锋穩鍖?,'澶╂渤鍖?,'娴︿笢鏂板尯','绂忕敯鍖?,'鍗楀北鍖?,'榧撴ゼ鍖?,'瑗挎箹鍖?,'閿︽睙鍖?,'姝︿警鍖?,'闆佸鍖?,'娲北鍖?])}{random.choice(['寤鸿璺?,'涓北璺?,'浜烘皯璺?,'瑙ｆ斁璺?,'鍜屽钩璺?,'闀垮畨琛?])}{random.randint(1,300)}鍙?

def random_date(start_days=365, end_days=0):
    start = datetime.now() - timedelta(days=start_days)
    end = datetime.now() - timedelta(days=end_days)
    delta = end - start
    return start + timedelta(seconds=random.randint(0, int(delta.total_seconds())))

def random_price(base=1000, spread=0.5):
    return round(random.uniform(base * (1-spread), base * (1+spread)), 2)

def gen_uuid():
    return str(uuid.uuid4()).replace("-","")[:32]

# 鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺?#  鏁版嵁鐢熸垚鍣?# 鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺?
class UserGenerator:
    """鐢ㄦ埛鏁版嵁鐢熸垚 鈥?鐪熷疄涓枃鐢ㄦ埛"""

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
    """鍟嗗搧鏁版嵁鐢熸垚 鈥?澶氬搧绫荤湡瀹炲晢鍝?""

    @staticmethod
    def generate(count=500) -> list[dict]:
        products = []
        for i in range(count):
            cat_name = random.choice(list(PRODUCT_CATEGORIES.keys()))
            cat = PRODUCT_CATEGORIES[cat_name]
            brand = random.choice(cat["鍝佺墝"])
            base = random.choice(cat["浜у搧"])
            pid = gen_uuid()
            price = base["price"]
            stock = random.choices([0,random.randint(1,50),random.randint(50,500),random.randint(500,5000)], weights=[5,30,45,20])[0]
            sales = random.randint(stock//2 if stock < 100 else 0, stock * 5) if stock > 0 else 0
            products.append({
                "uuid": pid,
                "title": f"[{brand}] {base['name']} {random.choice(['鏃楄埌鐗?,'Pro','Max','Plus','鏍囧噯鐗?,'灏婁韩鐗?])}",
                "brand": brand,
                "category": cat_name,
                "price": price + random.uniform(-200, 200),
                "original_price": price * (1 + random.uniform(0.1, 0.5)),
                "stock": stock,
                "sales": sales,
                "rating": round(random.uniform(3.5, 5.0), 1),
                "rating_count": random.randint(10, sales//2) if sales > 20 else random.randint(1, 10),
                "images": [f"https://picsum.photos/seed/{pid}{j}/800/800" for j in range(1,random.randint(3,6))],
                "description": f"<p>{brand}姝ｅ搧{base['name']}锛屽搧璐ㄤ繚璇侊紝鍏ㄥ浗鑱斾繚銆?/p><p>鏀寔7澶╂棤鐞嗙敱閫€鎹紝鍏嶈垂鍖呴偖銆?/p>",
                "status": 1 if stock > 0 and random.random() < 0.9 else 0,
                "is_hot": sales > 500,
                "is_new": random.random() < 0.15,
                "created_at": random_date(180, 1).strftime("%Y-%m-%d %H:%M:%S"),
            })
        return products

class OrderGenerator:
    """璁㈠崟/浜ゆ槗鏁版嵁鐢熸垚"""

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
    """閽卞寘/璧勯噾娴佹按鐢熸垚"""

    @staticmethod
    def generate(users: list, count=3000) -> list[dict]:
        txns = []
        types = ["鍏呭€?,"鎻愮幇","浜ゆ槗涔板叆","浜ゆ槗鍗栧嚭","閫€娆?,"濂栧姳","鎵嬬画璐?,"杞处鏀舵","杞处浠樻","骞冲彴璧犻€?,"绛惧埌濂栧姳","杩斾剑"]
        for i in range(count):
            user = random.choice(users)
            txn_type = random.choice(types)
            created = random_date(90, 0)
            amount = round(random.uniform(10, 50000), 2) if txn_type in ("鍏呭€?,"鎻愮幇","浜ゆ槗涔板叆") else round(random.uniform(0.1, 500), 2)
            txns.append({
                "uuid": gen_uuid(),
                "user_id": user["uuid"],
                "type": txn_type,
                "amount": amount,
                "balance_after": round(random.uniform(100, 100000), 2),
                "status": "success" if random.random() < 0.95 else "failed",
                "created_at": created.strftime("%Y-%m-%d %H:%M:%S"),
                "remark": f"{user['real_name']} {txn_type} {amount}鍏?,
            })
        return txns

class KlineGenerator:
    """K绾胯鎯呮暟鎹敓鎴?鈥?璁╀氦鏄撳浘琛ㄦ湁鐪熷疄娉㈠姩"""

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
    """瀹㈡湇娑堟伅鐢熸垚"""

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
                "reply": f"鎮ㄥソ锛寋msg_pair[1]}宸叉敹鍒帮紝鎴戜滑浼氬敖蹇鐞嗐€? if random.random() < 0.7 else "",
                "created_at": created.strftime("%Y-%m-%d %H:%M:%S"),
                "replied_at": reply_time.strftime("%Y-%m-%d %H:%M:%S"),
            })
        return messages

class SigninGenerator:
    """绛惧埌璁板綍鐢熸垚"""

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
    """Banner/鍏憡/璧勮鐢熸垚"""

    @staticmethod
    def generate(count=30) -> list[dict]:
        titles = [
            "馃帀 骞冲彴鍛ㄥ勾搴嗭紝鍏ㄥ満8鎶樿捣锛?,
            "馃敟 鏂扮敤鎴锋敞鍐屽嵆閫?00鍏冧綋楠岄噾",
            "馃摙 绯荤粺鍗囩骇缁存姢鍏憡",
            "馃拵 VIP浼氬憳鏉冪泭鍏ㄦ柊鍗囩骇",
            "馃巵 閭€璇峰ソ鍙嬶紝鍙屾柟鍚勫緱50鍏?,
            "馃弳 浜ゆ槗澶ц禌鐏儹杩涜涓?,
            "馃摫 APP鏂扮増鏈凡涓婄嚎",
            "馃洝锔?鍏充簬璐︽埛瀹夊叏鐨勬俯棣ㄦ彁绀?,
            "馃殌 鏂板竵涓婄嚎锛歋HIB/USDT浜ゆ槗瀵瑰紑鏀?,
            "馃捁 琛屾儏鍒嗘瀽锛欱TC绐佺牬鍏抽敭闃诲姏浣?,
            "馃帄 鍥藉簡鐗规儬锛屽叏鍦烘弧鍑?,
            "馃搳 2025骞村害浜ゆ槗鎶ュ憡宸茬敓鎴?,
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

# 鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺?#  铏氭嫙鏁版嵁涓诲紩鎿?# 鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺?
class VirtualDataEngine:
    """缁熶竴铏氭嫙鏁版嵁寮曟搸"""

    @staticmethod
    def generate_all(scale="small") -> dict:
        """涓€閿敓鎴愬叏骞冲彴铏氭嫙鏁版嵁

        scale: small(1000鐢ㄦ埛/500鍟嗗搧), medium(5000/2000), large(20000/5000)
        """
        configs = {
            "small": {"users": 1000, "products": 500, "orders": 2000, "txns": 3000, "msgs": 500, "signins": 3000},
            "medium": {"users": 5000, "products": 2000, "orders": 8000, "txns": 12000, "msgs": 2000, "signins": 12000},
            "large": {"users": 20000, "products": 5000, "orders": 30000, "txns": 50000, "msgs": 8000, "signins": 50000},
            "huge": {"users": 50000, "products": 10000, "orders": 100000, "txns": 200000, "msgs": 20000, "signins": 200000},
        }

        cfg = configs.get(scale, configs["small"])
        result = {"scale": scale, "generated_at": datetime.now().isoformat(), "data": {}}

        # 鐢ㄦ埛
        users = UserGenerator.generate(cfg["users"])
        result["data"]["users"] = users

        # 鍟嗗搧
        products = ProductGenerator.generate(cfg["products"])
        result["data"]["products"] = products

        # 璁㈠崟
        result["data"]["orders"] = OrderGenerator.generate(users, products, cfg["orders"])

        # 閽卞寘娴佹按
        result["data"]["wallet_txns"] = WalletActivityGenerator.generate(users, cfg["txns"])

        # K绾挎暟鎹?        result["data"]["klines"] = KlineGenerator.generate(days=90)

        # 瀹㈡湇娑堟伅
        result["data"]["customer_messages"] = CustomerServiceGenerator.generate(users, cfg["msgs"])

        # 绛惧埌璁板綍
        result["data"]["signin_records"] = SigninGenerator.generate(users, cfg["signins"])

        # 鍐呭
        result["data"]["content"] = ContentGenerator.generate(30)

        # 缁熻
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
        """鐢熸垚瀹炴椂娲诲姩鏃ュ織 鈥?妯℃嫙骞冲彴鏈変汉姝ｅ湪浣跨敤"""
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
        """浠〃鐩樺疄鏃剁粺璁℃暟鎹?""
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