<template>
  <div class="floating-ai" :class="{ 'is-open': chatOpen, 'is-mobile': isMobile }">
    <!-- ===== 3D 全息智能体 ===== -->
    <div class="holo-agent" @click="toggleChat" :class="{ active: agentActive, speaking: agentSpeaking, thinking: agentThinking }">
      <div class="holo-sphere">
        <div class="holo-core"></div>
        <div class="holo-ring ring-1"></div>
        <div class="holo-ring ring-2"></div>
        <div class="holo-ring ring-3"></div>
        <div class="holo-face">
          <div class="holo-eye left" :class="{ blink: blinking }"></div>
          <div class="holo-eye right" :class="{ blink: blinking }"></div>
          <div class="holo-mouth" :class="{ smile: agentActive }"></div>
        </div>
        <div class="holo-particles">
          <span v-for="i in 12" :key="i" class="particle" :style="{ '--i': i, '--delay': (i * 0.3) + 's' }"></span>
        </div>
        <div class="holo-glow"></div>
        <div class="holo-scanline"></div>
      </div>
      <div class="holo-label">Friday AI</div>
      <div class="holo-status">{{ statusText }}</div>
    </div>

    <!-- ===== AI 聊天面板 ===== -->
    <transition name="panel-slide">
      <div v-if="chatOpen" class="chat-panel" ref="panelRef">
        <!-- 标题栏 -->
        <div class="chat-header">
          <div class="header-left">
            <div class="header-avatar">
              <div class="mini-holo"></div>
              <span>AI</span>
            </div>
            <div class="header-info">
              <div class="header-title">Friday AI</div>
              <div class="header-subtitle">{{ loading ? '思考中...' : '在线' }}</div>
            </div>
          </div>
          <div class="header-actions">
            <button class="h-btn" @click="toggleVoice" :class="{ active: voiceActive }" title="语音输入">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M12 1a3 3 0 0 0-3 3v8a3 3 0 0 0 6 0V4a3 3 0 0 0-3-3z"/>
                <path d="M19 10v2a7 7 0 0 1-14 0v-2"/>
                <line x1="12" y1="19" x2="12" y2="23"/>
              </svg>
            </button>
            <button class="h-btn" @click="clearChat" title="清空对话">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <polyline points="3 6 5 6 21 6"/><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/>
              </svg>
            </button>
            <button class="h-btn close-btn" @click="closeChat">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/>
              </svg>
            </button>
          </div>
        </div>

        <!-- 消息列表 -->
        <div class="chat-messages" ref="msgList">
          <div v-if="messages.length === 0" class="empty-chat">
            <div class="empty-icon">
              <div class="mini-holo-big"></div>
            </div>
            <p class="empty-title">你好！我是 Friday AI</p>
            <p class="empty-sub">我可以帮你管理商城、分析数据、运维服务器</p>
            <div class="quick-actions">
              <button v-for="q in quickQuestions" :key="q.text" @click="quickAsk(q.text)" class="q-btn">
                <span class="q-icon">{{ q.icon }}</span>
                <span>{{ q.text }}</span>
              </button>
            </div>
          </div>

          <div v-for="(msg, i) in messages" :key="i" class="msg-row" :class="msg.role">
            <div class="msg-avatar" :class="msg.role">
              {{ msg.role === 'user' ? '你' : 'F' }}
            </div>
            <div class="msg-content">
              <div class="msg-bubble" :class="msg.role">
                <div class="msg-text">{{ msg.content }}</div>
              </div>
              <div class="msg-time">{{ msg.time }}</div>
            </div>
          </div>

          <div v-if="loading" class="msg-row assistant">
            <div class="msg-avatar assistant">F</div>
            <div class="msg-content">
              <div class="msg-bubble assistant">
                <div class="typing-dots">
                  <span class="dot"></span><span class="dot"></span><span class="dot"></span>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- 输入区 -->
        <div class="chat-input-area">
          <div v-if="voiceActive" class="voice-bar">
            <div class="voice-wave">
              <span v-for="i in 5" :key="i" class="wave-bar" :style="{ animationDelay: (i * 0.1) + 's' }"></span>
            </div>
            <span class="voice-text">正在聆听...</span>
            <button class="voice-stop" @click="stopVoice">取消</button>
          </div>
          <div class="input-row">
            <textarea
              v-model="inputText"
              @keydown.enter.exact.prevent="sendMessage"
              @keydown.enter.shift.exact="inputText += '\n'"
              placeholder="输入消息..."
              rows="1"
              ref="inputBox"
              :disabled="loading"
              class="chat-input"
            ></textarea>
            <button class="send-btn" @click="sendMessage" :disabled="loading || !inputText.trim()">
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
import { ref, nextTick, onMounted, onUnmounted, computed } from 'vue'
import { agentApi } from '@/api/index'

