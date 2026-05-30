''" API -- //// v2(30+)''"
from fastapi import APIRouter, Depends, HTTPException
from auth import verify_token
from risk import handle_risk
from state import state
from tools.registry import registry as tool_registry, ToolDef
import datetime


router = APIRouter(prefix="/agent/plugins", tags=["Plugins"])

# =====  =====
SKILLS_MARKETPLACE = [
    
    {"id":"server-monitor","name":" ","version":"2.0","desc":"CPU////","author":"Friday","category":'',"stars":95,"downloads":1280,"tags":["server","monitor","cpu","memory"]},
    {"id":"docker-manager","name":" Docker","version":"1.5","desc":":///","author":"Friday","category":'',"stars":88,"downloads":960,"tags":["docker","container"]},
    {"id":"nginx-manager","name":" Nginx","version":"1.3","desc":"Nginx//reload/","author":"Friday","category":'',"stars":82,"downloads":720,"tags":["nginx","web"]},
    {"id":"site-checker","name":" ","version":"1.1","desc":"/SSL","author":"Friday","category":'',"stars":76,"downloads":540,"tags":["site","ssl","uptime"]},
    {"id":"alert-center","name":" ","version":"1.2","desc":"://","author":"Friday","category":'',"stars":79,"downloads":610,"tags":["alert","notify"]},

    
    {"id":"auto-backup","name":" ","version":"1.0","desc":"/","author":"Friday","category":'',"stars":91,"downloads":1100,"tags":["backup","cron"]},
    {"id":"scraper-engine","name":" ","version":"2.1","desc":"7","author":"Friday","category":'',"stars":86,"downloads":890,"tags":["scraper","product","ebay"]},
    {"id":"auto-pilot","name":" ","version":"1.2","desc":"AI","author":"Friday","category":'',"stars":83,"downloads":670,"tags":["ops","auto","cron"]},
    {"id":"cron-manager","name":" ","version":"1.0","desc":"Cron/","author":"Friday","category":'',"stars":78,"downloads":520,"tags":["cron","schedule","timer"]},
    {"id":"batch-ops","name":" ","version":"1.1","desc":"//","author":"Friday","category":'',"stars":74,"downloads":430,"tags":["batch","bulk"]},

    
    {"id":"security-center","name":" ","version":"2.0","desc":"IP//","author":"Friday","category":'',"stars":90,"downloads":1050,"tags":["security","firewall","audit"]},
    {"id":"approval-flow","name":" ","version":"1.3","desc":"/","author":"Friday","category":'',"stars":85,"downloads":780,"tags":["approval","review","audit"]},
    {"id":"risk-scanner","name":" ","version":"1.1","desc":'',"author":"Friday","category":'',"stars":77,"downloads":490,"tags":["risk","scan","vulnerability"]},
    {"id":"emergency-kill","name":" ","version":"1.0","desc":"AI/","author":"Friday","category":'',"stars":93,"downloads":1350,"tags":["emergency","kill","safety"]},

    
    {"id":"mall-manager","name":" ","version":"3.0","desc":"142////","author":"Friday","category":'',"stars":97,"downloads":2100,"tags":["mall","shop","ecommerce"]},
    {"id":"mall-brain","name":" AI","version":"1.5","desc":"AI//","author":"Friday","category":'',"stars":89,"downloads":920,"tags":["ai","brain","analysis"]},
    {"id":"customer-service","name":" ","version":"1.2","desc":"//","author":"Friday","category":'',"stars":80,"downloads":580,"tags":["cs","ticket","support"]},
    {"id":"marketing-tools","name":" ","version":"1.0","desc":"//","author":"Friday","category":'',"stars":75,"downloads":450,"tags":["marketing","coupon","promo"]},
    {"id":"data-analytics","name":" ","version":"1.1","desc":'',"author":"Friday","category":'',"stars":81,"downloads":630,"tags":["analytics","report","stats"]},

    # AI/
    {"id":"ai-chat","name":" AI","version":"2.0","desc":"AI(Ollama/DeepSeek/Claude/GPT)","author":"Friday","category":"AI","stars":96,"downloads":3200,"tags":["chat","ai","llm"]},
    {"id":"vision-agent","name":" ","version":"1.2","desc":"OCR//","author":"Friday","category":"AI","stars":84,"downloads":"760","tags":["ocr","vision","image"]},
    {"id":"trend-agent","name":" ","version":"1.1","desc":"YouTube/X/Google","author":"Friday","category":"AI","stars":79,"downloads":540,"tags":["trend","social","hot"]},
    {"id":"code-agent","name":" ","version":"1.0","desc":"///API","author":"Friday","category":"AI","stars":73,"downloads":390,"tags":["code","dev","api"]},
    {"id":"playwright-agent","name":" ","version":"1.3","desc":"Playwright//","author":"Friday","category":"AI","stars":87,"downloads":840,"tags":["playwright","browser","crawl"]},

    # /
    {"id":"rotation-system","name":" ","version":"2.0","desc":"//","author":"Friday","category":'',"stars":92,"downloads":1150,"tags":["rotation","domain","dns"]},
    {"id":"ssl-manager","name":" SSL","version":"1.2","desc":"//(acme.sh)","author":"Friday","category":'',"stars":86,"downloads":880,"tags":["ssl","cert","https"]},
    {"id":"dns-manager","name":" DNS","version":"0.8","desc":"DNS","author":"Friday","category":'',"stars":68,"downloads":320,"tags":["dns","domain","resolve"]},

    
    {"id":"db-manager","name":" ","version":"1.1","desc":"MySQL///","author":"Friday","category":'',"stars":83,"downloads":710,"tags":["db","mysql","sql"]},
    {"id":"log-viewer","name":" ","version":"1.0","desc":'',"author":"Friday","category":'',"stars":76,"downloads":480,"tags":["log","debug","trace"]},
    {"id":"file-manager","name":" ","version":"1.0","desc":"///","author":"Friday","category":'',"stars":80,"downloads":560,"tags":["file","upload","manager"]},
    {"id":"api-explorer","name":" API","version":"0.9","desc":"API","author":"Friday","category":'',"stars":72,"downloads":410,"tags":["api","docs","swagger"]},
    {"id":"git-manager","name":" Git","version":"0.7","desc":"Git//","author":"Friday","category":'',"stars":65,"downloads":280,"tags":["git","version","code"]},

    
    {"id":"team-collab","name":" ","version":"0.6","desc":"/","author":"Friday","category":'',"stars":60,"downloads":210,"tags":["team","user","collab"]},
    {"id":"skill-devkit","name":" ","version":"0.5","desc":"/SDK","author":"Friday","category":'',"stars":55,"downloads":150,"tags":["sdk","devkit","extend"]},
]

