import { agentApi } from './index'

// 执行巡检
export function runPatrol() {
  return agentApi.post('/heal/patrol')
}

// 自动修复
export function autoFix(anomalyId = null) {
  return agentApi.post('/heal/auto-fix' + (anomalyId ? '?anomaly_id=' + anomalyId : ''))
}

// 异常历史
export function getAnomalyHistory(days = 7) {
  return agentApi.get('/heal/history', { params: { days } })
}

// 标记解决
export function resolveAnomaly(anomalyId, resolution = 'manual') {
  return agentApi.post('/heal/resolve', { anomaly_id: anomalyId, resolution })
}
