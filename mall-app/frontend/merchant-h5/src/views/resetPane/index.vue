<template>
  <div class="bg-white reset-pane">
    <fx-header>
      <template #title>
        {{ $t(headerTitle) }}
      </template>
    </fx-header>
    <div class="h-full w-full bg-white reset">
      <div class="pt-5 mb-5">
        <img style="margin: 0 auto; width: 70px; height: 70px;" :src="showImg" alt="">
      </div>
      <div class="text-center text-sm mb-5">{{$t(showTips)}}</div>
      <van-button class="w-full" style="margin-top:10px;" type="primary" @click="onSubmit">{{ $t(showbtn) }}
      </van-button>
    </div>
  </div>
  
</template>

<script setup>
import ResetEmail from "@/assets/imgs/me/reset-email.png";
import ResetPhone from "@/assets/imgs/me/reset-phone.png";
import { useRouter, useRoute } from "vue-router";
import {ref} from "vue";

import { useI18n } from 'vue-i18n'
const { t } = useI18n()
const route = useRoute();
const router = useRouter();
const type = route.query.type;
const headerTitle = type === 'email' ? ref('emailVerify') : ref('phoneVerify');
const showImg = type === 'email' ? ResetEmail : ResetPhone;
const showTips = type === 'email' ? ref('restEmailTip') : ref('resetPhoneTip');
const showbtn = type === 'email' ? ref('restEmailbtn') : ref('resetPhonebtn');
const onSubmit = () => {
  // type === 'email' ? router.push('/verifyPage?type=2') : router.push('/verifyPage?type=1')
  type === 'email' ? router.push('/bindVerify?type=2&reset=1') : router.push('/bindVerify?type=1&reset=1')
}


</script>

<style scoped lang="scss">
.reset-pane {
  min-height: 100vh;
}
.reset {
  padding: var(--van-cell-group-inset-padding);
  margin: 0 auto;
}
:deep(.van-button--primary) {
  background-color: var(--site-main-color);
  border-color: var(--site-main-color);
  border-radius: 4px;
}

</style>
