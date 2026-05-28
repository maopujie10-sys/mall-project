"""技能市场 API — 技能注册/下载/安装/卸载/配置 v2（30+真实技能）"""
from fastapi import APIRouter, Depends, HTTPException
from auth import verify_token
from risk import handle_risk
from state import state
from tools.registry import registry as tool_registry, ToolDef
import datetime


router = APIRouter(prefix="/agent/plugins", tags=["Plugins"])

# ===== 技能市场注册表 =====
SKILLS_MARKETPLACE = [
    # 监控类
    {"id":"server-monitor","name":"📊 服务器监控","version":"2.0","desc":"CPU/内存/磁盘/进程/端口实时监控","author":"Friday","category":"监控","stars":95,"downloads":1280,"tags":["server","monitor","cpu","memory"]},
    {"id":"docker-manager","name":"🐳 Docker管理","version":"1.5","desc":"容器全生命周期管理：列表/日志/重启/镜像","author":"Friday","category":"监控","stars":88,"downloads":960,"tags":["docker","container"]},
    {"id":"nginx-manager","name":"🔧 Nginx管理","version":"1.3","desc":"Nginx状态/配置/reload/日志查看","author":"Friday","category":"监控","stars":82,"downloads":720,"tags":["nginx","web"]},
    {"id":"site-checker","name":"🌐 站点监控","version":"1.1","desc":"多站点可用性检测/SSL证书监控","author":"Friday","category":"监控","stars":76,"downloads":540,"tags":["site","ssl","uptime"]},
    {"id":"alert-center","name":"🔔 告警中心","version":"1.2","desc":"统一告警管理：规则/通知/历史","author":"Friday","category":"监控","stars":79,"downloads":610,"tags":["alert","notify"]},

    # 自动化类
    {"id":"auto-backup","name":"💾 自动备份","version":"1.0","desc":"定时数据库/文件自动备份与恢复","author":"Friday","category":"自动化","stars":91,"downloads":1100,"tags":["backup","cron"]},
    {"id":"scraper-engine","name":"🕷️ 商品采集","version":"2.1","desc":"7平台商品自动采集与导入","author":"Friday","category":"自动化","stars":86,"downloads":890,"tags":["scraper","product","ebay"]},
    {"id":"auto-pilot","name":"🤖 自动运维","version":"1.2","desc":"AI自动执行日常运维任务","author":"Friday","category":"自动化","stars":83,"downloads":670,"tags":["ops","auto","cron"]},
    {"id":"cron-manager","name":"⏰ 定时任务","version":"1.0","desc":"可视化Cron任务管理/调度","author":"Friday","category":"自动化","stars":78,"downloads":520,"tags":["cron","schedule","timer"]},
    {"id":"batch-ops","name":"📦 批量操作","version":"1.1","desc":"批量处理商品/订单/数据","author":"Friday","category":"自动化","stars":74,"downloads":430,"tags":["batch","bulk"]},

    # 安全类
    {"id":"security-center","name":"🛡️ 安全中心","version":"2.0","desc":"IP封禁/权限管理/安全审计","author":"Friday","category":"安全","stars":90,"downloads":1050,"tags":["security","firewall","audit"]},
    {"id":"approval-flow","name":"✅ 审批流程","version":"1.3","desc":"高危操作审批/多级审批流程","author":"Friday","category":"安全","stars":85,"downloads":780,"tags":["approval","review","audit"]},
    {"id":"risk-scanner","name":"⚠️ 风险扫描","version":"1.1","desc":"自动扫描系统安全风险","author":"Friday","category":"安全","stars":77,"downloads":490,"tags":["risk","scan","vulnerability"]},
    {"id":"emergency-kill","name":"🚨 急救开关","version":"1.0","desc":"一键切断AI写权限/紧急模式切换","author":"Friday","category":"安全","stars":93,"downloads":1350,"tags":["emergency","kill","safety"]},

    # 商城类
    {"id":"mall-manager","name":"🏪 商城管理","version":"3.0","desc":"142个接口覆盖商品/订单/客服/财务/营销","author":"Friday","category":"商城","stars":97,"downloads":2100,"tags":["mall","shop","ecommerce"]},
    {"id":"mall-brain","name":"🧠 AI大脑","version":"1.5","desc":"AI商品扫描/运营报告/自动执行","author":"Friday","category":"商城","stars":89,"downloads":920,"tags":["ai","brain","analysis"]},
    {"id":"customer-service","name":"👥 客服系统","version":"1.2","desc":"工单管理/自动回复/满意度统计","author":"Friday","category":"商城","stars":80,"downloads":580,"tags":["cs","ticket","support"]},
    {"id":"marketing-tools","name":"📢 营销工具","version":"1.0","desc":"优惠券/活动/推送管理","author":"Friday","category":"商城","stars":75,"downloads":450,"tags":["marketing","coupon","promo"]},
    {"id":"data-analytics","name":"📊 数据分析","version":"1.1","desc":"商城运营数据分析与报表","author":"Friday","category":"商城","stars":81,"downloads":630,"tags":["analytics","report","stats"]},

    # AI/模型类
    {"id":"ai-chat","name":"💬 AI对话","version":"2.0","desc":"多模型AI对话（Ollama/DeepSeek/Claude/GPT）","author":"Friday","category":"AI","stars":96,"downloads":3200,"tags":["chat","ai","llm"]},
    {"id":"vision-agent","name":"👁️ 视觉识别","version":"1.2","desc":"OCR文字识别/图片分析/物体检测","author":"Friday","category":"AI","stars":84,"downloads":"760","tags":["ocr","vision","image"]},
    {"id":"trend-agent","name":"📈 趋势分析","version":"1.1","desc":"YouTube/X/Google多平台热点趋势","author":"Friday","category":"AI","stars":79,"downloads":540,"tags":["trend","social","hot"]},
    {"id":"code-agent","name":"💻 代码助手","version":"1.0","desc":"代码分析/生成/搜索/API生成","author":"Friday","category":"AI","stars":73,"downloads":390,"tags":["code","dev","api"]},
    {"id":"playwright-agent","name":"🎭 浏览器自动化","version":"1.3","desc":"Playwright截图/抓取/搜索","author":"Friday","category":"AI","stars":87,"downloads":840,"tags":["playwright","browser","crawl"]},

    # 轮值/域名类
    {"id":"rotation-system","name":"🌐 域名轮值","version":"2.0","desc":"企业级域名轮值/健康检测/自动切换","author":"Friday","category":"网络","stars":92,"downloads":1150,"tags":["rotation","domain","dns"]},
    {"id":"ssl-manager","name":"🔒 SSL证书","version":"1.2","desc":"自动签发/续签/状态监控（acme.sh）","author":"Friday","category":"网络","stars":86,"downloads":880,"tags":["ssl","cert","https"]},
    {"id":"dns-manager","name":"📡 DNS管理","version":"0.8","desc":"DNS解析记录管理","author":"Friday","category":"网络","stars":68,"downloads":320,"tags":["dns","domain","resolve"]},

    # 开发工具
    {"id":"db-manager","name":"🗄️ 数据库管理","version":"1.1","desc":"MySQL状态/表结构/查询/优化","author":"Friday","category":"开发","stars":83,"downloads":710,"tags":["db","mysql","sql"]},
    {"id":"log-viewer","name":"📋 日志查看","version":"1.0","desc":"集中式系统日志查看与分析","author":"Friday","category":"开发","stars":76,"downloads":480,"tags":["log","debug","trace"]},
    {"id":"file-manager","name":"📁 文件管理","version":"1.0","desc":"服务器文件浏览/上传/下载/编辑","author":"Friday","category":"开发","stars":80,"downloads":560,"tags":["file","upload","manager"]},
    {"id":"api-explorer","name":"🔌 API探索","version":"0.9","desc":"API接口文档浏览与测试","author":"Friday","category":"开发","stars":72,"downloads":410,"tags":["api","docs","swagger"]},
    {"id":"git-manager","name":"📦 Git管理","version":"0.7","desc":"Git仓库状态/提交/分支管理","author":"Friday","category":"开发","stars":65,"downloads":280,"tags":["git","version","code"]},

    # 社区
    {"id":"team-collab","name":"👥 团队协作","version":"0.6","desc":"多用户协作/权限管理","author":"Friday","category":"社区","stars":60,"downloads":210,"tags":["team","user","collab"]},
    {"id":"skill-devkit","name":"🧰 技能开发包","version":"0.5","desc":"自定义技能开发工具包/SDK","author":"Friday","category":"社区","stars":55,"downloads":150,"tags":["sdk","devkit","extend"]},
]

