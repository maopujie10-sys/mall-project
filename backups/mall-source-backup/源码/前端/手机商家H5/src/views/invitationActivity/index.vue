<template>
  <div :style="{'background-image': 'url('+ contentBg.href +')'}" class="invitation-content">
    <fx-header fixed></fx-header>
    <div class="info-title">
      <h2 v-html="t('邀请好友得现金')"></h2>
      <p v-html="t('邀请好友瓜分现金', {money: '100,000'})"></p>
    </div>

    <div class="block-content info">
      <div class="title">
        <div>
          <div><span></span><span></span><span></span></div>
          {{ t('活动规则') }}
          <div><span></span><span></span><span></span></div>
        </div>
      </div>
      <p class="info-txt">{{ t('活动期间，你每成功邀请一个新用户注册并激活店铺都将得到奖金,达到邀请人数之后奖金提升如下：') }}</p>
      <div class="intro-table">
        <div class="item title">
          <div>{{ t('邀请人数') }}</div>
          <div>{{ t('每人奖励') }}</div>
        </div>
        <div v-for="(item, index) in inviteData" :key="index" class="item">
          <div v-if="index < inviteData.length - 1">{{ item[1] }}-{{ Number(inviteData[index + 1][1]) - 1 }}</div>
          <div v-else>≥ {{ item[1] }}</div>
          <div>${{ numberStrFormat(item[0]) }}</div>
        </div>
      </div>
      <p class="info-txt">{{ t('邀请越多，奖励越多，先到先得，数量有限！') }}</p>
      <p class="info-txt one" v-html="t('好友开店首次充值金额满足', {money: validAmount})"></p>
    </div>
    <div class="block-content">
      <div class="title">
        <div>
          <div><span></span><span></span><span></span></div>
          {{ t('我的邀请记录') }}
          <div><span></span><span></span><span></span></div>
        </div>
      </div>
      <div class="record-content">
        <div class="item">
          <h2>{{ inviteNum }}</h2>
          <p>{{ t('成功邀请(人)') }}</p>
        </div>
        <div class="item">
          <h2>{{ numberStrFormat(inviteReceivedReward) }}</h2>
          <p>{{ t('累计返现($)') }}</p>
        </div>
      </div>
      <div class="link-content">
        <div class="txt">{{ inviteLink }}</div>
        <div class="btn" @click="copyHandle">{{ t('复制链接') }}</div>
      </div>
    </div>
  </div>
</template>

<script setup name="InvitationActivity">
import { ref, nextTick } from "vue"
import { useI18n } from "vue-i18n";
import { Toast } from "vant";
import useClipboard from 'vue-clipboard3'
import { numberStrFormat } from '@/utils'
import { getSysparaAction } from '@/service/user.api.js'
import { sellerInfo, sellerPromotional } from '@/service/shop.api.js'

const { t, locale } = useI18n()
const { toClipboard } = useClipboard()

const contentBg = ref(new URL('@/assets/imgs/me/invite-info-bg.png', import.meta.url))

const inviteData = ref([])
const inviteNum = ref(0)
const inviteReceivedReward = ref(0)
const validAmount = ref(0)
const inviteLink = ref('')

const copyHandle = async () => {
  try {
    await toClipboard(inviteLink.value)
    Toast(t('copySuccess'))
  } catch (e) {
    console.error(e);
  }
}

nextTick(() => {
  Toast.loading({
    forbidClick: true,
    duration: 0
  });

  // 活动信息
  getSysparaAction('mall_first_invite_recharge_rewards').then(res => {
    const data = res.mall_first_invite_recharge_rewards ? JSON.parse(res.mall_first_invite_recharge_rewards) : []
    inviteData.value = data
  })

  // 有效充值金额
  getSysparaAction('valid_recharge_amount_for_first_recharge_bonus').then(res => {
    validAmount.value = res.valid_recharge_amount_for_first_recharge_bonus || 0
    console.log('validAmount', validAmount.value)
  })

  // 邀请记录
  sellerInfo().then(res => {
    inviteNum.value = res.inviteNum
    inviteReceivedReward.value = res.inviteReceivedReward
  })

  // 邀请链接
  sellerPromotional().then(res => {
    inviteLink.value = res.download && res.code ? `${res.download}/#?usercode=${res.code}&lang=${locale.value}` : ''
  })
})
</script>

