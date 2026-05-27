<template>
  <div>
    <el-card v-if="active<3&&show" class="set-boot-steps">
      <div style="display: flex;justify-content: center;">
        <el-steps :active="active" align-center class="set-boot-steps-content">
          <el-step :title="$t('店铺设置')"></el-step>
          <el-step :title="$t('店铺认证')"></el-step>
          <el-step :title="$t('上架商品')"></el-step>
        </el-steps>
      </div>
      <div style="margin-top: 30px;display: flex;justify-content: center;">
        <span>{{ $t('请您完善店铺信息以保证顾客能正常访问到您') }}</span>
      </div>
      <div style="margin-top: 20px;display: flex;justify-content: center;">
        <el-button v-if="active===0" type="primary" @click="intoPage">{{ $t('立即设置') }}</el-button>
        <el-button v-else-if="active===1" type="primary" @click="intoPage">{{ $t('查看认证') }}</el-button>
        <el-button v-else-if="active===2" type="primary" @click="intoPage">{{ $t('上架商品') }}</el-button>
      </div>
    </el-card>
  </div>
</template>

<script>
import request from "@/utils/request";

export default {
  name: "SetBootSteps",
  data() {
    return {
      active: 4,
      show: false
    }
  },
  computed: {
    merchantInfo() {
      return this.$store.getters.merchantInfo
    }
  },
  watch: {
    merchantInfo() {
      this.getData()
    },
  },
  mounted() {
    let active = this.active = this.getActive();
    if (active != 3) {
      request({
        url: "seller/seller!info.action",
        method: "post",
        isLoading: false,
        params: {}
      }).then((res) => {
        this.show = true
        this.$store.commit('user/CHANGE_MERCHANT_INFO', res.data);
      });
    }
  },
  methods: {
    getData() {
      this.active = this.getActive();
    },
    getActive() {
      let active = 0
      let merchantInfo = this.merchantInfo;
      if (merchantInfo?.onShelvesFlag === "1") {
        active = 3
      } else if (merchantInfo?.sellerKycFlag === "1") {
        active = 2
      } else if (merchantInfo?.sellerSettingFlag === "1") {
        active = 1
      }
      return active;
    },
    intoPage() {
      switch (this.active) {
        case 0:
          this.$router.push({path: '/other/shopSetting'})
          break;
        case 1:
          this.$router.push({path: '/other/shopSetting'})
          break;
        case 2:
          this.$router.push({path: '/shopList/library'})
          break;
      }
    }
  },
}
</script>

<style lang="scss" scoped>
.set-boot-steps {
  display: flex;
  justify-content: center;
  align-items: center;
  flex-direction: column;
  min-height: 186px;
  width: 100%;
  background: #FFFFFF;
  margin-bottom: 10px;
  box-sizing: border-box;

  .set-boot-steps-content {
    width: 530px;
    display: flex;
    justify-content: center;
  }
}
</style>
