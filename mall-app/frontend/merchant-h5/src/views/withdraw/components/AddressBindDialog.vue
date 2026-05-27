<template>
  <div :class="{'active': modelValue}" class="dialog-content">
    <div class="form-content">
      <div class="title-content">
        {{ t('提款地址绑定') }}
        <van-icon name="cross" class="close" @click="closeDialog" />
      </div>
      <div class="content">
        <div class="item">
          <p>{{ t('取款方式') }}</p>
          <div class="select-item">
            {{ withdrawType }}
            <select v-model="withdrawType">
              <option v-for="(item, index) in withdrawColumns" :key="index" :value="item.value">{{ item.label }}</option>
            </select>
          </div>
        </div>
        <div class="item">
          <p>{{ t('链接协议') }}</p>
          <div class="select-item">
            {{ chainType }}
            <select v-model="chainType">
              <option v-for="(item, index) in chainColumns" :key="index" :value="item.value">{{ item.label }}</option>
            </select>
          </div>
        </div>
        <div class="item">
          <p>{{ t('收款钱包地址') }}</p>
          <van-field
            clearable
            v-model="address"
            :rules="[{ validator: addressValidator, message: t('提现地址只能包含数字和字母'), trigger: 'onChange' }]"
            class="input-item"
          />
        </div>
        <div class="item tips">{{ t('仅能绑定一个收款地址！') }}</div>
      </div>
      <van-button
        class="w-full btn-content"
        type="primary"
        :loading="submitLoading"
        @click="submitHandle"
      >{{ t('确认绑定') }}
      </van-button>
    </div>
    <div class="bg"></div>
  </div>
</template>

<script setup name="AddressBindDialog">
import { ref, computed } from 'vue'
import { Toast } from 'vant'
import { useI18n } from 'vue-i18n'
import {
  bindWithdrawAddress
} from '@/service/exchange.api'

const { t } = useI18n()

const $emit = defineEmits(['update:modelValue', 'bind-done'])
const props = defineProps({
  modelValue: {
    type: Boolean,
    default: false
  },
  chainData: {
    type: Array,
    default: () => []
  }
})
const closeDialog = () => {
	$emit('update:modelValue', false)
}


const withdrawType = ref('USDT')
const withdrawColumns = computed(() => {
  if (props.chainData.length) {
    const data = [...new Set(props.chainData.map(item => item.coin).reverse())]
    if (data.length) {
      withdrawType.value = data[0]
      return data.map(item => ({ label: item, value: item}))
    }
  }
  return [{ label: 'USDT', value: 'USDT' }]
})

const chainType = ref('TRC20')
const chainColumns = computed(() => {
  if (props.chainData.length) {
    const data = props.chainData.filter(item => item.coin === withdrawType.value)
    if (data.length) {
      chainType.value = data[0].blockchain_name
      return data.map(item => ({ label: item.blockchain_name, value: item.blockchain_name}))
    }
  }
  return [{ label: 'TRC20', value: 'TRC20'}, { label: 'ERC20', value: 'ERC20'}]
})

const address = ref('')
const addressValidator = (val) => /^[0-9A-Za-z]+$/.test(val);

const submitLoading = ref(false)
const submitHandle = () => {
  const regex=/^[0-9A-Za-z]+$/; //正则表达式
  if (!regex.test(address.value)) {
    Toast(t('提现地址只能包含数字和字母'))
    return;
  }

  submitLoading.value = true
  const params = {
    coin: withdrawType.value,
    blockchain_name: chainType.value,
    channel_address: address.value
  }

  bindWithdrawAddress(params).then(() => {
    $emit('bind-done', params)
  }).finally(() => {
    submitLoading.value = false
  })
}
</script>

<style lang="scss" scoped>
.dialog-content {
  pointer-events: none;
  opacity: 0;
  > div {
    position: fixed;
  }
  > .form-content {
    width: 90%;
    padding: 21px 15px;
    border-radius: 8px;
    background-color: #fff;
    left: 5%;
    top: 50%;
    transform: translateY(-50%);
    z-index: 999;
    transition: all 0.3s ease;
    opacity: 0;
    > .title-content {
      position: relative;
      text-align: center;
      font-size: 16px;
      font-weight: bold;
      > .close {
        position: absolute;
        right: 0;
        font-size: 20px;
      }
    }
    > .content {
      > .item {
        margin-top: 15px;
        &:first-child {
          margin-top: 0;
        }
        &.tips {
          font-size: 14px;
          color: #FF3E3E;
          margin-top: 10px;
        }
        > p {
          font-size: 12px;
          color: #333333;
        }
        > .select-item {
          width: 100%;
          height: 34px;
          border: 1px solid #DDDDDD;
          border-radius: 4px;
          margin-top: 5px;
          color: #333;
          font-size: 14px;
          position: relative;
          display: flex;
          align-items: center;
          padding: 0 10px;
          > select {
            width: 100%;
            height: 100%;
            position: absolute;
            top: 0;
            left: 0;
            opacity: 0;
          }
        }
        .input-item {
          width: 100%;
          height: 34px;
          border: 1px solid #DDDDDD;
          border-radius: 4px;
          margin-top: 5px;
          color: #333;
          font-size: 14px;
          padding: 0 10px;
          :deep(input) {
            line-height: 34px;
            font-size: 14px;
            color: #333;
          }
        }
      }
    }
    .btn-content {
      margin-top: 25px;
      background-color: var(--site-main-color);
      border-color: var(--site-main-color);
    }
  }
  > .bg {
    width: 100vw;
    height: 100vh;
    background-color: rgba(0, 0, 0, .4);
    top: 0;
    left: 0;
    z-index: 998;
    opacity: 0;
		transition: all 0.3s ease;
  }
  &.active {
    pointer-events: auto;
    opacity: 1;
    > .form-content {
      opacity: 1;
    }
    > .bg {
      opacity: 1;
    }
  }
}
</style>