# =====  =====
CATEGORIES = {}
for s in SKILLS_MARKETPLACE:
    cat = s["category"]
    if cat not in CATEGORIES:
        CATEGORIES[cat] = {"category": cat, "count": 0, "icon": s.get("icon", "")}
    CATEGORIES[cat]["count"] += 1


@router.get('')
async def list_plugins(_=Depends(verify_token)):
    ''''''
    await handle_risk("L1", '')
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
async def market_plugins(category: str = '', search: str = '', _=Depends(verify_token)):
    ''''''
    await handle_risk("L1", '')
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
    ''"()''"
    await handle_risk("L2", f" {plugin_id}")
    skill = next((s for s in SKILLS_MARKETPLACE if s["id"] == plugin_id), None)
    if not skill:
        raise HTTPException(404, f": {plugin_id}")
    saved = state._data.setdefault("plugins", [])
    if any(s["id"] == plugin_id for s in saved):
        return {"ok": True, "plugin_id": plugin_id, "status": "already_installed"}
    saved.append({
        "id": plugin_id, "enabled": True,
        "installed_at": datetime.datetime.now().isoformat(),
    })
    state._save()
    
    _register_tools(plugin_id, skill)
    return {"ok": True, "plugin_id": plugin_id, "status": "installed", "skill": skill}


@router.post("/uninstall")
async def uninstall_plugin(plugin_id: str, _=Depends(verify_token)):
    ''''''
    await handle_risk("L2", f" {plugin_id}")
    saved = state._data.setdefault("plugins", [])
    state._data["plugins"] = [s for s in saved if s["id"] != plugin_id]
    state._save()
    return {"ok": True, "plugin_id": plugin_id, "uninstalled": True}


@router.post("/toggle")
async def toggle_plugin(plugin_id: str, enabled: bool, _=Depends(verify_token)):
    ''"/''"
    await handle_risk("L1", f"{'' if enabled else ''} {plugin_id}")
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
    ''''''
    return {"ok": True, "categories": list(CATEGORIES.values()), "total": len(SKILLS_MARKETPLACE)}


def _register_tools(plugin_id: str, skill: dict):
    ''''''
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
                display_name=skill["name"].split('', 1)[-1] if '' in skill["name"] else skill["name"],
                description=skill["desc"],
                risk_level="L1",
                category=skill["category"],
            ))

# =====  =====
import os, json, tempfile
from tools.skill_loader import install_from_zip, uninstall, list_installed, create_skill_package

