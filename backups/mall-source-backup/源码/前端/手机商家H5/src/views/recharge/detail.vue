<template>
  <div>
    <fx-header fixed>
      <template #title>
        <div>{{ t('recharge') }}</div>
      </template>
      <template #right>
        <div @click="handleRecord">{{ t('rechargeRecord') }}</div>
      </template>
    </fx-header>

    <div v-if="currentType && currentType !== 'bank'" class="rechargeDetail">
      <ExRadioGroup
          :list="list"
          :label="t('blockchainNetwork')"
          v-model="channel"
      />

      <img v-if="qrCodeImgSrc" class="qrCode" :src="qrCodeImgSrc" alt=""/>

      <div class="download">
        <van-button type="default" @click="handleDownload"
        >{{ t('saveQrCode') }}
        </van-button>
      </div>

      <ExInput
          :label="t('rechargeAddress')"
          v-model="from"
          :clear-btn="false"
          readonly
          typeText="text"
      >
        <template #rightBtn>
          <div class="rechargeDetail-all" :class="{'is-ar': isArLang}" @click="handleCopy">
            {{ t('copy') }}
          </div>
        </template>
      </ExInput>

      <ExInput
          :label="t('rechargeAmount')"
          :placeholderText="t('rechargeAmountTips')"
          v-model="amount"
          typeText="number"
      >
      </ExInput>

      <ExInput
          :label="t('expectedAmount', { ratio: computedFee })"
          v-model="realWithdrawAmount"
          :maxLength="18"
          :clearBtn="false"
          readonly
          typeText="number"
      >
        <template #rightBtn>
          <div class="rechargeDetail-unit">{{ 'USDT' }}</div>
        </template>
      </ExInput>

      <div class="my-uploader">
        <div>{{ t('uploadPaymentImage') }}</div>
        <van-uploader
            v-model="fileList"
            :max-size="10000 * 1024"
            @oversize="onOversize"
            :after-read="afterRead"
            :max-count="1"
        />
      </div>

      <van-button
          class="w-full btn-content"
          type="primary"
          :loading="loading"
          @click="handleRecharge"
      >{{ t('submit') }}
      </van-button>
    </div>

    <div v-if="currentType === 'bank'" class="rechargeDetail bank-input-content">
      <div v-if="!isGcash" class="icon-type-content">
        <div class="mb-2.5 text-xs" style="color: #333;">{{ t('选择币种') }}</div>
        <van-field
            v-model="typeValue"
            readonly
            name="picker"
            :placeholder="t('请选择充值币种')"
            @click="showPicker = true"
        />
        <van-popup v-model:show="showPicker" position="bottom">
          <van-picker
              :columns="typeColumns"
              :cancel-button-text="t('cancel')"
              :confirm-button-text="t('confirm')"
              @confirm="onConfirm"
              @cancel="showPicker = false"
          />
        </van-popup>
      </div>
      <ExInput
          :label="t('充值金额')"
          :placeholderText="t('请输入充值金额')"
          v-model="amount"
          typeText="number"
      >
      </ExInput>
      <div v-if="typeValue && currentTypeObj && !isGcash" class="recharge-limit">{{
          t('充值限额')
        }}：<span>{{ currentTypeObj.min_amount }}</span> ~ <span>{{ currentTypeObj.max_amount }}</span></div>
      <div v-if="isGcash" class="recharge-limit">{{ t('充值限额') }}：<span>{{ gMin }}</span> ~ <span>{{ gMax }}</span>
      </div>

      <van-button
          class="w-full btn-content gap"
          type="primary"
          :loading="loading"
          @click="bankRechargeHandle"
      >{{ t('submit') }}
      </van-button>
    </div>
    <div class="pay-button" v-if="payUrl">
      <div class="pay-button-content">
        <span class="pay-button-title">{{ t('请前往{_$1}继续完成支付', {_$1: route.query.key}) }}</span>
        <div class="pay-button-button" @click="togoPayPage(payUrl)">{{ t('继续支付') }}</div>
      </div>
    </div>
  </div>
</template>

