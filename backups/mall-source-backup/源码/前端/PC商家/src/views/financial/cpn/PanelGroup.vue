<template>
  <el-row class="panel-group">
    <el-col class="card-panel-col">
      <div class="card-panel" style="background-color: #779DFF" @click="handleSetLineChartData('newVisitis')">
        <!-- <div class="card-panel-icon-wrapper icon-people">
          <svg-icon icon-class="peoples" class-name="card-panel-icon" />
        </div> -->
        <div class="card-panel-description">
          <FormatNumberShow :data="(saleInfo.n1).toFloor(2)" :currency="true"/>
          <div class="card-panel-text">{{ $t('待到账金额') }}</div>
        </div>
      </div>
    </el-col>
    <el-col class="card-panel-col">
      <div class="card-panel" style="background-color: #71C3FF" @click="handleSetLineChartData('newVisitis')">
        <!-- <div class="card-panel-icon-wrapper icon-people">
          <svg-icon icon-class="peoples" class-name="card-panel-icon" />
        </div> -->
        <div class="card-panel-description">
          <FormatNumberShow :data="(saleInfo.n2).toFloor(2)" :currency="true"/>
          <div class="card-panel-text">{{ $t('总销售额') }}</div>
        </div>
      </div>
    </el-col>
    <el-col class="card-panel-col">
      <div class="card-panel" style="background-color: #5AD7CF" @click="handleSetLineChartData('messages')">
        <div class="card-panel-description">
          <FormatNumberShow :data="(saleInfo.n3).toFloor(2)" :currency="true"/>
          <div class="card-panel-text">{{ $t('总利润') }}</div>
        </div>
      </div>
    </el-col>
    <el-col class="card-panel-col">
      <div class="card-panel" style="background-color: #98A0AE" @click="handleSetLineChartData('purchases')">
        <div class="card-panel-description">
          <FormatNumberShow :data="saleInfo.n4"/>
          <div class="card-panel-text">{{ $t('总订单') }}</div>
        </div>
      </div>
    </el-col>
    <el-col class="card-panel-col">
      <div class="card-panel" style="background-color: #FF7B5E" @click="handleSetLineChartData('shoppings')">
        <div class="card-panel-description">
          <FormatNumberShow :data="saleInfo.n5"/>
          <div class="card-panel-text">{{ $t('取消订单') }}</div>
        </div>
      </div>
    </el-col>
    <el-col class="card-panel-col">
      <div class="card-panel" style="background-color: #EE6060" @click="handleSetLineChartData('shoppings')">
        <!-- <div class="card-panel-icon-wrapper icon-shopping">
          <svg-icon icon-class="shopping" class-name="card-panel-icon" />
        </div> -->
        <div class="card-panel-description">
          <FormatNumberShow :data="saleInfo.n6"/>
          <div class="card-panel-text">{{ $t('退款订单') }}</div>
        </div>
      </div>
    </el-col>
  </el-row>
</template>

<script>
import FormatNumberShow from "@/components/FormatNumberShow";

export default {
  props: {
    saleInfo: {
      type: Object,
      default: () => {
        return {
          n1: 0,
          n2: 0,
          n3: 0,
          n4: 0,
          n5: 0,
          n6: 0,
        }
      },
    },
  },
  components: {
    FormatNumberShow
  },
  data() {
    return {
      goodsCount: 54,
      saleCount: 127361,
      orderCount: 155,
      payCount: 3652,
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
  padding: 10px 0px;
  margin-bottom: 10px;
  margin-right: 0 !important;
  margin-left: 0 !important;
  display: flex;
  flex: 1;
  padding-left: 10px;
  padding-right: 10px;
  border-radius: 8px;

  .card-panel-col {
    // margin-bottom: 32px;
    // display: flex;
    margin: 10px;
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
    display: flex;
    justify-content: center;
    align-items: center;

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
      font-weight: bold;
      font-family: 'Roboto';
      font-style: normal;
      font-weight: 600;
      font-size: 26px;
      line-height: 42px;
      color: #FFFFFF;
      width: 100%;
      text-align: center;

      .card-panel-text {
        line-height: 12px;
        font-size: 14px;
        margin-top: 12px;
        text-align: center;
      }

      .card-panel-num {
        font-size: 20px;
      }
    }
  }
}

@media (max-width: 1550px) {
  .card-panel {
    .card-panel-description {
      font-size: 24px !important;
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
