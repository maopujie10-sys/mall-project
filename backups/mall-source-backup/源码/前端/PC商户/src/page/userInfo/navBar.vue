<template>
  <div class="nav-bar">
    <div class="person">
      <div class="user-avatar">
        <img :src="avater" alt="" />
        <div class="cover-up" @click="gotoDashborad">
          {{ $t("message.home.修改头像") }}
        </div>
      </div>
      <p class="name">{{ userInfo.username }}</p>
      <p class="person-id">
        ID: {{ userInfo.usercode }}
        <i class="el-icon-copy-document" @click="copy"></i>
      </p>
    </div>
    <el-dialog
      :title="$t('message.home.头像选择')"
      :visible.sync="dialogVisible"
      width="442px"
      :center="false"
    >
      <div class="avater">
        <div
          class="avatar-item"
          v-for="i in 20"
          :key="i"
          @click="avatarChange(i)"
        >
          <img
            :src="require(`@/assets/image/avatar/${i}.png`)"
            alt=""
            class="img-avatar"
          />
          <img
            src="@/assets/image/wanc.png"
            v-if="i == currentAvatar"
            alt=""
            class="icon-avatar"
          />
        </div>
      </div>
      <span slot="footer" class="dialog-afooter">
        <el-button type="primary" @click="subAvatar()">{{
          $t("message.home.btnSure")
        }}</el-button>
      </span>
    </el-dialog>

    <el-divider />
    <ul>
      <li v-for="(item, i) in navList" :key="i" @click="changeNav(i)">
        <router-link :to="item.path">
          <span :class="currentIndex == i ? item.class + ' act iconfont' : item.class + ' iconfont'"></span>
          {{ item.name /**仪表板 */ }}
        </router-link>
      </li>
    </ul>
    <div
      style="
        display: flex;
        flex-direction: column;
        width: 100%;
        align-items: center;
        font-size: 14px;
        font-weight: 600;
        margin-top: 60px;
      "
    >
      <VueQr
        style="border-radius: 0px; margin-bottom: 16px"
        :size="132"
        :text="downAppUrl"
        :margin="0"
      />
      <span>{{ $t("message.home.scanAndDown") }}</span>
    </div>
  </div>
