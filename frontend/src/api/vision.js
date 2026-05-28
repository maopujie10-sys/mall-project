import { agentApi } from "./index"

// 图片分析（OCR + 物体检测 + 人脸检测）
export function analyzeImage(imageUrl) {
  return agentApi.get("/agent/friday/vision/analyze", { params: { url: imageUrl } })
}

// 上传图片并分析
export function uploadAndAnalyze(file) {
  const formData = new FormData()
  formData.append("file", file)
  return agentApi.post("/agent/friday/vision/upload", formData, {
    headers: { "Content-Type": "multipart/form-data" },
  })
}

// OCR 文字识别
export function ocrRecognize(imageUrl) {
  return agentApi.get("/agent/friday/vision/ocr", { params: { image_url: imageUrl } })
}

// 视频分析
export function analyzeVideo(videoUrl) {
  return agentApi.get("/agent/friday/vision/video", { params: { video_url: videoUrl } })
}

// 物体检测
export function detectObjects(imageUrl) {
  return agentApi.get("/agent/friday/vision/objects", { params: { image_url: imageUrl } })
}

// 人脸检测
export function detectFaces(imageUrl) {
  return agentApi.get("/agent/friday/vision/faces", { params: { image_url: imageUrl } })
}
