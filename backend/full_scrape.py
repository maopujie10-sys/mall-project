"""全品类采集 — 覆盖所有二级分类，采集后替换旧商品"""
import asyncio, sys, hashlib, time, gc, os, random
import psutil
sys.path.insert(0, ".")

# 内存安全配置（多进程分片模式）
MEMORY_LIMIT_PCT = 75
MEMORY_CHECK_INTERVAL = 20
SEARCH_DELAY_BASE = 0.08
SEARCH_DELAY_MAX = 10
PRODUCT_DELAY = 0.01
CONCURRENCY = 20           # 产品页并发数（单进程最大）
CATEGORY_PAUSE = 0.1
MAX_PAGES = 20             # 每个关键词搜索页数（深挖全量）
IMPORT_BATCH_SIZE = 30

SHARD_INDEX = 0
SHARD_TOTAL = 1
LOG_FILE = f"/tmp/full_scrape_{SHARD_INDEX}.log"

def _log(msg: str):
    """输出到stdout + 日志文件"""
    ts = time.strftime("%H:%M:%S")
    mem = psutil.virtual_memory()
    line = f"[{ts}] {msg} | 进程{psutil.Process().memory_info().rss//1024//1024}MB 系统{mem.percent:.1f}%"
    print(line, flush=True)
    with open(LOG_FILE, "a") as f:
        f.write(line + "\n")

# 已采集URL缓存(防重复)
seen_urls = set()

async def check_memory():
    """检查内存,超限则等待释放"""
    mem = psutil.virtual_memory()
    if mem.percent > MEMORY_LIMIT_PCT:
        print(f"\n[内存] {mem.percent}% > {MEMORY_LIMIT_PCT}%, 暂停30秒释放...", flush=True)
        gc.collect()
        await asyncio.sleep(30)
        mem = psutil.virtual_memory()
        print(f"[内存] 恢复: {mem.percent}%", flush=True)
    return mem.percent

