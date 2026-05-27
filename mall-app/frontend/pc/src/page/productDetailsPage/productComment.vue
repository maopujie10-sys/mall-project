<template>
  <div class="product-comment">
    <div class="p-header">
      <div class="title1">
        {{ this.$t("message.home.userEvaluation" /**用户评价 */) }}
        <span v-if="itemname !== 'Inchoi'">({{ productCommentNum || 0 }})</span>
       
      </div>
      <div style="display: flex; flex-direction: row">
        <div
          v-for="item in Object.keys(categoryNum)"
          @click="onEvaluationClick(item)"
          class="button"
          :class="item === evaluationTypeKey ? 'active' : ''"
          :key="item"
        >
          {{ categoryNum[item].text }}({{ categoryNum[item].num }})
        </div>
      </div>
    </div>
    <div
      class="product-comment-content"
      v-loading="loading"
      style="padding-top: 10px"
    >
      <div
        v-for="(item, index) in productComment"
        :key="index"
        class="product-comment-item"
      >
        <div class="product-comment-top flex-start">
          <div class="userInfo">
            <img
              :src="
                require(`@/assets/image/avatar/${
                  item.avatar || Math.floor(Math.random() * 20)
                }.png`)
              "
              alt="User"
            />
            <div>{{ item.userName }}</div>
          </div>
        </div>
        <div class="rate">
          <div class="rate-box">
            <el-rate disabled :value="item.rating"></el-rate>
            <span style="color: var(--color-main); font-size: 12px">{{
              $t("message.home.订单已完成")
            }}</span>
          </div>
        </div>
        <!-- <div v-if="item.attributes" class="attrbox">
          <div v-for="(i, d) in item.attributes" :key="d" class="attr">
            <div v-if="i.attrName">
              <span>{{ i.attrName }}</span
              >:<span>{{ i.attrValue }}</span>
            </div>
          </div>
        </div> -->
        <p class="product-comment-text">
          {{ item.content }}
        </p>
        <div>
          <el-image
            class="evaluation-img"
            v-for="url in evaluationImages[index]"
            :src="url"
            :key="url"
            :preview-src-list="evaluationImages[index]"
          >
          </el-image>
        </div>
        <span class="eval-time"
          ><span v-if="item.countryName && itemname !== 'Inchoi'&& itemname !== 'Green Mall'"
            >{{ item.countryName }}&nbsp;>>&nbsp; </span
          >{{ $formatZoneDate(item.evaluationTime) }}</span
        >
      </div>
    </div>
    <div>
      <el-empty
        :description="$t('message.home.noComments')"
        v-if="!productComment.length"
      ></el-empty>
    </div>
    <div class="product-comment-pagination" v-if="total > 5">
      <el-pagination
        background
        layout="prev,next"
        class="es-pagination"
        :current-page="pageNum"
        :page-size="pageSize"
        :total="total"
        :prev-text="$t('message.home.prevPage')"
        :next-text="$t('message.home.nextPage')"
        @current-change="currentChange"
      />
    </div>
  </div>
</template>

