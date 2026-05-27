<template>
  <div class="stroe">
    <div class="stroe-item flex-center">
      <div class="stroe-top flex-start">
        <img :src="item.avatar" alt="" />
        <div class="stroe-top-title">
          <div class="store_title">
            <h2>{{ item.name }}</h2>
          </div>
          <div class="flex-between">
            <div>
              <div class="stroe-top-introduce">
                <span>{{ $t("message.home.commodity") }}:</span>
                <span>{{ numberFormatA(item.sellerGoodsNum) }}</span>
              </div>
              <div class="stroe-top-introduce">
                <span>{{ $t("message.home.browse") }} :</span>
                <span>{{ numberFormatA(item.soldNum ? item.soldNum +item.fakeSoldNum : item.fakeSoldNum) || 0 }}</span>
              </div>
              <div class="stroe-top-introduce">
                <span>{{ $t("message.home.favorableRate") }}:</span>
                <span>{{ numberFormat(item.highOpinion || "1") * 100 }}%</span>
              </div>
            </div>
            <el-button
              @click="
                () => {
                  this.$router.push({
                    path: '/store',
                    query: { storeId: item.id },
                  });
                }
              "
            >
              {{ $t("message.home.visitStore") }} >
            </el-button>
          </div>
        </div>
      </div>
      <!-- <div class="stroe-bottom flex-start" v-if="showProduct">
        <div class="stroe-bottom-left">
          <img
            src="https://pro.jack123.shop/public/uploads/all/hZJvOuvoLUhaDp9tY90Zi4GD679Aj96VveZwVIT9.jpg"
            alt=""
          />
          <div class="amount">$14.99</div>
        </div>
        <div class="stroe-bottom-right">
          <div class="stroe-bottom-item">
            <img
              src="https://pro.jack123.shop/public/uploads/all/hZJvOuvoLUhaDp9tY90Zi4GD679Aj96VveZwVIT9.jpg"
              alt=""
            />
            <div class="amount">$56.12</div>
          </div>
          <div class="stroe-bottom-item">
            <img
              src="https://pro.jack123.shop/public/uploads/all/hZJvOuvoLUhaDp9tY90Zi4GD679Aj96VveZwVIT9.jpg"
              alt=""
            />
            <div class="amount">$56.12</div>
          </div>
        </div>
      </div> -->
    </div>
  </div>
</template>

<script>
import { numberFormat,numberFormatA } from "@/util";
export default {
  name: "EsStore",
  props: {
    showProduct: {
      type: Boolean,
      default: false,
    },
    item: {
      type: Object,
      default: () => {},
    },
  },
  data() {
    return {};
  },
  methods: {
    numberFormat,
    numberFormatA
  },
};
</script>

<style lang="scss">
.stroe {
  .store_title {
    overflow: hidden;
    text-overflow: ellipsis;
    display: -webkit-box;
    -webkit-line-clamp: 1;
    overflow: hidden;
    /*! autoprefixer: off */
    -webkit-box-orient: vertical;
  }
   &:hover &-item{
      border: 1px solid var(--color-main);
    }
  &-item {
    flex-direction: column;
    border: 1px solid var(--color-border);
    border-radius: 4px;
   
  }

  &-top {
    width: 100%;
    padding: 15px;

    img {
      width: 80px;
      height: 80px;
      border-radius: 50%;
      object-fit: cover;
    }

    &-title {
      flex: 1;
      margin-left: 15px;

      h2 {
        font-weight: 400;
        font-size: 14px;
        color: var(--color-black);
        margin-bottom: 6px;
      }

      .el-button {
        background: #fcf2e2;
        color: var(--color-main);
        border: 1px solid var(--color-main);
        border-radius: 27px;
        font-size: 12px;
        padding: 5px 10px;
        // margin-right: 10px;
        white-space: inherit;
        // flex: 0 0 1;
        width: 118px;
      }

      > div {
        width: 100%;
      }
    }

    &-introduce {
      font-weight: 400;
      font-size: 12px;
      color: var(--color-title);

      span:nth-child(1) {
        padding-right: 4px;
      }
    }
  }

  &-bottom {
    margin-top: 20px;
    padding: 10px;

    &-left {
      width: 173px;
      height: 163px;
      position: relative;

      img {
        max-width: 173px;
        max-height: 163px;
        width: 100%;
        height: 100%;
        border-radius: 4px;
      }
    }

    &-right {
      display: flex;
      justify-content: flex-start;
      align-content: center;
      flex-direction: column;
      flex: 1;
      margin-left: 5px;
      height: 163px;
    }

    &-item {
      position: relative;
      flex: 1;
      margin-bottom: 5px;

      img {
        flex: 1;
        width: 100%;
        height: 100%;
        border-radius: 4px;
      }
    }

    &-item:last-child {
      margin-bottom: 0;
    }

    .amount {
      position: absolute;
      bottom: 0;
      left: 0;
      width: 80px;
      height: 29px;
      line-height: 29px;
      font-weight: 500;
      font-size: 16px;
      color: var(--color-main);
      background: var(--color-white);
      opacity: 0.78;
      border-radius: 0px 0px 0px 4px;
      text-align: center;
    }
  }
}
</style>
