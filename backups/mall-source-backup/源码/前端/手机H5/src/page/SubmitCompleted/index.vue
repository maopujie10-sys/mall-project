<template>
  <div class="SubmitCompleted">
    <van-nav-bar safe-area-inset-top
        fixed
        :title="$t('提交成功')"
        left-arrow
        @click-left="onClickLeft"
    />
    <div class="nr">
      <div class="icon">
        <img class="icon-img" src="@/assets/image/public/wanc.png" />
      </div>
      <div class="t1">{{$t('提交成功')}}</div>
      <div class="t2">{{ $t('请注意查收到账信息，如有疑问请联系客服') }}</div>
      <div class="shouye" @click="shouye">{{ $t('返回首页') }}</div>
      <div class="dingdan" @click="dingdan">{{ $t('查看订单') }}</div>
    </div>
  </div>
</template>
<script>
import { NavBar } from 'vant';
import {shifoushezhi_zijinmima_post} from "@/API/user";
export default {
  data(){
    return{
      url:''
    }
  },
  components:{
    [NavBar.name]:NavBar
  },
  created() {
    if (this.$route.query.path){
      this.url = this.$route.query.path
    }
  },
  methods:{
    dingdan(){
      this.$router.push('/'+this.url)
    },
    shouye(){
      this.$router.push('/')
    },
    onClickLeft(){
      // this.$router.push('/me')
      this.$router.go(-1)
    },
    zijinmimatiaozhuan(){
      const t = this
      shifoushezhi_zijinmima_post().then(res=>{
        if (res.safeword==0){
          t.$router.push('/FundPasswordSettings')
        }else {
          t.$router.push('/FundPasswordReset')
        }
      })
    },
    // tuichu(){
    //   localStorage.removeItem('token')
    //   this.$router.push('/')
    // }
  }
}
</script>
<style lang="scss" scoped>
.SubmitCompleted{
  width: 100%;
  min-height: 100%;
  * {
    box-sizing: border-box;
  }
  .nr{
    padding: 0 15px;
    box-sizing: border-box;
    .icon{
      //width: 50px;
      //height: 50px;
      width: 100%;
      display: flex;
      margin-top: 74px;
      justify-content: center;
      margin-bottom: 15px;
      .icon-img{
        width: 52px;
        height: 52px;
      }
    }
    .t1{
      font-style: normal;
      font-weight: 400;
      font-size: 16px;
      line-height: 14px;
      /* identical to box height, or 88% */

      text-align: center;

      color: #333333;
    }
    .t2{
      margin-top: 15px;
      font-style: normal;
      font-weight: 400;
      font-size: 14px;
      line-height: 20px;
      /* or 143% */

      text-align: center;

      color: #999999;
    }
    .shouye{
      margin-top: 60px;
      width: 100%;
      height: 44px;
      background: #FFFFFF;
      border: 1px solid #333;
      border-radius: 4px;
      font-style: normal;
      font-weight: 400;
      font-size: 16px;
      line-height: 44px;
      /* identical to box height, or 100% */
      text-align: center;
      color: #333;
    }
    .dingdan{
      border-radius: 4px;
      margin-top: 17px;
      width: 100%;
      height: 44px;
      font-style: normal;
      font-weight: 400;
      font-size: 16px;
      line-height: 42px;
      /* identical to box height, or 100% */
      text-align: center;
      color: #fff;
      background-color: var(--main-color);
    }
  }
}
</style>
