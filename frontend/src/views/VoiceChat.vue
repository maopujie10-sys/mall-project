<template>
  <div class="voice-shell">
    <div class="voice-header">
      <h2>Voice Chat</h2>
      <span class="conn-status" :class="connected ? 'online' : 'offline'">{{ connected ? 'Connected' : 'Disconnected' }}</span>
    </div>

    <!-- Audio Visualizer -->
    <div class="visualizer">
      <div class="viz-ring" :class="{ active: isListening || isSpeaking }">
        <div class="viz-inner">
          <span class="viz-state">{{ stateText }}</span>
        </div>
        <div class="viz-wave" v-for="i in 24" :key="i" :style="{ '--i': i, animationDuration: 0.8 + Math.random() * 0.6 + 's' }"></div>
      </div>
    </div>

    <!-- Controls -->
    <div class="voice-controls">
      <button class="v-btn record" :class="{ active: isListening }" @click="toggleListen" :disabled="!connected">
        {{ isListening ? 'Stop' : 'Listen' }}
      </button>
      <button class="v-btn speak-btn" @click="toggleSpeak" :disabled="!connected">
        Text Input
      </button>
    </div>

    <!-- Text Input -->
    <div v-if="showTextInput" class="text-input-row">
      <input v-model="textInput" @keyup.enter="sendText" placeholder="Type and press Enter..." class="v-text-input" />
      <button @click="sendText" class="v-send">Send</button>
    </div>

    <!-- Transcript -->
    <div class="transcript" ref="transcriptEl">
      <div v-for="(msg, i) in messages" :key="i" :class="['msg', msg.role]">
        <span class="msg-role">{{ msg.role === 'user' ? 'You' : 'Friday' }}</span>
        <span class="msg-text">{{ msg.text }}</span>
        <button v-if="msg.role === 'assistant' && msg.text" class="msg-speak" @click="speakText(msg.text)">Play</button>
      </div>
    </div>

    <!-- Log -->
    <div class="voice-log" v-if="debugLog.length">
      <div v-for="(l, i) in debugLog" :key="i" class="log-line">{{ l }}</div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, nextTick } from 'vue'
import { agentApi } from '@/api/index'

const connected = ref(false)
const isListening = ref(false)
const isSpeaking = ref(false)
const showTextInput = ref(false)
const textInput = ref('')
const messages = ref([])
const debugLog = ref([])

let ws = null
let pingTimer = null
let sttRecognition = null
let sttText = ''

const stateText = ref('Idle')

function log(msg) {
  debugLog.value.push(`[${new Date().toLocaleTimeString()}] ${msg}`)
  if (debugLog.value.length > 20) debugLog.value.shift()
}

function connect() {
  const proto = location.protocol === 'https:' ? 'wss:' : 'ws:'
  const wsUrl = `${proto}//${location.host}/agent/voice/ws`
  log('Connecting...')
  try {
    ws = new WebSocket(wsUrl)
    ws.onopen = () => {
      connected.value = true
      stateText.value = 'Ready'
      log('Connected')
    }
    ws.onclose = () => {
      connected.value = false
      stateText.value = 'Disconnected'
      log('Disconnected, reconnecting...')
      setTimeout(connect, 3000)
    }
    ws.onerror = () => { connected.value = false; log('Connection error') }
    ws.onmessage = (e) => {
      try {
        const data = JSON.parse(e.data)
        if (data.type === 'stt_result') {
          messages.value.push({ role: 'user', text: data.text })
          stateText.value = 'Processing...'
          scrollDown()
        } else if (data.type === 'llm') {
          messages.value.push({ role: 'assistant', text: data.text })
          stateText.value = 'Ready'
          scrollDown()
        } else if (data.type === 'tts') {
          playAudioBase64(data.audio)
        } else if (data.type === 'error') {
          log('Server: ' + data.text)
          stateText.value = 'Error'
        }
      } catch {}
    }
  } catch (e) {
    log('Failed: ' + e.message)
    setTimeout(connect, 3000)
  }
}

