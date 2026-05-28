import { agentApi } from "./index"

export function getNginxStatus() { return agentApi.get("/nginx/status") }
export function testNginxConfig() { return agentApi.get("/nginx/test") }
export function getNginxConfig(path) { return agentApi.get("/nginx/config", { params: { path } }) }
export function getNginxSites() { return agentApi.get("/nginx/sites") }
export function getNginxErrors() { return agentApi.get("/nginx/errors") }
export function getNginxUpstreams() { return agentApi.get("/nginx/upstreams") }
export function getNginxConnections() { return agentApi.get("/nginx/connections") }
export function getNginxLogs(params) { return agentApi.get("/nginx/logs", { params }) }
export function searchNginxLogs(params) { return agentApi.post("/nginx/log/search", params) }
export function reloadNginx() { return agentApi.post("/nginx/reload") }
