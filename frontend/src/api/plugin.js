import { agentApi } from './index'

export async function getPlugins() {
  try { return await agentApi.get('/plugins') } catch { return [] }
}

export async function installPlugin(id) {
  return agentApi.post(`/plugins/install`, { id })
}

export async function uninstallPlugin(id) {
  return agentApi.delete(`/plugins/${id}`)
}

export async function togglePlugin(id, enabled) {
  return agentApi.post(`/plugins/${id}/toggle`, { enabled })
}
