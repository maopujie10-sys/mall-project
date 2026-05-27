import { agentApi } from './index'

/**
 * Get server status: CPU, memory, disk, load average
 */
export function getServerStatus() {
  return agentApi.get('/server/status')
}

/**
 * Get server disk usage details
 */
export function getDiskInfo() {
  return agentApi.get('/server/disk')
}

/**
 * Get port listening status
 */
export function getPortStatus() {
  return agentApi.get('/server/ports')
}

/**
 * Get process list
 */
export function getProcessList() {
  return agentApi.get('/server/processes')
}