# 每个二级分类 → Amazon搜索关键词
SUBCAT_KEYWORDS = {
    # Computer Peripherals
    "Computer Assembly Accessories": ["pc fan", "thermal paste", "sata cable"],
    "Desktop": ["desktop computer", "gaming pc", "all in one pc"],
    "Keyboard & Mouse": ["mechanical keyboard", "wireless mouse", "mouse pad"],
    "Laptop": ["laptop", "notebook computer", "chromebook"],
    "Monitor": ["computer monitor", "gaming monitor", "4k monitor"],
    "Networked Device": ["wifi router", "network switch", "mesh wifi"],
    "Printers & Scanners": ["printer", "document scanner", "label printer"],
    "Projectors & Accessories": ["projector", "mini projector", "projector screen"],
    "Tablet": ["tablet", "ipad case", "drawing tablet"],
    # Digital Products
    "Camera": ["digital camera", "dslr camera", "mirrorless camera"],
    "Camera Accessories": ["camera lens", "tripod", "camera bag", "sd card"],
    "Headphones & Headphones": ["wireless earbuds", "bluetooth headphones", "noise cancelling headphones"],
    "Home Theater System": ["soundbar", "home theater", "surround sound"],
    "Microphone": ["usb microphone", "wireless microphone", "condenser mic"],
    "Other Smart Devices": ["smart speaker", "smart plug", "smart light"],
    "Smart Tracker": ["bluetooth tracker", "airtag wallet", "gps tracker"],
    "Smart Watches & Accessories": ["smart watch", "apple watch band", "fitness tracker"],
    "Speaker": ["bluetooth speaker", "portable speaker", "bookshelf speaker"],
    "TV Box": ["streaming stick", "android tv box", "tv antenna"],
    "TVs & Accessories": ["tv wall mount", "hdmi cable", "tv remote"],
    "Video Game Equipment": ["gaming controller", "gaming headset", "nintendo switch"],
    # Phones & Accessories
    "Cell Phone": ["unlocked smartphone", "android phone", "rugged phone"],
    "Charger & Charging Cable": ["usb c charger", "lightning cable", "fast charger"],
    "Mobile Phone Holder": ["phone stand", "car phone mount", "desk phone holder"],
    "Mobile Phone Repair Tool": ["phone repair kit", "screen repair tool", "soldering kit"],
    "Mobile Power": ["power bank", "portable charger", "solar charger"],
    "Phone Cases & Cases": ["iphone case", "samsung case", "clear phone case"],
    "Photo & Pendant Accessories": ["phone lanyard", "phone charm", "pop socket"],
    "Screen Protector": ["screen protector", "tempered glass", "privacy screen"],
    # Home Appliances
    "Air Purifier": ["air purifier", "hepa filter", "air quality monitor"],
    "Cleaning Equipment": ["robot vacuum", "cordless vacuum", "steam mop"],
    "Fans & Air Conditioning Equipment": ["tower fan", "portable ac", "ceiling fan"],
    "Furniture Cupboard": ["storage cabinet", "bookshelf", "shoe rack"],
    "Home Appliance Accessories": ["vacuum bags", "water filter", "ac remote"],
    "Home Audio & Theater": ["record player", "bluetooth amplifier", "cd player"],
    "Kitchen Appliances": ["air fryer", "blender", "coffee maker", "toaster", "instant pot"],
    "Washing & Drying Appliances": ["portable washer", "clothes dryer", "laundry rack"],
    "Water Purification Equipment": ["water filter pitcher", "under sink filter", "water dispenser"],
    # Women's Clothing
    "Glasses & Sunglasses": ["sunglasses women", "cat eye glasses", "blue light glasses"],
    "Gloves": ["winter gloves women", "touch screen gloves", "leather gloves women"],
    "Ladies Coat": ["women coat", "winter jacket women", "trench coat women"],
    "Ladies Hat": ["bucket hat women", "beanie women", "sun hat women"],
    "Ladies Jeans": ["women jeans", "skinny jeans women", "high waist jeans"],
    "Ladies Pajamas": ["women pajamas", "silk pajamas women", "pajama set women"],
    "Ladies Shoes": ["women sneakers", "heels women", "flats women", "sandals women"],
    "Ladies Skirt": ["women skirt", "midi skirt", "mini skirt women"],
    "Ladies Suit": ["women blazer", "pantsuit women", "women suit set"],
    "Sock": ["women socks", "ankle socks", "compression socks"],
    "Underwear": ["women underwear", "bra set", "seamless underwear women"],
    "Women's Belts & Belts": ["women belt", "leather belt women", "waist belt women"],
    "Women's Shirt": ["women blouse", "white shirt women", "silk blouse women"],
    "Women's Shorts": ["women shorts", "denim shorts women", "biker shorts women"],
    "Women's Top": ["women t shirt", "women tank top", "crop top women"],
    "Women's Trousers": ["women pants", "wide leg pants", "dress pants women"],
    # Men's Clothing
    "Bow Tie": ["bow tie", "pre tied bow tie", "velvet bow tie"],
    "Glasses & Accessories": ["men sunglasses", "aviator sunglasses", "sport sunglasses"],
    "Men Belt": ["men belt", "leather belt men", "ratchet belt"],
    "Men's Bottoms": ["men pants", "chinos men", "cargo pants men"],
    "Men's Formal Wear": ["men dress shirt", "dress pants men", "formal vest"],
    "Men's Hat": ["baseball cap", "beanie men", "fedora hat men"],
    "Men's Jacket": ["men jacket", "bomber jacket men", "denim jacket men"],
    "Men's Leather Jacket": ["leather jacket men", "biker jacket", "suede jacket men"],
    "Men's Pajamas": ["men pajamas", "silk pajamas men", "cotton pajama men"],
    "Men's Shirts": ["men button shirt", "flannel shirt men", "linen shirt men"],
    "Men's Suits": ["men suit", "suit vest men", "blazer men"],
    "Men's T-shirt": ["men t shirt", "polo shirt men", "henley shirt men"],
    "Men's Tops": ["men hoodie", "men sweater", "men cardigan"],
    "Men's Underwear & Socks": ["boxer briefs", "men socks cotton", "compression shorts"],
    "Shoes For Men": ["men sneakers", "men dress shoes", "loafers men", "men boots"],
    "Sportswear": ["men gym shorts", "men tracksuit", "men sweatpants"],
    "Tie": ["neck tie", "skinny tie", "silk tie men"],
    # Health Beauty & Hair
    "Beauty Equipment": ["facial steamer", "led face mask", "microcurrent device"],
    "Cosmetic": ["foundation makeup", "eyeshadow palette", "mascara waterproof"],
    "Dental & Oral Care": ["electric toothbrush", "water flosser", "teeth whitening"],
    "Deodorants & Antiperspirants": ["deodorant stick", "clinical deodorant", "natural deodorant"],
    "Eyes & Eyelashes": ["eyeliner", "false eyelashes", "eyebrow pencil"],
    "Hair care & Styling": ["hair dryer", "flat iron", "curling wand"],
    "Health Care": ["vitamin supplement", "protein powder", "fish oil"],
    "Lipstick": ["lipstick set", "matte lipstick", "lip gloss"],
    "Makeup Tools": ["makeup brush set", "beauty blender", "makeup sponge"],
    "Nail Supplies": ["nail polish set", "gel nail kit", "nail art kit"],
    "Razor & Hair Removal": ["electric shaver", "hair removal cream", "wax kit"],
    "Skin Care": ["face moisturizer", "sunscreen spf", "vitamin c serum", "retinol cream"],
    "The Face": ["face wash", "face mask", "toner face"],
    # Jewelry & Watches
    "Anklet": ["anklet bracelet", "gold anklet", "beach anklet"],
    "Earrings": ["gold earrings", "hoop earrings", "stud earrings set"],
    "Jewelry": ["jewelry set", "statement necklace", "tennis bracelet"],
    "Jewelry Set": ["jewelry gift set", "bridal jewelry set", "pearl jewelry set"],
    "Keychains & Trinkets": ["keychain", "car keychain", "cute keychain"],
    "Ladies Bracelet": ["bracelet women", "gold bracelet women", "charm bracelet"],
    "Ladies Watch": ["women watch", "rose gold watch women", "leather watch women"],
    "Men's Watch": ["men watch", "chronograph watch", "dress watch men"],
    "Necklaces & Pendants": ["necklace women", "gold pendant", "silver chain necklace"],
    "Ring": ["ring set women", "engagement ring", "stackable rings"],
    "Tiaras & Brooches": ["tiara crown", "brooch pin", "hair crown"],
    # Kids & Babies
    "Baby & Mother": ["baby wrap carrier", "nursing pillow", "breast pump"],
    "Baby Clothes": ["baby onesies", "baby romper", "baby pajamas"],
    "Boy's Clothing": ["boys shirt", "boys pants", "boys hoodie"],
    "Boy's Jacket": ["boys winter jacket", "boys rain jacket", "boys fleece jacket"],
    "Boy's Pajamas": ["boys pajamas", "boys onesie pajama", "toddler boy pajamas"],
    "Boy's Pants": ["boys jeans", "boys joggers", "boys shorts"],
    "Boys Accessories": ["boys hat", "boys belt", "boys sunglasses"],
    "Boys Shoes": ["boys sneakers", "boys sandals", "boys boots"],
    "Boys Tops & T-Shirts": ["boys t shirt", "boys polo shirt", "boys long sleeve"],
    "Boys Underwear & Socks": ["boys underwear", "boys socks", "training pants"],
    "Children's Bag": ["kids backpack", "lunch bag kids", "kids suitcase"],
    "Girls Accessories": ["girls hair bow", "girls headband", "girls jewelry"],
    "Girls Clothing": ["girls dress", "girls leggings", "girls cardigan"],
    "Girls Jacket": ["girls winter coat", "girls denim jacket", "girls raincoat"],
    "Girls Pajamas": ["girls pajamas", "nightgown girls", "girls sleepwear"],
    "Girls Pants": ["girls jeans", "girls leggings cotton", "girls joggers"],
    "Girls Shoes": ["girls sneakers", "girls boots", "girls ballet flats"],
    "Girls Skirt": ["girls skirt", "tutu skirt", "pleated skirt girls"],
    "Girls Suit": ["girls outfit set", "girls formal dress", "flower girl dress"],
    "Girls Tops & T-Shirts": ["girls t shirt", "girls blouse", "girls tank top"],
    "Girls Underwear & Socks": ["girls underwear", "girls socks pack", "training bra"],
    "Milk powder": ["baby formula", "toddler milk powder", "organic baby formula"],
    # Kids Toys
    "Enlightenment Toys": ["montessori toys", "educational toys", "learning toys toddler"],
    "Metal Toys": ["metal toy car", "diecast cars", "metal puzzle"],
    "Plastic Toys": ["building blocks", "action figures", "dinosaur toys"],
    "Plush Toy": ["stuffed animal", "teddy bear", "plush doll"],
    "Wooden Toys": ["wooden blocks", "wooden puzzle", "wooden train set"],
    # Ladies Bag
    "Ladies Backpack": ["women backpack", "leather backpack women", "mini backpack women"],
    "Ladies Messenger Handbag": ["crossbody bag women", "messenger bag women", "sling bag women"],
    "Ladies Shoulder Bag": ["shoulder bag women", "hobo bag women", "satchel bag women"],
    "Ladies Wallet": ["women wallet", "rfid wallet women", "card holder women"],
    "Suitcase": ["luggage set", "carry on suitcase", "hard shell luggage"],
    # Men's Bag
    "Men's Backpack": ["men backpack", "laptop backpack men", "travel backpack men"],
    "Men's Briefcase": ["briefcase men", "leather briefcase", "attache case"],
    "Men's Shoulder Bag": ["sling bag men", "crossbody bag men", "chest bag men"],
    "Men's Wallet": ["men wallet", "rfid wallet men", "bifold wallet"],
    # Luxury
    "Art": ["wall art", "canvas painting", "modern art print"],
    "Bags": ["designer bag", "luxury handbag", "evening clutch"],
    "Clothing": ["cashmere sweater", "silk dress", "designer coat"],
    "Jewelry": ["diamond necklace", "pearl earrings", "gold chain"],
    "Watches": ["luxury watch", "automatic watch", "swiss watch"],
    # Office Stationery
    "Art Supplies": ["acrylic paint set", "sketchbook", "colored pencils"],
    "Calendar Goal Card": ["wall calendar", "planner notebook", "desk calendar"],
    "Desk Storage Classification": ["desk organizer", "file holder", "pen holder"],
    "Mail & Shipping Supplies": ["shipping envelopes", "packing tape", "bubble wrap"],
    "Office Accessories": ["stapler", "paper shredder", "laminator machine"],
    "Office Binding Supplies": ["binder clips", "paper clips", "rubber bands"],
    "Paper & Notebook": ["notebook journal", "printer paper", "sticky notes"],
    "Small Office Appliances": ["label maker", "paper cutter", "binding machine"],
    "Stationery Stickers & Labels": ["washi tape", "sticker pack", "label stickers"],
    "Tapes Adhesives and Fasteners": ["scotch tape", "super glue", "velcro strips"],
    "Writing & Correcting Supplies": ["gel pens", "fountain pen", "white out tape"],
    # Food & Beverage
    "Beer": ["craft beer", "beer glass set", "beer brewing kit"],
    "Carbonated Drinks": ["sparkling water", "soda maker", "coke glass bottle"],
    "Cocktail": ["cocktail shaker", "cocktail mixer", "margarita mix"],
    "Jilk Drink": ["almond milk", "oat milk", "coconut milk"],
    "Juice": ["orange juice", "cold press juicer", "apple juice organic"],
    "Liquor": ["whiskey", "vodka gift set", "rum premium"],
    "Mineral Water": ["mineral water", "sparkling mineral water", "water bottle glass"],
    "Tea": ["green tea", "tea gift set", "herbal tea sampler"],
    "Wine": ["red wine", "wine opener set", "wine glasses set"],
    # Sports & Outdoors
    "Bicycle Accessories": ["bike light", "bike lock", "bike helmet"],
    "Camping Equipment": ["camping tent", "sleeping bag", "camping stove"],
    "Fishing Gear": ["fishing rod", "fishing reel", "tackle box"],
    "Fitness & Bodybuilding": ["dumbbell set", "resistance bands", "yoga mat"],
    "Flashlight": ["led flashlight", "headlamp rechargeable", "tactical flashlight"],
    "Golf": ["golf balls", "golf glove", "golf club set"],
    "hiking & Rock Climbing": ["hiking boots", "hiking backpack", "climbing rope"],
    "Men's Sportswear": ["men compression shirt", "men running shorts", "dry fit shirt men"],
    "Outdoor Clothing & Shoes": ["hiking pants", "trail running shoes", "rain jacket"],
    "Outdoor Generator": ["portable generator", "solar generator", "power station"],
    "Outdoor Leisure": ["hammock", "folding chair", "cooler bag"],
    "Sports Protective Equipment": ["knee pads", "elbow pads", "mouth guard"],
    "Sportswear": ["yoga pants", "sports bra", "running jacket women"],
    "Travel Goods": ["travel pillow", "packing cubes", "luggage scale"],
    "Water Sports": ["swim goggles", "snorkel set", "dry bag"],
    "Winter Sports": ["ski goggles", "snow gloves", "ski mask"],
    # Epidemic Prevention Supplies
    "Alcohol & Sanitizers": ["hand sanitizer", "alcohol wipes", "surface disinfectant"],
    "Disposable Gloves": ["nitrile gloves", "disposable gloves box", "vinyl gloves"],
    "Goggles": ["safety goggles", "protective glasses", "lab goggles"],
    "Medical Mask": ["surgical mask", "n95 mask", "face mask disposable"],
    "Protective Suit": ["protective coverall", "disposable coverall", "hazmat suit"],
    "Thermometer": ["digital thermometer", "forehead thermometer", "infrared thermometer"],
    # Recreational Fishing Gear
    "Bait": ["fishing bait", "artificial bait", "soft plastic lure"],
    "Dip Net": ["landing net", "fishing dip net", "trout net"],
    "Fish Hook": ["fish hook set", "circle hook", "barbed hook"],
    "Fishing Box": ["tackle box waterproof", "fishing gear bag", "lure box"],
    "Fishing Line": ["braided fishing line", "fluorocarbon line", "monofilament line"],
    "Fishing Net": ["cast net", "fishing landing net", "bait net"],
    "Fishing Rod": ["spinning rod", "baitcasting rod", "telescopic fishing rod"],
    "Float": ["fishing float", "bobber set", "slip float"],
    "Lure": ["fishing lure set", "crankbait", "spinner bait"],
    "Sinker": ["fishing sinker", "lead sinker", "egg sinker"],
    # Snack Dessert
    "Cake": ["cake mix", "cake pan", "cake decorating kit"],
    "Dessert": ["chocolate truffle", "macaron gift box", "dessert topping"],
    "Ferky": ["beef jerky", "turkey jerky", "meat snack stick"],
    "Gluten": ["seitan", "gluten free flour", "vital wheat gluten"],
    "Jelly": ["fruit jelly", "jelly beans", "jello mix"],
    "Nut": ["mixed nuts", "almonds roasted", "cashew nuts", "pistachios"],
}

