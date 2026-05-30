<template>
  <!-- 鍏ㄥ眬鎮诞AI鍔╂墜 鈥?鏂囧瓧+璇煶+瑙嗛鍏ㄩ泦鎴?-->
  <div class="floating-ai" :class="{ 'chat-open': chatOpen, 'chat-expanded': chatExpanded, 'video-mode': videoActive }">
    <!-- ====== 鎮诞鎸夐挳 ====== -->
    <div
      v-if="!chatOpen"
      class="ai-float-btn"
      @click="openChat"
      @mousedown="startDrag" @touchstart="startDrag"
      :style="{ left: posX + 'px', top: posY + 'px' }"
    >
      <div class="btn-glow"></div>
      <div class="btn-inner">
        <svg width="28" height="28" viewBox="0 0 64 64">
          <defs><linearGradient id="aiGrad2" x1="0" y1="0" x2="1" y2="1"><stop offset="0%" stop-color="#667eea"/><stop offset="100%" stop-color="#764ba2"/></linearGradient></defs>
          <circle cx="32" cy="32" r="28" fill="url(#aiGrad2)"/>
          <text x="32" y="42" text-anchor="middle" font-size="22" font-weight="bold" fill="white">AI</text>
        </svg>
      </div>
      <span class="btn-pulse" v-if="hasUnread"></span>
    </div>

    <!-- ====== 鑱婂ぉ闈㈡澘 ====== -->
    <transition name="slide-up">
      <div v-if="chatOpen" class="ai-chat-panel" :class="{ expanded: chatExpanded, video: videoActive }">
        <!-- 澶撮儴宸ュ叿鏍?-->
        <div class="chat-header" @mousedown="startPanelDrag"><div class="header-scanline"></div>
          <div class="header-left">
            <div class="ai-avatar-small"><div class="avatar-holo"></div>AI</div>
            <div>
              <div class="header-title">{{ voiceActive ? '馃帳 鑱嗗惉涓? : (voiceCallActive ? '馃攰 鏈楄涓? : 'Friday AI 鍔╂墜') }}</div>
              <div class="header-status">{{ voiceActive ? '馃帳 姝ｅ湪鍚綘璇磋瘽...' : (voiceCallActive ? '馃攰 鑷姩鏈楄鍥炲' : '鍦ㄧ嚎 路 闅忔椂涓烘偍鏈嶅姟') }}</div>
            </div>
          </div>
          <div class="header-actions">
                        <button class="header-btn" @click="compareModels" title="妯″瀷瀵规瘮">鈿栵笍</button>
                        <button class="header-btn" @click="toggleVoiceInput" :title="voiceActive ? '鍋滄璇煶' : '璇煶杈撳叆'" :class="{ active: voiceActive }">馃帳</button>
            <button class="header-btn" @click="toggleVoiceCall" :title="voiceCallActive ? '鍏抽棴鏈楄' : '鏈楄鍥炲'" :class="{ active: voiceCallActive }">馃攰</button>
                        <button class="header-btn" @click="toggleExpand" :title="chatExpanded ? '缂╁皬' : '鎵╁ぇ'">
              {{ chatExpanded ? '鈯? : '鈯? }}
            </button>
            <button class="header-btn" @click="minimizeChat" title="鏈€灏忓寲">鈭</button>
            <button class="header-btn close-btn" @click="closeChat" title="鍏抽棴">脳</button>
          </div>
        </div>

                <!-- ====== 娑堟伅鍖?====== -->
        <div class="chat-messages" ref="msgList"><canvas ref="matrixCanvas" class="matrix-bg"></canvas>
          <div v-if="messages.length === 0" class="empty-chat">
            <div class="empty-icon">馃</div>
            <p>浣犲ソ锛佹垜鏄?Friday AI 鍔╂墜</p>
            <p class="empty-sub">鏂囧瓧 路 璇煶 路 瑙嗛 路 浼犲浘 路 浼犳枃浠</p>
            <div class="quick-actions">
              <button @click="quickAsk('鏈嶅姟鍣ㄧ姸鎬佹€庝箞鏍凤紵')">馃搳 鏈嶅姟鍣ㄧ姸鎬</button>
              <button @click="quickAsk('浠婂ぉ鏈夊灏戣鍗曪紵')">馃摝 浠婃棩璁㈠崟</button>
              <button @click="quickAsk('甯垜鍒嗘瀽鏈€杩戠殑寮傚父')">馃攳 寮傚父鍒嗘瀽</button>
              <button @click="quickAsk('鐢熸垚浠婃棩杩愯惀鎶ュ憡')">馃摑 杩愯惀鎶ュ憡</button>
            </div>
          </div>

          <div v-for="(msg, i) in messages" :key="i" class="msg-row" :class="msg.role">
            <div class="msg-avatar">{{ msg.role === 'user' ? '馃懁' : 'AI' }}</div>
            <div class="msg-bubble" :class="msg.role">
              <div class="msg-text" v-html="renderMsg(msg.content)"></div>
              <div class="msg-time">
                {{ msg.time }}
                <span v-if="msg.voice" class="voice-tag">馃帳 璇煶</span>
              </div>
            </div>
            <!-- 璇煶鎾斁鎸夐挳 -->
            <button v-if="msg.role === 'assistant'" class="play-voice-btn" @click="speakText(msg.content)" title="鏈楄">
              馃攰
            </button>
          </div>

          <div v-if="loading" class="msg-row assistant">
            <div class="msg-avatar">AI</div>
            <div class="msg-bubble assistant typing">
              <span class="dot"></span><span class="dot"></span><span class="dot"></span>
            </div>
          </div>
        </div>

        <!-- ====== 杈撳叆鍖?====== -->
        <div v-if="!videoActive" class="chat-input-area">
          <!-- 璇煶杈撳叆鎻愮ず -->
          <div v-if="attachments.length > 0" class="attachments-bar"><div v-for="(att, i) in attachments" :key="i" class="attach-item"><div v-if="att.type === 'image'" class="attach-preview-img"><img :src="att.dataUrl" /><button class="attach-remove" @click="removeAttachment(i)">x</button></div><div v-else-if="att.type === 'video'" class="attach-preview-video"><video :src="att.dataUrl" controls preload="metadata"></video><button class="attach-remove" @click="removeAttachment(i)">x</button></div><div v-else class="attach-tag"><span class="attach-icon">{{ getFileIcon(att.name) }}</span><span class="attach-name">{{ att.name }}</span><span class="attach-size">{{ formatSize(att.size) }}</span><button class="attach-remove" @click="removeAttachment(i)">x</button></div></div></div>
          <div v-if="voiceActive" class="voice-indicator">
            <div class="voice-wave">
              <span v-for="n in 5" :key="n" :style="{ animationDelay: n * 0.1 + 's' }"></span>
            </div>
            <span>姝ｅ湪鑱嗗惉... 鐐瑰嚮楹﹀厠椋庡仠姝</span>
          </div>

          <div class="input-row">
            <!-- 璇煶杈撳叆鎸夐挳 -->
            <button
              class="voice-input-btn"
              :class="{ recording: voiceActive }"
              @click="toggleVoiceInput"
              title="璇煶杈撳叆"
            >
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" :stroke="voiceActive ? '#fff' : '#889'" stroke-width="2">
                <path d="M12 1a3 3 0 0 0-3 3v8a3 3 0 0 0 6 0V4a3 3 0 0 0-3-3z"/>
                <path d="M19 10v2a7 7 0 0 1-14 0v-2"/>
                <line x1="12" y1="19" x2="12" y2="23"/>
                <line x1="8" y1="23" x2="16" y2="23"/>
              </svg>
            </button>

            <textarea
              v-model="inputText"
              @keydown.enter.exact.prevent="sendMessage"
              @keydown.enter.shift.exact="inputText += '\n'"
              :placeholder="voiceActive ? '璇煶璇嗗埆涓?..' : '杈撳叆娑堟伅... (Enter鍙戦€?'"
              rows="1"
              ref="inputBox"
              :disabled="loading || voiceActive"
            ></textarea>

            <button class="send-btn" @click="sendMessage" :disabled="loading || (!inputText.trim() && !attachments.length)">
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
                <path d="M22 2L11 13"/><path d="M22 2l-7 20-4-9-9-4 20-7z"/>
              </svg>
            </button>
          </div>
        </div>
      </div>
    </transition>
  </div>