const chatOpen = ref(false)
const messages = ref([])
const inputText = ref('')
const loading = ref(false)
const voiceActive = ref(false)
const agentActive = ref(false)
const agentSpeaking = ref(false)
const agentThinking = ref(false)
const blinking = ref(false)
const isMobile = ref(false)
const msgList = ref(null)
const inputBox = ref(null)
const panelRef = ref(null)
let recognition = null
let blinkInterval = null
let thinkTimeout = null

const statusText = computed(() => {
  if (agentSpeaking.value) return '说话中...'
  if (agentThinking.value) return '思考中...'
  return '点击对话'
})

const quickQuestions = [
  { text: '服务器状态', icon: '' },
  { text: '查看订单', icon: '' },
  { text: '系统健康', icon: '' },
  { text: '帮助', icon: '?' },
]

function checkMobile() {
  isMobile.value = window.innerWidth < 768
}

function toggleChat() {
  chatOpen.value = !chatOpen.value
  agentActive.value = chatOpen.value
  if (chatOpen.value) {
    nextTick(() => scrollToBottom())
  }
}

function closeChat() {
  chatOpen.value = false
  agentActive.value = false
}

function clearChat() {
  messages.value = []
  localStorage.removeItem('friday_chat_history')
}

async function sendMessage() {
  const text = inputText.value.trim()
  if (!text || loading.value) return

  messages.value.push({ role: 'user', content: text, time: now() })
  inputText.value = ''
  loading.value = true
  agentThinking.value = true
  scrollToBottom()

  try {
    const res = await agentApi.post('/chat/send', {
      message: text,
      conversation_id: localStorage.getItem('friday_conv_id') || ''
    })
    const reply = res.reply || res.message || '抱歉，我没有理解。'
    messages.value.push({ role: 'assistant', content: reply, time: now() })
    agentSpeaking.value = true
    setTimeout(() => { agentSpeaking.value = false }, reply.length * 30)
    if (res.conversation_id) {
      localStorage.setItem('friday_conv_id', res.conversation_id)
    }
  } catch (e) {
    messages.value.push({ role: 'assistant', content: '连接失败，请检查网络或后端服务。', time: now() })
  }
  loading.value = false
  agentThinking.value = false
  saveHistory()
  nextTick(() => scrollToBottom())
}

function quickAsk(text) {
  inputText.value = text
  sendMessage()
}

function toggleVoice() {
  voiceActive.value = !voiceActive.value
  if (voiceActive.value) startVoice()
  else stopVoice()
}

function startVoice() {
  if (!('webkitSpeechRecognition' in window)) {
    voiceActive.value = false
    return
  }
  recognition = new webkitSpeechRecognition()
  recognition.lang = 'zh-CN'
  recognition.continuous = false
  recognition.interimResults = false
  recognition.onresult = (e) => {
    inputText.value = e.results[0][0].transcript
    voiceActive.value = false
    sendMessage()
  }
  recognition.onerror = () => { voiceActive.value = false }
  recognition.start()
}

function stopVoice() {
  if (recognition) { recognition.stop(); recognition = null }
  voiceActive.value = false
}

