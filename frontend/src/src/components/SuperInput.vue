<template>
  <div class="super-input-bar" @dragover.prevent="isDragging = true" @dragleave.prevent="isDragging = false" @drop.prevent="onDrop">
    <div class="mode-tabs">
      <button v-for="m in modes" :key="m.id" class="mode-tab" :class="{ active: currentMode === m.id, listening: m.id === 'voice' && isListening, recording: m.id === 'camera' && isRecording }" @click="m.id === 'voice' ? toggleVoice() : m.id === 'camera' ? toggleCamera() : switchMode(m.id)">{{ m.icon }} {{ m.label }}</button>
    </div>
    <div v-if="files.length" class="file-pills">
      <span v-for="(f, i) in files" :key="i" class="file-pill">{{ f.type === 'image' ? '' : f.type === 'video' ? '' : '' }} {{ f.name }} <button class="pill-remove" @click="files.splice(i, 1)">x</button></span>
    </div>
    <Transition name="fade"><div v-if="isDragging" class="drop-hint"><div class="drop-icon">drop</div><div>{{ \('common.title') }}</div></div></Transition>

    <Transition name="fade">
      <div v-if="showCamera" class="camera-preview">
        <video ref="videoEl" autoplay playsinline class="camera-video"></video>
        <div class="camera-controls">
          <button class="cam-btn capture" @click="capturePhoto"></button>
          <button class="cam-btn close" @click="stopCamera"></button>
        </div>
        <canvas ref="canvasEl" style="display:none"></canvas>
      </div>
    </Transition>

    <Transition name="fade">
      <div v-if="isListening" class="voice-indicator">
        <span class="voice-pulse">{{ \('common.title') }}</span>
        <span>... </span>
      </div>
    </Transition>

    <div class="input-row">
      <span class="input-prefix">{{ currentMode === 'cmd' ? '>' : currentMode === 'voice' ? 'mic' : currentMode === 'camera' ? 'cam' : '' }}</span>
      <input ref="inputEl" v-model="text" :placeholder="isListening ? '...' : placeholders[currentMode]" @keydown.enter.exact="send" @keydown.esc="currentMode = 'chat'' :disabled="disabled || isListening" class="main-input" />
      <input ref="fileInput" type="file" multiple hidden @change="onFilePick" accept="image/*,video/*,.pdf,.doc,.docx,.txt,.json,.csv,.md" />
      <button class="action-btn" @click="fileInput.click()" title=''>+</button>
      <button class="action-btn send-btn" @click="send" :disabled="!canSend">></button>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onBeforeUnmount } from 'vue'

const emit = defineEmits(['send'])
const props = defineProps({ disabled: { type: Boolean, default: false } })

const text = ref('')
const currentMode = ref('chat')
const files = ref([])
const isDragging = ref(false)
const inputEl = ref(null)
const fileInput = ref(null)
const videoEl = ref(null)
const canvasEl = ref(null)

const modes = [
  { id: 'chat', icon: 'chat', label: '' },
  { id: 'cmd', icon: 'cmd', label: '' },
  { id: 'image', icon: 'img', label: '' },
  { id: 'video', icon: 'vid', label: '' },
  { id: 'voice', icon: 'mic', label: '' },
  { id: 'camera', icon: 'cam', label: '' },
]

const placeholders = {
  chat: ' AI ...',
  cmd: '...',
  image: '...',
  video: '...',
  voice: '',
  camera: '',
}

// =====  =====
const isListening = ref(false)
let recognition = null

function initRecognition() {
  const SR = window.SpeechRecognition || window.webkitSpeechRecognition
  if (!SR) return null
  const rec = new SR()
  rec.lang = 'zh-CN'
  rec.continuous = true
  rec.interimResults = true
  rec.maxAlternatives = 1
  rec.onresult = (event) => {
    let finalText = ''
    for (let i = event.resultIndex; i < event.results.length; i++) {
      finalText += event.results[i][0].transcript
    }
    text.value = finalText
  }
  rec.onerror = (event) => {
    if (event.error === 'no-speech' || event.error === 'aborted') {
      stopListening()
    }
  }
  rec.onend = () => {
    if (isListening.value) {
      try { rec.start() } catch (e) { stopListening() }
    }
  }
  return rec
}

