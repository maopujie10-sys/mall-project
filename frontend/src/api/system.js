import { agentApi } from './index'

/**
 * Get current system mode (ai-control / assist / readonly / human-control)
 */
export function getSystemMode() {
  return agentApi.get('/system/mode')
}

/**
 * Set system mode
 * @param {string} mode - 'ai_control' | 'readonly' | 'assist' | 'human_control'
 */
export function setSystemMode(mode) {
  return agentApi.post('/system/mode', { mode })
}

/**
 * Emergency kill switch - cut AI write permissions
 */
export function emergencyKill() {
  return agentApi.post('/system/emergency-kill')
}

/**
 * Get emergency operation history
 */
export function getEmergencyHistory() {
  return agentApi.get('/system/emergency-history')
}

/**
 * Get pending approval tasks
 */
export function getPendingApprovals() {
  return agentApi.get('/system/approvals/pending')
}

/**
 * Approve or reject a task
 * @param {string} taskId
 * @param {boolean} approved
 */
export function decideApproval(taskId, approved) {
  return agentApi.post('/system/approvals/decide', { taskId, approved })
}

/**
 * Get approval history
 */
export function getApprovalHistory() {
  return agentApi.get('/system/approvals/history')
}
