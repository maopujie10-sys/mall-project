<template>
  <div
    class="service-box flex flex-col pb-150"
    :style="{ height: height + 'px' }"
  >
    <div>
      <van-nav-bar
        :fixed="false"
        ref="navEl"
        :title="$t('onLineService')"
        left-arrow
        @click-left="onClickLeft"
      />
      <!-- <div class="px-3.5 py-5" :style="{'margin-top': navHeight + 'px'}"> -->
      <!-- <div class="text-xl black">订单将在 <span style="color: #2555F8">13：03</span> 后取消</div>
        <div class="mt-3 text-sm">
          <span class="mr-1" style="color: #8A919E">总额</span>
          <span class="black">$ 33,350.00</span>
        </div>
        <div class="mt-5">
          <van-button class="w-full" type="primary" @click="router.back()">去付款</van-button>
        </div> -->
      <!-- </div> -->
    </div>
    <div
      ref="msgContent"
      class="content flex-1 overflow-auto"
      style="background: #f5f5f5; padding-bottom: 70px"
    >
      <div
        class="flex flex-col px-16 box-border h-full"
        style="background: #f5f5f5; padding-bottom: 70px"
      >
        <div
          class="w-full py-4 text-grey text-center pt-100"
          @click="onMore"
          :style="{ display: finished ? 'none' : 'block' }"
        >
          {{ $t('historyMessage') }}
        </div>
        <ul ref="msgTxtContent" class="flex flex-col pt-3">
          <li
            v-for="(item, index) in list"
            :key="item.id"
            class="flex flex-col my-3"
          >
            <p
              class="font-13 text-center py-2 text-grey"
              v-if="showTime(index)"
            >
              {{ formatZoneDate(item.createtime, 'YYYY-MM-DD') }}
            </p>

            <div
              class="flex responser-content items-center"
              :class="item.send_receive === 'send' ? 'justify-end' : ''"
            >
              <template v-if="item.send_receive === 'receive'">
                <img
                  :src="serviceLogo"
                  class="w-9 h-9"
                  :class="isArLang ? 'ml-3' : 'mr-3'"
                  style="border-radius: 50%"
                />
                <div>
                  <div class="text-xs text-grey mb-1">
                    {{ formatZoneDate(item.createtime, 'YYYY-MM-DD HH:mm') }}
                  </div>
                  <!-- <div v-if="item.type === 'text'" class="chat-res-content text-sm">{{ item.content }}</div> -->
                  <div
                    v-if="item.type === 'text'"
                    class="chat-res-content text-sm"
                  >
                    <p v-html="item.content"></p>
                  </div>
                  <div v-else class="chat-res-content img text-sm">
                    <img :src="item.imgUrl" @click="onPreview(item.imgUrl)" />
                  </div>
                </div>
              </template>
              <template v-else>
                <div>
                  <div class="text-xs text-grey mb-1" style="text-align: right">
                    {{ formatZoneDate(item.createtime, 'YYYY-MM-DD HH:mm') }}
                  </div>
                  <!-- <div v-if="item.type === 'text'" class="chat-res-content text-sm" :class="item.send_receive === 'send' ? 'send-bg' : ''">{{ item.content }}</div> -->
                  <div
                    v-if="item.type === 'text'"
                    class="chat-res-content text-sm"
                    :class="item.send_receive === 'send' ? 'send-bg' : ''"
                  >
                    <p v-html="item.content"></p>
                  </div>
                  <div v-else class="chat-res-content img text-sm">
                    <img
                      :src="`${item.imgUrl}`"
                      @click="onPreview(item.imgUrl)"
                    />
                  </div>
                </div>
                <img
                  :src="fullAvatar"
                  class="w-9 h-9"
                  :class="isArLang ? 'mr-3' : 'ml-3'"
                  style="border-radius: 50%"
                />
              </template>
            </div>
          </li>
        </ul>
      </div>
    </div>
    <div
      class="relative bottom bottomBox flex justify-between items-center w-full fixed bottom-0 borderTop px-4 box-border bgBottom bg-white"
    >
      <!-- <van-uploader :max-size="10000 * 1024" @oversize="onOversize" :after-read="afterRead" :capture="androidAttrs ? 'camera' : null"> -->
      <van-uploader
        :max-size="10000 * 1024"
        @oversize="onOversize"
        :after-read="afterRead"
      >
        <img :src="iconImg.photo" class="w-9 h-9" />
      </van-uploader>
      <div
        class="flex-1 mx-3 h-full border-none bgBottom textColor send-msg-content"
      >
        <textarea
          v-model="message"
          :placeholder="$t('entryYouMessage')"
          class="flex-1 mx-3 h-full border-none bgBottom textColor"
          style="resize: none; background-color: #fff;"
        ></textarea>
      </div>

      <i class="iconfont icon-fasong" @click="send('text', message)"></i>
    </div>
  </div>
</template>

