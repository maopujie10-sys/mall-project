import { agentApi } from './index'

// 获取插件列表
export function listPlugins() {
  return agentApi.get('/agent/plugins')
}

// 安装插件
export function installPlugin(pluginId, source = 'marketplace') {
  return agentApi.post('/agent/plugins/install', { plugin_id: pluginId, source })
}

// 卸载插件
export function uninstallPlugin(pluginId) {
  return agentApi.post('/agent/plugins/uninstall', { plugin_id: pluginId })
}

// 启用/禁用插件
export function togglePlugin(pluginId, enabled) {
  return agentApi.post('/agent/plugins/toggle', { plugin_id: pluginId, enabled })
}

// 获取插件配置
export function getPluginConfig(pluginId) {
  return agentApi.get('/agent/plugins/config', { params: { plugin_id: pluginId } })
}

// 更新插件配置
export function updatePluginConfig(pluginId, config) {
  return agentApi.post('/agent/plugins/config', { plugin_id: pluginId, config })
}
