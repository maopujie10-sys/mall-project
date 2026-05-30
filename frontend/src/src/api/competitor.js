import { agentApi } from './index'

export function addTrack(product_name, platform, url, target_price, category) {
  return agentApi.post('/agent/competitor/track', { product_name, platform, url, target_price, category })
}

export function listTracks() {
  return agentApi.get('/agent/competitor/tracks')
}

export function removeTrack(trackId) {
  return agentApi.delete('/agent/competitor/track/' + trackId)
}

export function recordPrice(trackId, price, currency = 'USD') {
  return agentApi.post('/agent/competitor/track/' + trackId + '/price?price=' + price + '&currency=' + currency)
}

export function recordPromotion(trackId, title, discount) {
  return agentApi.post('/agent/competitor/track/' + trackId + '/promotion?title=' + encodeURIComponent(title) + '&discount=' + encodeURIComponent(discount || ''))
}

export function getPriceAlerts(days = 7) {
  return agentApi.get('/agent/competitor/alerts', { params: { days } })
}

export function getPriceTrends() {
  return agentApi.get('/agent/competitor/trends')
}

export function getActivePromotions() {
  return agentApi.get('/agent/competitor/promotions')
}

export function getCompetitorSummary() {
  return agentApi.get('/agent/competitor/summary')
}
