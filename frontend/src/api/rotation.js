import { agentApi } from './index'

/**
 * Get all domains and their status
 */
export function getDomains() {
  return agentApi.get('/rotation/domains')
}

/**
 * Toggle a domain on/off
 * @param {string} domain
 * @param {boolean} active
 */
export function toggleDomain(domain, active) {
  return agentApi.post('/rotation/toggle', { domain, active })
}

/**
 * Check a single domain's health
 * @param {string} domain
 */
export function checkDomain(domain) {
  return agentApi.post('/rotation/check', { domain })
}
