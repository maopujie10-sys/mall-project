import { agentApi } from './index'

// 保存记忆
export function rememberMemory(content, category = 'general', importance = 1, tags = []) {
  return agentApi.post('/memory/remember', { content, category, importance, tags })
}

// 检索记忆
export function recallMemory(query = '', category = null, limit = 20) {
  return agentApi.get('/memory/recall', { params: { query, category, limit } })
}

// 从对话中学习
export function learnFromConversation(userMessage, aiResponse, topic = '') {
  return agentApi.post('/memory/learn', { user_message: userMessage, ai_response: aiResponse, topic })
}

// 记忆摘要
export function getMemorySummary() {
  return agentApi.get('/memory/summary')
}

// 记忆统计
export function getMemoryStats() {
  return agentApi.get('/memory/stats')
}

// 清除旧记忆
export function cleanupMemory(daysOld = 30) {
  return agentApi.post('/memory/cleanup', { days_old: daysOld })
}
