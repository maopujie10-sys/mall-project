<template>
  <div class="page-main-content">
    <fx-header>
      <template #title>
        {{ $t('setting') }}
      </template>
    </fx-header>
    <van-cell-group :class="{'is-ar-cell-group': isArLang}">
      <van-cell :title="t('清除缓存')" value="0MB" />
      <van-cell @click="testUpdate" :title="t('检查更新')" is-link value="V1.0.2" />
      <van-cell v-if="showCancellation" @click="openCancellation" :title="t('账号注销')" is-link />
    </van-cell-group>
    <div class="btn">
      <van-button type="danger" block @click="loginOut">{{$t('退出')}}</van-button>
    </div>
  </div>
</template>

<script setup>
import { ref, nextTick, computed } from 'vue'
import { Toast } from "vant";
import { useRouter } from "vue-router";
import { useI18n } from 'vue-i18n';
import {useUserStore} from "@/store/user.js";
import { useSystemStore } from "@/store/system.js";
const { t } = useI18n();
const router = useRouter();

const showCancellation = ref(false)

nextTick(() => {
  const mode = import.meta.env.MODE
  showCancellation.value = ['argos', 'argos2'].includes(mode)
})

const systemStore = useSystemStore()
const isArLang = computed(() => {
  return systemStore.isArLang
})


// TODO: 推出登录
const loginOut = () => {
  let userStore = useUserStore()
  userStore.logout() // 恢复初始化
}

const testUpdate = () => {
  Toast.loading({
    message: t('加载中'),
    forbidClick: true,
  });
  setTimeout(() => {
    Toast({
      message: t('当前已是最新版本，无需更新~'),
      duration: 2000
    });
  }, 2000)
}

const openCancellation = () => {
  router.push('/setting/cancellation')
}
</script>

<style lang="scss" scoped>
.btn {
  margin: var(--van-cell-group-inset-padding);
  margin-top: 2rem;
}

:deep(.van-button) {
  border-radius: 4px;
}

:deep(.van-cell__title), :deep(.van-cell__value) {
  color: #333;
}

.is-ar-cell-group {
  :deep(.van-cell__value) {
    text-align: left;
    padding-left: 5px;
  }
}
</style>
