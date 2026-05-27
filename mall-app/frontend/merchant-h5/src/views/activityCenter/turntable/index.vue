<template>
  <div class="turntable-page">
    <div class="audio-container">
      <!-- <audio :src="bgMp3" autoplay loop="loop" ref="bgAudio"></audio> -->
      <audio :src="bgMp3" loop="loop" ref="bgAudio"></audio>
      <audio :src="getImg('activity/turntable/audio/rolling.mp3')" loop="loop" ref="rollingAudio"></audio>
      <audio :src="getImg('activity/turntable/audio/click.mp3')" ref="clickAudio"></audio>
      <audio :src="getImg('activity/turntable/audio/success.mp3')" ref="successAudio"></audio>
      <audio :src="getImg('activity/turntable/audio/fail.mp3')" ref="failAudio"></audio>
    </div>

    <!-- 登录弹窗 -->
    <login-dialog v-model="showLogin" @done="getActivityUserInfo"></login-dialog>

    <!-- 提示弹窗 -->
    <tips-dialog v-model="showTips" :tips-title="tipsTitle" :tips-info="tipsInfo" :again="shakeAgain" :times="turnTimes" @again="turnHandle(false)"></tips-dialog>

    <div v-if="showActive" class="turntable-warp">
      <div class="language-content">
        <LanguageChange />
      </div>
      <div class="play-content" @click="playBgHandle">
        <div class="play">
          <img :src="getImg(playBg ? 'activity/turntable/icon1.png' :'activity/turntable/icon2.png')" alt="">
        </div>
      </div>
      <div :style="{'background-image': 'url('+ getImg('activity/turntable/page-header.png') +')'}" class="page-header">
        <div class="img-width light-left">
          <img :src="getImg('activity/turntable/light-left.png')" alt="">
        </div>
        <div class="img-width light-right">
          <img :src="getImg('activity/turntable/light-right.png')" alt="">
        </div>
        <div class="img-width cart">
          <img :src="getImg('activity/turntable/cart.png')" alt="">
        </div>
        <div class="img-height target">
          <img :src="getImg('activity/turntable/target.png')" alt="">
        </div>
        <div class="img-height trumpet1">
          <img :src="getImg('activity/turntable/trumpet1.png')" alt="">
        </div>
        <div class="img-width trumpet2">
          <img :src="getImg('activity/turntable/trumpet2.png')" alt="">
        </div>
        <h1>{{ t('开店赢大奖') }}</h1>
        <h1 class="shadow-txt">{{ t('开店赢大奖') }}</h1>
        <div class="title-info">
          <div>{{ t('幸运转不停') }}</div>
        </div>
      </div>
      <div :style="{'background-image': 'url('+ getImg('activity/turntable/page-bg.png') +')'}" class="page-content">
        <div class="turntable-container">
          <div :style="{'background-image': 'url('+ getImg('activity/turntable/machine2.png') +')'}" class="machine-content">
            <div :class="{'active': rodActive}" class="img-width rod"><img :src="getImg('activity/turntable/machine1.png')" alt=""></div>
            <div class="notice-content">
              <van-swipe class="swiper" :autoplay="3000" :show-indicators="false" vertical>
                <van-swipe-item v-for="item in noticeData" :key="item">
                  <div class="notice-item">{{ item }}</div>
                </van-swipe-item>
              </van-swipe>
            </div>
            <div class="light-content top left" :class="{'active': rolling}"><div class="item"></div><div class="item"></div><div class="item"></div></div>
            <div class="light-content top right" :class="{'active': rolling}"><div class="item"></div><div class="item"></div><div class="item"></div></div>
            <div class="light-content bottom left" :class="{'active': rolling}"><div class="item"></div><div class="item"></div><div class="item"></div></div>
            <div class="light-content bottom right" :class="{'active': rolling}"><div class="item"></div><div class="item"></div><div class="item"></div></div>
            <div v-if="canvasWidth && canvasHeight" dir="ltr" class="lottery-content">
              <LuckyGrid 
                ref="lotteryCanvas"
                :width="canvasWidth"
                :height="canvasHeight"
                :default-config="defaultConfig"
                :default-style="defaultStyle"
                :active-style="activeStyle"
                :prizes="prizes"
                @end="endCallback"
              />
            </div>
            <div dir="ltr" class="btn-content">
              <div :style="{'background-image': 'url('+ getImg('activity/turntable/start-btn1.png') +')'}" :class="{'active': oneTouch, 'disabled': rodActive}" class="btn one" @click="turnHandle(false)" @touchstart="btnTouchStart(true)" @touchend="btnTouchEnd(true)">
                <h3>{{ t('抽N次', {times: 1}) }}</h3>
                <p v-if="activityInfo.pointsToNumber">{{ t('消耗N积分', {points: activityInfo.pointsToNumber}) }}</p>
              </div>
              <div :style="{'background-image': 'url('+ getImg('activity/turntable/start-btn2.png') +')'}" :class="{'active': twoTouch, 'disabled': rodActive}" class="btn two" @click="turnHandle(true)" @touchstart="btnTouchStart(false)" @touchend="btnTouchEnd(false)">
                <h3>{{ t('抽N次', {times: 5}) }}</h3>
                <p v-if="activityInfo.pointsToNumber" class="color">{{ t('消耗N积分', {points: activityInfo.pointsToNumber * 5}) }}</p>
              </div>
            </div>
            <div v-if="isLogin" :class="{'is-ar': isArLang}" class="user-content">
              <div class="item">
                <div v-if="!isMobileRef">
                  <span>{{ showUserName }}</span>
                  {{ t('欢迎您！') }}
                </div>
                <van-notice-bar
                  v-else
                  color="#ffffff"
                  background="rgba(0,0,0,0)"
                  :text="showUserName + ' ' + t('欢迎您！')"
                >
                </van-notice-bar>
              </div>
              <div class="item">
                {{ t('剩余积分') }}
                <span>{{ pointsRef }}</span>
              </div>
            </div>
            <div v-else class="user-content login" @click="showLogin = true">{{ t('请先登录') }}</div>
          </div>
          <div class="block-content">
            <div class="block-bottom"></div>
            <div class="block-line left"></div>
            <div class="block-line right"></div>
            <div class="title">{{ t('我的奖品') }}</div>
            <div class="content my-prize">
              <div class="item">
                <h2>{{ numberStrFormat(myAmount) }}</h2>
                <p>{{ t('累计彩金') }}</p>
                <div :class="{'active': myAmount > activityInfo.minPoints}" @click="receiveHandle(2)">{{ t('领取') }}</div>
              </div>
              <div class="item">
                <h2>{{ myGoodsNum }}</h2>
                <p>{{ t('获得实物') }}</p>
                <div :class="{'active': myGoodsNum}" @click="receiveHandle(1)">{{ t('领取') }}</div>
              </div>
            </div>
          </div>
          <div v-if="inviteLink" class="block-content">
            <div class="block-bottom"></div>
            <div class="block-line left"></div>
            <div class="block-line right"></div>
            <div class="title">{{ t('邀请好友') }}</div>
            <div class="content invite">
              <div class="link-content">
                <div class="txt">{{ inviteLink }}</div>
                <div class="btn" @click="copyHandle">{{ t('复制链接') }}</div>
              </div>
              <!-- <p v-html="t('成功邀请N人，获得N积分', {num: inviteNumber, points: invitePoints})"></p>
              <p v-html="t('每邀请N个好友开店可获得N积分', {num: 1, points: activityInfo.invitePoints})"></p> -->
            </div>
          </div>
          <div dir="ltr" v-if="isLogin" class="block-content">
            <div class="block-bottom"></div>
            <div class="block-line left"></div>
            <div class="block-line right"></div>
            <div class="title">{{ t('我的中奖') }}</div>
            <div class="content record" @scroll="recordScrollHandle($event)">
              <div v-if="recordData.length" class="record-content" ref="recordContent">
                <div v-for="item in recordData" :key="item.id" class="item">
                  <div class="prize"><img :src="item.prizeImage || defaultImg1" alt=""></div>
                  <p>{{ item.prizeName }}</p>
                </div>
                <div v-if="recordLoading" class="loading">
                  <van-loading color="#ffffff" type="spinner" />
                </div>
              </div>
              <div v-else class="no-data">{{ t('暂无中奖记录') }}</div>
            </div>
          </div>
          <div class="block-content bg2">
            <div class="block-bottom"></div>
            <div class="block-line left"></div>
            <div class="block-line right"></div>
            <div class="title">{{ t('活动规则') }}</div>
            <div class="content intro">
              <div v-if="activityInfo.description" v-html="activityInfo.description"></div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup name="ActivityTurntable">
