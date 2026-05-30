import { agentApi } from './index'


export function runPatrol() {
  return agentApi.post('/heal/patrol')
}


export function autoFix(anomalyId = null) {
  return agentApi.post('/heal/auto-fix' + (anomalyId ? '?anomaly_id=' + anomalyId : ''))
}


export function getAnomalyHistory(days = 7) {
  return agentApi.get('/heal/history', { params: { days } })
}


export function resolveAnomaly(anomalyId, resolution = 'manual') {
  return agentApi.post('/heal/resolve', { anomaly_id: anomalyId, resolution })
}
