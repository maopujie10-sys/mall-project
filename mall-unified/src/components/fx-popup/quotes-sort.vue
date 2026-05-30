<template>
    <van-popup round :value="props.showSort" @input="val => this.$emit('input', val)" :close-on-click-overlay="false"
        position="bottom">
        <div class="relative px-15 pt-23 px-4">
            <div class="flex justify-between py-4 items-center">
                <h4 class="font-20 font-500 text-black">排序</h4>
                <img @click="onClose" class="z-20 w-8 h-8" src="@/assets/imgs/quotes/Group3752.png" alt="" />
            </div>
            <div @click="onSort(item.id)" class="flex items-center py-4 van-hairline--bottom"
                v-for="(item, index) in sortList" :key="index">
                <img class="w-4 mr-4" src="@/assets/imgs/quotes/Group3703.png" alt="">
                <p class="font-16" style="color: var(--dark-black)">{{ item.text }}</p>
            </div>
        </div>
    </van-popup>
</template>

<script setup lang="ts">
import { ref } from 'vue'

// data
const sortList = ref([
    { id: 1, text: '按代码排序', icon: '' },
    { id: 2, text: '按最新价格排序', icon: '' },
    { id: 3, text: '按涨跌排序', icon: '' },
    { id: 4, text: '按涨跌幅(%)排序', icon: '' },

])
/// props
const props = defineProps({
    showSort: {
        type: Boolean,
        default: false
    }
})

const emits = defineEmits(['close', 'sort'])

/// methods
const onSort = (id: number) => {
    emits('sort', id)
    onClose()
}

const onClose = () => {
    emits('close')
}

</script>