# (,)

COMMUNITY_SKILLS = [
    {
        "id": "seo-optimizer",
        "name": " SEO",
        "version": "1.0.0",
        "desc": "SEO,",
        "author": "Friday",
        "category": '',
        "stars": 78,
        "downloads": 340,
        "tags": ["seo","optimize","rank"],
        "updated_at": "2026-05-28",
        "size_kb": 45,
        "readme": "AISEO [ID]"
    },
    {
        "id": "price-predictor",
        "name": " ",
        "version": "0.9.0",
        "desc": ",AI",
        "author": "Friday",
        "category": '',
        "stars": 82,
        "downloads": 510,
        "tags": ["price","predict","strategy"],
        "updated_at": "2026-05-27",
        "size_kb": 62,
        "readme": " [ID]"
    },
    {
        "id": "wechat-push",
        "name": " ",
        "version": "1.2.0",
        "desc": "//",
        "author": "Friday",
        "category": '',
        "stars": 90,
        "downloads": 1280,
        "tags": ["wechat","push","alert"],
        "updated_at": "2026-05-25",
        "size_kb": 28,
        "readme": ".envWECOM_WEBHOOK,"
    },
    {
        "id": "log-analyzer",
        "name": " ",
        "version": "1.1.0",
        "desc": "Nginx/MySQL/Python,",
        "author": "Friday",
        "category": '',
        "stars": 74,
        "downloads": 290,
        "tags": ["log","analyze","debug"],
        "updated_at": "2026-05-20",
        "size_kb": 38,
        "readme": "AI [] []"
    },
    {
        "id": "auto-translator",
        "name": " AI",
        "version": "1.0.0",
        "desc": "/50+,SEO",
        "author": "Friday",
        "category": '',
        "stars": 86,
        "downloads": 760,
        "tags": ["translate","i18n","seo"],
        "updated_at": "2026-05-18",
        "size_kb": 52,
        "readme": "AI [ID]  []"
    },
    {
        "id": "screenshot-bot",
        "name": " ",
        "version": "1.0.0",
        "desc": "/,",
        "author": "Friday",
        "category": '',
        "stars": 71,
        "downloads": 210,
        "tags": ["screenshot","monitor","change"],
        "updated_at": "2026-05-15",
        "size_kb": 35,
        "readme": " [URL] "
    },
]

# ==== GitHub Market ====
import os,json,httpx
_GITHUB_REPO=os.getenv("GITHUB_SKILLS_REPO",'')
_GITHUB_TOKEN=os.getenv("GITHUB_TOKEN",'')
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
async def community_skills(category: str = '', search: str = '', _=Depends(verify_token)):
    await handle_risk("L1","Browse community")
    skills=await _fetch_github_skills()
    if not skills: skills=await _fetch_local_skills()
    from tools.skill_loader import list_installed
    installed=list_installed()
    installed_ids={p.get("id") for p in installed}
    res=[]
    for s in skills:
        if category and s.get("category")!=category: continue
        if search and search.lower() not in s.get("name",'').lower() and search.lower() not in s.get("desc",'').lower(): continue
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
            ld=_os2.path.join(_os2.path.dirname(__file__),"..","..","scripts","friday-skills",skill.get("path",''))
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
async def publish_skill(file: bytes = None, download_url: str = '', _=Depends(verify_token)):
    ''"( ZIP  URL )''"
    await handle_risk("L2", '')
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
            return {"ok": False, "error": f": {str(e)}"}
    else:
        return {"ok": False, "error": " ZIP  URL"}

    try:
        result = await install_from_zip(tmp_path, source="upload")
        return result
    finally:
        try: os.unlink(tmp_path)
        except: pass


@router.get("/installed/packages")
async def installed_packages(_=Depends(verify_token)):
    ''"()''"
    await handle_risk("L1", '')
    skills = list_installed()
    return {"ok": True, "skills": skills, "count": len(skills)}


@router.post("/uninstall/{skill_id}")
async def uninstall_skill_package(skill_id: str, _=Depends(verify_token)):
    ''''''
    await handle_risk("L2", f" {skill_id}")
    result = await uninstall(skill_id)
    return result


@router.get("/installed/{skill_id}/readme")
async def skill_readme(skill_id: str, _=Depends(verify_token)):
    ''" README''"
    from tools.skill_loader import get_manifest
    manifest = get_manifest(skill_id)
    if not manifest:
        raise HTTPException(404, '')
    readme = manifest.get("readme", '')
    return {"ok": True, "skill_id": skill_id, "readme": readme}
