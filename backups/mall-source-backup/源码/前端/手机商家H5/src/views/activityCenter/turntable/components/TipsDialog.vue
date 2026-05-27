<template>
  <div :class="{'active': modelValue}" class="tips-dialog">
    <div class="tips-content">
      <div class="dialog-title">
        {{ t('提示') }}
      </div>
      <div class="info-content">
        <div class="txt-content">
          <p v-if="tipsTitle">{{ tipsTitle }}</p>
          <h2 v-if="tipsInfo">{{ tipsInfo }}</h2>
        </div>
        <div class="btn">
          <van-button v-if="again" type="custom" block @click="shakeAgainFn">{{ t('再抽一次') }}</van-button>
          <van-button v-else type="custom" block @click="sureHandle">{{ times ? t('确定') : t('知道了') }}</van-button>
          <van-button v-if="again" type="cancel" block @click="closeDialog">{{ t('取消') }}</van-button>
        </div>
      </div>
    </div>
    <div class="tips-bg" @click="bgHandle"></div>
  </div>
</template>

<script setup name="TipsDialog">
import { useI18n } from 'vue-i18n'

const { t } = useI18n()

const props = defineProps({
  modelValue: {
    type: Boolean,
    default: false
  },
  tipsTitle: {
    type: String,
    default: ''
  },
  tipsInfo: {
    type: String,
    default: ''
  },
  again: {
    type: Boolean,
    default: false
  },
  times: {
    type: Number,
    default: 0
  }
})
const emits = defineEmits(['update:modelValue', 'again'])

const closeDialog = () => {
	emits('update:modelValue', false)
}

const sureHandle = () => {
  if (props.times) {
    shakeAgainFn()
  } else {
    closeDialog()
  }
}

const bgHandle = () => {
  if (!props.times) {
    closeDialog()
  }
}

const shakeAgainFn = () => {
  closeDialog()
  emits('again')
}

</script>

<style lang="scss" scoped>
.tips-dialog {
  width: 100%;
  height: 100vh;
  pointer-events: none;
  z-index: 98;
  opacity: 0;
  position: fixed;
  top: 0;
  left: 0;
  > .tips-content {
    width: 540px;
    position: fixed;
    top: 20%;
    left: 50%;
    margin-left: -270px;
    animation-duration: .75s;
    z-index: 99;
    background-image: url('./../../../../assets/activity/turntable/login-bg.png');
    background-repeat: no-repeat;
    background-size: 100% 100%;
    background-position: center top;
    padding: 0 40px;
    padding-top: 20px;
    padding-bottom: 60px;
    display: flex;
    flex-direction: column;
    align-items: center;
    > .dialog-title {
      width: 204px;
      height: 70px;
      background-image: url('./../../../../assets/activity/turntable/login-title.png');
      background-repeat: no-repeat;
      background-size: 100% 100%;
      display: flex;
      align-items: center;
      justify-content: center;
      padding-top: 10px;
      background-position: center top;
      position: relative;
      color: #FFDE6D;
      font-size: 16px;
      top: -45px;
    }
    > .info-content {
      width: 100%;
      > .txt-content {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        min-height: 100px;
        padding-bottom: 20px;
        padding-top: 10px;
        > p {
          color: #fff;
          font-size: 20px;
          padding-bottom: 20px;
          line-height: 1.5;
          text-align: center;
        }
        > h2 {
          color: #EECB88;
          font-size: 28px;
          font-weight: bold;
          line-height: 1.5;
          text-align: center;
          white-space: pre-line;
        }
      }
      > .btn {
        margin-top: 40px;
      }
    }
  }
  > .tips-bg {
    position: fixed;
    left: 0;
    top: 0;
    width: 100%;
    height: 100vh;
    background-color: rgba(0, 0, 0, .4);
    z-index: 98;
    opacity: 0;
    transition: all 0.3s ease;
  }
  &.active {
    pointer-events: auto;
    opacity: 1;
    > .tips-content {
      animation-name: bounceInUp;
    }
    > .tips-bg {
      opacity: 1;
    }
  }
}

.van-button--custom {
  color: #8F6618;
  background: #EECB88;
  border-color: #F2DB9C;
  border-radius: 44px;
}

.van-button--cancel {
  margin-top: 15px;
  color: #8F6618;
  background: #fff;
  border-color: #F2DB9C;
  border-radius: 44px;
}

@media (max-width: 1180px) {
  .tips-dialog {
    > .tips-content {
      width: 80vw;
      margin-left: -40vw;
      padding: 0 20px;
      padding-top: 0;
      padding-bottom: 40px;
      > .dialog-title {
        width: 35vw;
        height: 12vw;
        font-size: 3.2vw;
        padding-top: 1vw;
        top: -5vw;
      }
      > .info-content {
        > .txt-content {
          > p {
            font-size: 14px;
          }
          > h2 {
            font-size: 18px;
          }
        }
        > .btn {
          margin-top: 20px;
        }
      }
    }
  }
}
</style>
