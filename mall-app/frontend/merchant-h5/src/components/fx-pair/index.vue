<template>
    <section class="fx-pair">
        <div class="flex">
            <div class="w-12 h-12 relative mx-4" ref="htmlRefHook" @click="itemClick">
                <!-- <img class="w-8 h-8 absolute left-0 top-0 z-10" src="./EUR.png" alt="EUR" />
                <img class="w-8 h-8 absolute bottom-0 right-0" src="./GBP.png" alt="GBP" /> -->
                <img :src="`${IMG_PATH}/symbol/${item.symbol}.png`" alt="">
            </div>
            <div class="flex flex-col">
                <p class="text-primary text-lg font-semibold">{{ item.symbol || '--' }}<span class=" text-xs ml-2">{{
                        type
                }}</span></p>
                <p class="font-14 text-gray whitespace-nowrap">{{ item.name || '--' }}</p>
            </div>
        </div>
    </section>
</template>

<script setup>
import { IMG_PATH } from '@/config'
const props = defineProps({
    type: {
        type: String,
        default: ''
    },
    item: {
        type: Object,
        default() {
            return {}
        }
    }
})

const emits = defineEmits(['click-item'])

const itemClick = () => {
  emits('click-item')
}
</script>