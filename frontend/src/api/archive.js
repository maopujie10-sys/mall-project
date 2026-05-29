export function listArchiveTargets() {
  return agentApi.get('/agent/archive/targets')
}

export function createArchive(targets, note = '', pushGithub = false) {
  return agentApi.post('/agent/archive/create', { targets, note, push_github: pushGithub })
}

export function listArchives() {
  return agentApi.get('/agent/archive/records')
}

export function deleteArchive(archiveId) {
  return agentApi.delete('/agent/archive/records/' + archiveId)
}

export function getArchiveStorage() {
  return agentApi.get('/agent/archive/storage')
}
