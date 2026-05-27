<template>
  <div>
    <fx-header :fixed="true">
      <template #title>
        {{ t('throughCar') }}
      </template>
      <template #right>
        <p @click="openPage('/shop/marketing/record')">{{ t('shopBuyRecord') }}</p>
      </template>
    </fx-header>
    <div style="height: 46px;" />
    <div v-if="listData.length" class="marketing-content">
      <div v-for="item in listData" :key="item.id" class="item">
        <div class="icon">
          <img :src="item.icon" alt="" />
        </div>
        <div class="info" :class="{'is-ar': isArLang}">
          <h3>{{ item.name }}</h3>
          <p>{{ t('可推广产品数') }}<span>{{ item.count }}</span></p>
          <p>{{ item.desc1 }}</p>
          <div>
            <p v-if="isArLang">${{ numberStrFormat(item.prize) }}<span>/{{ t('days') }}{{ item.per }}</span></p>
            <p v-else>${{ numberStrFormat(item.prize) }}<span>/{{ item.per }}{{ t('days') }}</span></p>
            <van-button v-if="item.count" type="primary" size="small" @click="buyHandle(item)">{{ t('shopBuyNow') }}</van-button>
            <van-button v-else type="default" disabled size="small">{{ t('购买达上限') }}</van-button>
          </div>
        </div>
      </div>
    </div>
    <van-empty v-if="!listData.length && !pageLoading" :image="empytImg.href" :description="t('noData')" />

    <van-action-sheet v-model:show="passwordShow" :title="t('shopSafeTips')">
      <div style="height: 22rem">
        <van-password-input
            :length="6"
            :value="safewordInput"
            :focused="showKeyboard"
            @focus="showKeyboard = true"
        />
        <van-number-keyboard
            v-model="safewordInput"
            :show="showKeyboard"
            @blur="showKeyboard = false"
        />
      </div>
    </van-action-sheet>
  </div>
</template>

<script>
import { defineComponent, nextTick, ref, computed, watch, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { Toast, Dialog } from 'vant'
import { useUserStore } from '@/store/user.js'
import { arLangCheck } from '@/utils/arLangCheck'

import {
  openPage,
  numberStrFormat
} from '@/utils'

import {
  sellerPromotionalView,
  sellerPromotionalBuy
} from '@/service/shop.api.js'

export default defineComponent({
  name: 'ShopMarketing',
  setup() {
    const { t } = useI18n()
    const empytImg = new URL('@/assets/image/public/no_data.png', import.meta.url)
    const listData = ref([])
    const userStore = useUserStore()
    const safewordInput = ref('')
    const currentItem = ref()
    const passwordShow = ref(false)
    const loading = ref(false)
    const pageLoading = ref(true)

    const isArLang = arLangCheck()

    watch(passwordShow, (val) => {
      if (!val) {
        safewordInput.value = ''
      }
    })

    const computedSafeWord = computed(() => {
      const val = safewordInput.value
      return String(val).length < 6
    })

    const buyHandle = (data) => {
      const safeword = Boolean(Number(userStore?.userInfo?.safeword))
      if (safeword) {
        currentItem.value = data
        passwordShow.value = true
        showKeyboard.value = true
      } else {
        Dialog.confirm({
          title: t('dialogTips'),
          message: t('shopSafeWord'),
          cancelButtonText: t('cancel'),
          confirmButtonText: t('gotoSet'),
          confirmButtonColor: '#1552F0',
          cancelButtonColor: '#999'
        }).then(() => {
          openPage('/fundsPasswordSettings')
        }).catch(() => {
          console.log('cancel')
        });
      }
    }

    const buySureHandle = () => {
      Toast.loading({
        duration: 0,
        forbidClick: false
      })
      loading.value = true
      const params = {
        id: currentItem.value.id,
        safeword: safewordInput.value
      }

      sellerPromotionalBuy(params).then(() => {
        Toast.success(t('shopBuySuc'))
        loading.value = false
        passwordShow.value = false
        getListData()
      }).catch(() => {
        loading.value = false
      })
    }

    const getListData = () => {
      sellerPromotionalView().then(res => {
        listData.value = res.line || []
        Toast.clear()
        pageLoading.value = false
      }).catch(() => {
        Toast.clear()
        pageLoading.value = false
      })
    }

    const showKeyboard = ref(true);

    // 密码输入到6位发送请求
      watch(() => safewordInput.value, (val) => {
        if (val.length === 6) {
          buySureHandle()

          passwordShow.value = false;
          safewordInput.value = ''
        }
      })

    nextTick(() => {
      Toast.loading({
        duration: 0,
        message: t('loading'),
        forbidClick: true
      })
      getListData()
    })

    onMounted(() => {
      document.addEventListener('langChange', () => {
        getListData()
      })
    })
    return {
      isArLang,
      listData,
      passwordShow,
      safewordInput,
      computedSafeWord,
      empytImg,
      loading,
      pageLoading,
      t,
      buyHandle,
      buySureHandle,
      numberStrFormat,
      openPage,
      showKeyboard
    }
  }
})
</script>

<style lang="scss" scoped>
.marketing-content {
  padding: 15px;
  > .item {
    padding: 15px;
    background-color: #fff;
    border-radius: 4px;
    margin-bottom: 15px;
    display: flex;
    > .icon {
      width: 48px;
    }
    > .info {
      flex: 1;
      padding-left: 15px;
      &.is-ar {
        padding-left: 0;
        padding-right: 15px;
      }
      > h3 {
        color: #000;
        font-size: 16px;
        font-weight: bold;
      }
      > p {
        font-size: 14px;
        color: #999;
        line-height: 16px;
        margin-top: 2px;
        line-height: 1.2;
        margin-top: 5px;
        > span {
          color: var(--site-main-color);
          font-weight: bold;
          padding-left: 5px;
        }
      }
      > div {
        width: 100%;
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin-top: 10px;
        > p {
          line-height: 1;
          font-size: 18px;
          font-weight: bold;
          color: var(--site-main-color);
          > span {
            font-weight: normal;
            font-size: 12px;
          }
        }
        :deep(.van-button--primary) {
          background-color: var(--site-main-color);
          border-color: var(--site-main-color);
          border-radius: 4px;
          padding: 1px 10px !important;
        }
        :deep(.van-button--disabled) {
          background-color: #666;
          border-color: #666;
          color: #fff;
          border-radius: 4px;
          padding: 1px 10px !important;
        }
      }
    }
  }
}
.popup-content {
  padding: 0 30px 30px 30px;
  > .title {
    padding-top: 15px;
    padding-bottom: 30px;
    text-align: center;
  }
  :deep(.van-button--primary) {
    width: 100%;
    background-color: var(--site-main-color);
    border-color: var(--site-main-color);
    border-radius: 4px;
  }
}
</style>
