<template>
  <div class="merchant-settled">
    <div class="merchant-settled-header">
      <div class="merchant-settled-header-wrap app-container">
        <div class="merchant-settled-top flex-between">
          <img
            class="logo"
            :src="require('@/assets/image/logo_1.png')"
            alt="EShop"
            @click="goHome"
          />
          <EsLang />
        </div>
        <div class="merchant-settled-banner">
          <h1>Merchant Settlement Agreement</h1>
          <p>
            The investment promotion policy comprehensively upgrades the
            high-quality merchants of sincere merchants
          </p>
        </div>
      </div>
    </div>

    <div class="merchant-settled-content app-container">
      <AgreeTextView v-if="!next" />
      <BusinessInforView v-else />
    </div>
    <EsFooterView />
  </div>
</template>

<script>
import EsLang from '@/components/header/lang'
import AgreeTextView from './agreeText.vue'
import BusinessInforView from './businessInfor.vue'
export default {
  name: 'EsMerchantSettled',
  components: { EsLang, AgreeTextView, BusinessInforView },
  data() {
    return {
      next: true,
    }
  },
  methods: {
    goHome() {
      this.$router.push('/')
    },
  },
}
</script>

<style lang="scss">
.merchant-settled {
  &-header {
    padding: 20px;
    min-height: 590px;
    background: var(--color-footer-bg);
    &-wrap {
      min-height: 590px;
      background: var(--color-footer-bg) url('../../assets/image/join.png')
        no-repeat;
      background-position: right;
    }
  }
  &-top {
    .logo {
      width: 165px;
      height: 44px;
      cursor: pointer;
    }
  }
  &-banner {
    max-width: 720px;
    min-height: 590px;
    display: flex;
    flex-direction: column;
    justify-content: center;
    h1 {
      font-weight: 600;
      font-size: 48px;
      color: var(--color-submain);
      margin-bottom: 10px;
    }
    p {
      font-weight: 600;
      font-size: 24px;
      color: var(--color-white);
      opacity: 0.6;
      line-height: 1.5em;
    }
  }
  &-content {
    position: relative;
    background-color: var(--color-white);
    padding: 0 20px;
    &-text {
      border-radius: 4px;
      border: 1px solid var(--color-border);
      position: relative;
      top: -90px;
      background-color: var(--color-white);
      padding: 24px;
      p {
        margin-bottom: 10px;
        line-height: 1.5em;
      }
    }

    &-agreement {
      font-weight: 500;
      font-size: 12px;
      width: 100%;
      text-align: center;
      margin: -60px 0 100px 0;
      .text {
        color: var(--color-black);
      }
      .agreement-link {
        font-weight: 400;
        color: var(--color-main);
        margin-left: 4px;
      }
      .agreement-btn {
        margin-top: 50px;
        .el-button {
          width: 100%;
          max-width: 475px;
          height: 52px;
          font-weight: 400;
          font-size: 16px;
        }
      }
    }
  }
}
</style>
