<template>
  <div class="classification">
    <EsHeaderView />
    <div class="app-container app-center">
      <h1 class="classification-title">
        {{ this.$t("message.home.classification" /**分类 */) }}
      </h1>
      <div style="min-width: 1200px">
        <EsLoadingView :loading="loading">
          <el-row :gutter="20">
            <el-col
              :xs="24"
              :sm="12"
              :md="12"
              :lg="12"
              :xl="12"
              v-for="(item, index) in categoryList"
              :key="index"
              @click.native="gotoCommodityPage(item.categoryId)"
            >
              <el-row class="classification-item" type="flex" align="middle" :gutter='10'>
                <el-col :span="8">
                  <div class="cla-img">
                    <img :src="item.iconImg" alt="" />
                  </div>
                </el-col>
                <el-col :span="15">
                  <div class="classification-item-text ">
                    <h2>{{ item.name }}</h2>
                    <div v-if="item.subList.length">
                      <span v-for="(i,index) in item.subList" :key="index" @click.stop="gotoCommodityPage(i.categoryId,item.categoryId)">
                        {{ i.name}}
                      </span>
                    </div>
                    <p v-else>{{ item.des}}</p>
                  </div>
                </el-col>
              </el-row>
            </el-col>
          </el-row>
          <div class="no-data" v-if="!categoryList.length && !loading">
            <el-empty :description="$t('message.home.noData')"></el-empty>
          </div>
        </EsLoadingView>
      </div>
    </div>
    <EsFooterView />
  </div>
</template>

<script>
// import { mapActions, mapGetters } from "vuex";
import { CategoryApiList } from "@/api/home";
export default {
  name: "EsClassification",
  data() {
    return {
      loading: false,
      pageNum: 1,
      categoryList:[]
    };
  },
  computed: {
    // ...mapGetters("home", ["categoryList"]),
  },
  mounted() {
    // this.requestData();
    this.getCategoryList();
  },
  methods: {
    // ...mapActions("home", ["requestCategoryList"]),
    async getCategoryList() {
      const res = await CategoryApiList();
      // console.log('res ->', res);
      // this.categoryList = res.data.filter((item) => {
      //   if (item.name && item.subList.length > 0) {
      //     item.subList = item.subList.filter((subItem) => subItem.name);
      //   }
      //   return item.name;
      // });
      this.categoryList = res.data.slice(0, 20);
    },
    // async requestData(params = {}) {
    //   try {
    //     this.loading = true;
    //     this.requestCategoryList({
    //       pageNum: this.pageNum,
    //       pageSize: "50",
    //       ...params,
    //     });
    //   } finally {
    //     this.loading = false;
    //   }
    // },
    currentChange(page) {
      this.pageNum = page;
      this.requestCategoryList({ pageNum: page });
    },
    gotoCommodityPage(id, parentId) {
      this.$router.push({ name: "commodity", query: { id ,parentId} });
    },
  },
};
</script>

<style lang="scss">
.classification {
  &-title {
    font-weight: 700;
    font-size: 24px;
    color: var(--color-title);
    margin: 24px 0;
  }
  &-item {
    border: 1px solid var(--color-border);
    padding: 24px;
    border-radius: 4px;
    margin: 0 !important;
    margin-bottom: 20px !important;
    height: 234px;
    cursor: pointer;
    .el-col {
      height: 100%;
    }
    .cla-img{
        height: 170px;
        width: 170px;
        overflow: hidden;
        margin-right: 10px;
    img {
          width: 100%;
          height: 100%;
          object-fit: cover;
          // min-height: 179px;
          // min-width: 179px;
        }
    }
   
    &-text {
      h2 {
        font-weight: 700;
        font-size: 20px;
        color: var(--color-title);
        margin-bottom: 14px;
      }
      p {
        font-weight: 400;
        font-size: 13px;
        color: #333;
        line-height: 1.5;
        overflow: hidden;
        height: 140px;
        text-overflow: ellipsis;
        display:-webkit-box; //作为弹性伸缩盒子模型显示。
        -webkit-box-orient:vertical; //设置伸缩盒子的子元素排列方式--从上到下垂直排列
        -webkit-line-clamp:7;
      }
      span {
        &:hover{
          color: var(--color-main);;
          font-size: 15px;
        }
        // color: blue;
      }
    }
  }
}
</style>
