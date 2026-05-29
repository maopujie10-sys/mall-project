<template>
  <div class="voice-chat-page">
    <div class="vc-header">
      <h2>🎙️ 实时语音对话</h2>
      <p>WebSocket流式 · STT→LLM→TTS · 像打电话一样自然</p>
      <div class="vc-status">
        <span class="status-dot" :class="{ connected: wsConnected }"></span>
        {{ wsConnected ? '已连接' : '未连接' }}
      </div>
    </div>

    <div class="vc-main">
      <!-- 对话记录 -->
      <div class="vc-messages" ref="msgList">
        <div v-if="messages.length === 0" class="vc-empty">
          <div class="empty-icon">🎤</div>
          <p>点击下方按钮开始语音对话</p>
          <p class="empty-sub">实时识别→AI回复→语音播报</p>
        </div>
        <div v-for="(msg, i) in messages" :key="i" class="vc-msg" :class="msg.role">
          <div class="vc-avatar">{{ msg.role === 'user' ? '👤' : '🤖' }}</div>
          <div class="vc-bubble">
            <div class="vc-text">{{ msg.text }}</div>
            <div class="vc-meta">
              {{ msg.time }}
              <button v-if="msg.role === 'assistant' && msg.audio" class="vc-replay" @click="playAudio(msg.audio)">🔊 重播</button>
            </div>
          </div>
        </div>
        <div v-if="listening" class="vc-msg assistant">
          <div class="vc-avatar">🤖</div>
          <div class="vc-bubble listening">
            <span class="step-text">{{ currentStep }}</span>
            <span class="dot"></span><span class="dot"></span><span class="dot"></span>
          </div>
        </div>
      </div>

      <!-- 控制区 -->
      <div class="vc-controls">
        <button class="vc-record-btn" :class="{ recording: isRecording }" @click="toggleRecording" :disabled="!wsConnected">
          <span class="btn-icon">{{ isRecording ? '⏹️' : '🎤' }}</span>
          <span class="btn-label">{{ isRecording ? '停止' : '按住说话' }}</span>
        </button>
        <div v-if="isRecording" class="recording-indicator">
          <div class="wave-bar" v-for="i in 5" :key="i" :style="{ animationDelay: i * 0.1 + 's' }"></div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, nextTick } from 'vue'
import { ElMessage } from 'element-plus'

const messages = ref([])
const isRecording = ref(false)
const listening = ref(false)
const currentStep = ref('')
const wsConnected = ref(false)

let ws = null
let mediaRecorder = null
let audioChunks = []
const msgList = ref(null)

function connectWS() {
  const protocol = location.protocol === 'https:' ? 'wss:' : 'ws:'
  const wsUrl = `${protocol}//${location.host}/agent/voice/ws`

  ws = new WebSocket(wsUrl)

  ws.onopen = () => {
    wsConnected.value = true
    ElMessage.success('语音服务已连接')
    // 心跳
    setInterval(() => {
      if (ws.readyState === WebSocket.OPEN) ws.send(JSON.stringify({ type: 'ping' }))
    }, 30000)
  }

  ws.onclose = () => {
    wsConnected.value = false
    setTimeout(connectWS, 3000)
  }

  ws.onmessage = (event) => {
    const data = JSON.parse(event.data)

    if (data.type === 'user_text') {
      messages.value.push({ role: 'user', text: data.text, time: new Date().toLocaleTimeString() })
      scrollDown()
    } else if (data.type === 'reply_text') {
      messages.value.push({ role: 'assistant', text: data.text, time: new Date().toLocaleTimeString(), audio: null })
    } else if (data.type === 'voice_reply') {
      const lastMsg = messages.value[messages.value.length - 1]
      if (lastMsg && lastMsg.role === 'assistant') {
        lastMsg.audio = data.audio_b64
      }
      listening.value = false
      currentStep.value = ''
      scrollDown()
      if (data.audio_b64) playAudio(data.audio_b64)
    } else if (data.type === 'status') {
      currentStep.value = data.message
    } else if (data.type === 'error') {
      listening.value = false
      ElMessage.error(data.message)
    }
  }

  ws.onerror = () => {
    wsConnected.value = false
  }
}

async function toggleRecording() {
  if (isRecording.value) {
    stopRecording()
  } else {
    startRecording()
  }
}

async function startRecording() {
  try {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
    mediaRecorder = new MediaRecorder(stream, { mimeType: 'audio/webm' })
    audioChunks = []

    mediaRecorder.ondataavailable = (e) => {
      if (e.data.size > 0) audioChunks.push(e.data)
    }

    mediaRecorder.onstop = async () => {
      stream.getTracks().forEach(t => t.stop())
      if (audioChunks.length === 0) return

      const blob = new Blob(audioChunks, { type: 'audio/webm' })
      const reader = new FileReader()
      reader.onloadend = () => {
        const b64 = reader.result.split(',')[1]
        if (ws && ws.readyState === WebSocket.OPEN) {
          listening.value = true
          currentStep.value = '正在发送...'
          ws.send(JSON.stringify({ type: 'voice', audio_b64: b64, fmt: 'webm' }))
        }
      }
      reader.readAsDataURL(blob)
    }

    mediaRecorder.start()
    isRecording.value = true
  } catch (e) {
    ElMessage.error('麦克风权限未开启: ' + e.message)
  }
}

