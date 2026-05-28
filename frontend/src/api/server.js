import { agentApi } from "./index"

export function getServerStatus() { return agentApi.get("/server/status") }
export function getServerPorts() { return agentApi.get("/server/ports") }
export function getServerProcesses() { return agentApi.get("/server/processes") }
export function getServerDisk() { return agentApi.get("/server/disk") }
export function getServerFiles(path) { return agentApi.get("/server/files", { params: { path } }) }
export function uploadServerFile(path, file) {
  const fd = new FormData(); fd.append("file", file)
  return agentApi.post("/server/files/upload", fd, { params: { path }, headers: { "Content-Type": "multipart/form-data" } })
}
export function deleteServerFile(path) { return agentApi.delete("/server/files", { params: { path } }) }
export function killServerProcess(pid) { return agentApi.post("/server/kill-process", { pid }) }
// 新增
export function getMemoryTop(limit) { return agentApi.get("/server/memory/top", { params: { limit } }) }
export function getMemoryTrend(hours) { return agentApi.get("/server/memory/trend", { params: { hours } }) }
export function getMemoryLeaks() { return agentApi.get("/server/memory/leaks") }
export function releaseMemory(mode) { return agentApi.post("/server/memory/release", { mode }) }
export function getLargeFiles(path, minMb) { return agentApi.get("/server/disk/large-files", { params: { path, min_mb: minMb } }) }
export function cleanTemp(days) { return agentApi.post("/server/disk/clean-temp", { days }) }
