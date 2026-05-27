<template>
  <div class="count">
    <div
      class="count-item"
      v-for="(item, index) in data"
      :key="index"
      @click="openPage(item)"
    >
      <div>
        <span>{{ item.count }}</span>
        <p>{{ item.desc }}</p>
      </div>
    </div>
  </div>
</template>
<script>
  import { keepGoodsCount, focusSellerCount } from "@/api/userCenter";
  export default {
    data() {
      return {
        data: [
          {
            count: 0,
            desc: this.$t("message.home.myCommodityCollection"),
            path: "/userInfo/collect-goods?index=3",
          },
          {
            count: 0,
            desc: this.$t("message.home.myFollowedShops"),
            path: "/userInfo/collect-shop",
          },
        ],
      };
    },
    mounted() {
      this.$nextTick(() => {
        this.getCount();
      });
    },
    methods: {
      getCount() {
        keepGoodsCount().then((res) => {
          if (!Number(res.code)) {
            this.data[0].count = res.data;
          }
        });

        focusSellerCount().then((res) => {
          if (!Number(res.code)) {
            this.data[1].count = res.data;
          }
        });
      },
      openPage(data) {
        this.$router.push(data.path);
      },
    },
  };
</script>
<style lang="scss">
  .count {
    &-item {
      width: 248px;
      height: 83px;
      display: flex;
      justify-content: center;
      align-items: center;
      background: var(--color-little-grey);
      text-align: center;
      margin-bottom: 20px;
      border: 1px solid var(--color-border);
      cursor: pointer;
      p {
        font-size: 12px;
        color: var(--color-title);
      }
      span {
        font-size: 18px;
        color: var(--color-main);
      }
    }
  }
</style>
