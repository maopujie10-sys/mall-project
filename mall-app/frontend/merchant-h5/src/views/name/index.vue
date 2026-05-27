<template>
  <div>
    <fx-header :fixed="true">
      <template #title>
        {{ t('realNameVertify') }}
      </template>
    </fx-header>
    <div style="height: 46px;" />

    <!-- 申请身份认证 -->
    <div v-if="!pageLoading" class="identity pl-15 pr-15 font-12 bg-white" style="padding-bottom: 30px;" >
      <div v-if="kycInfo.showStatus" class="flex justify-between items-center text-sm pt-6" style="color: #000">
        <div>{{t('authVerify')}}</div>
        <div class="flex items-center">
          <img v-if="kycInfo.status === 1" class="w-4 h-4" :class="isArLang ? 'ml-0.5': 'mr-0.5'" :src="KeyWait" alt="">
          <img v-if="kycInfo.status === 2" class="w-4 h-4" :class="isArLang ? 'ml-0.5': 'mr-0.5'" :src="KeySuccess" alt="">
          <img v-if="kycInfo.status === 3" class="w-4 h-4" :class="isArLang ? 'ml-0.5': 'mr-0.5'" :src="KeyFail" alt="">
          <div>{{ t(kycInfo.statusTxt) }}</div>
        </div>
      </div>
      <div v-if="kycInfo.status === 3 && kycInfo.msg" style="margin-top: 10px;">
        <van-notice-bar
          wrapable
          :scrollable="false"
          :text="kycInfo.msg"
        />
      </div>

      <div style="padding-top: 20px;">
        <div class="mb-5">
          <div class="mt-27 mb-13 font-12 textColor form-item-title" :class="{'is-ar': isArLang}">{{ t('nationality') }}</div>
          <country-select v-model="nationality" :disabled="kycInfo.disabled" />
        </div>
        <ExInput :label="t('realName')" :placeholderText="t('entryRealName')" :required="true" v-model="name" :disabled="kycInfo.disabled" :clearBtn="!kycInfo.disabled" />
        <ExInput :label="t('credentPassport')" :placeholderText="t('entryCredentPassport')" :maxLength="40" :required="true" v-model="idnumber" :disabled="kycInfo.disabled" :clearBtn="!kycInfo.disabled" />
        <div v-if="kycInfo.showImg">
          <!-- <div v-if="resultArr.length > 0" class="mb-13 textColor">{{ t('uploadCredentPassport') }}</div>
          <div v-else class="mt-55 mb-13">{{ t('uploadPicCredentPassport') }}</div> -->

          <div class="flex mt-4 mb-6 justify-between">
            <div class="flex-1 flex flex-col text-center justify-center items-center">
              <div class="upload-wrap">
                <van-uploader v-model="frontFile" multiple :max-count="1" :disabled="kycInfo.disabled"
                              :deletable="!kycInfo.disabled" :after-read="(file) => afterRead(file, frontFile, 'idimg_1')" />
              </div>
              <div class="mt-3 font-13 h-5 textColor">{{ t('credentFront') }}</div>
            </div>
            <div class="flex-1 flex flex-col text-center justify-center items-center">
              <div class="upload-wrap">
                <van-uploader v-model="reverseFile" multiple :max-count="1" :disabled="kycInfo.disabled"
                              :deletable="!kycInfo.disabled" :after-read="(file) => afterRead(file, reverseFile, 'idimg_2')" />
              </div>
              <div class="mt-3 font-13 h-5 textColor">{{ t('credentObverse') }}</div>
            </div>
            <div v-if="!hideImg3" class="flex-1 flex flex-col text-center justify-center items-center">
              <div class="upload-wrap">
                <van-uploader v-model="fileList" multiple :max-count="1" :disabled="kycInfo.disabled"
                              :deletable="!kycInfo.disabled" :after-read="(file) => afterRead(file, fileList, 'idimg_3')" />
              </div>
              <div class="mt-3 font-13 h-5 textColor">{{ t('handCredent') }}</div>
            </div>
          </div>
        </div>
        <template v-if="!kycInfo.disabled && kycInfo.showImg">
          <div class="mb-4 textColor">{{ t('photoExample') }}</div>
          <div class="flex items-center justify-between">
            <div class="flex-1 flex justify-center">
              <img src="../../assets/imgs/me/kyc1.png" alt=""
                  class="mb-4"
                  style="width: 6.2175rem; height: 4rem;">
              <!-- <img src="../../assets/imgs/me/kyc-true.png" style="width: 1.1875rem; height: 1.1875rem; margin: 0 auto" alt=""> -->
            </div>
            <div class="flex-1 flex justify-center">
              <img src="../../assets/imgs/me/kyc2.png" alt=""
                  class="mb-4"
                  style="width: 6.2175rem; height: 4rem;">
              <!-- <img src="../../assets/imgs/me/kyc-false.png" style="width: 1.1875rem; height: 1.1875rem; margin: 0 auto" alt=""> -->
            </div>
            <div v-if="!hideImg3" class="flex-1 flex justify-center">
              <img src="../../assets/imgs/me/kyc3.png" alt=""
                  class="mb-4"
                  style="width: 6.2175rem; height: 4rem;">
              <!-- <img src="../../assets/imgs/me/kyc-false.png" style="width: 1.1875rem; height: 1.1875rem; margin: 0 auto" alt=""> -->
            </div>
          </div>
        </template>
        <van-button v-if="!kycInfo.disabled" :loading="submitLoading" class="w-full" style="margin-top: 30px;" type="primary" @click="onSubmit">{{ t('certification') }}
        </van-button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { Uploader, Toast } from 'vant';
