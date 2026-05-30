<template>
  <div>
    <fx-header :fixed="true">
      <template #title>
        {{ t('basicInfo') }}
      </template>
    </fx-header>
    <div style="height: 46px;"/>

    <div class="form-content" :class="{'is-ar': isArLang}">
      <div class="item avatar">
        <p>{{ t('storeLogo') }}</p>
        <div class="info">
          <div class="avatar-img" :class="{'is-ar': isArLang}">
            <input
                ref="uploadInput"
                type="file"
                accept="image/jpg, image/jpeg, image/png, image/gif"
                @change="selectFile"
            />
            <img v-if="result.dataURL" :src="result.dataURL" alt=""/>
            <img v-else :src="storeInfo?.avatar || avatarDefault.href" alt=""/>
          </div>
          <van-icon name="arrow" color="#999" size="12"/>
        </div>
      </div>
      <div class="item">
        <van-field v-model="storeForm.name" type="text" :label="t('storeName')" :label-width="120"
                  :placeholder="t('pleaseEnter') + t('storeName')"/>
      </div>
      <div class="item">
        <van-field v-model="storeForm.contact" type="text" :label="t('contactPerson')" :label-width="120"
                  :placeholder="t('pleaseEnter') + t('contactPerson')"/>
      </div>
      <div class="item">
        <van-field v-model="storeForm.shopPhone" type="number" :label="t('storePhone')" :label-width="120"
                  :placeholder="t('pleaseEnter') + t('storePhone')"/>
      </div>
      <div class="item">
        <van-field v-model="storeForm.shopAddress" type="text" :label="t('storeAddress')" :label-width="120"
                  :placeholder="t('pleaseEnter') + t('storeAddress')"/>
      </div>
    </div>

    <div class="remark-content" :class="{'is-ar': isArLang}">
      <p>{{ t('storeProfile') }}</p>
      <van-field
          v-model="storeForm.shopRemark"
          rows="4"
          autosize
          type="textarea"
          :label-width="0"
          label=""
          :placeholder="t('pleaseEnter') + t('storeProfile')"
      />
    </div>
    <div class="form-content" :class="{'is-ar': isArLang}">
      <div class="item">
        <van-field v-model="storeForm.imInitMessage" type="text" :label="t('进店欢迎语')" :label-width="120"
                  :placeholder="t('pleaseEnter') + t('进店欢迎语')"/>
      </div>
    </div>

    <div v-if="isShowModal" class="croper-content-modal">
      <van-nav-bar
          :title="t('selectPhotos')"
          :right-text="t('sure')"
          left-arrow
          fixed
          @click-left="croperBack"
          @click-right="getResult"
      />
      <VuePictureCropper
          :boxStyle="{
          width: '100%',
          height: '100%',
          backgroundColor: '#f8f8f8',
          margin: 'auto',
        }"
          :img="pic"
          :options="{
          viewMode: 1,
          dragMode: 'crop',
          aspectRatio: 1,
        }"
      />
    </div>

    <div class="submit-btn">
      <van-button :loading="submitLoading" type="primary" size="large" :disabled="!showBtn" @click="submitHandle">
        {{ showBtn ? t('save') : t('商家入驻尚未完成') }}
      </van-button>
    </div>

  </div>
</template>

<script>
import {defineComponent, reactive, ref, computed} from 'vue'
import {useI18n} from 'vue-i18n'
import {Toast} from 'vant'
import VuePictureCropper, {cropper} from 'vue-picture-cropper'
import { arLangCheck } from '@/utils/arLangCheck'

import {
  sellerInfo,
  sellerUpdate
} from '@/service/shop.api.js'

import {
  uploadimgExecute
} from '@/service/upload.api.js'

