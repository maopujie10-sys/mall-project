<template>
<div class="flex items-center justify-between bg-white" v-if="Object.keys(itemData).length > 0">
  <div :class="isArLang ? 'pr-4' : 'pl-4'">
    <template v-if="itemData.amount < 0">
      <img class="w-5 h-5" src="@/assets/image/fundsRecords/out.png" alt="">
    </template>
    <template v-else>
      <img class="w-5 h-5" src="@/assets/image/fundsRecords/in.png" alt="">
    </template>
  </div>
  <div class="flex-1 pr-4 ml-4 van-hairline--bottom record-item">
    <div class="flex justify-between items-center">
      <div class="font-14">
        <div class="text-black">
          <p class="title" :class="{'is-ar': isArLang}">{{ itemData.typeStr }}</p>
          <van-icon v-if="itemData.content_type === 'order-income' && item.detail && item.detail.length" name="question" color="icon" @click="showMoneyLevel(item)" />
        </div>
        <div class="font-12 time">{{ formatZoneDate(item.createTimeStr) }}</div>
      </div>
      <div :class="[itemData.amount < 0 ? 'down' : 'up']" class="font-14">{{ itemData.count }}</div>
    </div>
    <div v-if="item.oderNum" class="order-num">
        <p>{{ t('订单号') }}:</p>
        <p>{{ item.oderNum }}</p>
        <i class="iconfont icon-fuzhi" @click="copy(item.oderNum)"></i>
      </div>
  </div>
</div>
</template>

<script setup>
import { computed } from 'vue'
import useClipboard from 'vue-clipboard3'
import { Toast } from 'vant'
import { useI18n } from 'vue-i18n'
import { formatZoneDate, numberStrFormat } from '@/utils'
import { arLangCheck } from '@/utils/arLangCheck'

const isArLang = arLangCheck()

const { t } = useI18n()
const props = defineProps(['item'])
const itemData = computed(() => {
  const data = props.item
  const amount = Number(data.amount)
  let amountStr = numberStrFormat(Math.abs(amount))
  data.count = amount > 0 ? `+ $${amountStr}` : `- $${amountStr}`
  return data
})

const { toClipboard } = useClipboard()
const copy = async (id) => {
    try {
        await toClipboard(id);
        Toast(t('copySuccess'));
    } catch (e) {
        console.error(e);
    }
}

const emits = defineEmits(['show'])

const showMoneyLevel = (data) => {
  emits('show', data)
}
</script>

<style lang="scss" scoped>
.up {
  color: #0ECB81;
}

.down {
  color: #FF3E3E;
}

.order-sn {
  font-size: 12px;
  display: flex;
  align-items: center;
  color: $text-color-dark;

  svg {
    margin-left: 8px;
    color: $text-color-light;
  }
}

.text-black {
  display: flex;
  align-items: center;
  > p {
    padding-right: 5px;
    &.is-ar {
      padding-right: 0;
      padding-left: 5px;
    }
  }
  .icon {
    color: var(--site-main-color);
  }
}

.record-item {
  padding: 10px 15px 10px 0;
  .title {
    font-size: 14px;
    color: #000;
  }
  .time {
    color: #999;
    font-size: 12px;
    margin-top: 2px;
  }
}

.order-num {
  display: flex;
  align-items: center;
  font-size: 12px;
  color: #666;
  > p {
    margin-right: 5px;
  }
}

</style>