<template>
  <div class="information">
    <EsHeaderView />
    <div class="information-content app-container app-center">
      <h1>Information</h1>
      <div class="information-content-list">
        <el-badge v-for="(item, index) in testData" :key="index" is-dot>
          <div class="flex-between" @click="openCustomerService">
            <div class="user-avatar flex-start">
              <img :src="require('@/assets/image/user.png')" alt="user" />
              <div>
                <span>xxxxx</span>
                <p>
                  My bf liked it and tbh I regret buyingMy bf liked it and tbh I
                  regret buyingMy bf liked it and tbh I regret buyingMy bf liked
                  it and tbh I regret buyingMy bf liked it and tbh I regret
                  buyingMy bf liked it and tbh I regret buyingMy bf liked it and
                  tbh I regret buyingMy bf liked it and tbh I regret buyingMy bf
                  liked it and tbh I regret buyingMy bf liked it and tbh I
                  regret buyingMy bf liked it and tbh I regret buyingMy bf liked
                  it and tbh I regret buyingMy bf liked it and tbh I regret
                  buyingMy bf liked it and tbh I regret buyingMy bf liked it and
                  tbh I regret buyingMy bf liked it and tbh I regret buying
                </p>
              </div>
            </div>
            <div>just</div>
          </div>
        </el-badge>
      </div>
      <div class="information-content-pagination">
        <el-pagination
          background
          layout="prev, pager, next"
          class="es-pagination"
        />
      </div>
    </div>
    <EsCustomerService v-model="customerServiceShow" />
    <EsFooterView />
  </div>
</template>

<script>
  import EsCustomerService from "@/components/customService";
  export default {
    name: "EsInformation",
    components: { EsCustomerService },
    data() {
      return {
        customerServiceShow: false,
        testData: [],
      };
    },
    methods: {
      openCustomerService() {
        console.log("open");
        this.customerServiceShow = true;
      },
    },
  };
</script>

<style lang="scss">
  .information {
    &-content {
      padding: 0 10px;
      h1 {
        font-weight: 600;
        font-size: 24px;
        color: var(--color-title);
        margin: 30px 0;
      }

      &-pagination {
        width: 100%;
        text-align: center;
        padding: 10px 0 40px 0;
      }

      &-list {
        margin-bottom: 30px;
        .el-badge {
          width: 100%;
          margin: 0 0 13px 0;
          padding: 12px 15px;
          border: 1px solid var(--color-border);
          border-radius: 4px;
          cursor: pointer;
        }
        .user-avatar {
          font-size: 12px;
          img {
            margin-right: 8px;
            width: 45px;
            height: 45px;
          }
          p {
            padding-right: 20px;
            overflow: hidden;
            text-overflow: ellipsis;
            display: -webkit-box;
            -webkit-line-clamp: 1;
            -webkit-box-orient: vertical;
            margin-top: 4px;
          }
        }
      }
    }
  }
</style>
