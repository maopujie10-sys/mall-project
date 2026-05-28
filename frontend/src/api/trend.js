import { agentApi } from './index'

// 获取热点数据
export function fetchTrends(platform = null) {
  return agentApi.get('/agent/friday/trends', { params: { platform } })
}

// 分析趋势
export function analyzeTrend(keyword) {
  return agentApi.get('/agent/friday/trends/analyze', { params: { keyword } })
}

// 预测热门
export function predictHot(category = '科技') {
  return agentApi.get('/agent/friday/trends/predict', { params: { category } })
}

// 搜索热点
export function searchTrends(query) {
  return agentApi.get('/agent/friday/trends/search', { params: { query } })
}
