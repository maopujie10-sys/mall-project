<template>
  <div class="view-pdf-content">
    <vue-pdf-embed v-if="!pageLoading" :source="source"></vue-pdf-embed>

    <div v-if="source && download && !pageLoading" class="download-btn">
      <van-button
        type="primary"
        @click="downloadHandle"
      >{{ t('下载') }}
      </van-button>
    </div>
  </div>
</template>

<script setup name="ViewPdf">
import { ref, nextTick } from 'vue'
import { Toast } from 'vant'
import { createLoadingTask } from 'vue3-pdfjs/esm'
import VuePdfEmbed from 'vue-pdf-embed'
import { useI18n } from 'vue-i18n'

const { t } = useI18n()

const props = defineProps({
  source: {
    type: String,
    default: ''
  },
  download: {
    type: Boolean,
    default: true
  }
})

const pageLoading = ref(true)
// 加载pdf
const getPdfInfo = () => {
  pageLoading.value = true
  Toast.loading({ duration: 0, mask: true })
  const loadingTask = createLoadingTask(props.source)
  loadingTask.promise.then(pdf => {
    pageLoading.value = false
    Toast.clear()
  })
}

const downloadHandle = () => {
  if (window.plus) {
    window.plus.runtime.openURL(props.source)
  } else if(window.webkit) {
    window.webkit.messageHandlers.openWindow.postMessage({url: props.source})
  } else {
    try {
      const url = props.source
      const fileNameStr = url.slice(url.lastIndexOf('/') + 1)
      const fileName = fileNameStr.indexOf('?') > -1 ? fileNameStr.slice(0, fileNameStr.indexOf('?')) : fileNameStr
      const link = document.createElement('a')
      Toast.loading({ duration: 0, mask: true })
      fetch(url + '?' + new Date().getTime()).then(res => res.blob()).then(blob => { // 将链接地址字符内容转变成blob地址
        link.href = URL.createObjectURL(blob)
        link.download = fileName;
        document.body.appendChild(link)
        link.click()
        link.remove()
        Toast.clear()
      })
    } catch {
      console.log('err')
    }
  }
}

nextTick(() => {
  getPdfInfo()
})
</script>

<style lang="scss" scoped>
.view-pdf-content {
  width: 100%;
}

.download-btn {
  width: 60%;
  position: fixed;
  left: 50%;
  transform: translateX(-50%);
  bottom: 50px;
  z-index: 9;
  :deep(.van-button) {
    width: 100%;
    background-color: var(--site-main-color);
    border-radius: 100px;
  }
}
</style>
