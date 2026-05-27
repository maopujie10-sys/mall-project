<template>
  <div class="navbar pl-11 pr-24 flex justify-between items-center font-14">
    <div class="flex items-center ">
      <hamburger id="hamburger-container" :is-active="sidebar.opened" class="hamburger-container"
                 @toggleClick="toggleSideBar"/>
      <breadcrumb id="breadcrumb-container" class="breadcrumb-container"/>
    </div>
    <div class="flex items-center h-full">
      <!--              <el-badge :value="1" class="relative top-2">-->
      <div class="vector" v-if="vectorContent.content">
        <el-image :src="vector" style="height: 22px;margin-right: 6px;"/>
        <div style="max-width: 300px;overflow: hidden;display: flex;align-items: center;">
          <span class="scrolling-text" ref="scrollingText">
            {{ vectorContent.content }}
          </span>
        </div>
      </div>
      <SoMessage/>
      <Globalization/>
      <img :src="avatar||require('@/assets/images/avatar.png')" alt="" class="w-30 h-30 ml-10 mr-6"
           style="border-radius: 50%;"/>
      <span class="mr-12 font-14 font-400">
        {{ showUserName }}</span>
      <img :src="require('@/assets/images/nav/Union.png')" alt="" class="w-16 cursor-pointer" @click="logout"/>
    </div>
    <div class="announcement" v-if="showAnnouncement">
      <div class="announcement-content">
        <el-image :src="announcementContentBg" class="announcement-content-bg"/>
        <el-image :src="closeIcon" class="announcement-close" @click="closeAnnouncement"/>
        <div class="announcement-title">
          {{ $t('系统公告') }}
        </div>
        <div class="announcement-text">
          {{ vectorContent.content }}
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import date from "date-php";
import {mapActions, mapGetters, mapMutations} from "vuex";
import Breadcrumb from "@/components/Breadcrumb";
import Hamburger from "@/components/Hamburger";
import ErrorLog from "@/components/ErrorLog";
import SizeSelect from "@/components/SizeSelect";
import Search from "@/components/HeaderSearch";
import {getToken, removeToken} from "@/utils/auth";
import {getOrigin, setStorage} from "@/utils/utis";
import Globalization from "@/components/Globalization";
import SoMessage from "@/components/Message";
import {projectTitle} from "@/settings";
import {getVector, logout} from "@/api/user";
import Vector from "@/assets/vector.png";
import announcementContentBg from "@/assets/images/announcement-content-bg.png";
import closeIcon from "@/assets/images/close.png";

