<template>
  <div class="mobile-shell">
    <!-- ===== 3D 全息智能体（小尺寸） ===== -->
    <div class="holo-agent" @click="toggleChat" :class="{ active: chatOpen, speaking: isSpeaking }">
      <div class="holo-sphere">
        <div class="holo-core"></div>
        <div class="holo-ring r1"></div>
        <div class="holo-ring r2"></div>
        <div class="holo-face">
          <div class="h-eye left" :class="{ blink: blinking }"></div>
          <div class="h-eye right" :class="{ blink: blinking }"></div>
          <div class="h-mouth" :class="{ smile: chatOpen }"></div>
        </div>
        <div class="holo-particles">
          <span v-for="i in 6" :key="i" class="p" :style="{ '--d': i * 0.4 + 's' }"></span>
        </div>
      </div>
    </div>

    <!-- ===== 标签内容 ===== -->
    <div class="tab-content" ref="tabContent" @touchstart="onTouchStart" @touchend="onTouchEnd">
      <div v-for="(tab, idx) in tabs" :key="idx" v-show="activeTab === idx">
        <div class="card-grid">
          <div
            v-for="item in tab.items"
            :key="item.path"
            class="m-card"
            @click="item.action === 'chat' ? toggleChat() : navTo(item.path)"
          >
            <span class="m-icon">{{ item.icon }}</span>
            <span class="m-label">{{ item.label }}</span>
          </div>
        </div>
      </div>
    </div>

    <!-- ===== 底部导航 ===== -->
    <div class="bottom-nav">
      <div
        v-for="(tab, idx) in tabs"
        :key="idx"
        class="nav-item"
        :class="{ active: activeTab === idx }"
        @click="activeTab = idx"
      >
        <span class="nav-icon">{{ tab.icon }}</span>
        <span class="nav-label">{{ tab.label }}</span>
      </div>
    </div>

    <!-- ===== AI 聊天面板（全屏覆盖） ===== -->
    <transition name="chat-slide">
      <div v-if="chatOpen" class="chat-overlay">
        <div class="chat-header">
          <div class="ch-left">
            <div class="ch-avatar">F</div>
            <div>
              <div class="ch-title">Friday AI</div>
              <div class="ch-status">{{ chatLoading ? '思考中...' : '在线' }}</div>
            </div>
          </div>
          <button class="ch-close" @click="closeChat">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/>
            </svg>
          </button>
        </div>

        <div class="chat-body" ref="chatBody">
          <div v-if="chatMessages.length === 0" class="chat-empty">
            <div class="ce-icon">AI</div>
            <p>你好！有什么可以帮助你的？</p>
          </div>
          <div
            v-for="(msg, i) in chatMessages"
            :key="i"
            class="cm-row"
            :class="msg.role"
          >
            <div class="cm-avatar">{{ msg.role === 'user' ? '你' : 'F' }}</div>
            <div class="cm-bubble">{{ msg.text }}</div>
          </div>
          <div v-if="chatLoading" class="cm-row assistant">
            <div class="cm-avatar">F</div>
            <div class="cm-bubble loading">
              <span class="d"></span><span class="d"></span><span class="d"></span>
            </div>
          </div>
        </div>

        <div class="chat-footer">
          <input
            v-model="chatInput"
            @keyup.enter="sendChat"
            placeholder="输入消息..."
            class="ci-input"
            :disabled="chatLoading"
          />
          <button class="ci-send" @click="sendChat" :disabled="!chatInput.trim() || chatLoading">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
              <path d="M22 2L11 13"/><path d="M22 2l-7 20-4-9-9-4 20-7z"/>
            </svg>
          </button>
        </div>
      </div>
    </transition>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { agentApi } from '@/api/index'

const router = useRouter()
const activeTab = ref(0)
const chatOpen = ref(false)
const chatMessages = ref([])
const chatInput = ref('')
const chatLoading = ref(false)
const blinking = ref(false)
const isSpeaking = ref(false)

const chatBody = ref(null)
let blinkTimer = null
let touchStartX = 0

