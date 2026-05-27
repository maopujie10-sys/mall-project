<template>
    <div :class="{'active': showPop}" class="notic-pop-container">
      <div class="content">
        <div class="content-info">
          <div class="title"><div>{{ t('初次见面') }}</div></div>
          <h2>{{ t('新人专属奖励') }}</h2>
          <div class="content">
            <img :src="images.img1" class="img1" alt="">
            <img :src="images.img2" class="img2" alt="">
            <div class="txt-content">
              <div class="intro-content">
                <div class="money">$<span>1000.00</span></div>
                <p>{{ t('激活礼金需充值，还差可激活', {m1: signBonus, m2: needRecharge}) }}</p>
              </div>
            </div>
          </div>
          <van-button class="btn" block @click="openPage('/recharge')">{{ t('去激活') }}</van-button>
        </div>
        <div class="close" @click="closeHandle"><img :src="images.close" alt=""></div>
      </div>
      <div class="bg"></div>
    </div>
  </template>
  
  <script setup>
  import { ref, nextTick } from 'vue'
  import { useI18n } from 'vue-i18n'
  import { _getBalance } from "@/service/user.api.js";
  import { openPage, numberStrFormat } from '@/utils'

  const { t } = useI18n()

  const images = {
    img1: new URL('@/assets/image/shop/money_img1.png', import.meta.url),
    img2: new URL('@/assets/image/shop/money_img2.png', import.meta.url),
    close: new URL('@/assets/image/shop/close.png', import.meta.url)
  }

  const showPop = ref(false)
  const signBonus = ref('')
  const needRecharge = ref('')

  const closeHandle = () => {
    showPop.value = false
  }

  const getSignBonusInfo = () => {
    _getBalance().then(res => {
      if (res.signBonus && Number(res.rechargeAmount) < Number(res.signBonus * res.sellerSignBonusRatio)) {
        showPop.value = true
        signBonus.value = numberStrFormat(res.signBonus * res.sellerSignBonusRatio)
        needRecharge.value = numberStrFormat((res.signBonus * res.sellerSignBonusRatio) - res.rechargeAmount)
      } else {
        showPop.value = false
      }
    })
  }

  nextTick(() => {
    getSignBonusInfo()
  })

  defineExpose({
    getSignBonusInfo
  })
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
          padding: 20px 15px;
          > .title {
            width: 100%;
            display: flex;
            justify-content: center;
            align-items: center;
            > div {
              position: relative;
              font-size: 16px;
              color: #999;
              &::before,
              &::after {
                content: '';
                display: block;
                width: 40px;
                height: 1px;
                position: absolute;
                top: 50%;
                transform: translateY(-50%);
              }
              &::before {
                background: linear-gradient(270deg, #DDDDDD 0%, rgba(221, 221, 221, 0) 92.16%);
                left: -55px;
              }
              &::after {
                background: linear-gradient(89.99deg, #DDDDDD 0%, rgba(221, 221, 221, 0) 93.13%);
                right: -55px;
              }
            }
          }
          > h2 {
            color: #000;
            font-size: 24px;
            font-weight: bold;
            text-align: center;
            padding: 15px 20px;
          }
          > .content {
            padding: 10px;
            background-color: rgba(21, 82, 240, 1);
            border-radius: 6px;
            position: relative;
            > img {
              position: absolute;
              height: auto;
              &.img1 {
                right: -20px;
                top: -15px;
                width: 62px;
                transform: rotate(5deg);
              }
              &.img2 {
                width: 42px;
                left: -10px;
                bottom: -10px;
              }
            }
            > .txt-content {
              background: linear-gradient(180deg, #FFFFFF 0%, #CEDCFF 100%);
              padding: 5px;
              border-radius: 6px;
              > .intro-content {
                padding: 5px 10px;
                border-radius: 4px;
                border: 1px solid rgba(236, 239, 244, 1);
                display: flex;
                flex-direction: column;
                align-items: center;
                justify-content: center;
                > .money {
                  font-size: 14px;
                  font-weight: bold;
                  display: flex;
                  justify-content: center;
                  color: rgba(21, 82, 240, 1);
                  padding: 5px 0;
                  > span {
                    font-size: 26px;
                    padding: 0 2px;
                  }
                }
                > p {
                  text-align: center;
                  font-size: 12px;
                  font-weight: bold;
                  color: rgba(51, 51, 51, 1);
                  margin-top: 5px;
                }
              }
            }
          }
          > .btn {
            background-color: var(--site-main-color);
            border-color: var(--site-main-color);
            color: #fff;
            margin-top: 20px;
            border-radius: 4px;
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
  