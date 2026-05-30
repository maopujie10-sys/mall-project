''" -- ,''"
import asyncio
import sys
sys.path.insert(0, ".")

CATEGORY_KEYWORDS = {
    "Digital Products": ["tablet", "smart watch", "laptop", "camera", "drone"],
    "Computer Peripherals": ["keyboard", "mouse pad", "monitor", "usb hub", "headset"],
    "Phones & Accessories": ["phone case", "charging cable", "wireless charger", "power bank", "phone holder"],
    "Home Appliances": ["air fryer", "vacuum cleaner", "blender", "coffee maker", "toaster"],
    "Women's Clothing": ["women dress", "women blouse", "women jacket", "women skirt", "women sweater"],
    "Men's Clothing": ["men shirt", "men jacket", "men jeans", "men hoodie", "men t-shirt"],
    "Kids & Babies": ["baby toys", "baby clothes", "stroller", "baby bottle", "diaper bag"],
    "Kids Toys": ["lego", "action figure", "puzzle", "remote control car", "board game"],
    "Health Beauty & Hair": ["face cream", "hair dryer", "makeup brush", "perfume", "nail polish"],
    "Sports & Outdoors": ["yoga mat", "dumbbell", "camping tent", "running shoes", "fishing rod"],
    "Jewelry & Watches": ["necklace", "bracelet", "earrings", "rings", "watch men"],
    "Food & Beverage": ["coffee beans", "tea set", "protein powder", "chocolate gift", "olive oil"],
    "Ladies Bag": ["handbag", "shoulder bag", "backpack women", "tote bag", "clutch bag"],
    "Men's Bag": ["backpack men", "messenger bag", "briefcase", "laptop bag", "waist bag"],
    "Office Stationery": ["pen set", "notebook", "stapler", "desk organizer", "whiteboard"],
    "Snack Dessert": ["cookies", "chocolate", "candy", "nuts", "chips"],
    "Luxury": ["luxury watch", "designer bag", "gold necklace", "luxury perfume", "sunglasses designer"],
    "Epidemic Prevention Supplies": ["face mask", "hand sanitizer", "disinfectant wipes", "gloves", "thermometer"],
    "Recreational Fishing Gear": ["fishing reel", "fishing line", "fishing lure", "fishing rod holder", "tackle box"],
}

async def run(platform="amazon", products_per_kw=3):
    from tools.scraper_engine import ADAPTERS
    from tools.mall_importer import import_batch
    import httpx
    from tools.scraper_engine import download_and_upload

    totals = {"cats": 0, "kws": 0, "found": 0, "imported": 0, "skipped": 0, "failed": 0}

    for cat_name, keywords in CATEGORY_KEYWORDS.items():
        print(f"\n{'='*60}")
        print(f"[] {cat_name}")
        totals["cats"] += 1

        adapter = ADAPTERS.get(platform, ADAPTERS["amazon"])
        async with httpx.AsyncClient(timeout=25, follow_redirects=True, verify=False) as session:
            for kw in keywords:
                print(f"  [] {kw}")
                totals["kws"] += 1

                try:
                    urls = await adapter.search(kw, max_pages=1, session=session)
                    print(f"    : {len(urls)} ")
                except Exception as e:
                    print(f"    : {e}")
                    continue

                products = []
                for url in urls[:products_per_kw]:
                    try:
                        p = await adapter.extract_product(url, session=session)
                        if p and p.title and p.images:
                            p.id = __import__('hashlib').md5(p.source_url.encode()).hexdigest()[:16]
                            products.append(p)
                    except Exception:
                        continue
                    await asyncio.sleep(1.5)

                if not products:
                    print(f'')
                    continue

                # (URL)
                for p in products:
                    uploaded = []
                    for idx, img_url in enumerate(p.images[:8]):
                        cos_url = await download_and_upload(img_url, p.id, idx, session)
                        if cos_url:
                            uploaded.append(cos_url)
                        elif img_url:
                            uploaded.append(img_url)
                    p.cos_images = uploaded

                
                pds = [p.to_dict() for p in products if p.cos_images]
                result = import_batch(pds)
                totals["found"] += len(pds)
                totals["imported"] += result["imported"]
                totals["skipped"] += result["skipped_duplicate"]
                totals["failed"] += result["failed"]
                print(f"    : {result['imported']} , {result['skipped_duplicate']} , {result['failed']} ")

                await asyncio.sleep(2)

    print(f"\n{'='*60}")
    print(f": {totals['cats']} , {totals['kws']} , {totals['imported']} , {totals['skipped']} , {totals['failed']} ")
    return totals

if __name__ == "__main__":
    platform = sys.argv[1] if len(sys.argv) > 1 else "amazon"
    ppk = int(sys.argv[2]) if len(sys.argv) > 2 else 3
    asyncio.run(run(platform, ppk))
