import { agentApi } from './index'

// 启动采集任务
export function startScrapeJob(platform, keyword, maxItems = 20, downloadImages = true) {
  return agentApi.post('/agent/scraper/jobs', { platform, keyword, max_items: maxItems, download_images: downloadImages })
}

// 获取采集任务列表
export function listScrapeJobs() {
  return agentApi.get('/agent/scraper/jobs')
}

// 获取采集任务详情
export function getScrapeJob(jobId) {
  return agentApi.get(`/agent/scraper/jobs/${jobId}`)
}

// 删除采集任务
export function deleteScrapeJob(jobId) {
  return agentApi.delete(`/agent/scraper/jobs/${jobId}`)
}

// 获取采集到的商品列表
export function listScrapedProducts(page = 1, size = 20, status = null) {
  return agentApi.get('/agent/scraper/products', { params: { page, size, status } })
}

// 导入商品到商城
export function importProducts(productIds) {
  return agentApi.post('/agent/scraper/products/import', { product_ids: productIds })
}

// COS 上传状态
export function getCOSStatus() {
  return agentApi.get('/agent/scraper/cos-status')
}
