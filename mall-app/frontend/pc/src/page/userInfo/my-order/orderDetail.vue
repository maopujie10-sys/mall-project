<template>
  <div class="detail_container" v-loading="loading">
    <div class="page-title" style="cursor: pointer" @click="goBack">
      <i class="el-icon-arrow-left"></i> {{ $t("message.home.myOrder") }}/{{
        $t("message.home.orderInfo")
      }}
    </div>
    <div class="detail_container">
      
      <div class="left">
        <div>
          <span class="info_title">{{ $t("message.home.productInfo") }}</span>
        <div
          class="product_info"
          v-for="product in orderGoodsList"
          :key="product.goodsId + Math.random()"
        >
          <!-- {{ product.goodsIcon }} -->
          <el-image
            class="img"
            style="width: 62px; height: 62px"
            :src="product.goodsIcon"
            fit="scale-down"
          ></el-image>
          <div class="prodesc">
            <span
              @click="() => goToDetail(product.goodsId, product.isShelf, product.isValid)"
              class="tit"
            >
              {{ product.goodsName }}
            </span>
            <div class="price">
              <span class="real_price">
                ${{ numberFormat(product.sellingPrice) }}
              </span>
              <span class="num"> x{{ product.goodsNum }} </span>
            </div>
            <span
              class="attr"
              v-if="product.attributes && product.attributes.length > 0"
            >
              {{
                product.attributes
                  .map((it) => `${it.attrName}:${it.attrValue}`)
                  .join(" ")
              }}
            </span>
          </div>
          <div class="delivery"></div>
          <div class="fees">
            <span class="desc">
              <!-- {{typeof(Number(numberFormat(product.sellingPrice + product.tax + product.fees)))}} -->
              <!-- {{ $t("message.home.totalPrice") }} : ${{  $big(
                    numberFormat(
                    $big( product.sellingPrice - 0 ).plus(product.tax - 0).plus(product.fees - 0)
                  )).times(product.goodsNum - 0) }} -->
                  {{ $t("message.home.totalPrice") }} : {{
                    numberFormat(
                     $big( product.sellingPrice).plus(product.tax).plus(product.fees )
                    .times(product.goodsNum))
                  }}
            </span>
            <span class="desc">
             {{ $t("message.home.discount") }} : -${{ numberFormat($big(product.sellingPrice).minus(product.goodsReal).times(product.goodsNum)) }}
              <!-- {{ $t("message.home.discount") }} : -${{ numberFormat(numberFormat(product.sellingPrice)-(numberFormat(product.goodsReal))*(product.goodsNum)) }} -->
            </span>
            <span class="desc">
              {{ $t("message.home.tax") }} : ${{
                numberFormat($big(product.tax).times(product.goodsNum))
              }}
              <!-- {{ $t("message.home.tax") }} : ${{
                numberFormat(product.tax * product.goodsNum)
              }}  -->
            </span>
            <span class="desc">
              {{ $t("message.home.goodsFreight") }} : ${{
                numberFormat($big(product.fees).times(product.goodsNum))
              }}
              <!-- {{ $t("message.home.goodsFreight") }} : ${{
                numberFormat(product.fees * product.goodsNum)
              }} -->
            </span>
            <span class="desc total_Desc">
              {{ $t("message.home.totalNum") }} :${{
                numberFormat($big(product.goodsReal).plus(product.tax).plus(product.fees).times(product.goodsNum))
              }}
              <!-- {{ $t("message.home.totalNum") }} :${{
                
                  $big(product.goodsReal).plus(product.tax)
              }} -->
            </span>
          </div>
        </div>
        </div>
        <div v-if="orderGoodsList.length" class="commodity-content-pagination">
              <el-pagination
                background
                layout="prev, pager, next"
                class="es-pagination"
                :page-size="pageSize"
                :current-page="pageNum"
                :total="total"
                @current-change="currentChange"
              />
            </div>
      </div>

      <div class="right">
        <span class="info_title" style="margin-bottom: 17px">
          {{ $t("message.home.orderInfo") }}
        </span>
        <div class="order_box boxMargin">
          <span class="orderFont"
            >{{ $t("message.home.serialNumber") }} : {{ orderDetails.id }}
            <i
              @click="copy"
              style="cursor: pointer"
              class="el-icon-copy-document"
          /></span>
          <span class="orderFont"
            >{{ $t("message.home.orderTime") }} :
            {{ $formatZoneDate(orderDetails.createTime) }}</span
          >
          <span class="orderFont"
            >{{ $t("message.home.orderStatus") }} :
            <span style="color: #e4111f">{{
              getOrderStatusLable(orderDetails.status)
            }}</span></span
          >
        </div>

        <div class="order_box boxMargin">
          <span
            style="font-weight: 500; font-size: 14px; margin-bottom: 10px"
            >{{ $t("message.home.receiver") }}</span
          >
          <span style="font-weight: 500; font-size: 12px">
            {{ orderDetails.contacts }}
            {{ phoneNumber(orderDetails.phone) }}</span
          >
          <span
            style="
              font-weight: 500;
              font-size: 12px;
              color: #999999;
              margin-bottom: 10px;
            "
            >{{ orderDetails.address }}</span
          >
        </div>

        <div class="order_box">
          <div
            class="flex_row_between"
            style="
              font-weight: 600;
              font-size: 12px;
              margin: 20px 14px 0px 14px;
            "
          >
            <span>{{ $t("message.home.orderPrefix") }}</span>
            <span> ${{ numberFormat(orderDetails.prizeOriginal) }} </span>
          </div>
          <span class="flex_row_between item_line">
            {{ $t("message.home.discount") }}
            <span>-${{ numberFormat(orderDetails.discount) }}</span>
          </span>
          <div class="flex_row_between item_line">
            <span>{{ $t("message.home.tax") }} </span>+${{ orderDetails.tax }}
          </div>
          <div class="flex_row_between item_line">
            <span> {{ $t("message.home.goodsFreight") }} </span>
            <span>+${{ orderDetails.fees }}</span>
          </div>
          <div style="margin-left: 14px; margin-right: 14px">
            <el-divider></el-divider>
          </div>
          <div
            style="
              display: flex;
              flex-direction: row;
              justify-content: flex-end;
              margin-right: 14px;
              margin-left: 14px;
            "
          >
            <span style="font-weight: 400; font-size: 12px"
              >{{ $t("message.home.totalNum") }} :
              <span class="real_price">${{ numberFormat($big(orderDetails.prizeReal).plus(orderDetails.fees).plus(orderDetails.tax)) }}</span></span
            >
          </div>
          <div
            style="
              display: flex;
              justify-content: space-between;
              flex-wrap: wrap;
              margin: 0 10px;
              margin-bottom: 24px;
            "
          >
            <div
              @click="button.func"
              v-for="button in getStatusButtons(orderDetails.status)"
              :key="button.key"
              class="button"
              :class="[button.activity ? 'active' : '']"
            >
              {{ button.text }}
            </div>
          </div>
        </div>
      </div>
    </div>
    <order-logistics-dialog
      v-model="logisticsDialogVisible"
      :currentOrderInfo="currentOrderInfo"
      :refresh="requestData"
    />
    <order-payment-dialog
      @closePay="closePayDialog"
      v-model="paymentDialogVisible"
      :currentOrderInfo="currentOrderInfo"
      :refresh="requestData"
    />
    <!-- 取消订单 -->
    <order-cancel-dialog
      v-model="cancelDialogVisible"
      :currentOrderInfo="currentOrderInfo"
      :refresh="requestData"
    />
  </div>
