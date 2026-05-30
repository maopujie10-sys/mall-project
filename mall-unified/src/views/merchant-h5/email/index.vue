<template>
  <div class="h-full w-full bg-white">
    <fx-header>
      <template #title>
        Email
      </template>
    </fx-header>
    <div class="main">
      <div>Email</div>
      <div>
        <ExInput style="padding-bottom:0!important;" placeholderText="Please enter your email"
                 v-model="name" />
      </div>
      <van-button class="w-full"
                  :type="name ? 'primary ' : ''"
                  :style="{'marginTop': '10px', backgroundColor: !name ? '#F6F6F6' : '#1552F0', color:  !name ? '#999' : '#fff'}"
                  @click="changeName">Save</van-button>
    </div>
  </div>
</template>

<script setup>
import { ref } from "vue";
let name = ref("");
const changeName = () => {
  console.log('changeName', name.value)
}
</script>

<style lang="scss" scoped>
.main {
  padding: var(--van-cell-group-inset-padding);
}
</style>
