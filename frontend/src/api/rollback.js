import { agentApi } from './index'

export function getBackups() { return agentApi.get('/rollback/backups') }
export function createBackup(data) { return agentApi.post('/rollback/backups', data) }
export function verifyBackup(backupId) { return agentApi.post(`/rollback/backups/${backupId}/verify`) }
export function executeRollback(backupId) { return agentApi.post(`/rollback/backups/${backupId}/rollback`) }
