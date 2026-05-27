import { agentApi } from './index'

// 图片分析（OCR + 物体检测 + 人脸检测）
export function analyzeImage(imageUrl) {
  return agentApi.get('/agent/friday/vision/analyze', { params: { url: imageUrl } })
}

// 上传图片并分析
export function uploadAndAnalyze(file) {
  const formData = new FormData()
  formData.append('file', file)
  return agentApi.post('/agent/friday/vision/upload', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  })
}

// OCR 文字识别
export function ocrRecognize(imageUrl) {
  return agentApi.post('/agent/friday/vision/ocr', { image_url: imageUrl })
}

// 视频分析
export function analyzeVideo(videoUrl) {
  return agentApi.post('/agent/friday/vision/video', { video_url: videoUrl })
}

// 物体检测
export function detectObjects(imageUrl) {
  return agentApi.post('/agent/friday/vision/objects', { image_url: imageUrl })
}

// 人脸检测
export function detectFaces(imageUrl) {
  return agentApi.post('/agent/friday/vision/faces', { image_url: imageUrl })
}
