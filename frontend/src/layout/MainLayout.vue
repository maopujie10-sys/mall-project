
<template>
  <div class="sci-fi-shell">
    <div class="neural-bg" :class="{ 'brain-active': brainActive, 'brain-thinking': brainThinking, 'brain-speaking': brainSpeaking, 'brain-pulse': brainPulse }">
      <NeuralNetwork3D />
    </div>
    <div class="content-overlay">
      <router-view v-slot="{ Component }">
        <transition name="page-fade" mode="out-in">
          <component :is="Component" />
        </transition>
      </router-view>
    </div>
    <FloatingNav />
    <FloatingAI />
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import { useRoute } from 'vue-router'
import { useSystemStore } from '@/stores/system'
import NeuralNetwork3D from '@/components/NeuralNetwork3D.vue'
import FloatingNav from '@/components/FloatingNav.vue'
import FloatingAI from '@/components/FloatingAI.vue'

const route = useRoute()
const systemStore = useSystemStore()
const brainActive = ref(false)
const brainThinking = ref(false)
const brainSpeaking = ref(false)
const brainPulse = ref(false)

watch(() => route.path, (path) => {
  const overlay = document.querySelector('.content-overlay')
  if (overlay) {
    if (path === '/friday' || path === '/') {
      overlay.classList.remove('has-content')
    } else {
      overlay.classList.add('has-content')
    }
  }
})
async function autoLogin() {
  const token = localStorage.getItem('agent_token')
  if (token) return token
  try {
    const res = await fetch('/agent/auth/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username: 'admin', password: 'admin123' })
    })
    if (res.ok) {
      const data = await res.json()
      if (data.access_token) {
        localStorage.setItem('agent_token', data.access_token)
        localStorage.setItem('friday_token', data.access_token)
      }
    }
  } catch (e) {}
}

function openFloatingChat() {
  const btn = document.querySelector('.ai-float-btn')
  if (btn) btn.click()
}
// 鐩戝惉璺敱鍙樺寲锛屾湁鍐呭鏃舵樉绀哄彔灞?let contentTimer = null
function showContent() {
  const overlay = document.querySelector('.content-overlay')
  if (overlay) overlay.classList.add('has-content')
}
function hideContent() {
  const overlay = document.querySelector('.content-overlay')
  if (overlay && window.location.hash === '' && window.location.pathname === '/ai/' || window.location.pathname === '/ai/friday') {
    // 棣栭〉涓嶆樉绀哄唴瀹?  } else if (overlay) {
    overlay.classList.add('has-content')
  }
}
onMounted(async () => {
  window.addEventListener('floating:openChat', openFloatingChat)
  await autoLogin()
  systemStore.fetchStatus()
  window.addEventListener('brain:active', (e) => { brainActive.value = e.detail })
  window.addEventListener('brain:thinking', (e) => { brainThinking.value = e.detail })
  window.addEventListener('brain:speaking', () => { brainSpeaking.value = true; setTimeout(() => { brainSpeaking.value = false }, 2000) })
  window.addEventListener('brain:pulse', () => { brainPulse.value = true; setTimeout(() => { brainPulse.value = false }, 600) })
  window.addEventListener('brain:openChat', () => { const btn = document.querySelector('.ai-float-btn'); if (btn) btn.click() })
})
</script>
<style>
/* ===== 绉戝够鍏ㄥ睆甯冨眬 ===== */
.sci-fi-shell {
  width: 100vw; height: 100vh;
  overflow: hidden;
  position: relative;
  background: #0a0a1a;
}

.neural-bg { position: fixed; inset: 0; width: 100vw; height: 100vh; z-index: 0;
  position: fixed; inset: 0;
  z-index: 0;
}

.content-overlay { position: fixed; inset: 0; z-index: 1; pointer-events: none;
  position: fixed; inset: 0;
  z-index: 10;
  pointer-events: none;
  overflow-y: auto;
}
.content-overlay > * {
  pointer-events: all;
}

/* 椤甸潰鍒囨崲鍔ㄧ敾 */
.page-fade-enter-active { transition: opacity 0.3s, transform 0.3s; }
.page-fade-leave-active { transition: opacity 0.15s, transform 0.15s; }
.page-fade-enter-from { opacity: 0; transform: translateY(10px); }
.page-fade-leave-to { opacity: 0; transform: translateY(-10px); }





/* 3D澶ц剳鑱斿姩鑴夊啿 */
.neural-bg.brain-active {
  filter: brightness(1.15) saturate(1.2);
  transition: filter 0.5s ease;
}
.neural-bg.brain-thinking {
  animation: brainThink 1.5s ease-in-out infinite;
}
.neural-bg.brain-speaking {
  filter: brightness(1.3) saturate(1.3);
  animation: brainSpeak 0.8s ease-in-out infinite;
}
.neural-bg.brain-pulse {
  animation: brainShock 0.6s ease-out;
}
@keyframes brainThink {
  0%, 100% { filter: brightness(1.1) saturate(1.1) hue-rotate(0deg); }
  50% { filter: brightness(1.25) saturate(1.3) hue-rotate(5deg); }
}
@keyframes brainSpeak {
  0%, 100% { filter: brightness(1.3) saturate(1.3); transform: scale(1); }
  25% { filter: brightness(1.5) saturate(1.5); transform: scale(1.005); }
  75% { filter: brightness(1.2) saturate(1.2); transform: scale(0.998); }
}
@keyframes brainShock {
  0% { filter: brightness(2) saturate(2); transform: scale(1.02); }
  100% { filter: brightness(1.15) saturate(1.2); transform: scale(1); }
}
</style>