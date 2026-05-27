<template>
  <div class="dashboard-editor-container">
    <SetBootSteps/>
    <TakeOver :data="head_data"/>
    <PanCount :data="head_data"/>
    <el-card class="rounded-lg">
      <div class="cursor-pointer">
        <span :class="{'active': selectCurrent === 0}" class="date-item" @click="changeChart(0)">{{ $t('今日') }}</span>
        <span :class="{'active': selectCurrent === 1}" class="date-item mx-10" @click="changeChart(1)">
                                      {{ $t('近7天') }}
                                    </span>
        <span :class="{'active': selectCurrent === 2}" class="date-item" @click="changeChart(2)">
                                      {{ $t('近30天') }}
                                    </span>
      </div>
      <line-chart :chart-data="line_data" style="top: 10px"/>
    </el-card>
    <div :class="categoryList.length > 0?'category active':'category'">
      <div class="category-title">
        <span>{{ $t('您的类别') }}</span>
        <span>（{{ categoryList.length }}）</span>
      </div>
      <div ref="categoryContent" class="category-content">
        <div v-for="(item , index) in categoryList" class="category-content-item" @click="intoGoodsList(item)">
          <div class="category-content-item-title">
            <div class="category-content-item-title-text">{{ item.name }}</div>
            <div class="category-content-item-title-text">（{{ item.goodCount }}）</div>
          </div>
          <div class="category-content-item-content">
            <el-image :src="item.iconImg" class="category-content-item-content-img" fit="cover"></el-image>
          </div>
        </div>
        <div ref="rectangle" class="rectangle">
          <div class="rectangle-icon left-rectangle" @click="changeScroll('left')">
            <img src="../../../assets/images/rectangle.png"/>
          </div>
          <div class="rectangle-icon right-rectangle" @click="changeScroll('right')">
            <img src="../../../assets/images/rectangle.png"/>
          </div>
        </div>
      </div>
    </div>

    <el-row :gutter="8">
      <el-col :lg="{ span: 18 }" :md="{ span: 24 }" :sm="{ span: 24 }" :xl="{ span: 18 }" :xs="{ span: 24 }"
              style="padding-right: 8px; margin-bottom: 30px">
        <transaction-table :transactionData="goods_data"/>
      </el-col>
      <el-col :lg="{ span: 6 }" :md="{ span: 12 }" :sm="{ span: 12 }" :xl="{ span: 6 }" :xs="{ span: 24 }"
              style="margin-bottom: 30px">
        <OrderSet :data="instrument_panel_stats_data"/>
      </el-col>
    </el-row>
  </div>
</template>

<script>
import GithubCorner from "@/components/GithubCorner";
import TakeOver from "./components/TakeOver";
import PanelGroup from "./components/PanelGroup";
import PanCount from "./components/PanCount";
import LineChart from "./components/LineChart";
import RaddarChart from "./components/RaddarChart";
import PieChart from "./components/PieChart";
import BarChart from "./components/BarChart";
import TransactionTable from "./components/TransactionTable";
import TodoList from "./components/TodoList";
import BoxCard from "./components/BoxCard";
import OrderSet from "./components/OrderSet";
import {fenlei_post, goods, head, instrument_panel_stats, line, seller_info_action_post} from "@/api/user";

const oneLineChartData = {
  newVisitis: {
    commData: ["11.01"],
    expectedData: [100],
    actualData: [120],
  },
  messages: {
    commData: ["11.01"],
    expectedData: [200],
    actualData: [120],
  },
  purchases: {
    commData: ["11.01"],
    expectedData: [80],
    actualData: [120],
  },
  shoppings: {
    commData: ["11.01"],
    expectedData: [129],
    actualData: [120],
  },
};
const lineChartData = {
  newVisitis: {
    commData: ["11.01", "11.02", "11.03", "11.04", "11.05", "11.06", "11.07"],
    expectedData: [100, 120, 161, 134, 105, 160, 165],
    actualData: [120, 82, 91, 154, 162, 140, 145],
  },
  messages: {
    commData: ["11.01", "11.02", "11.03", "11.04", "11.05", "11.06", "11.07"],
    expectedData: [200, 192, 120, 144, 160, 130, 140],
    actualData: [180, 160, 151, 106, 145, 150, 130],
  },
  purchases: {
    commData: ["11.01", "11.02", "11.03", "11.04", "11.05", "11.06", "11.07"],
    expectedData: [80, 100, 121, 104, 105, 90, 100],
    actualData: [120, 90, 100, 138, 142, 130, 130],
  },
  shoppings: {
    commData: ["11.01", "11.02", "11.03", "11.04", "11.05", "11.06", "11.07"],
    expectedData: [130, 140, 141, 142, 145, 150, 160],
    actualData: [120, 82, 91, 154, 162, 140, 130],
  },
};

