import { agentApi } from './index'
export function getAlertStatus() { return agentApi.get('/agent/order-alert/status') }
export function getAlertRules() { return agentApi.get('/agent/order-alert/rules') }
export function createAlertRule(data) { return agentApi.post('/agent/order-alert/rules', data) }
export function deleteAlertRule(rule_id) { return agentApi.delete('/agent/order-alert/rules/'+rule_id) }
export function runAlertCheck() { return agentApi.get('/agent/order-alert/check') }
export function getAlertHistory() { return agentApi.get('/agent/order-alert/history') }
export function getAlertStats() { return agentApi.get('/agent/order-alert/stats') }