</template>

<script setup>
import { ref, nextTick, onMounted, onUnmounted, watch } from 'vue'

// === 鐘舵€?===
const chatOpen = ref(false)
const chatExpanded = ref(false)
const messages = ref([])
const inputText = ref('')
const loading = ref(false)
const hasUnread = ref(false)

// 璇煶
const voiceActive = ref(false)
const voiceCallActive = ref(false)
let recognition = null
let synth = null

// 瑙嗛
const videoActive = ref(false)
const videoConnected = ref(false)
const micMuted = ref(false)
const cameraOff = ref(false)
const remoteVideo = ref(null)
const localVideo = ref(null)
let localStream = null
let peerConnection = null

// 浣嶇疆
const posX = ref(0)
const posY = ref(0)
let isDragging = false
let convId = localStorage.getItem('friday_conv_id') || ''
const conversations = ref([])
const showHistory = ref(false)
const selectedTemplate = ref('')
const promptTemplates = ref([])
const imagePreview = ref('')
const showImageUpload = ref(false)
let dragStartX = 0, dragStartY = 0, btnStartX = 0, btnStartY = 0
let panelDragging = false, panelStartX = 0, panelStartY = 0, panelPos = { x: 0, y: 0 }
let floatTimer = null
let floatPaused = false

const STORAGE_KEY = 'friday_floating_chat'

// === 鍒濆鍖?===
onMounted(() => {
  try {
    const saved = localStorage.getItem(STORAGE_KEY)
    if (saved) messages.value = JSON.parse(saved)
  } catch (e) {}
  posX.value = window.innerWidth - 80
  posY.value = window.innerHeight - 180
  initSpeechSynth()
})

onUnmounted(() => {
  stopVoiceInput()
  stopVideoCall()
})

watch(messages, (val) => {
  try { localStorage.setItem(STORAGE_KEY, JSON.stringify(val.slice(-50))) } catch (e) {}
}, { deep: true })

// === 闈㈡澘鎺у埗 ===
function openChat() { if (!isDragging) { floatPaused = false; chatOpen.value = true; hasUnread.value = false; window.dispatchEvent(new CustomEvent("brain:active", {detail:true})); nextTick(() => scrollBottom()) } }
function closeChat() { stopVoiceInput(); stopVideoCall(); chatOpen.value = false; chatExpanded.value = false; window.dispatchEvent(new CustomEvent("brain:active", {detail:false})) }
function minimizeChat() { stopTw(); stopStepAnimation(); chatOpen.value = false }
function toggleExpand() { chatExpanded.value = !chatExpanded.value; nextTick(() => scrollBottom()) }
function startDrag(e) {
  e.preventDefault()
  isDragging = false
  btnStartX = posX.value
  btnStartY = posY.value
  dragStartX = e.touches ? e.touches[0].clientX : e.clientX
  dragStartY = e.touches ? e.touches[0].clientY : e.clientY
  document.onmousemove = onDragMove
  document.onmouseup = onDragUp
  document.ontouchmove = onDragMove
  document.ontouchend = onDragUp
}
function onDragMove(ev) {
  const cx = ev.touches ? ev.touches[0].clientX : ev.clientX
  const cy = ev.touches ? ev.touches[0].clientY : ev.clientY
  const dx = cx - dragStartX, dy = cy - dragStartY
  if (Math.abs(dx) > 8 || Math.abs(dy) > 3) isDragging = true
  if (isDragging) {
    posX.value = Math.max(0, Math.min(window.innerWidth - 60, btnStartX + dx))
    posY.value = Math.max(0, Math.min(window.innerHeight - 60, btnStartY + dy))
  }
}
function onDragUp() {
  document.onmousemove = null
  document.onmouseup = null
  document.ontouchmove = null
  document.ontouchend = null
  setTimeout(() => { isDragging = false; floatPaused = false }, 100)
}
function startPanelDrag(e) {
  e.preventDefault()
  panelDragging = true
  panelStartX = e.touches ? e.touches[0].clientX : e.clientX
  panelStartY = e.touches ? e.touches[0].clientY : e.clientY
  const panel = document.querySelector('.ai-chat-panel')
  if (panel) {
    const rect = panel.getBoundingClientRect()
    panelPos.x = rect.left; panelPos.y = rect.top
  }
  document.onmousemove = onPanelDragMove
  document.onmouseup = onPanelDragUp
  document.ontouchmove = onPanelDragMove
  document.ontouchend = onPanelDragUp
}
function onPanelDragMove(ev) {
  if (!panelDragging) return
  const cx = ev.touches ? ev.touches[0].clientX : ev.clientX
  const cy = ev.touches ? ev.touches[0].clientY : ev.clientY
  const dx = cx - panelStartX, dy = cy - panelStartY
  const panel = document.querySelector('.ai-chat-panel')
  if (panel) {
    panel.style.left = (panelPos.x + dx) + 'px'
    panel.style.top = (panelPos.y + dy) + 'px'
    panel.style.right = 'auto'
    panel.style.bottom = 'auto'
  }
}
function onPanelDragUp() {
  panelDragging = false
  document.onmousemove = null
  document.onmouseup = null
  document.ontouchmove = null
  document.ontouchend = null
}

