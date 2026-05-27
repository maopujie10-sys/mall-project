<template>
  <div class="customerServiceIndex">
    <van-nav-bar
        :title="$t('客服')"
        left-arrow
        @click-left="onClickLeft"
    />
    <div class="nr">
      <img class="nr-img" src="../../assets/image/public/kefu.png" />
      <div class="t1">{{ $t('客服24小时为您竭诚服务') }}</div>
      <div class="t2">{{ $t('如果遇到问题需要帮助，请联系线上客服') }}</div>
      <router-link to="/customerService2">
      <div class="b1">{{ $t('开始咨询') }}</div>
      </router-link>
    </div>
  </div>
</template>
<script>
import {NavBar} from 'vant';

export default {
  data() {
    return {}
  },
  components:{
    [NavBar.name]:NavBar,
  },
  methods: {
    onClickLeft(){
      history.go(-1)
    },
  }
}
</script>
<style scoped lang="scss">
.customerServiceIndex{
  width: 100%;
  min-height: 100%;
  .nr{
    width: 100%;
    padding: 0 15px;
    box-sizing: border-box;
    //display: flex;
    //justify-content: center;
    .nr-img{
      margin-top: 15px;
      width: 100%;
    }
    .t1{
      margin-top: 30px;
      font-style: normal;
      font-weight: 400;
      font-size: 18px;
      line-height: 21px;
      /* identical to box height */

      text-align: center;
    }
    .t2{
      margin-top: 10px;
      font-style: normal;
      font-weight: 400;
      font-size: 14px;
      line-height: 16px;
      text-align: center;
      /* 全局主标题灰色 */
      color: #888CA1;
    }
    .b1{
      margin-top: 20px;
      width: 100%;
      height: 44px;
      background: var(--color-main);
      border-radius: 4px;
      font-style: normal;
      font-weight: 400;
      font-size: 16px;
      line-height: 44px;
      /* identical to box height, or 100% */

      text-align: center;
      color: #FFFFFF;
    }
  }
}
</style>