import { agentApi } from './index'

export function listModels() {
  return agentApi.get('/agent/friday/models')
}

export function routeModel(mode = 'quality') {
  return agentApi.get('/agent/friday/models/route', { params: { mode } })
}

export function testModelSpeed(modelId) {
  return agentApi.post('/agent/friday/models/test', { model_id: modelId })
}

export function compareModels(modelIds) {
  return agentApi.post('/agent/friday/models/compare', { model_ids: modelIds })
}

//  ()
export const getModels = listModels

export function switchModel(modelId) {
  return agentApi.post("/agent/friday/models/switch", { model_id: modelId })
}

export function getModelStatus() {
  return agentApi.get("/agent/friday/models/status")
}

//  ()
export const testModel = testModelSpeed