<style lang="scss" scoped>
.invitation-content {
  width: 100%;
  min-height: 100vh;
  background-position: center top;
  background-repeat: no-repeat;
  background-size: cover;
  background-attachment: fixed;
  padding: 0 15px;
  padding-bottom: 20px;
  padding-top: 26vh;
  box-sizing: border-box;
  color: #fff;
  position: relative;
  :deep(.van-nav-bar) {
    background: transparent !important;
    &::after {
      height: 0 !important;
    }
    .van-icon {
      color: #fff !important;
    }
  }
  .info-title {
    width: 100%;
    padding: 0 50px;
    position: absolute;
    top: 16vw;
    left: 0;
    > h2 {
      font-size: 24px;
      :deep(span) {
        color: rgba(255, 223, 111, 1);
      }
    }
    > p {
      padding-top: 10px;
      font-size: rgba(214, 239, 255, 1);
      font-size: 13px;
    }
  }

  .block-content {
    padding: 20px 15px;
    border-radius: 6px;
    background-color: rgba(226, 234, 255, 1);
    margin-bottom: 15px;
    > .title {
      color: rgba(21, 82, 240, 1);
      font-weight: bold;
      font-size: 18px;
      display: flex;
      align-items: center;
      justify-content: center;
      > div {
        position: relative;
        > div {
          height: 12px;
          display: flex;
          flex-direction: column;
          align-items: center;
          justify-content: space-between;
          position: absolute;
          top: 50%;
          transform: translateY(-50%);
          > span {
            display: block;
            height: 2px;
            width: 12px;
            border-radius: 2px;
            background-color: rgba(21, 82, 240, 1);
            &:nth-child(1),
            &:nth-child(3) {
              margin-left: 4px;
            }
          }
          &:first-child {
            left: -30px;
          }
          &:last-child {
            right: -30px;
            > span {
                &:nth-child(1),
                &:nth-child(3) {
                  margin-left: 0;
                  margin-right: 4px;
                }
              }
            }
        }
      }
    }
    > .info-txt {
      font-size: 12px;
      color: rgba(51, 51, 51, 1);
      line-height: 1.5;
      margin-top: 20px;
      &.one {
        margin-top: 5px;
      }
    }
    > .intro-table {
      background-color: rgba(241, 245, 255, 1);
      border-radius: 6px;
      overflow: hidden;
      margin-top: 10px;
      font-size: 13px;
      > .item {
        width: 100%;
        height: 34px;
        display: flex;
        align-items: center;
        color: #000;
        font-weight: bold;
        border-bottom: 1px solid rgba(255, 255, 255, 1);
        &:first-child,
        &:last-child {
          border-bottom: none;
        }
        &.title {
          background-color: rgba(195, 212, 255, 1);
          > div {
            color: #000 !important;
            font-weight: normal;
          }
        }
        > div {
          width: 50%;
          height: 100%;
          display: flex;
          align-items: center;
          justify-content: center;
          &:first-child {
            border-right: 1px solid rgba(255, 255, 255, 1);
          }
          &:last-child {
            color: rgba(21, 82, 240, 1);
          }
        }
      }
    }
    > .record-content {
      width: 100%;
      display: flex;
      align-items: center;
      margin-top: 20px;
      position: relative;
      &::after {
        content: "";
        display: block;
        width: 1px;
        height: 26px;
        background-color: rgba(176, 193, 237, 1);
        position: absolute;
        top: 50%;
        margin-top: -13px;
        left: 50%;
      }
      > .item {
        width: 50%;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        > h2 {
          color: rgba(21, 82, 240, 1);
          font-weight: bold;
          font-size: 24px;
        }
        > p {
          font-size: 12px;
          color: rgba(51, 51, 51, 1);
        }
      }
    }
    > .link-content {
      width: 100%;
      height: 41px;
      background-color: rgba(241, 245, 255, 1);
      border-radius: 6px;
      overflow: hidden;
      margin-top: 10px;
      display: flex;
      align-items: center;
      padding: 0 5px;
      > .txt {
        flex: 1;
        font-size: 12px;
        color: #000;
        line-height: 14px;
        padding: 0 10px;
      }
      > .btn {
        min-width: 83px;
        padding: 0 8px;
        height: 33px;
        border-radius: 6px;
        background-color: rgba(21, 82, 240, 1);
        color: #fff;
        font-size: 14px;
        text-align: center;
        line-height: 33px;
      }
    }
  }
}
</style>
