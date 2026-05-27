<template>
  <van-popup round :value="props.showItem" @input="val => this.$emit('input', val)" :close-on-click-overlay="false"
             position="bottom">
    <div class="relative px-15 pt-23 px-4">
      <div class="flex justify-between py-4 items-center">
        <h4 class="font-20 font-500 text-black font-bold">{{ props.symbol }}</h4>
        <img @click="onClose" class="z-20 w-8 h-8" src="@/assets/imgs/quotes/Group3752.png" alt=""/>
      </div>
      <div @click="onItem(item.id)" class="flex items-center py-4 van-hairline--bottom justify-between"
           v-for="(item, index) in sortList" :key="index">
        <p class="font-16 text-black">{{ item.text }}</p>
        <!-- <img class="w-4 mr-4" src="@/assets/imgs/quotes/Group3703.png" alt="" /> -->
        <van-icon :name="item.icon" size="24"></van-icon>
      </div>
    </div>
  </van-popup>
</template>

<script setup lang="ts">
import {ref} from 'vue'
import {useRouter} from 'vue-router'
import {useQuotesStore} from '@/store/quotes.store.js'
import {SET_STAGE} from '@/store/types.store'
import {defaultStage, defaultSeconds} from '@/config/index.js'
import {useVModels} from "@vueuse/core";

const quotesStore = useQuotesStore()

const router = useRouter()
// data
const sortList = ref([
  {id: 1, text: '新订单', icon: 'todo-list-o'},
  {id: 2, text: '图表', icon: 'todo-list-o'},
  {id: 3, text: '市场统计', icon: 'todo-list-o'},
  {id: 4, text: '高级视图模式', icon: 'todo-list-o'},

])
/// props
const props = defineProps({
  symbol: {
    type: String,
  },
  showItem: {
    type: Boolean,
    default: false
  }
})

const emits = defineEmits(['close', 'sort','advanced-mode'])

/// methods
const onItem = (id: number) => {
  if (id === 3) { // 详情
    router.push('detail?symbol=' + props.symbol)
  } else if (id === 2) {
    quotesStore[SET_STAGE]({stage: defaultStage, seconds: defaultSeconds})
    router.push(`/chart/index/${props.symbol}`)
  } else if (id === 1) {
    router.push(`/chart/order/${props.symbol}`)
  } else if (id === 4) {
    emits('advanced-mode')
  } else {
    console.log(123)
    emits('sort', id)
  }

  onClose()
}

const onClose = () => {
  emits('close')
}

</script>