function now() {
  const d = new Date()
  return d.getHours().toString().padStart(2,'0') + ':' + d.getMinutes().toString().padStart(2,'0')
}

function scrollToBottom() {
  if (msgList.value) {
    msgList.value.scrollTop = msgList.value.scrollHeight
  }
}

function saveHistory() {
  try {
    localStorage.setItem('friday_chat_history', JSON.stringify(messages.value.slice(-50)))
  } catch {}
}

function loadHistory() {
  try {
    const saved = localStorage.getItem('friday_chat_history')
    if (saved) messages.value = JSON.parse(saved)
  } catch {}
}

onMounted(() => {
  checkMobile()
  window.addEventListener('resize', checkMobile)
  loadHistory()

  blinkInterval = setInterval(() => {
    blinking.value = true
    setTimeout(() => { blinking.value = false }, 200)
  }, 3000)

  window.addEventListener('brain:openChat', toggleChat)
})

onUnmounted(() => {
  clearInterval(blinkInterval)
  clearTimeout(thinkTimeout)
  window.removeEventListener('resize', checkMobile)
  window.removeEventListener('brain:openChat', toggleChat)
})
</script>

<style scoped>
/* ===== 容器 ===== */
.floating-ai {
  position: fixed;
  z-index: 1000;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
}

/* ===== 3D 全息智能体 ===== */
.holo-agent {
  position: fixed;
  bottom: 30px;
  right: 30px;
  width: 80px;
  height: 80px;
  cursor: pointer;
  z-index: 1001;
  transition: all 0.4s cubic-bezier(0.34, 1.56, 0.64, 1);
}
.holo-agent:hover { transform: scale(1.1); }
.holo-agent.active { transform: scale(0.7); bottom: auto; top: 20px; right: 20px; }

.holo-sphere {
  width: 100%;
  height: 100%;
  position: relative;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
}

