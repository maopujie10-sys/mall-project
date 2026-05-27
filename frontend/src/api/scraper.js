import { agentApi } from './index'

export async function getScraperJobs() {
  try { return await agentApi.get('/scraper/jobs') } catch { return [] }
}

export async function createScraperJob(data) {
  return agentApi.post('/scraper/jobs', data)
}

export async function deleteScraperJob(id) {
  return agentApi.delete(`/scraper/jobs/${id}`)
}

export async function runScraperJob(id) {
  return agentApi.post(`/scraper/jobs/${id}/run`)
}

export async function getScraperResults(jobId) {
  try { return await agentApi.get(`/scraper/jobs/${jobId}/results`) } catch { return [] }
}
