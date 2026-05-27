import { agentApi } from './index'

export function runInspection() { return agentApi.post('/inspector/run') }
export function getInspectionHistory() { return agentApi.get('/inspector/history') }
