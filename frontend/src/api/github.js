import { agentApi } from './index'

export function getGitHubConfig() { return agentApi.get('/github/config') }
export function getRepo(repo) { return agentApi.get('/github/repo', { params: { repo } }) }
export function listIssues(repo, state = 'open', limit = 10) { return agentApi.get('/github/issues', { params: { repo, state, limit } }) }
export function listPRs(repo, state = 'open', limit = 10) { return agentApi.get('/github/prs', { params: { repo, state, limit } }) }
export function listBranches(repo, limit = 20) { return agentApi.get('/github/branches', { params: { repo, limit } }) }
export function listWorkflows(repo, limit = 10) { return agentApi.get('/github/workflows', { params: { repo, limit } }) }
export function listCommits(repo, branch = 'master', limit = 10) { return agentApi.get('/github/commits', { params: { repo, branch, limit } }) }
export function createIssue(repo, title, body) { return agentApi.post('/github/issues', { repo, title, body }) }
