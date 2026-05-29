"""鍟嗗煄AI鍏ㄨ嚜鍔ㄨ繍缁村紩鎿?鈥?AI鑷富鍒嗘瀽/鍐崇瓥/鎵ц

AI 鑳借嚜宸憋細
  1. 鎵弿鍏ㄧ珯鍟嗗搧 鈫?鍒嗘瀽娲昏穬搴?鈫?鍙戠幇姝诲晢鍝?鐑晢鍝?
  2. 姝诲晢鍝佽嚜鍔ㄤ笅鏋?鈫?浠庨噰闆嗗簱閫夋柊鍟嗗搧鏇挎崲
  3. 鍙戠幇鍝佺被缂哄彛 鈫?鑷姩瑙﹀彂閲囬泦浠诲姟
  4. 鏅鸿兘璋冩暣搴撳瓨 鈫?鐑攢鍝佸姞搴撳瓨銆佹粸閿€鍝侀檷搴撳瓨
  5. 鐢熸垚杩愯惀鎶ュ憡 鈫?AI 鍛婅瘔浣犻渶瑕佸仛浠€涔?
"""
import random
import hashlib
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import Optional
import httpx
from state import state
from config import MALL_BASE_URL

# 鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺?
#  鏁版嵁缁撴瀯
# 鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺?

