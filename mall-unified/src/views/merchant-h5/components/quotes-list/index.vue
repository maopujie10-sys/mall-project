<template>
  <van-cell-group v-if="list.length > 0">
    <template v-if="!advancedViewMode">
      <quotes-items
          v-for="(item, index) in list"
          :item="item"
          :key="index"
          :type="props.type"
          @click-item="onClickItem"
      />
    </template>
    <template v-else>
      <quotes-advanced-item
        :list="list"
      />
    </template>
  </van-cell-group>
</template>

<script setup>
import QuotesItems from '@/components/quotes-item/index.vue'
import QuotesAdvancedItem from '@/components/quotes-advanced-item/index.vue'

import {onMounted} from "vue";

const emits = defineEmits(['click-item'])
const props = defineProps({
  type: {
    type: String,
    default: ''
  },
  list: {
    type: Array,
    default() {
      return []
    }
  },
  advancedViewMode: {
    type: Boolean,
    required: true
  }
})

onMounted(() => {
  console.log(props.list);
})


const onClickItem = (evt) => {
  emits('click-item', evt)
}


</script>

<style lang="scss" scoped>

</style>