<template>
  <div class="HeahNavigation">
    <img class="HeahNavigation-menu" src="@/assets/image/head/menu.png" alt="menu" @click="show=true" />
    <img class="HeahNavigation-login" src="@/assets/image/head/logo.png" alt="logo">
    <div class="HeahNavigation-login-flex"></div>
    <div class="connect-wallet">链接钱包</div>
    <router-link to="/language">
    <img class="HeahNavigation-lang" src="@/assets/image/head/lang.png" alt="logo">
    </router-link>
<!--    弹出菜单栏-->
    <van-popup class="popup" round v-model="show" close-icon-position="top-left" position="left" >
      <div>
        <img class="show-false" src="@/assets/image/head/akar-icons_arrow-left.png" @click="show=false"/>
        <div class="User-Info" v-if="user_token">
          <div class="User-uid">UID：176672339</div>
          <div class="assets-title">
            <div class="title-text">总资产（USDT）</div>
            <img v-if="assets_show"  src="@/assets/image/head/show.png" class="title-img" @click="assets_show=false"/>
            <img v-if="!assets_show"  src="@/assets/image/head/hide.png" class="title-img" @click="assets_show=true"/>
          </div>
          <div v-if="assets_show" class="assets">12345678.123</div>
          <div v-if="!assets_show" class="assets">*******</div>
          <div class="Wallet-function">
            <div class="Wallet-function-button recharge">充币</div>
            <div class="Wallet-function-button withdraw">提币</div>
          </div>
        </div>
        <div class="User-Info" v-if="!user_token">
          <div class="avatar-div">
            <img class="avatar-img" src="@/assets/image/head/avatar.png" />
          </div>
          <div class="Link">链接钱包</div>
        </div>
        <div class="segmentation"></div>
        <div class="tab1">
          <router-link  v-for="(item,index) in tab" :key="index" :to="item.path">
          <div class="tab-list1">
            <img class="tab-list1-icon" :src="item.imgUrl"/>
            <div class="tab-list1-title">{{item.title}}</div>
            <div class="tab-list1-flex"></div>
            <img class="tab-list1-icon-right" src="@/assets/image/head/Rectangle.png" />
          </div>
          </router-link>
        </div>
        <div class="segmentation"></div>
        <div class="tab1">
          <router-link  v-for="(item,index) in tab2" :key="index" :to="item.path">
            <div class="tab-list1">
              <img class="tab-list1-icon" :src="item.imgUrl"/>
              <div class="tab-list1-title">{{item.title}}</div>
              <div class="tab-list1-flex"></div>
              <img class="tab-list1-icon-right" src="@/assets/image/head/Rectangle.png" />
            </div>
          </router-link>
        </div>
        <div style="width: 100%;" class="h100"></div>
      </div>
    </van-popup>
  </div>
