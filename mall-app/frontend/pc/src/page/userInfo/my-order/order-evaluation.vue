<template>
  <div
    class="evaluation-list"
    style="width: 866px; margin-top: 24px"
    v-loading="loading"
  >
    <div
      class="page-title"
      style="cursor: pointer; margin-bottom: 20px; margin-left: 34px"
      @click="goBack"
    >
      <i class="el-icon-arrow-left"></i> {{ $t("message.home.myOrder") }}/{{
        $t("message.home.Submitareview")
      }}
    </div>
    <div
      class="evaluation-item"
      v-for="(item, index) in orderGoods"
      :key="item.id"
    >
      <div style="margin-left: 40px; margin-top: 30px">
        <div class="product-item">
          <el-image
            style="width: 62px; height: 62px"
            fit="scale-down"
            :src="item.goodsIcon"
            alt="order-detail-product"
          />
          <div class="info">
            <div class="tit">{{ item.goodsName }}</div>
            <div
              style="margin-top: 9px; font-size: 12px"
              v-if="item.attributes && item.attributes.length > 0"
            >
              {{
                item.attributes
                  .map((it) => `${it.attrName}:${it.attrValue}`)
                  .join(" ")
              }}
            </div>
            <div class="price">${{ numberFormatFn(item.goodsReal) }}</div>
            <el-rate
              v-model="rateMap[item.goodsId]"
              :disabled="resultMap[item.goodsId]"
            />
          </div>
        </div>

        <el-input
          v-model="contentMap[item.goodsId]"
          class="content"
          type="textarea"
          :placeholder="$t('message.home.evaluateOrderPlaceholder')"
          resize="none"
          :disabled="resultMap[item.goodsId]"
          :maxlength="1000"
          show-word-limit
        />

        <div style="height: 15px" />

        <span>{{ $t("message.home.evaluateInput") }}</span>

        <el-upload
          :data="uploadParams"
          style="margin-top: 10px"
          :action="UploadApi"
          :on-change="(_, files) => handleFilesChange(files, item.goodsId)"
          list-type="picture-card"
          :disabled ="isUpload"
        >
          <img
            src="@/assets/image/bxs_camera-plus.png"
            style="width: 25.54px; height: 22.81px"
          />
          <div slot="file" slot-scope="{ file }">
            <img
              class="el-upload-list__item-thumbnail"
              :src="file.url"
              alt=""
            />
            <span class="el-upload-list__item-actions">
              <span
                class="el-upload-list__item-preview"
                @click="handlePictureCardPreview(file)"
              >
                <i class="el-icon-zoom-in"></i>
              </span>
              <span
                v-if="!disabled"
                class="el-upload-list__item-delete"
                @click="handleRemove(file, item.goodsId)"
              >
                <i class="el-icon-delete"></i>
              </span>
            </span>
          </div>
        </el-upload>
      </div>
      <el-divider v-if="index < orderGoods.length - 1"></el-divider>
    </div>
    <div class="action">
      <el-button @click="submit" :disabled="disabled">
        {{ $t("message.home.Submitareview") }}
      </el-button>
    </div>
    <el-dialog :visible.sync="dialogVisible">
      <img width="100%" :src="dialogImageUrl" alt="" />
    </el-dialog>
  </div>
</template>

