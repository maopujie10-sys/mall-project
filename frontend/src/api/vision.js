import { agentApi } from './index'

export async function analyzeVideo(url) {
  return agentApi.post('/vision/video', { url })
}

export async function extractSubtitles(url) {
  try { return await agentApi.post('/vision/subtitles', { url }) } catch { return null }
}

export async function analyzeImage(url) {
  return agentApi.post('/vision/image', { url })
}

export async function ocrImage(url) {
  return agentApi.post('/vision/ocr', { url })
}

export async function getVideoHistory() {
  try { return await agentApi.get('/vision/history') } catch { return [] }
}
