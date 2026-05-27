import { agentApi } from './index'

export function getNginxStatus() { return agentApi.get('/nginx/status') }
export function testNginxConfig() { return agentApi.get('/nginx/test') }
export function getNginxLogs(params) { return agentApi.get('/nginx/logs', { params }) }
export function reloadNginx() { return agentApi.post('/nginx/reload') }