import { ref, nextTick, computed, onUnmounted, watch } from 'vue'
import { useRoute } from 'vue-router'
import { Toast } from 'vant'
import { useI18n } from 'vue-i18n'
import useClipboard from 'vue-clipboard3'
import { getImg, isMobile, formeateUser, numberStrFormat } from '@/utils'
import { arLangCheck } from '@/utils/arLangCheck'
import { useUserStore } from '@/store/user'
import LanguageChange from '@/components/language-change/index.vue'
import { _getIdentify } from '@/service/user.api.js'
import { lotteryInfo, getPoints, lotteryDraw, lotteryCountPrize, receivePrize, getCountPoints, pageListMyPrize, getCurrentActivity } from '@/service/activity.api.js'
import { sellerPromotional } from '@/service/shop.api.js'
import { letters, numbers, emailsSuffix, prizes } from './config'
import LoginDialog from './components/LoginDialog.vue'
import TipsDialog from './components/TipsDialog.vue'

const isMobileRef = isMobile()
const { toClipboard } = useClipboard()

const route = useRoute()
const userStore = useUserStore()
const pageDone = ref(false)
// 用户信息
const userInfo = computed(() => {
  let obj = {
    username: '',
    email: ''
  }
  return { ...obj, ...userStore.userInfo }
})

