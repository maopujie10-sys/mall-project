<template>
  <div class="mobile-shell">

    <!-- 3D Holographic Agent -->
    <div class="holo-agent" @click="toggleAgent">
      <div class="holo-ring" :class="{ active: agentActive }">
        <div class="holo-face">
          <div class="holo-eye left" :class="{ blink: blinking }"></div>
          <div class="holo-eye right" :class="{ blink: blinking }"></div>
          <div class="holo-mouth" :class="{ speaking: agentSpeaking }"></div>
        </div>
        <div class="holo-glow"></div>
        <div class="holo-particles">
          <span v-for="i in 8" :key="i" class="particle" :style="{ '--i': i }"></span>
        </div>
      </div>
      <div class="holo-label">Friday AI</div>
    </div>

    <!-- Tab Content - swipe between tabs -->
    <div class="tab-content" @touchstart="onSwipeStart" @touchend="onSwipeEnd">
      <div v-for="(tab, tabIdx) in tabs" :key="tabIdx" v-show="activeTab === tabIdx" class="card-grid">
        <div class="m-card" v-for="item in tab.items" :key="item.path" @click="item.action === 'chat' ? toggleAgent() : $router.push(item.path)">
          <span class="m-card-icon">{{ item.icon }}</span>
          <span class="m-card-label">{{ item.label }}</span>
        </div>
      </div>
    </div>

    <!-- Bottom Tab Bar -->
    <div class="bottom-tabs">
      <div v-for="(tab, i) in tabs" :key="i" class="tab-item" :class="{ active: activeTab === i }" @click="activeTab = i">
        <span class="tab-icon">{{ tab.icon }}</span>
        <span class="tab-label">{{ tab.label }}</span>
      </div>
    </div>

    <!-- Chat Overlay -->
    <div v-if="showChat" class="chat-overlay">
      <div class="chat-header">
        <span>Friday AI Chat</span>
        <button @click="showChat = false" class="chat-close">X</button>
      </div>
      <div class="chat-body" ref="chatBody">
        <div v-for="(msg, i) in chatMessages" :key="i" :class="['chat-msg', msg.role]">{{ msg.text }}</div>
      </div>
      <div class="chat-input-row">
        <input v-model="chatInput" @keyup.enter="sendChat" placeholder="Ask Friday..." class="chat-input" />
        <button @click="sendChat" class="chat-send">Send</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { agentApi } from '@/api/index'

const activeTab = ref(0)
const agentActive = ref(false)
const agentSpeaking = ref(false)
const blinking = ref(false)
const showChat = ref(false)
const chatInput = ref('')
const chatMessages = ref([{ role: 'assistant', text: 'Hi, I am Friday. Tap a card to navigate or chat with me.' }])

let blinkTimer = null
onMounted(() => {
  blinkTimer = setInterval(() => { blinking.value = true; setTimeout(() => blinking.value = false, 200) }, 3500)
})
onUnmounted(() => clearInterval(blinkTimer))

function toggleAgent() {
  agentActive.value = !agentActive.value
  showChat.value = !showChat.value
  if (showChat.value) {
    agentSpeaking.value = true
    setTimeout(() => agentSpeaking.value = false, 2000)
  }
}

async function sendChat() {
  if (!chatInput.value.trim()) return
  const text = chatInput.value
  chatMessages.value.push({ role: 'user', text })
  chatInput.value = ''
  agentSpeaking.value = true
  try {
    const r = await agentApi.post('/agent/chat', { message: text, mode: 'smart' })
    const reply = r?.data?.response || r?.data?.content || 'Got it.'
    chatMessages.value.push({ role: 'assistant', text: reply })
  } catch {
    chatMessages.value.push({ role: 'assistant', text: 'Unable to reach AI right now.' })
  }
  agentSpeaking.value = false
}

// Swipe between tabs
let swipeX = 0
function onSwipeStart(e) { swipeX = e.changedTouches[0].clientX }
function onSwipeEnd(e) {
  const diff = e.changedTouches[0].clientX - swipeX
  if (Math.abs(diff) > 50) {
    activeTab.value = Math.max(0, Math.min(4, activeTab.value + (diff > 0 ? -1 : 1)))
  }
}

