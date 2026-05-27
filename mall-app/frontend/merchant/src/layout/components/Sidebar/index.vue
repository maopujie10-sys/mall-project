<template>
  <div :class="{ 'has-logo': showLogo }">
    <div v-if="!isCollapse" class="merchant-info">
      <div style="position: relative">
        <el-image :alt="merchantInfo.name" :src="merchantInfo.avatar||avatar"
                  class="w-60 h-60 avatar active" style="border: solid 1px #e5e5e5;"/>
        <el-image :alt="merchantInfo.name" :src="getLevelIcon(merchantInfo.mallLevel)"
                  v-if="!settings.hideSellerLevel"
                  style="position: absolute;right: 0;bottom: 0;width: 20px;"
        />
      </div>
      <div class="merchant-info-content active">
        <el-tooltip effect="light" :hide-after="0" :content="merchantInfo.name" placement="right">
          <p class="store-name">
            {{ merchantInfo.name }}
          </p>
        </el-tooltip>
        <div style="height: 16px;width: 100%;font-size: 12px;text-align: center;padding-top: 6px;color: #989898;">
          <p><span>ID</span>&nbsp;<span>{{ userInfo.usercode }}</span></p>
        </div>
        <el-tooltip effect="light" :hide-after="0" :content="showUserName" placement="right">
          <p class="user-email">{{ showUserName }}</p>
        </el-tooltip>
        <el-button class="into-my-shop" type="primary" @click="intoShop">
          {{ $t('查看我的店铺') }}
        </el-button>
      </div>
    </div>
    <div v-else style="text-align: center; margin: 10px 0;border-radius: 50%;">
      <el-image :alt="merchantInfo.name" :src="merchantInfo.avatar||avatar" class="w-20 h-20 avatar"/>
    </div>
    <logo v-if="showLogo" :collapse="isCollapse"/>
    <el-scrollbar ref="scrollbar" :style="`height: calc(100vh - ${top}px);`" wrap-class="scrollbar-wrapper">
      <audio ref="chatAudio" style="display: none;">
        <source :src="require('@/assets/chat.mp3')" type="audio/mpeg">
      </audio>
      <audio ref="chatAudioDD" style="display: none;">
        <source :src="require('@/assets/dingdong.mp3')" type="audio/mpeg">
      </audio>
      <div v-if="!isCollapse&&totalUnprocessedOrder > 0" class="message-icon">
        {{ totalUnprocessedOrder }}
      </div>
      <div v-if="isCollapse" class="message-icon-only-red">
      </div>
      <el-menu :collapse="isCollapse" :collapse-transition="false" :default-active="activeMenu"
               :text-color="variables.menuText" menu-trigger="click"
               :unique-opened="true" active-text-color="#1552F0" background-color="#EDF2FF" mode="vertical"
               @select="handleSelect">
        <sidebar-item v-for="route in permission_routes" :key="route.path" :base-path="route.path" :item="route"/>
        <div style="width: 100%;height: 50px;background-color: #ffffff;"></div>
      </el-menu>
    </el-scrollbar>
  </div>
</template>

<script>
import {mapGetters} from "vuex";
import Logo from "./Logo";
import SidebarItem from "./SidebarItem";
import variables from "@/styles/variables.scss";
import {seller_info_action_post} from "@/api/user";
import {getOrigin} from "@/utils/utis";
import levela from '@/assets/level/a.png'
import levelb from '@/assets/level/b.png'
import levelc from '@/assets/level/c.png'
import levelo from '@/assets/level/o.png'
import levels from '@/assets/level/s.png'
import levelss from '@/assets/level/ss.png'
import levelsss from '@/assets/level/sss.png'
import settings from "@/settings";
import FormatNumberShow from "@/components/FormatNumberShow/index.vue";

