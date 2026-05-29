锘縤mport { agentApi } from './index'

export function generateWeeklyReport() {
  return agentApi.post('/report/weekly')
}

export function listWeeklyReports() {
  return agentApi.get('/report/weekly')
}

export function getLatestWeeklyReport() {
  return agentApi.get('/report/weekly/latest')
}
