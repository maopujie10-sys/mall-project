<template>
  <div class="shipping-address">
    <div class="page-header">
      <div class="page-title" style="cursor: pointer" @click="goBack">
        <i class="el-icon-arrow-left"></i>
        {{ $t("message.home.shippingAddress") }}
      </div>
      <el-button
        type="primary"
        icon="el-icon-plus"
        size="small"
        @click="addAddressHandle"
        >{{ $t("message.home.addNewAddress") }}</el-button
      >
    </div>
    <div class="page-content" v-loading="loading">
      <div v-if="addressList.length" class="address_list">
        <div class="item" v-for="item in addressList" :key="item.id">
          <div class="info">
            <div class="name-and-mobile">
              <span class="name">{{ item.contacts }}</span>
              <span class="mobile">&nbsp;&nbsp;+{{ item.phone }}</span>
            </div>
            <!-- <el-switch
              :value="item.use"
              :active-value="1"
              :inactive-value="0"
              @change="setAddressDefalut($event, item)"
            /> -->
            <el-popover placement="bottom" width="250" trigger="click" ref="addressPup">
              <i class="el-icon-more" slot="reference"></i>
              <ul class="address-menu">
                <li @click="editAddrss(item)">{{ $t("message.home.edit") }}</li>
                <li @click="setAddressDefalut(1, item)">
                  {{ $t("message.home.markDefaultAddress") }}
                </li>
                <li @click="delAddress(item)">
                  {{ $t("message.home.delete") }}
                </li>
              </ul>
            </el-popover>
          </div>
          <!-- {{ item.country }} {{ item.province }} {{ item.city }} -->
          <div class="address">
            {{ item.country }} {{ item.province }} {{ item.city }}
            {{ item.address }}
          </div>
        </div>
      </div>
      <el-empty
        v-if="!addressList.length && !loading"
        :description="$t('message.home.noData')"
      ></el-empty>
    </div>

    <EsAddressDialog
      v-model="addAdressDialogVisible"
      :data="currentAddressInfo"
      :isEdit="isAddressEdit"
      :prov="prov"
      :itemCity="itemCity"
      :key="Math.random()"
    />
  </div>
</template>

<script>
import { mapGetters, mapActions } from "vuex";
import EsAddressDialog from "@/components/addAddress";
export default {
  name: "EsAddress",
  components: { EsAddressDialog },
  data() {
    return {
      loading: true,
      addAdressDialogVisible: false,
      currentAddressInfo: null,
      isAddressEdit: false,
      prov: "",
      itemCity: "",
    };
  },
  computed: {
    ...mapGetters("user", ["addressList"]),
  },
  methods: {
    ...mapActions("user", [
      "requestAddressList",
      "requestAddressEdit",
      "requestAddressAdd",
      "requestAddressDel",
    ]),
    async setAddressDefalut(value, item) {
      // console.log('item ->', item);
      try {
        this.loading = true;
        item.contacts = encodeURIComponent(item.contacts);
        await this.requestAddressEdit({
          ...item,
          ...{ use: value },
        });
      } finally {
        this.$refs.addressPup.forEach((item) => {
          item.showPopper = false;
        });
        this.loading = false;
      }
    },
    async delAddress(item) {
      try {
        this.loading = true;
        await this.requestAddressDel({ id: item.id });
      } finally {
        this.loading = false;
      }
    },
    editAddrss(item) {
      this.isAddressEdit = true;
      this.addAdressDialogVisible = true;
      this.prov = item.province || '';
      this.itemCity = item.city || '';
      this.currentAddressInfo = { ...item };
    },
    addAddressHandle() {
      this.prov = ''
      this.itemCity = ''
      this.isAddressEdit = false;
      this.addAdressDialogVisible = true;
      this.currentAddressInfo = null;
    },
    goBack() {
      this.$router.push("/userInfo/setup");
    },
  },
  async mounted() {
    try {
      this.loading = true;
      await this.requestAddressList();
    } finally {
      this.loading = false;
    }
  },
};
</script>

<style lang="scss" scoped>
html[dir='rtl']{
  .shipping-address .address_list > .item{
    float: right;
    margin-right: 0;
    margin-left: 22px;
  }
}
.shipping-address {
  .page-header {
    width: 100%;
    display: flex;
    align-items: center;
    justify-content: space-between;
  }
  .page-content {
    min-height: 270px;
  }
  .address_list {
    margin-top: 20px;
    overflow: hidden;
    > .item {
      width: 270px;
      height: 110px;
      padding: 20px 10px;
      font-size: 12px;
      float: left;
      border: 1px solid var(--color-border);
      margin-right: 22px;
      margin-bottom: 20px;
      border-radius: 4px;
      &:nth-child(3n) {
        margin-right: 0;
      }

      > img {
        width: 60px;
        height: 60px;
      }

      > .info {
        display: flex;
        align-items: center;
        margin-bottom: 15px;
        .name-and-mobile {
          flex: 1;
          font-weight: 400;
          color: var(--color-title);
          span {
            display: inline-block;
            max-width: 110px;
            overflow: hidden;
            text-overflow: ellipsis;
            white-space: nowrap;
          }
        }
        .el-icon-more {
          font-size: 14px;
          color: var(--color-subtitle);
          margin-left: 10px;
          transform: rotate(90deg);
          cursor: pointer;
        }
      }

      > .address {
        color: var(--color-subtitle);
        font-weight: 500;
        margin-top: 5px;
        width: 100%;
        display: -webkit-box;
        overflow: hidden;
        -webkit-line-clamp: 2;
        -webkit-box-orient: vertical;
      }
    }
  }
}
.address-menu {
  > li {
    padding: 8px 10px;
    font-size: 12px;
    &:hover {
      cursor: pointer;
    }
  }
}
</style>
