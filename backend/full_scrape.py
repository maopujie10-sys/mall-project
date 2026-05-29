"""全品类采集 — 覆盖所有二级分类，采集后替换旧商品"""
import asyncio, sys, hashlib, time, gc, os, random
import psutil
sys.path.insert(0, ".")

# 内存安全配置
MEMORY_LIMIT_PCT = 80     # 内存超此比例暂停
MEMORY_CHECK_INTERVAL = 10 # 每N个关键词检查一次内存
SEARCH_DELAY_BASE = 8      # 搜索基础间隔秒(自适应:遇429加倍)
SEARCH_DELAY_MAX = 60      # 搜索最大间隔秒
PRODUCT_DELAY = 3          # 产品并发批间隔秒
CONCURRENCY = 3            # 产品页并发数
CATEGORY_PAUSE = 30        # 每完成一个分类暂停秒

LOG_FILE = "/tmp/full_scrape.log"

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
print(f"覆盖 {len(SUBCAT_KEYWORDS)} 个子品类, {TOTAL} 个关键词")

async def run(ppk=5):
    from tools.scraper_engine import ADAPTERS
    from tools.mall_importer import import_batch
    import httpx, random, hashlib
    from tools.scraper_engine import download_and_upload

    _log(f"===== 全品类采集 启动 =====")
    _log(f"品类数: {len(SUBCAT_KEYWORDS)} | 关键词数: {TOTAL} | 每品类目标: {ppk}")
    _log(f"搜索间隔: {SEARCH_DELAY_BASE}s(自适应) | 产品延迟: {PRODUCT_DELAY}s | 并发: {CONCURRENCY}")

    stats = {"cats": 0, "kws": 0, "found": 0, "imported": 0, "skipped": 0, "failed": 0}
    amazon_adapter = ADAPTERS["amazon"]
    ebay_adapter = ADAPTERS.get("ebay_html")
    search_delay = SEARCH_DELAY_BASE

    async with httpx.AsyncClient(timeout=30, follow_redirects=True, verify=False) as session:
        for subcat, keywords in SUBCAT_KEYWORDS.items():
            stats["cats"] += 1
            if stats["cats"] > 1:
                _log(f"休息 {CATEGORY_PAUSE}s")
                gc.collect()
                await asyncio.sleep(CATEGORY_PAUSE)
            cat_imported = 0
            _log(f"[{stats['cats']}/{len(SUBCAT_KEYWORDS)}] {subcat}")

            for kw in keywords:
                if stats["kws"] % MEMORY_CHECK_INTERVAL == 0:
                    await check_memory()
                if cat_imported >= ppk:
                    break
                stats["kws"] += 1

                # ── 双平台搜索 ──
                all_fresh = []  # (platform_name, search_items)   items=URLs or itemIds
                need = ppk - cat_imported

                # Amazon
                await asyncio.sleep(search_delay)
                try:
                    amz_urls = await amazon_adapter.search(kw, max_pages=1, session=session)
                except Exception as e:
                    _log(f"  [Amazon] {kw}: 搜索异常 {e}")
                    search_delay = min(search_delay * 1.3, SEARCH_DELAY_MAX)
                    amz_urls = []
                if amz_urls:
                    fresh = [u for u in amz_urls[:need+2] if u not in seen_urls]
                    for u in fresh:
                        seen_urls.add(u)
                    if fresh:
                        all_fresh.append(("amazon", fresh))
                    search_delay = max(SEARCH_DELAY_BASE, search_delay * 0.95)
                else:
                    search_delay = min(search_delay * 1.1, SEARCH_DELAY_MAX)

                # eBay (补充，每关键词限5个itemId)
                if ebay_adapter and cat_imported < ppk:
                    await asyncio.sleep(2)  # eBay API短间隔
                    try:
                        ebay_ids = await ebay_adapter.search(kw, max_pages=1, session=session)
                    except Exception:
                        ebay_ids = []
                    if ebay_ids:
                        fresh_ebay = [i for i in ebay_ids[:5] if i not in seen_urls]
                        for i in fresh_ebay:
                            seen_urls.add(i)
                        if fresh_ebay:
                            all_fresh.append(("ebay", fresh_ebay))

                if not all_fresh:
                    _log(f"  {kw}: 双平台0结果")
                    continue

                # ── 并发提取+导入 ──
                for platform, items in all_fresh:
                    if cat_imported >= ppk:
                        break
                    adapter = amazon_adapter if platform == "amazon" else ebay_adapter
                    products = await adapter.extract_concurrent(
                        items[:need+2], session=session, concurrency=CONCURRENCY
                    )
                    for p in products:
                        p.id = hashlib.md5(p.source_url.encode()).hexdigest()[:16]

                    if not products:
                        continue

                    imported_now = 0
                    review_total = 0
                    sku_total = 0
                    for p in products[:need]:
                        uploaded = []
                        async def _dl(img_url, idx):
                            try:
                                return await download_and_upload(img_url, p.id, idx, session)
                            except Exception:
                                return img_url
                        tasks = [_dl(u, i) for i, u in enumerate(p.images[:8])]
                        results = await asyncio.gather(*tasks, return_exceptions=True)
                        for r in results:
                            if isinstance(r, str) and r:
                                uploaded.append(r)
                        p.cos_images = uploaded
                        if not uploaded:
                            continue

                        pd_dict = p.to_dict()
                        result = import_batch([pd_dict], subcat_name=subcat)
                        if result["imported"]:
                            imported_now += 1
                            stats["imported"] += 1
                            detail = result["details"]["imported"][0] if result["details"]["imported"] else {}
                            review_total += detail.get("reviews_count", 0)
                            sku_total += detail.get("skus_count", 0)
                        elif result["skipped_duplicate"]:
                            stats["skipped"] += 1
                        else:
                            stats["failed"] += 1

                    cat_imported += imported_now
                    tag = "[A]" if platform == "amazon" else "[e]"
                    _log(f"  {tag} +{imported_now}新品 | 评论{review_total} SKU{sku_total}")
                    need = ppk - cat_imported

                await asyncio.sleep(PRODUCT_DELAY)

            if cat_imported == 0:
                _log(f"  ⚠️ {subcat} 未采集到")

    _log(f"===== 完成 =====")
    _log(f"上架 {stats['imported']} | 重复 {stats['skipped']} | 失败 {stats['failed']}")
    _log(f"覆盖 {stats['cats']} 子品类, {stats['kws']} 关键词搜索")
    return stats

if __name__ == "__main__":
    ppk = int(sys.argv[1]) if len(sys.argv) > 1 else 5
    asyncio.run(run(ppk))
