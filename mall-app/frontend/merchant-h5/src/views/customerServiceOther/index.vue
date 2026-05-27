<template>
  <div class="iframe-content">
    <iframe :src="serviceUrl" class="flex-1"></iframe>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useSystemStore } from "@/store/system.js";
const systemStore = useSystemStore()

const serviceUrl = computed(() => {
  return systemStore.customer_service_url || ''
})
</script>

<style lang="scss" scoped>
.iframe-content {
  width: 100vw;
  height: 100vh;
  > iframe {
    width: 100%;
    height: 100%;
  }
}
</style>
