<template>
  <div class="setting">
    <van-nav-bar safe-area-inset-top
        fixed
        :title="$t('设置')"
        left-arrow
        @click-left="onClickLeft"
    />
    <div style="width: 100%;" class="h46"></div>
    <div class="caidan">
      <router-link to="/LoginPasswordReset">
        <div class="caidan-list">
          <div class="caidan-neirong">{{ $t('登录密码') }}</div>
          <img src="@/assets/image/me/arrow_right.png" style="width: 20px;height: 20px;"/>
        </div>
      </router-link>
<!--      <router-link >-->
        <div class="caidan-list" @click="zijinmimatiaozhuan">
          <div class="caidan-neirong">{{ $t('资金密码') }}</div>
          <img src="@/assets/image/me/arrow_right.png" style="width: 20px;height: 20px;"/>
        </div>
      <router-link to="/Authentication">
        <div class="caidan-list">
          <div class="caidan-neirong">{{ $t('身份验证') }}</div>
          <div style="margin-right: 5px;">{{ kyc_get.status==2?$t('已认证'):$t('未设置') }}</div>
          <img src="@/assets/image/me/arrow_right.png" style="width: 20px;height: 20px;"/>
        </div>
      </router-link>
      <router-link to="/PhoneSettings">
        <div class="caidan-list">
          <div class="caidan-neirong">{{ $t('手机号') }}</div>

          <div style="margin-right: 5px;">{{ info_data.phone==null?$t('未设置'):'***'+info_data.phone.substring(info_data.phone.length-4, info_data.phone.length) }}</div>
          <img src="@/assets/image/me/arrow_right.png" style="width: 20px;height: 20px;"/>
        </div>
      </router-link>
      <router-link to="/EmailSettings">
        <div class="caidan-list" >
          <div class="caidan-neirong">{{ $t('邮箱') }}</div>
          <div style="margin-right: 5px;">{{ info_data.email==null?$t('未设置'):'***'+info_data.email.substring(info_data.email.length-4, info_data.email.length) }}</div>
          <img src="@/assets/image/me/arrow_right.png" style="width: 20px;height: 20px;"/>
        </div>
      </router-link>
    </div>
    <div class="tuichu" @click="tuichu">{{ $t('退出') }}</div>
    <div style="width: 100%;" class="h120"></div>
  </div>
</template>
<script>
import { NavBar } from 'vant';
import {gerenxinxi_post, kyc_get_action_post, shifoushezhi_zijinmima_post} from "@/API/user";
export default {
  data(){
    return{
      info_data:{},
      kyc_get:{}
    }
  },
  components:{
    [NavBar.name]:NavBar
  },
  created() {
    this.info_post()
    this.touzi()
  },
  methods:{
    touzi(){
      const t = this
      kyc_get_action_post({}).then(res=>{
        console.log(res)
        t.kyc_get = res
      })

    },
    info_post() {
      gerenxinxi_post({}).then(res => {
        this.info_data = res
        console.log(res)
      })
    },
    onClickLeft(){
      this.$router.push('/me')
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
    tuichu(){
      localStorage.removeItem('token')
      this.$router.push('/')
    }
  }
}
</script>
<style lang="scss" scoped>
.setting{
  .caidan {
    width: 100%;
    //padding: 10px 0;
    box-sizing: border-box;

    .caidan-list {
      width: 100%;
      padding: 15px;
      box-sizing: border-box;
      display: flex;
      align-items: center;
      font-style: normal;
      font-weight: 400;
      font-size: 14px;
      line-height: 16px;
      color: #333333;
      .caidan-icon {
        width: 20px;
        height: 20px;
        margin-right: 10px;
      }

      .caidan-neirong {
        flex: 1;
        font-style: normal;
        font-weight: 400;
        font-size: 14px;
        line-height: 16px;
        color: #333333;
      }
    }
  }
  .tuichu{
    margin: 15px 15px;
    background: var(--main-color);
    border-radius: 4px;
    height: 44px;
    font-style: normal;
    font-weight: 400;
    font-size: 16px;
    line-height: 44px;
    /* identical to box height */

    text-align: center;

    color: #FFFFFF;
  }
}
</style>
<style>

</style>
