import { agentApi } from './index'
export function getPhoneStatus() { return agentApi.get('/agent/phone/status') }
export function getPhoneLogs(page=1) { return agentApi.get('/agent/phone/logs', {params:{page}}) }
export function getIVRMenu() { return agentApi.get('/agent/phone/ivr/menu') }
export function updateIVRMenu(menu) { return agentApi.post('/agent/phone/ivr/menu', menu) }
export function simulateCall(data) { return agentApi.post('/agent/phone/simulate', data) }
export function transferCall(call_id) { return agentApi.post('/agent/phone/transfer', {call_id, action:'transfer'}) }
export function getPhoneStats() { return agentApi.get('/agent/phone/stats') }