import { _applyIdentify, _getIdentify } from '@/service/user.api.js'
import { uploadimgExecute } from '@/service/upload.api'
import CountrySelect from '@/components/country-select/index.vue'
import ExInput from "@/components/ex-input/index.vue";
import { useRouter,useRoute } from "vue-router";
import { ref, reactive, onMounted } from "vue";
import { useI18n } from 'vue-i18n'
import { useUserStore } from '@/store/user';
import { formeateUser } from '@/utils'
import { arLangCheck } from '@/utils/arLangCheck'
import { computed } from 'vue';
const { t } = useI18n()
const router = useRouter()
const route = useRoute();

const isArLang = arLangCheck()
const nationality = ref('') // 国家地区号

const idnumber = ref('')
const name = ref('')
const pageLoading = ref(true)

const frontFile = ref([])
const reverseFile = ref([])
const fileList = ref([])
const curFile = ref('frontFile')
const status = ref(-1) // 0
const imgs = ref([])
// const resultArr = ref(['small-success_' + t('applynoView'), 'identifing_' + t('reviewing'), 'small-success_' + t('passView'), 'icon-close_' + t('noPassView')]) // 0 好像是未提交

const KeyWait = new URL('@/assets/imgs/me/wait1.png', import.meta.url)
const KeySuccess = new URL('@/assets/imgs/me/success1.png', import.meta.url)
const KeyFail = new URL('@/assets/imgs/me/fail1.png', import.meta.url)

const userStore = useUserStore()
const hideImg3 = ref(false)

// 图片上传是否为必填
const imgUploadRequset = computed(() => {
  const mode = import.meta.env.MODE
  return !['tiktokMall'].includes(mode)
})

onMounted(() => {
  const mode = import.meta.env.MODE
  hideImg3.value = ['inchoi', 'hive', 'antMall'].includes(mode)
  fetchInfo()
})

const handleShow = (status) => {
  switch (status) {
    case 1:
      return '审核中'
    case 2:
      return '已认证'
    case 3:
      return '审核失败'
  }
}

const kycInfo = ref({})
const fetchInfo = () => {   // 获取状态
  Toast.loading({
    duration: 0,
    message: t('loading'),
    forbidClick: true
  })
  pageLoading.value = true
  _getIdentify().then(data => {
    const status = Number(data.status)
    data.statusTxt = handleShow(status)
    data.disabled = [1, 2].includes(status)
    data.showStatus = [1, 2, 3].includes(status)
    data.showImg = status !== 2

    if (data.status !== 0) {
      nationality.value = data.nationality || ''
      idnumber.value = (data.idnumber && [1, 2].includes(status)) ? formeateUser(data.idnumber, false) : (data.idnumber || '')
      name.value = (data.name && [1, 2].includes(status)) ? formeateUser(data.name, false) : (data.name || '')
      frontFile.value = data.idimg_1 ? [{ url: data.idimg_1 }] : []
      reverseFile.value = data.idimg_2 ? [{ url: data.idimg_2 }] : []
      fileList.value = data.idimg_3 ? [{ url: data.idimg_3 }] : []
    }
    kycInfo.value = data
    pageLoading.value = false
  }).catch(() => {
    pageLoading.value = false
  })
}

