import { agentApi } from './index'

/**
 * Get all backup records
 */
export function getBackups() {
  return agentApi.get('/rollback/backups')
}

/**
 * Create a new manual backup
 */
export function createBackup() {
  return agentApi.post('/rollback/create')
}

/**
 * Execute a rollback to a specific backup
 * @param {string} backupId
 */
export function executeRollback(backupId) {
  return agentApi.post('/rollback/execute', { backupId })
}
