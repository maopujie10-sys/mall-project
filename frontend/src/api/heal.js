import { agentApi } from './index'

// 鎵ц宸℃
export function runPatrol() {
  return agentApi.post('/heal/patrol')
}

// 鑷姩淇
export function autoFix(anomalyId = null) {
  return agentApi.post('/heal/auto-fix' + (anomalyId ? '?anomaly_id=' + anomalyId : ''))
}

// 寮傚父鍘嗗彶
export function getAnomalyHistory(days = 7) {
  return agentApi.get('/heal/history', { params: { days } })
}

// 鏍囪瑙ｅ喅
export function resolveAnomaly(anomalyId, resolution = 'manual') {
  return agentApi.post('/heal/resolve', { anomaly_id: anomalyId, resolution })
}
