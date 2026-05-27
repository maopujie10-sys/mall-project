<template>
  <div class="h-full w-full bg-white">
    <fx-header>
      <template #title>
        Mobile number
      </template>
    </fx-header>
    <div class="main">
      <div>Mobile number</div>
      <div>
        <ExInput style="padding-bottom:0!important;" placeholderText="Please enter your number"
                 v-model="name" :dialCode="dialCode" @selectArea="onSelectArea" area :icon="icon" />
      </div>
      <van-button class="w-full"
                  :type="name ? 'primary ' : ''"
                  :style="{'marginTop': '10px', backgroundColor: !name ? '#F6F6F6' : '#1552F0', color:  !name ? '#999' : '#fff'}"
                  @click="changeName">Save</van-button>
      <nationality-list ref='controlChildRef' :title="$t('selectArea')" @get-name="getName"></nationality-list>

    </div>
  </div>
</template>

<script setup>
import { ref } from "vue";
import nationalityList from '../authentication/components/nationalityList.vue'

let name = ref(null);
let dialCode = ref(0)
const controlChildRef = ref(null)
let icon = ref('')
const changeName = () => {
  console.log('changeName', name.value)
}
const onSelectArea = () => {
  controlChildRef.value.open();
}

//获取到当前选中国家的code值
const getName = (childname, childcode, childdialCode) => {
  icon.value = childcode;
  dialCode.value = childdialCode;
}
</script>

<style lang="scss" scoped>
.main {
  padding: var(--van-cell-group-inset-padding);
}
</style>
