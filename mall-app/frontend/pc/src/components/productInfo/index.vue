<template>
  <div class="product-info" v-loading="loading" v-if="show">
    <div class="product-info-content flex-start">
      <div class="product-info-left">
        <vue-photo-zoom-pro :out-zoomer="true">
          <swiper
            class="swiper gallery-top"
            :options="swiperOptionTop"
            ref="swiperTop"
            @slideChange="onSlideChange()"
            @mouseenter.native="mouseEnter"
            @mouseleave.native="mouseLeave"
          >
            <swiper-slide
              v-for="(item, index) in imgList ? imgList : productImgs"
              :key="index"
            >
              <!-- <img :src="item" alt="" /> -->
              <img-preview :url="item" />
            </swiper-slide>
          </swiper>
          <template slot="zoomer">
            <img-zoomer
              :url="imgList ? imgList[curIndex] : productImgs[curIndex]"
            ></img-zoomer>
          </template>
        </vue-photo-zoom-pro>
        <swiper
          class="swiper gallery-thumbs"
          :options="swiperOptionTop.thumbs.swiper"
          ref="swiperThumbs"
        >
          <swiper-slide
            v-for="(item, index) in imgList ? imgList : productImgs"
            :key="index"
            @click.native="change(index)"
            :class="index == curIndex ? 'active' : ''"
          >
            <img :src="item" alt="" />
          </swiper-slide>
        </swiper>
      </div>
      <div class="product-info-right">
        <h1 class="product-info-right-title">
          {{ productDetails.name }}
        </h1>
        <div class="product-info-right-info">
          <div class="product-info-right-info-top flex-between">
            <div class="product-info-right-info-price flex-start">
              <h2>{{ $t("message.home.retailPrice" /**零售价 */) }}</h2>
              <span class="price"
                >${{
                  numberFormatFn(
                   this.price ??  productDetails.discountPrice ?? productDetails.sellingPrice
                  )
                }}</span
              > 
            </div>
            <div
              class="product-info-right-info-price del flex-start"
              v-if="![null, undefined].includes(productDetails.discountPrice)"
            >
              <h2>{{ $t("message.home.originPrice" /** 原价*/) }}</h2>
              <span class="price"
                >${{ numberFormatFn(this.skuPrice?? productDetails.sellingPrice) }}</span
              >
            </div>
            <div class="product-info-right-info-tool flex-start">
              <div
                class="product-info-right-info-tool-item flex-start"
                @click="showServiceDialog"
              >
                <i
                  class="el-icon-service"
                  style="color: var(--color-main); font-size: 20px"
                ></i>
                <span v-if="itemname =='FamilyMart'">{{$t("message.home.联系商家")}}</span>
                <span v-else>{{ $t("message.home.service" /**客服 */) }}</span>
              </div>
              <div
                class="product-info-right-info-tool-item flex-start"
                @click="collectEvent"
              >
                <!-- <img :src="require('@/assets/image/Star.png')" alt="Star" /> -->
                <i
                  :class="
                    productDetails.isKeep === 1
                      ? 'el-icon-star-on'
                      : 'el-icon-star-off'
                  "
                />
                <span>{{ $t("message.home.collect" /**收藏 */) }}</span>
              </div>
            </div>
          </div>

          <div class="product-info-right-info-des">
            <div class="product-info-right-info-des-item flex-start">
              <div>
                <span style="margin-right: 5px">{{
                  $t("message.home.sold" /**销售量 */)
                }}</span>
                <span>{{ numberFormatA(productDetails.soldNum) }}</span>
              </div>
              <div>
                <span style="margin-right: 5px">{{
                  $t("message.home.pageviews" /**浏览量 */)
                }}</span>
                <span>{{ numberFormatA(productDetails.viewsNum) }}</span>
              </div>
            </div>
            <div class="product-info-right-info-des-item flex-start">
              <span class="label-title">
                {{ $t("message.home.goodsShip") }}
              </span>
              <span>{{ $t("message.home.goodsShipTips") }}</span>
            </div>
            <div class="product-info-right-info-des-item flex-start">
              <span class="label-title">
                {{ $t("message.home.goodsFreight") }}
              </span>
              <div class="freight-tips">
                <p>
                  {{
                    Number(productDetails.freightAmount) === 0
                      ? $t("message.home.goodsFreeShipping")
                      : `$${numberFormatFn(productDetails.freightAmount ?? 0)}`
                  }}
                </p>
                <el-tooltip effect="dark" placement="top">
                  <div slot="content">
                    <p style="line-height: 18px">
                      {{ $t("message.home.goodsFreightTips1") }}
                    </p>
                    <p style="line-height: 18px">
                      {{ $t("message.home.goodsFreightTips2") }}
                    </p>
                    <p style="line-height: 18px">
                      {{ $t("message.home.goodsFreightTips3") }}
                    </p>
                  </div>
                  <i class="el-icon-info"></i>
                </el-tooltip>
              </div>
            </div>
            <div class="product-info-right-info-des-item flex-start">
              <span class="label-title">
                {{ $t("message.home.quantity" /**數量 */) }}
              </span>
              <el-input-number
                :key="productDetails.buyMin"
                @blur="inputNumBlur"
                v-model="num"
                :min="productDetails.buyMin ?? 1"
                :max="maxNum"
              />
            </div>
            <div v-if="productDetails.canSelectAttributes">
              <div
                class="product-info-right-info-des-item flex-start product-attr"
                v-for="(item, i) in productDetails.canSelectAttributes
                  .goodAttrs"
                :key="item.attrId"
              >
                <span class="label-title sku-titile">
                  {{ currentSkuTitle[i] }}
                </span>

                <div v-if="item.attrValues[0].icon" class="attr-container">
                  <div
                    v-for="(attrItem, index) in item.attrValues"
                    :key="attrItem.attrValueId"
                    @click="!attrItem.disabled&&changeColor(index, attrItem)"
                    :class="[
                      'attr-item',
                      currentIndex == index && 'active',
                      attrItem.disabled && 'disabled',
                    ]"
                  >
                    <div
                      class="attr-img"
                      @click="
                        !attrItem.disabled&&changeGoodAttr(item.attrId, attrItem.attrValueId, i)
                      "
                    >
                      <img :src="attrItem.iconImg" alt="" />
                    </div>
                  </div>
                </div>
                <el-select
                  @change="(v) => changeGoodAttr(item.attrId, v)"
                  :value="goodsAttrObj[item.attrId]"
                  :placeholder="`${$t('message.home.Opt')}${item.attrName}`"
                  v-else
                >
                  <el-option
                    :value="attrItem.attrValueId"
                    :label="attrItem.attrValueName"
                    v-for="attrItem in item.attrValues"
                    :key="attrItem.attrValueId"
                    :disabled="attrItem.disabled"
                  >
                  </el-option>
                </el-select>
              </div>
            </div>

            <div class="product-info-right-info-des-item flex-start">
              <span class="label-title">
                {{ $t("message.home.totalPrice" /**总价 */) }}
              </span>
              <p>
                <span class="price">${{ totalPrice }}</span>
                <!-- <span class="del-line">Total Price: $56.12</span> -->
              </p>
            </div>
          </div>
          <div class="product-info-right-info-buy">
            <el-button type="primary" @click="buy" :disabled='isIntDis'>
              {{ $t("message.home.buyNow" /**立即购买 */) }}
            </el-button>
            <div :class="['addcart', 'flex-start',isIntDis&&'disBtn']" @click="addCard" >
              <span>
                {{ $t("message.home.addCart" /** 添加购物车*/) }}
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>
    <EsOnlineServiceView v-model="showOnlieService" />
  </div>
