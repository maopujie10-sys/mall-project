import { agentApi } from './index'

export async function getMemories() {
  try { return await agentApi.get('/memory') } catch { return [] }
}

export async function getMemory(id) {
  try { return await agentApi.get(`/memory/${id}`) } catch { return null }
}

export async function saveMemory(data) {
  return agentApi.post('/memory', data)
}

export async function deleteMemory(id) {
  return agentApi.delete(`/memory/${id}`)
}

export async function searchMemories(query) {
  try { return await agentApi.get(`/memory/search?q=${encodeURIComponent(query)}`) } catch { return [] }
}

export async function getHandoffDoc() {
  try { return await agentApi.get('/memory/handoff') } catch { return null }
}

export async function getOperationLog() {
  try { return await agentApi.get('/memory/operation-log') } catch { return [] }
}

export async function getCodeChanges() {
  try { return await agentApi.get('/memory/code-changes') } catch { return [] }
}