function toggleVoice() {
  if (isListening.value) { stopListening(); return }
  if (!recognition) recognition = initRecognition()
  if (!recognition) {
    alert(' Chrome ')
    return
  }
  currentMode.value = 'voice'
  try {
    recognition.start()
    isListening.value = true
    text.value = ''
  } catch (e) {
    isListening.value = false
  }
}

function stopListening() {
  isListening.value = false
  if (recognition) {
    try { recognition.stop() } catch (e) { /* ignore */ }
  }
  if (currentMode.value === 'voice') currentMode.value = 'chat'
}

// =====  =====
const showCamera = ref(false)
const isRecording = ref(false)
let mediaStream = null

async function toggleCamera() {
  if (showCamera.value) { stopCamera(); return }
  try {
    mediaStream = await navigator.mediaDevices.getUserMedia({
      video: { facingMode: 'environment', width: { ideal: 1280 }, height: { ideal: 720 } }
    })
    currentMode.value = 'camera'
    showCamera.value = true
    isRecording.value = true
    await new Promise(r => setTimeout(r, 100))
    if (videoEl.value) videoEl.value.srcObject = mediaStream
  } catch (e) {
    alert('')
    isRecording.value = false
    currentMode.value = 'chat'
  }
}

function stopCamera() {
  isRecording.value = false
  showCamera.value = false
  if (mediaStream) {
    mediaStream.getTracks().forEach(t => t.stop())
    mediaStream = null
  }
  if (currentMode.value === 'camera') currentMode.value = 'chat'
}

function capturePhoto() {
  if (!videoEl.value || !canvasEl.value) return
  const video = videoEl.value
  const canvas = canvasEl.value
  canvas.width = video.videoWidth
  canvas.height = video.videoHeight
  const ctx = canvas.getContext('2d')
  ctx.drawImage(video, 0, 0)
  canvas.toBlob((blob) => {
    const file = new File([blob], 'photo_' + Date.now() + '.jpg', { type: 'image/jpeg' })
    files.value.push({ name: file.name, size: file.size, type: 'image', file })
  }, 'image/jpeg', 0.9)
  stopCamera()
}

// =====  =====
function switchMode(mode) {
  if (isListening.value) stopListening()
  if (showCamera.value) stopCamera()
  currentMode.value = mode
  setTimeout(() => inputEl.value && inputEl.value.focus(), 50)
}

// =====  =====
const canSend = computed(() => text.value.trim() || files.value.length)

function send() {
  if (!canSend.value) return
  emit('send', { text: text.value.trim(), mode: currentMode.value, files: [...files.value] })
  text.value = ''
  files.value = []
  if (isListening.value) stopListening()
  if (showCamera.value) stopCamera()
  currentMode.value = 'chat'
}

// =====  =====
function onFilePick(e) {
  addFiles(e.target.files)
  e.target.value = ''
}
function onDrop(e) {
  isDragging.value = false
  addFiles(e.dataTransfer.files)
}
function addFiles(fileList) {
  for (const f of fileList) {
    const type = f.type.startsWith('image/') ? 'image' : f.type.startsWith('video/') ? 'video' : 'file'
    files.value.push({ name: f.name, size: f.size, type, file: f })
  }
}

function speakText(t){if(!window.speechSynthesis)return;window.speechSynthesis.cancel();var u=new SpeechSynthesisUtterance(t);u.lang="zh-CN";u.rate=1.1;window.speechSynthesis.speak(u)}defineExpose({speakText})

onBeforeUnmount(() => {
  stopListening()
  stopCamera()
})
</script>

