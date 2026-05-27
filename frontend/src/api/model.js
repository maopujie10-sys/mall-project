import { agentApi } from './index'

export async function getModels() {
  try { return await agentApi.get('/models') } catch { return [] }
}

export async function switchModel(modelId) {
  return agentApi.post('/models/switch', { model: modelId })
}

export async function getModelStatus() {
  try { return await agentApi.get('/models/status') } catch { return null }
}

export async function testModel(modelId) {
  return agentApi.post('/models/test', { model: modelId })
}