<script setup>
import { Uploader, ImagePreview } from 'vant'
import { _getMsg, _getUnreadMsg, _sendMsg } from '@/service/im.api'
import { _uploadImage, uploadimgExecute } from '@/service/upload.api'
import { ref, onMounted, onUnmounted, computed, nextTick } from 'vue'
import { useI18n } from 'vue-i18n'
import { Toast } from 'vant'
import { useRouter, useRoute } from 'vue-router'
import { useUserStore, useShopInfoStore } from '@/store/user.js'
import { formatZoneDate } from '@/utils'
import { useWindowSize } from '@vueuse/core'
import { arLangCheck } from '@/utils/arLangCheck'

const isArLang = arLangCheck()

const { height } = useWindowSize()

const fullAvatar = ref(
  new URL(`/src/assets/image/avatar/avatar_d.png`, import.meta.url).href
)

const { t, locale } = useI18n()

const route = useRoute()

const router = useRouter()
const list = ref([])
const message = ref('')
const lastMsgId = ref('')
const interval = ref(null)
const unread = ref(0)
const finished = ref(false)
const androidAttrs = ref(null)
const navEl = ref(null)
const navHeight = ref(0)
const startInterval = ref(false)

const iconImg = {
  responser: new URL('../../assets/image/service/responser.png', import.meta.url),
  argos: new URL('../../assets/image/logo/argos.png', import.meta.url),
  argos2: new URL('../../assets/image/logo/argos.png', import.meta.url),
  argos3: new URL('../../assets/image/logo/argos.png', import.meta.url),
  familyShop: new URL('../../assets/image/logo/familyShop.png', import.meta.url),
  hive: new URL('../../assets/image/logo/hive.png', import.meta.url),
  inchoi: new URL('../../assets/image/logo/inchoi.png', import.meta.url),
  mbuy: new URL('../../assets/image/logo/mbuy.png', import.meta.url),
  greenMall: new URL('../../assets/image/logo/greenMall.png', import.meta.url),
  tiktokMall: new URL('../../assets/image/logo/tiktokMall.png', import.meta.url),
  shop2u: new URL('../../assets/image/logo/shop2u.png', import.meta.url),
  sm: new URL('../../assets/image/logo/sm.png', import.meta.url),
  iceland: new URL('../../assets/image/logo/iceland.png', import.meta.url),
  int: new URL('../../assets/image/logo/int.png', import.meta.url),
  'tiktok-wholesale': new URL('../../assets/image/logo/tiktok-wholesale.png', import.meta.url),
  antMall: new URL('../../assets/image/logo/antMall.png', import.meta.url),
  simon: new URL('../../assets/image/logo/simon.png', import.meta.url),
  texm: new URL('../../assets/image/logo/texm.png', import.meta.url),
  azedi: new URL('../../assets/image/logo/azedi.png', import.meta.url),
  starMall: new URL('../../assets/image/logo/starMall.png', import.meta.url),
  'alibaba-wholesale': new URL('../../assets/image/logo/alibaba-wholesale.png', import.meta.url),
  'sam-wholesale': new URL('../../assets/image/logo/sam-wholesale.png', import.meta.url),
  photo: new URL('../../assets/image/service/photo.png', import.meta.url)
}

const msgContent = ref(null)
const msgTxtContent = ref(null)
const sendOrFirstLoad = ref(false)

const serviceLogo = computed(() => {
  const mode = import.meta.env.MODE
  let logo = iconImg.responser.href
  if (mode && iconImg[mode]) {
    logo = iconImg[mode].href
  }

  return logo
})

// 店铺信息
const useShopStore = useShopInfoStore()
const shopLogo = computed(() => {
  return useShopStore.shopInfo?.avatar || ''
})

onMounted(async () => {
  navHeight.value = navEl.value.$el.getBoundingClientRect().height
  startInterval.value = false
  const model = navigator.userAgent
  // 判断是否是安卓手机，是则是true
  androidAttrs.value =
    model.indexOf('Android') > -1 || model.indexOf('Linux') > -1

  const { avatar, token, lang } = route.query
  if (shopLogo.value) {
    fullAvatar.value = shopLogo.value
  }

  if (avatar) {
    fullAvatar.value = avatar
  }

  if (lang) {
    locale.value = lang
    localStorage.setItem('lang', lang)
  }

  if (token) {
    const userStore = useUserStore()
    await userStore.getUserInfo(true, token)
  }

  sendOrFirstLoad.value = true
  fetchList()
})

