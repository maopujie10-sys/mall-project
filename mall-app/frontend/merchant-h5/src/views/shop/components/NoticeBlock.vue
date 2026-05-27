<template>
  <div v-if="noticeText" class="notice-block">
    <van-notice-bar
      color="#333333"
      background="#ffffff"
      :text="noticeText"
    >
      <template #left-icon>
        <van-icon name="volume" class="left-icon" />
      </template>
    </van-notice-bar>
  </div>
</template>

<script setup name="NoticeBlock">
  import { ref, nextTick } from "vue"

  import {
    cmsList
  } from '@/service/shop.api.js'

  const emits = defineEmits(['done'])

  const noticeText = ref('')

  const getCmsData = () => {
    cmsList().then(res => {
      noticeText.value = res && res.content ? res.content : ''
      emits("done", noticeText.value)
    })
  }

  nextTick(() => {
    getCmsData()
  })

  // 子组件传递数据
  defineExpose({
    getCmsData
  })
</script>

<style lang="scss" scoped>
.notice-block {
  margin-bottom: 15px;
  .notice-swipe {
    height: 40px;
    line-height: 40px;
  }
  .van-notice-bar {
    border-radius: 4px;
    overflow: hidden;
  }
  :deep(.van-notice-bar) {
    padding: 0 15px;
  }
  :deep(.van-notice-bar__wrap) {
    margin-left: 10px;
  }
  :deep(.left-icon) {
    color: var(--site-main-color);
    font-size: 18px;
  }
}
</style>
