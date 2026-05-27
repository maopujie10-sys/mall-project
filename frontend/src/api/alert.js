import { agentApi } from './index'

export function getAlertList(params) { return agentApi.get('/alert/list', { params }) }
export function createAlert(data) { return agentApi.post('/alert/create', data) }
export function resolveAlert(alertId) { return agentApi.post(`/alert/resolve/${alertId}`) }
export function getAlertStats() { return agentApi.get('/alert/stats') }