const showUserName = computed(() => {
  return userInfo.value.username || userInfo.value.email || ''
})

const bgMp3 = computed(() => {
  const mode = import.meta.env.MODE
  return ['argos'].includes(mode) ? getImg('activity/turntable/audio/bg1.mp3') : getImg('activity/turntable/audio/bg.mp3')
})

const isArLang = arLangCheck()
const activityId = ref('')
const defaultImg = getImg('activity/turntable/default-imgs.png')
const defaultImg1 = getImg('activity/turntable/default-imgs1.png')

const isLogin = ref(false)

const { t, locale } = useI18n()

const defaultPlayFlag = ref(false)
const playBg = ref(true)
const bgAudio = ref()
const rollingAudio = ref()
const clickAudio = ref()
const successAudio = ref()
const failAudio = ref()

const noticeData = ref([])

const canvasWidth = ref('')
const canvasHeight = ref('')

const rolling = ref(false)
const lotteryCanvas = ref()
const prizeList = ref([])

// 获取活动详情
const activityInfo = ref({})
const getActivityInfo = async () => {
  Toast.loading({
    duration: 0,
    forbidClick: true
  })

  await lotteryInfo({
    activityId: activityId.value
  }).then(res => {
    showActive.value = true

    let prizeData = res.prizeList || []
    if (prizeData.length > 9) {
      prizeData = prizeData.slice(0, 9)
    }
    prizeList.value = prizeData
    activityInfo.value = res
    
    if (prizeList.value.length) {
      for (let i = 0; i < prizeList.value.length; i++) {
        prizes.value[i].id = prizeList.value[i].id
        prizes.value[i].prizeName = prizeList.value[i].prizeName
        prizes.value[i].fonts[0].text = prizeList.value[i].prizeName
        prizes.value[i].imgs.push({
          src: prizeList.value[i].image || (Number(prizeList.value[i].prizeType) === 3 ? defaultImg : defaultImg1),
          width: '34%',
          top: '20%'
        })
      }
    }
    createRecordList()
    nextTick(() => {
      pageDone.value = true
      Toast.clear()
    })
  }).catch(() => {
    showActive.value = false
  })
}