const TLineChartData = {
  newVisitis: {
    commData: [
      "11.01",
      "11.02",
      "11.03",
      "11.04",
      "11.05",
      "11.06",
      "11.07",
      "11.01",
      "11.02",
      "11.03",
      "11.04",
      "11.05",
      "11.06",
      "11.07",
      "11.01",
      "11.02",
      "11.03",
      "11.04",
      "11.05",
      "11.06",
      "11.07",
    ],
    expectedData: [
      130, 140, 141, 142, 145, 150, 160, 130, 140, 141, 142, 145, 150, 160, 130,
      140, 141, 142, 145, 150, 160, 130, 140, 141, 142, 145, 150, 160,
    ],
    actualData: [
      120, 82, 91, 154, 162, 140, 145, 120, 82, 91, 154, 162, 140, 145, 120, 82,
      91, 154, 162, 140, 145, 120, 82, 91, 154, 162, 140, 145,
    ],
  },
};

export default {
  name: "DashboardAdmin",
  components: {
    TakeOver,
    GithubCorner,
    PanelGroup,
    LineChart,
    PanCount,
    RaddarChart,
    PieChart,
    BarChart,
    TransactionTable,
    TodoList,
    BoxCard,
    OrderSet,
  },
  data() {
    return {
      testImg: require("@/assets/images/test.jpg"),
      categoryList: [],
      lineChartData: lineChartData.newVisitis,
      TLineChartData: TLineChartData,
      oneLineChartData: oneLineChartData,
      SLineChartData: lineChartData,
      selectCurrent: 0,
      line_data: {
        commData: [],
        expectedData: [],
        actualData: [],
      },
      goods_data: [],
      instrument_panel_stats_data: {},
      head_data: {},
      info: {},
      fenlei: {}
    };
  },
  computed: {
    messageNumber() {
      return this.$store.getters.messageNumber
    }
  },
  created() {
    // this.line_post()
    this.goods_post()
    this.seller_info_action()
  },
  mounted() {
    this.$watch("messageNumber", (newVal, oldVal) => {
      if (newVal - 0 > oldVal - 0) {//有新消息
        this.head_post();
      }
    })
  },
  methods: {
    intoGoodsList(item) {
      console.log(item)
      this.$router.push({
        path: "/shopList/merchandise",
        query: {
          categoryId: item.categoryId,
        },
      });
    },
    changeScroll(type = 'left') {
      if (type === 'left') {
        let index = 45
        let interval = setInterval(() => {
          this.$refs.categoryContent.scrollLeft -= 4;
          index--
          if (index <= 0) clearInterval(interval)
        }, 10)
      } else {
        let index = 45
        let interval = setInterval(() => {
          this.$refs.categoryContent.scrollLeft += 4;
          index--
          if (index <= 0) clearInterval(interval)
        }, 10)
      }

    },
    tz() {
      this.$router.push('/shopList/merchandise')
    },
    getCategory() {
      fenlei_post({sellerId: this.info.id}).then((e) => {
        console.log(e)
        this.categoryList = e.data
      }).catch((e) => {
      })
    },

    seller_info_action() {
      seller_info_action_post({}).then((e) => {
        console.log(e)
        this.info = e.data
        this.head_post()
        this.getCategory()
        this.instrument_panel_stats_post()
        this.line_post()
      }).catch((e) => {
      })
    },
    instrument_panel_stats_post() {
      instrument_panel_stats({sellerId: this.info.id}).then((e) => {
        console.log(e)
        this.instrument_panel_stats_data = e.data.stats
      }).catch((e) => {
      })
    },
    goods_post() {
      goods({}).then((e) => {
        this.goods_data = e.data?.goods || []
      }).catch((e) => {
      })
    },
    line_post() {
      line({type: this.selectCurrent, sellerId: this.info.id}).then((e) => {
        console.log('line', e, e.data.line.length)
        this.line_data = {
          commData: [],
          expectedData: [],
          actualData: [],
        }
        for (let i = 0; i < e.data.line.length; i++) {
          // console.log('line',this.line_data,e.data.line[i]['dayString'])
          this.line_data['commData'].push(e.data.line[i]['dayString'])
          this.line_data['expectedData'].push(e.data.line[i]['countSales'])
          this.line_data['actualData'].push(e.data.line[i]['countVisits'])
        }
        // this.line_data['commData'] = 1
        console.log('line', this.line_data)
      }).catch((e) => {
      })
    },
    head_post() {
      head({sellerId: this.info.id}).then((e) => {
        console.log(e)
        this.head_data = e.data.head
      }).catch((e) => {
      })
    },
    handleSetLineChartData(type) {
      // this.lineChartData = lineChartData[type];
    },
    // TODO: 折线图数据改变事件
    changeChart(num) {
      this.selectCurrent = num;
      this.line_post()
      console.log(num);
      if (num == 1) {
        this.lineChartData = this.oneLineChartData["newVisitis"];
      } else if (num == 7) {
        this.lineChartData = this.SLineChartData["newVisitis"];
      } else {
        this.lineChartData = this.TLineChartData["newVisitis"];
      }
    },
  },
};
</script>

