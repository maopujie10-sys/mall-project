<template lang="pug">
section.quotes-header.flex.justify-between.p-4.bg-white
    div.flex
        img.w-8.h-8.mr-4(@click="emitSorts" src="@/components/quotes-header/sort.png" alt="sort")
        img.w-8.h-8(@click="route('/quotes/edit')" src="@/components/quotes-header/edit.png" alt="edit")
    div
        van-icon.font-bold(name="search" size="32" color="#000" @click="route('/quotes/search')")

</template>

<script setup lang="ts">
import { useRouter } from 'vue-router';

const emits = defineEmits(['show-sort'])
const router = useRouter()

//// methods
const emitSorts = () => {
    emits('show-sort')
}

const route = (url: string) => {
    router.push(url)
}



</script>