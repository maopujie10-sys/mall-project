<template>
  <el-dialog
    custom-class="recharge-method-dialog"
    :title="$t('message.home.recharge')"
    :center="true"
    :visible.sync="dialogVisible"
    :close-on-click-modal="false"
    :close-on-press-escape="false"
  >
    <img
      class="banner"
      src="@/assets/image/recharge-image.png"
      alt="recharge"
    />
    <div class="desc">
      {{ $t('message.home.rechargeTips') }}
    </div>
    <div class="currency-list">
      <div
        v-for="item in coinList"
        :key="item"
        class="currency-item"
        @click="selectCurrency(item)"
      >
        <img :src="coinIcons[item]" :alt="item" />
        <div class="name">{{ item }}</div>
        <i class="el-icon-arrow-right" />
      </div>
      <!-- <div class="currency-item" @click="selectCurrency('eth')">
        <img src="@/assets/image/eth.png" alt="eth" />
        <div class="name">ETH</div>
        <i class="el-icon-arrow-right" />
      </div> -->
      <!-- <div class="currency-item" @click="selectCurrency('btc')">
        <img src="@/assets/image/BTc.png" alt="btc" />
        <div class="name">BTC</div>
        <i class="el-icon-arrow-right" />
      </div> -->
    </div>
  </el-dialog>
</template>

<script>
import { mapActions, mapGetters } from 'vuex'
const usdtIcon = require('@/assets/image/usdt.png')
const ethIcon = require('@/assets/image/eth.png')
const btcIcon = require('@/assets/image/BTc.png')

export default {
  name: 'recharge-method-dialog',
  props: {
    value: {
      type: Boolean,
      default: false,
    },
  },
  data() {
    return {
      dialogVisible: this.value || false,
      selected: 'balance',
      coinIcons: {
        USDT: usdtIcon,
        ETH: ethIcon,
        BTC: btcIcon,
      },
    }
  },
  watch: {
    value(val) {
      this.dialogVisible = val
    },
    dialogVisible(val) {
      if (val !== this.value) {
        this.$emit('input', val)
      }
    },
  },
  computed: {
    ...mapGetters('recharge', ['rechargeAddress']),
    coinList() {
      if (this.rechargeAddress) {
        const coinSet = new Set()
        this.rechargeAddress.map((item) => coinSet.add(item.coin))
        return [...coinSet]
      }
      return []
    },
  },
  mounted() {
    this.requestRechargeAddress()
  },
  methods: {
    ...mapActions('recharge', ['requestRechargeAddress']),
    selectCurrency(val) {
      this.$emit('select-currency', val)
      this.dialogVisible = false
    },
  },
}
</script>

<style lang="scss" scoped>
.recharge-method-dialog {
  .banner {
    width: 450px;
    display: block;
    margin: 0 auto;
  }

  .desc {
    font-weight: 500;
    font-size: 12px;
    text-align: center;
    color: #999999;
    margin: 10px 22px;
  }

  .currency-list {
    width: 450px;
    margin: 40px auto 20px;

    .currency-item {
      display: flex;
      align-items: center;
      border: 1px solid #eeeeee;
      border-radius: 4px;
      height: 50px;
      padding: 0 18px;
      transition-duration: 0.3s;
      user-select: none;
      cursor: pointer;

      &:hover {
        background-color: #efefef;
      }

      + .currency-item {
        margin-top: 20px;
      }

      img {
        width: 24px;
      }

      .name {
        flex: 1;
        margin-left: 10px;
      }
    }
  }
}
</style>
