<template>
  <div id="mall-app">
    <!-- 落地页：无布局，全屏展示 -->
    <template v-if="isLanding">
      <router-view v-slot="{ Component }">
        <transition name="fade" mode="out-in">
          <component :is="Component" />
        </transition>
      </router-view>
    </template>

    <!-- 手机端布局 -->
    <MobileLayout v-else-if="isMobile">
      <router-view v-slot="{ Component }">
        <transition name="slide" mode="out-in">
          <component :is="Component" />
        </transition>
      </router-view>
    </MobileLayout>

    <!-- 商家后台布局 -->
    <MerchantLayout v-else-if="isMerchant">
      <router-view v-slot="{ Component }">
        <component :is="Component" />
      </router-view>
    </MerchantLayout>

    <!-- PC 商城布局 -->
    <PcLayout v-else>
      <router-view v-slot="{ Component }">
        <component :is="Component" />
      </router-view>
    </PcLayout>

    <!-- PWA 安装提示 -->
    <div v-if="showInstallPrompt" class="install-banner glass" @click="installPwa">
      <span>📲 安装到桌面，随时访问</span>
      <button class="btn btn-primary btn-sm">立即安装</button>
    </div>
  </div>
</template>

<script setup>
import { ref, watch, onMounted, computed } from 'vue'
import { useRoute } from 'vue-router'
import PcLayout from '@/layouts/PcLayout.vue'
import MobileLayout from '@/layouts/MobileLayout.vue'
import MerchantLayout from '@/layouts/MerchantLayout.vue'

const route = useRoute()

const isLanding = computed(() => route.path === '/')
const isMerchant = computed(() => route.path.startsWith('/seller/'))
const isMobile = computed(() => {
  if (route.path.startsWith('/m/') || route.path.startsWith('/m') || route.path === '/m') return true
  return window.innerWidth < 768
})

// PWA 安装
const showInstallPrompt = ref(false)
let deferredPrompt = null

window.addEventListener('beforeinstallprompt', e => {
  e.preventDefault()
  deferredPrompt = e
  showInstallPrompt.value = true
})

function installPwa() {
  if (deferredPrompt) {
    deferredPrompt.prompt()
    deferredPrompt.userChoice.then(() => {
      deferredPrompt = null
      showInstallPrompt.value = false
    })
  }
}
</script>

<style>
#mall-app {
  min-height: 100vh;
}

/* 路由切换动画 */
.fade-enter-active, .fade-leave-active {
  transition: opacity 0.25s ease;
}
.fade-enter-from, .fade-leave-to {
  opacity: 0;
}

.slide-enter-active, .slide-leave-active {
  transition: transform 0.25s ease, opacity 0.25s ease;
}
.slide-enter-from {
  transform: translateX(20px);
  opacity: 0;
}
.slide-leave-to {
  transform: translateX(-20px);
  opacity: 0;
}

/* PWA 安装提示 */
.install-banner {
  position: fixed;
  bottom: 80px;
  left: 50%;
  transform: translateX(-50%);
  z-index: 200;
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 12px 24px;
  border-radius: var(--border-radius);
  font-size: 14px;
  animation: slideUp 0.3s ease-out;
}
</style>