<style scoped>
.super-input-bar { background: var(--bg-card); border-top: 1px solid var(--border-color); padding: 10px 16px 12px; position: relative }
.mode-tabs { display: flex; gap: 4px; margin-bottom: 8px; flex-wrap: wrap }
.mode-tab { border: none; background: transparent; color: var(--text-muted); font-size: 11px; padding: 3px 10px; border-radius: 12px; cursor: pointer; transition: all .15s }
.mode-tab:hover { background: rgba(102,126,234,.08); color: #667eea }
.mode-tab.active { background: rgba(102,126,234,.15); color: #667eea; font-weight: 600 }
.mode-tab.listening { background: rgba(255,77,79,.15); color: #ff4d4f; animation: pulse-mic .8s ease-in-out infinite }
.mode-tab.recording { background: rgba(82,196,26,.15); color: #52c41a; animation: pulse-mic .8s ease-in-out infinite }
@keyframes pulse-mic { 0%,100%{opacity:1} 50%{opacity:.5} }
.file-pills { display: flex; flex-wrap: wrap; gap: 6px; margin-bottom: 8px }
.file-pill { display: inline-flex; align-items: center; gap: 4px; padding: 2px 8px; border-radius: 10px; background: rgba(102,126,234,.08); font-size: 11px; color: #667eea }
.pill-remove { border: none; background: none; color: var(--text-muted); cursor: pointer; font-size: 14px; padding: 0 2px }
.drop-hint { position: absolute; inset: 0; background: rgba(102,126,234,.12); backdrop-filter: blur(4px); display: flex; flex-direction: column; align-items: center; justify-content: center; z-index: 10; border-radius: 8px; color: #667eea; font-size: 14px; font-weight: 500 }
.drop-icon { font-size: 32px; margin-bottom: 6px }

.camera-preview { margin-bottom: 8px; border-radius: 12px; overflow: hidden; border: 2px solid #52c41a; position: relative; background: #000 }
.camera-video { width: 100%; max-height: 240px; display: block; object-fit: cover }
.camera-controls { display: flex; gap: 8px; padding: 8px; justify-content: center; background: rgba(0,0,0,.7) }
.cam-btn { border: none; border-radius: 8px; padding: 6px 16px; cursor: pointer; font-size: 13px; transition: all .15s }
.cam-btn.capture { background: #52c41a; color: #fff }
.cam-btn.capture:hover { background: #389e0d }
.cam-btn.close { background: rgba(255,255,255,.2); color: #fff }
.cam-btn.close:hover { background: rgba(255,255,255,.35) }

.voice-indicator { display: flex; align-items: center; gap: 8px; padding: 8px 16px; margin-bottom: 8px; border-radius: 10px; background: rgba(255,77,79,.08); color: #ff4d4f; font-size: 13px }
.voice-pulse { width: 10px; height: 10px; border-radius: 50%; background: #ff4d4f; animation: voice-pulse 1s ease-in-out infinite }
@keyframes voice-pulse { 0%,100%{transform:scale(1);opacity:1} 50%{transform:scale(1.8);opacity:.4} }

.input-row { display: flex; align-items: center; gap: 8px; background: var(--bg-page); border-radius: 12px; padding: 0 12px; border: 1px solid var(--border-color); transition: border-color .2s }
.input-row:focus-within { border-color: #667eea }
.input-prefix { font-size: 16px; color: #667eea; font-weight: 600; flex-shrink: 0 }
.main-input { flex: 1; border: none; background: transparent; color: var(--text-primary); font-size: 13px; padding: 12px 0; outline: none; font-family: inherit }
.main-input::placeholder { color: var(--text-muted) }
.main-input:disabled { opacity: .5 }
.action-btn { border: none; background: transparent; color: var(--text-muted); font-size: 16px; cursor: pointer; padding: 4px; border-radius: 6px; transition: all .15s }
.action-btn:hover { background: rgba(102,126,234,.08); color: #667eea }
.send-btn { width: 28px; height: 28px; border-radius: 50%; background: linear-gradient(135deg, #667eea, #764ba2); color: #fff; font-size: 14px; display: flex; align-items: center; justify-content: center }
.send-btn:hover { opacity: .9; transform: scale(1.05) }
.send-btn:disabled { background: var(--border-color); color: var(--text-muted); transform: none }
.fade-enter-active, .fade-leave-active { transition: opacity .2s }
.fade-enter-from, .fade-leave-to { opacity: 0 }
</style>