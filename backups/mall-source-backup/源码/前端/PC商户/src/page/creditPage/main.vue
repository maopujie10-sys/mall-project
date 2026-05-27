<template>
  <div>
    <!-- <EsHeaderView /> -->
    <div class="credit-container">
      <div class="bg">
        <div class="app-container sec">
          <img :src="require('@/assets/image/creditbg_text.png')" alt="" />
          <div class="title">{{ $t("message.home.creditText1") }}</div>
          <div class="tips">{{ $t("message.home.creditText2") }}</div>
          <div class="info">
            {{ $t("message.home.foryourmoney") }}
          </div>
          <div class="btn-group">
            <div
              @click="disabled ? goPage() : ''"
              :class="disabled ? '' : 'isDisabled'"
            >
              {{ $t("message.home.onlineApplin") }}
            </div>
            <div
              @click="!disabled ? goLoan() : ''"
              :class="!disabled ? '' : 'isDisabled'"
            >
              {{ $t("message.home.myloan") }}
            </div>
          </div>
        </div>
      </div>
      <div class="introduce app-container">
        <h2>{{ $t("message.home.safe") }}</h2>
        <div class="introduce-contain">
          <div class="item" v-for="(i, index) in itemList" :key="index">
            <img :src="i.url" alt="" />
            <div>
              <p>{{ i.name }}</p>
              <span>{{ i.dec }}</span>
            </div>
          </div>
        </div>
      </div>
      <div class="about">
        <div class="app-container">
          <div class="about-container">
            <div class="title">{{ $t("message.home.aboutUs") }}</div>
            <div class="info">
              <p>
                {{ $t("message.home.aboutText1") }}
              </p>
              <p>
                {{ $t("message.home.aboutText2") }}
              </p>
              <p>{{ $t("message.home.contactUs1") }}</p>
            </div>
            <div class="btn">
              <div class="item">{{ $t("message.home.committed") }}</div>
              <div class="item">{{ $t("message.home.financial") }}</div>
            </div>
          </div>
        </div>
      </div>
      <div class="introduce app-container cooperate">
        <h2>{{ $t("message.home.partnersTit") }}</h2>
         <div class="introduce-bank" v-if="itemname == 'FamilyShop' || itemname == 'SM-wholesale shop'">
          <div
            v-for="(i, index) in familyShopBankList"
            :key="index"
            @click="i.clickEvent"
            style="border:none"
          >
            <img :src="i.url" alt="" />
          </div>
        </div>
        <div class="introduce-bank" v-else>
          <div
            v-for="(i, index) in bankList"
            :key="index"
            @click="i.clickEvent"
          >
            <img :src="i.url" alt="" />
          </div>
        </div>
      </div>
    </div>
    <!-- <EsFooterView /> -->
  </div>
</template>

