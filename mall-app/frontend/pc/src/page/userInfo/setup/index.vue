<template>
  <div class="setup-index">
    <div class="page-title">{{ $t('message.home.setUp') }}</div>
    <div class="setup-list">
      <router-link class="item" to="/userInfo/setup/login-password">
        {{ $t('message.home.LoginPassword') }}
      </router-link>
      <router-link class="item" to="/userInfo/setup/transaction-password">
        {{ $t('message.home.transactionPassword') }}
      </router-link>
      <router-link class="item" to="/userInfo/setup/shipping-address">
        {{ $t('message.home.shippingAddress') }}
      </router-link>
      <router-link class="item" to="/userInfo/setup/account-cancellation" v-if="itemname == 'Argos'||itemname !== 'ArgosShop'">
        {{ $t('message.home.账号注销') }}
      </router-link>
    </div>
  </div>
</template>

<script>
export default {
  name: "SetupIndex",
  data() {
    return {
      itemname: process.env.VUE_APP_ITEM_NAME,
    };
  },
};
</script>

<style lang="scss" scoped>
.setup-index {
  > .setup-list {
    .item {
      margin-top: 26px;
      width: 422px;
      height: 50px;
      display: flex;
      align-items: center;
      padding: 0 17px;
      font-weight: 500;
      text-decoration: none;
      border: 1px solid #eeeeee;
      border-radius: 4px;
      color: #333;
      transition-duration: 0.3s;

      &:hover {
        box-shadow: 0 0 2px 1px rgba(0, 0, 0, 0.05);
      }
    }
  }
}
</style>
