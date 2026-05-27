import { agentApi } from './index'

export async function getTasks() {
  try { return await agentApi.get('/tasks') } catch { return [] }
}

export async function createTask(data) {
  return agentApi.post('/tasks', data)
}

export async function deleteTask(id) {
  return agentApi.delete(`/tasks/${id}`)
}

export async function runTask(id) {
  return agentApi.post(`/tasks/${id}/run`)
}

export async function getTaskLogs(id) {
  try { return await agentApi.get(`/tasks/${id}/logs`) } catch { return [] }
}