function scrollDown() {
  nextTick(() => {
    const el = document.querySelector('.transcript')
    if (el) el.scrollTop = el.scrollHeight
  })
}

// === STT: Browser SpeechRecognition or send audio to backend ===
function toggleListen() {
  if (isListening.value) {
    stopListen()
  } else {
    startListen()
  }
}

function startListen() {
  const SR = window.SpeechRecognition || window.webkitSpeechRecognition
  if (SR) {
    // Use browser STT
    sttRecognition = new SR()
    sttRecognition.lang = 'zh-CN'
    sttRecognition.continuous = false
    sttRecognition.interimResults = false
    sttText = ''
    sttRecognition.onresult = (e) => {
      const text = Array.from(e.results).map(r => r[0].transcript).join('')
      sttText = text
      if (text && ws && ws.readyState === WebSocket.OPEN) {
        messages.value.push({ role: 'user', text })
        stateText.value = 'Thinking...'
        ws.send(JSON.stringify({ type: 'text', text }))
        scrollDown()
      }
    }
    sttRecognition.onerror = (e) => {
      log('STT Error: ' + e.error)
      stopListen()
    }
    sttRecognition.onend = () => { isListening.value = false; stateText.value = 'Ready' }
    sttRecognition.start()
    isListening.value = true
    stateText.value = 'Listening...'
    log('Browser STT started')
  } else {
    log('Browser STT not available, use text input')
    showTextInput.value = true
  }
}

function stopListen() {
  if (sttRecognition) {
    try { sttRecognition.stop() } catch {}
    sttRecognition = null
  }
  isListening.value = false
}

// === TTS: Browser speechSynthesis ===
function speakText(text) {
  window.speechSynthesis.cancel()
  const utterance = new SpeechSynthesisUtterance(text.slice(0, 500))
  utterance.lang = 'zh-CN'
  utterance.rate = 1.0
  utterance.pitch = 1.0
  utterance.onstart = () => { isSpeaking.value = true }
  utterance.onend = () => { isSpeaking.value = false }
  utterance.onerror = () => { isSpeaking.value = false }
  window.speechSynthesis.speak(utterance)
}

function toggleSpeak() {
  showTextInput.value = !showTextInput.value
}

async function sendText() {
  const text = textInput.value.trim()
  if (!text) return
  messages.value.push({ role: 'user', text })
  textInput.value = ''
  scrollDown()

  if (ws && ws.readyState === WebSocket.OPEN) {
    stateText.value = 'Thinking...'
    ws.send(JSON.stringify({ type: 'text', text }))
  } else {
    // Fallback: HTTP API
    try {
      const r = await agentApi.post('/agent/chat', { message: text, mode: 'smart' })
      const reply = r?.data?.response || r?.data?.content || 'Got it.'
      messages.value.push({ role: 'assistant', text: reply })
      scrollDown()
    } catch {
      messages.value.push({ role: 'assistant', text: 'Unable to reach AI.' })
    }
  }
}

function playAudioBase64(b64) {
  try {
    const audio = new Audio('data:audio/mp3;base64,' + b64)
    audio.onplay = () => { isSpeaking.value = true }
    audio.onended = () => { isSpeaking.value = false }
    audio.onerror = () => { isSpeaking.value = false }
    audio.play()
  } catch {}
}

onMounted(() => {
  connect()
  pingTimer = setInterval(() => {
    if (ws && ws.readyState === WebSocket.OPEN) ws.send(JSON.stringify({ type: 'ping' }))
  }, 30000)
})
onUnmounted(() => {
  clearInterval(pingTimer)
  if (ws) ws.close()
  window.speechSynthesis.cancel()
})
</script>

