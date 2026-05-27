<template>
  <el-row :gutter="40" class="panel-group rounded-lg">
    <el-col :lg="6" :sm="12" :xs="12" class="card-panel-col">
      <div class="card-panel" style="background-color: #FF8399;" @click="handleSetLineChartData('newVisitis')">
        <!-- <div class="card-panel-icon-wrapper icon-people">
          <svg-icon icon-class="peoples" class-name="card-panel-icon" />
        </div> -->
        <div class="card-panel-description">
          <count-to :duration="2600" :end-val="data.goodsNum" :start-val="0" class="card-panel-num"/>
          <div class="card-panel-text">{{ $t('商品总量') }}</div>
        </div>
      </div>
    </el-col>
    <el-col :lg="6" :sm="12" :xs="12" class="card-panel-col">
      <div class="card-panel" style="background-color: #71C3FF" @click="handleSetLineChartData('messages')">
        <!-- <div class="card-panel-icon-wrapper icon-message">
          <svg-icon icon-class="message" class-name="card-panel-icon" />
        </div> -->
        <div class="card-panel-description">
          <count-to :duration="3000" :end-val="data.totalSales" :start-val="0" class="card-panel-num"/>
          <div class="card-panel-text">{{ $t('销售总量') }}</div>
        </div>
      </div>
    </el-col>
    <el-col :lg="6" :sm="12" :xs="12" class="card-panel-col">
      <div class="card-panel" style="background-color: #7190FF" @click="handleSetLineChartData('purchases')">
        <!-- <div class="card-panel-icon-wrapper icon-money">
          <svg-icon icon-class="money" class-name="card-panel-icon" />
        </div> -->
        <div class="card-panel-description">
          <count-to :duration="3200" :end-val="data.orderNum" :start-val="0" class="card-panel-num"/>
          <div class="card-panel-text">{{ $t('总订单') }}</div>
        </div>
      </div>
    </el-col>
    <el-col :lg="6" :sm="12" :xs="12" class="card-panel-col">
      <div class="card-panel" style="background-color: #5AD7CF" @click="handleSetLineChartData('shoppings')">
        <!-- <div class="card-panel-icon-wrapper icon-shopping">
          <svg-icon icon-class="shopping" class-name="card-panel-icon" />
        </div> -->
        <div class="card-panel-description">
          <count-to :duration="3600" :end-val="data.totalProfit" :start-val="0" class="card-panel-num"/>
          <div class="card-panel-text">{{ $t('总利润') }}</div>
        </div>
      </div>
      <!--      {{data}}-->
    </el-col>
    <!--    {{data}}-->
  </el-row>
</template>

<script>
import CountTo from "vue-count-to";

export default {
  components: {
    CountTo,
  },
  props: {
    data: {
      //类型不匹配会警告
      type: [Object],
      default: 0,
      required: true,
      // 返回值不是 true,会警告
    }
  },
  data() {
    return {
      goodsCount: this.data.goodsNum,
      saleCount: this.data.totalSales,
      orderCount: this.data.orderNum,
      payCount: this.data.totalProfit,
    };
  },
  methods: {
    handleSetLineChartData(type) {
      this.$emit("handleSetLineChartData", type);
    },
  },
};
</script>

<style lang="scss" scoped>
.panel-group {
  background-color: #fff;
  padding: 20px 0px;
  margin-bottom: 10px;
  margin-right: 0 !important;
  margin-left: 0 !important;

  .card-panel-col {
    // margin-bottom: 32px;
  }

  .card-panel {
    height: 108px;
    cursor: pointer;
    font-size: 12px;
    position: relative;
    overflow: hidden;
    color: #666;
    border-radius: 5px;
    background: #fff;
    box-shadow: 4px 4px 40px rgba(0, 0, 0, 0.05);
    border-color: rgba(0, 0, 0, 0.05);

    &:hover {
      .card-panel-icon-wrapper {
        color: #fff;
      }

      .icon-people {
        background: #40c9c6;
      }

      .icon-message {
        background: #36a3f7;
      }

      .icon-money {
        background: #f4516c;
      }

      .icon-shopping {
        background: #34bfa3;
      }
    }

    .icon-people {
      color: #40c9c6;
    }

    .icon-message {
      color: #36a3f7;
    }

    .icon-money {
      color: #f4516c;
    }

    .icon-shopping {
      color: #34bfa3;
    }

    .card-panel-icon-wrapper {
      float: left;
      margin: 14px 0 0 14px;
      padding: 16px;
      transition: all 0.38s ease-out;
      border-radius: 6px;
    }

    .card-panel-icon {
      float: left;
      font-size: 48px;
    }

    .card-panel-description {
      color: #fff;
      // float: right;
      font-weight: bold;
      margin: 26px 50px;

      .card-panel-text {
        line-height: 18px;
        font-size: 14px;
        margin-top: 12px;
      }

      .card-panel-num {
        font-size: 20px;
      }
    }
  }
}

@media (max-width: 550px) {
  .card-panel-description {
    display: none;
  }

  .card-panel-icon-wrapper {
    float: none !important;
    width: 100%;
    height: 100%;
    margin: 0 !important;

    .svg-icon {
      display: block;
      margin: 14px auto !important;
      float: none !important;
    }
  }
}
</style>
