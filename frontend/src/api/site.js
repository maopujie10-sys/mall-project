import { agentApi } from './index'

export function checkSite(url) { return agentApi.post('/site/check', { url }) }
export function checkDns(domain) { return agentApi.post('/site/dns', { domain }) }
export function checkSsl(domain) { return agentApi.post('/site/ssl', { domain }) }