</template>
<script>
import {Popup} from 'vant';
export default {
  name: 'HeahNavigation',
  data(){
    return{
      show:false,
      assets_show:true,
      user_token:false,//判断是否登录
      tab:[
          {imgUrl:require('@/assets/image/head/trade.png'),title:'合约交易',path:'/'},
          {imgUrl:require('@/assets/image/head/hall.png'),title:'矿池大厅',path:'/'}
      ],
      tab2:[
        {imgUrl:require('@/assets/image/head/assets.png'),title:'资产中心',path:'/assetsCenter/assets'},
        {imgUrl:require('@/assets/image/head/account_change.png'),title:'账变记录',path:'/accountChange'},
        {imgUrl:require('@/assets/image/head/identity.png'),title:'身份认证',path:'/authentication'},
        {imgUrl:require('@/assets/image/head/language.png'),title:'语言设置',path:'/language'},
        {imgUrl:require('@/assets/image/head/exchange_rate.png'),title:'汇率设置',path:'/'},
        {imgUrl:require('@/assets/image/head/question.png'),title:'常见问题',path:'/CommonProblem'},
        {imgUrl:require('@/assets/image/head/customer_service.png'),title:'在线客服',path:'/'},
        {imgUrl:require('@/assets/image/head/Serve.png'),title:'服务条款',path:'/'},
      ]
    }
  },
  components: {
    [Popup.name]: Popup,
  },

}
</script>
<style lang="scss" scoped>
.HeahNavigation {
  width: 828px;
  padding: 27px 30px;
  box-sizing: border-box;
  display: flex;
  flex-direction: row;
  align-items:center;

  .HeahNavigation-menu {
    width: 50px;
    height: 42px;
  }

  .HeahNavigation-login {
    width: 120px;
    height: 42px;
    margin-left: 27px;
    position:relative;
    animation:myfirst 3s;
    -webkit-animation:myfirst 3s; /* Safari and Chrome */
    animation-iteration-count: infinite;
  }
  @keyframes myfirst
  {
    0%   { width: 100px;height: 36px;}
    25%  { width: 120px;height: 42px;}
    50%  { width: 100px;height: 36px;}
    75%  { width: 120px;height: 42px;}
    100% { width: 100px;height: 36px;}
  }
  @-webkit-keyframes myfirst /* Safari and Chrome */
  {
    0%   { width: 100px;height: 36px;}
    25%  { width: 120px;height: 42px;}
    50%  { width: 100px;height: 36px;}
    75%  { width: 120px;height: 42px;}
    100% { width: 100px;height: 36px;}
  }

  .HeahNavigation-login-flex {
    flex: 1;
  }
  .connect-wallet{
    font-size: 18px;
    padding: 7px 20px 7px 20px;
    background: #A0ABC1;
    border-radius: 5px;
    color: white;
    margin-right: 27px;
  }

  .HeahNavigation-lang {
    width: 42px;
    height: 42px;
  }
}

</style>
<!--弹出层样式-->
<style lang="scss" scoped>
.popup{
  height: 100%;
  width: 670px;
  .show-false{
    width: 48px;
    height: 48px;
    margin-top: 57px;
    padding-left: 30px;
  }
  .User-Info{
    padding: 69px 30px 63px 30px;
    box-sizing: border-box;
    .User-uid{
      font-weight: 400;
      font-size: 35px;
      color: #868C9A;
    }
    .assets-title{
      margin-top: 36px;
      color: #868C9A;
      display: flex;
      flex-direction: row;
      align-items:center;
      .title-text{
        font-size: 35px;
      }
      .title-img{
        flex-direction: column-reverse;
        align-items:center;
        justify-content:center;
        width: 48px;
        height: 48px;
      }
    }
    .assets{
      margin-top: 22px;
      font-weight: 700;
      font-size: 45px;
      color: #000000;
    }
    .Wallet-function{
      margin-top: 46px;
      display: flex;
      flex-direction: row;
      .Wallet-function-button{
        border-radius: 6px;
        padding: 13px 65px;
        font-weight: 400;
        font-size: 25px;
        color: #FFFFFF;
      }
      .recharge{
        background: #2C78F8;
      }
      .withdraw{
        margin-left: 45px;
        background: #C8CAD2;
      }
    }
    .avatar-div{
      width: 250px;
      height: 150px;
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      .avatar-img{
        width: 150px;
        height: 150px;
      }
      margin-bottom: 46px;
    }
    .Link{
      width: 250px;
      height: 60px;
      background: #C8CAD2;
      border-radius: 6px;
      text-align: center;
      line-height: 60px;
      font-weight: 400;
      font-size: 25px;
      color: #FFFFFF;
    }
  }
  .segmentation{
    width: 100%;
    height: 1px;
    background: #E5E7ED;
  }
  .tab1{
    .tab-list1{
      padding: 40px 57px 40px 30px;
      box-sizing: border-box;
      display: flex;
      flex-direction: row;
      align-items:center;
      justify-content:center;

      .tab-list1-icon{
        width: 48px;
        height: 48px;
      }
      .tab-list1-title{
        font-weight: 400;
        font-size: 30px;
        color: #000000;
        margin-left: 30px;
      }
      .tab-list1-flex{
        flex: 1;
      }
      .tab-list1-icon-right{
        width: 16px;
        height: 24px;
      }
    }
  }
}
</style>
