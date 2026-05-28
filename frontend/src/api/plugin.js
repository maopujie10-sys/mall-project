import { agentApi } from './index'

// ===== 内置技能市场 =====
export function listPlugins() {
  return agentApi.get('/agent/plugins')
}
export function getMarketplace() {
  return agentApi.get('/agent/plugins/marketplace')
}
export function installPlugin(pluginId) {
  return agentApi.post('/agent/plugins/install', { plugin_id: pluginId })
}
export function uninstallPlugin(pluginId) {
  return agentApi.post('/agent/plugins/uninstall', { plugin_id: pluginId })
}
export function togglePlugin(pluginId, enabled) {
  return agentApi.post('/agent/plugins/toggle', { plugin_id: pluginId, enabled })
}
export function getPluginCategories() {
  return agentApi.get('/agent/plugins/categories')
}

// ===== 社区技能市场 =====
export function getCommunitySkills(params) {
  return agentApi.get('/agent/plugins/community', { params })
}
export function installCommunitySkill(skillId) {
  return agentApi.post('/agent/plugins/community/install', { skill_id: skillId })
}

// ===== 技能包分发系统 =====
export function publishSkill(file) {
  const form = new FormData()
  form.append('file', file)
  return agentApi.post('/agent/plugins/publish', form, {
    headers: { 'Content-Type': 'multipart/form-data' }
  })
}
export function publishSkillFromUrl(url) {
  return agentApi.post('/agent/plugins/publish', { download_url: url })
}
export function getInstalledPackages() {
  return agentApi.get('/agent/plugins/installed/packages')
}
export function uninstallSkillPackage(skillId) {
  return agentApi.post('/agent/plugins/uninstall/' + skillId)
}
export function getSkillReadme(skillId) {
  return agentApi.get('/agent/plugins/installed/' + skillId + '/readme')
}