export default defineComponent({
  name: 'ShopBasicInfo',
  components: {
    VuePictureCropper,
  },
  setup() {
    const {t} = useI18n()
    const storeInfo = ref({})
    const showBtn = ref(localStorage.getItem('sellerId') || '')
    const storeForm = reactive({
      name: '',
      contact: '',
      shopPhone: '',
      shopAddress: '',
      shopRemark: '',
      imInitMessage: ''
    })
    const avatarDefault = new URL('@/assets/image/shop/head_default.png', import.meta.url)


    const isArLang = arLangCheck()

    Toast.loading({
      duration: 0,
      message: t('loading'),
      forbidClick: true
    })

    sellerInfo().then(res => {
      storeInfo.value = res
      storeForm.name = res.name
      storeForm.contact = res.contact
      storeForm.shopPhone = res.shopPhone
      storeForm.shopAddress = res.shopAddress
      storeForm.shopRemark = res.shopRemark
      storeForm.imInitMessage = res.imInitMessage
      Toast.clear()
    }).catch(() => {
      Toast.clear()
    })

    const submitLoading = ref(false)
    const submitHandle = async () => {
      const params = {
        ...storeForm
      }

      if (!result.file && !storeInfo.value.avatar) {
        Toast(`${t('请设置')}${t('storeLogo')}`)
        return
      }

      if (!params.name) {
        Toast(`${t('请设置')}${t('storeName')}`)
        return
      }

      if (params.shopPhone) {
        const reg = /^\d{3,}$/
        if (!reg.test(params.shopPhone)) {
          Toast(t('电话格式有误'))
          return false
        }
      }

      submitLoading.value = true

      let imgData = ''

      if (result.file) {
        try {
          imgData = await uploadimgExecute({file: result.file, moduleName: 'shopAvatar'})
        } catch (err) {
          console.log(err)
          submitLoading.value = false
          return false
        }
      }

      if (imgData) {
        params.avatar = imgData
      }

      submitLoading.value = true
      sellerUpdate(params).then(() => {
        submitLoading.value = false
        document.dispatchEvent(new CustomEvent('headerRefresh'))
        Toast.success(t('saveSuc'))
      }).catch(() => {
        submitLoading.value = false
      })
    }

    const isShowModal = ref(false)
    const uploadInput = ref(null)
    const pic = ref('')
    const result = reactive({
      dataURL: '',
      blobURL: '',
      file: ''
    })

    function selectFile(e) {
      pic.value = ''
      result.dataURL = ''
      result.blobURL = ''
      result.file = ''
      const {files} = e.target
      if (!files || !files.length) return
      const file = files[0]
      const reader = new FileReader()
      reader.readAsDataURL(file)
      reader.onload = () => {
        pic.value = String(reader.result)
        isShowModal.value = true
        if (!uploadInput.value) return
        uploadInput.value.value = ''
      }
    }

    /**
     * Get cropping results
     */
    async function getResult() {
      if (!cropper) return
      const base64 = cropper.getDataURL()
      const blob = await cropper.getBlob()
      if (!blob) return
      const file = await cropper.getFile()
      // console.log({ base64, blob, file })
      result.dataURL = base64
      result.blobURL = URL.createObjectURL(blob)
      result.file = file
      isShowModal.value = false
    }

    const croperBack = () => {
      if (!cropper) return
      cropper.clear()
      cropper.reset()
      isShowModal.value = false
    }

    return {
      isArLang,
      avatarDefault,
      storeInfo,
      storeForm,
      submitLoading,
      showBtn,
      t,
      submitHandle,
      // Data
      uploadInput,
      pic,
      result,
      isShowModal,
      // Methods
      selectFile,
      getResult,
      croperBack
    }
  }
})
</script>

<style lang="scss" scoped>
.form-content {
  &.is-ar {
    :deep(.van-field__label) {
      margin-right: 0;
      margin-left: 12px;
      text-align: right;
    }
    :deep(.van-field__control) {
      text-align: right;
    }
  }
  > .item {
    background-color: #fff;
    border-bottom: 1px solid #EFF2F6;

    &:last-child {
      border-bottom: none;
    }

    &.avatar {
      display: flex;
      align-items: center;
      justify-content: space-between;
      padding: 16px;

      > .info {
        display: flex;
        align-items: center;

        > .avatar-img {
          width: 48px;
          height: 48px;
          border-radius: 50%;
          overflow: hidden;
          margin-right: 10px;
          position: relative;
          &.is-ar {
            margin-left: 10px;
            margin-right: 0;
          }

          > input {
            width: 100%;
            height: 100%;
            position: absolute;
            top: 0;
            left: 0;
            z-index: 2;
            opacity: 0;
          }
        }
      }
    }

    :deep(.van-field__label) {
      color: #000;
    }
  }
}

.remark-content {
  width: 100%;
  background-color: #fff;
  margin: 10px 0;
  &.is-ar {
    :deep(.van-field__control) {
      text-align: right;
    }
  }
  > p {
    font-size: 14px;
    color: #000;
    padding: 16px 16px 0 16px;
  }
}

.submit-btn {
  width: 100%;
  padding: 16px;
  margin-top: 30px;

  :deep(.van-button--primary) {
    background-color: var(--site-main-color);;
    border-color: var(--site-main-color);;
    border-radius: 4px;
  }
}

.croper-content-modal {
  width: 100vw;
  height: 100vh;
  position: fixed;
  top: 0;
  left: 0;
  z-index: 99;

  :deep(.van-nav-bar .van-icon) {
    font-size: 18px;
    color: #1F2025;
  }
}
</style>
