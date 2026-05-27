<template>
  <div class="table-list">
    <div class="search">
      <el-form ref="searchForm" :model="form" inline>
        <el-form-item :label="$t('订单编号')" prop="order_no">
          <el-input v-model="form.order_no"></el-input>
        </el-form-item>
        <el-form-item :label="$t('支付状态')" prop="order_status">
          <el-select v-model="form.order_status" :placeholder="$t('请选择')">
            <el-option v-for="item in order_options" :key="item.value" :label="item.label" :value="item.value">
            </el-option>
          </el-select>
        </el-form-item>
        <el-form-item :label="$t('物流状态')" prop="goods_status">
          <el-select v-model="form.goods_status" :placeholder="$t('请选择')">
            <el-option v-for="item in goods_options" :key="item.value" :label="item.label" :value="item.value">
            </el-option>
          </el-select>
        </el-form-item>
        <el-form-item :label="$t('下单时间')" prop="time">
          <el-date-picker v-model="form.time" :end-placeholder="$t('结束日期')"
                          :range-separator="$t('至')" :start-placeholder="$t('开始日期')" type="datetimerange">
          </el-date-picker>
        </el-form-item>
        <div class="btnList">
          <el-form-item>
            <el-button type="primary" @click="search">{{ $t('查询') }}</el-button>
          </el-form-item>
          <el-form-item>
            <el-button @click="reset">{{ $t('重置') }}</el-button>
          </el-form-item>
        </div>
      </el-form>
    </div>
    <div class="table">
      <el-button type="primary" @click="bulkPurchases" style="margin-bottom: 6px" :disabled="bulkPurchasesStates">
        {{ $t('批量采购') }}
      </el-button>
      <el-table :data="data.pageList" border stripe style="width: 100%;" @selection-change="selectionChange"
                ref="table">
        <el-table-column type="selection" width="55" align="center"></el-table-column>
        <el-table-column :label="$t('订单编号')" align="center" prop="id"></el-table-column>
        <el-table-column :label="$t('收货人姓名')" align="center" prop="contacts">
          <template slot-scope="scope">
            <div>{{ scope.row.contacts | formatContacts }}</div>
          </template>
        </el-table-column>
        <el-table-column :label="$t('商品金额')" align="center" prop="pay_price">
          <template slot-scope="scope">
            <FormatNumberShow :data=" scope.row.prizeReal" :currency="true"/>
            <!--            <div>${{ (scope.row.prizeReal || 0).toFloor(2) }}</div>-->
          </template>
        </el-table-column>
        <el-table-column :label="$t('利润')" align="center" prop="get_price">
          <template slot-scope="scope">
            <FormatNumberShow :data=" scope.row.profit" :currency="true"/>
            <!--            <div>${{ (scope.row.profit || 0).toFloor(2) }}</div>-->
          </template>
        </el-table-column>
        <el-table-column :label="$t('支付状态')" align="center" prop="pay_status">
          <template slot-scope="scope">
            <span v-if="scope.row.payStatus == 0">{{ $t('未支付') }}</span>
            <span v-if="scope.row.payStatus == 1">{{ $t('已支付') }}</span>
          </template>
        </el-table-column>
        <el-table-column :label="$t('采购状态')" align="center" prop="buy_status">
          <template slot-scope="scope">
            <el-tag v-if="parseInt(scope.row.purchStatus) === 0" type="danger">{{ $t('待采购') }}</el-tag>
            <el-tag v-else type="">{{ $t('已采购') }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column :label="$t('物流状态')" align="center" prop="good_status">
          <template slot-scope="scope">
            <div style="width: 100%;">
              <span>{{ getOrderStatus(scope.row.status) }}</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column :label="$t('下单时间')" align="center" prop="createTime">
        </el-table-column>
        <el-table-column :label="$t('操作')" align="center" :width="columnWidth">
          <template slot-scope="scope">
            <div style="position: relative;padding: 4px;box-sizing: border-box;">
              <el-dropdown size="small" split-button type="primary" @command="handleCommand($event,scope)"
                           trigger="click"
              >
                {{ $t('操作') }}
                <el-dropdown-menu slot="dropdown">
                  <el-dropdown-item @click="openOrder(scope.row)" command="a">
                    {{ $t('查看订单') }}
                  </el-dropdown-item>
                  <el-dropdown-item command="b"
                                    v-if="(scope.row.purchStatus == 0)&&scope.row.payStatus == 1&&scope.row.status===1"
                                    size="mini"
                                    @click="addGood(scope.row)">
                    {{ $t('采购') }}
                  </el-dropdown-item>
                  <el-dropdown-item command="c" v-else-if="[2,3,4,5].includes(scope.row.status)"
                                    @click="getLogisticsInfo(scope.row)">
                    {{ $t('物流信息') }}
                  </el-dropdown-item>
                </el-dropdown-menu>
              </el-dropdown>
              <div v-if="(scope.row.purchStatus == 0)&&scope.row.payStatus == 1&&scope.row.status===1"
                   style="position: absolute;right: 5px;top: 3px;width: 6px;height: 6px;border-radius: 50%;background-color: red;z-index: 999"></div>
            </div>
          </template>
        </el-table-column>
      </el-table>
    </div>
    <el-dialog :title="$t('采购确定')" :visible.sync="bugDialogVisible" width="560px">
      <div class="detail">
        <div class="header">{{ $t('订单详情') }}</div>
        <div class="main">
          <el-table :data="detailData" max-height="250px">
            <el-table-column :label="$t('封面图')">
              <template slot-scope="{row}">
                <el-image :alt="row.goodsName" :preview-src-list="[row.goodsIcon]" :src="row.goodsIcon"
                          fit="contain" style="width: 50px; height: 50px"/>
              </template>
            </el-table-column>
            <el-table-column :label="$t('产品名称')" prop="goodsName" show-overflow-tooltip></el-table-column>
            <el-table-column :label="$t('数量')" prop="goodsNum"></el-table-column>
            <el-table-column :label="$t('单价')" prop="goodsReal">
              <template slot-scope="{row}">
                <!--                <div>${{ (row.goodsReal || 0).toFloor(2) }}</div>-->
                <FormatNumberShow :data="row.goodsReal" :currency="true"/>
              </template>
            </el-table-column>
          </el-table>
        </div>
      </div>
      <div class="detail">
        <div class="header">{{ $t('采购') }}</div>
        <div class="main-price">
          <div class="item">
            <div class="name">{{ $t('买家付款') }}</div>
            <!--            <div class="price">${{ (buyDetail.systemPrice || 0).toFloor(2) }}</div>-->
            <FormatNumberShow :data="buyDetail.prizeReal" :currency="true"/>
          </div>
          <div class="item">
            <div class="name">{{ $t('采购金额') }}</div>
            <!--            <div class="price">${{ (buyDetail.systemPrice || 0).toFloor(2) }}</div>-->
            <div style="text-align: right;" v-if="!defaultSettings.hideSellerLevel">
              <FormatNumberShow :data="buyDetail.systemPrice" :currency="true"/>
              <div v-if="buyDetail.sellerDiscountPrice">{{ $t('优惠价') }}
                <FormatNumberShow :data="buyDetail.sellerDiscountPrice" :currency="true" style="color: #F56C6C"/>
                ，{{ $t("采购优惠") }}<span style="color: #F56C6C">{{
                    buyDetail.sellerDiscount * 100
                  }}%</span></div>
            </div>
          </div>

          <!--          <div class="item">-->
          <!--            <div class="name">{{ $t('销售金额') }}</div>-->
          <!--            <div class="price">${{ (buyDetail.prizeOriginal || 0).toFloor(2) }}</div>-->
          <!--          </div>-->
          <div class="item">
            <div class="name">{{ $t('采购数量') }}</div>
            <div class="price">{{ buyDetail.goodsCount }}</div>
          </div>
          <div class="item">
            <div class="name">{{ $t('利润') }}</div>
            <FormatNumberShow :data="buyDetail.profit" :currency="true"/>
            <!--            <div class="price">${{ (buyDetail.profit || 0).toFloor(2) }}</div>-->
          </div>
          <!--          <div class="item top">-->
          <!--            <div class="name">{{ $t('合计') }}</div>-->
          <!--            <FormatNumberShow :data="buyDetail.prizeReal" :currency="true"/>-->
          <!--            &lt;!&ndash;            <div class="price">${{ (buyDetail.prizeReal || 0).toFloor(2) }}</div>&ndash;&gt;-->
          <!--          </div>-->
        </div>
      </div>
      <div class="btn">
        <el-button @click="onSubmit" type="primary">{{ $t('确定支付') }}</el-button>
      </div>
    </el-dialog>
    <el-dialog :title="$t('订单编号')+`:${orderInfo.id}`" :visible.sync="orderDialogVisible" top="30px" width="800px">
      <div class="order-top">
        <div class="header">{{ $t('订单摘要') }}</div>
        <div class="main">
          <div class="main-content">
            <div class="left">
              <div class="item">
                <div>{{ $t('订单号') }}</div>
                <div>{{ orderInfo.id }}</div>
              </div>
              <div class="item">
                <div>{{ $t('付款方式') }}</div>
                <div>USDT</div>
              </div>

              <div class="item">
                <div>{{ $t('采购状态') }}</div>
                <div>
                            <span v-if="parseInt(orderInfo.purchStatus) === 0" :style="{color: '#fff',
                              padding: '2px 5px',
                              'background-color': 'red',
                            }">{{ $t('待采购') }}</span>
                  <span v-else :style="{color: '#fff',
                              padding: '2px 5px',
                              'background-color':
                                '#42b983' ,
                            }">{{ $t('已采购') }}</span>
                </div>
              </div>
              <div class="item">
                <div>{{ $t('采购金额') }}</div>
                <FormatNumberShow :data="orderInfo.systemPrice" :currency="true"/>
                <!--                <div>${{ (orderInfo.systemPrice || 0).toFloor(2) }}</div>-->
              </div>
              <div class="item">
                <div>{{ $t('采购时间') }}</div>
                <div>{{ orderInfo.pushTime | formatZoneDate }}</div>
              </div>
              <div class="item">
                <div>{{ $t('利润') }}</div>
                <FormatNumberShow :data="orderInfo.profit" :currency="true"/>
                <!--                <div>${{ (orderInfo.profit || 0).toFloor(2) }}</div>-->
              </div>
            </div>
            <div class="right">
              <div class="item">
                <div>{{ $t('下单时间') }}</div>
                <div>{{ orderInfo.createTime | formatZoneDate }}</div>
              </div>
              <div class="item">
                <div>{{ $t('支付状态') }}</div>
                <div v-if="orderInfo.payStatus == 0">{{ $t('未支付') }}</div>
                <div v-if="orderInfo.payStatus == 1">{{ $t('已支付') }}</div>
              </div>
              <div class="item">
                <div>{{ $t('物流状态') }}</div>
                <div>{{ getOrderStatus(orderInfo.status) }}</div>
              </div>
              <div class="item">
                <div>{{ $t('销售金额') }}</div>
                <FormatNumberShow :data="orderInfo.prizeReal" :currency="true"/>
                <!--                <div>${{ (orderInfo.prizeReal || 0).toFloor(2) }}</div>-->
              </div>

            </div>
          </div>
          <div class="main-content border">
            <div class="left">
              <div class="item">
                <div>{{ $t('姓名') }}</div>
                <div style="position: relative">
                  <div>{{ orderInfo.contacts }}</div>
                  <div class="contacts-icon" @click="contactsUser">
                    <img :src="contactsIcon"/>
                  </div>
                </div>

              </div>
              <div class="item">
                <div>{{ $t('地址') }}</div>
                <div>{{ orderInfo.address }}</div>
              </div>
              <div class="item">
                <div>{{ $t('国家') }}</div>
                <div>{{ getCountry(orderInfo.country) }}</div>
              </div>
              <div class="item">
                <div>{{ $t('城市') }}</div>
                <div>{{ getCity(orderInfo.city) }}</div>
              </div>
            </div>
            <div class="right">
              <div class="item">
                <div>{{ $t('邮箱') }}</div>
                <div>{{ orderInfo.email }}</div>
              </div>
              <div class="item">
                <div>{{ $t('电话') }}</div>
                <div>{{ orderInfo.phone }}</div>
              </div>
              <div class="item">
                <div>{{ $t('省区') }}</div>
                <div>{{ getState(orderInfo.province) }}</div>
              </div>
              <div class="item">
                <div>{{ $t('邮编') }}</div>
                <div>{{ orderInfo.postcode }}</div>
              </div>
            </div>
          </div>
        </div>
      </div>
      <div class="order-bottom">
        <div class="content-left">
          <div class="header">{{ $t('订单详情') }}</div>
          <div class="main">
            <el-table :data="detailData" max-height="250px">
              <el-table-column :label="$t('查看图片')">
                <template slot-scope="scope">
                  <el-image
                      style="width: 36px; height: 36px"
                      :src="scope.row.goodsIcon"
                      :preview-src-list="[scope.row.goodsIcon]">
                  </el-image>
                </template>
              </el-table-column>
              <el-table-column :label="$t('产品编号')" prop="goodsId" width="180">
              </el-table-column>
              <el-table-column :label="$t('产品名称')" prop="goodsName" show-overflow-tooltip>
              </el-table-column>
              <el-table-column :label="$t('规格')" prop="status">
                <template slot-scope="scope">
                  <div>
                    <div v-for="(item,index) in scope.row.attributes" :key="index">
                      <span>{{ item.attrName }}:</span>
                      <span>{{ item.attrValue }}</span>
                    </div>
                  </div>
                </template>
              </el-table-column>
              <el-table-column :label="$t('数量')" prop="goodsNum">
              </el-table-column>
              <el-table-column :label="$t('单价')" prop="goodsReal">
                <template slot-scope="scope">
                  <FormatNumberShow :data="scope.row.goodsReal" :currency="true"/>
                </template>
              </el-table-column>
            </el-table>
          </div>
        </div>
        <div class="content-right">
          <div class="order-price">
            <div class="header">{{ $t('订单金额') }}</div>
            <div class="main">
              <div class="item">
                <div class="name">{{ $t('小计') }}</div>
                <FormatNumberShow :data="orderInfo.prizeOriginal" :currency="true"/>
                <!--                <div class="name">${{ (orderInfo.prizeOriginal || 0).toFloor(2) }}</div>-->
              </div>
              <div class="item">
                <div class="name">{{ $t('税') }}</div>
                <FormatNumberShow :data="orderInfo.tax" :currency="true"/>

                <!--                <div class="name">${{ (orderInfo.tax || 0).toFloor(2) }}</div>-->
              </div>
              <div class="item">
                <div class="name">{{ $t('运费') }}</div>
                <FormatNumberShow :data="orderInfo.fees" :currency="true"/>

                <!--                <div class="name">${{ (orderInfo.fees || 0).toFloor(2) }}</div>-->
              </div>
              <div class="item">
                <div class="name">{{ $t('折扣') }}</div>
                <FormatNumberShow :data="orderInfo.prizeOriginal - orderInfo.prizeReal" :currency="true"/>
                <!--                <div class="name">${{ ((orderInfo.prizeOriginal - orderInfo.prizeReal) || 0).toFloor(2) }}</div>-->
              </div>
              <div class="item top">
                <div class="name">{{ $t('累计') }}</div>
                <FormatNumberShow :data="orderInfo.prizeReal + orderInfo.tax + orderInfo.fees" :currency="true"/>
                <!--                <div class="name">${{ ((orderInfo.prizeReal + orderInfo.tax + orderInfo.fees) || 0).toFloor(2) }}</div>-->
              </div>
            </div>
          </div>
        </div>
      </div>
    </el-dialog>
    <el-dialog :title="$t('物流信息')" :visible="logisticsDialog" width="560px" @close="logisticsDialog=false">
      <div v-loading="logisticsLoading">
        <div v-for="item in logisticsData" :key="item.id" class="logistics-item">
          <p class="time">{{ item.updateTime }}</p>
          <p class="info">{{ $t('订单') }}<span style="color: #2C78F8"> {{ item.orderId }} </span>{{ $t(item.tipsTxt) }}
          </p>
        </div>
      </div>
    </el-dialog>
    <PayModal v-model="payModalShow" :payCallback="payCallback" @changeShowModel="changeShowModel"/>
  </div>
