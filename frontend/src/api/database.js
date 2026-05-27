import { agentApi } from './index'

export async function getDatabases() {
  try { return await agentApi.get('/database') } catch { return [] }
}

export async function queryDatabase(id, sql) {
  return agentApi.post(`/database/${id}/query`, { sql })
}

export async function getDatabaseTables(id) {
  try { return await agentApi.get(`/database/${id}/tables`) } catch { return [] }
}
