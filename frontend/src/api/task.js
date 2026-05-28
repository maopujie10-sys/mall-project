import { agentApi } from './index'

// 添加任务到队列
export function enqueueTask(name, risk = 'L1', priority = 5, timeoutS = 60) {
  return agentApi.post('/tasks/enqueue', { name, risk, priority, timeout_s: timeoutS })
}

// 查看任务队列
export function listTasks() {
  return agentApi.get('/tasks/queue')
}

// 获取任务详情
export function getTask(taskId) {
  return agentApi.get(`/tasks/queue/${taskId}`)
}

// 取消任务
export function cancelTask(taskId) {
  return agentApi.post(`/tasks/queue/${taskId}/cancel`)
}

// 任务统计
export function getTaskStats() {
  return agentApi.get('/tasks/stats')
}