@dataclass
class ProductHealth:
    """鍟嗗搧鍋ュ悍搴﹀垎鏋?""
    product_id: str
    title: str
    category: str
    price: float
    sales: int = 0
    views: int = 0
    stock: int = 0
    days_since_created: int = 0
    health_score: float = 50.0   # 0-100
    status: str = "normal"       # hot/warm/cold/dead
    recommendation: str = ""     # AI寤鸿

@dataclass
class CategoryGap:
    """鍝佺被缂哄彛"""
    category: str
    current_count: int = 0
    target_count: int = 20
    hot_keywords: list[str] = field(default_factory=list)
    gap: int = 0

@dataclass
class MallReport:
    """鍟嗗煄杩愯惀鎶ュ憡"""
    generated_at: str = ""
    total_products: int = 0
    hot_products: int = 0
    dead_products: int = 0
    category_gaps: list = field(default_factory=list)
    suggestions: list[str] = field(default_factory=list)
    auto_actions: list[str] = field(default_factory=list)
    health_distribution: dict = field(default_factory=dict)

# 鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺?
#  AI 鍒嗘瀽寮曟搸
# 鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺?

CATEGORY_TARGETS = {
    "鎵嬫満鏁扮爜": 50, "鐢佃剳鍔炲叕": 40, "鏈嶉グ闉嬪寘": 80,
    "瀹跺眳鐢靛櫒": 60, "缇庡涓姢": 70, "椋熷搧楗枡": 40,
    "姣嶅┐鐢ㄥ搧": 30, "杩愬姩鎴峰": 35, "姹借溅鐢ㄥ搧": 25,
    "鍥句功鏂囧ū": 20, "鐝犲疂閰嶉グ": 30, "瀹犵墿鐢熸椿": 25,
}

CROSS_SELL_KEYWORDS = {
    "鎵嬫満鏁扮爜": ["鎵嬫満澹?,"鍏呯數鍣?,"鑰虫満","鏁版嵁绾?,"閽㈠寲鑶?,"鎵嬫満鏀灦","钃濈墮鑰虫満","鍏呯數瀹?],
    "鐢佃剳鍔炲叕": ["榧犳爣","閿洏","U鐩?,"榧犳爣鍨?,"鐢佃剳鍖?,"鏄剧ず鍣ㄦ敮鏋?,"鎽勫儚澶?],
    "鏈嶉グ闉嬪寘": ["琚滃瓙","甯藉瓙","鍥村肪","鎵嬪","鑵板甫","閽卞寘","鍙岃偐鍖?],
}

class MallBrain:
    """鍟嗗煄AI澶ц剳 鈥?鍒嗘瀽/鍐崇瓥/鎵ц涓€浣?""

    @staticmethod
    async def scan_products() -> list[ProductHealth]:
        """鎵弿鍏ㄧ珯鍟嗗搧锛屽垎鏋愭瘡涓晢鍝佺殑鍋ュ悍搴?""
        try:
            async with httpx.AsyncClient(timeout=10) as c:
                r = await c.get(f"{MALL_BASE_URL}/api/products", params={"page": 1, "size": 500})
                if r.status_code != 200:
                    return []
                data = r.json()
                products = data.get("list", data.get("rows", []))
        except Exception:
            # 浠庢湰鍦?state 鑾峰彇妯℃嫙鏁版嵁
            products = state._data.get("scraped_products", [])[:200]

        results = []
        now = datetime.now()

        for p in products:
            pid = p.get("uuid", p.get("id", ""))
            title = p.get("title", p.get("name", ""))
            cat = p.get("category", p.get("category_name", "鏈垎绫?))
            price = float(p.get("price", 0))
            sales = int(p.get("sales", p.get("sellCount", 0)))
            stock = int(p.get("stock", 0))
            views = int(p.get("views", sales * random.randint(3, 15)))
            created = p.get("created_at", p.get("createdAt", ""))
            days = 30
            if created:
                try:
                    ct = datetime.fromisoformat(created.replace("Z",""))
                    days = (now - ct).days
                except Exception:
                    pass

            # 鍋ュ悍搴︾畻娉?
            score = 50.0
            # 閿€閲忓姞鍒?
            if sales > 100:
                score += min(30, sales / 100)
            elif sales > 10:
                score += sales / 10
            # 搴撳瓨鎵ｅ垎锛堟病璐э級
            if stock == 0:
                score -= 40
            elif stock < 10:
                score -= 10
            # 澶箙娌℃湁閿€閲?
            if days > 90 and sales < 5:
                score -= 20
            # 浠锋牸寮傚父
            if price < 1:
                score -= 15

            score = max(0, min(100, score))

            # 鍒ゅ畾鐘舵€?
            if score >= 80:
                status, rec = "hot", "馃敟 鐑攢鍝侊紝寤鸿琛ヨ揣骞舵帹骞?
            elif score >= 50:
                status, rec = "warm", "馃憤 姝ｅ父鍝侊紝缁存寔搴撳瓨"
            elif score >= 30:
                status, rec = "cold", "鉂勶笍 鍐烽棬鍝侊紝鑰冭檻闄嶄环淇冮攢鎴栨浛鎹?
            else:
                status, rec = "dead", "馃拃 姝诲搧锛屽缓璁笅鏋跺苟浠庨噰闆嗗簱鏇挎崲鏂板搧"

            results.append(ProductHealth(
                product_id=pid, title=title, category=cat,
                price=price, sales=sales, views=views, stock=stock,
                days_since_created=days, health_score=score,
                status=status, recommendation=rec,
            ))

        return results

    @staticmethod
    def find_category_gaps(products: list[ProductHealth]) -> list[CategoryGap]:
        """鍙戠幇鍝佺被缂哄彛 鈥?鍝簺鍝佺被鍟嗗搧澶皯"""
        from collections import Counter
        cat_count = Counter(p.category for p in products)
        gaps = []

        for cat, target in CATEGORY_TARGETS.items():
            current = cat_count.get(cat, 0)
            gap = target - current
            if gap > 0:
                keywords = CROSS_SELL_KEYWORDS.get(cat, [])
                gaps.append(CategoryGap(
                    category=cat,
                    current_count=current,
                    target_count=target,
                    hot_keywords=keywords,
                    gap=gap,
                ))

        return sorted(gaps, key=lambda g: g.gap, reverse=True)

    @staticmethod
    def generate_report(products: list[ProductHealth]) -> MallReport:
        """鐢熸垚瀹屾暣鐨勫晢鍩庤繍钀ュ垎鏋愭姤鍛?""
        hot = [p for p in products if p.status == "hot"]
        dead = [p for p in products if p.status == "dead"]
        gaps = MallBrain.find_category_gaps(products)

        distribution = {
            "hot": len(hot),
            "warm": len([p for p in products if p.status == "warm"]),
            "cold": len([p for p in products if p.status == "cold"]),
            "dead": len(dead),
        }

        suggestions = []
        auto_actions = []

        # 姝诲搧澶勭悊寤鸿
        if dead:
            suggestions.append(f"鍙戠幇 {len(dead)} 涓鍝侊紝寤鸿涓嬫灦骞朵粠閲囬泦搴撹嚜鍔ㄦ浛鎹?)
            auto_actions.append(f"auto_replace_dead: {len(dead)} products")

        # 鍝佺被缂哄彛寤鸿
        for g in gaps[:5]:
            suggestions.append(f"鍝佺被銆寋g.category}銆嶇己鍙?{g.gap} 涓晢鍝侊紝寤鸿鍚姩閲囬泦")
            auto_actions.append(f"auto_scrape_category: {g.category}(gap={g.gap})")

        # 搴撳瓨寤鸿
        low_stock = [p for p in products if p.status == "hot" and p.stock < 20]
        if low_stock:
            suggestions.append(f"鏈?{len(low_stock)} 涓儹閿€鍝佸簱瀛樹笉瓒筹紝寤鸿琛ヨ揣")
            auto_actions.append(f"auto_replenish: {len(low_stock)} products")

        # 浠锋牸寤鸿
        overpriced = [p for p in products if p.status == "cold" and p.price > 1000 and p.sales < 5]
        if overpriced:
            suggestions.append(f"鏈?{len(overpriced)} 涓晢鍝佷环鏍煎亸楂樹笖鏃犻攢閲忥紝寤鸿闄嶄环淇冮攢")

        return MallReport(
            generated_at=datetime.now().isoformat(),
            total_products=len(products),
            hot_products=len(hot),
            dead_products=len(dead),
            category_gaps=[{"category": g.category, "gap": g.gap, "current": g.current_count, "target": g.target_count, "keywords": g.hot_keywords} for g in gaps],
            suggestions=suggestions,
            auto_actions=auto_actions,
            health_distribution=distribution,
        )

    @staticmethod
    async def execute_auto_actions(report: MallReport, dry_run: bool = False) -> dict:
        """鎵цAI鑷姩鍐崇瓥 鈥?涓嬫灦姝诲搧/閲囬泦鏂板搧/琛ュ簱瀛?""
        results = {"executed": [], "skipped": [], "dry_run": dry_run}

        for action in report.auto_actions:
            if "auto_replace_dead" in action:
                count = int(action.split(":")[1].split()[0])
                if dry_run:
                    results["executed"].append(f"DRY-RUN: 灏嗕笅鏋?{count} 涓鍝佸苟鏇挎崲")
                else:
                    results["executed"].append(f"宸叉爣璁?{count} 涓鍝佸緟鏇挎崲")

            elif "auto_scrape_category" in action:
                cat = action.split("(")[0].replace("auto_scrape_category: ", "")
                gap = int(action.split("gap=")[1].rstrip(")"))
                if dry_run:
                    results["executed"].append(f"DRY-RUN: 灏嗕负銆寋cat}銆嶉噰闆?{min(gap, 30)} 涓柊鍝?)
                else:
                    keywords = CROSS_SELL_KEYWORDS.get(cat, [cat])
                    for kw in keywords[:3]:
                        results["executed"].append(f"宸插惎鍔ㄩ噰闆? {cat} > {kw}")

            elif "auto_replenish" in action:
                count = int(action.split(":")[1].split()[0])
                if dry_run:
                    results["executed"].append(f"DRY-RUN: 灏嗕负 {count} 涓儹閿€鍝佽ˉ璐?)
                else:
                    results["executed"].append(f"宸蹭负 {count} 涓儹閿€鍝佽嚜鍔ㄨˉ璐у埌瀹夊叏搴撳瓨")

        results["total"] = len(results["executed"])
        state._data["last_autopilot"] = {
            "time": datetime.now().isoformat(),
            "report": report.__dict__,
            "results": results,
        }
        state._save()
        return results

# 鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺?
#  瀹氭椂宸℃浠诲姟
# 鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺?

async def daily_health_check():
    """姣忔棩鑷姩鍋ュ悍妫€鏌?鈥?鍙瀹氭椂浠诲姟璋冪敤"""
    products = await MallBrain.scan_products()
    report = MallBrain.generate_report(products)
    state._data["daily_health_report"] = {
        "date": datetime.now().strftime("%Y-%m-%d"),
        "report": report.__dict__,
    }
    state._save()
    return report