</template>
<script>
import { mapGetters, mapActions } from "vuex";
import { copyTextToClipboard } from "@/util";
import { changeUserAvatar } from "@/api/userCenter";
import VueQr from "vue-qr";
import { set } from "vue";
// import SvgIcon from '@/components/svgIcon'
export default {
  components: {
    VueQr,
  },

  data() {
    return {
      dialogVisible: false,
      name: "",
      personId: "",
      currentIndex: 0,
      avater: "",
      currentAvatar: 0,
      navList: [
        {
          path: "/userInfo/dashboard",
          class: "icon-yibiaopan",
          name: this.$t("message.home.dashboard" /**仪表板 */),
        },
        {
          path: "/userInfo/money-package",
          class: "icon-qianbao",
          name: this.$t("message.home.myPurse"),
        },
        {
          path: "/userInfo/my-order",
          class: "icon-xiugaidingdan",
          name: this.$t("message.home.myOrder"),
        },
        {
          path: "/userInfo/collect-goods",
          class: "icon-shangpinshoucang",
          name: this.$t("message.home.myCommodityCollection"),
        },
        {
          path: "/userInfo/collect-shop",
          class: "icon-guanzhudianpu",
          name: this.$t("message.home.myFollowedShops"),
        },
        {
          path: "/userInfo/setup",
          class: "icon-setup",
          name: this.$t("message.home.setUp"),
        },
      ],
    };
  },
  computed: {
    ...mapGetters(["userInfo"]),
    ...mapGetters({ downAppUrl: "home/downAppUrl" }),
  },
  created() {
    if (this.$route.query.index) {
      this.currentIndex = this.$route.query.index;
      localStorage.setItem("currentIndex", this.$route.query.index);
    } else {
      this.currentIndex = localStorage.getItem("currentIndex");
    }
    this.avater = require(`@/assets/image/avatar/${
      this.userInfo.avatar || "1"
    }.png`);
    this.currentAvatar = this.userInfo.avatar;
    if (window.history && window.history.pushState) {
      history.pushState(null, null, document.URL);
      window.addEventListener("popstate", this.goBack, false);
    }
  },
  watch: {
    "$store.state.user.currentIndex"(index) {
      this.currentIndex = index;
      localStorage.setItem("currentIndex", index);
    },
    // $route: function (to, from) {
    //   const paths = {
    //     "/userInfo/dashboard": 0,
    //     "/userInfo/collect-goods": 3,
    //     "/userInfo/collect-shop": 4,
    //     "/userInfo/order-return": 2,
    //   };

    //   this.currentIndex = paths[to.path] || this.currentIndex;

    //   if (
    //     from.path === "/userInfo/order-evaluation" ||
    //     from.path === "/userInfo/my-order"
    //   ) {
    //     this.$router.go(-1);
    //   }

    //   this.$router.push(to.path);
    // },
    userInfo(oldValue, newValue) {
      this.avater = require(`@/assets/image/avatar/${oldValue.avatar}.png`);
      this.currentAvatar = oldValue.avatar;
    },
  },
  mounted() {
    this.getUserInfo();
    this.avater = require(`@/assets/image/avatar/${this.currentAvatar}.png`);
  },
  deactivated() {
    // window.removeEventListener("popstate", this.goBack, false);
  },
  methods: {
    ...mapActions(["getUserInfo"]),
    avatarChange(i) {
      this.currentAvatar = i;
    },
    goBack() {
      console.log("location ->", location);
      const arr = [
        "#/userInfo/dashboard",
        "#/userInfo/money-package",
        "#/userInfo/my-order",
        "#/userInfo/collect-goods",
        "#/userInfo/collect-shop",
        "#/userInfo/setup",
      ];
      if (this.$route.query.index) {
        this.currentIndex = this.$route.query.index;
      } else {
        this.currentIndex = arr.findIndex((x) => x == location.hash);
      }
      if (
        location.hash == "#/userInfo/money-package/recharge" ||
        location.hash == "#/userInfo/money-package/withdraw"
      ) {
        this.currentIndex = 1;
      }
    },
    changeNav(i) {
      this.currentIndex = i;
      this.$store.state.user.currentIndex = i;
    },
    gotoDashborad() {
      this.dialogVisible = true;

      // if (this.$router.currentRoute.path !== "/userInfo/dashboard") {
      //   this.$router.push("/userInfo/dashboard?index=1");
      // }
    },
    subAvatar() {
      this.changeAvatar();
      // this.dialogVisible = false;
    },
    async changeAvatar() {
      if (this.currentAvatar !== this.userInfo.avatar) {
        const res = await changeUserAvatar({ idx: this.currentAvatar });
        if (res.code == "0") {
          this.$message.success(this.$t("message.home.successTips"));
          this.avater = require(`@/assets/image/avatar/${this.currentAvatar}.png`);
          this.getUserInfo();
        }
      }
      this.dialogVisible = false;
    },
    copy() {
      copyTextToClipboard(this.userInfo.usercode);
      this.$notify({
        title: this.$t("message.home.successTips" /**成功 */),
        message: this.$t("message.home.copySuccess" /**copySuccess */),
        type: "success",
      });
    },
  },
};
</script>
<style lang="scss" scoped>
html[dir='rtl']{
  .nav-bar ul span{
    margin-left: 5px;
    margin-right: 0;
  }
}
.nav-bar {
  width: 296px;
  color: var(--color-title);
  border-right: 1px solid var(--color-border);
  margin-top: -14px;
  .person {
    text-align: center;
    padding-top: 30px;
    cursor: pointer;
    display: flex;
    flex-direction: column;
    align-items: center;
  }
  /deep/ .el-dialog__title {
    text-align: left;
    padding-left: 15px;
    font-size: 16px;
  }
  // /deep/
  .avater {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(64px, 64px));
    grid-column-gap: 28px;
    grid-row-gap: 12px;
    align-content: center;
    padding: 0 27px;
    .avatar-item {
      width: 64px;
      height: 64px;
      margin: 8px;
      position: relative;
      border-radius: 100%;
      cursor: pointer;
      .img-avatar {
        width: 64px;
        height: 64px;
        border-radius: 100%;
      }
      .icon-avatar {
        width: 20px;
        height: 20px;
        position: absolute;
        bottom: 0;
        right: -5px;
      }
    }
  }
  /deep/ .el-dialog__footer {
    border: none;
  }
  .dialog-afooter {
    width: 70%;
    padding-bottom: 25px;
    /deep/ .el-button {
      width: 100%;
      padding-left: 0;
      text-align: center;
    }
  }
  .user-avatar {
    width: 74.88px;
    height: 74.88px;
    position: relative;
    &:hover .cover-up {
      display: block;
    }
    img {
      width: 74.88px;
      height: 74.88px;
      border-radius: 50%;
    }
    .cover-up {
      width: 100%;
      height: 100%;
      border-radius: 50%;
      background: rgba(0, 0, 0, 0.7);
      position: absolute;
      color: #fff;
      text-align: center;
      line-height: 74px;
      top: 0;
      left: 0;
      display: none;
    }
  }

  .name {
    font-size: 18px;
    margin: 8px 0;
    width: 200px;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }

  .person-id {
    font-size: 12px;
    margin: 0;
  }

  .el-divider {
    background: var(--color-border);
  }

  .el-button {
    text-align: left;
    padding-left: 32px;
    color: var(--color-white);
  }

  ul {
    padding-left: 32px;
    list-style: none;
    
    span {
      font-size: 24px;
      margin-right: 5px;
      font-weight: 500;
      display: inline-block;
    }

    li {
      height: 52px;
      display: flex;
      a {
        text-decoration: none;
        color: #111;
        height: 52px;
        display: flex;
        align-items: center;
        padding: 0 40px;

        &.router-link-active {
          // background-color: var(--color-main);
          color: var(--color-main);
        }
      }
    }
  }
}
</style>
