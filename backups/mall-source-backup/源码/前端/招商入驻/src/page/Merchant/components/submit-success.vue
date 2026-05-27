<template>
  <div class="submit-success-wrap">
    <div class="wanc">
      <img src="@/assets/image/public/wanc.png" />
    </div>
    <div class="title">{{ $t('店铺入住申请已提交，请联系客服获取加速认证') }}</div>
    <div class="success-but-wrap">
      <div class="but but-one" @click="openUrl(2)">{{ $t('联系客服') }}</div>
      <div class="but but-two" @click="openUrl(1)">{{ $t('去登录') }}</div>

    </div>
    <div class="step-wrap1">
      <ul>
        <li>
          <div class="step-img">
            <div  :class="[status === 0 ? 'span-success' : 'span-pidding']"></div>
          </div>
          <div class="text">{{ $t('提交申请表') }}</div>
        </li>
        <li>
          <div class="step-img">
            <div  :class="[status === 1 ? 'span-success' : 'span-pidding']"></div>
          </div>
          <div class="text">{{ $t('背景审计') }}</div>
        </li>
        <li>
          <div class="step-img">
            <div  :class="[status === 2 ? 'span-success' : 'span-pidding']"></div>
          </div>
          <div class="text">{{ $t('成为店主') }}</div>
        </li>
      </ul>
    </div>
    <div class="advertise-img" v-if="itemname !== 'Sam-wholesaleShop' && itemname !== 'Sky City' && itemname !== 'Azedi'&& itemname !== 'SM-wholesale shop' && itemname !== 'FamilyShop' && itemname !== 'INT Overstock'&& itemname !== 'EShop'">
      <img src="@/assets/image/Merchant/advertise.jpg" />
    </div>
    <div class="advertise-img" v-if="itemname == 'SM-wholesale shop'">
      <img src="@/assets/image/Merchant/advertiseJ.jpg" />
    </div>
    <div class="advertise-img" v-if="itemname == 'FamilyShop'">
      <img src="@/assets/image/Merchant/advertiseF.png" />
    </div>
    <div class="advertise-img" v-if="itemname == 'INT Overstock'">
      <img src="@/assets/image/Merchant/int-banner.png" />
    </div>
   <div class="advertise-img" v-if="itemname == 'EShop'">
      <img src="@/assets/image/Merchant/EShop-banner.jpg" />
    </div>
    <div class="advertise-img" v-if="itemname == 'Azedi'">
      <img src="@/assets/image/Merchant/Azedi-banner.png" />
    </div>
    <div class="advertise-img" v-if="itemname == 'Sky City'">
      <img src="@/assets/image/Sky_banner.png" />
    </div>
    <div class="advertise-img" v-if="itemname == 'Sam-wholesaleShop'">
      <img src="@/assets/image/Sam_banner.png" />
    </div>
    <div class="tc" v-if="sellerSign">
              <p class="padding-tb">
               {{$t('s1')}}
              </p>
              <p>
                <!-- {{ $t("rzTitle1info") }} -->
                 {{$t('s2',{ name: itemname })}}
              </p>
              <p>
                <!-- {{ $t("rzTitle1info1") }} -->
                 {{$t('s3')}}
              </p>
              <p> {{$t('s4')}}</p>
              <p>
                <!-- {{ $t("rzTitle1info2") }} -->
                {{$t('s5')}}
              </p>
              <p>
                {{$t('s6')}}
              </p>
              <p>
                 {{$t('s7')}}
              </p>
              <p> {{$t('s8')}}</p>
              <p> {{$t('s9')}}</p>
              <p> {{$t('s10')}}</p>
              <!-- <p class="padding-tb">{{ $t("rzTitle2") }}</p> -->




              <p class="padding-tb"> {{$t('s11')}}</p>
              <p>
                <!-- {{ $t("rzTitle2info", { name: itemname }) }} -->
                {{$t('s12')}}
              </p>
              <p>
                <!-- {{ $t("rzTitle2info1") }} -->
                {{$t('s13')}}
              </p>
              <p>
                <!-- {{ $t("rzTitle2info2") }} -->
                 {{$t('s14')}}
              </p>
              <!-- <p>
              {{ $t("rzTitle2info3") }}
            </p> -->
              <!-- <p class="padding-tb">{{ $t("rzTitle3") }}</p> -->
              <p class="padding-tb"> {{$t('s15')}}</p>
              <p>
                <!-- {{ $t("rzTitle3info") }} -->
                {{$t('s16',{ name: itemname })}}
              </p>
              <p>
                <!-- {{ $t("rzTitle3info1") }} -->
                {{$t('s17')}}
              </p>
              <p>
                <!-- {{ $t("rzTitle3info2") }} -->
                {{$t('s18')}}
              </p>
              <p> {{$t('s19',{ name: itemname })}}</p>
              <p> {{$t('s20')}}</p>
              <p> {{$t('s21')}}</p>
              <!-- <p class="padding-tb">{{ $t("rzTitle4") }}</p> -->
              <!-- <p>
              {{ $t("rzTitle4info") }}

            </p>
            <p>
              {{ $t("rzTitle4info1") }}
            </p> -->
            </div>
    <Service :isShow='isShow' @show='closeService'/>
  </div>
</template>

<script>

// import { Toast } from "vant";
import Service from '@/page/customerService/pcIndex.vue'
  import {is_mobile} from '@/utils/utis'
  import {apiGetCustomerService} from "@/API/home.js";