const tabs = [
  {
    icon: '□', label: '管理',
    items: [
      { icon: '', label: '仪表盘', path: '/dashboard' },
      { icon: '', label: '服务器', path: '/server' },
      { icon: '', label: 'Docker', path: '/docker' },
      { icon: '', label: 'Nginx', path: '/nginx' },
      { icon: '', label: '数据库', path: '/database' },
      { icon: '', label: '安全', path: '/security' },
    ]
  },
  {
    icon: '◇', label: '商城',
    items: [
      { icon: '', label: '商品管理', path: '/mall' },
      { icon: '', label: '订单', path: '/mall' },
      { icon: '', label: '客户', path: '/customer' },
      { icon: '', label: '域名轮值', path: '/rotation' },
      { icon: '', label: '爬虫', path: '/scraper' },
    ]
  },
  {
    icon: '○', label: 'AI',
    items: [
      { icon: '', label: 'AI 对话', action: 'chat' },
      { icon: '', label: 'AI 大脑', path: '/ai-brain' },
      { icon: '', label: '高级 AI', path: '/advanced-ai' },
      { icon: '', label: '知识库', path: '/knowledge' },
      { icon: '', label: '模型中心', path: '/models' },
    ]
  },
]

function toggleChat() {
  chatOpen.value = !chatOpen.value
  if (chatOpen.value) scrollToBottom()
}

function closeChat() { chatOpen.value = false }

function navTo(path) { router.push(path) }

function onTouchStart(e) { touchStartX = e.touches[0].clientX }
function onTouchEnd(e) {
  const diff = e.changedTouches[0].clientX - touchStartX
  if (Math.abs(diff) > 60) {
    if (diff > 0 && activeTab.value > 0) activeTab.value--
    else if (diff < 0 && activeTab.value < tabs.length - 1) activeTab.value++
  }
}

async function sendChat() {
  const text = chatInput.value.trim()
  if (!text || chatLoading.value) return
  chatMessages.value.push({ role: 'user', text, time: Date.now() })
  chatInput.value = ''
  chatLoading.value = true
  isSpeaking.value = false
  scrollToBottom()

  try {
    const res = await agentApi.post('/chat/send', {
      message: text,
      conversation_id: localStorage.getItem('friday_conv_id') || ''
    })
    const reply = res.reply || res.message || '抱歉，我没有理解。'
    chatMessages.value.push({ role: 'assistant', text: reply, time: Date.now() })
    isSpeaking.value = true
    setTimeout(() => { isSpeaking.value = false }, reply.length * 40)
    if (res.conversation_id) localStorage.setItem('friday_conv_id', res.conversation_id)
  } catch (e) {
    chatMessages.value.push({ role: 'assistant', text: '连接失败，请检查网络。', time: Date.now() })
  }
  chatLoading.value = false
  scrollToBottom()
}

function scrollToBottom() {
  setTimeout(() => {
    if (chatBody.value) chatBody.value.scrollTop = chatBody.value.scrollHeight
  }, 50)
}

onMounted(() => {
  blinkTimer = setInterval(() => {
    blinking.value = true
    setTimeout(() => { blinking.value = false }, 150)
  }, 3500)
})

onUnmounted(() => {
  clearInterval(blinkTimer)
})
</script>

<style scoped>
.mobile-shell {
  width: 100vw; height: 100vh;
  background: #0a0a1a;
  display: flex; flex-direction: column;
  position: relative;
  overflow: hidden;
  color: #e8eaf0;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
}

/* ===== 全息智能体 ===== */
.holo-agent {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 24px 0 12px;
  cursor: pointer;
  transition: all 0.3s;
}
.holo-agent.active { padding: 8px 0; }

.holo-sphere {
  width: 72px; height: 72px;
  position: relative;
  display: flex; align-items: center; justify-content: center;
  transition: all 0.3s;
}
.holo-agent.active .holo-sphere { width: 48px; height: 48px; }

