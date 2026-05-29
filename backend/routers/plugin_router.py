"""鎶€鑳藉競鍦?API 鈥?鎶€鑳芥敞鍐?涓嬭浇/瀹夎/鍗歌浇/閰嶇疆 v2锛?0+鐪熷疄鎶€鑳斤級"""
from fastapi import APIRouter, Depends, HTTPException
from auth import verify_token
from risk import handle_risk
from state import state
from tools.registry import registry as tool_registry, ToolDef
import datetime


router = APIRouter(prefix="/agent/plugins", tags=["Plugins"])

# ===== 鎶€鑳藉競鍦烘敞鍐岃〃 =====
SKILLS_MARKETPLACE = [
    # 鐩戞帶绫?
    {"id":"server-monitor","name":"馃搳 鏈嶅姟鍣ㄧ洃鎺?,"version":"2.0","desc":"CPU/鍐呭瓨/纾佺洏/杩涚▼/绔彛瀹炴椂鐩戞帶","author":"Friday","category":"鐩戞帶","stars":95,"downloads":1280,"tags":["server","monitor","cpu","memory"]},
    {"id":"docker-manager","name":"馃惓 Docker绠＄悊","version":"1.5","desc":"瀹瑰櫒鍏ㄧ敓鍛藉懆鏈熺鐞嗭細鍒楄〃/鏃ュ織/閲嶅惎/闀滃儚","author":"Friday","category":"鐩戞帶","stars":88,"downloads":960,"tags":["docker","container"]},
    {"id":"nginx-manager","name":"馃敡 Nginx绠＄悊","version":"1.3","desc":"Nginx鐘舵€?閰嶇疆/reload/鏃ュ織鏌ョ湅","author":"Friday","category":"鐩戞帶","stars":82,"downloads":720,"tags":["nginx","web"]},
    {"id":"site-checker","name":"馃寪 绔欑偣鐩戞帶","version":"1.1","desc":"澶氱珯鐐瑰彲鐢ㄦ€ф娴?SSL璇佷功鐩戞帶","author":"Friday","category":"鐩戞帶","stars":76,"downloads":540,"tags":["site","ssl","uptime"]},
    {"id":"alert-center","name":"馃敂 鍛婅涓績","version":"1.2","desc":"缁熶竴鍛婅绠＄悊锛氳鍒?閫氱煡/鍘嗗彶","author":"Friday","category":"鐩戞帶","stars":79,"downloads":610,"tags":["alert","notify"]},

    # 鑷姩鍖栫被
    {"id":"auto-backup","name":"馃捑 鑷姩澶囦唤","version":"1.0","desc":"瀹氭椂鏁版嵁搴?鏂囦欢鑷姩澶囦唤涓庢仮澶?,"author":"Friday","category":"鑷姩鍖?,"stars":91,"downloads":1100,"tags":["backup","cron"]},
    {"id":"scraper-engine","name":"馃暦锔?鍟嗗搧閲囬泦","version":"2.1","desc":"7骞冲彴鍟嗗搧鑷姩閲囬泦涓庡鍏?,"author":"Friday","category":"鑷姩鍖?,"stars":86,"downloads":890,"tags":["scraper","product","ebay"]},
    {"id":"auto-pilot","name":"馃 鑷姩杩愮淮","version":"1.2","desc":"AI鑷姩鎵ц鏃ュ父杩愮淮浠诲姟","author":"Friday","category":"鑷姩鍖?,"stars":83,"downloads":670,"tags":["ops","auto","cron"]},
    {"id":"cron-manager","name":"鈴?瀹氭椂浠诲姟","version":"1.0","desc":"鍙鍖朇ron浠诲姟绠＄悊/璋冨害","author":"Friday","category":"鑷姩鍖?,"stars":78,"downloads":520,"tags":["cron","schedule","timer"]},
    {"id":"batch-ops","name":"馃摝 鎵归噺鎿嶄綔","version":"1.1","desc":"鎵归噺澶勭悊鍟嗗搧/璁㈠崟/鏁版嵁","author":"Friday","category":"鑷姩鍖?,"stars":74,"downloads":430,"tags":["batch","bulk"]},

    # 瀹夊叏绫?
    {"id":"security-center","name":"馃洝锔?瀹夊叏涓績","version":"2.0","desc":"IP灏佺/鏉冮檺绠＄悊/瀹夊叏瀹¤","author":"Friday","category":"瀹夊叏","stars":90,"downloads":1050,"tags":["security","firewall","audit"]},
    {"id":"approval-flow","name":"鉁?瀹℃壒娴佺▼","version":"1.3","desc":"楂樺嵄鎿嶄綔瀹℃壒/澶氱骇瀹℃壒娴佺▼","author":"Friday","category":"瀹夊叏","stars":85,"downloads":780,"tags":["approval","review","audit"]},
    {"id":"risk-scanner","name":"鈿狅笍 椋庨櫓鎵弿","version":"1.1","desc":"鑷姩鎵弿绯荤粺瀹夊叏椋庨櫓","author":"Friday","category":"瀹夊叏","stars":77,"downloads":490,"tags":["risk","scan","vulnerability"]},
    {"id":"emergency-kill","name":"馃毃 鎬ユ晳寮€鍏?,"version":"1.0","desc":"涓€閿垏鏂瑼I鍐欐潈闄?绱ф€ユā寮忓垏鎹?,"author":"Friday","category":"瀹夊叏","stars":93,"downloads":1350,"tags":["emergency","kill","safety"]},

    # 鍟嗗煄绫?
    {"id":"mall-manager","name":"馃彧 鍟嗗煄绠＄悊","version":"3.0","desc":"142涓帴鍙ｈ鐩栧晢鍝?璁㈠崟/瀹㈡湇/璐㈠姟/钀ラ攢","author":"Friday","category":"鍟嗗煄","stars":97,"downloads":2100,"tags":["mall","shop","ecommerce"]},
    {"id":"mall-brain","name":"馃 AI澶ц剳","version":"1.5","desc":"AI鍟嗗搧鎵弿/杩愯惀鎶ュ憡/鑷姩鎵ц","author":"Friday","category":"鍟嗗煄","stars":89,"downloads":920,"tags":["ai","brain","analysis"]},
    {"id":"customer-service","name":"馃懃 瀹㈡湇绯荤粺","version":"1.2","desc":"宸ュ崟绠＄悊/鑷姩鍥炲/婊℃剰搴︾粺璁?,"author":"Friday","category":"鍟嗗煄","stars":80,"downloads":580,"tags":["cs","ticket","support"]},
    {"id":"marketing-tools","name":"馃摙 钀ラ攢宸ュ叿","version":"1.0","desc":"浼樻儬鍒?娲诲姩/鎺ㄩ€佺鐞?,"author":"Friday","category":"鍟嗗煄","stars":75,"downloads":450,"tags":["marketing","coupon","promo"]},
    {"id":"data-analytics","name":"馃搳 鏁版嵁鍒嗘瀽","version":"1.1","desc":"鍟嗗煄杩愯惀鏁版嵁鍒嗘瀽涓庢姤琛?,"author":"Friday","category":"鍟嗗煄","stars":81,"downloads":630,"tags":["analytics","report","stats"]},

    # AI/妯″瀷绫?
    {"id":"ai-chat","name":"馃挰 AI瀵硅瘽","version":"2.0","desc":"澶氭ā鍨婣I瀵硅瘽锛圤llama/DeepSeek/Claude/GPT锛?,"author":"Friday","category":"AI","stars":96,"downloads":3200,"tags":["chat","ai","llm"]},
    {"id":"vision-agent","name":"馃憗锔?瑙嗚璇嗗埆","version":"1.2","desc":"OCR鏂囧瓧璇嗗埆/鍥剧墖鍒嗘瀽/鐗╀綋妫€娴?,"author":"Friday","category":"AI","stars":84,"downloads":"760","tags":["ocr","vision","image"]},
    {"id":"trend-agent","name":"馃搱 瓒嬪娍鍒嗘瀽","version":"1.1","desc":"YouTube/X/Google澶氬钩鍙扮儹鐐硅秼鍔?,"author":"Friday","category":"AI","stars":79,"downloads":540,"tags":["trend","social","hot"]},
    {"id":"code-agent","name":"馃捇 浠ｇ爜鍔╂墜","version":"1.0","desc":"浠ｇ爜鍒嗘瀽/鐢熸垚/鎼滅储/API鐢熸垚","author":"Friday","category":"AI","stars":73,"downloads":390,"tags":["code","dev","api"]},
    {"id":"playwright-agent","name":"馃幁 娴忚鍣ㄨ嚜鍔ㄥ寲","version":"1.3","desc":"Playwright鎴浘/鎶撳彇/鎼滅储","author":"Friday","category":"AI","stars":87,"downloads":840,"tags":["playwright","browser","crawl"]},

    # 杞€?鍩熷悕绫?
    {"id":"rotation-system","name":"馃寪 鍩熷悕杞€?,"version":"2.0","desc":"浼佷笟绾у煙鍚嶈疆鍊?鍋ュ悍妫€娴?鑷姩鍒囨崲","author":"Friday","category":"缃戠粶","stars":92,"downloads":1150,"tags":["rotation","domain","dns"]},
    {"id":"ssl-manager","name":"馃敀 SSL璇佷功","version":"1.2","desc":"鑷姩绛惧彂/缁/鐘舵€佺洃鎺э紙acme.sh锛?,"author":"Friday","category":"缃戠粶","stars":86,"downloads":880,"tags":["ssl","cert","https"]},
    {"id":"dns-manager","name":"馃摗 DNS绠＄悊","version":"0.8","desc":"DNS瑙ｆ瀽璁板綍绠＄悊","author":"Friday","category":"缃戠粶","stars":68,"downloads":320,"tags":["dns","domain","resolve"]},

    # 寮€鍙戝伐鍏?
    {"id":"db-manager","name":"馃梽锔?鏁版嵁搴撶鐞?,"version":"1.1","desc":"MySQL鐘舵€?琛ㄧ粨鏋?鏌ヨ/浼樺寲","author":"Friday","category":"寮€鍙?,"stars":83,"downloads":710,"tags":["db","mysql","sql"]},
    {"id":"log-viewer","name":"馃搵 鏃ュ織鏌ョ湅","version":"1.0","desc":"闆嗕腑寮忕郴缁熸棩蹇楁煡鐪嬩笌鍒嗘瀽","author":"Friday","category":"寮€鍙?,"stars":76,"downloads":480,"tags":["log","debug","trace"]},
    {"id":"file-manager","name":"馃搧 鏂囦欢绠＄悊","version":"1.0","desc":"鏈嶅姟鍣ㄦ枃浠舵祻瑙?涓婁紶/涓嬭浇/缂栬緫","author":"Friday","category":"寮€鍙?,"stars":80,"downloads":560,"tags":["file","upload","manager"]},
    {"id":"api-explorer","name":"馃攲 API鎺㈢储","version":"0.9","desc":"API鎺ュ彛鏂囨。娴忚涓庢祴璇?,"author":"Friday","category":"寮€鍙?,"stars":72,"downloads":410,"tags":["api","docs","swagger"]},
    {"id":"git-manager","name":"馃摝 Git绠＄悊","version":"0.7","desc":"Git浠撳簱鐘舵€?鎻愪氦/鍒嗘敮绠＄悊","author":"Friday","category":"寮€鍙?,"stars":65,"downloads":280,"tags":["git","version","code"]},

    # 绀惧尯
    {"id":"team-collab","name":"馃懃 鍥㈤槦鍗忎綔","version":"0.6","desc":"澶氱敤鎴峰崗浣?鏉冮檺绠＄悊","author":"Friday","category":"绀惧尯","stars":60,"downloads":210,"tags":["team","user","collab"]},
    {"id":"skill-devkit","name":"馃О 鎶€鑳藉紑鍙戝寘","version":"0.5","desc":"鑷畾涔夋妧鑳藉紑鍙戝伐鍏峰寘/SDK","author":"Friday","category":"绀惧尯","stars":55,"downloads":150,"tags":["sdk","devkit","extend"]},
]

# ===== 鍒嗙被缁熻 =====
CATEGORIES = {}
for s in SKILLS_MARKETPLACE:
    cat = s["category"]
    if cat not in CATEGORIES:
        CATEGORIES[cat] = {"category": cat, "count": 0, "icon": s.get("icon", "馃摝")}
    CATEGORIES[cat]["count"] += 1


@router.get("")
async def list_plugins(_=Depends(verify_token)):
    """鑾峰彇鎵€鏈夊凡瀹夎鎶€鑳?""
    await handle_risk("L1", "鏌ョ湅鎶€鑳藉垪琛?)
    saved = state._data.get("plugins", [])
    merged = []
    for sp in SKILLS_MARKETPLACE:
        s = dict(sp)
        found = next((sv for sv in saved if sv["id"] == sp["id"]), None)
        s["installed"] = found is not None
        s["enabled"] = found.get("enabled", True) if found else False
        merged.append(s)
    return {"ok": True, "plugins": merged, "count": len(merged)}


@router.get("/marketplace")
async def market_plugins(category: str = "", search: str = "", _=Depends(verify_token)):
    """娴忚鎶€鑳藉競鍦?""
    await handle_risk("L1", "娴忚鎶€鑳藉競鍦?)
    saved = state._data.get("plugins", [])
    saved_ids = {s["id"] for s in saved}
    result = []
    for s in SKILLS_MARKETPLACE:
        if category and s["category"] != category:
            continue
        if search and search.lower() not in s["name"].lower() and search.lower() not in s["desc"].lower():
            continue
        item = dict(s)
        item["installed"] = s["id"] in saved_ids
        result.append(item)
    return {"ok": True, "skills": result, "count": len(result), "categories": list(CATEGORIES.values())}


@router.post("/install")
async def install_plugin(plugin_id: str, _=Depends(verify_token)):
    """瀹夎鎶€鑳斤紙娉ㄥ唽宸ュ叿鍒扮郴缁燂級"""
    await handle_risk("L2", f"瀹夎鎶€鑳?{plugin_id}")
    skill = next((s for s in SKILLS_MARKETPLACE if s["id"] == plugin_id), None)
    if not skill:
        raise HTTPException(404, f"鎶€鑳戒笉瀛樺湪: {plugin_id}")
    saved = state._data.setdefault("plugins", [])
    if any(s["id"] == plugin_id for s in saved):
        return {"ok": True, "plugin_id": plugin_id, "status": "already_installed"}
    saved.append({
        "id": plugin_id, "enabled": True,
        "installed_at": datetime.datetime.now().isoformat(),
    })
    state._save()
    # 娉ㄥ唽宸ュ叿鍒板伐鍏锋敞鍐屼腑蹇?
    _register_tools(plugin_id, skill)
    return {"ok": True, "plugin_id": plugin_id, "status": "installed", "skill": skill}


@router.post("/uninstall")
async def uninstall_plugin(plugin_id: str, _=Depends(verify_token)):
    """鍗歌浇鎶€鑳?""
    await handle_risk("L2", f"鍗歌浇鎶€鑳?{plugin_id}")
    saved = state._data.setdefault("plugins", [])
    state._data["plugins"] = [s for s in saved if s["id"] != plugin_id]
    state._save()
    return {"ok": True, "plugin_id": plugin_id, "uninstalled": True}


@router.post("/toggle")
async def toggle_plugin(plugin_id: str, enabled: bool, _=Depends(verify_token)):
    """鍚敤/绂佺敤鎶€鑳?""
    await handle_risk("L1", f"{'鍚敤' if enabled else '绂佺敤'}鎶€鑳?{plugin_id}")
    saved = state._data.setdefault("plugins", [])
    found = next((s for s in saved if s["id"] == plugin_id), None)
    if found:
        found["enabled"] = enabled
    else:
        saved.append({"id": plugin_id, "enabled": enabled})
    state._save()
    return {"ok": True, "plugin_id": plugin_id, "enabled": enabled}


@router.get("/categories")
async def list_categories(_=Depends(verify_token)):
    """鑾峰彇鎶€鑳藉垎绫?""
    return {"ok": True, "categories": list(CATEGORIES.values()), "total": len(SKILLS_MARKETPLACE)}


def _register_tools(plugin_id: str, skill: dict):
    """瀹夎鎶€鑳芥椂娉ㄥ唽瀵瑰簲宸ュ叿"""
    from tools.registry import registry
    tool_map = {
        "server-monitor": ["server.status","server.ports","server.processes","server.disk","server.cleanup"],
        "docker-manager": ["docker.ps","docker.logs","docker.status","docker.restart"],
        "nginx-manager": ["nginx.status","nginx.config","nginx.reload","nginx.test"],
        "rotation-system": ["rotation.domains","rotation.check","rotation.history","rotation.ssl"],
        "ssl-manager": ["ssl.status","ssl.issue","ssl.renew"],
        "mall-manager": ["mall.products","mall.orders","mall.customers","mall.finance"],
        "mall-brain": ["mallbrain.scan","mallbrain.report","mallbrain.auto","mallbrain.gaps"],
        "db-manager": ["db.status","db.tables","db.schema","db.query"],
        "security-center": ["security.scan","security.block","security.unblock"],
        "scraper-engine": ["scraper.start","scraper.jobs","scraper.products"],
        "playwright-agent": ["playwright.screenshot","playwright.scrape","playwright.search"],
        "emergency-kill": ["system.mode","system.emergency"],
        "ai-chat": ["agent.chat","agent.tools","agent.tasks"],
        "trend-agent": ["trend.get","trend.analyze","trend.predict"],
    }
    for tool_name in tool_map.get(plugin_id, []):
        if not registry.get(tool_name):
            registry.register(ToolDef(
                name=tool_name,
                display_name=skill["name"].split(" ", 1)[-1] if " " in skill["name"] else skill["name"],
                description=skill["desc"],
                risk_level="L1",
                category=skill["category"],
            ))

# ===== 鎶€鑳藉寘鍒嗗彂绯荤粺 =====
import os, json, tempfile
from tools.skill_loader import install_from_zip, uninstall, list_installed, create_skill_package

# 绀惧尯鎶€鑳藉競鍦猴紙绀轰緥鎶€鑳藉寘锛岀敤鎴峰彲鍙戝竷鑷繁鐨勶級
# 瀹為檯閮ㄧ讲鏃跺彲鏀逛负浠庤繙绋嬩粨搴撴媺鍙?
COMMUNITY_SKILLS = [
    {
        "id": "seo-optimizer",
        "name": "馃攳 SEO浼樺寲鍣?,
        "version": "1.0.0",
        "desc": "鑷姩鍒嗘瀽鍟嗗搧椤甸潰SEO锛岀敓鎴愪紭鍖栧缓璁紝鎻愬崌鎼滅储寮曟搸鎺掑悕",
        "author": "Friday绀惧尯",
        "category": "鍟嗗煄",
        "stars": 78,
        "downloads": 340,
        "tags": ["seo","optimize","rank"],
        "updated_at": "2026-05-28",
        "size_kb": 45,
        "readme": "瀹夎鍚庡湪AI瀵硅瘽涓緭鍏ャ€孲EO鍒嗘瀽 [鍟嗗搧ID]銆嶅嵆鍙娇鐢?
    },
    {
        "id": "price-predictor",
        "name": "馃搱 浠锋牸棰勬祴",
        "version": "0.9.0",
        "desc": "鍩轰簬鍘嗗彶鏁版嵁鍜屽競鍦鸿秼鍔匡紝AI棰勬祴鍟嗗搧鏈€浼樺畾浠风瓥鐣?,
        "author": "Friday绀惧尯",
        "category": "鍟嗗煄",
        "stars": 82,
        "downloads": 510,
        "tags": ["price","predict","strategy"],
        "updated_at": "2026-05-27",
        "size_kb": 62,
        "readme": "瀹夎鍚庤緭鍏ャ€屼环鏍奸娴?[鍟嗗搧ID]銆嶅嵆鍙娇鐢?
    },
    {
        "id": "wechat-push",
        "name": "馃挰 寰俊鎺ㄩ€?,
        "version": "1.2.0",
        "desc": "璁㈠崟鐘舵€佸彉鏇?搴撳瓨棰勮/绯荤粺鍛婅瀹炴椂鎺ㄩ€佷紒涓氬井淇?,
        "author": "Friday绀惧尯",
        "category": "閫氱煡",
        "stars": 90,
        "downloads": 1280,
        "tags": ["wechat","push","alert"],
        "updated_at": "2026-05-25",
        "size_kb": 28,
        "readme": "闇€鍦?env閰嶇疆WECOM_WEBHOOK锛屽畨瑁呭悗鑷姩娉ㄥ唽閫氱煡娓犻亾"
    },
    {
        "id": "log-analyzer",
        "name": "馃搵 鏃ュ織鍒嗘瀽鍣?,
        "version": "1.1.0",
        "desc": "鏅鸿兘鍒嗘瀽Nginx/MySQL/Python鏃ュ織锛岃嚜鍔ㄥ彂鐜板紓甯稿拰鎬ц兘鐡堕",
        "author": "Friday绀惧尯",
        "category": "寮€鍙?,
        "stars": 74,
        "downloads": 290,
        "tags": ["log","analyze","debug"],
        "updated_at": "2026-05-20",
        "size_kb": 38,
        "readme": "瀹夎鍚庡湪AI瀵硅瘽涓緭鍏ャ€屽垎鏋愭棩蹇?[绫诲瀷] [琛屾暟]銆?
    },
    {
        "id": "auto-translator",
        "name": "馃實 AI缈昏瘧瀹?,
        "version": "1.0.0",
        "desc": "鎵归噺缈昏瘧鍟嗗搧鏍囬/鎻忚堪鍒?0+璇█锛屼繚鐣橲EO鍏抽敭璇?,
        "author": "Friday绀惧尯",
        "category": "宸ュ叿",
        "stars": 86,
        "downloads": 760,
        "tags": ["translate","i18n","seo"],
        "updated_at": "2026-05-18",
        "size_kb": 52,
        "readme": "瀹夎鍚庡湪AI瀵硅瘽涓緭鍏ャ€岀炕璇?[鍟嗗搧ID] 鍒?[璇█]銆?
    },
    {
        "id": "screenshot-bot",
        "name": "馃摳 鎴浘鏈哄櫒浜?,
        "version": "1.0.0",
        "desc": "瀹氭椂鎴彇缃戦〉/绔炲搧椤甸潰蹇収锛岀洃鎺ч〉闈㈠彉鏇?,
        "author": "Friday绀惧尯",
        "category": "宸ュ叿",
        "stars": 71,
        "downloads": 210,
        "tags": ["screenshot","monitor","change"],
        "updated_at": "2026-05-15",
        "size_kb": 35,
        "readme": "瀹夎鍚庤緭鍏ャ€屾埅鍥剧洃鎺?[URL] 姣忓皬鏃躲€?
    },
]

# ==== GitHub Market ====
import os,json,httpx
_GITHUB_REPO=os.getenv("GITHUB_SKILLS_REPO","")
_GITHUB_TOKEN=os.getenv("GITHUB_TOKEN","")
async def _fetch_github_skills():
    if not _GITHUB_REPO: return []
    url=_GITHUB_REPO.rstrip("/")+"/index.json"
    headers={"User-Agent":"Friday-AI-OS"}
    if _GITHUB_TOKEN: headers["Authorization"]=f"token {_GITHUB_TOKEN}"
    try:
        async with httpx.AsyncClient(timeout=10) as cl:
            r=await cl.get(url,headers=headers)
            if r.status_code==200: return r.json()
    except: pass
    return []
async def _fetch_local_skills():
    import os as _os
    ld=_os.path.join(_os.path.dirname(_os.path.dirname(_os.path.abspath(__file__))),"..","..","scripts","friday-skills")
    ip=_os.path.join(ld,"index.json")
    if _os.path.exists(ip):
        try:
            with open(ip,"r",encoding="utf-8") as f: return json.load(f)
        except: pass
    return []

@router.get("/community")
async def community_skills(category: str = "", search: str = "", _=Depends(verify_token)):
    await handle_risk("L1","Browse community")
    skills=await _fetch_github_skills()
    if not skills: skills=await _fetch_local_skills()
    from tools.skill_loader import list_installed
    installed=list_installed()
    installed_ids={p.get("id") for p in installed}
    res=[]
    for s in skills:
        if category and s.get("category")!=category: continue
        if search and search.lower() not in s.get("name","").lower() and search.lower() not in s.get("desc","").lower(): continue
        item=dict(s);item["installed"]=s.get("id") in installed_ids
        if _GITHUB_REPO:
            repo=_GITHUB_REPO.replace("/contents/","/raw/main/")
            item["download_url"]=f"{repo}{s.get('path','')}.zip"
        res.append(item)
    return {"ok":True,"skills":res,"count":len(res),"installed_ids":list(installed_ids)}

@router.post("/community/install")
async def install_community_skill(skill_id:str,_=Depends(verify_token)):
    await handle_risk("L2",f"Install {skill_id}")
    skills=await _fetch_github_skills()
    if not skills: skills=await _fetch_local_skills()
    skill=next((s for s in skills if s["id"]==skill_id),None)
    if not skill: raise HTTPException(404,"Skill not found: "+skill_id)
    from tools.skill_loader import list_installed
    if any(p.get("id")==skill_id for p in list_installed()):
        return {"ok":True,"skill_id":skill_id,"status":"already_installed"}
    import tempfile,zipfile
    tmp=tempfile.NamedTemporaryFile(delete=False,suffix=".zip");tp=tmp.name;tmp.close()
    try:
        downloaded=False
        if _GITHUB_REPO:
            try:
                repo=_GITHUB_REPO.replace("/contents/","/raw/main/")
                zu=f"{repo}{skill.get('path','')}.zip"
                async with httpx.AsyncClient(timeout=30) as cl:
                    r=await cl.get(zu,headers={"User-Agent":"Friday-AI-OS"})
                    if r.status_code==200:
                        with open(tp,"wb") as f: f.write(r.content)
                        downloaded=True
            except: pass
        if not downloaded:
            import os as _os2
            ld=_os2.path.join(_os2.path.dirname(__file__),"..","..","scripts","friday-skills",skill.get("path",""))
            mp=_os2.path.join(ld,"skill.json")
            if not _os2.path.exists(mp):
                return {"ok":False,"error":"Skill package not available"}
            with zipfile.ZipFile(tp,"w",zipfile.ZIP_DEFLATED) as zf:
                zf.write(mp,"skill.json")
                mn=_os2.path.join(ld,"main.py")
                if _os2.path.exists(mn): zf.write(mn,"main.py")
        from tools.skill_loader import install_from_zip
        result=await install_from_zip(tp,source="community")
        if result.get("ok"):
            return {"ok":True,"skill_id":skill_id,"status":"installed","manifest":result.get("manifest")}
        return {"ok":False,"error":result.get("error","Install failed")}
    except Exception as e:
        return {"ok":False,"error":f"Install failed: {str(e)}"}
    finally:
        try: os.unlink(tp)
        except: pass

@router.post("/publish")
async def publish_skill(file: bytes = None, download_url: str = "", _=Depends(verify_token)):
    """鍙戝竷鎶€鑳斤紙涓婁紶 ZIP 鍖呮垨浠?URL 涓嬭浇锛?""
    await handle_risk("L2", "鍙戝竷鎶€鑳?)
    import tempfile

    if file:
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".zip")
        tmp.write(file)
        tmp_path = tmp.name
        tmp.close()
    elif download_url:
        import httpx
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".zip")
        tmp_path = tmp.name
        tmp.close()
        try:
            async with httpx.AsyncClient(timeout=60) as c:
                r = await c.get(download_url)
                with open(tmp_path, "wb") as f:
                    f.write(r.content)
        except Exception as e:
            os.unlink(tmp_path)
            return {"ok": False, "error": f"涓嬭浇澶辫触: {str(e)}"}
    else:
        return {"ok": False, "error": "璇蜂笂浼?ZIP 鏂囦欢鎴栨彁渚涗笅杞?URL"}

    try:
        result = await install_from_zip(tmp_path, source="upload")
        return result
    finally:
        try: os.unlink(tmp_path)
        except: pass


@router.get("/installed/packages")
async def installed_packages(_=Depends(verify_token)):
    """宸插畨瑁呯殑鎶€鑳藉寘鍒楄〃锛堝尯鍒簬鍐呯疆鎶€鑳斤級"""
    await handle_risk("L1", "鏌ョ湅宸插畨瑁呮妧鑳藉寘")
    skills = list_installed()
    return {"ok": True, "skills": skills, "count": len(skills)}


@router.post("/uninstall/{skill_id}")
async def uninstall_skill_package(skill_id: str, _=Depends(verify_token)):
    """鍗歌浇宸插畨瑁呯殑鎶€鑳藉寘"""
    await handle_risk("L2", f"鍗歌浇鎶€鑳藉寘 {skill_id}")
    result = await uninstall(skill_id)
    return result


@router.get("/installed/{skill_id}/readme")
async def skill_readme(skill_id: str, _=Depends(verify_token)):
    """鑾峰彇宸插畨瑁呮妧鑳界殑 README"""
    from tools.skill_loader import get_manifest
    manifest = get_manifest(skill_id)
    if not manifest:
        raise HTTPException(404, "鎶€鑳芥湭瀹夎")
    readme = manifest.get("readme", "鏆傛棤璇存槑鏂囨。")
    return {"ok": True, "skill_id": skill_id, "readme": readme}