// 生成中奖记录
const createRecordList = () => {
  const arr = []
  for (let i = 0; i < 50; i++) {
    const isEmail = Math.random() < 0.5
    let userName = ''
    if (isEmail) {
      let lTxt = ''
      let rTxt = ''
      const lCount = Math.floor(Math.random() * 4)
      const rCount = Math.floor(Math.random() * 5)
      const randomInteger = Math.floor(Math.random() * emailsSuffix.length)
      const suffix = '@' + emailsSuffix[randomInteger]
      for (let i = 0; i < lCount; i++) {
        const index = Math.floor(Math.random() * letters.length)
        lTxt += letters[index]
      }
      for (let i = 0; i < rCount; i++) {
        const index = Math.floor(Math.random() * numbers.length)
        rTxt += numbers[index]
      }
      userName = `${lTxt}**${rTxt}${suffix}`
    } else {
      let rTxt = ''
      for (let i = 0; i < 4; i++) {
        const index = Math.floor(Math.random() * numbers.length)
        rTxt += numbers[index]
      }
      userName = `**${rTxt}`
    }
    const prizeName = createPrizeTxt()
    arr.push(`${userName} ${t('抽中了')} ${prizeName}`)
  }
  noticeData.value = arr
}

// 生成中奖礼品
const createPrizeTxt = () => {
  const list = prizeList.value.filter(item => Number(item.prizeType) !== 3)
  const proArr = [...new Set(list.map(item => item.odds))].sort((a, b) => a -b)
  const sum = proArr.reduce((sum, item) => sum + item, 0)
  const prizeNum = Math.random() * sum
  const index = getPrizeIndex(prizeNum, proArr)
  const winArr = prizeList.value.filter(item => item.odds === proArr[index])
  const winIndex = Math.floor(Math.random() * winArr.length)
  return winArr[winIndex].prizeName
}

// 找到中奖的下标
const getPrizeIndex = (num, arr) => {
  for (let i = 0; i < arr.length; i++) {
    if (num < arr[i]) {
      return i
    }
  }
  return arr.length - 1
}

// 播放背景音乐
const playBgHandle = () => {
  playBg.value = !playBg.value
  if (!playBg.value) {
    bgAudio.value.pause()
  } else {
    bgAudio.value.play()
  }
}

const showLogin = ref(false)
const showTips = ref(false)
const tipsTitle = ref('')
const tipsInfo = ref('')
const shakeAgain = ref(false)

// 活动状态判断
const checkStatus = (flag = false) => {
  if (isLogin.value) {
    // 活动未开启
    if (!activityInfo.value.state) {
      tipsTitle.value = ''
      tipsInfo.value = t('活动未开启')
      showTips.value = true
      return false
    }

    // 活动时间
    const nowTime = new Date().getTime()
    const startTime = new Date(activityInfo.value.startTime).getTime()
    const endTime = new Date(activityInfo.value.endTime).getTime()

    // 活动未开始
    if (startTime > nowTime) {
      tipsTitle.value = t('活动开始时间')
      tipsInfo.value = activityInfo.value.startTime
      showTips.value = true
      return false
    }

    if (!flag) {
      // 活动已结束
      if (endTime < nowTime) {
        tipsTitle.value = t('本次活动已结束')
        tipsInfo.value = t('欢迎下次再来！')
        showTips.value = true
        return false
      }

      // 积分不足
      if (Number(pointsRef.value) < Number(activityInfo.value.pointsToNumber)) {
        tipsTitle.value = ""
        tipsInfo.value = t('积分不足')
        showTips.value = true
        return false
      }
    }

    return true
  } else {
    if (pageDone.value) {
      showLogin.value = true
    } else {
      Toast(t('请稍后重试'))
    }
    return false
  }
}

