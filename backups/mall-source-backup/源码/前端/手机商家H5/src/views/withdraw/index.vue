<template>
  <div>
    <fx-header>
      <template #title>
        <div>{{ t('withdrawal') }}</div>
      </template>
      <template #right>
        <div @click="handleRecord">{{ t('withdrawalRecord') }}</div>
      </template>
    </fx-header>
    <div class="withdraw" :class="{ 'is-ar': isArLang }">
      <div class="icon-type-content">
        <div class="mb-2.5 text-xs required-txt" style="color: #333">
          {{ t('取款方式') }}
        </div>
        <van-field
          v-model="withdrawType"
          readonly
          name="picker"
          @click="typePicker = true"
        />
        <van-popup v-model:show="typePicker" position="bottom">
          <van-picker
            :columns="withdrawTypeData"
            :cancel-button-text="t('cancel')"
            :confirm-button-text="t('confirm')"
            @confirm="typePickerConfirm"
            @cancel="typePicker = false"
          />
        </van-popup>
      </div>

      <div v-if="withdrawTypeVal === 'icon'" class="icon-type-content">
        <div class="mb-2.5 text-xs required-txt" style="color: #333">
          {{ t('选择币种') }}
        </div>
        <van-field
          v-model="typeValue"
          readonly
          name="picker"
          @click="openShowPicker"
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
      <ExRadioGroup
        v-if="withdrawTypeVal === 'icon'"
        :list="list"
        :label="t('blockchainNetwork')"
        :disabled="isBindType"
        v-model="channel"
      />
      <van-form v-if="withdrawTypeVal === 'icon'">
        <div class="mb-2.5 text-xs required-txt" style="color: #333">
          {{ t('withdrawalAddress') }}
        </div>
        <div
          class="mb-5 border border-solid rounded"
          style="border-color: #eeeeee"
        >
          <van-field
            clearable
            v-model="from"
            :disabled="isBindType"
            :placeholder="t('withdrawalAddressTips')"
            :rules="[
              {
                validator,
                message: t('提现地址只能包含数字和字母'),
                trigger: 'onChange'
              }
            ]"
          />
        </div>
      </van-form>
      <van-form v-if="withdrawTypeVal === 'bank' && showBankNational">
        <div class="mb-2.5 text-xs required-txt" style="color: #333">
          {{ t('国家') }}
        </div>
        <div class="mb-5 nationality-select">
          <country-select
            v-model="nationality"
            get-name="true"
            @done="countrySelectDone"
          />
        </div>
      </van-form>
      <van-form v-if="withdrawTypeVal === 'bank'">
        <div class="mb-2.5 text-xs required-txt" style="color: #333">
          {{ t('开户行') }}
        </div>
        <div
          class="mb-5 border border-solid rounded"
          style="border-color: #eeeeee"
        >
          <van-field
            clearable
            v-model="bankName"
            :placeholder="t('请输入开户行名称')"
          />
        </div>
      </van-form>
      <van-form v-if="withdrawTypeVal === 'bank'">
        <div class="mb-2.5 text-xs required-txt" style="color: #333">
          {{ t('姓名') }}
        </div>
        <div
          class="mb-5 border border-solid rounded"
          style="border-color: #eeeeee"
        >
          <van-field
            clearable
            v-model="bankUserName"
            :placeholder="t('entryName')"
          />
        </div>
      </van-form>
      <van-form v-if="withdrawTypeVal === 'bank'">
        <div class="mb-2.5 text-xs required-txt" style="color: #333">
          {{ t('卡号') }}
        </div>
        <div
          class="mb-5 border border-solid rounded"
          style="border-color: #eeeeee"
        >
          <van-field
            clearable
            v-model="bankCardNo"
            :placeholder="t('请输入卡号')"
          />
        </div>
      </van-form>

      <van-form v-if="withdrawTypeVal === 'bank' && showBankMoreInfo">
        <div class="mb-2.5 text-xs" style="color: #333">
          {{ t('国际代码') }}
        </div>
        <div
          class="mb-5 border border-solid rounded"
          style="border-color: #eeeeee"
        >
          <van-field
            clearable
            v-model="swiftCode"
            :placeholder="t('请输入国际代码')"
          />
        </div>
      </van-form>
      <van-form v-if="withdrawTypeVal === 'bank' && showBankMoreInfo">
        <div class="mb-2.5 text-xs" style="color: #333">
          {{ t('路由号码') }}
        </div>
        <div
          class="mb-5 border border-solid rounded"
          style="border-color: #eeeeee"
        >
          <van-field
            clearable
            v-model="routingNum"
            :placeholder="t('请输入路由号码')"
          />
        </div>
      </van-form>
      <van-form v-if="withdrawTypeVal === 'bank' && showBankMoreInfo">
        <div class="mb-2.5 text-xs" style="color: #333">
          {{ t('账户地址') }}
        </div>
        <div
          class="mb-5 border border-solid rounded"
          style="border-color: #eeeeee"
        >
          <van-field
            clearable
            v-model="accountAddress"
            :placeholder="t('请输入账户地址')"
          />
        </div>
      </van-form>
      <van-form v-if="withdrawTypeVal === 'bank' && showBankMoreInfo">
        <div class="mb-2.5 text-xs" style="color: #333">
          {{ t('银行地址') }}
        </div>
        <div
          class="mb-5 border border-solid rounded"
          style="border-color: #eeeeee"
        >
          <van-field
            clearable
            v-model="bankAddress"
            :placeholder="t('请输入银行地址')"
          />
        </div>
      </van-form>

      <ExInput
        :label="t('withdrawalAmount')"
        :placeholderText="t('withdrawalAmountTips')"
        v-model="amount"
        :maxLength="16"
        :disabled="notSub"
        required
        typeText="number"
      >
        <template #rightBtn>
          <div
            class="withdraw-all"
            :class="{ 'is-ar': isArLang }"
            @click="handleAll"
            style="min-width: 40px"
          >
            {{ t('total') }}
          </div>
        </template>
      </ExInput>

      <div
        v-if="
          (balanceAll || balanceAll === 0) &&
          typeValue &&
          withdrawTypeVal === 'icon'
        "
        class="current-balance"
      >
        {{ t('当前余额') }}: <span>{{ numberStrFormat(balanceAll) }}</span
        >USDT ≈ <span>{{ numberStrFormat(balanceTypeAll, balanceFixed) }}</span
        >{{ typeValue }}
      </div>
      <div v-if="withdrawTypeVal !== 'icon'" class="current-balance">
        {{ t('当前余额') }}: <span>{{ numberStrFormat(balanceAll) }}</span
        >USD
      </div>

      <!-- <div class="tips">
        <div>
          <span
            >{{ t('realWithdrawalAccount') }}: {{ realWithdrawAmount
            }}<span>{{
              withdrawTypeVal === 'icon' ? ` ${typeValue}` : ' USD'
            }}</span></span
          >
          <p v-if="typeValue !== 'USDT'" class="money">≈<span>{{ realWithdrawAmountUsdt }}</span>USDT</p>
        </div>
        <span>{{ t('withdrawalFee') }}: {{ withdrawFee }}%</span>
      </div> -->

      <van-button
        class="w-full btn-content"
        type="primary"
        :disabled="notSub"
        @click="withdraw"
        >{{ t('submit') }}
      </van-button>

      <van-action-sheet
        v-model:show="passwordShow"
        :title="t('请输入交易密码')"
      >
        <div style="height: 22rem">
          <van-password-input
            :length="6"
            :value="safeword"
            :focused="showKeyboard"
            @focus="showKeyboard = true"
          />
          <van-number-keyboard
            v-model="safeword"
            :show="showKeyboard"
            @blur="showKeyboard = false"
          />
        </div>
      </van-action-sheet>
    </div>

    <address-bind-dialog
      v-model="showBindDialog"
      :chain-data="blockChainData"
      @bind-done="bindDoneHandle"
    />
  </div>