<script setup>
import {computed, onMounted, ref, watch, nextTick} from 'vue'
import QRCode from 'qrcode'
import NP from 'number-precision'
import {Toast} from 'vant'
import {useI18n} from 'vue-i18n'
import {
  exchangeGetBlockChain,
  exchangeGetRechargeApply,
  exchangeSetRechargeToken,
  thirdPartyRecharge,
  thirdPartyRechargeApi,
  thirdPartyRechargePhpApi
} from '@/service/exchange.api'
import {uploadimgExecute} from '@/service/upload.api'
import {downloadFile, openPage} from '@/utils'
import ExRadioGroup from '@/components/ex-radio-group/index.vue'
import ExInput from '@/components/ex-input/index.vue'
import {useRoute, useRouter} from 'vue-router'
import {useUserStore} from '@/store/user'
import useClipboard from 'vue-clipboard3'
import {arLangCheck} from '@/utils/arLangCheck'

const isArLang = arLangCheck()
const userStore = useUserStore()
const router = useRouter()
const route = useRoute()
const {t} = useI18n()

const userBalance = ref(10e8)
const channel = ref('')
const from = ref('')
const safeword = ref('')
const amount = ref('')
const fee = ref('')
const qrCodeImgSrc = ref('')
const payUrl = ref('')
const loading = ref(false)

const list = ref([])
const fileList = ref([])
const uploadImg = ref('')
const {toClipboard} = useClipboard()

const isEmptyParams = (str) => [null, undefined, ''].includes(str)

const getQrCodeImg = async (src) => {
  qrCodeImgSrc.value = await QRCode.toDataURL(src)
}

watch(
    channel,
    (val) => {
      const dataArr = list.value
      const current = dataArr.find((item) => item.blockchain_name === val)
      const address = current?.address ?? ''
      if (address) {
        from.value = address
        fee.value = current?.fee ?? ''
        getQrCodeImg(address)
      }
    },
    {deep: true}
)

/**
 * 获取提现区块
 */
const isGcash = ref(false)
const gMin = ref(50)
const gMax = ref(30000)
const getWithdrawBlockChain = () => {
  const id = route.params.id
  currentType.value = id
  if (id) {
    Toast.loading({duration: 0, forbidClick: true})
    if (id !== 'bank') {
      exchangeGetBlockChain().then((res) => {
        const filterList = res.filter((i) => i.coin === id.toUpperCase())
        const newList = filterList.map((i) => ({
          ...i,
          label: i.blockchain_name,
          value: i.blockchain_name
        }))
        if (newList.length) {
          channel.value = newList[0].value
        }

        list.value = newList ?? []
      })
    } else {
      const {g, key} = route.query
      isGcash.value = Boolean(g)
      if (!g) {
        thirdPartyRecharge().then(res => {
          const obj = res.find(item => item.productType === 'Bank')
          bankData.value = obj.range || []
        })
      } else {
        thirdPartyRecharge().then(res => {
          const obj = res.find(item => item.productType === key)
          if (obj) {
            gMin.value = obj.range[0].min_amount
            gMax.value = obj.range[0].max_amount
          }
        })
      }
    }
  } else {
    Toast(t('参数错误'))
    setTimeout(() => {
      router.back()
    }, 1500)
  }
}

onMounted(async () => {
  // 判断认证状态
  await checkKycStatus()

  // 获取提现区块
  await getWithdrawBlockChain()

  Toast.clear()
})

const checkKycStatus = () => {
  const kycStatus = Number(userStore.userInfo.kyc_status)
  let kycStatusTxt = ''
  switch (kycStatus) {
    case 0:
      kycStatusTxt = '未认证'
      break
    case 1:
      kycStatusTxt = '审核中'
      break
    case 3:
      kycStatusTxt = '审核失败'
      break
  }
  if (kycStatus !== 2) {
    Toast(t(kycStatusTxt))
    setTimeout(() => {
      router.back()
    }, 1500)
  }
}

const realWithdrawAmount = computed(() => {
  const val = amount.value
  const curFee = fee.value ?? 1
  return NP.times(val, curFee)
})

const computedSafeWord = computed(() => {
  const val = safeword.value
  return String(val).length < 6
})

const computedFee = computed(() => {
  const val = fee.value
  return `1:${val}`
})

const handleAll = () => {
  amount.value = userBalance.value
}

const handleRecord = () => {
  router.push({name: 'RechargeRecord'})
}

const handleDownload = () => {
  downloadFile(qrCodeImgSrc.value, 'QRCode')
}

const onOversize = (file) => {
  Toast(t('fileMaxLimit'))
}