# ===== 分类统计 =====
CATEGORIES = {}
for s in SKILLS_MARKETPLACE:
    cat = s["category"]
    if cat not in CATEGORIES:
        CATEGORIES[cat] = {"category": cat, "count": 0, "icon": s.get("icon", "📦")}
    CATEGORIES[cat]["count"] += 1


@router.get("")
async def list_plugins(_=Depends(verify_token)):
    """获取所有已安装技能"""
    await handle_risk("L1", "查看技能列表")
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
    """浏览技能市场"""
    await handle_risk("L1", "浏览技能市场")
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
    """安装技能（注册工具到系统）"""
    await handle_risk("L2", f"安装技能 {plugin_id}")
    skill = next((s for s in SKILLS_MARKETPLACE if s["id"] == plugin_id), None)
    if not skill:
        raise HTTPException(404, f"技能不存在: {plugin_id}")
    saved = state._data.setdefault("plugins", [])
    if any(s["id"] == plugin_id for s in saved):
        return {"ok": True, "plugin_id": plugin_id, "status": "already_installed"}
    saved.append({
        "id": plugin_id, "enabled": True,
        "installed_at": datetime.datetime.now().isoformat(),
    })
    state._save()
    # 注册工具到工具注册中心
    _register_tools(plugin_id, skill)
    return {"ok": True, "plugin_id": plugin_id, "status": "installed", "skill": skill}