</template>

<script setup>
import { ref, onMounted, computed, watch } from 'vue'
import NP from 'number-precision'
import { Toast, Dialog } from 'vant'
import { useI18n } from 'vue-i18n'
import {
  exchangeGetWithdrawLimit,
  exchangeGetBlockChain,
  exchangeGetWithdrawFee,
  exchangeSetWithdrawToken,
  exchangeGetWithdrawApply
} from '@/service/exchange.api'
import ExRadioGroup from '@/components/ex-radio-group/index.vue'
import ExInput from '@/components/ex-input/index.vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/store/user'
import { arLangCheck } from '@/utils/arLangCheck'
import { openPage, numberStrFormat } from '@/utils'
import AddressBindDialog from './components/AddressBindDialog.vue'

const userStore = useUserStore()
const router = useRouter()
const { t } = useI18n()

const mode = import.meta.env.MODE

const isArLang = arLangCheck()

const channel = ref('')
const from = ref('')
const safeword = ref('')
const amount = ref('')
const withdrawFee = ref('0.00')
const withdrawAmountMin = ref(0)
const withdrawAmountMax = ref('0.00')

const passwordShow = ref(false)
const loading = ref(false)

const isEmptyParams = (str) => [null, undefined, ''].includes(str)

// 显示银行卡额外信息
const showBankMoreInfo = computed(() => {
  return ['argos'].includes(mode)
})

