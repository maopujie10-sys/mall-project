''"AI -- AI
AI :
  1.  ->  -> /
  2.  -> 
  3.  -> 
  4.  -> 
  5.  -> AI 
''"
import random
import hashlib
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import Optional
import httpx
from state import state
from config import MALL_BASE_URL


@dataclass
class ProductHealth:
    ''''''
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
    recommendation: str = ''     # AI

@dataclass
class CategoryGap:
    ''''''
    category: str
    current_count: int = 0
    target_count: int = 20
    hot_keywords: list[str] = field(default_factory=list)
    gap: int = 0

@dataclass
class MallReport:
    ''''''
    generated_at: str = ''
    total_products: int = 0
    hot_products: int = 0
    dead_products: int = 0
    category_gaps: list = field(default_factory=list)
    suggestions: list[str] = field(default_factory=list)
    auto_actions: list[str] = field(default_factory=list)
    health_distribution: dict = field(default_factory=dict)


#  AI 

CATEGORY_TARGETS = {
    '': 50, '': 40, '': 80,
    '': 60, '': 70, '': 40,
    '': 30, '': 35, '': 25,
    '': 20, '': 30, '': 25,
}

CROSS_SELL_KEYWORDS = {
    '': ['','','','','','','',''],
    '': ['','',"U",'','','',''],
    '': ['','','','','','',''],
}

class MallBrain:
    ''"AI -- //''"

    @staticmethod
    async def scan_products() -> list[ProductHealth]:
        ''",''"
        try:
            async with httpx.AsyncClient(timeout=10) as c:
                r = await c.get(f"{MALL_BASE_URL}/api/products", params={"page": 1, "size": 500})
                if r.status_code != 200:
                    return []
                data = r.json()
                products = data.get("list", data.get("rows", []))
        except Exception:
            #  state 
            products = state._data.get("scraped_products", [])[:200]

        results = []
        now = datetime.now()

        for p in products:
            pid = p.get("uuid", p.get("id", ''))
            title = p.get("title", p.get("name", ''))
            cat = p.get("category", p.get("category_name", ''))
            price = float(p.get("price", 0))
            sales = int(p.get("sales", p.get("sellCount", 0)))
            stock = int(p.get("stock", 0))
            views = int(p.get("views", sales * random.randint(3, 15)))
            created = p.get("created_at", p.get("createdAt", ''))
            days = 30
            if created:
                try:
                    ct = datetime.fromisoformat(created.replace("Z",''))
                    days = (now - ct).days
                except Exception:
                    pass

            
            score = 50.0
            
            if sales > 100:
                score += min(30, sales / 100)
            elif sales > 10:
                score += sales / 10
            # ()
            if stock == 0:
                score -= 40
            elif stock < 10:
                score -= 10
            
            if days > 90 and sales < 5:
                score -= 20
            
            if price < 1:
                score -= 15

            score = max(0, min(100, score))

            
            if score >= 80:
                status, rec = "hot", " ,"
            elif score >= 50:
                status, rec = "warm", " ,"
            elif score >= 30:
                status, rec = "cold", " ,"
            else:
                status, rec = "dead", " ,"

            results.append(ProductHealth(
                product_id=pid, title=title, category=cat,
                price=price, sales=sales, views=views, stock=stock,
                days_since_created=days, health_score=score,
                status=status, recommendation=rec,
            ))

        return results

    @staticmethod
    def find_category_gaps(products: list[ProductHealth]) -> list[CategoryGap]:
        ''" -- ''"
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
        ''''''
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

        
        if dead:
            suggestions.append(f" {len(dead)} ,")
            auto_actions.append(f"auto_replace_dead: {len(dead)} products")

        
        for g in gaps[:5]:
            suggestions.append(f"{g.category} {g.gap} ,")
            auto_actions.append(f"auto_scrape_category: {g.category}(gap={g.gap})")

        
        low_stock = [p for p in products if p.status == "hot" and p.stock < 20]
        if low_stock:
            suggestions.append(f" {len(low_stock)} ,")
            auto_actions.append(f"auto_replenish: {len(low_stock)} products")

        
        overpriced = [p for p in products if p.status == "cold" and p.price > 1000 and p.sales < 5]
        if overpriced:
            suggestions.append(f" {len(overpriced)} ,")

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
        ''"AI -- //''"
        results = {"executed": [], "skipped": [], "dry_run": dry_run}

        for action in report.auto_actions:
            if "auto_replace_dead" in action:
                count = int(action.split(":")[1].split()[0])
                if dry_run:
                    results["executed"].append(f"DRY-RUN:  {count} ")
                else:
                    results["executed"].append(f" {count} ")

            elif "auto_scrape_category" in action:
                cat = action.split("(")[0].replace("auto_scrape_category: ", '')
                gap = int(action.split("gap=")[1].rstrip(")"))
                if dry_run:
                    results["executed"].append(f"DRY-RUN: {cat} {min(gap, 30)} ")
                else:
                    keywords = CROSS_SELL_KEYWORDS.get(cat, [cat])
                    for kw in keywords[:3]:
                        results["executed"].append(f": {cat} > {kw}")

            elif "auto_replenish" in action:
                count = int(action.split(":")[1].split()[0])
                if dry_run:
                    results["executed"].append(f"DRY-RUN:  {count} ")
                else:
                    results["executed"].append(f" {count} ")

        results["total"] = len(results["executed"])
        state._data["last_autopilot"] = {
            "time": datetime.now().isoformat(),
            "report": report.__dict__,
            "results": results,
        }
        state._save()
        return results


async def daily_health_check():
    ''" -- ''"
    products = await MallBrain.scan_products()
    report = MallBrain.generate_report(products)
    state._data["daily_health_report"] = {
        "date": datetime.now().strftime("%Y-%m-%d"),
        "report": report.__dict__,
    }
    state._save()
    return report

def _save_state():
    from tools.memory_store import memory_store
    import json
    try:
        memory_store.set_knowledge("autopilot_state", '', json.dumps({"last_run": getattr(MallBrain,"_last_run",0)}, ensure_ascii=False))
    except: pass
def _load_state():
    from tools.memory_store import memory_store
    import json
    try:
        data = memory_store.get_knowledge("autopilot_state")
        if data and isinstance(data, list) and data:
            d = json.loads(data[0][2] if isinstance(data[0],tuple) else str(data[0]))
            MallBrain._last_run = d.get("last_run", 0)
    except: pass
try: _load_state()
except: pass