const tabs = [
  { icon: '\u{1F9E0}', label: 'AI', items: [
    { icon: '\u{1F52E}', label: 'Friday Brain', path: '/ai/friday' },
    { icon: '\u{1F4AC}', label: 'AI Chat', path: '#chat', action: 'chat' },
    { icon: '\u{1F916}', label: 'Agents', path: '/ai/agents' },
    { icon: '\u{1F9E0}', label: 'AI Brain', path: '/ai/ai-brain' },
    { icon: '\u{1F4E1}', label: 'Models', path: '/ai/models' },
    { icon: '\u{1F4DD}', label: 'Memory', path: '/ai/memory' },
    { icon: '\u{1F4C8}', label: 'Evolution', path: '/ai/evolution' },
    { icon: '\u{1F399}', label: 'Voice Chat', path: '/ai/voice-chat' },
    { icon: '\u{1F4F9}', label: 'Video AI', path: '/ai/video' },
    { icon: '\u{1F916}', label: 'Collab', path: '/ai/agent-collab' },
    { icon: '\u{1F4DA}', label: 'Knowledge', path: '/ai/knowledge' },
    { icon: '\u{1F527}', label: 'AI Tools', path: '/ai/ai-tools' },
  ]},
  { icon: '\u{1F4CA}', label: 'Data', items: [
    { icon: '\u{1F4CA}', label: 'Dashboard', path: '/ai/dashboard' },
    { icon: '\u{1F4C8}', label: 'Trends', path: '/ai/trends' },
    { icon: '\u{1F50D}', label: 'Scraper', path: '/ai/scraper' },
    { icon: '\u{1F5C4}', label: 'Database', path: '/ai/database' },
    { icon: '\u{1F4C4}', label: 'Logs', path: '/ai/log-viewer' },
    { icon: '\u{1F4C5}', label: 'Weekly', path: '/ai/weekly-report' },
    { icon: '\u{1F4DD}', label: 'Text2SQL', path: '/ai/text2sql' },
    { icon: '\u{1F4C8}', label: 'Predict', path: '/ai/predict' },
    { icon: '\u{2B50}', label: 'Recommend', path: '/ai/recommend' },
    { icon: '\u{1F3AE}', label: 'Virtual', path: '/ai/virtual' },
    { icon: '\u{1F4CA}', label: 'A/B Test', path: '/ai/ab-test' },
    { icon: '\u{1F3AF}', label: 'Competitor', path: '/ai/competitor' },
  ]},
  { icon: '\u{1F6E1}', label: 'Ops', items: [
    { icon: '\u{1F5A5}', label: 'Servers', path: '/ai/server' },
    { icon: '\u{1F433}', label: 'Docker', path: '/ai/docker' },
    { icon: '\u{1F310}', label: 'Nginx', path: '/ai/nginx' },
    { icon: '\u{1F4E1}', label: 'Network', path: '/ai/network' },
    { icon: '\u{1F3D7}', label: 'GitHub', path: '/ai/github' },
    { icon: '\u{1F6E1}', label: 'Security', path: '/ai/security' },
    { icon: '\u{1F514}', label: 'Alerts', path: '/ai/alert' },
    { icon: '\u{1F6A8}', label: 'Emergency', path: '/ai/emergency' },
    { icon: '\u{1F3A5}', label: 'Self-Heal', path: '/ai/self-healing' },
    { icon: '\u{1F504}', label: 'Rollback', path: '/ai/rollback' },
    { icon: '\u{1F504}', label: 'Rotation', path: '/ai/rotation' },
    { icon: '\u{1F50D}', label: 'Scan', path: '/ai/security-scan' },
  ]},
  { icon: '\u{1F3EA}', label: 'Mall', items: [
    { icon: '\u{1F3EC}', label: 'Mall Panel', path: '/ai/mall' },
    { icon: '\u{1F9E0}', label: 'Ecom AI', path: '/ai/ecommerce-ai' },
    { icon: '\u{1F4F7}', label: 'OCR', path: '/ai/ocr' },
    { icon: '\u{1F5BC}', label: 'Images', path: '/ai/image-process' },
    { icon: '\u{1F30D}', label: 'Multi-Lang', path: '/ai/multilang' },
    { icon: '\u{1F4E6}', label: 'Batch', path: '/ai/batch-upload' },
    { icon: '\u{1F4AC}', label: 'Auto-Reply', path: '/ai/auto-reply' },
    { icon: '\u{1F514}', label: 'Orders', path: '/ai/order-alert' },
    { icon: '\u{1F4DD}', label: 'Content', path: '/ai/content-factory' },
    { icon: '\u{1F465}', label: 'Customer', path: '/ai/customer' },
    { icon: '\u{1F4CA}', label: 'Profile', path: '/ai/customer-profile' },
    { icon: '\u{1F4DE}', label: 'Phone', path: '/ai/phone' },
  ]},
  { icon: '\u{2699}', label: 'Admin', items: [
    { icon: '\u{1F9E9}', label: 'Plugins', path: '/ai/plugins' },
    { icon: '\u{1F52E}', label: 'Skills', path: '/ai/skill-market' },
    { icon: '\u{1F511}', label: 'Key Mgr', path: '/ai/key-manager' },
    { icon: '\u{1F465}', label: 'Users', path: '/ai/user-manager' },
    { icon: '\u{1F4F1}', label: 'WeChat', path: '/ai/wechat-config' },
    { icon: '\u{2705}', label: 'Approval', path: '/ai/approval' },
    { icon: '\u{1F4CB}', label: 'Audit', path: '/ai/audit' },
    { icon: '\u{1F4CB}', label: 'Tasks', path: '/ai/tasks' },
    { icon: '\u{1F527}', label: 'Self-Svc', path: '/ai/self-service' },
    { icon: '\u{1F4C1}', label: 'Files', path: '/ai/files' },
    { icon: '\u{1F4C5}', label: 'Workflow', path: '/ai/workflow' },
    { icon: '\u{1F680}', label: 'Deploy', path: '/ai/code-deploy' },
    { icon: '\u{1F9E0}', label: 'Advanced', path: '/ai/advanced-ai' },
    { icon: '\u{1F4CB}', label: 'Capabilities', path: '/ai/capabilities' },
  ]},
]
</script>