</template>

<script>
import { getOrderStatusLable } from "@/util/shop";
import { mapActions, mapGetters } from "vuex";
import { numberFormat, phoneNumber } from "@/util";
import ordermix from "./ordermix";
import {OrderGoodsApi} from "@/api/order";
export default {
  mixins: [ordermix],
  data(){
    return{
      orderGoodsList:[],
      pageNum:1,
      pageSize:3,
      total:0,
    }
  },
  mounted() {
    console.log(this.$route.query?.orderId);
    if (!this.$route.query?.orderId) {
      this.$message({
        type: "error",
        message: this.$t("message.home.paramError"),
      });
    } else {
      this.requestData();
      this.getList()
    }

    // console.log(this.$router.query.orderId)
  },
  watch: {
    $route: function (to, from) {
      console.log("from-detail ->", from);
    },
  },
  computed: {
    ...mapGetters({
      orderDetails: "order/orderDetails",
      orderGoods: "order/orderGoods",
    }),

    getOrderPrefix() {
      let total = 0;
      if (Array.isArray(this.orderGoods)) {
        this.orderGoods.forEach((item) => {
          total += (item.goodsReal + item.fees + item.tax) * item.goodsNum; //    accAdd(accTimes(item.goodsReal, item.goodsNum), item.fees, item.tax)
        });
      }
      return numberFormat(total);
    },
  },

  methods: {
    getOrderStatusLable,
    numberFormat,
    phoneNumber,
    ...mapActions({
      requestOrderDetailsList: "order/requestOrderDetailsList",
      requestOrderGoodsList: "order/requestOrderGoodsList",
    }),
    goToDetail(id) {
      let status = localStorage.getItem("orderStatus");
      if (status == 1) {
        this.$router.push({ name: "productDetails", query: { id } });
      } else {
        this.$message({
          type: "warning",
          message: this.$t("message.home.productAvailable"),
        });
      }
      // if (isShelf && isValid) {
        // this.$router.push({ name: "productDetails", query: { id } });
      // } else {
      //   this.$message({
      //     type: "warning",
      //     message: this.$t("message.home.productAvailable"),
      //   });
      // }
    },
    async requestData() {
      try {
        this.loading = true;
        await this.requestOrderDetailsList({
          orderId: this.orderId,
          type: 1,
        });
        await this.requestOrderGoodsList({
          orderId: this.orderId
        });
        this.currentOrderInfo = this.orderDetails;
        console.log('this.orderDetails ->', this.orderDetails);
      } finally {
        this.loading = false;
      }
    },
    async getList(){
       const res = await OrderGoodsApi({ orderId: this.orderId , pageNum: this.pageNum,
              pageSize: this.pageSize,});
          const { pageInfo, pageList } = res.data;
          this.total = pageInfo.totalElements;
          this.orderGoodsList = pageList;
    },
    currentChange(val){
      this.pageNum = val;
      this.getList()
    },
    goBack() {
      this.$router.push("/userInfo/my-order");
    },
    
    getStatusButtons(number) {
      switch (number) {
        case -1:
          return [];
        case 0:
          return [this.payButton, this.cancelButton];
        case 1:
        case 2:
          return [this.sendInfoButton, this.returnPayButton];
        case 3:
          return [
            this.confirmButton,
            this.queryLogisticsButton,
            this.returnPayButton,
          ];
        case 4:
          return [this.evaluateButton, this.queryLogisticsButton];
        case 5:
          return [this.queryLogisticsButton];
        case 6:
          return [this.queryLogisticsButton];
      }
    },
  },
};
</script>