// === 璇煶鍚堟垚 (TTS) ===
function initSpeechSynth() {
  if ('speechSynthesis' in window) {
    synth = window.speechSynthesis
  }
}

function speakText(text) {
  if (!synth) return
  synth.cancel()
  const cleanText = text.replace(/\*\*/g, '').replace(/`/g, '').replace(/<[^>]*>/g, '')
  const utterance = new SpeechSynthesisUtterance(cleanText.slice(0, 500))
  utterance.lang = 'zh-CN'
  utterance.rate = 1.0
  utterance.pitch = 1.1
  utterance.volume = 0.9
  synth.speak(utterance)
}

// === 璇煶璇嗗埆 (STT) ===
function toggleVoiceInput() {
  if (voiceActive.value) { stopVoiceInput(); return }
  startVoiceInput()
}

function startVoiceInput() {
  const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition
  if (!SpeechRecognition) {
    inputText.value = '[娴忚鍣ㄤ笉鏀寔璇煶璇嗗埆锛岃浣跨敤Chrome]'
    return
  }
  recognition = new SpeechRecognition()
  recognition.lang = 'zh-CN'
  recognition.interimResults = true
  recognition.continuous = true
  recognition.maxAlternatives = 1

  recognition.onresult = (event) => {
    let transcript = ''
    for (let i = event.resultIndex; i < event.results.length; i++) {
      transcript += event.results[i][0].transcript
    }
    inputText.value = transcript
  }
  recognition.onerror = (e) => { voiceActive.value = false }
  recognition.onend = () => { voiceActive.value = false }
  recognition.start()
  voiceActive.value = true
}

function stopVoiceInput() {
  if (recognition) { recognition.stop(); recognition = null }
  voiceActive.value = false
}

// === 璇煶閫氳瘽 ===
function toggleVoiceCall() {
  if (voiceCallActive.value) {
    synth && synth.cancel()
    voiceCallActive.value = false
  } else {
    voiceCallActive.value = true
    // 鑷姩鏈楄妯″紡锛氭敹鍒癆I鍥炲鍚庤嚜鍔ㄦ湕璇?
  }
}

// === 瑙嗛閫氳瘽 ===
async function toggleVideoCall() {
  if (videoActive.value) { endVideoCall(); return }
  try {
    localStream = await navigator.mediaDevices.getUserMedia({ video: true, audio: true })
    if (localVideo.value) {
      localVideo.value.srcObject = localStream
    }
    videoActive.value = true
    videoConnected.value = false
    // 妯℃嫙杩炴帴锛堢湡瀹炲満鏅渶瑕乄ebRTC淇′护鏈嶅姟鍣級
    setTimeout(() => { videoConnected.value = true }, 2000)
  } catch (e) {
    alert('鏃犳硶璁块棶鎽勫儚澶?楹﹀厠椋? ' + e.message)
  }
}

function endVideoCall() {
  if (localStream) {
    localStream.getTracks().forEach(t => t.stop())
    localStream = null
  }
  videoActive.value = false
  videoConnected.value = false
}
function captureSnapshot() {
  const videoEl = document.querySelector('.ai-video-preview video')
  if (!videoEl) return
  const canvas = document.createElement('canvas')
  canvas.width = videoEl.videoWidth; canvas.height = videoEl.videoHeight
  canvas.getContext('2d').drawImage(videoEl, 0, 0)
  const dataUrl = canvas.toDataURL('image/jpeg', 0.9)
  attachments.value.push({ name: 'snapshot.jpg', type: 'image', dataUrl, mimeType: 'image/jpeg', size: 0 })
  ElMessage.success('宸叉埅鍥撅紝鍙彂閫佺粰AI鍒嗘瀽')
}

function toggleMic() {
  micMuted.value = !micMuted.value
  if (localStream) {
    localStream.getAudioTracks().forEach(t => { t.enabled = !micMuted.value })
  }
}

function toggleCamera() {
  cameraOff.value = !cameraOff.value
  if (localStream) {
    localStream.getVideoTracks().forEach(t => { t.enabled = !cameraOff.value })
  }
}

function stopVideoCall() {
  endVideoCall()
}

// === 娑堟伅 ===
async function sendMessage() {
  const text = inputText.value.trim(); const files = [...attachments.value]
  if ((!text && !files.length) || loading.value) return
  stopVoiceInput()

  const now = new Date().toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' })
  clearAttachments()
  
  // 鍥剧墖鍒嗘瀽妯″紡
  if (files.length && files[0].type === 'image' && text && files[0].dataUrl) {
    messages.value.push({ role: 'user', content: text + ' [鍥剧墖]', time: now })
    await analyzeWithVision(files[0].dataUrl, text)
    return
  }
  
  // 鍥剧墖鍙戦€侊紙鏃犳枃瀛楋級
  if (files.length && files[0].type === 'image') {
    messages.value.push({ role: 'user', content: '[鍥剧墖]', time: now, image: files[0].dataUrl })
    loading.value = true; window.dispatchEvent(new CustomEvent('brain:thinking', {detail:true}))
    await nextTick(); scrollBottom()
    try {
      const token = getAgentToken()
      const res = await fetch('/agent/vision/analyze', {
        method: 'POST', headers: { 'Content-Type': 'application/json', 'X-Agent-Token': token },
        body: JSON.stringify({ image_base64: files[0].dataUrl.split(',')[1], question: '璇锋弿杩拌繖寮犲浘鐗? })
      })
      if (res.ok) {
        const data = await res.json()
        messages.value.push({ role: 'assistant', content: data.result || '鍒嗘瀽瀹屾垚', time: new Date().toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' }) })
        speakIfActive(data.result)
      }
    } catch (e) { messages.value.push({ role: 'assistant', content: '鍥剧墖鍒嗘瀽澶辫触', time: now }) }
    loading.value = false; return
  }

  // 鏅€氭枃鏈秷鎭?- 浣跨敤SSE娴佸紡
  messages.value.push({ role: 'user', content: text, time: now })
  inputText.value = ''
  loading.value = true; window.dispatchEvent(new CustomEvent('brain:thinking', {detail:true}))
  await nextTick(); scrollBottom()

  // 娣诲姞AI鍗犱綅娑堟伅
  const aiMsg = { role: 'assistant', content: '', time: new Date().toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' }) }
  messages.value.push(aiMsg)
  await nextTick(); scrollBottom()

  try {
    const token = getAgentToken()
    const res = await fetch('/agent/chat/stream', {
      method: 'POST', headers: { 'Content-Type': 'application/json', 'X-Agent-Token': token },
      body: JSON.stringify({ message: text, conv_id: convId, model: '' })
    })
    
    const reader = res.body.getReader()
    const decoder = new TextDecoder()
    let fullText = ''
    
    while (true) {
      const { done, value } = await reader.read()
      if (done) break
      const chunk = decoder.decode(value, { stream: true })
      const lines = chunk.split('\n')
      for (const line of lines) {
        if (line.startsWith('data: ')) {
          try {
            const data = JSON.parse(line.slice(6))
            if (data.token) {
              fullText += data.token
              aiMsg.content = fullText
              await nextTick(); scrollBottom()
            }
            if (data.done) {
              if (data.conv_id) { convId = data.conv_id; localStorage.setItem('friday_conv_id', convId) }
              speakIfActive(fullText)
            }
          } catch(e) {}
        }
      }
    }
  } catch (e) {
    aiMsg.content = '杩炴帴澶辫触锛岃閲嶈瘯'
  }
  loading.value = false; window.dispatchEvent(new CustomEvent('brain:thinking', {detail:false}))
}

function getAgentToken() {
  return localStorage.getItem('agent_token') || localStorage.getItem('friday_token') || 'kWs4N6GiD4vtjnuHV31r14m6HPpKttBSI35lFnpiI90'
}

function speakIfActive(text) {
  window.dispatchEvent(new CustomEvent('brain:speaking', {detail:text}))
  setTimeout(() => window.dispatchEvent(new CustomEvent('brain:thinking', {detail:false})), 500)
  if (typeof voiceCallActive !== 'undefined' && voiceCallActive.value) { speakText(text) }
}

async function analyzeWithVision(dataUrl, question) {
  loading.value = true; window.dispatchEvent(new CustomEvent('brain:thinking', {detail:true}))
  const aiMsg = { role: 'assistant', content: '', time: new Date().toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' }) }
  messages.value.push(aiMsg); await nextTick(); scrollBottom()
  try {
    const token = getAgentToken()
    const res = await fetch('/agent/vision/analyze', {
      method: 'POST', headers: { 'Content-Type': 'application/json', 'X-Agent-Token': token },
      body: JSON.stringify({ image_base64: dataUrl.split(',')[1], question })
    })
    if (res.ok) {
      const data = await res.json()
      aiMsg.content = data.result || '鍒嗘瀽瀹屾垚'
      speakIfActive(aiMsg.content)
    }
  } catch(e) { aiMsg.content = '鍒嗘瀽澶辫触' }
  loading.value = false; window.dispatchEvent(new CustomEvent('brain:thinking', {detail:false}))
}

// Load conversations on mount
async function loadConversations() {
  try {
    const token = getAgentToken()
    const res = await fetch('/agent/chat/conversations', { headers: { 'X-Agent-Token': token } })
    if (res.ok) { const data = await res.json(); conversations.value = data.conversations || [] }
  } catch(e) {}
}

function switchConversation(cid) {
  convId = cid; localStorage.setItem('friday_conv_id', cid)
  messages.value = []
  showHistory.value = false
  loadConversationMessages(cid)
}

async function loadConversationMessages(cid) {
  try {
    const token = getAgentToken()
    const res = await fetch('/agent/chat/conversations/' + cid, { headers: { 'X-Agent-Token': token } })
    if (res.ok) { const data = await res.json(); messages.value = (data.messages || []).map(m => ({...m, time: ''})) }
  } catch(e) {}
}

function newConversation() {
  convId = ''; localStorage.removeItem('friday_conv_id')
  messages.value = []; showHistory.value = false
}

async function loadPromptTemplates() {
  try {
    const token = getAgentToken()
    const res = await fetch('/agent/prompts', { headers: { 'X-Agent-Token': token } })
    if (res.ok) { const data = await res.json(); promptTemplates.value = data.templates || [] }
  } catch(e) {}
}

function applyTemplate(tmpl) {
  inputText.value = ''; selectedTemplate.value = tmpl.name
  ElMessage.info('宸查€夋嫨妯℃澘: ' + tmpl.name + '锛岃緭鍏ュ唴瀹瑰悗鍙戦€?)
}



const processingStatus = ref(''); const processingSteps = ref([]); let stepTimer = null
const attachments = ref([])
function onFileSelected(e) {
  const files = Array.from(e.target.files || [])
  for (const file of files) {
    if (attachments.value.length >= 5) { alert('鏈€澶?涓枃浠?); break }
    const reader = new FileReader()
    reader.onload = (ev) => {
      let type = 'file'
      if (file.type.startsWith('image/')) type = 'image'
      else if (file.type.startsWith('video/')) type = 'video'
      attachments.value.push({ name: file.name, size: file.size, type, dataUrl: ev.target.result, mimeType: file.type, file })
    }
    reader.readAsDataURL(file)
  }
  e.target.value = ''
}
function removeAttachment(i) { attachments.value.splice(i, 1) }
function getFileIcon(name) { const ext = name.split('.').pop().toLowerCase(); const icons={pdf:'pdf',doc:'doc',docx:'doc',xls:'xls',xlsx:'xls',csv:'csv',json:'json',txt:'txt',zip:'zip'}; return icons[ext]||'file' }
function formatSize(bytes) { if(!bytes) return ''; if(bytes<1024) return bytes+'B'; if(bytes<1024*1024) return (bytes/1024).toFixed(1)+'KB'; return (bytes/(1024*1024)).toFixed(1)+'MB' }
function clearAttachments() { attachments.value = [] }



// === SCI-FI EFFECTS ===
const matrixCanvas = ref(null)
let matrixInterval = null

function startMatrixRain() {
  nextTick(() => {
    const canvas = matrixCanvas.value
    if (!canvas) return
    const parent = canvas.parentElement
    canvas.width = parent.clientWidth
    canvas.height = parent.clientHeight
    const ctx = canvas.getContext('2d')
    const chars = '?????????????????????????01'
    const fontSize = 10
    const columns = Math.floor(canvas.width / fontSize)
    const drops = Array(columns).fill(1)

    function draw() {
      ctx.fillStyle = 'rgba(10,10,30,0.05)'
      ctx.fillRect(0, 0, canvas.width, canvas.height)
      ctx.fillStyle = 'rgba(0,240,255,0.08)'
      ctx.font = fontSize + 'px monospace'
      for (let i = 0; i < drops.length; i++) {
        const char = chars[Math.floor(Math.random() * chars.length)]
        ctx.fillText(char, i * fontSize, drops[i] * fontSize)
        if (drops[i] * fontSize > canvas.height && Math.random() > 0.975) drops[i] = 0
        drops[i]++
      }
    }
    matrixInterval = setInterval(draw, 50)
  })
}
function stopMatrixRain() {
  if (matrixInterval) { clearInterval(matrixInterval); matrixInterval = null }
}

// Auto-start matrix when panel opens
const origOpen = openChat
openChat = function() { origOpen(); setTimeout(startMatrixRain, 200) }
const origClose = closeChat
closeChat = function() { stopMatrixRain(); origClose() }
const origMin = minimizeChat
minimizeChat = function() { stopMatrixRain(); origMin() }

function detectTask(msg) {
  const m = msg.toLowerCase();
  processingSteps.value = [];
  if (m.includes('鏈嶅姟')||m.includes('server')||m.includes('鐘舵€?)||m.includes('cpu')||m.includes('鍐呭瓨')) {
    processingSteps.value = ['杩炴帴鏈嶅姟鍣?..', '鏌ヨCPU鐘舵€?..', '璇诲彇鍐呭瓨鏁版嵁...', '鍒嗘瀽璐熻浇鎯呭喌...', '鐢熸垚鎶ュ憡...'];
    return '绯荤粺璇婃柇';
  }
  if (m.includes('璁㈠崟')||m.includes('order')) {
    processingSteps.value = ['鏌ヨ鏁版嵁搴?..', '缁熻璁㈠崟鏁版嵁...', '鐢熸垚姹囨€?..'];
    return '璁㈠崟鏌ヨ';
  }
  if (m.includes('鎶ュ憡')||m.includes('report')||m.includes('鍛ㄦ姤')) {
    processingSteps.value = ['鏀堕泦杩愯鏁版嵁...', '鍒嗘瀽瓒嬪娍...', 'AI鐢熸垚鎽樿...', '鎺掔増杈撳嚭...'];
    return '鎶ュ憡鐢熸垚';
  }
  if (m.includes('寮傚父')||m.includes('鍛婅')||m.includes('閿欒')||m.includes('鏁呴殰')) {
    processingSteps.value = ['鎵弿寮傚父鐐?..', '鍏宠仈鍒嗘瀽...', 'AI璇婃柇...', '鐢熸垚澶勭悊寤鸿...'];
    return '寮傚父鎺掓煡';
  }
  if (m.includes('瀹氫环')||m.includes('浠锋牸')||m.includes('price')) {
    processingSteps.value = ['鑾峰彇甯傚満鏁版嵁...', '绔炲搧鍒嗘瀽...', 'AI瀹氫环寤鸿...'];
    return '鏅鸿兘瀹氫环';
  }
  if (m.includes('缂栫▼')||m.includes('浠ｇ爜')||m.includes('寮€鍙?)) {
    processingSteps.value = ['鍒嗘瀽闇€姹?..', 'AI鐢熸垚浠ｇ爜...', '楠岃瘉娴嬭瘯...'];
    return 'AI缂栫▼';
  }
  if (m.includes('澶囦唤')||m.includes('backup')) {
    processingSteps.value = ['蹇収鐘舵€?..', '鎵撳寘鏁版嵁...', '瀹夊叏瀛樺偍...'];
    return '澶囦唤鍥炴粴';
  }
  if (m.includes('閲囬泦')||m.includes('鐖?)||m.includes('scrape')) {
    processingSteps.value = ['杩炴帴鏁版嵁婧?..', '瑙ｆ瀽瀛楁...', '娓呮礂鍘婚噸...', '鍏ュ簱瀛樺偍...'];
    return '鏁版嵁閲囬泦';
  }
  processingSteps.value = ['鍒嗘瀽涓?..', '澶勭悊涓?..', 'AI鎬濊€?..'];
  return 'AI 澶勭悊';
}
function startStepAnimation() {
  if (stepTimer) clearInterval(stepTimer);
  let si = 0;
  stepTimer = setInterval(() => {
    if (si < processingSteps.value.length && loading.value) {
      processingStatus.value = processingSteps.value[si];
      si++;
    } else if (!loading.value) {
      clearInterval(stepTimer);
    } else {
      clearInterval(stepTimer);
    }
  }, 800);
}
function stopStepAnimation() {
  if (stepTimer) { clearInterval(stepTimer); stepTimer = null; }
  processingSteps.value = [];
}

function quickAsk(question) { inputText.value = question; sendMessage() }


// typewriter
let twTimer=null
function typeEffect(txt,idx){if(twTimer)clearInterval(twTimer);let i=0;const f=txt;messages.value[idx].content='';twTimer=setInterval(()=>{if(i<f.length){const s=/[\u4e00-\u9fff]/.test(f[i])?2:4;messages.value[idx].content=f.substring(0,i+s);i+=s;scrollBottom()}else{clearInterval(twTimer);twTimer=null;stopStepAnimation();processingStatus.value=''}},25)}
function stopTw(){if(twTimer){clearInterval(twTimer);twTimer=null}}

function renderMsg(text) {
  if (!text) return ''
  return text.replace(/\n/g, '<br>').replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>').replace(/`(.*?)`/g, '<code style="background:rgba(102,126,234,0.2);padding:1px 5px;border-radius:3px;font-size:12px">$1</code>')
}

function scrollBottom() {
  nextTick(() => {
    const el = document.querySelector('.floating-ai .chat-messages')
    if (el) el.scrollTop = el.scrollHeight
  })
}

// === v7: Prompt妯℃澘 + 妯″瀷瀵规瘮 ===
async function compareModels() { 
  const text=inputText.value.trim(); if(!text)return; inputText.value=""
  messages.value.push({role:"user",content:text,time:new Date().toLocaleTimeString("zh-CN",{hour:"2-digit",minute:"2-digit"})})
  loading.value=true
  try{
    const t=localStorage.getItem("agent_token")||localStorage.getItem("friday_token")||"kWs4N6GiD4vtjnuHV31r14m6HPpKttBSI35lFnpiI90"
    const r=await fetch("/agent/chat/compare",{method:"POST",headers:{"Content-Type":"application/json","X-Agent-Token":t},body:JSON.stringify({message:text})})
    if(r.ok){const d=await r.json();const results=(d.results||[]).map(x=>"**"+x.model+"**: "+((x.reply||x.error||"").slice(0,300))).join("\n\n");messages.value.push({role:"assistant",content:results,time:new Date().toLocaleTimeString("zh-CN",{hour:"2-digit",minute:"2-digit"})})}
  }catch(e){messages.value.push({role:"assistant",content:"妯″瀷瀵规瘮澶辫触",time:new Date().toLocaleTimeString("zh-CN",{hour:"2-digit",minute:"2-digit"})})}
  loading.value=false 
}
function applyTemplateByName(name) { const t=promptTemplates.value.find(p=>p.name===name); if(t){selectedTemplate.value=t.name;ElMessage.info("宸查€夋ā鏉? "+t.name);inputText.value="";inputText.focus()} }
loadPromptTemplates()
</script>

<style scoped>
.floating-ai {
  position: fixed;
  z-index: 99999;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
}

/* === 鎮诞鎸夐挳 === */
.ai-float-btn {
  position: fixed;
  width: 56px; height: 56px;
  border-radius: 50%;
  cursor: pointer;
  box-shadow: 0 4px 20px rgba(102, 126, 234, 0.4);
  transition: transform 0.2s, box-shadow 0.2s;
  user-select: none;
  z-index: 99999;
}
.ai-float-btn:hover { transform: scale(1.08); box-shadow: 0 6px 28px rgba(102,126,234,0.55); }
.ai-float-btn:active { transform: scale(0.95); }
.btn-glow {
  position: absolute; inset: -4px; border-radius: 50%;
  background: linear-gradient(135deg, #667eea, #764ba2);
  opacity: 0.3;
  animation: glowPulse 2s ease-in-out infinite;
}
@keyframes glowPulse {
  0%, 100% { opacity: 0.3; transform: scale(1); }
  50% { opacity: 0.6; transform: scale(1.1); }
}
.btn-inner {
  position: absolute; inset: 2px; border-radius: 50%;
  background: linear-gradient(135deg, #1a1a2e, #16213e);
  display: flex; align-items: center; justify-content: center; overflow: hidden;
}
.btn-pulse {
  position: absolute; top: -2px; right: -2px;
  width: 12px; height: 12px; border-radius: 50%;
  background: #ff4757; border: 2px solid #1a1a2e;
  animation: pulse 2s infinite;
}
@keyframes pulse {
  0% { box-shadow: 0 0 0 0 rgba(255,71,87,0.6); }
  70% { box-shadow: 0 0 0 8px rgba(255,71,87,0); }
  100% { box-shadow: 0 0 0 0 rgba(255,71,87,0); }
}

/* === 闈㈡澘 === */
.ai-chat-panel {
  position: fixed;
  bottom: 20px; right: 20px;
  width: 380px; height: 520px;
  background: linear-gradient(180deg, #1a1a2e 0%, #16213e 100%);
  border-radius: 16px;
  box-shadow: 0 8px 40px rgba(0,0,0,0.5), 0 0 0 1px rgba(102,126,234,0.2);
  display: flex; flex-direction: column; overflow: hidden;
  z-index: 99999;
}
.ai-chat-panel.expanded {
  width: 700px; height: 85vh;
  bottom: 5vh; right: calc(50% - 350px);
}
.ai-chat-panel.video {
  width: 700px; height: 600px;
  bottom: 20px; right: 20px;
}

/* === 澶撮儴 === */
.chat-header {
  display: flex; align-items: center; justify-content: space-between;
  padding: 10px 14px;
  background: linear-gradient(135deg, #667eea, #764ba2);
  color: #fff; cursor: move; user-select: none;
}
.header-left { display: flex; align-items: center; gap: 10px; }
.ai-avatar-small {
  width: 30px; height: 30px; border-radius: 8px;
  background: rgba(255,255,255,0.2);
  display: flex; align-items: center; justify-content: center;
  font-weight: bold; font-size: 12px;
}
.header-title { font-weight: 600; font-size: 14px; }
.header-status { font-size: 11px; opacity: 0.8; }
.header-actions { display: flex; gap: 4px; }
.header-btn {
  width: 28px; height: 28px; border: none; border-radius: 6px;
  background: rgba(255,255,255,0.15); color: #fff;
  font-size: 14px; cursor: pointer;
  display: flex; align-items: center; justify-content: center;
  transition: background 0.2s;
}
.header-btn:hover { background: rgba(255,255,255,0.3); }
.header-btn.active { background: rgba(255,255,255,0.35); box-shadow: 0 0 8px rgba(255,255,255,0.3); }
.close-btn:hover { background: rgba(255,71,87,0.6); }

/* === 瑙嗛鍖哄煙 === */
.video-area {
  flex: 1; position: relative; background: #000;
  display: flex; align-items: center; justify-content: center;
}
.video-main {
  width: 100%; height: 100%; object-fit: cover;
}
.video-thumb {
  position: absolute; bottom: 12px; right: 12px;
  width: 140px; height: 100px; object-fit: cover;
  border-radius: 10px; border: 2px solid rgba(255,255,255,0.3);
  box-shadow: 0 2px 10px rgba(0,0,0,0.5);
}
.video-overlay {
  position: absolute; inset: 0;
  display: flex; flex-direction: column;
  align-items: center; justify-content: center;
  background: rgba(0,0,0,0.6); color: #fff; gap: 12px;
}
.connect-spinner {
  width: 40px; height: 40px; border: 3px solid rgba(255,255,255,0.2);
  border-top-color: #667eea; border-radius: 50%;
  animation: spin 1s linear infinite;
}
@keyframes spin { to { transform: rotate(360deg); } }
.video-controls {
  position: absolute; bottom: 16px; left: 50%; transform: translateX(-50%);
  display: flex; gap: 10px; padding: 8px 16px;
  background: rgba(0,0,0,0.7); border-radius: 30px;
}
.video-controls button {
  width: 40px; height: 40px; border: none; border-radius: 50%;
  background: rgba(255,255,255,0.15); color: #fff;
  font-size: 18px; cursor: pointer; transition: background 0.2s;
}
.video-controls button:hover { background: rgba(255,255,255,0.3); }
.video-controls button.muted { background: rgba(255,71,87,0.5); }
.end-call-btn {
  width: auto !important; padding: 0 16px !important;
  background: #ff4757 !important; border-radius: 20px !important;
  font-size: 14px !important;
}

/* === 娑堟伅鍖?=== */
.chat-messages {
  flex: 1; overflow-y: auto; padding: 14px;
  display: flex; flex-direction: column; gap: 10px;
}
.chat-messages::-webkit-scrollbar { width: 4px; }
.chat-messages::-webkit-scrollbar-thumb { background: rgba(102,126,234,0.3); border-radius: 2px; }
.empty-chat { text-align: center; padding: 24px 10px; color: #aab; }
.empty-icon { font-size: 44px; margin-bottom: 10px; }
.empty-sub { font-size: 12px; opacity: 0.6; margin-top: 4px; }
.quick-actions { display: flex; flex-wrap: wrap; gap: 8px; justify-content: center; margin-top: 14px; }
.quick-actions button {
  padding: 6px 14px; border-radius: 20px;
  border: 1px solid rgba(102,126,234,0.3);
  background: rgba(102,126,234,0.1); color: #aac;
  font-size: 12px; cursor: pointer; transition: all 0.2s;
}
.quick-actions button:hover { background: rgba(102,126,234,0.25); border-color: #667eea; color: #fff; }

.msg-row { display: flex; gap: 8px; align-items: flex-start; }
.msg-row.user { flex-direction: row-reverse; }
.msg-avatar {
  width: 26px; height: 26px; border-radius: 8px;
  display: flex; align-items: center; justify-content: center;
  font-size: 13px; background: rgba(255,255,255,0.06); flex-shrink: 0;
}
.msg-bubble { max-width: 75%; padding: 10px 14px; border-radius: 14px; font-size: 13px; line-height: 1.55; }
.msg-bubble.user { background: linear-gradient(135deg, #667eea, #764ba2); color: #fff; border-bottom-right-radius: 4px; }
.msg-bubble.assistant { background: rgba(255,255,255,0.06); color: #dde; border-bottom-left-radius: 4px; }
.msg-bubble.typing { display: flex; gap: 4px; padding: 14px 18px; }
.msg-bubble.typing .dot {
  width: 6px; height: 6px; border-radius: 50%; background: #667eea;
  animation: typingBounce 1.4s infinite;
}
.msg-bubble.typing .dot:nth-child(2) { animation-delay: 0.2s; }
.msg-bubble.typing .dot:nth-child(3) { animation-delay: 0.4s; }
@keyframes typingBounce {
  0%, 60%, 100% { transform: translateY(0); }
  30% { transform: translateY(-6px); }
}
.msg-time { font-size: 10px; margin-top: 4px; opacity: 0.5; }
.msg-bubble.user .msg-time { text-align: right; }
.voice-tag { margin-left: 4px; opacity: 0.6; }
.play-voice-btn {
  width: 24px; height: 24px; border: none; border-radius: 50%;
  background: rgba(102,126,234,0.15); font-size: 12px;
  cursor: pointer; flex-shrink: 0; align-self: flex-end;
  transition: background 0.2s;
}
.play-voice-btn:hover { background: rgba(102,126,234,0.35); }

/* === 璇煶鎸囩ず鍣?=== */
.voice-indicator {
  display: flex; align-items: center; gap: 10px;
  padding: 8px 12px; margin-bottom: 8px;
  background: rgba(255,71,87,0.1); border-radius: 10px;
  color: #ff6b7a; font-size: 12px;
}
.voice-wave { display: flex; gap: 2px; align-items: flex-end; height: 20px; }
.voice-wave span {
  width: 3px; background: #ff4757; border-radius: 2px;
  animation: wave 0.8s ease-in-out infinite;
}
.voice-wave span:nth-child(1) { height: 8px; }
.voice-wave span:nth-child(2) { height: 14px; }
.voice-wave span:nth-child(3) { height: 20px; }
.voice-wave span:nth-child(4) { height: 14px; }
.voice-wave span:nth-child(5) { height: 8px; }
@keyframes wave {
  0%, 100% { transform: scaleY(1); }
  50% { transform: scaleY(0.4); }
}

/* === 杈撳叆鍖?=== */
.chat-input-area { padding: 10px 12px; border-top: 1px solid rgba(255,255,255,0.06); }
.input-row { display: flex; gap: 8px; align-items: flex-end; }
.voice-input-btn {
  width: 34px; height: 34px; border: none; border-radius: 10px;
  background: rgba(255,255,255,0.05); cursor: pointer;
  display: flex; align-items: center; justify-content: center;
  transition: all 0.2s; flex-shrink: 0;
}
.voice-input-btn:hover { background: rgba(255,255,255,0.12); }
.voice-input-btn.recording { background: #ff4757; animation: pulse-rec 1.5s infinite; }
@keyframes pulse-rec {
  0%, 100% { box-shadow: 0 0 0 0 rgba(255,71,87,0.5); }
  50% { box-shadow: 0 0 0 8px rgba(255,71,87,0); }
}
.input-row textarea {
  flex: 1; background: rgba(255,255,255,0.05);
  border: 1px solid rgba(255,255,255,0.1); border-radius: 10px;
  padding: 8px 12px; color: #dde; font-size: 13px;
  resize: none; outline: none; max-height: 100px;
  font-family: inherit; line-height: 1.4;
}
.input-row textarea:focus { border-color: #667eea; background: rgba(255,255,255,0.08); }
.input-row textarea::placeholder { color: #667; }
.send-btn {
  width: 34px; height: 34px; border: none; border-radius: 10px;
  background: linear-gradient(135deg, #667eea, #764ba2); color: #fff;
  cursor: pointer; display: flex; align-items: center; justify-content: center;
  flex-shrink: 0; transition: transform 0.2s, opacity 0.2s;
}
.send-btn:hover:not(:disabled) { transform: scale(1.05); }
.send-btn:disabled { opacity: 0.4; cursor: not-allowed; }

/* === 鍔ㄧ敾 === */
.slide-up-enter-active { transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1); }
.slide-up-leave-active { transition: all 0.2s ease-in; }
.slide-up-enter-from { opacity: 0; transform: translateY(20px) scale(0.95); }
.slide-up-leave-to { opacity: 0; transform: translateY(10px) scale(0.98); }

/* === ?????? === */
.header-status.busy { color: #667eea; animation: statusPulse 1.5s ease-in-out infinite; }

/* Processing steps in chat */
.processing-steps { margin-bottom: 10px; }
.step-header { font-size: 13px; font-weight: 600; color: #667eea; margin-bottom: 8px; animation: statusPulse 1.5s ease-in-out infinite; }
.step-item {
  display: flex; align-items: center; gap: 8px;
  padding: 4px 0; font-size: 12px; color: #667; opacity: 0.5;
  transition: all 0.3s;
}
.step-item.done { color: #667eea; opacity: 1; font-weight: 500; }
.step-dot {
  width: 6px; height: 6px; border-radius: 50%; background: #445;
  transition: all 0.3s;
}
.step-item.done .step-dot { background: #667eea; box-shadow: 0 0 6px rgba(102,126,234,0.5); animation: dotPulse 0.8s ease-in-out infinite; }
@keyframes dotPulse {
  0%, 100% { box-shadow: 0 0 4px rgba(102,126,234,0.3); }
  50% { box-shadow: 0 0 10px rgba(102,126,234,0.8); }
}
.typing-dots { display: flex; gap: 5px; padding-left: 14px; }
.typing-dots .dot {
  width: 6px; height: 6px; border-radius: 50%; background: #667eea;
  animation: typingBounce 1.4s infinite;
}
.typing-dots .dot:nth-child(2) { animation-delay: 0.2s; }
.typing-dots .dot:nth-child(3) { animation-delay: 0.4s; }

/* Enhanced Energy System */
.energy-rings { position: absolute; inset: -28px; pointer-events: none; z-index: 0; }
.energy-ring {
  position: absolute; inset: 0; border-radius: 50%;
  border: 2px solid transparent;
  animation: ringSpin 4s linear infinite;
}
.ring1 {
  border-top-color: rgba(102,126,234,0.7);
  border-right-color: rgba(118,75,162,0.5);
  animation-duration: 3s;
  box-shadow: 0 0 18px rgba(102,126,234,0.3), inset 0 0 18px rgba(102,126,234,0.15), 0 0 40px rgba(102,126,234,0.1);
}
.ring2 {
  inset: -10px;
  border-bottom-color: rgba(102,126,234,0.5);
  border-left-color: rgba(118,75,162,0.4);
  animation-duration: 5s; animation-direction: reverse;
}
.ring3 {
  inset: -18px;
  border-top-color: rgba(102,126,234,0.25);
  border-bottom-color: rgba(118,75,162,0.2);
  animation-duration: 7s;
}

.energy-lines { position: absolute; inset: -40px; pointer-events: none; z-index: 0; }
.line {
  position: absolute;
  background: linear-gradient(90deg, transparent, rgba(102,126,234,0.8), rgba(118,75,162,0.6), transparent);
  animation: lineFlow 2s ease-in-out infinite;
  border-radius: 1px;
  filter: blur(0.5px);
}
.line-top { top: 0; left: 6%; width: 88%; height: 2px; }
.line-right { top: 6%; right: 0; width: 2px; height: 88%; animation-delay: 0.5s; background: linear-gradient(180deg, transparent, rgba(118,75,162,0.8), rgba(102,126,234,0.6), transparent); }
.line-bottom { bottom: 0; left: 6%; width: 88%; height: 2px; animation-delay: 1s; }
.line-left { top: 6%; left: 0; width: 2px; height: 88%; animation-delay: 1.5s; background: linear-gradient(180deg, transparent, rgba(118,75,162,0.8), rgba(102,126,234,0.6), transparent); }

@keyframes lineFlow {
  0%, 100% { opacity: 0.4; transform: scaleX(1); }
  50% { opacity: 1; transform: scaleX(1.25); }
}

.energy-particles { position: absolute; inset: -14px; pointer-events: none; z-index: 0; }
.particle {
  position: absolute; width: 5px; height: 5px; border-radius: 50%;
  background: #667eea;
  box-shadow: 0 0 8px #667eea, 0 0 16px rgba(102,126,234,0.6), 0 0 24px rgba(102,126,234,0.3);
  animation: particleOrbit 3s linear infinite;
  --angle: calc(var(--i) * 45deg);
  top: 50%; left: 50%;
  transform: translate(-50%, -50%) rotate(var(--angle)) translateX(48px);
  opacity: 0.6;
  animation-delay: calc(var(--i) * 0.12s);
}
.particle:nth-child(even) { background: #764ba2; box-shadow: 0 0 8px #764ba2, 0 0 16px rgba(118,75,162,0.6); }
.particle:nth-child(3n) { width: 3px; height: 3px; }
@keyframes particleOrbit {
  0% { opacity: 0.15; transform: translate(-50%, -50%) rotate(var(--angle)) translateX(42px) scale(0.7); }
  50% { opacity: 0.95; transform: translate(-50%, -50%) rotate(calc(var(--angle) + 180deg)) translateX(52px) scale(1.3); }
  100% { opacity: 0.15; transform: translate(-50%, -50%) rotate(calc(var(--angle) + 360deg)) translateX(42px) scale(0.7); }
}

/* Status tag enhancement */
.btn-status-tag {
  position: absolute; bottom: -32px; left: 50%; transform: translateX(-50%);
  padding: 5px 14px; border-radius: 16px;
  background: linear-gradient(135deg, #667eea, #764ba2);
  color: #fff; font-size: 11px; font-weight: 600; white-space: nowrap;
  animation: statusBounce 1.5s ease-in-out infinite;
  box-shadow: 0 6px 24px rgba(102,126,234,0.55), 0 0 40px rgba(102,126,234,0.2);
  letter-spacing: 0.5px;
  z-index: 10;
}
.btn-status-tag::before {
  content: ''; position: absolute; inset: -2px; border-radius: 18px;
  background: linear-gradient(135deg, rgba(102,126,234,0.4), rgba(118,75,162,0.4));
  filter: blur(6px); z-index: -1;
}
.btn-status-tag::after {
  content: ''; position: absolute; left: 0; right: 0; bottom: -1px; height: 2px;
  background: linear-gradient(90deg, transparent, rgba(255,255,255,0.7), transparent);
  animation: shimmerBar 1.2s linear infinite;
}
@keyframes statusBounce {
  0%, 100% { opacity: 0.85; transform: translateX(-50%) translateY(0); }
  50% { opacity: 1; transform: translateX(-50%) translateY(-3px); }
}
@keyframes shimmerBar {
  0% { transform: translateX(-100%); }
  100% { transform: translateX(100%); }
}

/* Button breathing when processing */
.ai-float-btn.processing { animation: btnBreathe 2s ease-in-out infinite; }
@keyframes btnBreathe {
  0%, 100% { transform: scale(1); box-shadow: 0 4px 20px rgba(102,126,234,0.4); }
  50% { transform: scale(1.05); box-shadow: 0 6px 32px rgba(102,126,234,0.7), 0 0 50px rgba(118,75,162,0.3); }
}


/* ===== 绉诲姩绔€傞厤 ===== */
@media (max-width: 768px) {
  .floating-ai { z-index: 99999; }
  .ai-float-btn {
    width: 48px; height: 48px;
    bottom: 80px; right: 12px;
  }
  .ai-float-btn .btn-inner svg { width: 22px; height: 22px; }
  .ai-chat-panel {
    width: 100vw !important; height: 100vh !important;
    max-width: 100vw; max-height: 100vh;
    left: 0 !important; top: 0 !important;
    right: 0 !important; bottom: 0 !important;
    border-radius: 0;
  }
  .ai-chat-panel.expanded { width: 100vw !important; height: 100vh !important; }
  .msg-bubble { max-width: 88%; }
  .empty-chat { padding: 20px 12px; }
  .quick-actions { flex-wrap: wrap; }
  .quick-actions button { font-size: 11px; padding: 6px 10px; }
}
</style>