TOTAL = sum(len(v) for v in SUBCAT_KEYWORDS.values())

# 自动扩充关键词：中性修饰词+品牌，覆盖全量而非仅最新/最热
def expand_keywords(keywords):
    modifiers = ["best", "top rated", "cheap", "popular", "budget"]
    brands = ["logitech","samsung","sony","apple","anker","jbl","bose","dyson",
              "philips","dell","hp","lenovo","asus","acer","razer","corsair",
              "steelseries","hyperx","msi","gigabyte","intel","amd","nvidia"]
    result = list(keywords)
    for kw in keywords:
        for mod in modifiers:
            result.append(f"{mod} {kw}")
    for brand in random.sample(brands, min(8, len(brands))):
        for kw in keywords[:3]:
            result.append(f"{brand} {kw}")
    return list(dict.fromkeys(result))

for cat in SUBCAT_KEYWORDS:
    SUBCAT_KEYWORDS[cat] = expand_keywords(SUBCAT_KEYWORDS[cat])

TOTAL = sum(len(v) for v in SUBCAT_KEYWORDS.values())
print(f"覆盖 {len(SUBCAT_KEYWORDS)} 个子品类, {TOTAL} 个关键词(扩充后)")

CHECKPOINT_FILE = f"/tmp/full_scrape_checkpoint_{SHARD_INDEX}.json"

