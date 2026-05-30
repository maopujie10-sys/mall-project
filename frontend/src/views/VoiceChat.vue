<template>
  <div class="voice-shell">
    <div class="voice-header">
      <h2>Voice Chat</h2>
      <span class="conn-status" :class="wsConnected ? 'online' : 'offline'">{{ wsConnected ? 'Connected' : 'HTTP Mode' }}</span>
    </div>

    <!-- Visualizer -->
    <div class="visualizer">
      <div class="viz-ring" :class="{ active: state !== 'idle' }">
        <div class="viz-inner"><span class="viz-state">{{ stateLabel }}</span></div>
        <div class="viz-wave" v-for="i in 24" :key="i" :style="{'--i':i, '--dur':(0.7+Math.random()*0.6)+'s'}"></div>
      </div>
    </div>

    <!-- Controls -->
    <div class="voice-controls">
      <button class="v-btn record" :class="{active:recording}" @click="toggleRecord" :disabled="state==='processing'">
        {{ recording ? 'Stop' : sttCapable ? 'Speak' : 'Record' }}
      </button>
      <button class="v-btn text-btn" @click="showInput=!showInput">Type</button>
    </div>

    <!-- Text fallback -->
    <div v-if="showInput" class="text-row">
      <input v-model="textInput" @keyup.enter="sendText" placeholder="Type and Enter..." class="v-input" />
      <button @click="sendText" class="v-send">Send</button>
    </div>

    <!-- Transcript -->
    <div class="transcript" ref="tsEl">
      <div v-for="(m,i) in messages" :key="i" :class="['msg', m.role]">
        <span class="msg-role">{{ m.role==='user'?'You':'Friday' }}</span>
        <span class="msg-text">{{ m.text }}</span>
        <button v-if="m.role==='assistant'" class="msg-play" @click="speakLocal(m.text)">Play</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, nextTick, computed } from 'vue'
import { agentApi } from '@/api/index'

// ---- State ----
const messages = ref([])
const recording = ref(false)
const showInput = ref(false)
const textInput = ref('')
const state = ref('idle')
const wsConnected = ref(false)

// STT capability detection
const sttCapable = ref(false)

// MediaRecorder for non-Chrome browsers
let mediaRecorder = null
let audioChunks = []

// WebSocket
let ws = null
let pingTimer = null

const stateLabel = computed(() => {
  if (recording.value) return 'Recording...'
  if (state.value === 'processing') return 'Thinking...'
  if (state.value === 'speaking') return 'Speaking...'
  return 'Ready'
})

// ---- Init ----
onMounted(() => {
  // Detect SpeechRecognition (Chrome)
  const SR = window.SpeechRecognition || window.webkitSpeechRecognition
  sttCapable.value = !!SR
  connectWS()
  pingTimer = setInterval(() => { if (ws?.readyState === WebSocket.OPEN) ws.send(JSON.stringify({type:'ping'})) }, 30000)
})

onUnmounted(() => {
  clearInterval(pingTimer)
  if (ws) ws.close()
  window.speechSynthesis?.cancel()
  if (mediaRecorder?.state === 'recording') mediaRecorder.stop()
})

function scrollDown() {
  nextTick(() => { const el = document.querySelector('.transcript'); if (el) el.scrollTop = el.scrollHeight })
}

// ---- WebSocket ----
function connectWS() {
  const proto = location.protocol === 'https:' ? 'wss:' : 'ws:'
  try {
    ws = new WebSocket(`${proto}//${location.host}/agent/voice/ws`)
    ws.onopen = () => { wsConnected.value = true }
    ws.onclose = () => { wsConnected.value = false; setTimeout(connectWS, 3000) }
    ws.onerror = () => { wsConnected.value = false }
    ws.onmessage = (e) => {
      try {
        const d = JSON.parse(e.data)
        if (d.type === 'stt_result' && d.text) {
          messages.value.push({role:'user',text:d.text}); state.value='processing'; scrollDown()
        } else if (d.type === 'llm' && d.text) {
          messages.value.push({role:'assistant',text:d.text}); state.value='idle'; scrollDown()
        } else if (d.type === 'tts' && d.audio) {
          playAudioB64(d.audio)
        } else if (d.type === 'error') {
          state.value = 'idle'
        }
      } catch {}
    }
  } catch { wsConnected.value = false; setTimeout(connectWS, 3000) }
}

