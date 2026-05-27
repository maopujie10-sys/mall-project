<template>
  <div class="shop-socail" :class="{'is-ar': isArLang}">
    <fx-header :fixed="true">
      <template #title>
        {{ t('soical') }}
      </template>
    </fx-header>
    <div style="height: 46px;" />

    <div class="form-item">
      <div class="title">Facebook</div>
      <van-field v-model="formData.facebook" label="" :placeholder="t('httpsTips')" />
    </div>
    <div class="form-item">
      <div class="title">Twitter</div>
      <van-field v-model="formData.twitter" label="" :placeholder="t('httpsTips')" />
    </div>
    <div class="form-item">
      <div class="title">Google</div>
      <van-field v-model="formData.google" label="" :placeholder="t('httpsTips')" />
    </div>
    <div class="form-item">
      <div class="title">YouTube</div>
      <van-field v-model="formData.youtube" label="" :placeholder="t('httpsTips')" />
    </div>
    <div class="form-item">
      <div class="title">Instagram</div>
      <van-field v-model="formData.instagram" label="" :placeholder="t('httpsTips')" />
    </div>
    <div class="submit-btn"><van-button :loading="submitLoading" type="primary" size="large" :disabled="!showBtn" @click="submitHandle">{{ showBtn ? t('save') : t('商家入驻尚未完成') }}</van-button></div>
  </div>
</template>

<script>
import { defineComponent, reactive, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { Toast } from 'vant'
import { arLangCheck } from '@/utils/arLangCheck'

import {
  sellerInfo,
  sellerUpdate
} from '@/service/shop.api.js'

export default defineComponent({
  name: 'ShopSocial',
  setup() {
    const { t } = useI18n()
    const showBtn = ref(localStorage.getItem('sellerId') || '')
    const formData = reactive({
      facebook: '',
      instagram: '',
      twitter: '',
      google: '',
      youtube: ''
    })

    const isArLang = arLangCheck()

    Toast.loading({
      duration: 0,
      message: t('loading'),
      forbidClick: true
    })

    sellerInfo().then(res => {
      formData.facebook = res.facebook
      formData.instagram = res.instagram
      formData.twitter = res.twitter
      formData.google = res.google
      formData.youtube = res.youtube
      Toast.clear()
    }).catch(() => {
      Toast.clear()
    })

    const submitLoading = ref(false)
    const submitHandle = () => {
      submitLoading.value = true
      const params = {
        ...formData
      }
      sellerUpdate(params).then(() => {
        submitLoading.value = false
        Toast.success(t('saveSuc'))
      }).catch(() => {
        submitLoading.value = false
      })
    }
    return {
      formData,
      submitLoading,
      showBtn,
      isArLang,
      t,
      submitHandle
    }
  }
})
</script>

<style lang="scss" scoped>
.shop-socail {
  min-height: 100vh;
  background-color: #fff;
  padding: 0 15px 30px 15px;
  &.is-ar {
    :deep(.van-field__control) {
      text-align: right;
    }
  }
  > .form-item {
    margin-top: 20px;
    > .title {
      font-size: 12px;
      color: #333;
      margin-bottom: 3px;
    }
    :deep(.van-cell) {
      border: 1px solid #DDDDDD;
      border-radius: 4px;
    }
  }
  .submit-btn {
    width: 100%;
    margin-top: 40px;
    :deep(.van-button--primary) {
      background-color: var(--site-main-color);;
      border-color: var(--site-main-color);;
      border-radius: 4px;
    }
  }
}
</style>