const rowTurn = ref(false)
const turnTimes = ref(0)
const turnHandle = async (flag) => {
  clickPlay()
  if (checkStatus()) {
    if (!sellerIdentify.value) {
      Toast(t('未认证商家'))
      return
    }
    
    rowTurn.value = flag
    if (flag) {
      // 抽十次
      if (Number(pointsRef.value) < Number(activityInfo.value.pointsToNumber) * 5) {
        tipsTitle.value = ""
        tipsInfo.value = t('积分不足')
        showTips.value = true
      } else {
        // turnTimes.value = 10
        turnFn(true)
      }
    } else {
      turnFn(false)
    }
  }
}

// 获取中间下标
const getDrawPrizeIndex = (id) => {
  if (id) {
    return prizeList.value.findIndex(item => item.id === id)
  } else {
    return prizeList.value.findIndex(item => Number(item.prizeType) === 3)
  }
}

// 摇奖方法
const rodActive = ref(false)
const timesResData = ref([])
const turnFn = async (flag) => {
  if (!rodActive.value) {
    shakeAgain.value = false
    timesResData.value = []
    // 摇奖动画
    rodActive.value = true
    lotteryCanvas.value.play()
    rollingAudio.value.play()
    rolling.value = true
    await lotteryDraw({
      drawTimes: flag ? 5 : 1,
      activityId: activityId.value
    }).then(res => {
      let resId = null
      if (res) {
        const seNum = flag ?(Number(activityInfo.value.pointsToNumber) * 5) : Number(activityInfo.value.pointsToNumber)
        pointsRef.value = Number(pointsRef.value) - seNum
        if (flag) {
          const thanksId = prizeList.value.find(item => Number(item.prizeType) === 3).id
          timesResData.value = res
          const timesObj = res.find(item => item.id !== thanksId)
          resId = timesObj ? timesObj.id : thanksId
        } else {
          resId = res[0].id
        }
        // if (turnTimes.value) {
        //   turnTimes.value -= 1
        // }
      } else {
        Toast(t('系统错误，请稍后重试'))
      }
      
      lotteryCanvas.value.stop(getDrawPrizeIndex(resId))
    }).catch((err) => {
      lotteryCanvas.value.stop(getDrawPrizeIndex())
      if (err === 'login') {
        window.location.reload()
      }
    })
  }
}

const endCallback = (prize) => {
  const prizeItem = prizeList.value.find(item => item.id === prize.id)
  rollingAudio.value.pause()
  rollingAudio.value.currentTime = 0
  rolling.value = false
  rodActive.value = false

  getPriceCountInfo(true)

  if (timesResData.value.length) {
    if (Number(prizeItem.prizeType) === 3) {
      failAudio.value.play()
    } else {
      successAudio.value.play()
    }
    const thanksId = prizeList.value.find(item => Number(item.prizeType) === 3).id
    const winArr = timesResData.value.filter(item => item.id !== thanksId)
    for (let i = 0; i < winArr.length; i++) {
      let timesPrizeItem = prizeList.value.find(item => item.id === winArr[i].id)
      noticeData.value.push(`${formeateUser(showUserName.value, false)} ${t('抽中了')} ${timesPrizeItem.prizeName}`)

      const recordItem = {
        ...timesPrizeItem,
        prizeImage: timesPrizeItem.image,
        id: new Date().getTime()
      }
      recordData.value.unshift(recordItem)
    }
    tipsTitle.value = winArr.length ? t('恭喜您，中奖了！') : t('很遗憾，此次未能中奖')
    tipsInfo.value = timesResData.value.map(item => item.prizeName).join('\n')
    showTips.value = true
  } else {
    shakeAgain.value = Number(pointsRef.value) > Number(activityInfo.value.pointsToNumber) && !rowTurn.value && !turnTimes.value
  
    if (Number(prizeItem.prizeType) === 3) {
      // 未中奖
      failAudio.value.play()
      tipsTitle.value = t('很遗憾，此次未能中奖')
      tipsInfo.value = prizeItem.prizeName
      showTips.value = true
    } else {
      // 中奖
      successAudio.value.play()
      tipsTitle.value = t('恭喜您，中奖了！')
      tipsInfo.value = prizeItem.prizeName
      showTips.value = true
      noticeData.value.push(`${formeateUser(showUserName.value, false)} ${t('抽中了')} ${prizeItem.prizeName}`)

      const recordItem = {
        ...prizeItem,
        prizeImage: prizeItem.image,
        id: new Date().getTime()
      }
      recordData.value.unshift(recordItem)
    }
  }
}

