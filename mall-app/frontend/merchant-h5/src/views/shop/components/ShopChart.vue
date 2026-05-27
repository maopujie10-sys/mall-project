<template>
  <div class="shop-chart">
    <div class="dashbord-content" :class="{'is-ar': isArLang}">
      <div class="legend">
        <div v-for="item in legendData" :key="item.name" class="item">
          <div :style="{ 'background-color': item.color }"></div>
          <p>{{ t(item.name) }}</p>
        </div>
      </div>
      <div class="days">
        <div
          v-for="(item, index) in daysData"
          :key="item"
          :class="{ active: index === current }"
          class="item"
          @click="daysChange(index)"
        >
          {{ t(item) }}
        </div>
      </div>
    </div>
    <div v-if="chartLoading" class="chart-content loading">
      <van-loading :color="themeColor[colorMode]" />
    </div>
    <div v-if="sellerId" class="chart-content" ref="chartRef"></div>
    <div v-else class="chart-content">
      <van-empty :image="empytImg.href" :description="t('noData')" />
    </div>
  </div>
</template>

<script>
import { defineComponent, ref, toRefs } from 'vue'
import * as echarts from 'echarts'
import { useI18n } from 'vue-i18n'
import { themeColor, needChangeMode } from '@/config'
import { arLangCheck } from '@/utils/arLangCheck'
import { sellerInstrumentPanelLine } from '@/service/shop.api.js'
export default defineComponent({
  name: 'ShopChart',
  props: {
    sellerId: {
      type: String,
      default: ''
    }
  },
  setup(props) {
    const modeType = import.meta.env.MODE
    const colorMode = needChangeMode.includes(modeType) ? modeType : 'main'


    const { t } = useI18n()
    const { sellerId } = toRefs(props)
    const empytImg = new URL('@/assets/image/public/no_data.png', import.meta.url)

    const isArLang = arLangCheck()

    const legendData = [
      {
        name: 'sales',
        color: themeColor[colorMode]
      },
      {
        name: 'browse',
        color: '#9B9B9B'
      }
    ]

    const chartLoading = ref(false)
    const daysData = ref(['today', 'today7', 'today30'])
    const current = ref(0)
    const chartRef = ref()

    const getChartData = () => {
      if (!sellerId.value) {
        return false
      }
      chartLoading.value = true
      const params = {
        type: current.value,
        sellerId: sellerId.value
      }
      sellerInstrumentPanelLine(params)
        .then((res) => {
          const data = res.line || []
          // const dataArr = data.reverse()
          const dataArr = data
          const dateData = []
          const saleData = []
          const browseData = []
          dataArr.forEach((item) => {
            dateData.push(item.dayString.slice(item.dayString.indexOf('-') + 1))
            saleData.push(item.countSales)
            browseData.push(item.countVisits)
          })

          drawLine(dateData, saleData, browseData)
          chartLoading.value = false
        })
        .catch(() => {
          chartLoading.value = false
        })
    }

    const daysChange = (index) => {
      if (index !== current.value) {
        current.value = index
        getChartData()
      }
    }

    const drawLine = (date, sale, browse) => {
      const chartObj = echarts.init(chartRef.value)
      const option = {
        tooltip: {
          trigger: 'axis',
          axisPointer: {
            type: 'cross',
            label: {
              backgroundColor: '#6a7985'
            }
          }
        },
        grid: {
          left: '14%',
          top: 10,
          right: 10,
          bottom: 30
        },
        color: [themeColor[colorMode], '#9B9B9B'],
        xAxis: {
          type: 'category',
          boundaryGap: false,
          axisLine: {
            show: true,
            lineStyle: {
              type: 'dashed',
              color: '#ccc'
            }
          },
          axisTick: {
            show: false
          },
          axisLabel: {
            textStyle: {
              color: '#333'
            }
          },
          splitLine: {
            show: true,
            lineStyle: {
              type: 'dashed',
              color: '#ccc'
            }
          },
          data: date
        },
        yAxis: {
          type: 'value',
          minInterval: 1,
          axisLabel: {
            textStyle: {
              color: '#333'
            }
          },
          splitLine: {
            lineStyle: {
              type: 'dashed',
              color: '#ccc'
            }
          }
        },
        series: [
          {
            name: t('sales'),
            type: 'line',
            areaStyle: {
              color: 'rgba(21, 82, 240, 0.2)'
            },
            data: sale
          },
          {
            name: t('browse'),
            type: 'line',
            areaStyle: {
              color: 'rgba(155, 155, 155, 0.2)'
            },
            data: browse
          }
        ]
      }
      chartObj.setOption(option, true)
    }

    return {
      t,
      legendData,
      daysData,
      current,
      chartRef,
      chartLoading,
      sellerId,
      empytImg,
      isArLang,
      themeColor,
      colorMode,
      daysChange,
      getChartData
    }
  }
})
</script>

<style lang="scss" scoped>
.shop-chart {
  background-color: #fff;
  border-radius: 4px;
  margin-bottom: 15px;
  padding: 12px 15px;
  > .dashbord-content {
    display: flex;
    align-items: center;
    justify-content: space-between;
    &.is-ar {
      > .legend > .item {
        &:first-child {
          margin-left: 14px;
          margin-right: 0;
        }
        > div {
          margin-right: 0;
          margin-left: 8px;
        }
      }
      > .days > .item {
        margin-right: 0;
        margin-left: 6px;
        &:last-child {
          margin-left: 0;
        }
      }
    }
    > .legend {
      display: flex;
      align-items: center;
      > .item {
        display: flex;
        align-items: center;
        &:first-child {
          margin-right: 14px;
        }
        > div {
          width: 18px;
          height: 6px;
          border-radius: 12px;
          margin-right: 8px;
        }
        > p {
          color: #333;
          font-size: 12px;
        }
      }
    }
    > .days {
      display: flex;
      align-items: center;
      > .item {
        width: 46px;
        height: 22px;
        border-radius: 2px;
        background-color: #f6f6f6;
        color: #999;
        margin-right: 6px;
        font-size: 10px;
        text-align: center;
        line-height: 22px;
        &:last-child {
          margin-right: 0;
        }
        &.active {
          color: #fff;
          background-color: var(--site-main-color);
        }
      }
    }
  }
  > .chart-content {
    width: 100%;
    height: 190px;
    margin-top: 15px;
    &.loading {
      position: absolute;
      display: flex;
      align-items: center;
      justify-content: center;
      left: 0;
      pointer-events: none;
    }
    .van-empty {
      padding: 0 !important;
    }
  }
}
</style>