const afterRead = (file) => {
  // 文件上传
  file.status = 'uploading'
  file.message = t('uploading')

  uploadimgExecute({
    file: file.file,
    moduleName: 'recharge'
  }).then(data => {
    file.status = 'success'
    file.message = t('uploadSuccess')
    uploadImg.value = data
  }).catch(() => {
    file.message = t('上传失败')
    file.status = 'failed'
  })
}

const handleCopy = async () => {
  try {
    await toClipboard(from.value);
    Toast(t('copySuccess'));
  } catch (e) {
    console.error(e);
  }
}
const session_token = ref('')
const getSessionToken = () => {
  return new Promise((resolve, reject) => {
    exchangeSetRechargeToken({session_token: userStore?.userInfo?.token}).then((res) => {
      session_token.value = res.session_token
      resolve()
    }).catch(() => {
      reject()
    })
  })
}

/**
 * 充值
 */
const handleRecharge = async () => {
  if (isEmptyParams(channel.value)) {
    Toast(t('blockchainNetworkRequire'))
    return
  }

  if (isEmptyParams(amount.value)) {
    Toast(t('rechargeAmountRequire'))
    return
  }

  if (isEmptyParams(uploadImg.value)) {
    Toast(t('uploadPaymentImageRequire'))
    return
  }

  const params = {
    session_token: session_token.value,
    from: '123', // 客户转出地址
    blockchain_name: channel.value,  //充值链名称
    channel_address: from.value, // 通道充值地址
    amount: amount.value, // 充值金额
    img: uploadImg.value, // 已充值的上传图片
    coin: (route.params.id ?? '').toUpperCase(), // 充值币种
    tx: ''// 转账hash
  }
  loading.value = true

  getSessionToken().then(() => {
    exchangeGetRechargeApply(params).then((res) => {
      Toast(t('rechargeApplySuccess'))
      setTimeout(() => {
        handleRecord()
      }, 1500);
    }).finally(() => {
      loading.value = false
    })
  })

}

const currentType = ref('')
const bankData = ref([])
const showPicker = ref(false)
const typeValue = ref('')
const typeColumns = computed(() => {
  return bankData.value.map(item => ({text: item.bank_code, value: item.bank_code}))
})
const currentTypeObj = computed(() => {
  const obj = bankData.value.find(item => item.bank_code === typeValue.value)
  return obj ? obj : null
})

const onConfirm = ({value}) => {
  typeValue.value = value
  showPicker.value = false
}

const togoPayPage = (url) => {
  payUrl.value = ""
  openPage(url, true)
}

const bankRechargeHandle = () => {
  if (!typeValue.value && !isGcash.value) {
    Toast(t('请选择充值币种'))
    return
  }
  if (!amount.value) {
    Toast(t('请输入充值金额'))
    return
  }

  const amountNum = Number(amount.value)
  if (!isNaN(amountNum)) {
    const min_amount = isGcash.value ? gMin.value : currentTypeObj.value.min_amount
    const max_amount = isGcash.value ? gMax.value : currentTypeObj.value.max_amount
    if (amountNum < min_amount) {
      Toast(t('充值金额不得低于最小限额'))
      return
    }
    if (amountNum > max_amount) {
      Toast(t('充值金额不得高于最大限额'))
      return
    }
    const { g } = route.query
    loading.value = true
    getSessionToken().then(async () => {
      const {key} = route.query

      const params = {
        session_token: session_token.value,
        amount: amount.value,
        pageUrl: key === 'gcash' ? null : window.location.href + '/www/#/my'
      }
      let rechargeType = 'PHP_recharge'
      switch (key) {
        case 'GCash pay':
          rechargeType = 'PHP_recharge5'
          break
        case 'gcash':
          rechargeType = 'PHP_recharge'
          break
        case 'GCash2.0':
          rechargeType = 'PHP_recharge2'
          break
        case 'GCash3.0':
          rechargeType = 'PHP_recharge3'
          break
        case 'Maya':
          rechargeType = 'PHP_recharge4'
          break
      }

      const ajaxFn = g ? thirdPartyRechargePhpApi : thirdPartyRechargeApi
      if (!g) {
        params.frenchCurrency = typeValue.value
      }

      await ajaxFn(params, rechargeType).then(res => {
        amount.value = ''
        loading.value = false
        payUrl.value = res
      }).catch(() => {
        loading.value = false
      })
    })
  } else {
    Toast(t('请输入充值金额'))
  }
}

