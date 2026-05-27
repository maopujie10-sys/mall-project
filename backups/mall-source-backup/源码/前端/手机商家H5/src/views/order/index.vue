<template>
  <div id="order" :class="{'is-ar': isArLang}">
    <van-tabs v-model:active="activeName"  @click="tab">
      <van-tab :title="t('total')" name=""></van-tab>
      <van-tab :title="t('待采购')" name="0" :dot="hasNoPushNum"></van-tab>
      <van-tab :title="t('已采购')" name="1"></van-tab>
    </van-tabs>

    <div class="main">
      <div class="seach" style="border-radius: 25px">
        <van-search style="border-radius: 25px" readonly @click="onSearch" v-model="orderId" :placeholder="t('搜索')"/>
      </div>

      <div class="dropdown">
        <div class="dropdownitem one h-10.5" @click="handleShow(1)">
          <div class="p-2.5 bg-white flex justify-between items-center w-full h-full">
            <span class="text-xs">{{ t(title1) }}</span>
            <div class="triangle"></div>
          </div>
        </div>

        <div class="dropdownitem one h-10.5" @click="handleShow(2)">
          <div class="p-2.5 bg-white flex justify-between items-center w-full h-full">
            <span class="text-xs">{{ t(title2) }}</span>
            <div class="triangle"></div>
          </div>
        </div>
      </div>
      <van-popup v-model:show="showCenter" round>
        <div @click="handleChoose(item)"
            class="font-3.5 w-72 h-12 flex justify-center items-center border-bottom relative"
            v-for="(item, index) in option1">
          {{ t(item.text) }}
          <van-icon v-if="item.isCurrent" name="success" class="yes"/>
        </div>
      </van-popup>
      <van-popup v-model:show="showCenter2" round>
        <div @click="handleChoose2(item)"
            class="text-xs w-72 h-12 flex justify-center items-center border-bottom relative"
            :key="index + 'option2'"
            v-for="(item, index) in option2">
          {{ t(item.text) }}
          <van-icon v-if="item.isCurrent" name="success" class="yes"/>
        </div>
      </van-popup>
      <div class="main-list">
        <van-pull-refresh
            v-if="list.length > 0"
            v-model="refreshing"
            @refresh="onRefresh"
            :loading-text="$t('加载中')" :loosing-text="$t('释放以刷新')" :pulling-text="$t('下拉以刷新')">
          <van-list
              :immediate-check="false"
              v-model:loading="loading"
              :loading-text="$t('加载中')"
              :finished="finished"
              :finished-text="$t('noMore')"
              @load="getOrderList">
            <div class="goods">
              <orderItem v-for="item in list" :info="item"/>

            </div>
          </van-list>
        </van-pull-refresh>
        <van-empty v-else :description="$t('noData')"/>
        <div class="safe-area-inset-bottom"></div>
      </div>
    </div>
  </div>
</template>

<script>
import {orderlist} from "@/service/my.api";   //  接口地址
import orderItem from "./orderItem.vue";
import {useI18n} from 'vue-i18n';
import {Toast} from "vant";
import {ref} from "vue";
import {merchantGoodsList} from "@/service/product.api.js";
import { useOrderStore } from "@/store/order.js";
import { arLangCheck } from '@/utils/arLangCheck'
const isArLang = arLangCheck()

