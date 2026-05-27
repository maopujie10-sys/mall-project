import { agentApi } from "./index"

export function getDockerContainers() {
  return agentApi.get("/docker/ps")
}

export function getDockerStatus() {
  return agentApi.get("/docker/status")
}

export function getDockerLogs(container, lines = 50) {
  return agentApi.get("/docker/logs", { params: { container, lines } })
}

export function getDockerImages() {
  return agentApi.get("/docker/images")
}

export function getDockerNetworks() {
  return agentApi.get("/docker/network")
}

export function restartDockerContainer(container_id) {
  return agentApi.post("/docker/restart", { container_id, action: "restart" })
}

export function getDockerCompose() {
  return agentApi.get("/docker/compose")
}