</template>

<script>
import {api_order_info_action_post, api_order_listGoods_action_post, caigouPost, getLogisticsInfo} from "@/api/user";
import {listCity, listCountry, listState} from "@/api/address";
import PayModal from '@/components/payModal'
import {getJson} from "@/utils/utis";
import FormatNumberShow from "@/components/FormatNumberShow/index.vue";
import defaultSettings, {projectTitle} from "@/settings";

export default {
  name: "table-list",
  props: {
    data: {
      //类型不匹配会警告
      type: [Object],
      default: 0,
      required: true,
      // 返回值不是 true,会警告
    },
    type: {
      type: String,
      default: "",
    },
  },
  mounted() {
    console.log("mounted", this.type);
    // 这边根据type去请求对应的数据
  },
  components: {
    PayModal,
    FormatNumberShow
  },
  data() {
    return {
      logisticsLoading: false,
      logisticsDialog: false,
      logisticsData: [],
      defaultSettings,
      contactsIcon: require('@/assets/images/frame.png'),
      payModalShow: false,
      currentPage: 0,
      orderId: "",
      bulkPurchasesStates: true,
      order_options: [
        {
          label: this.$t('全部'),
          value: undefined,
        },
        {
          label: this.$t('已支付'),
          value: "1",
        },
        {
          label: this.$t('未支付'),
          value: "0",
        },
      ],
      goods_options: [
        {
          label: this.$t('全部'),
          value: undefined,
        },
        {
          label: this.getOrderStatus(0),
          value: "0",
        },
        {
          label: this.getOrderStatus(1),
          value: "1",
        },
        {
          label: this.getOrderStatus(2),
          value: "2",
        },
        {
          label: this.getOrderStatus(3),
          value: "3",
        },
        {
          label: this.getOrderStatus(4),
          value: "4",
        },
        {
          label: this.getOrderStatus(5),
          value: "5",
        },
        {
          label: this.getOrderStatus(6),
          value: "6",
        },
      ],
      form: {
        order_no: undefined,
        order_status: undefined,
        goods_status: undefined,
        time: undefined,
      },
      tableData: [],
      detailData: [],
      detailOrderData: [],
      bugDialogVisible: false,
      orderDialogVisible: false,
      buyDetail: {},
      orderInfo: {},
      userInfo: {},
      userInfo2: {},
      orderMoney: {},
      pageSize: 10,
      show: false,
      countryCodeMap: {},//国家
      stateCodeMap: {},//省
      cityCodeMap: {}//城市
    };
  },
  computed: {
    columnWidth() {
      let width = 120;
      switch (this.$i18n.locale) {
        case 'en':
          width = 160;
          break;
        case 'cn':
          width = 120;
          break;
        case 'tw':
          width = 120;
          break;
        case 'de':
          width = 140;
          break;
        case 'fr':
          width = 160;
          break;
        case 'ja':
          width = 160;
          break;
        case 'ko':
          width = 160;
          break;
        case 'ms':
          width = 160;
          break;
        case 'th':
          width = 160;
          break;
        case 'pt':
          width = 160;
          break;
        case 'es':
          width = 160;
          break;
        case 'ru':
          width = 160;
          break;
        case 'el':
          width = 160;
          break;
        case 'it':
          width = 160;
          break;
        case 'tr':
          width = 160;
          break;
        case 'af':
          width = 160;
          break;
        case 'ph':
          width = 160;
          break;
        case 'ar':
          width = 160;
          break;
        case 'vi':
          width = 160;
          break;
        case 'id':
          width = 160;
          break;
        case 'hi':
          width = 160;
          break;
      }
      return width;
    },
  },
  filters: {
    formatContacts(val) {
      // 用户姓名脱敏
      if (val) {
        let name = val.split(' ');
        if (name.length > 1) {
          return val.replace(/^(.{1})(.*)(.{1})$/, "$1****$3");
        } else {
          return name[0].substring(0, 1) + '***';
        }
      }
    }
  },
  methods: {
    handleCommand(e, scope) {
      switch (e) {
        case 'a':
          this.openOrder(scope.row)
          break;
        case 'b':
          this.addGood(scope.row)
          break;
        case 'c':
          this.getLogisticsInfo(scope.row)
          break;
      }
    },
    getLogisticsInfo(item) {
      this.logisticsDialog = true;
      this.logisticsLoading = true;
      getLogisticsInfo({orderId: item.id}).then((res) => {
        this.logisticsLoading = false;
        const data = res.data.map(item => {
          const arr = item.log.split(item.orderId)
          return {
            ...item,
            tipsTxt: arr[1]
          }
        }).reverse()
        this.logisticsData = data
        console.log(data);
      })
    },
    getOrderStatus(status) {
      let obj = {
        '-1': "订单已取消",
        0: "等待买家付款",
        1: "买家已付款",
        2: "供应商已接单",
        3: "物流运输中",
        4: "买家已签收",
        5: "订单已完成",
        6: "已退款"
      };
      if (['Argos'].includes(projectTitle)) {
        obj = {
          '-1': "订单已取消",
          0: "等待买家付款",
          1: "买家已付款",
          2: "供应商已接单",
          3: "物流运输中",
          4: "订单已完成",
          5: "买家已评价",
          6: "已退款"
        };
      }

      return this.$t(obj[status]);
    },
    getAddress(countryId, cb) {
      listState({
        countryId: countryId
      }).then(function (data) {
        cb && cb(data);
      });
    },
    selectionChange() {
      let ids = this.$refs.table.selection.filter((item) => {
        if (item.purchStatus == 0) {
          return item.id;
        }
      });
      this.bulkPurchasesStates = !(ids.length > 0);
    },
    bulkPurchases() {
      //获取表格选中的数据
      let ids = this.$refs.table.selection.filter((item) => {
        if ((item.purchStatus == 0) && item.payStatus == 1 && item.status == 1) {
          return item.id;
        }
      });
      //如果ids是空的，提示用户
      if (ids.length == 0) {
        this.$notify({
          title: this.$t('提示'),
          message: this.$t('没有需要采购的订单'),
          type: 'warning'
        });
        return;
      }
      //ids用,衔接成字符串
      this.orderId = ids.map((item) => {
        return item.id;
      }).join(",");
      this.payModalShow = true;
    },
    contactsUser() {
      this.$router.push({
        path: '/chat/index',
        query: {name: this.orderInfo.contacts, partyid: this.orderInfo.partyId}
      })
    },
    changeShowModel(e) {
      this.showModel = e
    },
    payCallback(password) {
      const that = this
      that.payModalShow = false
      caigouPost({safeword: password, orderId: that.orderId}).then((res) => {
        that.orderId = "";
        that.$notify({
          title: this.$t('成功'),
          message: this.$t('订单采购成功'),
          type: 'success'
        });
        that.payModalShow = false;
        this.$emit("showCityName", this.form);
      }).catch(function (err) {
        that.orderId = "";
        that.payModalShow = false;
      });
    },
    // TODO: 搜索请求
    search() {
      console.log(this.form);
      this.$emit("sousuo", this.form);
    },
    // TODO: 重置搜索条件并且请求
    reset() {
      this.$refs.searchForm.resetFields();
      this.$emit("showCityName", this.form);
    },
    // TODO: 每页几条,去请求获取数据
    handleSizeChange(val) {
      console.log(`每页 ${val} 条`);
    },
    // TODO: 当前第几页,去请求获取数据
    handleCurrentChange(val) {
      console.log(`当前页: ${val}`);
    },
    // TODO: 采购
    addGood(row) {
      this.userInfo2 = row;
      this.orderId = row.id
      api_order_info_action_post({orderId: row.id}).then((e) => {
        console.log(e);
        this.buyDetail = e.data.orderInfo;
        // this.orders_list_data = e.data
        this.orderInfo = e.data.orderInfo;
      });
      api_order_listGoods_action_post({orderId: row.id}).then((e) => {
        this.detailData = e.data.pageList;
      });
      this.bugDialogVisible = true;
      console.log("采购请求，并且重新获取数据");
    },
    getCountry(code) {
      var obj = this.countryCodeMap[code] || {};
      return obj.countryName || code;
    },
    getState(code) {
      var obj = this.stateCodeMap[code] || {};
      return obj.stateName || code;
    },
    getCity(code) {
      var obj = this.cityCodeMap[code] || {};
      return obj.cityName || code;
    },
    // TODO: 查看订单详情
    openOrder(row) {
      this.userInfo2 = row;
      api_order_info_action_post({orderId: row.id}).then((e) => {
        const orderInfo = this.orderInfo = e.data.orderInfo,
            lang = localStorage.getItem('lang');
        listCountry({
          lang: lang
        }).then(data => {
          this.countryCodeMap = getJson(data.data.data, "id");
        });
        listState({
          countryId: orderInfo.country,
          lang: lang
        }).then(data => {
          this.stateCodeMap = getJson(data.data.data, "id");
        });

        listCity({
          stateId: orderInfo.province,
          queryType: 'noShow',
          lang: lang
        }).then(data => {
          this.cityCodeMap = getJson(data.data.data, "id");
          console.log(this.cityCodeMap);
        });
      });
      api_order_listGoods_action_post({orderId: row.id}).then((e) => {
        this.detailData = e.data.pageList;
      });
      this.orderDialogVisible = true;
    },
    // TODO: 确定订单,采购请求
    onSubmit() {
      this.bugDialogVisible = false;
      this.payModalShow = true;
    },
  },
};
</script>

