锘縤mport { agentApi } from './index'

export function listLogSources() {
  return agentApi.get('/agent/logs/sources')
}

export function viewLogs(source = 'app', lines = 100, filterText = '', level = '') {
  return agentApi.get('/agent/logs/view', { params: { source, lines, filter_text: filterText, level } })
}

export function searchLogs(source, keyword) {
  return agentApi.post('/agent/logs/search?source=' + source + '&keyword=' + encodeURIComponent(keyword))
}

export function getRecentErrors(hours = 24) {
  return agentApi.get('/agent/logs/recent-errors', { params: { hours } })
}
