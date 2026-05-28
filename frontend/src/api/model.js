import { agentApi } from './index'

// 列出所有可用模型
export function listModels() {
  return agentApi.get('/agent/friday/models')
}

// 智能路由选择模型
export function routeModel(mode = 'quality') {
  return agentApi.get('/agent/friday/models/route', { params: { mode } })
}

// 测试模型速度
export function testModelSpeed(modelId) {
  return agentApi.post('/agent/friday/models/test', { model_id: modelId })
}

// 模型对比
export function compareModels(modelIds) {
  return agentApi.post('/agent/friday/models/compare', { model_ids: modelIds })
}


// 获取模型列表 (别名)
export const getModels = listModels

// 切换当前模型
export function switchModel(modelId) {
  return agentApi.post("/agent/friday/models/switch", { model_id: modelId })
}

// 获取模型状态
export function getModelStatus() {
  return agentApi.get("/agent/friday/models/status")
}

// 模型测速 (别名)
export const testModel = testModelSpeed
