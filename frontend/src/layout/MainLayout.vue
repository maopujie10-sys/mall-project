<template>
  <div class="sci-fi-shell">
    <!-- 3D 神经网络背景 -->
    <div class="neural-bg">
      <NeuralNetwork3D />
    </div>

    <!-- 内容覆盖层 -->
    <div class="content-overlay">
      <router-view v-slot="{ Component }">
        <transition name="page-fade" mode="out-in">
          <component :is="Component" />
        </transition>
      </router-view>
    </div>

    <!-- 4 类漂浮导航光球 -->
    <FloatingNav />

    <!-- AI 漂浮聊天 -->
    <FloatingAI />

    <!-- 手机底部导航 -->
    <nav class="mobile-bottom-nav">
      <router-link to="/friday" class="mb-item"><span>🧠</span><span>大脑</span></router-link>
      <router-link to="/chat" class="mb-item"><span>💬</span><span>对话</span></router-link>
      <router-link to="/dashboard" class="mb-item"><span>📊</span><span>总览</span></router-link>
      <router-link to="/server" class="mb-item"><span>🖥️</span><span>服务器</span></router-link>
      <router-link to="/mall" class="mb-item"><span>🏬</span><span>商城</span></router-link>
    </nav>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRoute } from 'vue-router'
import { useSystemStore } from '@/stores/system'
import { useThemeStore } from '@/stores/theme'
import NeuralNetwork3D from '@/components/NeuralNetwork3D.vue'
import FloatingNav from '@/components/FloatingNav.vue'
import FloatingAI from '@/components/FloatingAI.vue'
import { ElMessage } from 'element-plus'

const route = useRoute()
const systemStore = useSystemStore()
const theme = useThemeStore()

const emergencyVisible = ref(false)
const tokenDialogVisible = ref(false)
const tokenInput = ref(localStorage.getItem('agent_token') || '')

function saveToken() {
  localStorage.setItem('agent_token', tokenInput.value)
  tokenDialogVisible.value = false
  ElMessage.success('Token 已保存')
}

onMounted(() => {
  systemStore.fetchStatus()
})

function isActive(path) {
  return route.path.startsWith(path)
}

<style>
/* ===== 科幻全屏布局 ===== */
.sci-fi-shell {
  width: 100vw; height: 100vh;
  overflow: hidden;
  position: relative;
  background: #0a0a1a;
}

.neural-bg {
  position: fixed; inset: 0;
  z-index: 0;
}

.content-overlay {
  position: fixed; inset: 0;
  z-index: 10;
  pointer-events: none;
  overflow-y: auto;
}
.content-overlay > * {
  pointer-events: all;
}

/* 页面切换动画 */
.page-fade-enter-active { transition: opacity 0.3s, transform 0.3s; }
.page-fade-leave-active { transition: opacity 0.15s, transform 0.15s; }
.page-fade-enter-from { opacity: 0; transform: translateY(10px); }
.page-fade-leave-to { opacity: 0; transform: translateY(-10px); }

/* 手机底部导航 */
.mobile-bottom-nav {
  display: none;
  position: fixed; bottom: 0; left: 0; right: 0;
  z-index: 2000;
  background: rgba(10,10,30,0.9);
  backdrop-filter: blur(20px);
  border-top: 1px solid rgba(102,126,234,0.2);
  padding: 6px 0 env(safe-area-inset-bottom);
  justify-content: space-around;
}
.mb-item {
  display: flex; flex-direction: column; align-items: center; gap: 2px;
  text-decoration: none; color: rgba(255,255,255,0.5);
  padding: 4px 12px; border-radius: 8px; transition: all 0.2s;
  font-size: 10px;
}
.mb-item span:first-child { font-size: 18px; }
.mb-item:hover, .mb-item.router-link-active { color: #667eea; }

@media (max-width: 768px) {
  .mobile-bottom-nav { display: flex; }
  .content-overlay { bottom: 60px; }
}
</style>