// ---- Record (universal: STT API for Chrome, MediaRecorder for others) ----
async function toggleRecord() {
  if (recording.value) { stopRecord(); return }

  if (sttCapable.value) {
    startChromeSTT()
  } else {
    await startMediaRecorder()
  }
}

// Chrome: SpeechRecognition
let recognition = null
function startChromeSTT() {
  const SR = window.SpeechRecognition || window.webkitSpeechRecognition
  recognition = new SR()
  recognition.lang = 'zh-CN'
  recognition.continuous = false
  recognition.interimResults = false
  recognition.onresult = (e) => {
    const text = Array.from(e.results).map(r=>r[0].transcript).join('')
    if (text) sendToAI(text)
  }
  recognition.onerror = (e) => {
    if (e.error !== 'no-speech') sendToAI('') // fallback to text
    stopRecord()
  }
  recognition.onend = () => { recording.value = false }
  recognition.start()
  recording.value = true
}

// Safari/Firefox: MediaRecorder -> upload
async function startMediaRecorder() {
  try {
    const stream = await navigator.mediaDevices.getUserMedia({audio:true})
    mediaRecorder = new MediaRecorder(stream, {mimeType:'audio/webm;codecs=opus'})
    audioChunks = []
    mediaRecorder.ondataavailable = (e) => { if (e.data.size>0) audioChunks.push(e.data) }
    mediaRecorder.onstop = async () => {
      stream.getTracks().forEach(t=>t.stop())
      if (audioChunks.length === 0) { recording.value = false; return }
      const blob = new Blob(audioChunks, {type:'audio/webm'})
      state.value = 'processing'
      try {
        const form = new FormData()
        form.append('file', blob, 'recording.webm')
        const r = await agentApi.post('/agent/voice/stt', form, {
          headers: {'Content-Type':'multipart/form-data'}
        })
        const text = r?.data?.text
        if (text) sendToAI(text)
      } catch { state.value = 'idle' }
      recording.value = false
    }
    mediaRecorder.start()
    recording.value = true
  } catch {
    recording.value = false
    showInput.value = true
  }
}

function stopRecord() {
  if (recognition) { try{recognition.stop()}catch{}; recognition=null }
  if (mediaRecorder?.state === 'recording') mediaRecorder.stop()
  recording.value = false
}

// ---- Send to AI ----
function sendToAI(text) {
  if (!text) return
  messages.value.push({role:'user',text})
  state.value = 'processing'
  scrollDown()
  if (ws?.readyState === WebSocket.OPEN) {
    ws.send(JSON.stringify({type:'text',text}))
  } else {
    // HTTP fallback
    agentApi.post('/agent/chat',{message:text,mode:'smart'}).then(r=>{
      const reply = r?.data?.response || r?.data?.content || 'Got it.'
      messages.value.push({role:'assistant',text:reply})
      state.value = 'idle'
      scrollDown()
    }).catch(()=>{
      messages.value.push({role:'assistant',text:'Unable to reach AI.'})
      state.value = 'idle'
    })
  }
}

function sendText() {
  const t = textInput.value.trim()
  if (!t) return
  textInput.value = ''
  sendToAI(t)
}

// ---- TTS (cross-browser: speechSynthesis) ----
function speakLocal(text) {
  window.speechSynthesis?.cancel()
  const u = new SpeechSynthesisUtterance(text.slice(0,500))
  u.lang = 'zh-CN'; u.rate = 1.0; u.pitch = 1.0
  u.onstart = () => { state.value = 'speaking' }
  u.onend = () => { state.value = 'idle' }
  u.onerror = () => { state.value = 'idle' }
  window.speechSynthesis?.speak(u)
}