<style scoped>
.mobile-shell {
  display: flex;
  flex-direction: column;
  height: 100dvh;
  background: linear-gradient(180deg, #080b1a 0%, #0d1025 100%);
  color: #e0e0e0;
  overflow: hidden;
}

/* === 3D Holographic Agent === */
.holo-agent {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 8px 0 4px;
  cursor: pointer;
  flex-shrink: 0;
}
.holo-ring {
  position: relative;
  width: 80px; height: 80px;
  border-radius: 50%;
  background: radial-gradient(circle at 35% 40%, rgba(102,126,234,0.25), rgba(13,16,37,0.6) 70%);
  border: 2px solid rgba(102,126,234,0.4);
  box-shadow: 0 0 30px rgba(102,126,234,0.3), inset 0 0 30px rgba(102,126,234,0.1);
  transition: all 0.4s;
  animation: holoPulse 3s ease-in-out infinite;
}
.holo-ring.active {
  border-color: rgba(102,200,234,0.8);
  box-shadow: 0 0 50px rgba(102,200,234,0.5), inset 0 0 40px rgba(102,200,234,0.2);
}
.holo-face { position: absolute; inset: 20%; display: flex; flex-wrap: wrap; justify-content: center; align-items: center; }
.holo-eye {
  width: 8px; height: 8px; background: #667eea; border-radius: 50%;
  margin: 0 6px; box-shadow: 0 0 8px #667eea; transition: height 0.1s;
}
.holo-eye.blink { height: 2px; }
.holo-mouth {
  width: 20px; height: 4px; background: #667eea; border-radius: 0 0 10px 10px;
  margin-top: 8px; box-shadow: 0 0 6px #667eea; transition: all 0.3s;
}
.holo-mouth.speaking { height: 10px; border-radius: 50%; animation: speakMouth 0.4s ease-in-out infinite alternate; }
.holo-glow {
  position: absolute; inset: -6px; border-radius: 50%;
  border: 1px solid transparent; border-top-color: rgba(102,126,234,0.3);
  animation: holoSpin 4s linear infinite;
}
.holo-particles { position: absolute; inset: -12px; }
.particle {
  position: absolute; width: 3px; height: 3px; background: #667eea; border-radius: 50%;
  animation: particleFloat 2s ease-in-out infinite;
  animation-delay: calc(var(--i) * 0.25s);
  left: calc(50% + cos(calc(var(--i) * 45deg)) * 35px);
  top: calc(50% + sin(calc(var(--i) * 45deg)) * 35px);
}
.holo-label {
  font-size: 11px; color: rgba(102,126,234,0.8); margin-top: 2px; letter-spacing: 2px;
}

/* === Tab Content === */
.tab-content {
  flex: 1; overflow-y: auto; padding: 6px 10px;
  -webkit-overflow-scrolling: touch;
}
.card-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 6px;
}
.m-card {
  display: flex; flex-direction: column; align-items: center; justify-content: center;
  padding: 12px 4px; background: rgba(102,126,234,0.08);
  border: 1px solid rgba(102,126,234,0.12); border-radius: 12px;
  cursor: pointer; transition: all 0.15s; min-height: 60px;
}
.m-card:active { background: rgba(102,126,234,0.2); transform: scale(0.95); }
.m-card-icon { font-size: 22px; margin-bottom: 3px; }
.m-card-label { font-size: 10px; color: #a0b4ff; text-align: center; line-height: 1.2; }

/* === Bottom Tabs === */
.bottom-tabs {
  display: flex; flex-shrink: 0;
  background: rgba(13,16,37,0.95); border-top: 1px solid rgba(102,126,234,0.12);
  padding: 4px 0 env(safe-area-inset-bottom, 4px);
}
.tab-item {
  flex: 1; display: flex; flex-direction: column; align-items: center;
  padding: 6px 0; cursor: pointer; transition: all 0.2s; opacity: 0.45;
}
.tab-item.active { opacity: 1; }
.tab-icon { font-size: 20px; }
.tab-label { font-size: 10px; margin-top: 2px; color: #a0b4ff; }

/* === Chat Overlay === */
.chat-overlay {
  position: fixed; inset: 0; background: rgba(8,11,26,0.98);
  z-index: 100; display: flex; flex-direction: column;
}
.chat-header {
  display: flex; justify-content: space-between; align-items: center;
  padding: 12px 16px; border-bottom: 1px solid rgba(102,126,234,0.2);
  font-size: 16px; font-weight: 600;
}
.chat-close {
  background: none; border: 1px solid rgba(255,255,255,0.2);
  color: #fff; padding: 4px 12px; border-radius: 20px; font-size: 14px; cursor: pointer;
}
.chat-body { flex: 1; overflow-y: auto; padding: 12px; display: flex; flex-direction: column; gap: 8px; }
.chat-msg { max-width: 85%; padding: 10px 14px; border-radius: 16px; font-size: 14px; line-height: 1.4; }
.chat-msg.user { align-self: flex-end; background: #667eea; }
.chat-msg.assistant { align-self: flex-start; background: rgba(255,255,255,0.1); }
.chat-input-row { display: flex; padding: 8px 12px; gap: 8px; border-top: 1px solid rgba(102,126,234,0.2); }
.chat-input {
  flex: 1; padding: 10px 14px; border-radius: 20px;
  border: 1px solid rgba(102,126,234,0.3); background: rgba(255,255,255,0.05);
  color: #fff; font-size: 14px; outline: none;
}
.chat-send {
  padding: 10px 18px; border-radius: 20px; border: none;
  background: #667eea; color: #fff; font-size: 14px; cursor: pointer;
}

@keyframes holoPulse { 0%,100%{transform:scale(1)} 50%{transform:scale(1.05)} }
@keyframes holoSpin { to{transform:rotate(360deg)} }
@keyframes speakMouth { from{height:4px;border-radius:50%} to{height:12px;border-radius:50%} }
@keyframes particleFloat { 0%,100%{opacity:.3;transform:translateY(0)} 50%{opacity:1;transform:translateY(-4px)} }
</style>
