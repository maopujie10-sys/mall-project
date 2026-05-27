<template>
  <div class="collect-content">
    <el-dialog
      class="es-dialog"
      :visible.sync="dialogVisible"
      :center="true"
      :destroy-on-close="true"
    >
      <div slot="title" class="dialog-title">
        <span>{{ $t("message.home.addCart" /** 添加购物车*/) }}</span>
      </div>
      <div class="dialog-content" v-if="dialogVisible">
        <EsProductInfo :id="currentId" @handleBuy="handleBuy" />
      </div>
      <span slot="footer"></span>
    </el-dialog>

    <div class="page-title" style="cursor: pointer" @click="goBack">
      <i class="el-icon-arrow-left"></i>
      {{ $t("message.home.myCommodityCollection") }}
    </div>
    <div v-loading="loading" >
      <div ref="collentGoods" class="content">
        <div v-if="listData.length" class="list-content">
        <div v-for="item in listData" :key="item.sellerId" class="item" >
          <div class="discount" v-if="item.discountRatio">
            <span>{{ numberFormatFn(item.discountRatio) * 100 }} %</span>
            <br>
            <span>OFF</span>
          </div>
          <div class="poster" @click="gotoDetails(item)">
            <img
              :src="
                item.imgUrl1 || item.imgUrl2 || item.imgUrl3 || item.imgUrl4
              "
              alt="collection-item"
            />
          </div>
          <div class="price">
            <p>
              ${{ numberFormatFn(item.discountPrice || item.sellingPrice) }}
            </p>
            <i class="el-icon-star-on" @click="cancelCol(item)" />
          </div>
          <div class="name">
            <p @click="gotoDetails(item)">{{ item.name || "-" }}</p>
            <div>
              <i class="el-icon-shopping-cart-full"></i>
              <span class="buy-btn" @click="buyNow(item)">
                {{ $t("message.home.buyNow" /**立即购买 */) }}
              </span>
            </div>
          </div>
        </div>
      </div>
      </div>
      
      <el-empty
        v-if="!listData.length && !loading"
        :description="$t('message.home.noData')"
      ></el-empty>
    </div>
    <div v-if="listData.length || total" class="common-pagination">
      <el-pagination
        background
        class="es-pagination"
        layout="prev,pager, next"
        :pager-count="5"
        :page-size="pageSize"
        :current-page="pageNum"
        :total="total"
        @current-change="currentChange"
      />
    </div>
  </div>
</template>

<script>
  import EsProductInfo from "@/components/productInfo";
  import { KeepGoodsListApi, KeepGoodsCancelApi } from "@/api/userCenter";
  import { numberFormat } from "@/util";
  export default {
    name: "CollectGoods",
    components: { EsProductInfo },
    data() {
      return {
        listData: [],
        loading: true,
        pageNum: 1,
        pageSize: 8,
        total: 0,
        dialogVisible: false,
        currentId: "",
      };
    },
    mounted() {
      this.$nextTick(() => {
        this.getListData();
      });
      this.$store.state.user.currentIndex = 3;
    },
    methods: {
      goBack() {
        this.$router.go(-1);
      },

      numberFormatFn(num) {
        return numberFormat(num);
      },

      currentChange(page) {
        this.pageNum = page;
        this.getListData();
      },

      getListData() {
        this.loading = true;
        const params = {
          pageNum: this.pageNum,
          pageSize: this.pageSize,
        };
        KeepGoodsListApi(params)
          .then((res) => {
            const data = res.data;
            // console.log("this.listData ->", data);
            this.total = res.data.pageInfo?.totalElements || 0;
            data.pageList.forEach((item) => {
              item.loading = false;
            });
            this.listData = data.pageList;
            // console.log(" this.listData->", this.total);
            // collentGoods
            this.$Gsap.from(this.$refs.collentGoods,{
                delay: 0.5,
                duration: 1,
                y: '+100',
                autoAlpha: 0,
                ease: "back.out(1.7)"
              })
            this.loading = false;
          })
          .catch(() => {
            this.loading = false;
          });
      },

      cancelCol(data) {
        KeepGoodsCancelApi({ sellerGoodsId: data.id }).then(() => {
          this.pageNum = 1;
          this.getListData();
        });
      },

      buyNow(data) {
        this.currentId = data.id;
        setTimeout(() => {
          this.dialogVisible = true;
        }, 300);
      },

      handleBuy() {
        this.dialogVisible = false;
      },

      gotoDetails(data) {
        if (data.isShelf) {
        this.$router.push({ name: "productDetails", query: { id: data.id } });
      } else {
        this.$message({
          type: "warning",
          message: this.$t("message.home.productAvailable"),
        });
      }
        // this.$router.push({
        //   name: "productDetails",
        //   query: { id: data.id },
        // });
      },
    },
  };
</script>

<style lang="scss" scoped>
html[dir="rtl"] {
  .collect-content{
    padding-left: 0;
    padding-right: 50px;
  }
}
  .collect-content {
    padding-top: 32px;
    padding-left: 50px;
     .content {
      margin-top: 15px;
      min-height: 120px;
      > .list-content {
        overflow: hidden;
        > .item {
          width: 200px;
          border: 1px solid #eeeeee;
          border-radius: 4px;
          float: left;
          margin-right: calc(52px / 3);
          margin-bottom: 20px;
          overflow: hidden;
          position: relative;
          .discount{
            width: 31px;
            height: 32px;
            background: url("../../../assets/image/discount.png") no-repeat 100%/100%;
            position: absolute;
            top: 0;
            right: 0;
            text-align: center;
            font-size: 11px;
            color: #fff;
            font-weight: 500;
          }
          &:nth-child(4n) {
            margin-right: 0;
          }
          > .poster {
            width: 180px;
            height: 180px;
            padding: 10px;
            display: flex;
            align-items: center;
            justify-content: center;
            overflow: hidden;
            cursor: pointer;
            > img {
              width: 100%;
              height: auto;
            }
          }
          > .price {
            padding: 0 10px;
            display: flex;
            align-items: center;
            justify-content: space-between;
            margin-top: 10px;
            > p {
              font-size: 16px;
              color: var(--color-price);
            }
            > i {
              font-size: 18px;
              color: var(--color-main);
              cursor: pointer;
            }
          }
          > .name {
            padding: 10px;
            height: 90px;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
            cursor: pointer;
            > p {
              overflow: hidden;
              text-overflow: ellipsis;
              display: -webkit-box;
              -webkit-line-clamp: 2;
              -webkit-box-orient: vertical;
            }
            > div {
              cursor: pointer;
            }
          }
        }
      }
    }
  }
</style>
