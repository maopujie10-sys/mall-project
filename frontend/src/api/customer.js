import { agentApi } from './index'

export function getMessages() {
  return agentApi.get('/agent/customer/messages')
}

export function markRead(messageId) {
  return agentApi.post('/agent/customer/read', { messageId })
}

export function markAllRead() {
  return agentApi.post('/agent/customer/read-all')
}

export function transferToHuman(messageIds) {
  return agentApi.post('/agent/customer/transfer', { messageIds })
}