.holo-core {
  width: 55%; height: 55%;
  border-radius: 50%;
  background: radial-gradient(circle at 35% 35%, #667eea, #764ba2);
  box-shadow: 0 0 25px rgba(102,126,234,0.4);
  animation: cPulse 3s ease-in-out infinite;
}
@keyframes cPulse {
  0%, 100% { transform: scale(1); opacity: 0.85; }
  50% { transform: scale(1.1); opacity: 1; }
}

.holo-ring {
  position: absolute;
  border-radius: 50%;
  border: 1.5px solid rgba(102,126,234,0.25);
  animation: rSpin 4s linear infinite;
}
.r1 { width: 100%; height: 100%; }
.r2 { width: 130%; height: 130%; animation-duration: 6s; animation-direction: reverse; border-color: rgba(118,75,162,0.2); }
.holo-agent.speaking .holo-ring { border-color: rgba(102,126,234,0.5); animation-duration: 1.5s; }

@keyframes rSpin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.holo-face {
  position: absolute;
  width: 36%; height: 28%;
  display: flex; flex-direction: column; align-items: center; justify-content: center;
}

.h-eye {
  width: 5px; height: 7px;
  background: #a8b5ff;
  border-radius: 50%;
  position: absolute;
  box-shadow: 0 0 6px rgba(102,126,234,0.7);
}
.h-eye.left { left: 3px; }
.h-eye.right { right: 3px; }
.h-eye.blink { height: 1px; }

.h-mouth {
  position: absolute;
  bottom: 2px;
  width: 10px; height: 2.5px;
  background: #a8b5ff;
  border-radius: 0 0 5px 5px;
  transition: all 0.3s;
}
.h-mouth.smile { width: 14px; height: 3px; }

.holo-particles { position: absolute; width: 100%; height: 100%; }
.p {
  position: absolute;
  width: 2px; height: 2px;
  background: #667eea;
  border-radius: 50%;
  animation: pFloat 3s ease-in-out infinite;
  animation-delay: var(--d);
}
.p:nth-child(1) { top: 8%; left: 15%; }
.p:nth-child(2) { top: 75%; left: 10%; }
.p:nth-child(3) { top: 15%; left: 70%; }
.p:nth-child(4) { top: 65%; left: 80%; }
.p:nth-child(5) { top: 40%; left: 5%; }
.p:nth-child(6) { top: 30%; left: 85%; }

@keyframes pFloat {
  0%, 100% { transform: translateY(0); opacity: 0.5; }
  50% { transform: translateY(-8px); opacity: 1; }
}

/* ===== 标签内容 ===== */
.tab-content {
  flex: 1;
  overflow-y: auto;
  padding: 8px 12px;
}

.card-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 10px;
}

.m-card {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 6px;
  padding: 16px 8px;
  background: rgba(255,255,255,0.03);
  border: 1px solid rgba(255,255,255,0.06);
  border-radius: 14px;
  cursor: pointer;
  transition: all 0.2s;
}
.m-card:active { transform: scale(0.95); background: rgba(102,126,234,0.1); }