export default {
  data() {
    return {
      userClick: false,
      top: '',
      storeName: '',
      n2: '',
      levela,
      levelb,
      levelc,
      levelo,
      levels,
      levelss,
      levelsss,
      settings
    }
  },
  components: {FormatNumberShow, SidebarItem, Logo},
  watch: {
    totalUnprocessedOrder(newVal, oldVal) {
      if (newVal - 0 > oldVal - 0) {//有新消息
        this.userClick && this.$refs["chatAudioDD"].play();
      }
    },
  },
  computed: {
    ...mapGetters(["permission_routes", "sidebar", "avatar", 'merchantInfo', 'userInfo']),
    showUserName() {
      let username = this.userInfo.username || this.userInfo.phone || this.userInfo.email
      if (username.indexOf('@') === -1) {
        username = '+' + username
      }
      return username
    },
    totalUnreadMessages() {
      return (this.$store.getters.totalUnreadMessages > 99 ? 99 : this.$store.getters.totalUnreadMessages) + ''
    },
    totalUnprocessedOrder() {
      return (this.$store.getters.totalUnprocessedOrder > 99 ? 99 : this.$store.getters.totalUnprocessedOrder) + ''
    },
    activeMenu() {
      const route = this.$route;
      const {meta, path} = route;
      // if set path, the sidebar will highlight the path you set
      if (meta.activeMenu) {
        return meta.activeMenu;
      }
      return path;
    },
    showLogo() {
      return this.$store.state.settings.sidebarLogo;
    },
    variables() {
      return variables;
    },
    isCollapse() {
      return !this.sidebar.opened;
    },
  },
  mounted() {
    var self = this, chatAudio = self.$refs["chatAudio"];
    this.seller_info_action()
    this.top = this.$refs.scrollbar.$el.getBoundingClientRect().top;
    document.addEventListener("click", audio);

    function audio() {
      self.userClick = true;
      chatAudio && (chatAudio.muted = false);
      document.removeEventListener("click", audio);
    }


    this.$watch("totalUnreadMessages", (newVal, oldVal) => {
      if (newVal - 0 > oldVal - 0) {//有新消息
        this.userClick && chatAudio && (location.hash != '#/chat/index') && chatAudio.play();
      }
    })
  },
  methods: {
    getLevelIcon(mallLevel) {
      switch (mallLevel) {
        case 'A':
          return this.levela
        case 'B':
          return this.levelb
        case 'C':
          return this.levelc
        case 'O':
          return this.levelo
        case 'S':
          return this.levels
        case 'SS':
          return this.levelss
        case 'SSS':
          return this.levelsss
        default:
          return this.levelo
      }
    },
    intoShop() {
      //打开新窗口，不显示地址栏
      window.open(getOrigin() + "/#/store?storeId=" + this.$store.getters.merchantInfo.id + '&lang=' + this.$store.getters.lang);
    },
    seller_info_action() {
      seller_info_action_post({}).then((res) => {
        // this.promotional = e.data
        this.storeName = res.data?.name
        this.$store.commit('user/CHANGE_MERCHANT_INFO', res.data)
      })
    },
    handleOpen(key, keyPath) {
      console.log(key, keyPath);
    },
    handleClose(key, keyPath) {
      console.log(key, keyPath);
    },
    handleSelect(e) {
      console.log(e);
    },
  }
};
</script>

<style lang="scss" scoped>
.merchant-info {
  display: flex;
  justify-content: center;
  align-items: center;
  flex-direction: column;
  padding: 30px 12px 15px 12px;
  //旋转动画
  @keyframes rotate {
    0% {
      transform: rotateY(360deg) scale(1);
      opacity: 0;
    }
    50% {
      transform: rotateY(180deg) scale(1);
      opacity: 0;
    }
    100% {
      ransform: rotateY(0deg) scale(1);
      opacity: 1;
    }
  }

  .avatar {
    transform: rotateY(180deg) scale(0);

    &.active {
      // 动画由快变慢
      animation: rotate 0.5s ease-in;
      transform: rotateY(360deg) scale(1);
    }
  }

  .store-name {
    word-wrap: break-word;
    word-break: normal;
    font-family: 'Roboto';
    font-style: normal;
    font-weight: 600;
    font-size: 14px;
    line-height: 16px;
    height: 16px;
    text-align: center;
    color: #333333;
    margin-top: 12px;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
    width: 120px;
    text-align: center;
  }

  .user-email {
    font-family: 'Roboto';
    font-style: normal;
    font-weight: 400;
    font-size: 12px;
    line-height: 14px;
    color: #333333;
    margin-top: 12px;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
    width: 120px;
    text-align: center;
  }

  .into-my-shop {
    min-width: 100px;
    padding: 0 12px;
    box-sizing: border-box;
    height: 30px;
    text-align: center;
    line-height: 28px;
    font-size: 14px;
    margin-top: 12px;
    cursor: pointer;
  }

  .merchant-info-content {
    height: auto;
    display: flex;
    justify-content: center;
    align-items: center;
    flex-direction: column;
    overflow: hidden;
    position: relative;
    transition: all 1s ease;
    opacity: 0;

    &.active {
      opacity: 1;
    }
  }

}

.sidebar-container {
  box-shadow: 2px 0px 4px rgba(0, 0, 0, 0.06);
}

.avatar {
  border-radius: 50%;
}

.message-icon {
  height: 20px;
  width: 20px;
  background-color: #F56C6C;
  color: #ffffff;
  border-radius: 50%;
  position: absolute;
  top: 76px;
  left: 180px;
  z-index: 999;
  font-size: 12px;
  text-align: center;
  line-height: 20px;
  transform: scale(0.8);

  &.order {
    top: 130px;
  }
}

.message-icon-only-red {
  position: absolute;
  left: 30px;
  top: 74px;
  width: 8px;
  height: 8px;
  z-index: 999;
  background-color: red;
  border-radius: 8px;

  &.order {
    top: 130px;
  }
}

::v-deep {
  .el-scrollbar__view {
    position: relative;
  }

  .el-image__error {
    font-size: 12px;
  }

  .el-menu {
    li,
    .el-submenu__title {
      background: #fff !important;
    }

    .el-submenu__title,
    .el-menu-item {
      color: #999 !important;
    }
  }

  .el-menu-item.is-active {
    background: #edf2ff !important;
    color: #1552f0 !important;
  }
}

</style>