def load_checkpoint():
    import json
    if os.path.exists(CHECKPOINT_FILE):
        try:
            with open(CHECKPOINT_FILE) as f:
                return json.load(f)
        except Exception:
            pass
    return {"done_cats": [], "seen_urls": []}

def save_checkpoint(done_cats, seen_urls_sample):
    import json
    try:
        with open(CHECKPOINT_FILE, "w") as f:
            json.dump({"done_cats": list(done_cats),
                       "seen_urls": list(seen_urls_sample)[:5000]}, f)
    except Exception:
        pass

async def run(ppk=80):
    from tools.scraper_engine import ADAPTERS
    from tools.mall_importer import import_batch
    import httpx, random, hashlib, json
    from tools.scraper_engine import download_and_upload

    cp = load_checkpoint()
    done_cats = set(cp.get("done_cats", []))
    for u in cp.get("seen_urls", []):
        seen_urls.add(u)

    _log(f"===== 全品类采集 启动 =====")
    _log(f"品类数: {len(SUBCAT_KEYWORDS)} | 关键词数: {TOTAL} | 每品类目标: {ppk}")
    _log(f"搜索间隔: {SEARCH_DELAY_BASE}s(自适应) | 产品延迟: {PRODUCT_DELAY}s | 并发: {CONCURRENCY}")
    if done_cats:
        _log(f"断点续传: 跳过 {len(done_cats)} 个已完成品类")

    stats = {"cats": 0, "kws": 0, "found": 0, "imported": 0, "skipped": 0, "failed": 0}
    amazon_adapter = ADAPTERS["amazon"]
    ebay_adapter = ADAPTERS.get("ebay_html")
    search_delay = SEARCH_DELAY_BASE

    async with httpx.AsyncClient(timeout=30, follow_redirects=True, verify=False) as session:
        for subcat, keywords in SUBCAT_KEYWORDS.items():
            stats["cats"] += 1
            if subcat in done_cats:
                _log(f"[{stats['cats']}/{len(SUBCAT_KEYWORDS)}] {subcat} (已跳过)")
                continue
            if stats["cats"] > 1:
                _log(f"休息 {CATEGORY_PAUSE}s")
                gc.collect()
                await asyncio.sleep(CATEGORY_PAUSE)
            cat_imported = 0
            cat_kw = 0  # 本品类关键词计数
            dry_kws = 0
            _log(f"[{stats['cats']}/{len(SUBCAT_KEYWORDS)}] {subcat}")

            for kw in keywords:
                if stats["kws"] % MEMORY_CHECK_INTERVAL == 0:
                    await check_memory()
                if cat_imported >= ppk:
                    break
                # 已刮空品类跳过：3个关键词总计<5新品
                if cat_kw >= 3 and cat_imported < 5:
                    _log(f"  ⚡ {subcat} {cat_kw}关键词仅{cat_imported}新品，跳过")
                    break
                cat_kw += 1
                stats["kws"] += 1

                # ── 双平台搜索 ──
                all_fresh = []  # (platform_name, search_items)   items=URLs or itemIds
                need = ppk - cat_imported

                # Amazon
                await asyncio.sleep(search_delay)
                try:
                    amz_urls = await amazon_adapter.search(kw, max_pages=MAX_PAGES, session=session)
                except Exception as e:
                    _log(f"  [A] {kw}: search err {e}")
                    search_delay = min(search_delay * 1.3, SEARCH_DELAY_MAX)
                    amz_urls = []
                if amz_urls:
                    fresh = [u for u in amz_urls if u not in seen_urls]
                    for u in fresh:
                        seen_urls.add(u)
                    if fresh:
                        all_fresh.append(("amazon", fresh[:need+5]))
                    search_delay = max(SEARCH_DELAY_BASE, search_delay * 0.95)
                else:
                    search_delay = min(search_delay * 1.1, SEARCH_DELAY_MAX)

                # eBay
                if ebay_adapter and cat_imported < ppk:
                    await asyncio.sleep(0.3)
                    try:
                        ebay_ids = await ebay_adapter.search(kw, max_pages=MAX_PAGES, session=session)
                    except Exception:
                        ebay_ids = []
                    if ebay_ids:
                        fresh_ebay = [i for i in ebay_ids if i not in seen_urls]
                        for i in fresh_ebay:
                            seen_urls.add(i)
                        if fresh_ebay:
                            all_fresh.append(("ebay", fresh_ebay[:15]))

                if not all_fresh:
                    continue

                # 并发提取+批量下载+批量导入
                for platform, items in all_fresh:
                    if cat_imported >= ppk:
                        break
                    adapter = amazon_adapter if platform == "amazon" else ebay_adapter
                    products = await adapter.extract_concurrent(
                        items[:need+5], session=session, concurrency=CONCURRENCY
                    )
                    for p in products:
                        p.id = hashlib.md5(p.source_url.encode()).hexdigest()[:16]

                    if not products:
                        continue

                    # 限制COS并发连接数，所有产品图片并发下载
                    dl_sem = asyncio.Semaphore(12)
                    async def _dl_limited(img_url, idx, pid):
                        async with dl_sem:
                            try:
                                return await download_and_upload(img_url, pid, idx, session)
                            except Exception:
                                return None

                    dl_results = await asyncio.gather(*[_dl_limited(u, i, p.id)
                        for p in products[:need]
                        for i, u in enumerate(p.images[:3])], return_exceptions=True)

                    # 将结果分配回各产品，收集可入库的
                    dl_idx = 0
                    ready_products = []
                    for p in products[:need]:
                        uploaded = []
                        for i in range(min(3, len(p.images))):
                            r = dl_results[dl_idx]
                            dl_idx += 1
                            if isinstance(r, str) and r:
                                uploaded.append(r)
                        if not uploaded:
                            continue
                        p.cos_images = uploaded
                        ready_products.append(p)

                    # 分批入库，控制每批内存
                    imported_now = 0
                    review_total = 0
                    sku_total = 0
                    for batch_start in range(0, len(ready_products), IMPORT_BATCH_SIZE):
                        batch_products = ready_products[batch_start:batch_start+IMPORT_BATCH_SIZE]
                        batch_dicts = [p.to_dict() for p in batch_products]
                        result = import_batch(batch_dicts, subcat_name=subcat)
                        imported_now += result["imported"]
                        stats["imported"] += result["imported"]
                        stats["skipped"] += result["skipped_duplicate"]
                        stats["failed"] += result["failed"]
                        for d in (result.get("details", {}).get("imported", []) or []):
                            review_total += d.get("reviews_count", 0)
                            sku_total += d.get("skus_count", 0)
                        # 子批次间释放引用
                        del batch_products, batch_dicts

                    cat_imported += imported_now
                    tag = "[A]" if platform == "amazon" else "[e]"
                    _log(f"  {tag} +{imported_now}新品 | 评论{review_total} SKU{sku_total}")
                    need = ppk - cat_imported

                # 追踪低产关键词
                if imported_now == 0:
                    dry_kws += 1
                else:
                    dry_kws = 0

                await asyncio.sleep(PRODUCT_DELAY)

            if cat_imported == 0:
                _log(f"  ⚠️ {subcat} 未采集到")
            elif cat_imported >= ppk:
                done_cats.add(subcat)
                save_checkpoint(done_cats, list(seen_urls)[:5000])

    _log(f"===== 完成 =====")
    _log(f"上架 {stats['imported']} | 重复 {stats['skipped']} | 失败 {stats['failed']}")
    _log(f"覆盖 {stats['cats']} 子品类, {stats['kws']} 关键词搜索")
    return stats

