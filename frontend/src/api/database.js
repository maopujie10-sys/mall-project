import { agentApi } from './index'

// 安全SQL执行
export function executeSQL(sql, dbName = 'mall_db') {
  return agentApi.post('/agent/sql/execute', { sql, db_name: dbName })
}

// 获取数据库表列表
export function getTables(dbName = 'mall_db') {
  return agentApi.get('/agent/sql/tables', { params: { db_name: dbName } })
}

// 获取表结构
export function getTableSchema(tableName, dbName = 'mall_db') {
  return agentApi.get('/agent/sql/schema', { params: { table: tableName, db_name: dbName } })
}

// 数据库状态
export function getDBStatus() {
  return agentApi.get('/agent/sql/status')
}
