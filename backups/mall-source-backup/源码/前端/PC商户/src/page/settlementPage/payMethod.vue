<template>
    <!-- TODOLIST 2.切换支付方式disabled -->
  <div class="pay-method">
    <h1 v-if="showTitle">{{ $t('message.home.paymentMethod') }}</h1>
    <ul class="pay-method-content">
      <li class="pay-method-item flex-between">
        <div class="pay-method-item-left flex-start">
          <img :src="require('@/assets/image/Union.png')" alt="" />
          <p class="name">
            <span>{{ $t('message.home.Balance') }}</span>
            (
            <span class="amount">${{numberFormat (userBalance) }}</span>
            )
          </p>
        </div>
        <el-radio v-model="check" :label="1"></el-radio>
      </li>
      <li class="pay-method-item flex-between">
        <div class="pay-method-item-left flex-start">
          <img :src="require('@/assets/image/pay.png')" alt="" />
          <p class="name">
            <span>{{ $t('message.home.payPal') }}</span>
            (
            <span class="not-bind">{{ $t('message.home.notOpen') }}</span>
            )
          </p>
        </div>
        <el-radio v-model="check" :label="2" disabled></el-radio>
      </li>
      <li class="pay-method-item flex-between">
        <div class="pay-method-item-left flex-start">
          <img :src="require('@/assets/image/visa.png')" alt="" />
          <p class="name">
            <span>Visa</span>
            (
            <span class="not-bind">{{ $t('message.home.notOpen') }}</span>
            )
          </p>
        </div>
        <el-radio v-model="check" :label="3" disabled></el-radio>
      </li>
      <li class="pay-method-item flex-between">
        <div class="pay-method-item-left flex-start">
          <img :src="require('@/assets/image/master.png')" alt="" />
          <p class="name">
            <span>{{ $t('message.home.mastercard') }}</span>
            (
            <!-- <span class="tips">
              {{ $t('message.home.additional') }}
              <i>$23</i>
              {{ $t('message.home.handlingfee') }}
            </span> -->
            <span class="not-bind">{{ $t('message.home.notOpen') }}</span>
            )
          </p>
        </div>
        <el-radio v-model="check" :label="4" disabled></el-radio>
      </li>
    </ul>
  </div>
</template>

<script>
import { mapGetters, mapActions } from 'vuex'
import { numberFormat } from "@/util";
export default {
  naem: 'EsPayMethod',
  props: {
    showTitle: {
      type: Boolean,
      default: true
    },
  },
  data() {
    return {
      check: 1,
    }
  },
  computed: {
    ...mapGetters('user', ['userBalance']),
  },
  mounted() {
    this.requestGetUserBalanceList()
  },
  methods: {
    ...mapActions({
      requestGetUserBalanceList: 'user/requestGetUserBalanceList',
    }),
    numberFormat
  },
}
</script>

<style lang="scss">
html[dir="rtl"]{
  .pay-method-item-left .name{
    margin-right: 5px;
  }
}
.pay-method {
  h1 {
    font-weight: 600;
    font-size: 24px;
    color: var(--color-title);
    margin: 18px 0;
  }

  &-content {
    background: linear-gradient(0deg, #fff7ec, #fff7ec), #eeeeee;
    border-radius: 4px;
    padding: 0 28px;
  }

  &-item {
    padding: 15px 0;
    &-left {
      img {
        width: 20px;
      }
      .name {
        min-width: 200px;
        margin-left: 5px;
        span:first-child {
          font-weight: 600;
          font-size: 14px;
          color: var(--color-black);
        }
      }
      .amount {
        color: var(--color-price);
        font-weight: 600;
      }
      .not-bind {
        color: var(--color-subtitle);
        font-weight: 600;
      }
      .tips {
        color: var(--color-subtitle);
        font-weight: 400;
        i {
          color: var(--color-main);
        }
      }
    }
    .el-radio__label {
      display: none;
    }
    .el-radio__inner {
      background-color: #d9d9d9;
    }
  }
}
</style>