import { getStatus } from "@/API/commodity";
import { HOST_URL } from '@/config'
export default {
  name: 'submitSuccess',
  components:{Service},
  props: {
    sellerSign: {
      default: false
    }
  },
  data() {
    return {
      itemname: process.env.VUE_APP_ITEM_NAME,
      status: 0,
      screenWidth: document.body.clientWidth,
      labelPosition: 'top',
      isShow:false,
      onlinePath:'',
      HOST_URL
    }
  },
  computed: {

  },
  created() {
    // this.getStatusInfo()

    if (this.screenWidth >= 500) {
      this.labelPosition = "left"
    } else {
      this.labelPosition = "top"
    }
    this.getOnlinePath()
  },
  methods: {
     async getOnlinePath() {
      let res = await apiGetCustomerService({code:'customer_service_url'});
      this.onlinePath = res.customer_service_url
    },
    //查询店铺申请进度
    getStatusInfo() {
      getStatus({}).then((res) => {
        this.status = res.status
      })
    },
    closeService(val){
        this.isShow = val
      },
    openUrl(index) {
      switch (index) {
        case 1:
          if (this.labelPosition=="left"){
            window.location.href = location.origin+"/ww"
            // window.location.href = location.origin+"/ww"
          }
          if (this.labelPosition=="top"){
            if(parent !== window){
              window.open(parent.location.origin+"/www")
            }else{
              window.location.href = location.origin+"/www"
            }

          }

          break;
          case 2:
            if(this.itemname == 'FamilyShop'){
              im_create_iframe_client.open();
              return
            }
             if (this.onlinePath) {
              window.open(
                this.onlinePath,
                "_blank"
              );
              }else if (is_mobile()) {
                this.$router.push("/customerServiceIndex");
              } else {
                this.isShow = true;
              }

          break;
        default:
          break;
      }
    }
  }
}
</script>

<style lang="scss" scoped>
.submit-success-wrap {
  width: 1200Px;
  border: 1px solid #EEEEEE;
  border-radius: 4Px;
  margin: 0 auto;
  padding-bottom: 30Px;
  margin-bottom: 30Px;
  background: #fff;
  .wanc {
    margin-top: 70Px;

    img {
      width: 100Px;
      height: 100Px;
      display: block;
      margin: 0 auto;
    }
  }

  .title {
    font-size: 16Px;
    color: #333333;
    line-height: 22Px;
    width: 700Px;
    margin: 0 auto;
    text-align: center;
    margin-top: 40Px;
  }

  .success-but-wrap {
    display: flex;
    justify-content: center;
    margin-top: 70Px;
    cursor: pointer;
    .but {
      width: 255Px;
      height: 50Px;
      border-radius: 4Px;
      text-align: center;
      line-height: 50Px;
      font-size: 16Px;
      overflow: hidden;
      text-overflow: ellipsis;
    }

    .but-one {
      border: 1px solid #EEEEEE;
      color: #333333;
    }

    .but-two {
      background: var(--color-main);
      color: #fff;
      margin-left: 40Px;
    }
  }

  .step-wrap1 {
    margin-top: 100Px;

    ul {
      display: flex;
      justify-content: center;

      li {
        width: 280Px;
        position: relative;

        .step-img {
          height: 55Px;
          display: flex;
          align-items: center;

          .span-success {
            width: 34Px;
            height: 34Px;
            background: url('@/assets/image/public/wanc.png');
            background-size: 100% 100%;
            margin: 0 auto;
          }

          .span-pidding {
            width: 28Px;
            height: 28Px;
            background: url('@/assets/image/Merchant/wanc2.png');
            background-size: 100% 100%;
            margin: 0 auto;
          }

        }

        .text {
          font-size: 16Px;
          color: #333333;
          text-align: center;
        }
      }

      li:not(:last-child) {
        &::after {
          background: #EEEEEE;
          position: absolute;
          content: '';
          right: 0;
          top: 40%;
          width: 110Px;
          height: 2Px;
        }
      }

      li:not(:first-child) {
        &::before {
          background: #EEEEEE;
          position: absolute;
          content: '';
          left: 0;
          top: 40%;
          width: 110Px;
          height: 2Px;
        }
      }
    }
  }

  .advertise-img {
    width: 938Px;
    margin: 0 auto;
    margin-top: 40Px;

    img {
      width: 100%;
    }
  }
}

@media screen and (max-width:500Px) {
  .tc{
    width: auto !important;
  }
  .submit-success-wrap {
    width: 100% !important;

    .wanc {
      margin-top: 70Px;

      img {}
    }

    .title {
      font-size: 16Px;
      color: #333333;
      line-height: 22Px;
      margin: 0 auto;
      width: 100%;
      text-align: center;
      margin-top: 40Px;
    }

    .success-but-wrap {
      display: block;
      margin-top: 70Px;

      .but {
        width: 80%;
        margin: 0 auto;
      }

      .but-two {
        background: var(--color-main);
        color: #fff;
        margin-left: 40Px;
        margin-top: 20Px;

      }
    }

    .step-wrap1 {
      margin-top: 30Px;

      ul {
        display: block !important;

        li {
          width: 280Px;
          position: relative;
          margin: 0 auto;
          margin-top: 20Px;

          .step-img {
            height: 55Px;
            display: flex;
            align-items: center;

          }

          .text {
            font-size: 16Px;
            color: #333333;
            text-align: center;
          }
        }

        li {
          &::after {
            height: 0Px !important;
          }
        }

        li {
          &::before {
            height: 0Px !important;
          }
        }
      }
    }

    .advertise-img {
      width: 90% !important;

    }
  }

}
.tc{
  padding: 0 20px;
  width: 938Px;
    margin: 0 auto;
    p {
          font-family: "PingFang HK";
          font-style: normal;
          font-size: 14px;
          // line-height: 20px;
          color: #333333;
          padding: 6px 0;
        }
    .padding-tb {
      color: #333333;
      font-weight: 600;
  padding: 10px 0 !important;
  img {
    width: 84px;
  }

}
  }
</style>