function playAudioB64(b64) {
  try {
    const a = new Audio('data:audio/mp3;base64,'+b64)
    a.onplay = () => { state.value = 'speaking' }
    a.onended = () => { state.value = 'idle' }
    a.play()
  } catch {}
}
</script>

<style scoped>
.voice-shell{display:flex;flex-direction:column;height:calc(100vh - 80px);padding:16px;max-width:600px;margin:0 auto}
.voice-header{display:flex;justify-content:space-between;align-items:center;margin-bottom:8px}
.voice-header h2{font-size:18px;color:#e0e0ff;margin:0}
.conn-status{font-size:11px;padding:4px 10px;border-radius:12px}
.conn-status.online{background:rgba(82,196,26,.15);color:#52c41a}
.conn-status.offline{background:rgba(255,179,0,.15);color:#ffb300}
.visualizer{display:flex;justify-content:center;padding:16px 0}
.viz-ring{position:relative;width:110px;height:110px;border-radius:50%;border:2px solid rgba(102,126,234,.2);display:flex;align-items:center;justify-content:center;transition:.3s}
.viz-ring.active{border-color:rgba(102,200,234,.6);box-shadow:0 0 40px rgba(102,126,234,.3)}
.viz-inner{width:72px;height:72px;border-radius:50%;background:rgba(102,126,234,.1);display:flex;align-items:center;justify-content:center}
.viz-state{font-size:11px;color:#a0b4ff;text-align:center}
.viz-wave{position:absolute;width:2px;background:rgba(102,126,234,.35);transform-origin:bottom;animation:wave var(--dur,1s) ease-in-out infinite;animation-delay:calc(var(--i)*.08s);left:calc(50% + cos(calc(var(--i)*15deg))*46px);top:calc(50% + sin(calc(var(--i)*15deg))*46px);height:6px}
.viz-ring.active .viz-wave{background:rgba(102,200,234,.6)}
.voice-controls{display:flex;gap:12px;justify-content:center;margin:8px 0}
.v-btn{padding:12px 28px;border-radius:24px;border:none;font-size:14px;cursor:pointer;transition:.2s}
.v-btn.record{background:#667eea;color:#fff}
.v-btn.record.active{background:#ff4d4f;animation:pulse 1s infinite}
.v-btn.text-btn{background:rgba(255,255,255,.1);color:#a0b4ff;border:1px solid rgba(102,126,234,.3)}
.v-btn:disabled{opacity:.4;cursor:not-allowed}
.text-row{display:flex;gap:8px;margin:8px 0}
.v-input{flex:1;padding:10px 14px;border-radius:20px;border:1px solid rgba(102,126,234,.3);background:rgba(255,255,255,.05);color:#fff;font-size:14px;outline:none}
.v-send{padding:10px 18px;border-radius:20px;border:none;background:#667eea;color:#fff;font-size:14px;cursor:pointer}
.transcript{flex:1;overflow-y:auto;margin-top:12px}
.msg{display:flex;align-items:flex-start;gap:8px;padding:8px 0;border-bottom:1px solid rgba(255,255,255,.04)}
.msg-role{font-size:11px;color:#667eea;min-width:50px;font-weight:600}
.msg.user .msg-role{color:#52c41a}
.msg-text{flex:1;font-size:14px;line-height:1.4}
.msg-play{background:none;border:1px solid rgba(102,126,234,.3);color:#667eea;padding:2px 8px;border-radius:10px;font-size:11px;cursor:pointer}
@keyframes wave{0%,100%{opacity:.15;transform:scaleY(.3)}50%{opacity:1;transform:scaleY(1.5)}}
@keyframes pulse{0%,100%{box-shadow:0 0 0 0 rgba(255,77,79,.4)}50%{box-shadow:0 0 0 12px rgba(255,77,79,0)}}
</style>
