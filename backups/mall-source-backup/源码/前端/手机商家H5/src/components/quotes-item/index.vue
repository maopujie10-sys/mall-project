<template>
  <!--  @click="itemClick(props.item)"-->
  <van-cell>
    <template #title>
      <div class="flex items-center">
        <img src="./bookmark.png" alt="bookmark" class="w-4 h-4 -ml-4" v-if="!props.type">
        <van-icon name="cross" size="24" class="text-down" v-if="props.type === 'edit'"/>
        <fxPair @click-item="itemClick(props.item)" :item="item"/>
      </div>
    </template>
    <template #value>
      <div class="flex justify-end">
        <!-- 搜索 -->
        <div class="flex flex-col" v-if="props.type === 'search'">
          <p class="flex text-primary justify-end items-center">
            <van-icon name="search" class="mr-2"/>
            <span class="font-semibold text-lg">FXCM</span>
          </p>
          <p class="text-sm">
            forex
          </p>
        </div>
        <!-- 价格-->
        <div class="flex flex-col" v-else>
          <p class="flex text-primary justify-end">
                        <span
                            class="font-semibold text-lg">{{
                            item.close.toString().substr(0, item.close.toString().length
                                - 1)
                          }}</span>
            <span class="text-xs">{{ item.close.toString().substr(item.close.toString().length - 1) }}</span>
          </p>
          <p class="text-up text-sm" :class="item.change_ratio > 0 ? 'text-up' : 'text-down'">
            <span class="mr-2">{{ item.netChange }}</span>
            <span> {{ item.change_ratio }}%</span>
          </p>
        </div>
        <!-- 编辑右侧按钮 -->
        <div class="flex justify-end items-center ml-4" v-if="props.type === 'edit'">
          <van-icon name="exchange" size="20"/>
        </div>
      </div>
    </template>
  </van-cell>
</template>

<script setup>
import fxPair from '@/components/fx-pair/index.vue'

const emits = defineEmits(['click-item'])
const props = defineProps({
  item: {
    type: Object,
    default() {
      return {}
    }
  },
  type: {
    type: String,
    default: ''
  }
})


const itemClick = (a) => {
  console.log(a);
  emits('click-item', props.item)
  // console.log(1111)
}
</script>