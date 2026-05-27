<template>
  <div class="commodity recommend">
    <div class="app-container">
      <!-- <div class="recommend-swiper">
        <swiper class="swiper" :options="swiperOptions">
          <swiper-slide v-for="item in bannerList" :key="item">
            <img :src="item" alt="" />
          </swiper-slide>
          <div class="swiper-pagination" slot="pagination"></div>
        </swiper>
      </div> -->

      <div class="commodity-wrap flex-start">
        <div v-loading="pageLoading" class="commodity-content">
          <div ref="commodityL">
            <div v-if="listData.length" class="commodity-content-item">
              <div
                v-for="(item, index) in listData"
                :key="item.goodsId + '_' + index"
                class="item"
              >
                <EsProductView :item="item" />
              </div>
            </div>
            <div v-if="listData.length" class="commodity-content-pagination">
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
            <div class="no-data" v-if="!listData.length && !pageLoading">
              <el-empty :description="$t('message.home.noData')"></el-empty>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import EsProductView from "@/components/product";

import { MerchantProductListApi } from "@/api";

export default {
  name: "EsRecommed",
  components: { EsProductView },
  data() {
    return {
      swiperOptions: {
        autoplay: {
          delay: 4500,
          disableOnInteraction: false,
        },
        pagination: {
          el: ".swiper-pagination",
        },
      },
      listData: [],
      pageLoading: true,
      pageNum: 1,
      pageSize: 18,
      total: 0,
      currentId: null,
    };
  },
  mounted() {
    this.$nextTick(() => {
      if (this.$route.query && this.$route.query.storeId) {
        this.currentId = this.$route.query.storeId;
        this.getListData();
      } else {
        this.pageLoading = false;
      }
    });
  },
  methods: {
    getListData(flag) {
      try {
        if (flag) {
        this.pageNum = 1;
        this.currentId = this.$route.query.storeId;
      }
      this.pageLoading = true;
      MerchantProductListApi({
        pageNum: this.pageNum,
        pageSize: this.pageSize,
        sellerId: this.currentId,
        isRec: 1,
      })
        .then((res) => {
          // console.log(res);
          const { pageInfo, pageList } = res.data;
          this.total = pageInfo.totalElements;
          this.listData = pageList;
          this.pageLoading = false;
          this.$Gsap.fromTo(this.$refs.commodityL, {
              delay: 0,
              duration: 1,
              y: '100',
              autoAlpha: 0,
              ease: "back.out(1.7)"
            },{
              delay: 0.5,
              duration: 1,
              y: '0',
              autoAlpha: 1,
              ease: "back.out(1.7)"
            })
        })
        .catch(() => {
          this.pageLoading = false;
        });
      } finally {
        this.pageLoading = false;
        console.log('this.$refs ->', this.$refs);
         
      }
      
    },
    currentChange(page) {
      this.pageNum = page;

      window.scrollTo(0, 0);
      this.getListData();
    },
    // currentChange(page) {},
  },
};
</script>

<style lang="scss" scoped>
.recommend {
  &-swiper {
    max-width: 1112px;
    margin: 0 auto;
    height: 198px;
    margin-bottom: 48px;
    .swiper-slide {
      height: 198px;
      img {
        width: 100%;
        height: 100%;
        object-fit: cover;
      }
    }
  }
  .commodity-content {
    min-height: 300px;
  }
  .commodity-content-item {
    // overflow: hidden;
    margin-top: 20px;
        display: grid;
    grid-template-columns: repeat(auto-fit, minmax(188px, 165px));
    grid-column-gap: 14px;
    grid-row-gap: 20px;
    align-content: center;
    > .item {
      // width: 165px;
      // margin-right: 34px;
      // margin-bottom: 30px;
      // float: left;
      // &:nth-child(6n) {
      //   margin-right: 0;
      // }
      /deep/ .product {
        p {
          height: 42px !important;
        }
      }
    }
  }
}
</style>
