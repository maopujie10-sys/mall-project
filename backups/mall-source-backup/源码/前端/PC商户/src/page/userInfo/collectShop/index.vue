<template>
  <div class="collect-content">
    <div class="page-title" style="cursor: pointer" @click="goBack">
      <i class="el-icon-arrow-left"></i>
      {{ $t("message.home.myFollowedShops") }}
    </div>
    <div v-loading="loading" class="content">
      <div v-if="listData.length" class="list-content">
        <div v-for="item in listData" :key="item.sellerId" class="item">
          <div class="avatar">
            <img :src="item.sellerVo.avatar" alt="" />
          </div>
          <div class="info">
            <div class="name">
              <p :title="item.sellerVo.name">{{ item.sellerVo.name || "-" }}</p>
              <el-button
                plain
                size="mini"
                round
                :loading="item.loading"
                @click="cancelFollow(item)"
                >{{ $t("message.home.myUnfollow") }}</el-button
              >
            </div>
            <div class="census">
              <div class="number">
                <p>
                  {{ $t("message.home.mySold" /**已售 */) }}：
                  {{ numberFormatA(item.sellerVo.soldNum ? item.sellerVo.soldNum +  item.sellerVo.fakeSoldNum :item.sellerVo.fakeSoldNum)  || "0"
                  }}
                </p>
                <p>
                  {{ $t("message.home.myPageviews" /**浏览量 */) }}：{{
                    numberFormatA(item.sellerVo.viewsNum) || "0"
                  }}
                </p>
              </div>
              <div class="bottom">
                <p>
                  {{ $t("message.home.myPraiseRate" /**好评率 */) }}：{{
                    (numberFormat(item.sellerVo.highOpinion) || "1") * 100
                  }}%
                </p>
                <el-button class="visiti-btn" @click="gotoStroe(item)">
                  {{ $t("message.home.visitStore" /**访问商店 */) }}
                </el-button>
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
        layout="prev,pager, next"
        :pager-count="5"
        class="es-pagination"
        :page-size="pageSize"
        :current-page="pageNum"
        :total="total"
        @current-change="currentChange"
      />
    </div>
  </div>
</template>

<script>
import { FocusSellerListApi, FocusSellerDelApi } from "@/api/userCenter";
import { numberFormat ,numberFormatA} from "@/util";
export default {
  name: "CollectShop",
  data() {
    return {
      listData: [],
      loading: true,
      pageNum: 1,
      pageSize: 8,
      total: 0,
    };
  },
  mounted() {
    this.$nextTick(() => {
      this.getListData();
    });
  },
  methods: {
    numberFormatA,
    numberFormat,
    currentChange(page) {
      this.pageNum = page;
      this.getListData();
    },

    goBack() {
      this.$router.go(-1);
    },

    getListData() {
      this.loading = true;
      const params = {
        pageNum: this.pageNum,
        pageSize: this.pageSize,
      };
      FocusSellerListApi(params)
        .then((res) => {
          const data = res.data;
          this.total = data.pageInfo?.totalElements || 0;
          data.pageList.forEach((item) => {
            item.loading = false;
          });
          this.listData = data.pageList;
          this.loading = false;
        })
        .catch(() => {
          this.loading = false;
        });
    },

    cancelFollow(data) {
      data.loading = true;
      FocusSellerDelApi({ sellerId: data.sellerId })
        .then(() => {
          data.loading = false;
          this.pageNum = 1;
          this.getListData();
        })
        .catch(() => {
          data.loading = false;
        });
    },

    gotoStroe(data) {
      this.$router.push({
        name: "store",
        query: { storeId: data.sellerId },
      });
    },
  },
};
</script>

<style lang="scss" scoped>
html[dir="rtl"] {
  .collect-content{
    padding-left: 0;
    padding-right: 50px;
     > .content > .list-content > .item > .info{
      padding-left: 0;
      padding-right: 10px;
    }
  }
}
.collect-content {
  width: 775px;
  padding-top: 32px;
  padding-left: 50px;
  > .content {
    margin-top: 15px;
    min-height: 120px;
    > .list-content {
      overflow: hidden;
      > .item {
        width: 350px;
        height: 120px;
        padding: 10px;
        font-size: 12px;
        float: left;
        border: 1px solid var(--color-border);
        margin-right: 25px;
        margin-bottom: 20px;
        border-radius: 4px;
        display: flex;
        &:nth-child(2n) {
          margin-right: 0;
        }
        > .avatar {
          width: 62px;
          height: 62px;
          overflow: hidden;
          display: flex;
          align-items: center;
          justify-content: center;
          > img {
            width: 100%;
            height: auto;
          }
        }
        > .info {
          flex: 1;
          padding-left: 10px;
          display: flex;
          flex-direction: column;
          justify-content: space-between;
          > .name {
            display: flex;
            align-items: flex-start;
            > p {
              flex: 1;
              padding-right: 5px;
              font-size: 14px;
              color: #000;
              line-height: 18px;
              position: relative;
              top: 3px;
              overflow: hidden;
              text-overflow: ellipsis;
              display: -webkit-box;
              -webkit-line-clamp: 2;
              -webkit-box-orient: vertical;
            }
            .el-button--mini {
              padding: 0;
              height: 24px;
              width: 80px;
            }
          }
          > .census {
            margin-top: 10px;
            font-size: 12px;
            color: #333;
            > .number {
              display: flex;
              align-items: center;
              justify-content: space-between;
            }
            > .bottom {
              margin-top: 5px;
              display: flex;
              justify-content: space-between;
              align-items: center;
            }
            .visiti-btn {
              height: 26px;
              background: var(--color-submain1);
              border: 1px solid var(--color-main);
              border-radius: 27px;
              font-size: 12px;
              color: var(--color-main);
              line-height: 0px;
              &:hover {
                border-color: var(--color-submain);
              }
            }
          }
        }
      }
    }
  }
}
</style>
