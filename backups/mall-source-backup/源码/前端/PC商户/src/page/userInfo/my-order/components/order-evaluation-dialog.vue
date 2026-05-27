<template>
  <el-dialog
    custom-class="evaluation-dialog"
    :title="$t('message.home.evaluateOrder')"
    :visible.sync="dialogVisible"
  >
    <div class="evaluation-list" v-loading="loading">
      <div class="evaluation-item" v-for="item in orderGoods" :key="item.id">
        <div class="product-item">
          <img :src="item.goodsIcon" alt="order-detail-product" />
          <div class="info">
            <div class="title">
              {{ item.goodsName }}
            </div>
            <div class="price">${{ numberFormatFn(item.goodsReal) }}</div>
            <el-rate
              v-model="rateMap[item.goodsId]"
              :disabled="resultMap[item.goodsId]"
            />
          </div>
        </div>
        <el-input
          v-model="contentMap[item.goodsId]"
          class="content"
          type="textarea"
          :placeholder="$t('message.home.evaluateOrderPlaceholder')"
          resize="none"
          :disabled="resultMap[item.goodsId]"
        />
        <div class="action">
          <el-button @click="submit(item)" :disabled="resultMap[item.goodsId]">
            {{ $t('message.home.Submitareview') }}
          </el-button>
        </div>
      </div>
    </div>
  </el-dialog>
</template>

<script>
import { mapGetters, mapActions } from 'vuex'
import { numberFormat } from '@/util'
export default {
  name: 'order-evaluation-dialog',
  props: {
    value: {
      type: Boolean,
      default: false,
    },
    currentOrderInfo: {
      type: Object,
      default: () => {},
    },
    refresh: {
      type: Function,
    }
  },
  data() {
    return {
      dialogVisible: this.value || false,
      loading: false,
      rateMap: {},
      contentMap: {},
      resultMap: {},
    }
  },
  computed: {
    ...mapGetters({
      orderGoods: 'order/orderGoods',
    }),
  },
  watch: {
    value(val) {
      this.dialogVisible = val
    },
    dialogVisible(val) {
      if (val !== this.value) {
        this.$emit('input', val)
      }
      if (val) this.requestData()
    },
    orderGoods(newValue) {
      let rateMap = {}
      let contentMap = {}
      let resultMap = {}

      newValue.forEach((item) => {
        rateMap[item.goodsId] = 5
        contentMap[item.goodsId] = ''
        resultMap[item.goodsId] = false
      })

      this.rateMap = { ...rateMap }
      this.contentMap = { ...contentMap }
      this.resultMap = { ...resultMap }
    },
  },
  methods: {
    ...mapActions({
      requestOrderGoodsList: 'order/requestOrderGoodsList',
      requestOrderEvaluationList: 'order/requestOrderEvaluationList',
    }),
    getRate(id) {
      if (this.rateMap[id] < 2) {
        return 3
      } else if (this.rateMap[id] < 4) {
        return 2
      } 
      return 1
    },
    async requestData() {
      try {
        this.loading = true
        await this.requestOrderGoodsList({ orderId: this.currentOrderInfo.id })
      } finally {
        this.loading = false
      }
    },
    async submit(item) {
      const content = this.contentMap[item.goodsId]?.trim() ?? ''
      // if (!content) {
      //   this.$message.warning(this.$t('message.home.evaluateOrderPlaceholder'))
      //   return
      // }

      try {
        this.btnLoading = true
        await this.requestOrderEvaluationList({
          sellerGoodsId: item.goodsId,
          evaluationType: this.getRate(),
          rating: this.rateMap[item.goodsId],
          orderId: this.currentOrderInfo.id,
          content: content || this.$t('message.home.defaultRate'),
        })
        this.resultMap[item.goodsId] = true
        this.$notify({
          title: this.$t('message.home.successTips'),
          message: this.$t('message.home.evaluateOrderSuccess'),
          type: 'success',
        })
        this.$emit("closeDetails");
        this.refresh && this.refresh()
      } finally {
        this.btnLoading = false
      }
    },

    numberFormatFn(num) {
      return numberFormat(num);
    },
  },
}
</script>

<style lang="scss" scoped>
.evaluation-dialog {
  .evaluation-list {
    .evaluation-item {
      border: 1px solid #eeeeee;
      padding: 22px;

      + .evaluation-item {
        margin-top: 18px;
      }

      .product-item {
        display: flex;

        img {
          width: 62px;
          height: 62px;
        }

        .info {
          margin-left: 18px;
          flex: 1;

          .price {
            font-weight: 500;
            font-size: 16px;
            color: var(--color-main);
            margin-top: 7px;
          }

          .el-rate {
            margin-top: 5px;
          }
        }
      }

      .content {
        margin-top: 25px;

        .el-textarea__inner {
          border: 1px solid #efefef;
          height: 70px;
        }
      }
    }
  }

  .action {
    padding: 20px 0;
    display: flex;
    align-items: center;
    justify-content: center;

    .el-button {
      width: 450px;
      height: 50px;
      color: #fff;
      background: var(--color-main);
      border-color: var(--color-main);
      border-radius: 4px;
    }
  }
}
</style>
