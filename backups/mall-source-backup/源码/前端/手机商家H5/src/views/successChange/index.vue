<template>
  <div class="resetSuccess">
<!--    <fx-header :back="false" @back="loginOut">-->
<!--    </fx-header>-->
    <div class="content">
      <div class="text-base h-11">{{$t('passwordChangeSuccess')}}</div>
      <div class="imgBox"><img src="@/assets/imgs/me/success.png" alt=""></div>
      <div class="mt-4 font-700 text-base">{{ $t('changeSuccess') }}</div>
      <div class="text-grey mt-5 text-sm">{{ $t('useNewPasswordLogin') }}!</div>
      <van-button class="w-full btn-content" type="primary" @click="loginOut">({{time}}s) {{ $t('loginOut') }}
      </van-button>
    </div>
  </div>
</template>

<script setup>
import {ref, onMounted, onBeforeUnmount} from "vue";
import { useRouter } from 'vue-router';
import { useUserStore } from '@/store/user';
const router = useRouter()
const userStore = useUserStore()

const loginOut = () => {
  userStore.userInfo = {}
  router.push('/login')
}
let time = ref(10);
let timer = null;
const downTime = () => {
  timer = setInterval(() => {
    if (time.value > 0) {
      time.value--;
    } else {
      loginOut();
    }
  },1000)
};
onMounted(() => {
  downTime()
})
onBeforeUnmount(() => {
  clearInterval(timer);
})
</script>

<style lang="scss" scoped>
.resetSuccess {
  width: 100%;
  box-sizing: border-box;
}

.content {
  font-size: 12px;
  padding: 16px;
  text-align: center;
}

.imgBox {
  width: 50px;
  height: 50px;
  margin: auto;

  img {
    width: 100%;
    height: 100%;
  }
}

.btn-content {
    margin-top: 20px;
    background-color: var(--site-main-color);
    border-color: var(--site-main-color);
}
</style>