// 银行卡提现国家选择
const showBankNational = computed(() => {
  return ['shop2u'].includes(mode)
})

const nationality = ref('')
const countryName = ref('')
const countrySelectDone = (data) => {
  countryName.value = data.countryName
}

const validator = (val) => /^[0-9A-Za-z]+$/.test(val)
/**
 * 获取提现费率
 */
const getWithdrawFee = () => {
  exchangeGetWithdrawFee({
    channel: withdrawTypeVal.value === 'icon' ? typeValue.value : 'bank'
  }).then((res) => {
    const { withdraw_fee } = res
    withdrawFee.value = (withdraw_fee * 100).toFixed(2)
  })
}

/**
 * 获取提现区块
 */
const blockChainData = ref([])
const getWithdrawBlockChain = async () => {
  await exchangeGetBlockChain()
    .then((res) => {
      if (res.length) {
        const data = [...new Set(res.map((item) => item.coin).reverse())]
        typeValue.value = data[0]
      } else {
        typeValue.value = 'USDT'
      }
      blockChainData.value = res || []
    })
    .catch(() => {
      Toast.clear()
    })
}

const hasBindType = ref('')

// 协议类型
const list = computed(() => {
  let newList = []
  if (hasBindType.value) {
    newList = [
      {
        label: hasBindType.value,
        value: hasBindType.value
      }
    ]
  } else {
    const filterList = blockChainData.value.filter(
      (i) => i.coin === typeValue.value
    )
    newList = filterList.map((i) => ({
      ...i,
      label: i.blockchain_name,
      value: i.blockchain_name
    }))
  }

  if (newList.length) {
    channel.value = newList[0]?.value ?? ''
  }
  return newList ?? []
})

// 是否开启了通过绑定的地址提现
const isBindType = ref(false)
const showBindDialog = ref(false)
const notSub = ref(false)

const session_token = ref('')
const getSessionToken = async () => {
  await exchangeSetWithdrawToken({
    session_token: userStore?.userInfo?.token
  }).then((res) => {
    isBindType.value = Boolean(res.openWithdrawAddressBinding)
    showBindDialog.value =
      Boolean(res.openWithdrawAddressBinding) &&
      (!res.chainName || !res.existWithdrawAddress)
    notSub.value =
      Boolean(res.openWithdrawAddressBinding) &&
      (!res.chainName || !res.existWithdrawAddress)
    session_token.value = res.session_token

    // 数据
    if (Boolean(res.openWithdrawAddressBinding)) {
      typeValue.value = res.coinType
      from.value = res.existWithdrawAddress
      hasBindType.value = res.chainName
    }
  })
}

// 取款方式
const typeValue = ref('')
const showPicker = ref(false)
const typeColumns = computed(() => {
  if (blockChainData.value.length) {
    const data = [
      ...new Set(blockChainData.value.map((item) => item.coin).reverse())
    ]
    if (data.length) {
      return data.map((item) => ({ text: item, value: item }))
    }
  }
  return [{ text: 'USDT', value: 'USDT' }]
})

const openShowPicker = () => {
  if (!isBindType.value) {
    showPicker.value = true
  }
}

const onConfirm = ({ value }) => {
  typeValue.value = value
  showPicker.value = false
  getWithdrawFee()
}

onMounted(async () => {
  Toast.loading({
    duration: 0,
    message: t('loading'),
    forbidClick: true
  })

  // 获取提现范围
  getWithdrawLimit()
  // 获取提现区块
  await getWithdrawBlockChain()
  // 提现参数
  await getSessionToken()
  // 获取提现费率
  await getWithdrawFee()
  Toast.clear()
})

const getWithdrawLimit = () => {
  exchangeGetWithdrawLimit().then(res => {
    withdrawAmountMin.value = res.withdrawAmountMin || 0
    withdrawAmountMax.value = res.withdrawAmountMax || 0
  })
}

const withdrawUsdt = ref(0)

const realWithdrawAmount = computed(() => {
  const val = amount.value
  const fee = withdrawFee.value
  const ratio = NP.divide(NP.minus(100, fee), 100)
  const num = NP.times(val, ratio)
  const numStr = String(num)

  const obj = blockChainData.value.find(
    (item) =>
      item.coin === typeValue.value && item.blockchain_name === channel.value
  )
  const iconFee = obj ? obj.fee : 0
  withdrawUsdt.value = Number((Number(val) * iconFee).toFixed(2))

  if (numStr.includes('.')) {
    const numArr = numStr.split('.')
    return numArr[1].length === 1 ? numStr + '0' : numStr
  } else {
    return numStr + '.00'
  }
})

