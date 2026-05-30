import { agentApi } from './index'

/** 启动采集任务 */
export function startScrapeJob(params) {
  return agentApi.post('/scraper/start', params)
}

/** 列出采集任务 */
export function listScrapeJobs() {
  return agentApi.get('/scraper/jobs')
}

/** 删除采集任务 */
export function deleteScrapeJob(jobId) {
  return agentApi.delete('/scraper/jobs/' + jobId)
}

/** 获取COS状态 */
export function getCOSStatus() {
  return agentApi.get('/scraper/cos-status')
}

/** 获取已采集商品 */
export function listScrapedProducts(keyword = '') {
  return agentApi.get('/scraper/products', { params: { keyword } })
}

/** 导入商品到商城 */
export function importToMall(productIds) {
  return agentApi.post('/scraper/import', { product_ids: productIds })
}