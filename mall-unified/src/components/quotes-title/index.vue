<template>
  <div class="px-4 py-2 bg-white shadow-md">
    <h2 class="text-3xl font-bold">行情</h2>
    <div class="overflow-auto flex tab mt-4" v-if="!advancedViewMode">
      <div class="item">
        <img class="w-4 h-4" src="./all.png" alt="all">
      </div>
      <div class="item" :class="{ 'active': activeIndex === 0 }" @click="tabItemClick(0)">
        <img class="w-4 h-4" src="./collect.png" alt="collect">
      </div>
      <div class="item" v-for="(item, index) in tabList" :key="item + index"
           :class="{ 'active': activeIndex === index + 1 }" @click="tabItemClick(index + 1, item.title)">
        {{ item.title }}
      </div>
      <div class="item" @click="handlerShowAddList">添加列表</div>
    </div>
    <div class="overflow-auto flex tab mt-4" v-else>
      <div class="item" :class="{ 'active': activeIndex === 0 }" @click="tabItemClick(0)">
        <img class="w-4 h-4" src="./collect.png" alt="collect">
      </div>
      <div class="item" @click="change">全部</div>
    </div>
  </div>
</template>

<script setup>
import {ref} from 'vue';
import {useRouter} from 'vue-router';

const props = defineProps({
  advancedViewMode: {
    type: Boolean,
    required: true
  }
})

const emits = defineEmits(['advanced-mode'])

// tab 列表点击
const activeIndex = ref(0)
const activeTitle = ref('');
const router = useRouter()
const tabList = ref([
  {
    title: 123,
    dataList: [],
  }
]);

// 添加
const handlerShowAddList = () => {
  router.push('/quotes/add')
}

const tabItemClick = () => {
  console.log(11)
}

// 切换模式
const change = () => {
  emits('advanced-mode')
}
</script>

<style lang="scss" scoped>
.tab {
  .item {
    flex-shrink: 0;
    display: flex;
    align-items: center;
    margin-right: 12px;
    padding: 3px 15px;
    border-radius: 10px;
    background: #F1F3F9;
    font-size: 12px;
    color: #1F2025;

    &:last-child {
      margin-right: 0;
    }
  }

  .active {
    background: #F45847;
    color: #fff;
  }
}

// :deep(.add.van-button) {
//   // height: 36px;
// }
</style>