if __name__ == "__main__":
    ppk = 150
    shard_idx = 0
    shard_total = 1
    args = sys.argv[1:]
    i = 0
    while i < len(args):
        if args[i] == "--shard" and i+2 < len(args):
            shard_idx = int(args[i+1])
            shard_total = int(args[i+2])
            i += 3
        else:
            try:
                ppk = int(args[i])
            except ValueError:
                pass
            i += 1

    # 分片：抽取该进程负责的品类
    import itertools
    cats = list(SUBCAT_KEYWORDS.items())
    shard_cats = dict(cats[shard_idx::shard_total])
    SUBCAT_KEYWORDS.clear()
    SUBCAT_KEYWORDS.update(shard_cats)
    TOTAL = sum(len(v) for v in SUBCAT_KEYWORDS.values())

    # 更新分片相关的全局变量(必须通过__main__，因为直接运行时模块名不是full_scrape)
    main_mod = sys.modules["__main__"]
    main_mod.SHARD_INDEX = shard_idx
    main_mod.SHARD_TOTAL = shard_total
    main_mod.LOG_FILE = f"/tmp/full_scrape_{shard_idx}.log"
    main_mod.CHECKPOINT_FILE = f"/tmp/full_scrape_checkpoint_{shard_idx}.json"

    print(f"Shard {shard_idx}/{shard_total}: {len(SUBCAT_KEYWORDS)} 品类, {TOTAL} 关键词, 目标{ppk}/品类")
    asyncio.run(run(ppk))