<script>
  import item1 from "@/assets/image/vector-1.png";
  import item2 from "@/assets/image/vector-2.png";
  import item3 from "@/assets/image/vector-3.png";
  import bank1 from "@/assets/image/banklogo1.png";
  import bank2 from "@/assets/image/banklogo-2.png";
  import bank3 from "@/assets/image/banklogo-3.png";
  import bank4 from "@/assets/image/banklogo-4.png";
  import bank5 from "@/assets/image/banklogo-5.png";
  import bank6 from "@/assets/image/banklogo-6.png";
  import bank7 from "@/assets/image/banklogo-7.png";
  import bank8 from "@/assets/image/banklogo-8.png";
  import bank9 from "@/assets/image/banklogo-9.png";
  import bank10 from "@/assets/image/banklogo-10.png";
  import { isCredit } from "@/api/credit";
  import { mapGetters } from "vuex";
  export default {
    data() {
      return {
        itemname: process.env.VUE_APP_ITEM_NAME,
        itemList: [
          {
            url: item1,
            name: this.$t("message.home.creditQuota"),
            dec: this.$t("message.home.aboutText2"),
          },
          {
            url: item2,
            name: this.$t("message.home.quickLoan"),
            dec: this.$t("message.home.creditReview"),
          },
          {
            url: item3,
            name: this.$t("message.home.safe"),
            dec: this.$t("message.home.safeInfo"),
          },
        ],
        familyShopBankList:[
          {
            url: require('@/assets/image/FamilyShop/Group_1.png'),
            clickEvent: () => {
              window.open("https://www.jpmorganchase.com/", "_blank");
            },
          },
          {
            url: require('@/assets/image/FamilyShop/Group_2.png'),
            clickEvent: () => {
              window.open("https://www.bankofamerica.com/", "_blank");
            },
          },
          {
            url: require('@/assets/image/FamilyShop/Group_3.png'),
            clickEvent: () => {
              window.open("https://www.wellsfargo.com/", "_blank");
            },
          },{
            url: require('@/assets/image/FamilyShop/Group_4.png'),
            clickEvent: () => {
              window.open("https://www.citi.com/", "_blank");
            },
          },
          {
            url: require('@/assets/image/FamilyShop/Group_5.png'),
            clickEvent: () => {
              window.open("https://www.goldmansachs.com/", "_blank");
            },
          },
          {
            url: require('@/assets/image/FamilyShop/Group_6.png'),
            clickEvent: () => {
              window.open("https://www.hsbc.com", "_blank");
            },
          },
          {
            url: require('@/assets/image/FamilyShop/Group_7.png'),
            clickEvent: () => {
              window.open("https://www.ubs.com", "_blank");
            },
          },
          {
            url: require('@/assets/image/FamilyShop/Group_8.png'),
            clickEvent: () => {
              window.open("https://www.credit-suisse.com", "_blank");
            },
          },
          {
            url: require('@/assets/image/FamilyShop/Group_9.png'),
            clickEvent: () => {
              window.open("https://www.barclays.co.uk/", "_blank");
            },
          },
          {
            url: require('@/assets/image/FamilyShop/Group_10.png'),
            clickEvent: () => {
              window.open("https://www.sc.com/en/", "_blank");
            },
          },
          {
            url: require('@/assets/image/FamilyShop/Group_11.png'),
            clickEvent: () => {
              window.open("https://10bestpersonalloans.com/go/pmax-usa-eng-d-g.html#o6", "_blank");
            },
          },
          {
            url: require('@/assets/image/FamilyShop/Group_12.png'),
            clickEvent: () => {
              window.open("https://www.mastercard.com/global/en.html", "_blank");
            },
          }
        ],

        bankList: [
          {
            url: bank1,
            clickEvent: () => {
              window.open("https://www.cimbclicks.com.my", "_blank");
            },
          },
          {
            url: bank2,
            clickEvent: () => {
              window.open("https://www.cimb.com.my", "_blank");
            },
          },
          {
            url: bank3,
            clickEvent: () => {
              window.open("https://www.rhbgroup.com", "_blank");
            },
          },
          {
            url: bank4,
            clickEvent: () => {
              window.open("https://www.loanstreet.sg/", "_blank");
            },
          },
          {
            url: bank5,
            clickEvent: () => {
              window.open("https://www.dbs.com.sg", "_blank");
            },
          },
          {
            url: bank6,
            clickEvent: () => {
              window.open("https://www.graceloanadvance.com/", "_blank");
            },
          },
          {
            url: bank7,
            clickEvent: () => {
              window.open("https://hk.lendela.com", "_blank");
            },
          },
          {
            url: bank8,
            clickEvent: () => {
              window.open("https://epaycash.hk/", "_blank");
            },
          },
          {
            url: bank9,
            clickEvent: () => {
              window.open("https://www.hangseng.com", "_blank");
            },
          },
          {
            url: bank10,
            clickEvent: () => {
              window.open("https://www.hsbc.com.hk", "_blank");
            },
          },
        ],
        disabled: false,
      };
    },
    mounted() {
      this.getIsCredit();
    },
     computed: {
      ...mapGetters(["isLogin"]),
    },
    methods: {
      async getIsCredit() {
        // console.log('this.isLogin ->', this.isLogin);
        if(this.isLogin){
        let res = await isCredit();
        this.disabled = res.data === "true" ? true : false;
      }
      },
      goPage() {
        this.$router.push("/credit/application");
      },
      goLoan() {
        this.$router.push("/credit/myLoan");
      },
    },
  };
</script>

