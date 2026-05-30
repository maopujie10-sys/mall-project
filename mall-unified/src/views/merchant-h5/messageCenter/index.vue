<template>
  <div>
    <div>
      <van-nav-bar ref="navEl" :title="title" left-arrow @click-left="onClickLeft" fixed/>
    </div>
    <div v-if="chatSrc" :style="{height: (calcHeight + 46) + 'px'}" class="iframe-content">
      <iframe :src="chatSrc" class="flex-1"></iframe>
    </div>
  </div>
</template>

<script setup>
import {ref, nextTick} from "vue";
import {useI18n} from "vue-i18n";
import {Toast} from "vant";
import {useRoute} from "vue-router";
import { useUserStore } from '@/store/user'

import { useWindowSize } from '@vueuse/core'
import {
  sellerInfo
} from '@/service/shop.api.js'
import qs from  'qs'
const {  height } = useWindowSize()
const el = ref(null)
const calcHeight = height.value - 46
const {t} = useI18n()
const store = useUserStore()

let host = ''
if(process.env.NODE_ENV === 'development') {
  host = 'tiktokmall666.com'
} else {
  host = location.host
}

const route = useRoute()
let dataObj = null
if ('partyId' in route.query) {
  dataObj = {
    token: store.userInfo.token,
    lang: localStorage.getItem('lang') || 'en',
    height:`${calcHeight}px`,
    partyid: route.query.partyId,
    // isH5: true,
    name: route.query.username
  }
} else {
  dataObj = {
    token: store.userInfo.token,
    lang: localStorage.getItem('lang') || 'en',
    height:`${calcHeight}px`
  }
}
let title = ref('')
if ('name' in dataObj) {
  title.value = dataObj.name
} else {
  title.value = t('消息中心')
}

const chatSrc = ref('')
nextTick(async () => {
  Toast.loading({duration: 0})
  let avatar = ''
  try {
    await sellerInfo().then(res => {
      avatar = res.avatar || ''
    })
  } catch(err) {
    console.log(err)
  }
  
  dataObj.nohead = true
  dataObj.type = 'shop'
  if (avatar) {
    dataObj.selfimg = avatar
  }
  chatSrc.value = 'https://' + host + '/chat/#/h5/message/blue?' + qs.stringify(dataObj)
})
const onClickLeft = () => { // 返回
  router.go(-1);
}
</script>

<style lang="scss" scoped>
.service-box {
  width: 100%;
  box-sizing: border-box;

  :deep(.van-hairline--bottom::after) {
    border-color: #f3f3f3;
  }
}

.break-word {
  word-wrap: break-word;
}

.max-w-230 {
  max-width: 115px;
}

.responser {
  position: relative;

  &::after {
    content: '';
    width: 0;
    height: 0;
    border-top: 5px solid transparent;
    border-bottom: 5px solid transparent;
    border-right: 10px solid #f3f3f3;
    position: absolute;
    left: -10px;
    top: 10px;
  }
}

.borderTop {
  border-top: 1px solid #f3f3f3;
}

.bottomBox {
  height: 65px;
}

.black {
  color: #1F2025;
}

.chatBg {
  border-radius: 10.0022px 10.0022px 0px 10.0022px;
  max-width: 50vw;
}

.responser-content {
  > img {
    &.res {
      width: 50px;
      height: 50px;
      margin: 0;
      margin-right: 15px;
    }
  }
  > .res-content {
    border-radius: 10.0022px 10.0022px 10.0022px 0;
  }
}

.iframe-content {
  width: 100%;
  height: 100vh;
  padding-top: 46px;
  > iframe {
    width: 100%;
    height: 100%;
  }
}
</style>