function stopRecording() {
  if (mediaRecorder && mediaRecorder.state !== 'inactive') {
    mediaRecorder.stop()
  }
  isRecording.value = false
}

function playAudio(b64) {
  if (!b64) return
  const audio = new Audio('data:audio/mp3;base64,' + b64)
  audio.play()
}

function scrollDown() {
  nextTick(() => {
    if (msgList.value) msgList.value.scrollTop = msgList.value.scrollHeight
  })
}

onMounted(() => connectWS())
onUnmounted(() => {
  if (ws) ws.close()
  if (mediaRecorder && mediaRecorder.state !== 'inactive') mediaRecorder.stop()
})
</script>

<style scoped>
.voice-chat-page {
  max-width: 600px; margin: 0 auto; padding: 20px;
  height: calc(100vh - 40px); display: flex; flex-direction: column;
}
.vc-header { text-align: center; margin-bottom: 16px; }
.vc-header h2 { font-size: 22px; color: #e0e0ff; margin: 0; }
.vc-header p { font-size: 12px; color: rgba(255,255,255,0.5); margin: 4px 0; }
.vc-status { font-size: 12px; margin-top: 6px; }
.status-dot { width: 8px; height: 8px; border-radius: 50%; display: inline-block; margin-right: 6px; background: #ff4444; }
.status-dot.connected { background: #44ff44; box-shadow: 0 0 8px #44ff44; }
.vc-main { flex: 1; display: flex; flex-direction: column; overflow: hidden; }
.vc-messages { flex: 1; overflow-y: auto; padding: 12px 0; }
.vc-empty { text-align: center; padding: 40px 20px; color: rgba(255,255,255,0.4); }
.empty-icon { font-size: 48px; margin-bottom: 12px; }
.empty-sub { font-size: 11px; margin-top: 4px; }
.vc-msg { display: flex; gap: 10px; margin-bottom: 14px; }
.vc-msg.user { flex-direction: row-reverse; }
.vc-avatar { width: 32px; height: 32px; border-radius: 50%; background: rgba(102,126,234,0.2); display: flex; align-items: center; justify-content: center; font-size: 16px; flex-shrink: 0; }
.vc-bubble { max-width: 75%; padding: 10px 14px; border-radius: 14px; background: rgba(255,255,255,0.08); border: 1px solid rgba(255,255,255,0.1); }
.vc-msg.user .vc-bubble { background: rgba(102,126,234,0.2); border-color: rgba(102,126,234,0.3); }
.vc-text { font-size: 14px; color: #e0e0e0; line-height: 1.5; }
.vc-meta { font-size: 10px; color: rgba(255,255,255,0.3); margin-top: 4px; display: flex; align-items: center; gap: 8px; }
.vc-replay { background: none; border: 1px solid rgba(255,255,255,0.2); color: rgba(255,255,255,0.5); border-radius: 10px; padding: 2px 8px; font-size: 10px; cursor: pointer; }
.vc-replay:hover { background: rgba(255,255,255,0.1); }
.vc-bubble.listening { display: flex; align-items: center; gap: 6px; }
.step-text { font-size: 12px; color: rgba(255,255,255,0.5); }
.dot { width: 6px; height: 6px; border-radius: 50%; background: rgba(102,126,234,0.6); animation: dotBounce 1.4s infinite; }
.dot:nth-child(2) { animation-delay: 0.2s; }
.dot:nth-child(3) { animation-delay: 0.4s; }
@keyframes dotBounce { 0%, 80%, 100% { transform: scale(0); } 40% { transform: scale(1); } }
.vc-controls { padding: 16px 0; display: flex; flex-direction: column; align-items: center; gap: 12px; }
.vc-record-btn {
  width: 80px; height: 80px; border-radius: 50%; border: 3px solid rgba(102,126,234,0.4);
  background: rgba(15,15,35,0.9); cursor: pointer; display: flex; flex-direction: column; align-items: center;
  justify-content: center; transition: all 0.3s; color: #e0e0ff;
}
.vc-record-btn:hover { border-color: rgba(102,126,234,0.8); box-shadow: 0 0 30px rgba(102,126,234,0.3); }
.vc-record-btn.recording { border-color: #ff4444; animation: pulse 1.5s infinite; }
@keyframes pulse { 0%, 100% { box-shadow: 0 0 0 0 rgba(255,68,68,0.5); } 50% { box-shadow: 0 0 0 20px rgba(255,68,68,0); } }
.btn-icon { font-size: 28px; }
.btn-label { font-size: 10px; margin-top: 2px; }
.recording-indicator { display: flex; gap: 4px; align-items: flex-end; height: 30px; }
.wave-bar { width: 4px; border-radius: 2px; background: linear-gradient(to top, #ff4444, #667eea); animation: waveAnim 0.8s ease-in-out infinite; height: 10px; }
@keyframes waveAnim { 0%, 100% { height: 8px; } 50% { height: 28px; } }

@media (max-width: 768px) {
  .voice-chat-page { padding: 10px; height: calc(100vh - 20px); }
  .vc-bubble { max-width: 85%; }
}
</style>
