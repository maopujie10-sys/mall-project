<template>
  <div class="balance">
    <div v-loading="loading">
      <span>{{ $t("message.home.balance") }}</span>
      <!-- <i class="el-icon-view" @click="showBalance = !showBalance"></i> -->
      <img
        class="password-icon"
        :src="showBalance ? imageMap.open : imageMap.close"
        alt=""
        @click="isshow()"
      />
      <p>{{ showBalance ? numberFormat(userBalance) : "******" }}</p>
    </div>
  </div>
</template>
<script>
  import { mapActions, mapGetters } from "vuex";
  import { numberFormat } from "@/util";
  export default {
    data() {
      return {
        loading: false,
        showBalance: true,
        imageMap: {
          open: require("@/assets/image/eye-open.png"),
          close: require("@/assets/image/eye-close.png"),
        },
      };
    },
    computed: {
      ...mapGetters("user", ["userBalance"]),
    },
    async mounted() {
      this.showBalance =
        localStorage.getItem("showBalance") == "false" ? false : true;
      try {
        await this.requestGetUserBalanceList();
      } finally {
        this.loading = false;
      }
    },
    methods: {
      numberFormat,
      ...mapActions("user", ["requestGetUserBalanceList"]),
      isshow() {
        console.log("2 ->", 2);
        this.showBalance = !this.showBalance;
        localStorage.setItem("showBalance", this.showBalance);
      },
    },
  };
</script>
<style lang="scss">
html[dir="rtl"]{
  .visit-title{
    padding-left: 0;
    padding-right: 12px;
  }
  .visit-item-desc{
    padding-left: 0;
    padding-right: 10px;
  }
}
  .balance {
    width: 250px;
    height: 85px;
    text-align: center;
    background: url("../../../../assets/image/Group 3527.png");
    display: flex;
    align-items: center;
    justify-content: center;
    margin-bottom: 20px;

    span,
    i {
      color: var(--color-white);
      font-size: 12px;
      cursor: pointer;
    }

    .password-icon {
      width: 16px;
      cursor: pointer;
    }

    p {
      font-size: 26px;
      font-weight: 600;
      color: var(--color-price);
    }
  }
</style>