export default {
  data() {
    return {
      chatInter: null,
      dateTime: {
        date: "",
        hours: "",
        week: "",
      },
      test: '',
      Token: '',
      languageName: 'English',
      languages: [],
      vector: Vector,
      vectorContent: {},
      announcementContentBg,
      closeIcon,
      showAnnouncement: false,
    };
  },
  components: {
    Breadcrumb,
    Hamburger,
    ErrorLog,
    // Screenfull,
    SoMessage,
    Globalization,
    SizeSelect,
    Search,
  },
  created() {
    this.Token = getToken()
  },
  mounted() {
    this.languages = this.$store.getters.languages
    this.formatTime();
    this.getInfo()
    this.startChatInterval()
    this.getVector()

    // MessageBox.confirm(this.$t("你的账号在其他地方登录,你被迫退出"), this.$t("确认登出"), {
    //   confirmButtonText: this.$t('重新登录'),
    //   showCancelButton: false,
    //   type: 'warning'
    // })
  },
  computed: {
    ...mapGetters(["sidebar", "avatar", "device", "currentLanguage", 'userInfo']),
    showUserName() {
      let username = this.userInfo.username || this.userInfo.phone || this.userInfo.email
      if (username.indexOf('@') === -1) {
        username = '+' + username
      }
      return username
    }
  },
  methods: {
    ...mapActions('chat', ['startChatInterval']),
    ...mapMutations('language', ['setCurrentLanguage']),
    ...mapActions("user", ["getInfo"]),
    closeAnnouncement() {
      this.showAnnouncement = false
      localStorage.setItem('announcement', this.vectorContent.content)
    },
    openBell() {
      //打开新窗口，不显示地址栏
      const url = getOrigin() + '/chat/#/pc/blue?token=' + this.Token + '&lang=' + this.$store.getters.lang
      window.open(url, projectTitle, "scrollbars=no,resizable=no,status=no,location=no,toolbar=no,menubar=no,innerHeight=646,innerWidth=790")
    },
    getVector() {
      getVector().then(res => {
        this.vectorContent = res.data || {}
        this.$nextTick(() => {
          if (this.$refs.scrollingText) {
            let start = (this.$refs.scrollingText.clientWidth / 500).toFloor(0) * 1 + 1
            if (['ar'].includes(this.$store.getters.lang)) {
              this.$refs.scrollingText.className = `animation-right-${start} scrolling-text`
            } else {
              this.$refs.scrollingText.className = `animation-${start} scrolling-text`
            }
            //用localStorage标记，只展示一次
            if (this.vectorContent.content !== localStorage.getItem('announcement')) {
              this.showAnnouncement = true
            }
          }
        })


      })
    },
    toggleSideBar() {
      this.$store.dispatch("app/toggleSideBar");
    },
    // 退出登录
    async logout() {
      logout().then(res => {
        this.$store.commit('chat/DELETE_CHAT_INTERVAL')
        this.$store.commit('chat/DELETE_MASSAGE_INTERVAL')
        removeToken()
        this.$router.push(`/login?redirect=${this.$route.fullPath}`);
      })
    },
    formatTime() {
      const time = new Date();
      this.dateTime.date = date("Y-m-d", time);
      this.dateTime.hours = date("H:i:s", time);
      this.dateTime.week = date("周K", time);
      setInterval(() => {
        const time = new Date();
        this.dateTime.date = date("Y-m-d", time);
        this.dateTime.hours = date("H:i:s", time);
        this.dateTime.week = date("周K", time);
      }, 1000);
    },
    handleClick(item) {
      setStorage('merchant_pc_lang', item)
      //刷新页面
      this.$router.go(0)
    }
  },
};
</script>

<style lang="scss" scoped>

.navbar {
  height: 60px;
  overflow: hidden;
  position: relative;
  background: #fff;
  box-shadow: 0 1px 4px rgba(0, 21, 41, 0.08);

  .lang-icon {
    border: solid 1px #e6e6e6;
    border-radius: 50%;
  }

  .hamburger-container {
    line-height: 46px;
    height: 100%;
    float: left;
    cursor: pointer;
    transition: background 0.3s;
    -webkit-tap-highlight-color: transparent;

    &:hover {
      background: rgba(0, 0, 0, 0.025);
    }
  }

  .breadcrumb-container {
    float: left;
  }

  .errLog-container {
    display: inline-block;
    vertical-align: top;
  }

  .right-menu {
    float: right;
    height: 100%;
    line-height: 50px;

    &:focus {
      outline: none;
    }

    .right-menu-item {
      display: inline-block;
      padding: 0 8px;
      height: 100%;
      font-size: 18px;
      color: #5a5e66;
      vertical-align: text-bottom;

      &.hover-effect {
        cursor: pointer;
        transition: background 0.3s;

        &:hover {
          background: rgba(0, 0, 0, 0.025);
        }
      }
    }

    .avatar-container {
      margin-right: 30px;

      .avatar-wrapper {
        margin-top: 5px;
        position: relative;

        .user-avatar {
          cursor: pointer;
          width: 40px;
          height: 40px;
          border-radius: 10px;
        }

        .el-icon-caret-bottom {
          cursor: pointer;
          position: absolute;
          right: -20px;
          top: 25px;
          font-size: 12px;
        }
      }
    }
  }

  .vector {
    font-family: 'Roboto';
    font-style: normal;
    font-weight: 400;
    font-size: 12px;
    line-height: 14px;
    /* identical to box height */
    padding-left: 24px;
    line-height: 22px;
    display: flex;
    justify-content: flex-start;
    align-items: center;
    margin-right: 24px;
    color: #333333;
  }
}

