<template>
  <!-- 已认证 -->
  <div class="verified">
    <van-nav-bar :title="$t('身份认证')" left-arrow @click-left="onClickLeft"/>
    <div class="flex flex-col px-30 justify-center items-center pt-124">
      <img alt="success img" class="w-122 h-122" src="../../assets/image/assets-center/small-success.png"/>
      <div class="font-55 text-black mt-55">{{ $t('提交成功') }}</div>
      <div class="font-26 text-grey mt-23">{{ $t('您的资料已经成功上传！') }}</div>
      <div class="font-26 text-grey mt-20">{{ $t('系统将在三个工作日内审核完毕请您耐心等候。') }}</div>
      <button class="apply-btn w-full border-none rounded bg-blue text-white font-35 h-100 rounded mt-193"
              @click="$router.go(-1)">{{ $t('返回') }}
      </button>
    </div>
  </div>
</template>

<script>
export default {
  name: "Verified",
  data() {
    return {}
  },
  created() {

  },
  methods: {
    onClickLeft() {
      this.$router.go(-1);
    }
  }
}
</script>

<style lang="scss" scoped>
.verified {
  width: 100%;
  box-sizing: border-box;
}
</style>
