<template>
  <div class="footer yongqi">

    <div class="yongqi" v-for='(item,index) of items' :key="index" :class='[item.cls,{on:index === idx}]' @click="change(item,index)"
         style="display: flex;flex-direction:column;justify-content:center;align-items:center;">
      <img :src="index===idx?item.srcSelect:item.src">
      <!--      <div><i :class="index===idx?item.iconSelect:item.icon" v-if="!showIconOrSrc"></i></div>-->
      <span :class="['colorChange',{on:index===idx}]">{{ item.name }}</span>
    </div>
<!--    <div class="qiangdan">-->
<!--      <img v-if="!$store.state.qiangdan.qiangdan_status" @click="qiangdan_sj(true)" class="qiangdan1" src="../../assets/image/bottom/qiangdan.png" />-->
<!--      <img v-if="$store.state.qiangdan.qiangdan_status" class="qiangdan1 rotateImages" src="../../assets/image/bottom/refresh.png" />-->
<!--    </div>-->

  </div>
</template>
<script type="text/javascript">
// eslint-disable-next-line
/* eslint-disable */
import {Overlay, Toast} from 'vant';
import {qiangdan_post, qiangdanxiangqing_post} from "@/API/user";
import {mapGetters, mapMutations} from "vuex";
export default {
  props: {
    idx: {
      type: Number,
      default: 0,
    },
    items: {
      type: Array,
      default: function () {
        return ([{
          cls: "home",
          name: this.$t("首页"),
          push: "/home",
          src: require('../../assets/image/bottom/home.png'),
          srcSelect: require('../../assets/image/bottom/home2.png'),
        },
          {
            cls: "commodity",
            name: this.$t("商品"),
            push: "/commodity",
            src: require('../../assets/image/bottom/chongzhi.png'),
            srcSelect: require('../../assets/image/bottom/chongzhi2.png'),
          },
          // {
          //   cls: "shop",
          //   name: this.$t("店铺"),
          //   push: "/shop",
          //   src: require('../../assets/image/bottom/company_normal.png'),
          //   srcSelect: require('../../assets/image/bottom/company_normal2.png'),
          // },
          {
            cla: "cart",
            name: this.$t("购物车"),
            push: "/cart",
            src: require('../../assets/image/bottom/renwu.png'),
            srcSelect: require('../../assets/image/bottom/renwu2.png'),
          },
          {
            cla: "me",
            name: this.$t("我的"),
            push: "/me",
            src: require('../../assets/image/bottom/wode.png'),
            srcSelect: require('../../assets/image/bottom/wode2.png'),
          }]);
      }
    }
  },
  data() {
    return {
      qiangdan_show:false,
      timer_shijian:''
    }
  },
  components:{
    [Overlay.name]:Overlay
  },
  methods: {
    ...mapMutations(['setQiangdan']),
    ...mapMutations(['qiangdan_status_sj']),
    ...mapMutations(['qiangdan_tanchuang_sj']),
    qiangdan_sj(e){
      const t = this
      this.qiangdan_status_sj(e)
      qiangdan_post({}).then(res=>{
        console.log(res)
        // brush_time: 5
        // orderId: "3987503220907183731"
        var time = res.brush_time*1000
        console.log(time)
        t.timer_shijian = setTimeout(function () {
          t.qiangdan_xq(res.orderId);
        }, time);
      }).catch(function (err) {
        console.log(2222222222222)
        // Toast('网络波动请刷新页面');
        t.qiangdan_status_sj(false)
      })
    },
    qiangdan_xq(e){
      var t = this
      qiangdanxiangqing_post({orderId:e}).then(res=>{
        console.log(res)
        this.qiangdan_status_sj(false)
        this.setQiangdan(res)
        this.qiangdan_tanchuang_sj(true)
        console.log(this.$store.state)
      }).catch(function (err) {
        console.log(2222222222222)
        // Toast('网络波动请刷新页面');
        t.qiangdan_status_sj(false)

      })
    },
    change(item, index) {
      console.log(item.push)
      if (this.$route.path!==item.push){
        this.$router.push({path:item.push})
      }
      this.$emit("change", index)

    }
  },
  beforeDestroy() {
    clearTimeout(this.timer_shijian);
  }
}

</script>
<style lang="scss" scoped>
.rotate_bg{
  width: 500px;
  height: 500px;
  background: #59d1b6;
  margin: 200px auto;
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
.qiangdan{
  width: 44px;
  height: 44px;
  background: white;
  border-radius: 50%;
  position: absolute;
  bottom: 27px;
  display: flex;
  justify-content: center;
  align-items: center;
  //z-index: 999;
  .qiangdan1{
    width: 38px;
    height: 38px;
  }
}
.footer {
  box-shadow: 0 -2px 4px rgba(0, 0, 0, 0.08);
  display: flex;
  justify-content: center;
  position: fixed;

  /*left: 0;*/
  bottom: 0;
  //box-sizing: border-box;
  background: #ffffff;
  /*max-width: 100%;*/
  width: 375px;
  height: 56px;
  //z-index: 2000;
}

.yongqi {
  flex: 1;
  padding: 5px;
  box-sizing: border-box;
  font-size: 12px;
  width: 100%;
}

div img {
  width: 20px;
  height: 20px;
  //background: white;
}

div span {
  display: block;
  font-style: normal;
  font-weight: 400;
  font-size: 10px;
  line-height: 12px;
  /* identical to box height */

  text-align: center;

  color: #AAAAAA;
  margin-top: 4px;
}

.on {
  color: var(--color-main);
}
</style>
