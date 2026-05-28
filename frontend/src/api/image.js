import { agentApi } from './index'
export function removeBg(url='', file=null) {
  const fd = new FormData()
  if (url) fd.append('url', url)
  if (file) fd.append('file', file)
  return agentApi.post('/agent/image/remove-bg', fd, {headers:{'Content-Type':'multipart/form-data'}})
}
export function addWatermark(url, text='Friday AI', position='bottom-right') {
  return agentApi.post('/agent/image/watermark', {url, text, position})
}
export function batchProcess(urls, operation='remove_bg', params={}) {
  return agentApi.post('/agent/image/batch', {urls, operation, params})
}
export function getImageHistory() { return agentApi.get('/agent/image/history') }