const realWithdrawAmountUsdt = computed(() => {
  const val = amount.value
  const fee = withdrawFee.value
  const ratio = NP.divide(NP.minus(100, fee), 100)
  const num = NP.times(val, ratio)

  const obj = blockChainData.value.find(
    (item) =>
      item.coin === typeValue.value && item.blockchain_name === channel.value
  )
  const iconFee = obj ? obj.fee : 0
  const res = num * iconFee

  return numberStrFormat(res)
})

const balanceFixed = ref(2)
const balanceAll = computed(() => userStore.userInfo.money)
const balanceTypeAll = computed(() => {
  const num = balanceAll.value ? Number(balanceAll.value) : 0
  const obj = blockChainData.value.find(
    (item) =>
      item.coin === typeValue.value && item.blockchain_name === channel.value
  )
  if (obj) {
    balanceFixed.value =
      typeValue.value === 'BTC' ? 6 : typeValue.value === 'ETH' ? 6 : 2
    return Number(num / Number(obj.fee))
  }
  return 0
})

const handleAll = () => {
  if (!notSub.value) {
    const allMoney = Number(
      numberStrFormat(balanceTypeAll.value, balanceFixed.value).replace(
        /,/g,
        ''
      )
    )
    amount.value = allMoney
  }
}

const handleRecord = () => {
  router.push({ name: 'WithdrawRecord' })
}

/**
 * 提现验证
 */
const withdraw = () => {
  console.log('sss');
  if (withdrawTypeVal.value === 'icon') {
    const regex = /^[0-9A-Za-z]+$/ //正则表达式
    if (!regex.test(from.value)) {
      Toast(t('提现地址只能包含数字和字母'))
      return
    }

    if (isEmptyParams(channel.value)) {
      Toast(t('blockchainNetworkRequire'))
      return
    }

    if (isEmptyParams(from.value)) {
      Toast(t('withdrawalAddressRequire'))
      return
    }

    if (withdrawUsdt.value > balanceAll.value) {
      Toast(t('余额不足'))
      return
    }
    // if (withdrawUsdt.value < withdrawAmountMin.value) {
    //   Toast(`${t('提款金额不得低于最小提款限额')}: ${withdrawAmountMin.value}USDT`)
    //   return
    // }

    if (withdrawUsdt.value > withdrawAmountMax.value) {
      Toast(`${t('提款金额不得高于最大提款限额')}: ${withdrawAmountMax.value}USDT`)
      return
    }
  }

  if (withdrawTypeVal.value === 'bank') {
    if (showBankNational.value) {
      if (isEmptyParams(countryName.value)) {
        Toast(t('selectNation'))
        return
      }
    }

    if (isEmptyParams(bankName.value)) {
      Toast(t('请输入开户行名称'))
      return
    }

    if (isEmptyParams(bankUserName.value)) {
      Toast(t('entryName'))
      return
    }

    if (isEmptyParams(bankCardNo.value)) {
      Toast(t('请输入卡号'))
      return
    }

    // if (showBankMoreInfo.value) {
    //   if (isEmptyParams(routingNum.value)) {
    //     Toast(t('请输入路由号码'))
    //     return
    //   }

    //   if (isEmptyParams(accountAddress.value)) {
    //     Toast(t('请输入账户地址'))
    //     return
    //   }

    //   if (isEmptyParams(bankAddress.value)) {
    //     Toast(t('请输入银行地址'))
    //     return
    //   }
    // }
  }

  if (isEmptyParams(amount.value)) {
    Toast(t('withdrawalAmountRequire'))
    return
  }

  // 打开密码弹出层
  if (userStore?.userInfo?.safeword === 1) {
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
    })
      .then(() => {
        openPage('/personalInfo')
      })
      .catch(() => {
        console.log('cancel')
      })
  }
}

// 绑定成功
const bindDoneHandle = (data) => {
  typeValue.value = data.coin
  channel.value = data.blockchain_name
  from.value = data.channel_address
  notSub.value = false
  showBindDialog.value = false
}

/**
 * 提现提交
 */
