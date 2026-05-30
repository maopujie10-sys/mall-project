import { agentApi } from './index'

export function startScrapeJob(source, params = {}) {
  return agentApi.post('/scraper/start', { source, ...params })
}

export function listScrapeJobs() {
  return agentApi.get('/scraper/jobs')
}

export function deleteScrapeJob(jobId) {
  return agentApi.delete('/scraper/jobs/' + jobId)
}

export function getCOSStatus() {
  return agentApi.get('/scraper/cos-status')
}