<style lang="scss" scoped>
html[dir="rtl"]{
  .credit-container .bg .sec .btn-group div:nth-child(1){
    margin-right: 0 !important;
    margin-left: 36px !important;
  }
}
  .credit-container {
    margin-top: -14px;
    width: 100%;
    .bg {
      width: 100%;
      min-width: 1920px;
      height: 732px;
      background: url("~@/assets/image/credit-bg1.png") no-repeat center/cover;
      .sec {
        position: relative;
        padding-top: 174px;
        img {
          width: 793px;
          height: 107px;
          top: 129px;
          left: -50px;
          position: absolute;
        }
        .title {
          font-weight: 600;
          font-size: 64px;
          color: var(--color-main);
        }
        .tips {
          font-weight: 500;
          font-size: 36px;
          color: #ffffff;
        }
        .info {
          width: 950px;
          font-weight: 400;
          font-size: 20px;
          line-height: 23px;
          margin-top: 35px;
          color: #fff;
        }
        .btn-group {
          display: flex;
          div {
            width: 203px;
            height: 53px;
            border-radius: 4px;
            font-size: 18px;
            line-height: 53px;
            margin-top: 74px;
            text-align: center;
            cursor: pointer;
            will-change: filter;
            transition: filter 800ms;
            // cursor: no-drop;
            &:nth-child(1) {
              background: var(--color-main);
              color: #fff;
              margin-right: 36px;
              // pointer-events: none;
              // cursor: no-drop;
            }
            &:nth-child(2) {
              border: 1px solid var(--color-main);
              color: var(--color-main);
            }
            &:hover {
              filter: drop-shadow(0 0 4px var(--color-main));
            }
          }
          .isDisabled {
            background: #f1cfcf !important;
            color: #999 !important;
            border: 1px solid #999 !important;
            cursor: no-drop !important;
          }
        }
      }
    }

    .introduce {
      padding: 82px 0 150px 0;

      h2 {
        width: 100%;
        text-align: center;
        margin: 0 auto;
        font-weight: 600;
        font-size: 36px;
        color: #333;
        position: relative;
        &:after {
          //伪元素实现第二层
          content: " ";
          position: absolute;
          left: 48%;
          bottom: -9px;
          width: 54px;
          height: 4px;
          border-radius: 3px;
          background-color: var(--color-main);
          // -webkit-transform-origin: 0 0;
          // transform-origin: 0 0;
          // -webkit-transform: scaleY(0.5);
          // transform: scaleY(0.5);
        }
      }
      .introduce-contain {
        display: flex;
        justify-content: space-between;
        margin-top: 56px;
        .item {
          width: 306px;
          height: 345px;
          border: 1px solid #ededed;
          border-radius: 8px;
          display: flex;
          align-items: center;
          flex-direction: column;
          padding: 50px 20px;
          justify-content: space-between;
          will-change: filter;
          transition: filter 800ms;
          &:hover {
            // filter: drop-shadow(0 0 4px var(--color-main));
            filter: brightness(0.9);
          }
          &:nth-child(1) img {
            width: 91px;
            height: 91px;
          }
          &:nth-child(2) img {
            width: 100px;
            height: 100px;
          }
          &:nth-child(3) img {
            width: 82px;
            height: 78px;
          }
          p {
            font-weight: 600;
            font-size: 20px;
            text-align: center;
            color: #333333;
            margin-bottom: 10px;
          }
          span {
            display: inline-block;
            font-weight: 400;
            font-size: 16px;
            text-align: center;
            color: #777777;
          }
        }
      }
    }
    .about {
      width: 100%;
      height: 494px;
      background: url("~@/assets/image/image.svg") no-repeat center/cover;
      padding-top: 102px;
      .about-container {
        width: 50%;
        margin-left: 50%;
        .title {
          font-weight: 600;
          font-size: 36px;
          color: #ffffff;
          position: relative;
          &:after {
            //伪元素实现第二层
            content: " ";
            position: absolute;
            left: 0;
            bottom: -5px;
            width: 54px;
            height: 4px;
            border-radius: 3px;
            background-color: var(--color-main);
          }
        }
        .info {
          font-size: 14px;
          color: #ffffff;
          margin-top: 20px;
        }
        .btn {
          height: 45px;
          display: flex;
          margin-top: 30px;
          .item {
            font-size: 18px;
            text-align: center;
            line-height: 45px;
            &:nth-child(1) {
              width: 298px;
              height: 45px;
              background: url("~@/assets/image/about-btn1.png");
              color: #212121;
            }
            &:nth-child(2) {
              width: 268px;
              height: 45px;
              background: url("~@/assets/image/about-btn2.png");
              margin-left: -22px;
              color: var(--color-main);
            }
          }
        }
      }
    }
    .cooperate {
      // h2 {
      //   width: 392px;
      //   &::after {
      //     left: 174px;
      //   }
      // }
      .introduce-bank {
        display: flex;
        flex-wrap: wrap;
        div {
          width: calc((100% - 32px) / 4);
          min-width: calc((100% - 32px) / 4);
          max-width: calc((100% - 32px) / 4);
          height: 80px;
          background: #ffffff;
          border: 1px solid #ebebeb;
          border-radius: 4px;
          display: flex;
          vertical-align: middle;
          margin: 56px 10px 0 0;
          cursor: pointer;
          will-change: filter;
          transition: filter 800ms;
          &:nth-child(4n + 4) {
            margin-right: 0;
          }
          &:hover {
              filter: drop-shadow(0 0 4px var(--color-main));
            }
          img {
            max-width: 100%;
            max-height: 100%;
            display: block;
            margin: auto;
          }
        }
      }
    }
  }
</style>
