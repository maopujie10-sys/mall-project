export function listSchedulerTasks() {
  return agentApi.get('/agent/scheduler/tasks')
}

export function triggerTask(taskId) {
  return agentApi.post('/agent/scheduler/tasks/' + taskId + '/trigger')
}

export function pauseTask(taskId) {
  return agentApi.post('/agent/scheduler/tasks/' + taskId + '/pause')
}

export function resumeTask(taskId) {
  return agentApi.post('/agent/scheduler/tasks/' + taskId + '/resume')
}
