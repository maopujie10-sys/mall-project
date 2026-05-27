<template>
  <div>
    <fx-header :fixed="true">
      <template #title>
        {{ t('bannerSet') }}
      </template>
    </fx-header>
    <div style="height: 46px;" />

    <div class="banner-content">
      <div v-for="(item, index) in bannerData" :key="item.id" class="item">
        <div class="title">{{ item.name }}</div>
        <div class="img-content">
          <div v-if="item.dataURL" class="close" @click="removeHandle(item)"><van-icon name="cross" /></div>
          <input
            type="file"
            accept="image/jpg, image/jpeg, image/png, image/gif"
            @change="(e) => selectFile(e, index)"
          />
          <img v-if="item.dataURL" :src="item.dataURL" alt="" />
          <div v-else class="default">
            <img :src="bannerImg" alt="" />
            <p>{{ t('addBanner') }}</p>
          </div>
        </div>
      </div>

      <div class="submit-btn"><van-button :loading="submitLoading" type="primary" size="large" :disabled="!showBtn" @click="submitHandle">{{ showBtn ? t('save') : t('商家入驻尚未完成') }}</van-button></div>
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
        :img="cropperImage"
        :options="{
          viewMode: 1,
          dragMode: 'crop',
          aspectRatio: 1920 / 300,
        }"
      />
    </div>
  </div>
</template>

<script>
import { defineComponent, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { Toast } from 'vant'
import VuePictureCropper, { cropper } from 'vue-picture-cropper'

import {
  sellerInfo,
  sellerUpdate
} from '@/service/shop.api.js'

import {
  uploadimgExecute
} from '@/service/upload.api.js'

export default defineComponent({
  name: 'ShopBanner',
  components: {
    VuePictureCropper,
  },
  setup() {
    const { t } = useI18n()
    const showBtn = ref(localStorage.getItem('sellerId') || '')
    const bannerImg = new URL('@/assets/image/shop/bxs_camera-plus.png', import.meta.url)
    const bannerData = ref([{
      name: `${t('storeBanner')} 1(1920X300)`,
      id: 'banner1',
      dataURL: '',
      blobURL: '',
      file: '',
      imgUrl: ''
    }, {
      name: `${t('storeBanner')} 2(1920X300)`,
      id: 'banner2',
      dataURL: '',
      blobURL: '',
      file: '',
      imgUrl: ''
    }, {
      name: `${t('storeBanner')} 3(1920X300)`,
      id: 'banner3',
      dataURL: '',
      blobURL: '',
      file: '',
      imgUrl: ''
    }])

    Toast.loading({
      duration: 0,
      message: t('loading'),
      forbidClick: true
    })

    sellerInfo().then(res => {
      bannerData.value[0].dataURL = res.banner1 || ''
      bannerData.value[1].dataURL = res.banner2 || ''
      bannerData.value[2].dataURL = res.banner3 || ''
      Toast.clear()
    }).catch(() => {
      Toast.clear()
    })

    const isShowModal = ref(false)
    const cropperImage = ref('')
    const currentIndex = ref(null)
    const selectFile = (e, index) => {
      cropperImage.value = ''
      bannerData.value[index].dataURL = ''
      bannerData.value[index].blobURL = ''
      bannerData.value[index].file = ''
      currentIndex.value = index

      const { files } = e.target
      if (!files || !files.length) return
      const file = files[0]
      const reader = new FileReader()
      reader.readAsDataURL(file)
      reader.onload = () => {
        cropperImage.value = String(reader.result)
        isShowModal.value = true
      }
    }

    const getResult = async () => {
      if (!cropper) return
      const base64 = cropper.getDataURL()
      const blob = await cropper.getBlob()
      if (!blob) return
      const file = await cropper.getFile()
      // console.log({ base64, blob, file })

      if (currentIndex.value === null) {
        isShowModal.value = false
        return false
      } else {
        bannerData.value[currentIndex.value].dataURL = base64
        bannerData.value[currentIndex.value].blobURL = URL.createObjectURL(blob)
        bannerData.value[currentIndex.value].file = file
        isShowModal.value = false
      }
    }

    const croperBack = () => {
      if (!cropper) return
      cropper.clear()
      cropper.reset()
      isShowModal.value = false
    }

    const imgUpload = async (data) => {
      for (let i = 0; i < data.length; i++) {
        await uploadimgExecute({file: data[i].file, moduleName: data[i].id}).then(res => {
          const item = bannerData.value.find(item => item.id === data[i].id)
          item.imgUrl = res
        })
      }
    }

    const submitLoading = ref(false)
    const submitHandle = async () => {
      const paramsData = bannerData.value.filter(item => item.file || item.remove)
      if (paramsData.length) {
        const uploadParams = paramsData.filter(item => item.file)
        submitLoading.value = true
        try {
          await imgUpload(uploadParams)
        } catch(err) {
          submitLoading.value = false
          return false
        }
        
        const params = {}
        paramsData.forEach(item => {
          params[item.id] = item.imgUrl
        })
        sellerUpdate(params).then(() => {
          submitLoading.value = false
          bannerData.value.map(item => {
            item.file = ''
            item.imgUrl = ''
            item.remove = false
          })
          Toast.success(t('saveSuc'))
        }).catch(() => {
          submitLoading.value = false
        })
      } else {
        Toast(t('noNeedSub'))
      }
    }

    const removeHandle = (item) => {
      item.dataURL = ''
      item.imgUrl = ''
      item.blobURL = ''
      item.file = ''
      item.remove = true
    }

    return {
      bannerImg,
      bannerData,
      submitLoading,
      isShowModal,
      cropperImage,
      showBtn,
      t,
      selectFile,
      getResult,
      croperBack,
      submitHandle,
      removeHandle
    }
  }
})
</script>

<style lang="scss" scoped>
.banner-content {
  padding: 0 15px 30px 15px;
  > .item {
    margin-top: 20px;
    > .title {
      font-size: 14px;
      color: #000;
    }
    > .img-content {
      margin-top: 10px;
      width: 100%;
      height: calc((300 / 1920) * (100vw - 30px));
      background-color: #fff;
      border: 1px solid #DDDDDD;
      border-radius: 4px;
      overflow: hidden;
      position: relative;
      > .close {
        position: absolute;
        width: 24px;
        height: 24px;
        border-radius: 24px;
        background-color: rgba(0, 0, 0, .5);
        display: flex;
        align-items: center;
        justify-content: center;
        top: 5px;
        right: 5px;
        color: #fff;
        z-index: 3;
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
      > img {
        width: 100%;
        height: 100%;
      }
      > .default {
        width: 100%;
        height: 100%;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        > img {
          width: 26px;
          height: auto;
        }
        > p {
          font-size: 12px;
          line-height: 14px;
          padding-top: 2px;
          color: #aaa;
        }
      }
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