</template>

<script>
import { mapActions, mapGetters, mapMutations } from "vuex";
import { ES_TOKEN } from "@/common";
import { notLogin } from "@/common/pageHook";
import { numberFormat, openChatPage, numberFormatA } from "@/util";
import Bus from "@/util/bus";
import vuePhotoZoomPro from "vue-photo-zoom-pro";
import { ImgZoomer, ImgPreview } from "vue-photo-zoom-pro";
import "vue-photo-zoom-pro/dist/style/vue-photo-zoom-pro.css";
export default {
  name: "EsProductionInfo",
  props: {
    id: {
      type: String,
      default: "0",
    },
  },
  components: {
    vuePhotoZoomPro,
    ImgZoomer,
    ImgPreview,
  },
  data() {
    return {
      itemname: process.env.VUE_APP_ITEM_NAME,
      currentIndex: 0,
      swiperOptionTop: {
        // loop: false,
        // loopedSlides: 3, // looped slides should be the same
        // spaceBetween: 10,
        centeredSlides: true,
        spaceBetween: 10,
        autoplay: {
          delay: 2500,
          disableOnInteraction: false,
        },
        thumbs: {
          swiper: {
            el: ".gallery-thumbs", //定义关联的thumbs的class
            spaceBetween: 10,
            slidesPerView: "auto",
            slideToClickedSlide: true,
            watchSlidesVisibility: true,
          },
          slideThumbActiveClass: "slide-thumb-active",
        },
      },
      num: 1,
      minbuy: 1,
      goodsAttrObj: {},
      showOnlieService: false,
      loading: false,
      isCollect: false,
      canSelectAttributes: [],
      price: null,
      curIndex: 0,
      currentSkuTitle: [],
      imgList: "",
      skuPrice: null,
      maxNum:100,
      isIntDis: true,
      show:true,
      min: 1
      // skuSellingPrice:0
    };
  },
  computed: {
    ...mapGetters({
      productDetails: "productDetails/productDetails",
    }),
    ...mapGetters(["isLogin"]),
    totalPrice() {
      if (this.price) {
        return numberFormat(this.$big(this.num).times(this.price));
      } else {
        return numberFormat(
          this.$big(this.num).times(
            this.productDetails.discountPrice ??
              this.productDetails.sellingPrice ??
              0
          )
        );
      }
    },
    productImgs() {
      return new Array(10)
        .fill("")
        .map((_, index) => this.productDetails[`imgUrl${index + 1}`])
        .filter((item) => !!item);
    },
  },
  watch: {
    productDetails: {
      handler(newValue, oldValue) {
        this.minbuy = newValue.minbuy ?? '1'
        if (newValue.canSelectAttributes) {
         if (newValue.canSelectAttributes?.goodAttrs.length){
          // console.log('newValue.canSelectAttributes?.goodAttrs.length->', newValue.canSelectAttributes?.goodAttrs.length );
           newValue.canSelectAttributes?.goodAttrs.forEach((x) => {
            this.goodsAttrObj[x.attrId] = x.attrValues[0].attrValueId;
          });
          // console.log('222 ->', 222);
          this.getAttrNameAndSkuId();
         }
        }else{
          this.isIntDis = false
        }
      },
      deep: true,
      immediate: true,
    },
  },

  async mounted() {
    sessionStorage.setItem("path", "1")
    this.maxNum = Number(localStorage.getItem('maxBuy') || 100) 
    if (this.id && this.id !== "0") {
      try {
        this.loading = true;
        await this.requestProductDetails({
          sellerGoodsId: this.id,
        });
        
      } finally {
        console.log("productDetails ->", this.productDetails);
        this.loading = false;
      }
    }
    Bus.$on("cancelKeep", (id) => {
      if (this.productDetails.id == id) {
        this.info();
      }
    });
    Bus.$on("keepProduct", (id) => {
      if (this.productDetails.id == id) {
        this.info();
      }
    });
  },
  beforeDestroy() {
    localStorage.setItem(
      "seller_cache",
      JSON.stringify({
        id: this.productDetails.seller.id,
        name: this.productDetails.seller.name,
      })
    );
    this.updateProductDetails({ seller: {} });
  },
  methods: {
    numberFormatA,
    async info() {
      await this.requestProductDetails({
        sellerGoodsId: this.id,
        token: localStorage.getItem(ES_TOKEN),
      });
    },
    mouseEnter() {
      this.$refs.swiperTop.$swiper.autoplay.stop();
    },
    mouseLeave() {
      this.$refs.swiperTop.$swiper.autoplay.start();
    },
    changeColor(index, info) {
      this.currentIndex = index;
    },
    numberFormatFn(num) {
      return numberFormat(num);
    },

    inputNumBlur() {
      // this.num = 1;
      let maxCount = localStorage.getItem('maxBuy')
      // console.log(' maxCount->',maxCount );
      var pattern = /^[1-9][0-9]*$/;
      if (!pattern.test(this.num)) {
        // input 框绑定的内容为空
        this.num = "1";
      } else {
        if (this.num == undefined) {
          this.num = "1";
        }
        if (this.num > maxCount) {
          this.num = maxCount;
        }
      }
    },

    ...mapActions({
      requestProductDetails: "productDetails/requestProductDetails",
      requestCollectGoods: "user/requestCollectGoods",
      requestCollectGoodsDel: "user/requestCollectGoodsDel",
    }),
    ...mapMutations({
      updateCheckProductPay: "shopCart/updateCheckProductPay",
      updateProductDetails: "productDetails/updateProductDetails",
    }),
    onSlideChange() {
      this.curIndex = this.$refs.swiperTop.$swiper.activeIndex;
    },
    change(index) {
      this.$refs.swiperTop.$swiper.slideTo(index);
      this.curIndex = index;
    },

    changeGoodAttr(attrId, valueId, index, bool) {
      // console.log('111 ->', 111);
      const obj = { ...this.goodsAttrObj };
      obj[attrId] = valueId;
      this.goodsAttrObj = obj;
      const disAttr = new Set();
      const allGood = this.productDetails?.canSelectAttributes?.goodAttrs;
      const temparr = JSON.parse(JSON.stringify(this.goodsAttrObj));

      if (allGood.length === Object.keys(this.goodsAttrObj).length) {
        allGood.forEach((item, i) => {
          if (i != index) {
            item.attrValues.forEach((attr, j) => {
              temparr[item.attrId] = attr.attrValueId;
              const { skuId } = this.getAttrNameAndSkuId(true, temparr);
              if (skuId == -1) {
                disAttr.add(attr.attrValueId);
              }
            });
          }
        });
      }
      this.productDetails?.canSelectAttributes?.goodAttrs.forEach((item) => {
        item.attrValues.forEach((attr) => {
          attr.disabled = disAttr.has(attr.attrValueId);
        });
      });
      this.getAttrNameAndSkuId();
      !bool && this.changeGoodAttr(attrId, valueId, index, true)
    },
    getAttrNameAndSkuId(find, obj) {
      const { skus } = this.productDetails.canSelectAttributes ?? {};
      if (obj && "undefined" in obj) {
        delete obj[undefined];
      }
      const attrIds = find ? Object.keys(obj) : Object.keys(this.goodsAttrObj);
      console.log('attrIds ->',attrIds );
      const finde = find ? obj : this.goodsAttrObj;
      const sku = skus?.find((x) => {
        let length = 0;
        if(x.attrs && x.attrs.length > 0){
          x.attrs.forEach((attr) => {
          if (
            attrIds.includes(attr.attrId) &&
            attr.attrValueId == finde[attr.attrId]
          ) {
            length += 1;
          }
        });
        }

        return length == attrIds.length;
      }) || { skuId: -1 };
      let checkAttrName = "";

      const attrs = this.productDetails.canSelectAttributes?.goodAttrs;
      if (attrIds.length > 0) {
        attrIds.forEach((attrId) => {
          const a = attrs.find((attr) => attr.attrId == attrId);
          const { attrValueName } = a.attrValues.find(
            (value) => value.attrValueId === this.goodsAttrObj[attrId]
          );
          checkAttrName += `${a.attrName} : ${attrValueName}   `;
        });
      }
      this.currentSkuTitle = checkAttrName.split("  ");
      this.price = sku.discountPrice || sku.sellingPrice || this.productDetails.price;
      this.skuPrice = sku.sellingPrice;
      this.imgList = sku?.img;
      this.isIntDis = sku.skuId == -1;
      // console.log('skuId ->', sku);
      return {
        checkAttrName,
        img: sku.img,
        skuId: sku.attrs?.length == 0 ?'-1':sku.skuId,
        price: this.price
      };
    },

    buy() {
      if (!this.isLogin) {
        this.$router.push("/login");
        this.$emit("handleBuy");
        return;
      }
      const isShelf = this.productDetails.isShelf;
      if (!isShelf) {
        this.$message({
          type: "warning",
          message: this.$t("message.home.productAvailable"),
        });
        return;
      }
      const { skuId, checkAttrName, price } = this.getAttrNameAndSkuId();
      const attrs = this.productDetails.canSelectAttributes?.skus;
      const a = attrs?.find((attr) => attr.skuId == skuId);
      const zoomImg = a?.coverImg;
      this.updateCheckProductPay([
        {
          title: this.productDetails.name,
          checkList: [new Date().getTime()],
          checkAll: true,
          isIndeterminate: false,
          list: [
            {
              ...this.productDetails,
              checkTotal: this.num,
              skuid: skuId,
              checkAttrName,
              price,
              Identifier: new Date().getTime(),
              zoomImg: zoomImg ? zoomImg : "",
            },
          ],
        },
      ]);
      this.$router.push("/settlement");
      this.$emit("handleBuy");
    },
    addCard() {
      if (this.isIntDis){
        return;
      }
      if (notLogin()) {
        return;
      }
      const isShelf = this.productDetails.isShelf;
      if (!isShelf) {
        this.$message({
          type: "warning",
          message: this.$t("message.home.productAvailable"),
        });
        return;
      }
      
      const shopCart = this.$store.state.shopCart.shopCart;
      const { skuId, checkAttrName, price } = this.getAttrNameAndSkuId();
      const attrs = this.productDetails.canSelectAttributes?.skus;
      const a = attrs?.find((attr) => attr.skuId == skuId);
      const zoomImg = a?.coverImg;
      const count = this.num;
      const sellerName = this.productDetails.seller.name;
      let str1 = shopCart.some((item) => {
        if (skuId !== -1  ) {
          return item.skuid == skuId;
        } else {
          return item.id == this.productDetails.id;
        }

      });
      this.isIntDis = false
     let isSellerName = shopCart.filter((item)=>item.seller.name == sellerName)
      
      
      if (str1 && isSellerName.length) {
        this.$message({
          message: this.$t(
            "message.home.addCartMessageFaild" /**添加到购物车成功 */
          ),
          type: "warning",
        });
      } else {
        shopCart.push({
          ...this.productDetails,
          skuid: skuId,
          checkAttrName,
          zoomImg: zoomImg ? zoomImg : "",
          count,
          price,
          Identifier: new Date().getTime(),
        });
        this.$store.commit("shopCart/updateShopCart", shopCart);
        this.$message({
          message: this.$t(
            "message.home.addCartMessage" /**添加到购物车成功 */
          ),
          type: "success",
        });
      }
    },
    async collectEvent() {
      if (notLogin()) {
        return;
      }
      try {
        if (this.productDetails.isKeep === 1) {
          await this.requestCollectGoodsDel({
            sellerGoodsId: this.productDetails.id,
            token: localStorage.getItem(ES_TOKEN),
          });
          this.$message.warning(this.$t("message.home.cancelSuccess"));
          Bus.$emit("updateCollect", this.productDetails.id);
        } else {
          await this.requestCollectGoods({
            sellerGoodsId: this.productDetails.id,
            token: localStorage.getItem(ES_TOKEN),
          });
          this.$message.success(this.$t("message.home.collectionSuccess"));
          Bus.$emit("updateUnKeep", this.productDetails.id);
        }

        await this.requestProductDetails({
          sellerGoodsId: this.id,
          token: localStorage.getItem(ES_TOKEN),
        });
      } catch (err) {}
    },
    showServiceDialog() {
      if (notLogin()) {
        return;
      }
      const sellerId = this.productDetails.seller.id;
      const name = this.productDetails.seller.name;
      openChatPage(
        this.$store.state.token,
        sellerId,
        name,
        this.productDetails.id
      );
      // const prefix = config.HOST_URL + "/chat/#/pc/yellow?";
      // const suffix = `token=${
      //   this.$store.state.token
      // }&partyid=${sellerId}&name=${name}&productId=${
      //   this.productDetails.id
      // }&lang=${getCurrentLang().lang}`;

      // window.open(prefix + suffix, "_blank");

      // if (!notLogin()) {
      //   this.showOnlieService = true;
      // }

      // openChatPage(localStorage.getItem('ES_TOKEN'), this.productDetails.seller.id, this.productDetails.seller.name)
    },
  },
};
</script>

