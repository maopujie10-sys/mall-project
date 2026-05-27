<template>
  <div class="pay-success">
    <EsHeaderView />
    <div class="app-container">
      <div class="pay-success-content">
        <!-- <img :src="require('@/assets/image/wanc.png')" alt="success" /> -->
        <span class="iconfont icon-icon_duihao-mian"></span>
        <h2>{{ $t("message.home.paymentSuccessful") }}</h2>
        <p>
          {{ $t("message.home.receiver") }}：{{
            paySelectAddress.contacts || contacts
          }}
          +{{ paySelectAddress.phone || phone }}
        </p>
        <p>
          {{ $t("message.home.shippingAddress") }}：{{
            paySelectAddress.country || country
          }}
          {{ paySelectAddress.province || province }}
          {{ paySelectAddress.city || city }}
          {{ paySelectAddress.address || address }}
        </p>
        <p>
          {{ $t("message.home.desc5") }}
          <span class="customer-service" @click="showOnlieServiceDialog">
            {{ $t("message.home.customeService") }}
          </span>
        </p>
        <div class="pay-success-content-btns flex-start">
          <el-button @click="goHome">{{
            $t("message.home.BackHome")
          }}</el-button>
          <el-button type="primary" @click="checkOrder">{{
            $t("message.home.Checkorder")
          }}</el-button>
        </div>
      </div>
      <EsIconTips />
    </div>
    <EsFooterView />
    <EsOnlineServiceView v-model="showOnlieService" />
  </div>
</template>

<script>
  import { mapGetters } from "vuex";
  import EsIconTips from "@/components/iconTips";
  // import { notLogin } from '@/common/pageHook'
  import { openChatPage } from "@/util";
  export default {
    name: "EsPaySuccess",
    components: { EsIconTips },
    data() {
      return {
        showOnlieService: false,
        contacts: "",
        phone: "",
        country: "",
        province: "",
        city: "",
        address: "",
      };
    },
    computed: {
      ...mapGetters({
        paySelectAddress: "user/paySelectAddress",
        productDetails: "productDetails/productDetails",
      }),
    },
    mounted() {
      let address = this.paySelectAddress;
      if (address.address) {
        localStorage.setItem(
          "addressList",
          JSON.stringify({
            contacts: address.contacts,
            phone: address.phone,
            country: address.country,
            province: address.province,
            city: address.city,
            address: address.address,
          })
        );
      } else {
        const { contacts, phone, country, province, city, address } =
          JSON.parse(localStorage.getItem("addressList") || "{}");
        this.contacts = contacts;
        this.phone = phone;
        this.country = country;
        this.province = province;
        this.city = city;
        this.address = address;
      }
    },
    methods: {
      goHome() {
        this.$router.replace("/");
      },
      checkOrder() {
        this.$router.replace("/userInfo/my-order?index=2");
      },
      showOnlieServiceDialog() {
        // !notLogin() && (this.showOnlieService = true);
        const { id, name } = JSON.parse(
          localStorage.getItem("seller_cache") || "{}"
        );
        openChatPage(localStorage.getItem("ES_TOKEN"), id, name);
      },
    },
  };
</script>

<style lang="scss">
.icon-icon_duihao-mian{
  color: var(--color-main);
  margin-bottom: 10px;
  font-size: 128px;
}
  .pay-success {
    min-height: 100vh;
    position: relative;

    &-content {
      text-align: center;
      padding: 84px 20px;
          align-items: center;
    display: flex;
    justify-content: center;
    flex-direction: column;

      img {
        width: 100%;
        height: 100%;
        max-width: 98px;
        max-height: 98px;
        margin-bottom: 17px;
      }

      h2 {
        font-weight: 600;
        font-size: 24px;
        color: var(--color-title);
        margin-bottom: 12px;
      }

      p {
        //  display: inline-block;
        // font-weight: 500;
        max-width: 1000px !important;
        overflow:hidden; //超出的文本隐藏
        text-overflow:ellipsis; //溢出用省略号显示
        white-space:nowrap; 
        font-weight: 500;
        font-size: 16px;
        color: var(--color-title);
        margin-bottom: 12px;
      }

      .customer-service {
        color: var(--color-main);
        cursor: pointer;
      }

      &-btns {
        margin: 50px 0;
        display: flex;
        justify-content: center;

        .el-button {
          width: 255px;
          height: 50px;
        }

        .el-button--primary {
          margin-left: 35px;
        }
      }
    }

    .footer {
      position: absolute;
      left: 0;
      right: 0;
    }
  }
</style>
