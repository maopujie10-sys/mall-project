import { agentApi } from './index'

export function getSystemMode() {
  return agentApi.get('/system/mode')
}

export function setSystemMode(mode) {
  return agentApi.post('/system/mode', { mode })
}

export function emergencyKill() {
  return agentApi.post('/system/emergency-kill')
}

export function getEmergencyHistory() {
  return agentApi.get('/system/emergency-history')
}

export function getPendingApprovals() {
  return agentApi.get('/system/pending-approvals')
}

export function decideApproval(taskId, approved) {
  return agentApi.post('/system/decide-approval', { task_id: taskId, approved })
}

export function getApprovalHistory() {
  return agentApi.get('/system/approval-history')
}
