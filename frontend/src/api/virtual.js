import { agentApi } from './index'

// 一键生成虚拟数据
export function generateData(scale = 'medium', target = null) {
  return agentApi.post('/agent/virtual/generate', { scale, target })
}

// 实时活动日志
export function getRealtimeActivity(count = 20) {
  return agentApi.post('/agent/virtual/realtime', { count })
}

// 仪表盘统计
export function getDashboardStats() {
  return agentApi.get('/agent/virtual/dashboard')
}

// 数据统计
export function getDataStats() {
  return agentApi.get('/agent/virtual/stats')
}

// 规模列表
export function getScales() {
  return agentApi.get('/agent/virtual/scales')
}
