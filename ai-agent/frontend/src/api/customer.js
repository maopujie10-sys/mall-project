import { agentApi } from './index'

/**
 * Get customer messages list
 */
export function getMessages() {
  return agentApi.get('/customer/messages')
}

/**
 * Mark a single message as read
 * @param {number|string} messageId
 */
export function markRead(messageId) {
  return agentApi.post('/customer/read', { messageId })
}

/**
 * Mark all messages as read
 */
export function markAllRead() {
  return agentApi.post('/customer/read-all')
}

/**
 * Transfer messages to human agent
 * @param {number[]} messageIds
 */
export function transferToHuman(messageIds) {
  return agentApi.post('/customer/transfer', { messageIds })
}
