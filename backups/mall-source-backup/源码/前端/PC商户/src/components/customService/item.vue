<template>

  <div>
    <div
      :key="source.id"
      :class="`${
        source.isSelf
          ? 'customer-service-item customer-service-rigth'
          : 'customer-service-item customer-service-left'
      }`"
    >
      <div
        v-if="source.isSelf"
        class="customer-service-item-message flex-start"
      >
        <div
          v-if="source.contentType === 'img'"
          class="customer-service-item-image"
        >
          <h3>{{ $formatZoneDate(source.date) }}</h3>
          <el-image
            :src="source.content"
            :preview-src-list="[source.content]"
          />
        </div>
        <div v-else class="customer-service-item-text">
          <h3>{{ $formatZoneDate(source.date) }}</h3>
          <!-- <h3>{{calculateTime(source.date)}}</h3> -->
          <p v-html="source.content"></p>
        </div>
        <el-image class="user-icon" :src="userAvater" />
      </div>
     
      <div v-else class="customer-service-item-message flex-start">
        <el-image
          :class="itemname=='FamilyMart' ?'user-icon martIcon':'user-icon'"
         :src="itemname=='FamilyShop' ? require(`@/assets/image/${itemname}/sevice.png`):itemname =='TikTok' ?require(`@/assets/image/${itemname}/${itemname}logo.png`) : itemname =='FamilyMart' || 'Shopee' ?require(`@/assets/image/${itemname}/${itemname}logo.svg`) :require(`@/assets/image/${itemname}/logo.svg`)"
        />
        <div
          v-if="source.contentType === 'img'"
          class="customer-service-item-image"
        >
          <h3>{{ $formatZoneDate(source.date) }}</h3>
           <!-- <h3>{{calculateTime(source.date)}}</h3> -->
          <el-image
            :src="source.content"
            :preview-src-list="[source.content]"
          />
        </div>
        <div v-else class="customer-service-item-text">
          <h3>{{ $formatZoneDate(source.date) }}</h3>
          <p v-html="source.content"></p>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { getFullDate, isToday, isYesterday, getTime } from "@/util/imDate.js";
import dayjs from "dayjs";
import { mapGetters } from "vuex";
// import userAvater from "@/assets/image/head_16.jpg";
export default {
  name: "EsChartItem",
  props: {
    source: Object,
  },
  computed: {
    ...mapGetters({
      userInfo: "userInfo",
    }),
  },
  data() {
    return {
      itemname: process.env.VUE_APP_ITEM_NAME,
      imagePreviewId: "",
      imagePreviewStatus: "",
      userAvater: "",
    };
  },
  created() {
    this.userAvater = require(`@/assets/image/avatar/${
      this.userInfo.avatar || "1"
    }.png`);
  },
  methods: {
    calculateTime(time) {
      // console.log('time ->', time);
      // console.log('-----calculateTime-----', dayjs(time).unix())
      time = dayjs(time).unix();
      if (isToday(new Date(time * 1000))) {
        return getTime(new Date(time * 1000));
      } else if (isYesterday(time * 1000)) {
        return (
          this.$t("message.home.yesterday") + getTime(new Date(time * 1000))
        );
      } else {
        return getFullDate(new Date(time * 1000));
      }
    },
  },
};
</script>

<style lang="scss">
.customer-service {
  &-item {
    display: flex;
    align-items: flex-start;
    margin-bottom: 25px;
    .martIcon{
      border-radius: 0% !important;
    }
    .user-icon {
      width: 45px;
      height: 45px;
      border-radius: 50%;
    }
   

    &-message {
      align-items: flex-start;
    }

    &-text {
      flex: 1;
      width: 100%;
      max-width: 468px;
      margin: 0 20px;

      p {
        background-color: #fff;
        border: 1px solid var(--color-border);
        text-align: left;
        color: #000;
        padding: 10px;
        border-radius: 4px;
        font-size: 12px;
      }
    }

    &-image {
      flex: 1;
      width: 100%;
      max-width: 125px;
      margin: 0 20px;
    }

    h3 {
      color: var(--color-subtitle);
      margin-bottom: 10px;
      font-size: 12px;
      font-weight: 400;
    }
  }

  &-left {
    justify-content: flex-start;
  }

  &-rigth {
    justify-content: flex-end;

    h3 {
      text-align: right;
    }

    .customer-service-item-text p {
      background: #fef1db;
      border: 1px solid var(--color-main);
      border-radius: 4px;
    }
  }
}
</style>
