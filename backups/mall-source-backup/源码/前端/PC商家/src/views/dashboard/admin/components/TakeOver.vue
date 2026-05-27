<template>
  <el-card class="take-over active">
    <div class="take-over-title">{{ $t('仪表盘') }}</div>
    <div class="take-over-content">
      <div class="take-over-content-item color-1">
        <div class="take-over-content-item-number">
          <FormatNumberShow :data="data.goodsNum"/>
        </div>
        <div class="take-over-content-item-title">{{ $t('商品总数') }}</div>
      </div>
      <div class="take-over-content-item color-2">
        <div class="take-over-content-item-number">
          <FormatNumberShow :data="data.totalSales" :currency="true"/>
        </div>
        <div class="take-over-content-item-title">{{ $t('销售总额') }}</div>
      </div>
      <div class="take-over-content-item color-3">
        <div class="take-over-content-item-number">
          <FormatNumberShow :data="data.orderNum"/>
        </div>
        <div class="take-over-content-item-title">{{ $t('总订单') }}</div>
      </div>
      <div class="take-over-content-item color-4">
        <div class="take-over-content-item-number">
          <FormatNumberShow :data="data.totalProfit" :currency="true"/>
        </div>
        <div class="take-over-content-item-title">{{ $t('总利润') }}</div>
      </div>
    </div>
  </el-card>
</template>

<script>
import FormatNumberShow from "@/components/FormatNumberShow";

export default {
  name: "TakeOver",
  data() {
    return {}
  },
  components: {
    FormatNumberShow
  },
  props: {
    data: {
      type: Object,
      default: {
        goodsNum: 0,
        totalSales: 0,
        orderNum: 0,
        totalProfit: 0
      },
      required: true,
    }
  },
  filters: {
    formatNumber(value = 0) {
      if (value) {
        return (value + '').replace(/\B(?=(\d{3})+(?!\d))/g, ",");
      } else {
        return value
      }
    },
    formatMoney(num = 0) {
      const numStr = num.toString().split('.'); //先转为字符串，再分开整数和小数部分
      let numInt = numStr[0]; // 整数部分
      let numDec = numStr.length > 1 ? '.' + numStr[1] : '.'; // 小数部分，只有原数字存在小数点的时候，分割完长度才会大于1
      while (3 - numDec.length) numDec += '0';  //补0，只有整数的补2个，有一位小数的补1个
      let resultInt = ''; //存储整数部分处理结果
      while (numInt.length > 3) {     //当剩余整数部分长度大于3时继续处理
        resultInt = ',' + numInt.slice(-3) + resultInt;  //把后三位截出来，和处理结果拼在一起，前面加逗号
        numInt = numInt.slice(0, -3); // 剩下的部分是除去刚刚截掉的3位的部分
      }
      return numInt + resultInt + numDec; //结果是“剩余的不足3位的整数”+“处理好的整数结果”+“小数部分”
    }
  },
  methods: {
    formatNumberShow(value, fixed = false) {
      return undefined;
    }
  }
}
</script>

<style lang="scss" scoped>
.take-over {
  width: 100%;
  height: 0;
  background-color: #fff;
  transition: height 1s;
  overflow: hidden;

  &.active {
    height: 190px;
  }

  .take-over-title {
    font-family: 'Roboto';
    font-style: normal;
    font-weight: 400;
    font-size: 16px;
    line-height: 19px;
    height: 19px;
    color: #000000;
    margin-bottom: 12px;
  }

  .take-over-content {
    display: flex;
    justify-content: space-between;

    .take-over-content-item {
      margin-right: 20px;
      flex: 1;
      display: flex;
      justify-content: center;
      align-items: center;
      height: 120px;
      flex-direction: column;
      border-radius: 4px;

      .take-over-content-item-number {
        font-family: 'Roboto';
        font-style: normal;
        font-weight: 600;
        font-size: 26px;
        line-height: 42px;
        color: #FFFFFF;
      }

      .take-over-content-item-title {
        font-family: 'Roboto';
        font-style: normal;
        font-weight: 400;
        font-size: 14px;
        line-height: 16px;
        color: #FFFFFF;
      }

      &:last-child {
        margin-right: 0;
      }

      &.color-1 {
        background-color: #FF8399;
      }

      &.color-2 {
        background-color: #71C3FF;
      }

      &.color-3 {
        background-color: #7190FF;
      }

      &.color-4 {
        background-color: #5AD7CF;
      }
    }
  }
}
</style>
