"""插件管理 API — 插件注册/启用/禁用/配置"""
from fastapi import APIRouter, Depends
from auth import verify_token
from risk import handle_risk
from state import state
import datetime

router = APIRouter(prefix="/agent/plugins", tags=["Plugins"])

BUILTIN_PLUGINS = [
    {"id": "trend-monitor", "name": "趋势监控", "version": "1.0", "description": "多平台热点监控", "enabled": True},
    {"id": "scraper-engine", "name": "商品采集", "version": "1.2", "description": "7平台商品采集引擎", "enabled": True},
    {"id": "auto-backup", "name": "自动备份", "version": "0.9", "description": "定时数据库/项目备份", "enabled": True},
    {"id": "ai-factory", "name": "AI作图", "version": "0.5", "description": "AI文案/图片/视频生成", "enabled": False},
    {"id": "github-mcp", "name": "GitHub MCP", "version": "1.0", "description": "GitHub仓库/Issues/PRs管理", "enabled": True},
    {"id": "playwright-mcp", "name": "Playwright MCP", "version": "1.0", "description": "浏览器自动化截图/抓取", "enabled": False},
]

@router.get("")
async def list_plugins(_=Depends(verify_token)):
    """获取所有插件列表"""
    await handle_risk("L1", "查看插件列表")
    saved = state._data.get("plugins", [])
    merged = []
    for bp in BUILTIN_PLUGINS:
        p = dict(bp)
        found = next((s for s in saved if s["id"] == bp["id"]), None)
        if found:
            p["enabled"] = found.get("enabled", bp["enabled"])
        merged.append(p)
    return {"ok": True, "plugins": merged, "count": len(merged)}

@router.post("/toggle")
async def toggle_plugin(plugin_id: str, enabled: bool, _=Depends(verify_token)):
    """启用/禁用插件"""
    await handle_risk("L1", f"{'启用' if enabled else '禁用'}插件 {plugin_id}")
    saved = state._data.setdefault("plugins", [])
    found = next((s for s in saved if s["id"] == plugin_id), None)
    if found:
        found["enabled"] = enabled
    else:
        saved.append({"id": plugin_id, "enabled": enabled})
    state._save()
    return {"ok": True, "plugin_id": plugin_id, "enabled": enabled}

@router.post("/install")
async def install_plugin(plugin_id: str, source: str = "marketplace", _=Depends(verify_token)):
    """安装插件"""
    await handle_risk("L2", f"安装插件 {plugin_id}")
    saved = state._data.setdefault("plugins", [])
    if not any(s["id"] == plugin_id for s in saved):
        saved.append({"id": plugin_id, "enabled": True, "source": source, "installed_at": datetime.datetime.now().isoformat()})
        state._save()
    return {"ok": True, "plugin_id": plugin_id, "installed": True}

@router.post("/uninstall")
async def uninstall_plugin(plugin_id: str, _=Depends(verify_token)):
    """卸载插件"""
    await handle_risk("L2", f"卸载插件 {plugin_id}")
    saved = state._data.setdefault("plugins", [])
    state._data["plugins"] = [s for s in saved if s["id"] != plugin_id]
    state._save()
    return {"ok": True, "plugin_id": plugin_id, "uninstalled": True}

@router.get("/config")
async def get_plugin_config(plugin_id: str, _=Depends(verify_token)):
    """获取插件配置"""
    await handle_risk("L1", f"查看插件 {plugin_id} 配置")
    configs = state._data.setdefault("plugin_configs", {})
    return {"ok": True, "plugin_id": plugin_id, "config": configs.get(plugin_id, {})}

@router.post("/config")
async def update_plugin_config(plugin_id: str, config: dict, _=Depends(verify_token)):
    """更新插件配置"""
    await handle_risk("L2", f"更新插件 {plugin_id} 配置")
    configs = state._data.setdefault("plugin_configs", {})
    configs[plugin_id] = config
    state._save()
    return {"ok": True, "plugin_id": plugin_id}
