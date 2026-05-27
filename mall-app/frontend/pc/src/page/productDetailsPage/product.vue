<template>
  <div>
    <div  v-if="item" @mouseenter="onEnterTd($event.target)" @mouseleave="onLeave($event.target)">
      <div class="productc">
        <div class="discount" v-if="item.discountRatio">
        <span>{{ numberFormatFn(item.discountRatio) * 100 }} %</span>
        <br>
        <span>OFF</span>
      </div>
        <div class="poster" @click="gotoDetails">
          <img v-if="item.imgUrl1" :src="item.imgUrl1" />
          <img v-else src="@/assets/image/morenImg.png" />
        </div>
        <div class="productc-foote">
          <p @click="gotoDetails">
            {{ item.name }}
          </p>
          <div class="sc">
            <h2>
              ${{ numberFormatFn(item.discountPrice ?? item.sellingPrice) }}
            </h2>
            <div :key="key">
              <i
                :class="keep ? 'el-icon-star-on' : 'el-icon-star-off'"
                @click="collect(item)"
                :style="keep ? 'color:var(--color-main)' : ''"
              ></i>
            </div>
          </div>
        </div>
      </div>
    </div>
    <!-- <el-dialog
      :independent-modal="true"
      :modal-append-to-body="false"
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
    </el-dialog> -->
  </div>
</template>

<script>
// import EsProductInfo from "@/components/productInfo";
import { numberFormat } from "@/util";
import { mapActions } from "vuex";
import { ES_TOKEN } from "@/common";
import { notLogin } from "@/common/pageHook";
import Bus from "@/util/bus";

export default {
  name: "EsProduct",
  // components: { EsProductInfo },
  props: {
    item: {
      type: Object,
      default: () => {},
    },
  },

  data() {
    return {
      dialogVisible: false,
      currentId: "",
      keep: false,
      key: 0,
    };
  },
  inject: ["getLikeMethed"],
  mounted() {
    this.keep = this.item.isKeep;
  },
  methods: {
    onEnterTd(e){
        let el = e
          this.$Gsap.to(el,{
          delay: 0,
          duration: .5,
          scale:1.1,
          ease: "back.outIn(1.7)"
        })
      },
    onLeave(e){
      this.$Gsap.to(e,{
          delay: 0,
          duration: .5,
          scale:1,
          ease: "back.outIn(1.7)"
        })
    },
    ...mapActions({
      requestProductDetails: "productDetails/requestProductDetails",
      requestCollectGoods: "user/requestCollectGoods",
      requestCollectGoodsDel: "user/requestCollectGoodsDel",
    }),
    gotoDetails() {
      localStorage.setItem("scroll", document.documentElement.scrollTop);
      this.$router.push({
        name: "productDetails",
        query: { id: this.item.id },
      });
    },
    buyNow() {
      this.currentId = this.item.id;
      this.$nextTick(() => {
        this.dialogVisible = true;
      });
    },
    async collect() {
      // const goodId = id
      if (notLogin()) {
        return;
      }
      try {
        if (this.keep) {
          await this.requestCollectGoodsDel({
            sellerGoodsId: this.item.id,
            token: localStorage.getItem(ES_TOKEN),
          });
          Bus.$emit("collect", this.item.id);
          this.$message.warning(this.$t("message.home.cancelSuccess"));
        } else {
          await this.requestCollectGoods({
            sellerGoodsId: this.item.id,
            token: localStorage.getItem(ES_TOKEN),
          });
          Bus.$emit("UnCollect", this.item.id);
          this.$message.success(this.$t("message.home.collectionSuccess"));
        }

        await this.requestProductDetails({
          sellerGoodsId: this.item.id,
          token: localStorage.getItem(ES_TOKEN),
        });
      } finally {
        this.keep = !this.keep;
        this.getLikeMethed();
      }
    },
    handleBuy() {
      this.dialogVisible = false;
    },
    numberFormatFn(num) {
      return numberFormat(num);
    },
  },
};
</script>

<style lang="scss">
.productc {
  border: 1px solid var(--color-border);
  padding: 0 8px 8px 8px;
  border-radius: 5px;
  display: flex;
  // justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
  position: relative;
  > div {
    cursor: pointer;
  }
  .discount{
      width: 31px;
      height: 32px;
      background: url("../../assets/image/discount.png") no-repeat 100%/100%;
      position: absolute;
      top: 0;
      left: 0;
      text-align: center;
      font-size: 11px;
      color: #fff;
      font-weight: 500;
    }
  .product-res {
    font-family: "Roboto";
    font-style: normal;
    font-weight: 400;
    font-size: 10px;
    line-height: 12px;
    /* identical to box height */
    color: #999999;
  }
  .poster {
    width: 100%;
    height: 100%;
    width: 65px;
    height: 65px;
    margin-right: 4px;
    overflow: hidden;
  }
  img {
    width: 100%;
    height: 100%;
    max-width: 65px;
    // height: 65px;
    object-fit: contain;
  }

  h2 {
    font-size: 12px;
    color: var(--color-price);
    margin-bottom: 6px;
    font-weight: 500;
  }

  p {
    font-size: 12px;
    font-weight: 400;
    height: 35px;
    line-height: 1.5;
    color: var(--color-title);
    max-width: 132px;
    overflow: hidden;
    text-overflow: ellipsis;
    display: -webkit-box;
    -webkit-line-clamp: 2;
    -webkit-box-orient: vertical;
    margin: 6px 0 15px 0;
  }

  &-foote {
    display: flex;
    justify-content: space-between;
    align-items: center;
    flex-direction: column;
    flex: 1;
    div {
      display: flex;
      align-items: center;
    }
    .el-icon-shopping-cart-full {
      margin-right: 8px;
    }
    .buy-btn {
      font-size: 12px;
      font-weight: 600;
      cursor: pointer;
    }
  }
  .sc {
    display: flex;
    justify-content: space-between;
    align-items: center;
    width: 100%;
  }

  // &-dialog {
  //   .el-dialog__header {
  //     padding: 0;
  //     border-radius: 6px;
  //   }
  //   .el-dialog__close {
  //     font-size: 24px;
  //   }
  //   .el-dialog__headerbtn {
  //     top: 14px;
  //     right: 14px;
  //   }
  //   .el-dialog {
  //     width: 80vw;
  //     max-width: 1000px;
  //   }
  //   .dialog-title {
  //     height: 50px;
  //     line-height: 50px;
  //     background-color: #f5f5f5;
  //     font-weight: 700;
  //     font-size: 18px;
  //     color: var(--color-title);
  //     border-radius: 6px;
  //   }
  //   .dialog-content {
  //     display: flex;
  //     justify-content: center;
  //     align-items: center;
  //     flex-direction: column;
  //   }
  // }
}
</style>