<script>
import { mapGetters, mapActions } from "vuex";
import { getProductEvaluationCategory } from "@/api";
// import { request } from "http";
export default {
  name: "EsProductComment",
  data() {
    return {
      loading: false,
      itemname: process.env.VUE_APP_ITEM_NAME,
      pageNum: 1,
      pageSize: 5,
      evaluationTypeKey: undefined,
      total: 0,
      categoryNum: {
        havePicture: {
          text: this.$t("message.home.hasImage"),
          num: "0",
          evaluationType: -2,
        },
        positiveComments: {
          text: this.$t("message.home.highOpinion"),
          num: "0",
          evaluationType: 1,
        },
        mediumReview: {
          text: this.$t("message.home.mediumOpinion"),
          num: "0",
          evaluationType: 2,
        },
        negativeComment: {
          text: this.$t("message.home.lowOpinion"),
          num: "0",
          evaluationType: 3,
        },
      },
      evaluationImages: [],
    };
  },
  computed: {
    ...mapGetters("productDetails", [
      "productDetails",
      "productComment",
      "productCommentPageInfo",
      "productCommentNum",
    ]),
  },
  filters: {
    abbreviatedName(str, frontLen = 2, endLen = 2) {
      let len = str.length - frontLen - endLen;
      let x = "";
      for (let i = 0; i < len; i++) {
        x += "*";
      }
      return (
        str.substring(0, frontLen) + x + str.substring(str.length - endLen)
      );
    },
  },
  watch: {
    async productDetails(newValue, oldValue) {
      if (newValue && oldValue && newValue.id !== oldValue.id) {
        this.requestCommend();
        this.requestEvaluationCategory();
      }
    },
  },
  methods: {
    ...mapActions("productDetails", ["requestRecommendLList"]),
    // subUsername(user) {
    //   if (user.indexOf("@") < 0) {
    //     let str = user.substring(2, user.length - 1);
    //     let name = user.replace(str, "***");
    //     return name;
    //   } else {
    //     let str = user.substring(1, user.indexOf("@"));
    //     let name = user.replace(str, "***");
    //     return name;
    //   }
    // },
    
    async requestCommend(params) {
      try {
        this.loading = true;
        params = params ?? {
          sellerGoodsId: this.productDetails.id,
          pageNum: this.pageNum,
          pageSize: this.pageSize,
        };
        await this.requestRecommendLList(params).then((res) => {
          const { pageInfo } = res;
          this.total = pageInfo.totalElements;
        });
      } finally {
        this.loading = false;
      }
      this.genImageList();
    },

    async requestEvaluationCategory() {
      const res = await getProductEvaluationCategory({
        goodId: this.productDetails.id,
      });
      if (res && res.code === "0") {
        for (let key in res.data) {
          this.categoryNum[key].num = res.data[key];
        }
      }
    },

    genImageList() {
      this.evaluationImages = [];
      for (let evaluation of this.productComment) {
        const imgUrls = Object.keys(evaluation)
          .filter((x) => x.includes("imgUrl") && !!evaluation[x])
          .map((x) => evaluation[x]);
        this.evaluationImages.push(imgUrls);
        if (evaluation.content == "") {
          evaluation.content = this.$t("message.home.用户未发表评论");
        }
        if (evaluation.content == "系统默认好评") {
          evaluation.content = this.$t("message.home.系统默认好评");
        }
      }
    },

    onEvaluationClick(key) {
      this.pageNum = 0;
      this.total = 0;
      this.evaluationTypeKey = key;
      this.requestCommend({
        sellerGoodsId: this.productDetails.id,
        pageNum: this.pageNum,
        pageSize: this.pageSize,
        evaluationType: this.categoryNum[key].evaluationType,
      });
    },

    currentChange(page) {
      this.pageNum = page;
      this.requestCommend();
    },
    timestampToTime(timestamp) {
      timestamp = timestamp ? timestamp : null;
      let date = new Date(timestamp); //时间戳为10位需*1000，时间戳为13位的话不需乘1000
      let Y = date.getFullYear() + "-";
      let M =
        (date.getMonth() + 1 < 10
          ? "0" + (date.getMonth() + 1)
          : date.getMonth() + 1) + "-";
      let D =
        (date.getDate() < 10 ? "0" + date.getDate() : date.getDate()) + " ";
      let h =
        (date.getHours() < 10 ? "0" + date.getHours() : date.getHours()) + ":";
      let m =
        (date.getMinutes() < 10 ? "0" + date.getMinutes() : date.getMinutes()) +
        ":";
      let s =
        date.getSeconds() < 10 ? "0" + date.getSeconds() : date.getSeconds();
      return $formatZoneDate(Y + M + D + h + m + s);
    },
    isInteger(num) {
      if (parseInt(num, 10) === num) {
        return num + ".0";
      } else {
        return num;
      }
    },
  },
};
</script>

<style lang="scss">
.product-comment {
  border: 1px solid var(--color-border);
  width: 957px;
  .product-comment-text {
    display: -webkit-box;
  }

  .button {
    display: flex;
    justify-content: center;
    align-items: center;
    padding: 4px 10px;
    // height: 28px;
    border-radius: 14px;
    color: #999999;
    margin-right: 13px;
    cursor: pointer;
    background: #eeeeee;

    &.active {
      color: #ffffff;
      // border: 1px solid var(--color-main);
      background: var(--color-main);
    }
  }

  .evaluation-img {
    width: 87px;
    height: 87px;
    border: 1px solid #eeeeee;
    border-radius: 4px;
    margin-right: 10px;
  }

  .p-header {
    display: flex;
    flex-direction: row;
    justify-content: space-between;
    align-items: center;
    border-bottom: 1px solid #eee;
    height: 70px;
    padding-left: 37px;
    padding-right: 16px;
    // padding-bottom: 30px;
    // background-color: #eee;
  }

  .title1 {
    font-weight: 600;
    font-size: 20px;
    color: var(--color-title);
    margin-left: 22px;
    // border-bottom: 1px solid var(--color-border);
    // padding: 20px 37px 19px 37px;
  }

  &-item {
    padding: 15px 40px;
    border-bottom: 1px solid #eee;
  }

  &-top {
    font-size: 12px;
    justify-content: space-between;

    .userInfo {
      display: flex;
      align-items: center;
      font-weight: 400;
      font-size: 12px;
      color: var(-color-black);
      margin-bottom: 4px;

      img {
        width: 31px;
        height: 31px;
        object-fit: cover;
        border-radius: 100%;
        margin-right: 8px;
      }

      span {
        color: var(--color-subtitle);
      }
    }
  }
  .rate {
    .rate-box {
      display: flex;
      align-items: center;
      font-size: 12px;
      color: #000;
    }
  }
  .eval-time {
    font-size: 12px;
    color: #999999;
    margin-top: 10px;
    display: inline-block;
  }
  &-text {
    font-weight: 400;
    font-size: 16px;
    padding: 10px 0;
    color: var(-color-black);
    display: inherit !important;
    word-wrap: break-word;
  }

  &-pagination {
    width: 100%;
    text-align: center;
    padding: 40px 0;
  }
  .attrbox {
    display: flex;
    font-size: 12px;
    color: #333;
    .attr {
      &:nth-child(2) {
        margin-left: 5px;
        padding-left: 5px;
        border-left: 1px solid #999;
      }
    }
  }
}
</style>