.m-icon { font-size: 22px; }
.m-label { font-size: 11px; color: #aab; text-align: center; }

/* ===== 底部导航 ===== */
.bottom-nav {
  display: flex;
  border-top: 1px solid rgba(255,255,255,0.06);
  background: rgba(0,0,0,0.3);
  padding-bottom: env(safe-area-inset-bottom, 0);
}

.nav-item {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 2px;
  padding: 8px 0;
  cursor: pointer;
  color: #667;
  transition: all 0.2s;
}
.nav-item.active { color: #667eea; }
.nav-icon { font-size: 18px; }
.nav-label { font-size: 10px; }

/* ===== 聊天面板 ===== */
.chat-overlay {
  position: fixed;
  inset: 0;
  z-index: 2000;
  background: #0a0a1a;
  display: flex;
  flex-direction: column;
}

.chat-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 16px;
  border-bottom: 1px solid rgba(102,126,234,0.1);
  background: rgba(0,0,0,0.3);
}

.ch-left { display: flex; align-items: center; gap: 10px; }

.ch-avatar {
  width: 32px; height: 32px;
  border-radius: 50%;
  background: linear-gradient(135deg, #667eea, #764ba2);
  display: flex; align-items: center; justify-content: center;
  font-size: 12px; font-weight: 700; color: white;
}

.ch-title { font-size: 15px; font-weight: 600; }
.ch-status { font-size: 11px; color: #52c41a; }

.ch-close {
  width: 32px; height: 32px;
  border-radius: 50%;
  border: none;
  background: rgba(255,255,255,0.05);
  color: #889;
  display: flex; align-items: center; justify-content: center;
  cursor: pointer;
}

.chat-body {
  flex: 1;
  overflow-y: auto;
  padding: 16px;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.chat-empty {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 8px;
  color: #667;
}

.ce-icon {
  width: 48px; height: 48px;
  border-radius: 50%;
  background: radial-gradient(circle at 35% 35%, rgba(102,126,234,0.3), rgba(118,75,162,0.2));
  display: flex; align-items: center; justify-content: center;
  font-size: 14px; font-weight: 700;
  color: #667eea;
}

.cm-row {
  display: flex;
  gap: 8px;
  max-width: 85%;
}
.cm-row.user { align-self: flex-end; flex-direction: row-reverse; }
.cm-row.assistant { align-self: flex-start; }

.cm-avatar {
  width: 26px; height: 26px;
  border-radius: 50%;
  display: flex; align-items: center; justify-content: center;
  font-size: 10px; font-weight: 700; flex-shrink: 0;
}
.cm-avatar:not(.assistant) { background: linear-gradient(135deg, #1890ff, #40a9ff); color: white; }
.cm-avatar.assistant { background: linear-gradient(135deg, #667eea, #764ba2); color: white; }

.cm-bubble {
  padding: 10px 14px;
  border-radius: 14px;
  font-size: 14px;
  line-height: 1.5;
  word-break: break-word;
}
.cm-row.user .cm-bubble {
  background: linear-gradient(135deg, #667eea, #764ba2);
  color: white;
  border-bottom-right-radius: 4px;
}
.cm-row.assistant .cm-bubble {
  background: rgba(255,255,255,0.06);
  color: #d0d4e0;
  border: 1px solid rgba(255,255,255,0.06);
  border-bottom-left-radius: 4px;
}

.cm-bubble.loading { padding: 12px 16px; display: flex; gap: 4px; }
.d {
  width: 6px; height: 6px;
  border-radius: 50%;
  background: #667eea;
  animation: dB 1.4s ease-in-out infinite;
}
.d:nth-child(2) { animation-delay: 0.2s; }
.d:nth-child(3) { animation-delay: 0.4s; }
@keyframes dB {
  0%, 80%, 100% { transform: scale(0.6); opacity: 0.4; }
  40% { transform: scale(1); opacity: 1; }
}

.chat-footer {
  display: flex;
  gap: 8px;
  padding: 10px 12px 14px;
  border-top: 1px solid rgba(102,126,234,0.1);
  background: rgba(0,0,0,0.3);
  padding-bottom: calc(14px + env(safe-area-inset-bottom, 0));
}

.ci-input {
  flex: 1;
  padding: 12px 14px;
  border-radius: 12px;
  border: 1px solid rgba(102,126,234,0.15);
  background: rgba(255,255,255,0.04);
  color: #e8eaf0;
  font-size: 14px;
  outline: none;
}
.ci-input::placeholder { color: #556; }

.ci-send {
  width: 44px; height: 44px;
  border-radius: 12px;
  border: none;
  background: linear-gradient(135deg, #667eea, #764ba2);
  color: white;
  display: flex; align-items: center; justify-content: center;
  cursor: pointer;
}
.ci-send:disabled { opacity: 0.4; }

/* ===== 聊天动画 ===== */
.chat-slide-enter-active { transition: all 0.3s cubic-bezier(0.34, 1.56, 0.64, 1); }
.chat-slide-leave-active { transition: all 0.25s ease-in; }
.chat-slide-enter-from { transform: translateY(100%); }
.chat-slide-leave-to { transform: translateY(100%); }
</style>
