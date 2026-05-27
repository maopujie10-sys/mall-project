<template>
  <div class="visit">
    <div class="visit-title">
      {{ title }}
    </div>
    <div v-if="collectSellerList.length" class="visit-item">
      <div
        class="visit-item-box"
        v-for="(item, index) in collectSellerList"
        :key="index"
      >
        <div class="visit-item-box-flex">
          <div class="avatar">
            <img :src="item.sellerVo.avatar" alt="" />
          </div>

          <div class="visit-item-desc">
            <span>{{ item.sellerVo.name }}</span>
            <div class="visit-item-text">
              {{ $t("message.home.mySold" /**已售 */) }}：{{
                numberFormatA(item.sellerVo.soldNum ? item.sellerVo.soldNum +  item.sellerVo.fakeSoldNum :item.sellerVo.fakeSoldNum) || "0"
              }}
            </div>
            <div class="visit-item-text">
              {{ $t("message.home.myPageviews" /**浏览量 */) }}：{{
                numberFormatA(item.sellerVo.viewsNum) || "0"
              }}
            </div>
            <div class="visit-item-text">
              {{ $t("message.home.myPraiseRate" /**好评率 */) }}：{{
                (numberFormat(item.sellerVo.highOpinion) || "1") * 100
              }}%
            </div>
          </div>
        </div>
        <el-button class="visit-btn" @click="gotoStroe(item)">
          {{ $t("message.home.visitStore" /**访问商店 */) }}
        </el-button>
      </div>
    </div>
    <el-empty v-else :description="$t('message.home.noData')"></el-empty>
  </div>
</template>
<script>
import { mapActions, mapGetters } from "vuex";
import { numberFormat ,numberFormatA} from "@/util";
export default {
  data() {
    return {
      title: this.$t("message.home.myFollowedShops"),
    };
  },
  computed: {
    ...mapGetters({
      collectSellerList: "user/collectSellerList",
    }),
  },
  mounted() {
    this.getDataList();
  },
  methods: {
    numberFormat,
    numberFormatA,
    gotoStroe(data) {
      this.$router.push({
        name: "store",
        query: { storeId: data.sellerId },
      });
    },
    ...mapActions({
      requestCollectSellerList: "user/requestCollectSellerList",
    }),
    getDataList() {
      this.requestCollectSellerList({ pageSize: 3 });
    },
  },
};
</script>
<style lang="scss">
.visit {
  width: 250px;
  border: 1px solid var(--color-border);
  &-title {
    width: 100%;
    height: 49px;
    line-height: 50px;
    font-size: 14px;
    border-bottom: 1px solid var(--color-border);
    padding-left: 12px;
    margin-bottom: 10px;
  }
  &-btn {
    width: 100%;
    height: 26px;
    background: var(--color-submain1);
    border: 1px solid var(--color-main);
    border-radius: 27px;
    margin: 10px 0 5px 0;
    font-size: 12px;
    color: var(--color-main);
    line-height: 0px;
  }
  &-item {
    width: 223px;
    margin: 0 auto;
    .avatar {
      width: 55px;
      height: 55px;
      display: flex;
      align-items: center;
      justify-content: center;
      > img {
        width: 100%;
        height: 100%;
        object-fit: cover;
        margin: 0;
      }
    }
    &-box {
      padding: 7px 12px;
      border: 1px solid var(--color-border);
      border-radius: 4px;
      margin-bottom: 10px;
      &-flex {
        display: flex;
        align-items: center;
      }
    }
    &-desc {
      flex: 1;
      padding-left: 10px;
      span {
        color: var(--color-black);
        font-size: 12px;
      }
    }
    &-text {
      color: var(--color-title);
      font-size: 10px;
      margin-top: 3px;
    }
  }
}
</style>