/* 核心光球 */
.holo-core {
  position: absolute;
  width: 60%;
  height: 60%;
  border-radius: 50%;
  background: radial-gradient(circle at 35% 35%, #667eea, #764ba2);
  box-shadow: 0 0 30px rgba(102,126,234,0.5), 0 0 60px rgba(102,126,234,0.2);
  animation: corePulse 3s ease-in-out infinite;
}

@keyframes corePulse {
  0%, 100% { transform: scale(1); opacity: 0.9; }
  50% { transform: scale(1.08); opacity: 1; }
}

/* 全息环 */
.holo-ring {
  position: absolute;
  border-radius: 50%;
  border: 1.5px solid rgba(102,126,234,0.3);
  animation: ringRotate 4s linear infinite;
}
.ring-1 { width: 100%; height: 100%; }
.ring-2 { width: 130%; height: 130%; animation-duration: 6s; animation-direction: reverse; border-color: rgba(118,75,162,0.2); }
.ring-3 { width: 160%; height: 160%; animation-duration: 8s; border-color: rgba(102,126,234,0.15); }
.holo-agent.speaking .holo-ring { border-color: rgba(102,126,234,0.6); animation-duration: 2s; }

@keyframes ringRotate {
  0% { transform: rotate(0deg) scale(1); }
  50% { transform: rotate(180deg) scale(1.05); }
  100% { transform: rotate(360deg) scale(1); }
}

/* 全息脸 */
.holo-face {
  position: absolute;
  width: 40%;
  height: 30%;
  z-index: 2;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 3px;
}

.holo-eye {
  width: 6px;
  height: 8px;
  background: #a8b5ff;
  border-radius: 50%;
  position: absolute;
  box-shadow: 0 0 8px rgba(102,126,234,0.8);
  transition: all 0.1s;
}
.holo-eye.left { left: 5px; }
.holo-eye.right { right: 5px; }
.holo-eye.blink { height: 1px; }

.holo-mouth {
  position: absolute;
  bottom: 2px;
  width: 12px;
  height: 3px;
  background: #a8b5ff;
  border-radius: 0 0 6px 6px;
  box-shadow: 0 0 6px rgba(102,126,234,0.6);
  transition: all 0.3s;
}
.holo-mouth.smile { width: 16px; height: 4px; }

/* 粒子 */
.holo-particles {
  position: absolute;
  width: 100%;
  height: 100%;
}
.particle {
  position: absolute;
  width: 2px;
  height: 2px;
  background: #667eea;
  border-radius: 50%;
  animation: particleFloat 3s ease-in-out infinite;
  animation-delay: var(--delay);
  opacity: 0.6;
}
.particle:nth-child(1) { top: 10%; left: 20%; }
.particle:nth-child(2) { top: 20%; left: 70%; }
.particle:nth-child(3) { top: 50%; left: 5%; }
.particle:nth-child(4) { top: 70%; left: 15%; }
.particle:nth-child(5) { top: 15%; left: 50%; }
.particle:nth-child(6) { top: 60%; left: 75%; }
.particle:nth-child(7) { top: 30%; left: 85%; }
.particle:nth-child(8) { top: 80%; left: 60%; }
.particle:nth-child(9) { top: 40%; left: 40%; }
.particle:nth-child(10) { top: 85%; left: 30%; }
.particle:nth-child(11) { top: 5%; left: 40%; }
.particle:nth-child(12) { top: 75%; left: 80%; }

@keyframes particleFloat {
  0%, 100% { transform: translateY(0) scale(1); opacity: 0.6; }
  50% { transform: translateY(-10px) scale(1.5); opacity: 1; }
}

/* 发光 */
.holo-glow {
  position: absolute;
  width: 120%;
  height: 120%;
  border-radius: 50%;
  background: radial-gradient(circle, rgba(102,126,234,0.15) 0%, transparent 70%);
  animation: glowPulse 2s ease-in-out infinite;
}

@keyframes glowPulse {
  0%, 100% { transform: scale(1); opacity: 0.5; }
  50% { transform: scale(1.2); opacity: 0.8; }
}

.holo-scanline {
  position: absolute;
  width: 100%;
  height: 3px;
  background: linear-gradient(90deg, transparent, rgba(102,126,234,0.4), transparent);
  animation: scanlineMove 2s linear infinite;
  top: 0;
  border-radius: 50%;
}

@keyframes scanlineMove {
  0% { top: 0; opacity: 0; }
  10% { opacity: 1; }
  90% { opacity: 1; }
  100% { top: 100%; opacity: 0; }
}

.holo-label {
  position: absolute;
  bottom: -20px;
  left: 50%;
  transform: translateX(-50%);
  font-size: 10px;
  color: rgba(255,255,255,0.5);
  white-space: nowrap;
  letter-spacing: 1px;
}

.holo-status {
  position: absolute;
  bottom: -34px;
  left: 50%;
  transform: translateX(-50%);
  font-size: 9px;
  color: rgba(102,126,234,0.6);
  white-space: nowrap;
}

/* ===== 聊天面板 ===== */
.chat-panel {
  position: fixed;
  bottom: 0;
  right: 0;
  width: 380px;
  height: 600px;
  background: rgba(10, 10, 30, 0.92);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border: 1px solid rgba(102, 126, 234, 0.15);
  border-radius: 16px 16px 0 0;
  box-shadow: 0 -10px 40px rgba(0,0,0,0.5), 0 0 0 1px rgba(102,126,234,0.1);
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

/* 标题栏 */
.chat-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 16px;
  border-bottom: 1px solid rgba(102,126,234,0.1);
  background: rgba(0,0,0,0.3);
}

.header-left {
  display: flex;
  align-items: center;
  gap: 10px;
}

.header-avatar {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: linear-gradient(135deg, #667eea, #764ba2);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  font-weight: 700;
  color: white;
  position: relative;
  overflow: hidden;
}

.mini-holo {
  position: absolute;
  inset: -50%;
  background: radial-gradient(circle at 50% 50%, rgba(255,255,255,0.1), transparent);
  animation: miniHolo 3s ease-in-out infinite;
}

@keyframes miniHolo {
  0%, 100% { transform: rotate(0deg); }
  50% { transform: rotate(180deg); }
}

.header-info { line-height: 1.3; }
.header-title { font-size: 14px; font-weight: 600; color: #e8eaf0; }
.header-subtitle { font-size: 11px; color: #52c41a; }

.header-actions { display: flex; gap: 4px; }

.h-btn {
  width: 30px;
  height: 30px;
  border-radius: 8px;
  border: none;
  background: transparent;
  color: #889;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
}
.h-btn:hover { background: rgba(102,126,234,0.15); color: #e8eaf0; }
.h-btn.active { color: #667eea; background: rgba(102,126,234,0.15); }
.h-btn.close-btn:hover { background: rgba(255,77,79,0.15); color: #ff4d4f; }

/* 消息列表 */
.chat-messages {
  flex: 1;
  overflow-y: auto;
  padding: 16px;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.chat-messages::-webkit-scrollbar { width: 4px; }
.chat-messages::-webkit-scrollbar-track { background: transparent; }
.chat-messages::-webkit-scrollbar-thumb { background: rgba(102,126,234,0.3); border-radius: 2px; }

/* 空状态 */
.empty-chat {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 8px;
  text-align: center;
  padding: 20px;
}

.empty-icon {
  width: 60px;
  height: 60px;
  border-radius: 50%;
  background: radial-gradient(circle at 35% 35%, rgba(102,126,234,0.3), rgba(118,75,162,0.2));
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 8px;
  animation: corePulse 3s ease-in-out infinite;
}

.mini-holo-big {
  width: 30px;
  height: 30px;
  border-radius: 50%;
  background: radial-gradient(circle at 35% 35%, #667eea, #764ba2);
  box-shadow: 0 0 20px rgba(102,126,234,0.4);
}

.empty-title { font-size: 16px; font-weight: 600; color: #e8eaf0; margin: 0; }
.empty-sub { font-size: 12px; color: #667; margin: 0; }

.quick-actions { display: flex; flex-wrap: wrap; gap: 8px; justify-content: center; margin-top: 8px; }
.q-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 14px;
  border-radius: 20px;
  border: 1px solid rgba(102,126,234,0.2);
  background: rgba(102,126,234,0.08);
  color: #aab;
  font-size: 12px;
  cursor: pointer;
  transition: all 0.2s;
}
.q-btn:hover { background: rgba(102,126,234,0.2); border-color: rgba(102,126,234,0.4); color: #e8eaf0; }
.q-icon { font-size: 14px; }

/* 消息行 */
.msg-row {
  display: flex;
  gap: 8px;
  max-width: 85%;
}
.msg-row.user { align-self: flex-end; flex-direction: row-reverse; }
.msg-row.assistant { align-self: flex-start; }

.msg-avatar {
  width: 28px;
  height: 28px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 11px;
  font-weight: 700;
  flex-shrink: 0;
}
.msg-avatar.user { background: linear-gradient(135deg, #1890ff, #40a9ff); color: white; }
.msg-avatar.assistant { background: linear-gradient(135deg, #667eea, #764ba2); color: white; }

.msg-content { display: flex; flex-direction: column; gap: 3px; }
.msg-row.user .msg-content { align-items: flex-end; }

.msg-bubble {
  padding: 10px 14px;
  border-radius: 14px;
  font-size: 13px;
  line-height: 1.5;
  word-break: break-word;
}
.msg-bubble.user {
  background: linear-gradient(135deg, #667eea, #764ba2);
  color: white;
  border-bottom-right-radius: 4px;
}
.msg-bubble.assistant {
  background: rgba(255,255,255,0.06);
  color: #d0d4e0;
  border: 1px solid rgba(255,255,255,0.06);
  border-bottom-left-radius: 4px;
}

.msg-time {
  font-size: 10px;
  color: #556;
  padding: 0 4px;
}

/* 打字动画 */
.typing-dots { display: flex; gap: 4px; padding: 2px 0; }
.dot {
  width: 6px; height: 6px;
  border-radius: 50%;
  background: #667eea;
  animation: dotBounce 1.4s ease-in-out infinite;
}
.dot:nth-child(2) { animation-delay: 0.2s; }
.dot:nth-child(3) { animation-delay: 0.4s; }

@keyframes dotBounce {
  0%, 80%, 100% { transform: scale(0.6); opacity: 0.4; }
  40% { transform: scale(1); opacity: 1; }
}

/* 输入区 */
.chat-input-area {
  padding: 10px 12px 14px;
  border-top: 1px solid rgba(102,126,234,0.1);
  background: rgba(0,0,0,0.2);
}

.voice-bar {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 8px 12px;
  background: rgba(102,126,234,0.1);
  border-radius: 12px;
  margin-bottom: 8px;
}

.voice-wave {
  display: flex;
  align-items: center;
  gap: 3px;
  height: 24px;
}

.wave-bar {
  width: 3px;
  height: 100%;
  background: #667eea;
  border-radius: 2px;
  animation: waveAnim 0.8s ease-in-out infinite;
}

@keyframes waveAnim {
  0%, 100% { transform: scaleY(0.3); }
  50% { transform: scaleY(1); }
}

.voice-text { font-size: 12px; color: #aab; flex: 1; }
.voice-stop { padding: 4px 12px; border-radius: 8px; border: none; background: rgba(255,77,79,0.2); color: #ff4d4f; font-size: 11px; cursor: pointer; }

.input-row {
  display: flex;
  align-items: flex-end;
  gap: 8px;
}

.chat-input {
  flex: 1;
  padding: 10px 14px;
  border-radius: 12px;
  border: 1px solid rgba(102,126,234,0.15);
  background: rgba(255,255,255,0.04);
  color: #e8eaf0;
  font-size: 13px;
  resize: none;
  outline: none;
  max-height: 80px;
  line-height: 1.4;
  font-family: inherit;
  transition: border-color 0.2s;
}
.chat-input:focus { border-color: rgba(102,126,234,0.4); }
.chat-input::placeholder { color: #556; }
.chat-input:disabled { opacity: 0.5; }

.send-btn {
  width: 38px;
  height: 38px;
  border-radius: 12px;
  border: none;
  background: linear-gradient(135deg, #667eea, #764ba2);
  color: white;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
  flex-shrink: 0;
}
.send-btn:hover { transform: scale(1.05); box-shadow: 0 4px 15px rgba(102,126,234,0.4); }
.send-btn:disabled { opacity: 0.4; cursor: not-allowed; transform: none; box-shadow: none; }

/* ===== 面板出现动画 ===== */
.panel-slide-enter-active { transition: all 0.35s cubic-bezier(0.34, 1.56, 0.64, 1); }
.panel-slide-leave-active { transition: all 0.25s ease-in; }
.panel-slide-enter-from { opacity: 0; transform: translateY(30px) scale(0.95); }
.panel-slide-leave-to { opacity: 0; transform: translateY(20px) scale(0.95); }

/* ===== 移动端适配 ===== */
@media (max-width: 768px) {
  .holo-agent {
    bottom: 20px;
    right: 20px;
    width: 60px;
    height: 60px;
  }
  .holo-agent.active {
    top: 12px;
    right: 12px;
    width: 50px;
    height: 50px;
  }

  .chat-panel {
    width: 100%;
    height: 100%;
    border-radius: 0;
    left: 0;
    right: 0;
    bottom: 0;
  }

  .holo-label, .holo-status { display: none; }

  .panel-slide-enter-from { opacity: 0; transform: translateY(50px); }
  .panel-slide-leave-to { opacity: 0; transform: translateY(50px); }
}
</style>