<script>
import { mapGetters, mapActions } from "vuex";
import { numberFormat } from "@/util";
import { UploadApi, AddOrderEvaluateList } from "@/api";
export default {
  name: "order-evaluation-dialog",
  props: {
    value: {
      type: Boolean,
      default: false,
    },
    // currentOrderInfo: {
    //     type: Object,
    //     default: () => { },
    // },
    refresh: {
      type: Function,
    },
  },
  data() {
    return {
      // currentOrderInfo: this.$route.params?.currentOrderInfo || {},
      // dialogVisible: this.value || false,
      orderId: this.$route.query.orderId,
      loading: false,
      rateMap: {},
      contentMap: {},
      imagesMap: {},
      resultMap: {},
      dialogImageUrl: "",
      isUpload:false,
      dialogVisible: false,
      disabled: false,
      UploadApi,
      uploadParams: {
        moduleName: "evaluate",
        token: localStorage.getItem("ES_TOKEN"),
      },
    };
  },
  mounted() {
    if (this.orderId) {
      this.requestData();
    }
  },
  computed: {
    ...mapGetters({
      orderGoods: "order/orderGoods",
    }),
  },
  watch: {
    orderGoods(newValue) {
      let rateMap = {};
      let contentMap = {};
      let resultMap = {};

      newValue.forEach((item) => {
        rateMap[item.goodsId] = 5;
        contentMap[item.goodsId] = "";
        resultMap[item.goodsId] = false;
      });

      this.rateMap = { ...rateMap };
      this.contentMap = { ...contentMap };
      this.resultMap = { ...resultMap };
    },

  },
  methods: {
    ...mapActions({
      requestOrderGoodsList: "order/requestOrderGoodsList",
      requestOrderEvaluationList: "order/requestOrderEvaluationList",
    }),
    uploadFile(params, goodsId) {
      console.log(goodsId, params);
    },

    handleRemove(file, goodsId) {
      const index = this.imagesMap[goodsId]?.findIndex(
        (x) => x.uid == file.uid
      );
      index >= 0 && this.imagesMap[goodsId]?.splice(index, 1);
    },
    handlePictureCardPreview(file) {
      this.dialogImageUrl = file.url;
      this.dialogVisible = true;
    },

    handleFilesChange(files, goodsId) {
      if (files.length >8) {
        this.$message.warning(this.$t("message.home.最多上传9张图片"));
        this.isUpload = true
      }else{
        this.imagesMap[goodsId] = files;
      }
      
    },

    goBack() {
      this.$router.push("/userInfo/my-order");
    },
    getRate(id) {
      if (this.rateMap[id] < 2) {
        return 3;
      } else if (this.rateMap[id] < 4) {
        return 2;
      }
      return 1;
    },
    async requestData() {
      try {
        this.loading = true;
        await this.requestOrderGoodsList({ orderId: this.orderId });
      } finally {
        this.loading = false;
      }
    },
    async submit() {
      // const content = this.contentMap[item.goodsId]?.trim() ?? ''
      // if (!content) {
      //   this.$message.warning(this.$t('message.home.evaluateOrderPlaceholder'))
      //   return
      // }

      try {
        this.btnLoading = true;
        this.disabled = true;
        // await this.requestOrderEvaluationList({
        //     sellerGoodsId: item.goodsId,
        //     evaluationType: this.getRate(),
        //     rating: this.rateMap[item.goodsId],
        //     orderId: this.orderId,
        //     content: content || this.$t('message.home.defaultRate'),
        // })
        // this.resultMap[item.goodsId] = true
        const evaluationAdds = [];
        // const canContinue = true;
        for (let { goodsId } of this.orderGoods) {
          const evaluation = {
            sellerGoodsId: goodsId,
            evaluationType: this.getRate(goodsId),
            rating: this.rateMap[goodsId],
            content: this.contentMap[goodsId],
          };

          const notUpload = this.imagesMap[goodsId]?.filter((x) => !x.response);

          if (notUpload && notUpload.length > 0) {
            this.$message({
              // title: this.$t('message.home.successTips'),
              message: this.$t("message.home.evaluationUploading"),
              type: "error",
            });
            return;
          }

          const imageUrls =
            this.imagesMap[goodsId]
              ?.filter((x) => x.response && x.response.code == "0")
              .map((x) => x.response.data) || [];

          for (let i = 0; i < imageUrls.length; i++) {
            evaluation[`imgUrl${i + 1}`] = imageUrls[i];
          }
          evaluationAdds.push(evaluation);
        }

        let res = await AddOrderEvaluateList({
          orderId: this.orderId,
          evaluationAdds,
        });

        if (res.code == 0) {
          this.$router.push({path:"/userInfo/my-order",replace:true});
          this.$notify({
            title: this.$t("message.home.successTips"),
            message: this.$t("message.home.evaluateOrderSuccess"),
            type: "success",
          });
        }else{
          // this.$message({
          //   title: this.$t('message.home.fuilTips'),
          //   message: this.$t("message.home.evaluateOrderFuil"),
          //   type: "error",
          // });
        }

        // this.$emit("closeDetails");
        // this.refresh && this.refresh()
      } finally {
        this.btnLoading = false;
        this.disabled = false;
      }
    },

    numberFormatFn(num) {
      return numberFormat(num);
    },
  },
};
</script>

<style lang="scss" scoped>
.evaluation-list {
  /deep/ .el-upload--picture-card {
    width: 70px;
    height: 70px;
  }

  /deep/ .el-upload {
    width: 70px;
    height: 70px;
    line-height: 70px;
  }

  /deep/ .el-upload-list--picture-card .el-upload-list__item {
    width: 70px;
    height: 70px;
    line-height: 70px;
  }

  /deep/ .el-upload-list--picture-card .el-upload-list__item-thumbnail {
    width: 70px;
    height: 70px;
    line-height: 70px;
  }

  .evaluation-item {
    + .evaluation-item {
      margin-top: 18px;
    }

    .product-item {
      display: flex;
      flex-direction: row;

      img {
        width: 62px;
        height: 62px;
      }

      .info {
        margin-left: 18px;
        flex: 1;

        .price {
          font-weight: 500;
          font-size: 16px;
          color: var(--color-main);
          margin-top: 8px;
        }

        .el-rate {
          margin-top: 5px;
        }
      }
    }

    .content {
      margin-top: 25px;

      .el-textarea__inner {
        border: 1px solid #efefef;
        height: 70px;
      }
    }
  }
}

.action {
  // padding: 20px 0;
  display: flex;
  align-items: center;
  // justify-content: center;
  margin-top: 52px;
  margin-left: 34px;

  .el-button {
    width: 480px;
    height: 44px;
    color: #fff;
    background: var(--color-main);
    border-color: var(--color-main);
    border-radius: 4px;
  }
}
</style>