<style scoped lang="scss">
  .commodity-content-pagination{
    margin: 10px auto;
  }
.button {
  height: 28px;
  padding: 0 10px;
  /* padding-right: 20px; */
  line-height: 28px;
  white-space: nowrap;
  border: 1px solid #8c8c8c;
  border-radius: 14px;
  color: #333333;
  margin-right: 5px;
  margin-top: 5px;
  max-width: 155px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  cursor: pointer;

  &.active {
    color: var(--color-main);
    border: 1px solid var(--color-main);
    background: linear-gradient(0deg, #fff7ec, #fff7ec), #eeeeee;
  }
}

.detail_container {
  // width: 775px;
  margin-top: 24px;
  margin-left: 34px;
  display: flex;
  flex-direction: column;

  .info_title {
    font-weight: 500;
    font-size: 14px;
  }

  .flex_row_between {
    display: flex;
    flex-direction: row;
    justify-content: space-between;
  }

  .delivery {
    height: 92px;
    width: 0px;

    margin-left: 21px;
    margin-right: 31px;

    border: 1px solid #eeeeee;
    -webkit-transform-origin: 0 0;
    transform-origin: 0 0;
    // -webkit-transform: scale(.5, .5);
  }

  .real_price {
    font-family: "Roboto";
    font-style: normal;
    font-weight: 500;
    font-size: 16px;
    line-height: 19px;
    color: var(--color-price);
  }

  .detail_container {
    display: flex;
    flex-direction: row;

    .left {
      flex-direction: column;
      width: 484px;

      .product_info {
        margin-top: 17px;
        width: 484px;
        // height: 128px;
        padding-top: 10px;
        padding-bottom: 10px;
        border: 1px solid #eeeeee;
        border-radius: 4px;
        display: flex;
        flex-direction: row;
        align-items: center;

        .img {
          display: flex;
          justify-content: center;
          width: 62.73px;
          height: 62.73px;
          margin-left: 3px;
          margin-right: 18px;
        }

        .prodesc {
          display: flex;
          flex-direction: column;
          width: 242px;

          .tit {
            font-family: "Roboto";
            font-style: normal;
            font-weight: 400;
            font-size: 14px;
            overflow: hidden;
            line-height: 24px;
            text-overflow: ellipsis;
            display: -webkit-box;
            -webkit-line-clamp: 2;
            overflow: hidden;
            /*! autoprefixer: off */
            -webkit-box-orient: vertical;
            cursor: pointer;
          }

          .attr {
            font-family: "Roboto";
            font-style: normal;
            font-weight: 400;
            font-size: 12px;
            margin-top: 4px;
          }

          .price {
            display: flex;
            flex-direction: row;
            justify-content: space-between;
            margin-top: 10px;

            .num {
              font-size: 14px;
            }
          }
        }

        .fees {
          display: flex;
          flex-direction: column;
          font-family: "Roboto";
          font-style: normal;
          font-weight: 400;
          font-size: 12px;

          .desc {
            margin-top: 4px;
          }

          .total_Desc {
            font-weight: 600;
          }
        }
      }
    }
  }

  .right {
    display: flex;
    flex-direction: column;
    margin-left: 14px;
    width: 347px;

    .boxMargin {
      margin-bottom: 14px;
      padding-top: 14px;
      padding-left: 14px;
    }

    .item_line {
      font-weight: 400;
      font-size: 12px;
      margin-top: 18px;
      margin-left: 14px;
      margin-right: 14px;
    }

    .order_box {
      width: 347px;
      /* eee */
      border: 1px solid #eeeeee;
      border-radius: 4px;
      display: flex;
      flex-direction: column;
      span {
        white-space: nowrap;
        text-overflow: ellipsis;
        overflow: hidden;
      }
    }

    .orderFont {
      font-weight: 400;
      font-size: 12px;
      margin-bottom: 10px;
    }
  }
}
</style>