.scrolling-text {
  display: inline-block;
  white-space: nowrap;
  //overflow: hidden;
  width: auto;

  &.animation-1 {
    animation: scroll-left 20s linear infinite;
  }

  &.animation-2 {
    animation: scroll-left 40s linear infinite;
  }

  &.animation-3 {
    animation: scroll-left 60s linear infinite;
  }

  &.animation-4 {
    animation: scroll-left 80s linear infinite;
  }

  &.animation-5 {
    animation: scroll-left 100s linear infinite;
  }

  &.animation-6 {
    animation: scroll-left 120s linear infinite;
  }

  &.animation-7 {
    animation: scroll-left 140s linear infinite;
  }

  &.animation-8 {
    animation: scroll-left 160s linear infinite;
  }

  &.animation-9 {
    animation: scroll-left 180s linear infinite;
  }

  &.animation-10 {
    animation: scroll-left 200s linear infinite;
  }

  &.animation-right-1 {
    animation: scroll-right 20s linear infinite;
  }

  &.animation-right-2 {
    animation: scroll-right 40s linear infinite;
  }

  &.animation-right-3 {
    animation: scroll-right 60s linear infinite;
  }

  &.animation-right-4 {
    animation: scroll-right 80s linear infinite;
  }

  &.animation-right-5 {
    animation: scroll-right 100s linear infinite;
  }

  &.animation-right-6 {
    animation: scroll-right 120s linear infinite;
  }

  &.animation-right-7 {
    animation: scroll-right 140s linear infinite;
  }

  &.animation-right-8 {
    animation: scroll-right 160s linear infinite;
  }

  &.animation-right-9 {
    animation: scroll-right 180s linear infinite;
  }

  &.animation-right-10 {
    animation: scroll-right 200s linear infinite;
  }
}

@keyframes scroll-left {
  0% {
    transform: translateX(300px);
  }
  100% {
    transform: translateX(-100%);
  }
}

@keyframes scroll-right {
  0% {
    transform: translateX(-300px);
  }
  100% {
    transform: translateX(100%);
  }
}

.announcement {
  background-color: rgb(0, 0, 0, 0.5);
  position: fixed;
  left: 0;
  top: 0;
  z-index: 99999;
  width: 100%;
  height: 100%;
  display: flex;
  justify-content: center;
  align-items: center;

  .announcement-content {
    width: 500px;
    background-color: #ffffff;
    position: relative;
    border-radius: 12px;

    .announcement-close {
      display: flex;
      justify-content: center;
      align-items: center;
      position: absolute;
      bottom: -80px;
      width: 50px;
      height: 50px;
      padding: 1px;
      left: 50%;
      transform: translateX(-50%);
      cursor: pointer;
    }

    .announcement-content-bg {
      position: absolute;
      left: 0;
      top: 0;
    }

    .announcement-title {
      position: relative;
      width: 100%;
      height: 160px;
      color: #FFF;
      font-family: Roboto;
      font-size: 26px;
      font-style: normal;
      font-weight: 900;
      text-transform: uppercase;
      display: flex;
      align-items: center;
      padding: 0 120px 0 32px;
    }

    .announcement-text {
      width: 100%;
      min-height: 300px;
      text-align: left;
      padding: 0px 32px 0px 32px;
      color: #333;
      font-family: Roboto;
      font-size: 15px;
      font-style: normal;
      font-weight: 400;
      line-height: 120.187%; /* 18.028px */
      letter-spacing: 0.7px;
      display: flex;
      justify-content: center;
      align-items: center;
    }
  }
}
</style>
