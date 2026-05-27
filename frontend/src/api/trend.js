import { agentApi } from './index'

export async function getTrends(platform = 'all') {
  try { return await agentApi.get(`/trends?platform=${platform}`) } catch { return [] }
}

export async function analyzeTrend(url) {
  return agentApi.post('/trends/analyze', { url })
}

export async function getHotRanking() {
  try { return await agentApi.get('/trends/hot') } catch { return [] }
}