export default {
  name: "Order",
  beforeRouteEnter(to, from, next) {
    console.log('beforeRouteEnter')
    next(vm => {
      // 回到原来的位置
      const position = JSON.parse(window.sessionStorage.getItem('position'))
      document.querySelector('.main-list').scrollTop = position
    })
  },
  beforeRouteLeave(to, from, next) {
    // 保存离开页面时的位置
    const position = document.querySelector('.main-list').scrollTop
    window.sessionStorage.setItem('position', JSON.stringify(position))
    next()
  },
  components: {
    orderItem
  },
  data() {
    return {
      loading: false,
      refreshing: false,
      finished: false,
      showCenter: false,
      showCenter2: false,
      t: useI18n().t,
      activeName: '',
      payStatus: "-1",
      showSeach: false,
      list: [],
      option1: [],
      option2: [],
      title1: "",
      title2: "",
      orderId: "",
      purchStatus: "",
      status: "-2",
      pageNum: 1,
      isArLang
    }
  },
  activated() {
  },
  created() {
    const mode = import.meta.env.MODE
    
    window.sessionStorage.setItem('position', JSON.stringify(0))
    this.title1 = "支付状态"
    this.title2 = "物流状态"
    this.option1 = [
      {text: '全部', value: -1, isCurrent: true},
      {text: '未支付', value: 0, isCurrent: false},
      {text: '已支付', value: 1, isCurrent: false},
    ]
    this.option2 = [
      {text: '全部', value: -2, isCurrent: true},
      {text: '订单已取消', value: -1, isCurrent: false}, // 订单已取消
      {text: '等待买家付款', value: 0, isCurrent: false}, // 订单已取消
      {text: '买家已付款', value: 1, isCurrent: false}, // 买家已下单
      {text: '供应商已接单', value: 2, isCurrent: false}, // 供应商已接单
      {text: '物流运输中', value: 3, isCurrent: false}, // 物流已发货
      {text: '买家已签收', value: 4, isCurrent: false}, // 买家已签收
      {text: '订单已完成', value: 5, isCurrent: false}, // 订单已完成
      {text: '已退款', value: 6, isCurrent: false}, // 买家已退款
    ]

    if (['argos'].includes(mode)) {
      this.option2.forEach(item => {
        if (item.value === 4) {
          item.text = '订单已完成'
        }
        if (item.value === 5) {
          item.text = '买家已签收'
        }
      })
    }

    this.onRefresh()

    // 监听未处理订单请求触发
    document.addEventListener('reloadOrderList', () => {
      this.onRefresh()
    }, false)
  },
  computed: {
    hasNoPushNum: () => {
      const orderStore = useOrderStore()
      return Boolean(orderStore.num)
    }
  },
  methods: {
    onLoad() {

    },
    onRefresh() {
      this.init();
      this.getOrderList()
    },
    handleChoose(item) {
      let currentPayStatus = this.payStatus / 1
      let currentIndex = this.option1.findIndex(item2 => item2.value === currentPayStatus)
      this.option1.splice(currentIndex, 1, {...this.option1[currentIndex], isCurrent: false})// 去掉原来的选中
      let index = this.option1.findIndex(item3 => item3.value === item.value)
      this.option1.splice(index, 1, {...this.option1[index], isCurrent: true})// 现在的选中
      this.payStatus = item.value;
      this.title1 = item.text;
      this.showCenter = false;
      this.init();
      this.getOrderList();
    },
    handleChoose2(item) {
      let currentStatus = this.status / 1
      let currentIndex = this.option2.findIndex(item2 => item2.value === currentStatus)
      this.option2.splice(currentIndex, 1, {...this.option2[currentIndex], isCurrent: false})// 去掉原来的选中
      let index = this.option2.findIndex(item3 => item3.value === item.value)
      this.option2.splice(index, 1, {...this.option2[index], isCurrent: true})// 现在的选中
      this.status = item.value;
      this.title2 = item.text;
      this.showCenter2 = false;
      this.init();
      this.getOrderList();
    },
    handleShow(index) {
      if (index === 1) {
        this.showCenter = true;
      } else {
        this.showCenter2 = true;
      }
    },
    init() {  //  初始
      this.pageNum = 1
      this.list = []
      this.loading = false
      this.refreshing = false
      this.finished = false
    },
    getOrderList() {

      const data = {
        orderId: this.orderId,
        payStatus: this.payStatus,
        purchStatus: this.activeName,
        status: this.status,
        begin: "",
        end: "",
        pageNum: this.pageNum,
      }

      Object.keys(data).forEach(key => {
        if (!data[key] && data[key] !== 0) {
          delete data[key];
        }
      })
      if (data.payStatus / 1 === -1) {
        delete data.payStatus
      }
      if (data.status / 1 === -2) {
        delete data.status
      }

      Toast.loading({
        message: this.t('加载中'),
        forbidClick: true,
        duration: 0
      });
      orderlist(data).then((res) => {
        if (this.refreshing) {
          this.refreshing = false
        }
        this.pageNum++
        this.loading = false

        if (res.pageList.length == 0) {
          this.finished = true
        }

        const dataArr = this.list.concat(res.pageList)
        this.list = Number(data.purchStatus) === 0 ? dataArr.filter(item => Number(item.status) !== -1 && Number(item.status) !== 6) : dataArr
      }).catch(err => {
        console.log(err)
      })
    },
    tab(name, title) {  //  标题
      this.activeName = name;
      console.log(this.activeName, 'activeName')
      this.onRefresh()
    },
    onSearch() {  // 搜索
      this.showSeach = true;
      this.$router.push('/order_search')
    },
    change(item) {  //  选择搜索
      this.value = item;
      this.showSeach = false;
    },
    onConfirm2(val) {
      this.title2 = this.option2[val].text;
      this.getOrderList();
    },
  }
}
</script>

<style lang="scss" scoped>
#order {
  width: 100%;
  height: 100vh;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  &.is-ar {
    :deep(.van-field__control) {
      text-align: right;
      padding-right: 10px;
    }
  }
}

.main-list {
  overflow: scroll;
}

.yes {
  color: var(--site-main-color);
  position: absolute;
  right: 30px;
  top: 50%;
  transform: translateY(-50%);
}

.triangle {
  width: 0;
  height: 0;
  border: 6px solid transparent;
  border-top-color: #000;
  position: relative;
  top: 3px;
}

.main {
  padding: 15px;
  box-sizing: border-box;
  height: calc(100vh - 95px);
  display: flex;
  flex-direction: column;
}

.van-search {
  padding: 0px !important;
  border-radius: 5px;
  height: 44px;
}

::v-deep {
  .van-search__content {
    border-radius: 20px;
  }
}

.seach {
  position: relative;

  .seach_list {
    position: absolute;
    top: 35px;
    left: 0px;
    z-index: 999;
    background: #fff;
    width: 100%;
    max-height: 200px;
    overflow-y: scroll;
    padding: 0px 10px;
    box-sizing: border-box;

    div {
      height: 25px;
      line-height: 25px;
    }
  }
}

.dropdown {
  margin: 10px 0px;
  justify-content: space-between;
  display: flex;

  .dropdownitem {
    width: 48%;
    border-radius: 5px;
    overflow: hidden;
  }
}

.cenger {
  display: inline-block;
  width: 50px;
}

.goods {
  height: calc(100% - 190px);
  overflow: auto;
}
</style>