const handleWithdraw = async () => {
  const coinItem = list.value.find(
    (item) => item.blockchain_name === channel.value
  )
  const coin = coinItem ? coinItem.coin : 'USDT'
  const params = {
    safeword: safeword.value,
    amount: amount.value,
    from: from.value,
    channel: coin,
    session_token: session_token.value
  }

  if (withdrawTypeVal.value === 'bank') {
    params.channel = 'bank'
    params.bankName = bankName.value
    params.bankUserName = bankUserName.value
    params.bankCardNo = bankCardNo.value

    if (showBankMoreInfo.value) {
      params.swiftCode = routingNum.value || ''
      params.routingNum = routingNum.value || ''
      params.accountAddress = accountAddress.value || ''
      params.bankAddress = bankAddress.value || ''
    }

    if (showBankNational.value) {
      params.countryName = countryName.value || ''
    }
  }

  loading.value = true

  exchangeGetWithdrawApply(params)
    .then(async () => {
      await userStore.getUserInfo(true)
      Toast(t('withdrawalApplySuccess'))
      getSessionToken()
      setTimeout(() => {
        handleRecord()
      }, 1500)
    })
    .finally(() => {
      loading.value = false
      getSessionToken()
    })
}

const showKeyboard = ref(true)

// 密码输入到6位发送请求
watch(
  () => safeword.value,
  (val) => {
    if (val.length === 6) {
      Toast.loading({
        duration: 0,
        forbidClick: true
      })
      handleWithdraw()

      passwordShow.value = false
      safeword.value = ''
    }
  }
)

// 是否有银行卡提现方式
const hasBankType = computed(() => {
  const mode = import.meta.env.MODE
  return !['tiktok-wholesale'].includes(mode)
  // return true
})

// 银行卡相关配置
let iconName = '虚拟币'
if (['familyShop', 'sm'].includes(mode)) {
  iconName = '加密货币'
}
if (['argos2'].includes(mode)) {
  iconName = '货币'
}

const withdrawType = ref(t(iconName))
const withdrawTypeVal = ref('icon')

const withdrawTypeData = ref([{ text: t(iconName), value: 'icon' }])
if (hasBankType.value) {
  withdrawTypeData.value.push({
    text: ['sm'].includes(mode) ? t('银行卡2') : t('银行卡'),
    value: 'bank'
  })
}
const typePicker = ref(false)
const bankName = ref('')
const bankUserName = ref('')
const bankCardNo = ref('')
const swiftCode = ref('')
const routingNum = ref('')
const accountAddress = ref('')
const bankAddress = ref('')

const typePickerConfirm = (data) => {
  if (data.value === 'bank' && ['familyShop', 'sm'].includes(mode)) {
    router.push({ path: `/customerService` })
  } else {
    withdrawType.value = data.text
    withdrawTypeVal.value = data.value
    typePicker.value = false
    amount.value = ''
    getWithdrawFee()
  }
}
</script>

<style scoped lang="scss">
.withdraw {
  padding: 25px;
  height: calc(100vh - var(--van-nav-bar-height));
  background-color: $background-color;
  overflow-y: scroll;
  &.is-ar {
    :deep(.van-field__control) {
      text-align: right !important;
    }
  }

  :deep(.inputCom) {
    .label {
      font-size: 12px;
    }

    input {
      font-size: 14px !important;
    }
  }

  .tips {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    font-size: 12px;
    padding-bottom: 10px;

    span:nth-child(1) {
      color: $text-color-light;
    }

    span:nth-child(2) {
      color: $primary-color;
    }

    .money {
      line-height: 1;
      > span {
        color: rgb(103, 194, 58) !important;
        padding: 0 4px;
      }
      color: rgb(103, 194, 58) !important;
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
}

.popup-content {
  padding: 80px 30px 0;
}

:deep(.van-field__control::placeholder) {
  color: #868c9a;
}

.icon-type-content {
  margin-bottom: 1.25rem;
  .van-cell {
    border: 1px solid rgb(238, 238, 238);
    box-sizing: border-box;
    height: 44px;
    border-radius: 4px;
    &::after {
      height: 0 !important;
      border-bottom: none !important;
    }
  }
}

.withdraw-all.is-ar {
  padding-left: 0;
  padding-right: 16px;
}

.current-balance {
  font-size: 12px;
  color: rgb(103, 194, 58);
  > span {
    padding-right: 4px;
  }
}

.required-txt {
  position: relative;
  padding-left: 10px;
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

.nationality-select {
  font-size: 14px;
  :deep(.input-item) {
    padding: 0 16px;
  }
}

.btn-content {
  margin-top: 10px;
  margin-bottom: 30px;
  background-color: var(--site-main-color);
  border-color: var(--site-main-color);
}
</style>