const defaultPlay = () => {
  if (!defaultPlayFlag.value && showActive.value) {
    bgAudio.value.play()
    playBg.value = true
    defaultPlayFlag.value = true
  }
}

const defaultConfig = ref({
  gutter: 20,
  speed: 20,
  // accelerationTime: 1000,
  // decelerationTime: 1000
})

const defaultStyle = ref({
  borderRadius: 0,
  lineClamp: 1
})

const activeStyle = ref({
  background: 'rgba(0,0,0,0)'
})

const oneTouch = ref(false)
const twoTouch = ref(false)
const btnTouchStart = (flag) => {
  flag ? oneTouch.value = true : twoTouch.value = true
}

const btnTouchEnd = (flag) => {
  flag ? oneTouch.value = false : twoTouch.value = false
}

// 查询用户积分
const pointsRef = ref(0)
const getPointsHandle = async (flag = false) => {
  if (flag) {
    Toast.loading({
      duration: 0,
      forbidClick: true
    })
  }
  await getPoints({
    activityId: activityId.value
  }).then(res => {
    isLogin.value = true
    pointsRef.value = res || 0
  }).catch(() => {
    console.log('need login')
  })
}

// 获取用户相关信息
const getActivityUserInfo = () => {
  isLogin.value = true
  getIdentifyHandle()
  getPointsHandle(true)
  getPriceCountInfo()
  getRecordList(true)
  getCountPointsHandle()
}

// 获取中奖统计
const myAmount = ref(0)
const myGoodsNum = ref(0)
const getPriceCountInfo = async (flag = false) => {
  if (!flag) {
    Toast.loading({
      duration: 0,
      forbidClick: true
    })
  }
  await lotteryCountPrize({
    activityId: activityId.value
  }).then(res => {
    myAmount.value = res.amount || 0
    myGoodsNum.value = res.goodsNum || 0
  })
}

// 领取奖品
const receiveHandle = (prizeType) => { // 奖品类型， 1-实物、2-彩金
  clickPlay()
  if (checkStatus(true)) {
    if (Number(prizeType) === 1) {
      if (!myGoodsNum.value) {
        Toast(t('暂无奖品'))
        return
      }
    } else {
      if (myAmount.value < Number(activityInfo.value.minPoints)) {
        Toast(`${t('最小领取金额')}≥${activityInfo.value.minPoints}`)
        return
      }
    }

    Toast.loading({
      duration: 0,
      forbidClick: true
    })
    receivePrize({
      activityId: activityId.value,
      prizeType
    }).then(async () => {
      await getPriceCountInfo()
      Toast(t('领取成功'))
    }).catch(() => {
      Toast.clear()
    })
  }
}