<style lang="scss">

html[dir="rtl"]{ 
  .product-info-right-info-des-item div:first-child{
    margin-right: 0 !important;
  }
  .product-info-left{
    margin-right: 0 !important;
    margin-left: 22px !important;
  }
  .product-details-merchant,.titleRe{
    margin-right: 17px;
    margin-left: 0;
  }
  .product-details-merchant-top h1{
    margin-right: 10px;
    margin-left: 0;
  }
  .product-info-right-info-price h2{
    padding-right: 0;
    padding-left: 8px;
  }
  .product-info-right-info-tool-item {
    margin-right: 0;
    margin-left: 30px;
    span{
      margin-right: 6px;
      margin-left: 0;
    }
  }
  .product-info-right-info-des{
    .label-title{
      margin-right: 0;
    }
    .el-select{
      width: 200px;
    }
    .product-attr {
      align-items: flex-start !important;
    }
  }
  .sku-titile{
    display: inline-block;
    text-align: right;
    width: 100%;
  }
  
}
.product-info {
  margin-top: 3px;

  &-content {
    align-items: flex-start;
  }

  &-left {
    width: 378px;
    margin-right: 22px;

    .gallery-top {
      width: 378px;
      height: 378px;
      border: 1px solid var(--color-border);
      border-radius: 4px;
      .swiper-slide {
        width: 378px;
        height: 378px;
        display: flex;
        justify-content: center;
        align-items: center;
        box-sizing: border-box;
        padding: 10px;
        img {
          max-width: 100%;
          max-height: 100%;
          object-fit: contain;
        }
      }
    }
    .selector {
      z-index: 2 !important;
    }
    .out-zoomer {
      z-index: 8 !important;
      background: #fff;
      img{
        width: 100%;
        height: 100%;
        object-fit: contain;
      }
    }
    .gallery-thumbs {
      height: 89px;
      margin-top: 15px;

      .swiper-slide {
        width: 87px;
        height: 89px;
        border: 1px solid var(--color-border);
        box-sizing: border-box;
        border-radius: 4px;
        padding: 5px;
        cursor: pointer;
        img {
          width: 100%;
          height: 100%;
          max-width: 87px;
          object-fit: cover;
        }
      }
      .active {
        border: 1px solid var(--color-main);
      }
      .slide-thumb-active {
        border-color: var(--color-main) !important;
        border-width: 2px !important;
      }

      // .swiper-slide-active {
      //   // opacity: 1;
      // }
    }
  }

  &-right {
    max-width: 563px;

    &-title {
      font-weight: 600;
      font-size: 20px;
      line-height: 30px;
      color: var(--color-black);
      margin-bottom: 14px;
      word-break: break-all;
    }

    &-info {
      &-top {
        width: 100%;
        padding: 18px 0;
        border-top: 1px solid var(--color-border);
        border-bottom: 1px solid var(--color-border);
      }

      &-price {
        h2 {
          min-width: 10px;
          text-align: left;
          font-weight: 400;
          font-size: 12px;
          color: var(--color-subtitle);
          padding-right: 8px;
        }

        &.del {
          text-decoration: line-through;

          h2 {
            width: auto;
            min-width: 10px;
            padding-right: 2px;
          }

          .price {
            font-size: 14px;
            color: var(--color-price);
          }
        }
      }

      &-tool {
        &-item {
          cursor: pointer;
          margin-right: 30px;

          &:last-child {
            margin-right: 0;
          }

          span {
            color: var(--color-title);
            margin-left: 6px;
          }

          .el-icon-star-off {
            font-size: 18px;
            color: var(--color-main);
          }

          .el-icon-star-on {
            font-size: 18px;
            color: var(--color-main);
          }
        }
      }

      &-des {
        font-weight: 400;
        font-size: 12px;
        color: var(--color-subtitle);

        &-item {
          margin-top: 25px;

          div:first-child {
            margin-right: 20px;
          }
        }

        .del-line {
          text-decoration: line-through;
          margin-left: 27px;
        }

        .label-title {
          display: inline-block;
          min-width: 67px;
          margin-right: 16px;
        }
        .product-attr {
          flex-direction: column;
          align-items: baseline !important;
          .label-title {
            margin-bottom: 10px;
          }
        }
        .attr-container {
          width: 100%;
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(54px, 54px));
          grid-column-gap: 10px;
          grid-row-gap: 5px;
          align-content: center;
          padding-bottom: 4px;
        }
        .active {
          border: 1px solid var(--color-main);

          border-radius: 4px;
          .attr-img {
            border: none !important;
          }
        }
        .disabled {
          opacity: 0.5;
          // cursor: not-allowed;
          border: 1px dashed #e6e6e6;
          cursor: no-drop !important;
          .attr-img {
            border: none !important;
            -webkit-filter: grayscale(100%);
            -moz-filter: grayscale(100%);
            -ms-filter: grayscale(100%);
            -o-filter: grayscale(100%);
            filter: grayscale(100%);
            filter: gray;
          }
        }
        .attr-item {
          // width: 100%;
          // display: flex;
          // flex-wrap: wrap;
          margin-right: 0 !important;
          cursor: pointer;

          .attr-img {
            width: 54px;
            height: 54px;
            padding: 5px;
            border-radius: 4px;
            border: 1px solid var(--color-border);
            img {
              width: 100%;
              height: 100%;
              object-fit: cover;
            }
          }
        }
      }

      &-buy {
        width: 100%;
        text-align: center;
        margin-top: 72px;
        margin-bottom: 40px;
        display: flex;
        justify-content: space-between;
        .el-button {
          width: 45%;
          max-width: 570px;
          height: 44px;
          font-weight: 700;
          font-size: 14px;
          padding: 0;
        }
        .addcart {
          width: 45%;
          max-width: 570px;
          height: 44px;
          font-weight: 700;
          font-size: 14px;
          padding: 0;
          justify-content: center;
          color: var(--color-main);
          background: linear-gradient(0deg, #fff7ec, #fff7ec), #eeeeee;
          border: 1px solid var(--color-main);
          border-radius: 4px;
          cursor: pointer;
          will-change: filter;
          transition: filter 500ms;
          &:hover {
           filter: drop-shadow(0 0 4px var(--color-main));
            // color: var();
          }
        }
      }

      .price {
        font-weight: 500;
        font-size: 16px;
        color: var(--color-price);
      }
    }
  }
}

.freight-tips {
  display: flex;
  align-items: center;

  i {
    margin-left: 10px;
    cursor: pointer;
    font-size: 16px;

    &:hover {
      color: #000;
    }
  }
}
.disBtn{
    opacity: .5;
    cursor: no-drop !important;
}
</style>
