<template>
  <div class="pro-container">
    <div class="product" v-if="item" @mouseenter="onEnterTd($event.target)" @mouseleave="onLeave($event.target)">
      <div class="discount" v-if="item.discountRatio">
        <span>{{ numberFormatFn(item.discountRatio) * 100 }} %</span>
        <br>
        <span>OFF</span>
      </div>
      <div @click="gotoDetails($event.target)">
        <div class="poster">
          <img v-if="item.imgUrl1" :src="item.imgUrl1" />
          <img v-else src="@/assets/image/morenImg.png" />
        </div>
        <h2>${{ numberFormatFn(item.discountPrice ?? item.sellingPrice) }}</h2>
        <div class="product-res">
          {{ $t("message.home.sold") }} {{ numberFormatA(item.soldNum) || 0 }}
        </div>
        <p>
          {{ item.name }}
        </p>
      </div>

      <div class="product-footer">
        <div>
          <i class="el-icon-shopping-cart-full"></i>
          <span class="buy-btn" @click="belike ? gotoDetails()  :buyNow()">
            {{ $t("message.home.buyNow" /**立即购买 */) }}
          </span>
        </div>
        <div>
          <i
            :class="keep ? 'el-icon-star-on' : 'el-icon-star-off'"
            @click="collect()"
            :style="keep ? 'color:var(--color-main)' : ''"
          ></i>
        </div>
      </div>
    </div>
    <el-dialog
      :independent-modal="true"
      :modal-append-to-body="true"
      :append-to-body="true"
      class="es-dialog"
      :visible.sync="dialogVisible"
      :center="true"
      :destroy-on-close="true"
      :lock-scroll="false"
    >
      <div slot="title" class="dialog-title">
        <span>{{ $t("message.home.addCart" /** 添加购物车*/) }}</span>
      </div>
      <div class="dialog-content" v-if="dialogVisible">
        <EsProductInfo :id="currentId" @handleBuy="handleBuy" />
      </div>
      <span slot="footer"></span>
    </el-dialog>
  </div>
</template>

<script>
  import EsProductInfo from "@/components/productInfo";
  import { numberFormat ,numberFormatA} from "@/util";
  import { mapActions } from "vuex";
  import { ES_TOKEN } from "@/common";
  import { notLogin } from "@/common/pageHook";
  import Bus from '@/util/bus'
  export default {
    name: "EsProduct",
    components: { EsProductInfo },
    props: {
      item: {
        type: Object,
        default: () => {},
      },
      belike: {
        type: Boolean,
        default: false,
      },
    },

    data() {
      return {
        dialogVisible: false,
        currentId: "",
        keep: false,
      };
    },
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
        this.$Gsap.to('.product',{
          delay: 0,
          duration: .5,
          scale:1,
          ease: "back.outIn(1.7)"
        })
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
        console.log("this.item ->", this.item);
        // const goodId = id
        if (notLogin()) {
          return;
        }
        // console.log(this.productDetails);
        // console.log('id ->', id);
        try {
          if (this.keep) {
            await this.requestCollectGoodsDel({
              sellerGoodsId: this.item.id,
              token: localStorage.getItem(ES_TOKEN),
            });
            // localStorage.setItem('keepProduct', true)
            // const  id = this.item.id 
            Bus.$emit('cancelKeep', this.item.id)
            this.$message.warning(this.$t("message.home.cancelSuccess"));
            // if (this.item.id )
          } else {
            await this.requestCollectGoods({
              sellerGoodsId: this.item.id,
              token: localStorage.getItem(ES_TOKEN),
            });
            Bus.$emit('keepProduct', this.item.id)
            this.$message.success(this.$t("message.home.collectionSuccess"));
          }

          // await this.requestProductDetails({
          //   sellerGoodsId: id,
          //   token: localStorage.getItem(ES_TOKEN),
          // });
        } finally {
          // this.$router.go(0)
          this.keep = !this.keep;
        }
      },
      handleBuy() {
        this.dialogVisible = false;
      },
      numberFormatFn(num) {
        return numberFormat(num);
      },
      numberFormatA(num) {
        return numberFormatA(num)
      }
    },
  };
</script>

<style lang="scss">
.pro-container{
  &:hover{
    .product{
      border: 1px solid var(--color-main);
    }
  }
}
  .product {
    border: 1px solid var(--color-border);
    padding: 0 8px 8px 8px;
    border-radius: 5px;
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
      right: 0;
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
      max-width: 165px;
      height: 165px;
      overflow: hidden;
    }
    img {
      width: 100%;
      height: 100%;
      max-width: 165px;
      height: 165px;
      object-fit: contain;
    }

    h2 {
      font-size: 16px;
      color: var(--color-price);
      margin-bottom: 6px;
      font-weight: 500;
    }

    p {
      font-size: 14px;
      font-weight: 400;
      min-height: 40px;
      line-height: 1.5;
      color: var(--color-title);
      max-width: 138px;
      overflow: hidden;
      text-overflow: ellipsis;
      display: -webkit-box;
      -webkit-line-clamp: 2;
      -webkit-box-orient: vertical;
      margin: 6px 0 15px 0;
    }

    &-footer {
      display: flex;
      justify-content: space-between;
      align-items: center;
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
