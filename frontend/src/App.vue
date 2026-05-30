<template>
  <MobileLayout v-if="isMobile" />
  <router-view v-else />
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import MobileLayout from '@/components/MobileLayout.vue'

const isMobile = ref(false)

function checkMobile() {
  isMobile.value = window.innerWidth < 768 || ('ontouchstart' in window)
}

onMounted(() => {
  checkMobile()
  window.addEventListener('resize', checkMobile)
})
onUnmounted(() => {
  window.removeEventListener('resize', checkMobile)
})
</script>

<style>
/* === Global Reset === */
html, body {
  margin: 0; padding: 0;
  width: 100%; height: 100%;
  overflow-x: hidden;
  -webkit-overflow-scrolling: touch;
  -webkit-tap-highlight-color: transparent;
  background: #080b1a;
  color: #e0e0e0;
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
}
#app { width: 100%; min-height: 100%; min-height: 100dvh; }

/* Safe area for notched phones */
@supports (padding: env(safe-area-inset-top)) {
  body {
    padding-top: env(safe-area-inset-top);
    padding-bottom: env(safe-area-inset-bottom);
    padding-left: env(safe-area-inset-left);
    padding-right: env(safe-area-inset-right);
  }
}

/* Responsive tweaks for desktop views on tablet */
@media (max-width: 768px) {
  .el-card { border-radius: 8px !important; }
  .el-button { font-size: 13px !important; padding: 8px 14px !important; }
}

/* PWA standalone */
@media (display-mode: standalone) {
  body { padding-top: 20px; }
}
</style>
