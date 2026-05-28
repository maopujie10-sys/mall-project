import { agentApi } from "./index"

export function getDomains() {
  return agentApi.get("/rotation/domains")
}

export function toggleDomain(domain, active) {
  return agentApi.post("/rotation/toggle", { domain, active })
}

export function checkDomain(domain) {
  return agentApi.post("/rotation/check", { domain })
}

export function checkAllDomains() {
  return agentApi.post("/rotation/check-all")
}

export function manualRotate() {
  return agentApi.post("/rotation/rotate")
}

export function getRotationReport() {
  return agentApi.get("/rotation/report")
}

export function setDomainWeight(domain, weight) {
  return agentApi.post("/rotation/weight", { domain, weight })
}

export function addDomain(domain, type) {
  return agentApi.post("/rotation/domains", { domain, type })
}

export function removeDomain(domain) {
  return agentApi.delete(`/rotation/domains/${encodeURIComponent(domain)}`)
}

export function getRotationHistory() {
  return agentApi.get("/rotation/history")
}