@router.post("/uninstall")
async def uninstall_plugin(plugin_id: str, _=Depends(verify_token)):
    """卸载技能"""
    await handle_risk("L2", f"卸载技能 {plugin_id}")
    saved = state._data.setdefault("plugins", [])
    state._data["plugins"] = [s for s in saved if s["id"] != plugin_id]
    state._save()
    return {"ok": True, "plugin_id": plugin_id, "uninstalled": True}


@router.post("/toggle")
async def toggle_plugin(plugin_id: str, enabled: bool, _=Depends(verify_token)):
    """启用/禁用技能"""
    await handle_risk("L1", f"{'启用' if enabled else '禁用'}技能 {plugin_id}")
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
    """获取技能分类"""
    return {"ok": True, "categories": list(CATEGORIES.values()), "total": len(SKILLS_MARKETPLACE)}


def _register_tools(plugin_id: str, skill: dict):
    """安装技能时注册对应工具"""
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

# ===== 技能包分发系统 =====
import os, json, tempfile
from tools.skill_loader import install_from_zip, uninstall, list_installed, create_skill_package

# 社区技能市场（示例技能包，用户可发布自己的）
# 实际部署时可改为从远程仓库拉取
COMMUNITY_SKILLS = [
    {
        "id": "seo-optimizer",
        "name": "🔍 SEO优化器",
        "version": "1.0.0",
        "desc": "自动分析商品页面SEO，生成优化建议，提升搜索引擎排名",
        "author": "Friday社区",
        "category": "商城",
        "stars": 78,
        "downloads": 340,
        "tags": ["seo","optimize","rank"],
        "updated_at": "2026-05-28",
        "size_kb": 45,
        "readme": "安装后在AI对话中输入「SEO分析 [商品ID]」即可使用"
    },
    {
        "id": "price-predictor",
        "name": "📈 价格预测",
        "version": "0.9.0",
        "desc": "基于历史数据和市场趋势，AI预测商品最优定价策略",
        "author": "Friday社区",
        "category": "商城",
        "stars": 82,
        "downloads": 510,
        "tags": ["price","predict","strategy"],
        "updated_at": "2026-05-27",
        "size_kb": 62,
        "readme": "安装后输入「价格预测 [商品ID]」即可使用"
    },
    {
        "id": "wechat-push",
        "name": "💬 微信推送",
        "version": "1.2.0",
        "desc": "订单状态变更/库存预警/系统告警实时推送企业微信",
        "author": "Friday社区",
        "category": "通知",
        "stars": 90,
        "downloads": 1280,
        "tags": ["wechat","push","alert"],
        "updated_at": "2026-05-25",
        "size_kb": 28,
        "readme": "需在.env配置WECOM_WEBHOOK，安装后自动注册通知渠道"
    },
    {
        "id": "log-analyzer",
        "name": "📋 日志分析器",
        "version": "1.1.0",
        "desc": "智能分析Nginx/MySQL/Python日志，自动发现异常和性能瓶颈",
        "author": "Friday社区",
        "category": "开发",
        "stars": 74,
        "downloads": 290,
        "tags": ["log","analyze","debug"],
        "updated_at": "2026-05-20",
        "size_kb": 38,
        "readme": "安装后在AI对话中输入「分析日志 [类型] [行数]」"
    },
    {
        "id": "auto-translator",
        "name": "🌍 AI翻译官",
        "version": "1.0.0",
        "desc": "批量翻译商品标题/描述到50+语言，保留SEO关键词",
        "author": "Friday社区",
        "category": "工具",
        "stars": 86,
        "downloads": 760,
        "tags": ["translate","i18n","seo"],
        "updated_at": "2026-05-18",
        "size_kb": 52,
        "readme": "安装后在AI对话中输入「翻译 [商品ID] 到 [语言]」"
    },
    {
        "id": "screenshot-bot",
        "name": "📸 截图机器人",
        "version": "1.0.0",
        "desc": "定时截取网页/竞品页面快照，监控页面变更",
        "author": "Friday社区",
        "category": "工具",
        "stars": 71,
        "downloads": 210,
        "tags": ["screenshot","monitor","change"],
        "updated_at": "2026-05-15",
        "size_kb": 35,
        "readme": "安装后输入「截图监控 [URL] 每小时」"
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
async def community_skills(category:""="",search:""="",_=Depends(verify_token)):
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
            item["download_url"]=f"{repo}{s.get("path","")}.zip"
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
                zu=f"{repo}{skill.get("path","")}.zip"
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
        

@router.post("/publish")
async def publish_skill(file: bytes = None, download_url: str = "", _=Depends(verify_token)):
    """发布技能（上传 ZIP 包或从 URL 下载）"""
    await handle_risk("L2", "发布技能")
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
            return {"ok": False, "error": f"下载失败: {str(e)}"}
    else:
        return {"ok": False, "error": "请上传 ZIP 文件或提供下载 URL"}

    try:
        result = await install_from_zip(tmp_path, source="upload")
        return result
    finally:
        try: os.unlink(tmp_path)
        except: pass


@router.get("/installed/packages")
async def installed_packages(_=Depends(verify_token)):
    """已安装的技能包列表（区别于内置技能）"""
    await handle_risk("L1", "查看已安装技能包")
    skills = list_installed()
    return {"ok": True, "skills": skills, "count": len(skills)}


@router.post("/uninstall/{skill_id}")
async def uninstall_skill_package(skill_id: str, _=Depends(verify_token)):
    """卸载已安装的技能包"""
    await handle_risk("L2", f"卸载技能包 {skill_id}")
    result = await uninstall(skill_id)
    return result


@router.get("/installed/{skill_id}/readme")
async def skill_readme(skill_id: str, _=Depends(verify_token)):
    """获取已安装技能的 README"""
    from tools.skill_loader import get_manifest
    manifest = get_manifest(skill_id)
    if not manifest:
        raise HTTPException(404, "技能未安装")
    readme = manifest.get("readme", "暂无说明文档")
    return {"ok": True, "skill_id": skill_id, "readme": readme}