const afterRead = (file, type, moduleName) => { /// 处理文件
  file.status = 'uploading'
  file.message = t('uploading')
  uploadimgExecute({
    file: file.file,
    moduleName
  }).then(data => {
    file.status = 'success'
    file.message = t('uploadSuccess')
    file.resURL = data
    type.value = [file]
  }).catch(() => {
    file.message = t('上传失败')
    file.status = 'failed'
  })
}

const submitLoading = ref(false)

const onSubmit = () => {
  if (!nationality.value) {
    Toast(t('selectNation'))
    return
  }
  if (!name.value) {
    Toast(t('entryName'))
    return
  }
  const reg = /^[\u4e00-\u9fa5a-zA-Z-，,\s]+$/

  if (!reg.test(name.value)) {
    Toast(t('真实姓名格式有误'))
    return
  }
  if (!idnumber.value) {
    Toast(t('entryCredent'))
    return
  }

  // 正则只是判断为数字或者字母
  if (!/^[0-9a-zA-Z]*$/.test(idnumber.value)) {
    Toast(t('证件号格式有误'))
    return
  }

  if (!frontFile.value.length && imgUploadRequset.value) {
    Toast(`${t('请上传')}${t('credentFront')}`)
    return
  }
  if (!reverseFile.value.length && imgUploadRequset.value) {
    Toast(`${t('请上传')}${t('credentObverse')}`)
    return
  }
  if (!fileList.value.length && !hideImg3.value && imgUploadRequset.value) {
    Toast(`${t('请上传')}${t('handCredent')}`)
    return
  }

  const params = {
    name: name.value,
    idnumber: idnumber.value,
    frontFile: frontFile.value,
    reverseFile: reverseFile.value,
    fileList: fileList.value,
    nationality: nationality.value
  }

  submitLoading.value = true

  _applyIdentify(params, hideImg3.value).then(async () => {
    await userStore.getUserInfo(true)
    Toast(t('submitSuccess'))
    submitLoading.value = false
    document.dispatchEvent(new CustomEvent('headerRefresh'))
    setTimeout(() => {
      router.back()
    }, 300);
  }).catch(err => {
    console.log(err)
    submitLoading.value = false
    message = err.message ? err.message : (err || t('上传失败'))
    Toast(message);
  })
}

</script>
<style lang="scss" scoped>
@import "@/views/authentication/components/intl.css";

.identity {
  width: 100%;
  box-sizing: border-box;
}

.upload-wrap {
  width: 110px;
  height: 110px;
  display: flex;
  justify-content: center;
  align-items: center;
}

input {
  font-size: 18px;
}

input:disabled {
  background: #fff;
}

.list-view {
  overflow-y: scroll;
  border-bottom: 1px solid #e5e5e5;
}

.kyc-input {
  width: 100%;
  border: none;
}


.service-text {
  text-decoration: underline;
}

.header {
  display: flex;
  justify-content: space-between;
  padding: 0 13px;
  font-size: 14px;
  height: 50px;
  line-height: 50px;
}

.stepBox {
  padding: 0 15px;
}

.title {
  font-weight: 700;
  font-size: 26px;
  margin-top: 25px;
  margin-bottom: 30px;
}

.city {
  background: #F5F5F5;
}
::v-deep(.van-button--primary) {
  background-color: var(--site-main-color);
  border-color: var(--site-main-color);
}
:deep(.inputBackground) {
  background-color: #fff !important;
  border-radius: 4px;
  border: 1px solid #eee;
}

.form-item-title {
  position: relative;
  padding-left: 10px;
  &.is-ar {
    padding-left: 0;
    padding-right: 10px;
    &::after {
      left: calc(100% - 4px);
    }
  }
  &::after {
    content: '*';
    display: block;
    position: absolute;
    top: 50%;
    transform: translateY(-50%);
    color: red;
    left: 0;
  }
}
</style>