<style scoped>
.voice-shell {
  display: flex;
  flex-direction: column;
  height: calc(100vh - 80px);
  padding: 16px;
  max-width: 600px;
  margin: 0 auto;
}
.voice-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}
.voice-header h2 { font-size: 18px; color: #e0e0ff; margin: 0; }
.conn-status { font-size: 11px; padding: 4px 10px; border-radius: 12px; }
.conn-status.online { background: rgba(82,196,26,0.15); color: #52c41a; }
.conn-status.offline { background: rgba(255,77,79,0.15); color: #ff4d4f; }

/* Visualizer */
.visualizer {
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 20px 0;
}
.viz-ring {
  position: relative;
  width: 120px; height: 120px;
  border-radius: 50%;
  border: 2px solid rgba(102,126,234,0.25);
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s;
}
.viz-ring.active {
  border-color: rgba(102,200,234,0.6);
  box-shadow: 0 0 40px rgba(102,126,234,0.3);
}
.viz-inner {
  width: 80px; height: 80px;
  border-radius: 50%;
  background: rgba(102,126,234,0.1);
  display: flex;
  align-items: center;
  justify-content: center;
}
.viz-state { font-size: 12px; color: #a0b4ff; }
.viz-wave {
  position: absolute;
  width: 2px;
  background: rgba(102,126,234,0.4);
  transform-origin: bottom center;
  animation: waveAnim var(--animation-duration, 1s) ease-in-out infinite;
  animation-delay: calc(var(--i) * 0.08s);
  left: calc(50% + cos(calc(var(--i) * 15deg)) * 50px);
  top: calc(50% + sin(calc(var(--i) * 15deg)) * 50px);
  height: 8px;
}
.viz-ring.active .viz-wave { animation-play-state: running; }

/* Controls */
.voice-controls {
  display: flex;
  gap: 12px;
  justify-content: center;
  margin: 8px 0;
}
.v-btn {
  padding: 12px 28px;
  border-radius: 24px;
  border: none;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.2s;
}
.v-btn.record { background: #667eea; color: #fff; }
.v-btn.record.active { background: #ff4d4f; animation: pulse 1s infinite; }
.v-btn.speak-btn { background: rgba(255,255,255,0.1); color: #a0b4ff; border: 1px solid rgba(102,126,234,0.3); }
.v-btn:disabled { opacity: 0.4; cursor: not-allowed; }

/* Text Input */
.text-input-row {
  display: flex;
  gap: 8px;
  margin: 8px 0;
}
.v-text-input {
  flex: 1;
  padding: 10px 14px;
  border-radius: 20px;
  border: 1px solid rgba(102,126,234,0.3);
  background: rgba(255,255,255,0.05);
  color: #fff;
  font-size: 14px;
  outline: none;
}
.v-send {
  padding: 10px 18px;
  border-radius: 20px;
  border: none;
  background: #667eea;
  color: #fff;
  font-size: 14px;
  cursor: pointer;
}

/* Transcript */
.transcript {
  flex: 1;
  overflow-y: auto;
  margin-top: 12px;
  padding: 8px 0;
}
.msg {
  display: flex;
  align-items: flex-start;
  gap: 8px;
  padding: 8px 0;
  border-bottom: 1px solid rgba(255,255,255,0.04);
}
.msg-role {
  font-size: 11px;
  color: #667eea;
  min-width: 50px;
  font-weight: 600;
}
.msg.user .msg-role { color: #52c41a; }
.msg-text { flex: 1; font-size: 14px; line-height: 1.4; }
.msg-speak {
  background: none;
  border: 1px solid rgba(102,126,234,0.3);
  color: #667eea;
  padding: 2px 8px;
  border-radius: 10px;
  font-size: 11px;
  cursor: pointer;
}

.voice-log {
  max-height: 80px;
  overflow-y: auto;
  font-size: 10px;
  color: rgba(255,255,255,0.3);
  margin-top: 8px;
  border-top: 1px solid rgba(255,255,255,0.05);
  padding-top: 4px;
}
.log-line { line-height: 1.6; }

@keyframes waveAnim {
  0%,100% { opacity: 0.2; transform: scaleY(0.3); }
  50% { opacity: 1; transform: scaleY(1.5); }
}
@keyframes pulse {
  0%,100% { box-shadow: 0 0 0 0 rgba(255,77,79,0.4); }
  50% { box-shadow: 0 0 0 12px rgba(255,77,79,0); }
}
</style>
