<template>
  <div class="order-sum">
    <h1>{{ $t("message.home.orderSummary") }}</h1>
    <ul class="order-sum-content">
      <li
        v-for="(item, index) in orderSum"
        :key="index"
        :class="{ total: index === orderSum.length - 1, 'flex-between': true }"
      >
        <span>{{ item.name }}</span>
        <span> {{ item.value }} </span>
      </li>
    </ul>
  </div>
</template>

<script>
import { numberFormat } from "@/util";
export default {
  naem: "EsOrderSum",
  props: {
    checkGoods: {
      type: [],
      default: 0,
    },
  },
  data() {
    return {
      orderSum: [
        {
          name:
            this.$t("message.home.commodity") + this.$t("message.home.amount"),
          value: `$0`,
        },
        {
          name: this.$t("message.home.discount"),
          value: "-$0.00",
        },
        {
          name: this.$t("message.home.tax"),
          value: "+$0.00",
        },
        {
          name: this.$t("message.home.deliveryFee"),
          value: "+$0.00",
        },

        {
          name: this.$t("message.home.totalNum"),
          value: `$22`,
        },
      ],
    };
  },
  watch: {
    checkGoods(newValue, oldvalue) {
      if (newValue !== oldvalue) {
        // console.log("this.checkGoods ->", this.checkGoods);
        this.$set(
          this.orderSum[0],
          "value",
          "$" +
            numberFormat(
              this.checkGoods.reduce(
                (a, b) =>
                  this.$big(a).plus(
                    this.$big(b.price || b.sellingPrice).times(b.checkTotal)
                  ),
                0
              )
            )
        );
        this.$set(
          this.orderSum[1],
          "value",
          "-$" +
            numberFormat(
              this.checkGoods.reduce(
                (a, b) =>
                  // a -
                  b.price
                    ? "0"
                    : b.discountPrice == null
                    ? "0"
                    : this.$big(
                        this.$big(b.sellingPrice).times(b.checkTotal)
                      ).minus(this.$big(b.discountPrice).times(b.checkTotal)),
                0
              )
            )
        );
        this.$set(
          this.orderSum[2],
          "value",
          "+$" +
            numberFormat(
              this.checkGoods.reduce(
                (a, b) =>
                  this.$big(a).plus(
                    this.$big(b.goodsTax || 0).times(b.checkTotal)
                  ),
                0
              )
            )
        );
        this.$set(
          this.orderSum[3],
          "value",
          "+$" +
            numberFormat(
              this.checkGoods.reduce(
                (a, b) =>
                  this.$big(a).plus(
                    this.$big(b.freightAmount || 0).times(b.checkTotal)
                  ),
                0
              )
            )
        );

        this.$set(
          this.orderSum[4],
          "value",
          "$" +
            numberFormat(
              this.checkGoods.reduce(
                (a, b) =>
                  this.$big(a).plus(
                    this.$big(b.price || b.discountPrice || b.sellingPrice)
                      .plus(b.goodsTax || 0)
                      .plus(b.freightAmount || 0)
                      .times(b.checkTotal)
                  ),
                0
              )
            )
        );

        // this.$set(this.orderSum[0], "value", `$${newValue}`);
        // this.$set(this.orderSum[3], "value", `$${newValue}`);
      }
    },
  },
};
</script>

<style lang="scss">
.order-sum {
  margin-bottom: 20px;

  h1 {
    font-weight: 600;
    font-size: 24px;
    color: var(--color-title);
    margin: 18px 0;
  }

  &-content {
    background-color: var(--color-little-grey);
    padding: 0 28px;
    border-radius: 4px;

    li {
      font-weight: 600;
      font-size: 14px;
      padding: 15px 0;

      span:first-child {
        color: var(--color-subtitle);
      }

      span:last-child {
        color: var(--color-black);
      }
    }

    .total {
      border-top: 1px solid var(--color-border);

      span {
        color: var(--color-price) !important;
      }
    }
  }
}
</style>
