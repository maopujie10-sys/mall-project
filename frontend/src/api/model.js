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
