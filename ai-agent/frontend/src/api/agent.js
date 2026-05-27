import { agentApi } from './index'

/**
 * Send a chat message to the AI agent
 * @param {string} message - User's input message
 */
export function sendChat(message) {
  return agentApi.post('/agent/chat', { message })
}

/**
 * Confirm an L3/L4 high-risk task
 * @param {string} taskId - Task identifier
 * @param {boolean} approved - Whether approved
 */
export function confirmTask(taskId, approved) {
  return agentApi.post('/agent/confirm', { taskId, approved })
}

/**
 * Get current agent tasks / status
 */
export function getAgentTasks() {
  return agentApi.get('/agent/tasks')
}

/**
 * Handover to human operator
 * @param {string} reason - Reason for handover
 */
export function handover(reason) {
  return agentApi.post('/agent/handover', { reason })
}