const onOversize = (file) => {
  Toast(t('fileMaxLimit'))
}
const onPreview = (url) => {
  // 预览
  ImagePreview([url])
}
const showTime = (index) => {
  // 时间显示
  let res = false
  if (index === 0) {
    res = true
  }
  if (
    index > 0 &&
    list.value[index].createtime.split(' ')[0] !==
      list.value[index - 1].createtime.split(' ')[0]
  ) {
    res = true
  }
  return res
}
const afterRead = (file) => {
  // 文件上传
  Toast.loading({ duration: 0 })
  uploadimgExecute({
    file: file.file,
    moduleName: 'customerService'
  })
    .then((data) => {
      Toast.clear()
      send('img', data)
    })
    .catch(() => {
      Toast.clear()
    })

  // _uploadImage(file, (percent) => {
  //   console.log(percent)
  // }).then(data => {
  //   Toast.clear()
  //   send('img', data)
  // }).catch(() => {
  //   Toast.clear()
  // })
}
const fetchList = (message_id = '') => {
  // 获取消息列表
  _getMsg({ message_id }).then((data) => {
    //
    if (!lastMsgId.value) {
      lastMsgId.value = data.length && data[data.length - 1]['id']
    }
    if (data.length) {
      let dataArr = []
      data.forEach((item) => {
        if (item.type === 'img') {
          const imgUrl = item.content
          const str = 'imagePath='
          item.imgUrl = imgUrl
          const index = imgUrl.indexOf(str)
          if (index > 0) {
            const url = imgUrl.slice(index + str.length)
            item.imgUrl = url
          }
        }
      })
      if (message_id) {
        // 加载更多
        lastMsgId.value = data[data.length - 1]['id']
        dataArr = filterDeleteMsg([...data.reverse(), ...list.value])
      } else {
        dataArr = filterDeleteMsg([...list.value, ...data.reverse()])
        let hash = {}
        dataArr = dataArr.reduce(function (preVal, curVal) {
          hash[curVal.id]
            ? ' '
            : (hash[curVal.id] = true && preVal.push(curVal))
          return preVal
        }, [])
      }
      list.value = dataArr
      if (data.length < 10) {
        finished.value = true
      }
    }

    if (sendOrFirstLoad.value) {
      nextTick(() => {
        msgContent.value.scrollTop = msgTxtContent.value.offsetHeight
        sendOrFirstLoad.value = false
      })
    }

    if (!startInterval.value) {
      startInterval.value = true
      interval.value = setInterval(() => {
        fetchList()
      }, 1000)
    }
  })
}

const filterDeleteMsg = (data) => {
  let ids = []
  ids = data.filter(item => Number(item.delete_status) === -1).map(item => item.id)
  return data.filter(item => !ids.includes(item.id))
}

const onMore = () => {
  // 加载更多
  fetchList(lastMsgId.value)
}
const clearIntervalTimer = () => {
  if (interval.value) {
    clearInterval(interval.value)
    interval.value = null
  }
}
const fetchUnread = () => {
  // 获取未读
  _getUnreadMsg().then((data) => {
    unread.value = data
    // console.log(data)
  })
}
const onClickLeft = () => {
  // 返回
  router.go(-1)
}

const sendLoading = ref(false)
const send = (type = 'text', content = '') => {
  // 发送消息, img 也当消息text
  if (sendLoading.value) {
    return
  }
  if (!content) {
    Toast(t('entryMessageContent'))
    return
  }

  Toast.loading({
    duration: 0,
    forbidClick: true
  })
  sendLoading.value = true

  _sendMsg(type, content)
    .then((data) => {
      console.log(data)
      message.value = ''
      sendLoading.value = false
      Toast.clear()
      // document.getElementById('bottom').click()
      sendOrFirstLoad.value = true
      fetchList()
    })
    .catch(() => {
      sendLoading.value = false
      Toast.clear()
    })
}
onUnmounted(() => {
  clearIntervalTimer()
})
</script>
<style lang="scss" scoped>
.service-box {
  width: 100%;
  box-sizing: border-box;

  :deep(.van-hairline--bottom::after) {
    border-color: #f3f3f3;
  }
}

.send-bg {
  background-color: rgb(255, 234, 209) !important;
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
  color: #1f2025;
}

.chatBg {
  border-radius: 10.0022px 10.0022px 0px 10.0022px;
  max-width: 50vw;
}

.responser-content {
  > img {
    &.res {
      //width: 36px;
      //height: 36px;
      //margin: 0;
      //margin-right: 15px;
    }
  }
  > .res-content {
    border-radius: 10.0022px 10.0022px 10.0022px 0;
  }
}

.chat-res-content {
  padding: 10px;
  border-radius: 10.0022px 10.0022px 10.0022px 0;
  background-color: #fff;
  max-width: 70vw;
  word-break: break-all;
  &.img {
    max-width: 50vw;
    > img {
      width: 100%;
      height: auto;
      margin: 0;
    }
  }
  > p {
    white-space: pre-line;
    word-break: normal;
  }
}

.send-msg-content {
  padding: 10px 0;
  > textarea {
    width: 100%;
    padding: 10px 0;
    margin: 0;
  }
}

.icon-fasong {
  color: var(--site-main-color);
  font-size: 28px;
}
</style>
