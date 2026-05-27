<template>
  <div class="order-set">
    <el-card class="order">
      <div class="text">{{ $t('订单统计') }}</div>
      <div class="list">
        <div class="list-item">
          <count-to :duration="3000" :end-val="data.orderNum" :start-val="0" class="card-panel-num"/>
          <div>{{ $t('总订单') }}</div>
        </div>
        <div class="list-item">
          <count-to :duration="3000" :end-val="data.orderIng" :start-val="0" class="card-panel-num"/>
          <div>{{ $t('进行中') }}</div>
        </div>
        <div class="list-item">
          <count-to :duration="3000" :end-val="data.orderFinish" :start-val="0" class="card-panel-num"/>
          <div>{{ $t('已完成') }}</div>
        </div>
        <div class="list-item">
          <count-to :duration="3000" :end-val="data.orderCancel" :start-val="0" class="card-panel-num"/>
          <div>{{ $t('取消订单') }}</div>
        </div>
      </div>
    </el-card>
    <el-card class="set">
      <div v-if='merchantInfo.sellerKycFlag === "1"'
           style="display: flex;justify-content: center;align-items: center;width: 100%;height: 180px">
        <img :src="sellerKycImage" style="width: 142px;height: 142px;"/>
      </div>
      <div v-else>
        <div class="text">{{ $t('店铺设置') }}</div>
        <div class="main">
          <p style="line-height: 60px">{{ $t('管理和设置您的店铺') }}</p>
          <el-button style="background: #1552F0; border: 1px solid #1552F0;margin-bottom: 24px;"
                     @click="intoShopSetting">
            {{ $t('立即设置') }}
          </el-button>
        </div>
      </div>
    </el-card>
  </div>
</template>

<script>
import CountTo from "vue-count-to";

export default {
  name: "order-set",
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
  computed: {
    merchantInfo() {
      return this.$store.getters.merchantInfo
    }
  },
  data() {
    return {
      sellerKycImage: require("@/assets/image/auth/sellerKyc.png"),
    };
  },
  methods: {
    intoShopSetting() {
      this.$router.push({path: "/other/shopSetting"});
    }
  }
};
</script>

<style lang="scss" scoped>
.order-set {
  width: 100%;

  .order {
    height: 340px;
    width: 100%;
    background-color: #fff;

    .list {
      display: flex;
      flex: 1;
      flex-wrap: wrap;
      margin-top: 20px;

      &-item {
        width: 50%;
        text-align: center;
        padding-bottom: 30px;
      }
    }
  }

  .set {
    height: 220px;
    width: 100%;
    background-color: #fff;

    .main {
      text-align: center;

      ::v-deep .el-button {
        background-color: #e99d42;
        color: #fff;
      }
    }
  }

  .text {
    color: #333;
    font-size: 18px;
    font-weight: 500;
    margin-bottom: 36px
  }

  .card-panel-num {
    color: #e99d42;
    font-weight: 700;
    font-size: 20px;
    line-height: 60px;
  }
}
</style>
