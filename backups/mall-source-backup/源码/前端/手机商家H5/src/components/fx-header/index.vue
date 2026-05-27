<template>
  <div class="fx-header">
    <van-nav-bar :title="title" :left-arrow="showLeft" :fixed="fixed" @click-left="onClickLeft">
      <template #title>
        <slot name="title"></slot>
      </template>
      <template #right>
        <slot name="right"></slot>
      </template>
    </van-nav-bar>
  </div>
  
</template>

<script setup>
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { arLangCheck } from '@/utils/arLangCheck'
const emit = defineEmits(['back'])
const props = defineProps({
  title: {
    type: String,
    default: ''
  },
  // 是否路由返回
  back: {
    default: true
  },
  showLeft: {
    type: Boolean,
    default: true
  },
  fixed: {
    type: Boolean,
    default: false
  }
})

const router = useRouter();

const isArLang = arLangCheck()

// 返回
const onClickLeft = () => {
  return props.back ? router.back() : emit('back')
}

</script>

<style lang="scss" scoped>
.fx-header {
  :deep(.van-icon) {
    font-size: 18px;
    color: #1F2025;
  }

  :deep(.van-nav-bar__title) {
    color: #333;
  }

  :deep(.van-nav-bar__right) {
    color: #999;
  }

  :deep(.van-nav-bar--fixed) {
    z-index: 99 !important;
  }
}
</style>
