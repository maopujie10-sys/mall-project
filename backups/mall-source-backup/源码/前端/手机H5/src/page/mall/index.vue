<template>
  <div class="mall">
<!--    <van-nav-bar safe-area-inset-top-->
<!--        title="我要投资"-->
<!--    />-->
    <div class="gz">
      <router-link to="/PointsRules">
      <div class="gz-z">{{ $t('规则') }}</div>
      </router-link>
      <div class="yu-e">
        <div>{{ goods_points_action_data }}</div>
        <img v-if="show" class="yu-e-img rotateImages" src="@/assets/image/me/refresh.png" />
        <img @click="goods_points_action" v-if="!show" class="yu-e-img" src="@/assets/image/me/refresh.png" />
      </div>
      <div class="yu-e-title">{{ $t('当前积分') }}</div>
    </div>
    <van-pull-refresh style="min-height: 100vh;" v-model="refreshing" @refresh="onRefresh" :pulling-text="$t('下拉即可刷新')" :loosing-text="$t('释放即可刷新')" :loading-text="$t('加载中')">
      <van-list
          v-model="loading"
          :finished="finished"
          :loading-text="$t('加载中')"
          :finished-text="$t('没有更多了')"
          @load="onLoad"
      >
    <div class="shangp">

      <div v-for="(item,index) in list" :key="index" @click="touzi(item.goodsId)" class="shangp-item">
        <img class="shangp-img" :src="'https://rfbhabkjk.com/wap/public/showimg!showImg.action?imagePath='+item.iconImg" />
        <div class="van-multi-ellipsis--l3 shangp-title">
         {{item.name}}
        </div>
        <div class="shangp-jiage">
          <div class="t1"> {{item.prize}} </div>
          <div class="t2"> {{ $t('积分') }}</div>
        </div>
      </div>

    </div>
      </van-list>
    </van-pull-refresh>
    <div style="width: 100%;" class="h90"></div>
  </div>
</template>
<script>
import {NavBar, Tab, Tabs,PullRefresh,List} from 'vant';
import {goods_list_action_post, goods_points_action_post, project_listProject_action_post} from "@/API/user";

export default {
  data(){
    return{
      active:0,
      goods_points_action_data:'',
      show:false,
      list: [],
      loading: false,
      finished: false,
      refreshing: false,
      page_no: 0,
    }
  },
  components:{
    [List.name]: List,
    [PullRefresh.name]: PullRefresh,
  },
  created() {
    this.goods_points_action()
  },
  methods:{
    onRefresh() {
      // 清空列表数据
      this.finished = false;
      this.page_no = 0
      // 重新加载数据
      // 将 loading 设置为 true，表示处于加载状态
      this.loading = true;
      this.onLoad();
    },
    onLoad() {
      if (this.refreshing) {
        this.list = [];
        this.refreshing = false;
      }
      this.tuanduimingxi_post()
    },
    tuanduimingxi_post() {
      this.page_no++
      var data = {
        'pageNum': this.page_no,
        'pageSize': 10,
      }
      goods_list_action_post(data).then(res => {
        console.log(res)
        for (let i = 0; i < res.pageList.length; i++) {
          this.list.push(res.pageList[i]);
        }
        console.log(this.list)
        this.loading = false;

        if (res.pageList.length == 0) {
          this.finished = true;
        }
      })
    },
    qiehuan() {
      this.list = [];
      this.loading = false;
      this.finished = false;
      this.refreshing = false;
      this.page_no = 0;
      // this.onLoad()
    },
    goods_points_action(){
      this.show = true
      goods_points_action_post({}).then(res=>{
        console.log(res)

        this.show = false
        this.goods_points_action_data = res.points
      })
    },
    touzi(e) {
      console.log(e)
      this.$router.push('/InvestmentDetails?goodsId='+e)
    },
    onClickLeft(){
      this.$router.push('/me')
    },
  }
}
</script>
<style lang="scss" scoped>
.mall{
  position: relative;
  //background: #EFF2F7;
  min-height: 100%;
  font-size: 14px;
  padding: 0 15px;
  box-sizing: border-box;
  .gz{
    position: relative;
    margin-top: 10px;
    width: 100%;
    height: 86px;
    background: #1552F0;
    padding: 15px;
    box-sizing: border-box;
    border-radius: 4px;
    .gz-z{
      position: absolute;
      width: 70px;
      height: 26px;
      right: -1px;
      top: 0;
      bottom: 0;
      margin-top: auto;
      margin-bottom: auto;
      border-radius: 30px 0 0 30px;
      background: #F1F5FF;
      //background: url("@/assets/image/mall/Rectangle1372.png") no-repeat 100% 100%;
      text-align: center;
      font-style: normal;
      font-weight: 400;
      font-size: 12px;
      line-height: 26px;
      color: #1552F0;
    }
    .yu-e{
      display: flex;
      font-weight: 600;
      font-size: 30px;
      line-height: 36px;
      align-items: center;
      /* identical to box height */
      color: #FFFFFF;
      .yu-e-img{
        width: 22px;
        height: 22px;
        margin-left: 3px;
      }
    }
    .yu-e-title{
      margin-top: 4px;
      font-style: normal;
      font-weight: 400;
      font-size: 12px;
      line-height: 14px;
      color: #FFFFFF;
    }
  }
  .shangp{
    margin-top: 15px;
    display: flex;
    flex-wrap: wrap;
    //justify-content: center;
    gap: 15px;
    .shangp-item{
      width: 165px;
      .shangp-img{
        width: 165px;
        height: 165px;

      }
      .shangp-title{
        margin-top: 11px;
        font-style: normal;
        font-weight: 400;
        font-size: 14px;
        line-height: 16px;

        color: #000000;
      }
      .shangp-jiage{
        margin-top: 12px;
        display: flex;
        .t1{
          font-style: normal;
          font-weight: 400;
          font-size: 16px;
          line-height: 16px;
          /* identical to box height */


          /* 主题色 */

          color: #1552F0;
        }
        .t2{
          margin-left: 5px;
          font-style: normal;
          font-weight: 400;
          font-size: 14px;
          line-height: 20px;

          /* #333333 */

          color: #333333;

        }
      }
    }
  }
  .rotateImages{
    -webkit-animation:myRotate 1s linear infinite;
    animation:myRotate 1s linear infinite;
  }
  @-webkit-keyframes myRotate{
    0%{ -webkit-transform: rotate(0deg);}
    50%{ -webkit-transform: rotate(180deg);}
    100%{ -webkit-transform: rotate(360deg);}
  }
  @keyframes myRotate{
    0%{ -webkit-transform: rotate(0deg);}
    50%{ -webkit-transform: rotate(180deg);}
    100%{ -webkit-transform: rotate(360deg);}
  }
}
</style>
<style>
.invest [class*=van-hairline]::after{
  border:none;
}
</style>