<style lang="scss" scoped>
.contacts-icon {
  width: 34px;
  height: 34px;
  margin-left: 12px;
  padding: 8px;
  box-sizing: border-box;
  background-color: #1552F0;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  position: absolute;
  right: -50px;
  top: 0;
  cursor: pointer;
  box-shadow: 0px 4.5px 6px rgba(21, 82, 240, 0.25);

  img {
    width: 100%;
    height: 100%;
  }
}

.six-digit-wrapper {
  width: 100%;
  display: flex;
  justify-content: center;
  flex-direction: row;
  margin-top: 30px;

  .input {
    display: flex;
    width: 35px;
    margin-left: 10px;
    height: 44px;
    font-size: 18px;
    color: #333333;
    background-color: #f2f2f2;
    text-align: center;
    outline: none; // 去除选中状态边框
    border: solid 1px #d2d2d2;
    border-top: 0px;
    border-left: 0px;
    border-right: 0px;
  }
}

.wrapper {
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  height: 100%;
}

.table-list {
  width: 100%;
  height: 100%;

  .search {
    padding: 20px 20px 0px 20px;
    background-color: #fff;
    margin-bottom: 10px;
    border-radius: 10px;
  }

  .table {
    padding: 20px;
    background-color: #fff;
    border-radius: 10px;
  }

  .detail {
    border: 1px solid #dfe6ec;
    border-radius: 3px;
    margin-bottom: 20px;

    .header {
      line-height: 40px;
      padding-left: 10px;
      border-bottom: 1px solid #dfe6ec;
    }

    .main-price {
      .item {
        display: flex;
        line-height: 30px;
        padding: 5px 10px;
        justify-content: space-between;
        font-size: 14px;
        font-weight: 600;

        .name {
          font-weight: 600;
          font-size: 14px;
        }
      }

      .top {
        border-top: 1px solid #dfe6ec;
        padding-top: 5px;
      }
    }
  }

  .btn {
    text-align: center;

    ::v-deep .el-button {
      color: #fff;
    }
  }

  .order-top {
    border: 1px solid #dfe6ec;
    border-radius: 3px;
    margin-bottom: 20px;

    .header {
      line-height: 40px;
      padding-left: 10px;
      border-bottom: 1px solid #dfe6ec;
    }

    .main {
      .border {
        border-top: 1px solid #dfe6ec;
      }

      &-content {
        display: flex;
        justify-content: space-between;
        padding: 0 10px;

        .left {
          width: 46%;

          .item {
            display: flex;
            line-height: 14px;
            margin: 16px 6px;
            justify-content: space-between;
            font-size: 14px;
            font-weight: 600;

            > div:first-child {
              width: 48%;
            }
          }
        }

        .right {
          width: 46%;

          .item {
            display: flex;
            line-height: 14px;
            margin: 16px 10px;
            justify-content: space-between;
            font-size: 14px;
            font-weight: 600;

            div:first-child {
              width: 48%;
            }
          }
        }
      }
    }
  }

  .order-bottom {
    display: flex;
    justify-content: space-between;

    .content-left,
    .content-right {
      border: 1px solid #dfe6ec;
      border-radius: 3px;
      margin-bottom: 20px;

      .header {
        line-height: 40px;
        padding-left: 10px;
        border-bottom: 1px solid #dfe6ec;
      }
    }

    .content-left {
      width: calc(70% - 20px);
    }

    .content-right {
      width: 30%;

      .item {
        display: flex;
        line-height: 30px;
        margin: 10px;
        justify-content: space-between;
        font-size: 14px;
        font-weight: 600;

        .name {
          font-weight: 600;
          font-size: 14px;
        }
      }

      .top {
        border-top: 1px solid #dfe6ec;
        padding-top: 10px;
      }
    }
  }

  //::v-deep .el-dialog__header {
  //  font-weight: 700;
  //  color: #000000;
  //}
  //::v-deep .el-dialog__headerbtn .el-dialog__close {
  //  color: #333;
  //}
}

::v-deep {
  .el-table__body-wrapper,
  .el-table__header-wrapper {
    .cell {
      text-align: center;
    }
  }
}

.logistics-item {
  padding: 10px 0;
  border-bottom: 1px solid #dfe6ec;

  .time {
    color: #999;
    font-size: 12px;
    margin-bottom: 5px;
  }

  .info {
    font-size: 14px;
    color: #333;
  }
}
</style>