nextTick(() => {
  getSessionToken()
})
</script>

<style scoped lang="scss">
.pay-button {
  .pay-button-content {
    width: 300px;
    height: 180px;
    position: fixed;
    z-index: 99999;
    top: 50%;
    left: 50%;
    background-color: #ffffff;
    transform: translate(-50%, -50%);
    border-radius: 10px;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: 24px;
    text-align: center;

    .pay-button-break {
      width: 24px;
      height: 24px;
      border-radius: 50%;
      background-color: var(--site-main-color);
      color: #fff;
      display: flex;
      align-items: center;
      justify-content: center;
      margin-bottom: 24px;
    }

    .pay-button-title {
      font-size: 16px;
      color: #0c0c0c;
      margin-bottom: 24px;
      text-align: center;
    }

    .pay-button-button {
      height: 40px;
      background-color: var(--site-main-color);
      border-radius: 5px;
      padding: 0 10px;
      color: #fff;
      display: flex;
      align-items: center;
      margin-bottom: 0;
      justify-content: center;

      &.pay-button-break {
        background-color: #ffffff;
        color: var(--site-main-color);
        border: 1px solid var(--site-main-color);
      }
    }
  }

  &::after {
    position: fixed;
    width: 100%;
    height: 100%;
    content: '';
    top: 0;
    left: 0;
    background-color: rgba(0, 0, 0, 0.5);
    z-index: 9999;
  }
}

.rechargeDetail-all.is-ar {
  padding-left: 0;
  padding-right: 6px;
}

.rechargeDetail {
  padding: 25px;
  padding-top: calc(71px);
  min-height: 100vh;
  background-color: $background-color;
  // overflow-y: scroll;

  :deep(.inputCom) {
    .label {
      font-size: 12px;
    }

    input {
      font-size: 14px !important;
    }
  }

  .qrCode {
    width: 160px;
    height: 160px;
    margin: 0 auto;
  }

  .download {
    margin: 10px 0 20px;
    text-align: center;

    :deep(.van-button) {
      border-radius: 4px;
    }
  }

  .my-uploader {
    > div:nth-child(1) {
      font-size: 12px;
    }

    :deep(.van-uploader) {
      margin-top: 10px;
      margin-bottom: 20px;
      border: 1px dashed #ddd;
      border-radius: 4px;

      .van-uploader__upload {
        width: 110px;
        height: 110px;
        background: transparent;
        margin: 0;
      }

      .van-uploader__preview {
        width: 110px;
        height: 110px;
        margin: 0;

        .van-uploader__preview-image {
          width: 100%;
          height: 100%;
        }
      }
    }
  }

  .tips {
    display: flex;
    justify-content: space-between;
    align-items: center;
    font-size: 12px;
    padding-bottom: 10px;

    span:nth-child(1) {
      color: $text-color-light;
    }

    span:nth-child(2) {
      color: $primary-color;
    }
  }

  :deep(.inputBackground) {
    background: transparent;

    input {
      padding-left: 0;
    }
  }

  :deep(.inputBackground.iptbox) {
    border: 1px solid $border-color;
  }

  &-all {
    font-size: 14px;
    color: $primary-color;
    padding-left: 6px;
  }

  &-unit {
    font-size: 14px;
    padding-left: 6px;
  }
}

.popup-content {
  padding: 80px 30px 0;
}

.icon-type-content {
  margin-bottom: 1.25rem;

  :deep(.van-cell) {
    border: 1px solid rgb(238, 238, 238);
    box-sizing: border-box;
    height: 44px;
    border-radius: 4px;
    padding: 0 11px;
    display: flex;
    align-items: center;

    &::after {
      height: 0 !important;
      border-bottom: none !important;
    }

    input::-webkit-input-placeholder {
      color: #868c9a !important;
    }
  }
}

.bank-input-content {
  :deep(.inputCom) {
    padding-bottom: 10px;
  }

  .recharge-limit {
    font-size: 12px;
    text-align: right;

    span {
      color: #1552F0;
    }
  }
}

.btn-content {
  margin-top: 10px;
  background-color: var(--site-main-color);
  border-color: var(--site-main-color);
  &.gap {
    margin-top: 30px;
  }
}
</style>
