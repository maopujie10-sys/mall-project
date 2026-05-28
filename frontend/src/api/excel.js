import { agentApi } from './index'
export function parseExcel(file) {
  const fd = new FormData()
  fd.append('file', file)
  return agentApi.post('/agent/excel/parse', fd, {headers:{'Content-Type':'multipart/form-data'}})
}
export function batchPublish(products, category_id='', auto_pricing=true) {
  return agentApi.post('/agent/excel/publish', {products, category_id, auto_pricing})
}
export function getExcelHistory() { return agentApi.get('/agent/excel/history') }
export function getTemplate() { return agentApi.get('/agent/excel/templates') }