<style lang="scss" scoped>
.rounded-lg {
  position: relative;
}

.cursor-pointer {
  position: absolute;
  right: 20px;
  z-index: 10;
}

.category {
  position: relative;
  display: flex;
  justify-content: flex-start;
  flex-direction: column;
  height: 0px;
  margin: 0;
  user-select: none;
  transition: height 500ms, margin 500ms, opacity 500ms;
  overflow: hidden;

  &.active {
    height: 234px;
    margin: 10px 0 32px 0;
  }

  .category-title {
    font-family: 'Roboto';
    font-style: normal;
    font-weight: 400;
    font-size: 16px;
    line-height: 16px;
    color: #333333;
    margin-bottom: 24px;
  }

  .category-content {
    width: 100%;
    height: 188px;
    overflow-y: hidden;
    overflow-x: auto;
    display: flex;

    .category-content-item {
      position: relative;
      width: 160px;
      height: 188px;
      border-radius: 4px;
      overflow: hidden;
      flex-shrink: 0;
      margin-right: 20px;
      transition: 500ms;

      &:nth-last-child(2) {
        margin-right: 0;
      }

      .category-content-item-title {
        position: absolute;
        left: 0;
        top: 0;
        width: 100%;
        height: 100%;
        display: flex;
        justify-content: center;
        items-align: center;
        flex-direction: column;
        background-color: rgba(0, 0, 0, 0.5);
        z-index: 11;

        .category-content-item-title-text {
          font-family: 'Roboto';
          font-style: normal;
          font-weight: 400;
          font-size: 12px;
          line-height: 14px;
          text-align: center;
          letter-spacing: -0.3px;
          color: #FFFFFF;
        }
      }

      .category-content-item-content {
        width: 160px;
        height: 188px;
        position: absolute;
        left: 0;
        top: 0;
        z-index: 10;

        .category-content-item-content-img {
          width: 100%;
          height: 100%;
        }
      }
    }

    &:hover .rectangle .rectangle-icon {
      opacity: 1;
    }

    .rectangle {
      position: absolute;
      left: 0;
      top: 0;
      width: 100%;
      height: 100%;
      padding: 110px 2px 0 2px;
      box-sizing: border-box;

      .rectangle-icon {
        opacity: 0;
        cursor: pointer;
        position: absolute;
        width: 40px;
        height: 40px;
        border-radius: 50%;
        background-color: rgba(0, 0, 0, 0.5);
        display: flex;
        justify-content: center;
        align-items: center;
        z-index: 12;
        transition: opacity 500ms;

        img {
          width: 16px;
          height: 16px;
          position: relative;
          left: 2px;
        }

        &.left-rectangle {
          position: absolute;
          left: 0;
        }

        &.right-rectangle {
          //  旋转180度
          transform: rotate(180deg);
          position: absolute;
          right: 0;
        }
      }
    }
  }

}

.dashboard-editor-container {
  padding: 20px;
  background-color: rgb(240, 242, 245);
  position: relative;
  overflow: scroll;

  .github-corner {
    position: absolute;
    top: 0px;
    border: 0;
    right: 0;
  }

  .chart-wrapper {
    background: #fff;
    padding: 16px 16px 0;
    margin-bottom: 32px;
  }
}

.date-item {
  border: 1px solid #aaa;
  padding: 4px 10px;
  display: inline-block;
  background-color: #fff;
  color: #aaa;
  border-radius: 5px;
  font-size: 12px;
  height: 24px;
  line-height: 14px;


  &.active {
    border-color: #1552f0;
    color: #1552f0;
  }
}

@media (max-width: 1024px) {
  .chart-wrapper {
    padding: 8px;
  }
}
</style>
