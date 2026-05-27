<template>
  <div id="app" :class="['ar'].includes(currentLanguage)?'rtl':''">
    <router-view/>
  </div>
</template>

<script>

import {mapActions, mapMutations} from "vuex";
import {setToken} from "@/utils/auth";
import {heartBeat} from "@/api/user";

export default {
  name: 'App',
  data() {
    return {
      heartBeatInter: {
        a: null,
        b: null
      },
      heartBeatLock: 150
    }
  },
  computed: {
    currentLanguage() {
      return this.$store.getters.currentLanguage
    },
    userInfo() {
      return this.$store.getters.userInfo
    },
    userToken() {
      return this.$store.getters.token
    }
  },
  watch: {
    userToken(newVal, oldVal) {
      if (this.$route.path !== '/login' && newVal && oldVal && (typeof oldVal) === 'string' && newVal !== oldVal) {
        setToken(newVal)
        //刷新页面
        window.location.reload()
      }
    },
  },
  created() {
    if (['ar'].includes(this.currentLanguage)) {
      document.body.className = 'rtl'
    }
    setInterval(() => {
      this.$store.commit('user/SET_TOKEN', localStorage.getItem('token'))
    }, 2000)
    //判断当前浏览器环境是否是移动端
    const ua = navigator.userAgent.toLowerCase()
    const isMobile = ua.indexOf('mobile') > -1
    this.$store.commit('app/SET_IS_MOBILE', isMobile)
    console.log("isMobile", this.$store.getters.isMobile)
    //如果是移动端则跳转到移动端页面
    if (this.$store.getters.isMobile) {
      const BASE_URL = window.location.protocol + "//" + window.location.host + '/'
      window.location.href = BASE_URL + 'www'
    }
  },
  mounted() {
    const that = this
    this.$i18n.locale = this.$store.getters.currentLanguage
    that.$nextTick(() => {
      setTimeout(() => {
        that.handleSetLang()
      }, 300)
    })
    that.heartBeat()
  },
  methods: {
    ...mapActions('user', ['getInfo']),
    ...mapMutations('language', ['setCurrentLanguage']),
    //心跳
    heartBeat() {
      const that = this
      //5分钟调用一次心跳
      clearInterval(that.heartBeatInter.a)
      clearInterval(that.heartBeatInter.b)
      that.heartBeatInter.a = setInterval(() => {
        let status = "1"
        if (this.heartBeatLock <= 0) {
          status = "2"
        }
        heartBeat({status}).then((res) => {
          console.log('心跳', status)
        })
      }, 60000)
      let lock = 60
      //监听鼠标移动事件
      document.onmousemove = function () {
        that.heartBeatLock = lock
      }
      //监听键盘事件
      document.onkeydown = function () {
        that.heartBeatLock = lock
      }
      //监听鼠标点击事件
      document.onclick = function () {
        that.heartBeatLock = lock
      }
      //监听鼠标滚动事件
      document.onmousewheel = function () {
        that.heartBeatLock = lock
      }
      //监听触摸事件
      document.ontouchstart = function () {
        that.heartBeatLock = lock
      }
      //监听手指滑动事件
      document.ontouchmove = function () {
        that.heartBeatLock = lock
      }
      //监听手指离开事件
      document.ontouchend = function () {
        that.heartBeatLock = lock
      }
      //监听路由变化
      that.$router.afterEach((to, from) => {
        that.heartBeatLock = lock
      })
      that.heartBeatInter.b = setInterval(() => {
        that.heartBeatLock--
      }, 1000)
    },
    handleSetLang() {
      let lang = this.$route.query.lang
      if (!lang) {
        return
      }
      localStorage.setItem('lang', lang)
      // 设置i18n.locale 组件库会按照上面的配置使用对应的文案文件
      this.$i18n.locale = lang
      // 提交mutations
      this.setCurrentLanguage(lang)
    },
  }
}

</script>

<style lang="scss">
@import "~@/styles/rtl.scss";

#app {

  min-width: 1024px;

  .sidebar-container {
    background: #fff;
  }
}

p {
  margin: 0;
  padding: 0;
}

#app .sidebar-container .submenu-title-noDropdown:hover, #app .sidebar-container .el-submenu__title:hover, #app .sidebar-container .el-submenu .el-menu-item:hover {
  background: #EDF2FF !important;
  color: #1552F0 !important;
}

#app .sidebar-container .is-active > .el-submenu__title {
  color: #999 !important;
}

#app .sidebar-container .nest-menu .el-submenu > .el-submenu__title, #app .sidebar-container .el-submenu .el-menu-item {
  background: #fff !important;
}

#app .sidebar-container .el-submenu .el-menu-item.is-active {
  background: #EDF2FF !important;
}

.el-menu--vertical .el-menu-item {
  background: #fff !important;

  &:hover {
    background: #EDF2FF !important;
  }
}

.el-menu--vertical .el-menu.el-menu--popup {
  padding: 0;
  background: #fff !important;
}
</style>
