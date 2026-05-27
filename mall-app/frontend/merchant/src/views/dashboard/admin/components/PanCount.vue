<template>
  <div class="pan-count">
    <el-card class="pan-count__traffic">
      <div class="text">{{ $t('店铺概况') }}</div>
      <div class="list">
        <div class="list-item">
          {{ (data.rating || 0).toFloor(1) }}
          <div class="list-item-text">{{ $t('综合评分') }}</div>
        </div>
        <div class="list-item">
          <FormatNumberShow :data="data.creditScore"/>
          <div class="list-item-text">
            <span>{{ $t('卖家信用分') }}</span>
            <span>
              <i class="el-icon-question"
                 style="cursor: pointer;color: #cccccc;margin-left: 4px;font-size: 16px;position: relative;top: 2px;"
                 @click="intoPage"></i>
            </span>
          </div>
        </div>
        <div class="list-item">
          <FormatNumberShow :data="(data.focusCount)||0"/>
          <div class="list-item-text">{{ $t('店铺关注') }}</div>
        </div>
      </div>
    </el-card>
    <el-card class="pan-count__traffic">
      <div class="text">{{ $t('流量概况') }}</div>
      <div class="list">
        <div class="list-item">
          <FormatNumberShow :data="data.visits1Today"/>
          <div class="list-item-text">{{ $t('今日访客数') }}</div>
        </div>
        <div class="list-item">
          <FormatNumberShow :data="data.visits7Today"/>
          <div class="list-item-text">{{ $t('7日访客数') }}</div>
        </div>
        <div class="list-item">
          <FormatNumberShow :data="data.visits30Today"/>
          <div class="list-item-text">{{ $t('30日访客数') }}</div>
        </div>
      </div>
    </el-card>
    <el-card class="pan-count__traffic">
      <div class="text">{{ $t('今日概况') }}</div>
      <div class="list">
        <div class="list-item">
          <FormatNumberShow :data="data.todayOrder"/>
          <div class="list-item-text">{{ $t('今日订单') }}</div>
        </div>
        <div class="list-item">
          <div>
            <FormatNumberShow :data="data.todaySales" :currency="true"/>
          </div>
          <div class="list-item-text">{{ $t('今日销售额') }}</div>
        </div>
        <div class="list-item">
          <div>
            <FormatNumberShow :data="data.todayProfit" :currency="true"/>
          </div>
          <div class="list-item-text">{{ $t('预计利润') }}</div>
        </div>
      </div>
    </el-card>
  </div>
</template>

<script>
import CountTo from "vue-count-to";
import FormatNumberShow from "@/components/FormatNumberShow";

export default {
  name: "pan-count",
  components: {
    CountTo,
    FormatNumberShow
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
      score: 4.7,
      tNumber: 875,
      sNumber: 3652,
      tNunmber: 1232,
      tOrder: 98,
      sOrder: 62121,
      pOrder: 12312,
    };
  },
  methods: {
    intoPage() {
      //打开新窗口，不显示地址栏
      const BASE_URL = window.location.protocol + "//" + window.location.host + '/'
      window.open(`${BASE_URL}promote/#/shippingPolicy?lang=${this.$store.getters.lang}`);
    }
  }
};
</script>

<style lang="scss" scoped>
.pan-count {
  width: 100%;
  height: 200px;
  display: flex;
  margin-bottom: 10px;
  display: flex;
  justify-content: space-between;

  .pan-count__traffic {
    display: flex;
    justify-content: flex-start;
    flex-direction: column;
    width: 100%;
    background: #FFFFFF;
    margin-right: 12px;

    &:nth-last-child(1) {
      margin-right: 0;
    }

    .list {
      display: flex;
      justify-content: space-between;
      align-items: center;
      width: 100%;

      .text {
        font-family: 'Roboto';
        font-style: normal;
        font-weight: 400;
        font-size: 16px;
        line-height: 19px;
        color: #000000;
      }

      .list-item {
        text-align: center;
        font-family: 'Roboto';
        font-style: normal;
        font-weight: 600;
        font-size: 26px;
        line-height: 47px;
        color: #FFA63E;
        height: 140px;
        width: 33.33%;
        display: flex;
        justify-content: center;
        align-items: center;
        flex-direction: column;

        .list-item-text {
          height: 40px;
          margin-top: 8px;
          font-family: 'Roboto';
          font-style: normal;
          font-weight: 400;
          font-size: 14px;
          line-height: 16px;
          color: #000000;
          padding: 0 6px;
        }
      }
    }
  }


}

@media (max-width: 1550px) {
  .list-item {
    font-size: 24px !important;

    .list-item-text {
      font-size: 14px !important
    }
  }
}

@media (max-width: 1200px) {
  .list-item {
    font-size: 18px !important;

    .list-item-text {
      font-size: 14px !important
    }
  }
}
</style>