// 邀请好友数据
const inviteNumber = ref(0)
const invitePoints = ref(0)
const inviteLink = ref('')
const getCountPointsHandle = () => {
  sellerPromotional().then(res => {
    inviteLink.value = res.download && res.code ? `${res.download}/#?usercode=${res.code}&lang=${locale.value}` : ''
  })
  getCountPoints({
    activityId: activityId.value
  }).then(res => {
    inviteNumber.value = res.number || 0
    invitePoints.value = res.points || 0
  })
}

const copyHandle = async () => {
  clickPlay()
  try {
    await toClipboard(inviteLink.value)
    Toast(t('copySuccess'))
  } catch (e) {
    console.error(e);
  }
}

// 我的中奖记录
const recordContent = ref()
const pageSize = ref(20)
const pageNum = ref(1)
const recordData = ref([])
const hasMore = ref(true)
const recordLoading = ref(false)

const getRecordList = (reload = false) => {
  if (reload) {
    pageNum.value = 1
    hasMore.value = true
    recordData.value = []
  }

  if (hasMore.value && !recordLoading.value) {
    recordLoading.value = true
    pageListMyPrize({
      pageNum: pageNum.value,
      pageSize: pageSize.value,
      activityId: activityId.value
    }).then(res => {
      pageNum.value += 1
      hasMore.value = !res.pageInfo.lastPage
      recordData.value = [...recordData.value, ...res.pageList]
      recordLoading.value = false
    }).catch(() => {
      recordLoading.value = false
    })
  }
}

const recordScrollHandle = (e) => {
  const el = e.target
  const isRight = Math.ceil(el.scrollLeft + el.clientWidth) >= el.scrollWidth - 50
  if (isRight) {
    getRecordList()
  }
}

const lotteryGetIdHandle = async () => {
  Toast.loading({
    duration: 0,
    forbidClick: true
  })
  await getCurrentActivity().then(res => {
    if (res.id) {
      activityId.value = res.id
    } else {
      Toast(t('活动未开始'))
    }
  })
}

const sellerIdentify = ref(false)
const getIdentifyHandle = () => {
  _getIdentify().then(res => {
    sellerIdentify.value = Number(res.status) === 2
  })
}

onUnmounted(() => {
  document.removeEventListener('click', defaultPlay)
})

const showActive = ref(false)
nextTick(async () => {
  // 系统点击默认触发一次声音播放
  document.addEventListener('click', defaultPlay, false)

  document.addEventListener('langChange', async () => {
    await getActivityInfo()
    getRecordList(true)
    nextTick(() => {
      lotteryCanvas.value.init()
    })
  })

  if (isMobileRef) {
    canvasWidth.value = '60vw'
    canvasHeight.value = '56vw'
    defaultConfig.value.gutter = 5
    defaultConfig.value.speed = 50
    prizes.value.forEach(item => {
      if (item.fonts) {
        item.fonts.forEach(_item => {
          _item.fontSize = '2.4vw'
        })
      }
    })
  } else {
    canvasWidth.value = '690px'
    canvasHeight.value = '630px'
    defaultConfig.value.gutter = 20
    defaultConfig.value.speed = 20
  }
  bgAudio.value.volume = 0.25

  const { lang, token, id } = route.query
  if (lang) {
    locale.value = lang
    localStorage.setItem('lang', lang)
  }

  if (token) {
    Toast.loading({duration: 0})
    await userStore.getUserInfo(true, token)
  }
  if (!id) {
    Toast(t('暂无活动'))
  } else {
    activityId.value = id
    // await lotteryGetIdHandle()
    if (activityId.value) {
      await getActivityInfo()
      if (pageDone.value) {
        await getPointsHandle(true)
        if (isLogin.value) {
          getIdentifyHandle()
          getPriceCountInfo()
          getCountPointsHandle()
          getRecordList(true)
        }
      }
    }
  }
})

const clickPlay = () => {
  clickAudio.value.play()
}
</script>

<style lang="scss" scoped>
@import './turntable.scss';
</style>
