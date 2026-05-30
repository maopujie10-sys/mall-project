<template>
  <div :class="{'active': modelValue}" class="notic-pop-container">
    <div class="content">
      <div class="content-info">
        <div class="img-bg" :style="{'background-image': 'url('+ images.noticeImg +')'}">
          {{ t('系统通知') }}
        </div>
        <div v-html="infoData" class="txt-content"></div>
      </div>
      <div class="close" @click="closeHandle"><img :src="images.close" alt=""></div>
    </div>
    <div class="bg"></div>
  </div>
</template>

<script setup name="NoticPop">
import { useI18n } from 'vue-i18n'

defineProps({
  modelValue: {
    type: Boolean,
    default: false
  },
  infoData: {
    type: String,
    default: ''
  }
})

const { t } = useI18n()

const emits = defineEmits(['update:modelValue'])

const images = {
  noticeImg: new URL('@/assets/image/shop/notice_bg.png', import.meta.url),
  close: new URL('@/assets/image/shop/close.png', import.meta.url)
}

const closeHandle = () => {
  emits('update:modelValue', false)
}
</script>

<style lang="scss" scoped>
.notic-pop-container {
  &.active {
    > div {
      opacity: 1;
      pointer-events: auto;
    }
  }
  > div {
    width: 100vw;
    height: 100vh;
    position: fixed;
    top: 0;
    left: 0;
    opacity: 0;
    pointer-events: none;
    transition: all 0.3s ease;
    &.content {
      z-index: 9999;
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      > .content-info {
        width: 84.5vw;
        overflow: hidden;
        background-color: #fff;
        border-radius: 6px;
        > .img-bg {
          width: 84.5vw;
          height: 27vw;
          background-size: cover;
          background-position: center;
          background-repeat: no-repeat;
          color: #fff;
          font-weight: bold;
          font-size: 18px;
          padding-left: 5vw;
          padding-top: 8vw;
        }
        > .txt-content {
          width: 100%;
          max-height: 50vw;
          min-height: 30vw;
          padding: 13px;
          font-size: 12px;
          overflow-y: scroll;
        }
      }
      > .close {
        width: 30px;
        height: 30px;
        margin-top: 20px;
      }
    }
    &.bg {
      background-color: rgba(0,0,0,.4);
      z-index: 9998;
    }
  }
}
</style>
