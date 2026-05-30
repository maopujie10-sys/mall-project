<template>
  <van-cell-group>
    <van-cell
        v-for="(item,index) in list"
        :key="item.ts"
    >
      <template #title>
        <div class="font-13 text-gray">
          <span class="mr-1" v-if="item.netChange > 0">+{{ item.netChange }}</span>
          <span class="mr-1" v-else>{{ item.netChange }}</span>
          <span :class="item.change_ratio > 0 ? 'text-up' : 'text-down'">{{ item.change_ratio }}%</span>
        </div>
        <div class="font-bold text-base" style="color: #1F2025">{{ item.symbol }}</div>
        <div class="text-gray">
          <span>{{ item.current_time }}</span>
        </div>
      </template>
      <template #value>
        <div class="flex justify-end h-full ">
          <div class="mr-2.5">
            <p class="flex text-primary justify-end" :class="item.open < 1  ? 'text-up' : 'text-down'">
                        <span

                            class="font-semibold text-lg">{{
                            item.open.toString().substr(0, item.open.toString().length
                                - 1)
                          }}</span>
              <span class="text-xs">{{ item.open.toString().substr(item.open.toString().length - 1) }}</span>
            </p>
            <div class="text-gray">
              <span class="mr-1.5">H: {{ item.high }}</span>
            </div>
          </div>
          <div>
            <p class="flex text-primary justify-end" :class="item.close < 1  ? 'text-up' : 'text-down'">
                        <span

                            class="font-semibold text-lg">{{
                            item.close.toString().substr(0, item.close.toString().length
                                - 1)
                          }}</span>
              <span class="text-xs">{{ item.close.toString().substr(item.close.toString().length - 1) }}</span>
            </p>
            <div class="text-gray">
              <span>L: {{ item.low }}</span>
            </div>
          </div>
        </div>
      </template>
    </van-cell>
  </van-cell-group>
</template>

<script setup>
const props = defineProps({
  list: {
    type: Array,
    default() {
      return []
    }
  },
})

</script>

<style scoped>
.text-up {
  color: #2555F8;
}
</style>