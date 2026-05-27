<template>
  <div :class="classObj" class="app-wrapper">
    <div v-if="device==='mobile'&&sidebar.opened" class="drawer-bg" @click="handleClickOutside"/>
    <sidebar class="sidebar-container"/>
    <div :class="{hasTagsView:needTagsView}" class="main-container">
      <div :class="{'fixed-header':fixedHeader}">
        <navbar/>
        <tags-view v-if="needTagsView"/>
      </div>
      <app-main/>
      <right-panel v-if="showSettings">
        <settings/>
      </right-panel>
    </div>
    <Chat/>
    <Customer ref="customer"/>
    <CreatePdf ref="createPdf" @closePdf="closePdf" v-if="sellerSign&&showCreatePdf"/>
  </div>
</template>

<script>
import RightPanel from '@/components/RightPanel'
import {AppMain, Navbar, Settings, Sidebar, TagsView} from './components'
import ResizeMixin from './mixin/ResizeHandler'
import {mapActions, mapGetters, mapState} from 'vuex'
import {projectTitle} from "@/settings";
import Customer from '@/components/Customer'
import {getSysParaContract} from "@/api/user";
import CreatePdf from "@/components/Pact/createPdf.vue";
import Chat from "@/views/chat/index.vue"

export default {
  name: 'Layout',
  components: {
    CreatePdf,
    AppMain,
    Navbar,
    RightPanel,
    Settings,
    Sidebar,
    TagsView,
    Customer,
    Chat
  },
  data() {
    return {
      unRead: 0,
      userClick: false,
      timer: '',
      projectTitle,
      sellerSign: false,
      showCreatePdf: false,
    }
  },
  mixins: [ResizeMixin],
  computed: {
    ...mapGetters(['userInfo']),
    ...mapActions('user', ['getInfo']),
    ...mapState({
      showCustomer: state => state.app.showCustomer,
      sidebar: state => state.app.sidebar,
      device: state => state.app.device,
      showSettings: state => state.settings.showSettings,
      needTagsView: state => state.settings.tagsView,
      fixedHeader: state => state.settings.fixedHeader
    }),
    classObj() {
      return {
        hideSidebar: !this.sidebar.opened,
        openSidebar: this.sidebar.opened,
        withoutAnimation: this.sidebar.withoutAnimation,
        mobile: this.device === 'mobile',
        rtl: ['ar'].includes(this.$store.getters.currentLanguage)
      }
    }
  },
  watch: {
    showCustomer(to) {
      console.log('showCustomer', this.showCustomer)
      if (this.showCustomer === true) {
        this.$refs.customer.openCustomerService();
      }
      this.$store.commit('app/SET_SHOW_CUSTOMER', false)
    },
    userInfo(val) {
      if (!val.signPdfUrl) {
        this.getSysParaContract()
      }
    }
  },
  mounted() {

  },
  methods: {
    getSysParaContract() {
      getSysParaContract().then(res => {
        this.sellerSign = res.data.sellerSign === 'true'
        if (this.sellerSign) this.createPdf()
      })
    },
    createPdf() {
      this.showCreatePdf = true
      document.body.style.overflow = 'hidden'; // 禁止滚动条
    },
    closePdf() {
      this.showCreatePdf = false
      document.body.style.overflow = 'auto'; // 出现滚动条
      this.getInfo()
    },
    handleClickOutside() {
      this.$store.dispatch('app/closeSideBar', {withoutAnimation: false})
    },
  }
}
</script>

<style lang="scss" scoped>
@import "~@/styles/mixin.scss";
@import "~@/styles/variables.scss";
@import "~@/styles/rtl.scss";

::v-deep {
  .ax_default_shadow {
    box-shadow: 0 0 8px 0 rgba(0, 0, 0, 0.1);
  }
}

.tip {
  display: block;
  width: 16px;
  height: 16px;
  content: ' ';
  background-color: #F56C6C;
  border-radius: 100%;
  line-height: 16px;
  font-size: 12px;
  color: #FFFFFF;
  position: absolute;
  text-align: center;
  top: 0;
  right: 0;
  // 缩小字体
  transform: scale(0.9);
}

.app-wrapper {
  @include clearfix;
  position: relative;
  height: 100%;
  width: 100%;

  &.mobile.openSidebar {
    position: fixed;
    top: 0;
  }
}

.drawer-bg {
  background: #000;
  opacity: 0.3;
  width: 100%;
  top: 0;
  height: 100%;
  position: absolute;
  z-index: 999;
}

.fixed-header {
  position: fixed;
  top: 0;
  right: 0;
  z-index: 9;
  width: calc(100% - #{$sideBarWidth});
  transition: width 0.28s;
}

.hideSidebar .fixed-header {
  width: calc(100% - 54px)
}

.mobile .fixed-header {
  width: 100%;
}


/*! CSS Used from: http://18.138.254.116:9002/pm1/sc2.0/resources/css/axure_rp_page.css */
p {
  margin: 0px;
  text-rendering: optimizeLegibility;
  font-feature-settings: "kern" 1;
  -webkit-font-feature-settings: "kern";
  -moz-font-feature-settings: "kern";
  -moz-font-feature-settings: "kern=1";
  font-kerning: normal;
}

/*! CSS Used from: http://18.138.254.116:9002/pm1/sc2.0/data/styles.css */
.ax_default {
  font-family: 'Arial Normal', 'Arial', sans-serif;
  font-weight: 400;
  font-style: normal;
  font-size: 14px;
  letter-spacing: normal;
  color: #666666;
  vertical-align: none;
  text-align: center;
  line-height: normal;
  text-transform: none;
}

/*! CSS Used from: http://18.138.254.116:9002/pm1/sc2.0/files/%E4%BB%AA%E8%A1%A8%E7%9B%98/styles.css */
#u8199 {
  position: fixed;
  right: 12px;
  bottom: 12px;
}

#u8199_state0 {
  position: relative;
  left: 0px;
  top: 0px;
  width: 57px;
  height: 57px;
  background-image: none;
  border: none;
  border-radius: 0px;
  -moz-box-shadow: none;
  -webkit-box-shadow: none;
  box-shadow: none;
}

#u8199_state0_content {
  border-width: 0px;
  position: absolute;
  left: 0px;
  top: 0px;
  width: 1px;
  height: 1px;
}

#u8200_img {
  border-width: 0px;
  position: absolute;
  left: -10px;
  top: -10px;
  width: 77px;
  height: 77px;
}

#u8200 {
  border-width: 0px;
  position: absolute;
  left: 0px;
  top: 0px;
  width: 57px;
  height: 57px;
  display: flex;
}

#u8200 .text {
  position: absolute;
  align-self: center;
  padding: 2px 2px 2px 2px;
  box-sizing: border-box;
  width: 100%;
}

#u8200_text {
  border-width: 0px;
  word-wrap: break-word;
  text-transform: none;
  visibility: hidden;
}

#u8201_img {
  border-width: 0px;
  position: absolute;
  left: 0px;
  top: 0px;
  width: 31px;
  height: 31px;
}

#u8201 {
  border-width: 0px;
  position: absolute;
  left: 13px;
  top: 13px;
  width: 31px;
  height: 31px;
  display: flex;
}

#u8201 .text {
  position: absolute;
  align-self: center;
  padding: 2px 2px 2px 2px;
  box-sizing: border-box;
  width: 100%;
}

#u8201_text {
  border-width: 0px;
  word-wrap: break-word;
  text-transform: none;
  visibility: hidden;
}

/*! CSS Used from: http://18.138.254.116:9002/pm1/sc2.0/resources/css/axure_rp_page.css */
p {
  margin: 0px;
  text-rendering: optimizeLegibility;
  font-feature-settings: "kern" 1;
  -webkit-font-feature-settings: "kern";
  -moz-font-feature-settings: "kern";
  -moz-font-feature-settings: "kern=1";
  font-kerning: normal;
}

input {
  padding: 1px 0px 1px 0px;
  box-sizing: border-box;
  -moz-box-sizing: border-box;
}

div.annnotelabel {
  font-family: Helvetica, Arial;
  white-space: nowrap;
  padding-top: 1px;
  background-color: #fff849;
  font-size: 10px;
  font-weight: bold;
  line-height: 14px;
  margin-right: 3px;
  padding: 0px 4px;
  color: #000;
  -moz-box-shadow: 1px 1px 3px #aaa;
  -webkit-box-shadow: 1px 1px 3px #aaa;
  box-shadow: 1px 1px 3px #aaa;
}

div.annnote {
  display: flex;
  position: absolute;
  cursor: help;
  line-height: 14px;
}

/*! CSS Used from: http://18.138.254.116:9002/pm1/sc2.0/data/styles.css */
.ax_default {
  font-family: 'Arial Normal', 'Arial', sans-serif;
  font-weight: 400;
  font-style: normal;
  font-size: 14px;
  letter-spacing: normal;
  color: #666666;
  vertical-align: none;
  text-align: center;
  line-height: normal;
  text-transform: none;
}

.primary_button {
  color: #FFFFFF;
}

._二级标题 {
  font-family: 'Arial Normal', 'Arial', sans-serif;
  font-weight: bold;
  font-style: normal;
  font-size: 24px;
  color: #333333;
  text-align: left;
}

.label {
  font-size: 14px;
  text-align: left;
}

.text_field {
  color: #000000;
  text-align: left;
}

input {
  outline: none;
}

/*! CSS Used from: http://18.138.254.116:9002/pm1/sc2.0/files/%E4%BB%AA%E8%A1%A8%E7%9B%98/styles.css */
#u8177 {
  position: fixed;
  right: 30px;
  bottom: 30px;
  visibility: hidden;
}

#u8177_state0 {
  position: relative;
  left: 0px;
  top: 0px;
  width: 412px;
  height: 534px;
  background-image: none;
  border: none;
  border-radius: 0px;
  -moz-box-shadow: none;
  -webkit-box-shadow: none;
  box-shadow: none;
}

#u8177_state0_content {
  border-width: 0px;
  position: absolute;
  left: 0px;
  top: 0px;
  width: 1px;
  height: 1px;
}

#u8178_div {
  border-width: 0px;
  position: absolute;
  left: 0px;
  top: 0px;
  width: 412px;
  height: 534px;
  background: inherit;
  background-color: rgba(255, 255, 255, 1);
  border: none;
  border-radius: 6px;
  -moz-box-shadow: 0px 0px 10px rgba(127, 127, 127, 0.349019607843137);
  -webkit-box-shadow: 0px 0px 10px rgba(127, 127, 127, 0.349019607843137);
  box-shadow: 0px 0px 10px rgba(127, 127, 127, 0.349019607843137);
}

#u8178 {
  border-width: 0px;
  position: absolute;
  left: 0px;
  top: 0px;
  width: 412px;
  height: 534px;
  display: flex;
}

#u8178 .text {
  position: absolute;
  align-self: center;
  padding: 2px 2px 2px 2px;
  box-sizing: border-box;
  width: 100%;
}

#u8178_text {
  border-width: 0px;
  word-wrap: break-word;
  text-transform: none;
  visibility: hidden;
}

#u8179_div {
  border-width: 0px;
  position: absolute;
  left: 0px;
  top: 0px;
  width: 412px;
  height: 52px;
  background: inherit;
  background-color: rgba(4, 104, 254, 1);
  border: none;
  border-radius: 6px;
  border-bottom-right-radius: 0px;
  border-bottom-left-radius: 0px;
  -moz-box-shadow: none;
  -webkit-box-shadow: none;
  box-shadow: none;
}

#u8179 {
  border-width: 0px;
  position: absolute;
  left: 0px;
  top: 0px;
  width: 412px;
  height: 52px;
  display: flex;
}

#u8179 .text {
  position: absolute;
  align-self: center;
  padding: 2px 2px 2px 2px;
  box-sizing: border-box;
  width: 100%;
}

#u8179_text {
  border-width: 0px;
  word-wrap: break-word;
  text-transform: none;
  visibility: hidden;
}

#u8180_img {
  border-width: 0px;
  position: absolute;
  left: 0px;
  top: 0px;
  width: 30px;
  height: 30px;
}

#u8180 {
  border-width: 0px;
  position: absolute;
  left: 12px;
  top: 9px;
  width: 30px;
  height: 30px;
  display: flex;
}

#u8180 .text {
  position: absolute;
  align-self: center;
  padding: 2px 2px 2px 2px;
  box-sizing: border-box;
  width: 100%;
}

#u8180_text {
  border-width: 0px;
  word-wrap: break-word;
  text-transform: none;
  visibility: hidden;
}

#u8181_div {
  border-width: 0px;
  position: absolute;
  left: 0px;
  top: 0px;
  width: 56px;
  height: 16px;
  background: inherit;
  background-color: rgba(255, 255, 255, 0);
  border: none;
  border-radius: 0px;
  -moz-box-shadow: none;
  -webkit-box-shadow: none;
  box-shadow: none;
  color: #FFFFFF;
}

#u8181 {
  border-width: 0px;
  position: absolute;
  left: 49px;
  top: 16px;
  width: 56px;
  height: 16px;
  display: flex;
  color: #FFFFFF;
}

#u8181 .text {
  position: absolute;
  align-self: flex-start;
  padding: 0px 0px 0px 0px;
  box-sizing: border-box;
  width: 100%;
}

#u8181_text {
  border-width: 0px;
  white-space: nowrap;
  text-transform: none;
}

#u8182_img {
  border-width: 0px;
  position: absolute;
  left: 0px;
  top: 0px;
  width: 12px;
  height: 8px;
}

#u8182 {
  border-width: 0px;
  position: absolute;
  left: 381px;
  top: 22px;
  width: 12px;
  height: 8px;
  display: flex;
  -webkit-transform: rotate(180deg);
  -moz-transform: rotate(180deg);
  -ms-transform: rotate(180deg);
  transform: rotate(180deg);
}

#u8182 .text {
  position: absolute;
  align-self: center;
  padding: 2px 2px 2px 2px;
  box-sizing: border-box;
  width: 100%;
}

#u8182_text {
  border-width: 0px;
  word-wrap: break-word;
  text-transform: none;
  visibility: hidden;
}

#u8183_img {
  border-width: 0px;
  position: absolute;
  left: 0px;
  top: 0px;
  width: 44px;
  height: 44px;
}

#u8183 {
  border-width: 0px;
  position: absolute;
  left: 358px;
  top: 204px;
  width: 44px;
  height: 44px;
  display: flex;
}

#u8183 .text {
  position: absolute;
  align-self: center;
  padding: 2px 2px 2px 2px;
  box-sizing: border-box;
  width: 100%;
}

#u8183_text {
  border-width: 0px;
  word-wrap: break-word;
  text-transform: none;
  visibility: hidden;
}

#u8184_img {
  border-width: 0px;
  position: absolute;
  left: 0px;
  top: 0px;
  width: 300px;
  height: 47px;
}

#u8184 {
  border-width: 0px;
  position: absolute;
  left: 49px;
  top: 204px;
  width: 300px;
  height: 47px;
  display: flex;
}

#u8184 .text {
  position: absolute;
  align-self: center;
  padding: 2px 2px 2px 2px;
  box-sizing: border-box;
  width: 100%;
}

#u8184_text {
  border-width: 0px;
  word-wrap: break-word;
  text-transform: none;
  visibility: hidden;
}

#u8185_div {
  border-width: 0px;
  position: absolute;
  left: 0px;
  top: 0px;
  width: 248px;
  height: 19px;
  background: inherit;
  background-color: rgba(255, 255, 255, 0);
  border: none;
  border-radius: 0px;
  -moz-box-shadow: none;
  -webkit-box-shadow: none;
  box-shadow: none;
  font-family: 'PingFang SC ', 'PingFang SC', sans-serif;
  font-weight: 400;
  font-style: normal;
}

#u8185 {
  border-width: 0px;
  position: absolute;
  left: 72px;
  top: 218px;
  width: 248px;
  height: 19px;
  display: flex;
  font-family: 'PingFang SC ', 'PingFang SC', sans-serif;
  font-weight: 400;
  font-style: normal;
}

#u8185 .text {
  position: absolute;
  align-self: flex-start;
  padding: 0px 0px 0px 0px;
  box-sizing: border-box;
  width: 100%;
}

#u8185_text {
  border-width: 0px;
  white-space: nowrap;
  text-transform: none;
}

#u8186_img {
  border-width: 0px;
  position: absolute;
  left: 0px;
  top: 0px;
  width: 44px;
  height: 44px;
}

#u8186 {
  border-width: 0px;
  position: absolute;
  left: 12px;
  top: 98px;
  width: 44px;
  height: 44px;
  display: flex;
}

#u8186 .text {
  position: absolute;
  align-self: center;
  padding: 2px 2px 2px 2px;
  box-sizing: border-box;
  width: 100%;
}

#u8186_text {
  border-width: 0px;
  word-wrap: break-word;
  text-transform: none;
  visibility: hidden;
}

#u8187_img {
  border-width: 0px;
  position: absolute;
  left: 0px;
  top: 0px;
  width: 300px;
  height: 47px;
}

#u8187 {
  border-width: 0px;
  position: absolute;
  left: 66px;
  top: 98px;
  width: 300px;
  height: 47px;
  display: flex;
  -webkit-transform: rotate(180deg);
  -moz-transform: rotate(180deg);
  -ms-transform: rotate(180deg);
  transform: rotate(180deg);
}

#u8187 .text {
  position: absolute;
  align-self: center;
  padding: 2px 2px 2px 2px;
  box-sizing: border-box;
  width: 100%;
}

#u8187_text {
  border-width: 0px;
  word-wrap: break-word;
  text-transform: none;
  visibility: hidden;
}

#u8188_div {
  border-width: 0px;
  position: absolute;
  left: 0px;
  top: 0px;
  width: 140px;
  height: 19px;
  background: inherit;
  background-color: rgba(255, 255, 255, 0);
  border: none;
  border-radius: 0px;
  -moz-box-shadow: none;
  -webkit-box-shadow: none;
  box-shadow: none;
  font-family: 'PingFang SC ', 'PingFang SC', sans-serif;
  font-weight: 400;
  font-style: normal;
}

#u8188 {
  border-width: 0px;
  position: absolute;
  left: 85px;
  top: 113px;
  width: 140px;
  height: 19px;
  display: flex;
  font-family: 'PingFang SC ', 'PingFang SC', sans-serif;
  font-weight: 400;
  font-style: normal;
}

#u8188 .text {
  position: absolute;
  align-self: flex-start;
  padding: 0px 0px 0px 0px;
  box-sizing: border-box;
  width: 100%;
}

#u8188_text {
  border-width: 0px;
  white-space: nowrap;
  text-transform: none;
}

#u8189_div {
  border-width: 0px;
  position: absolute;
  left: 0px;
  top: 0px;
  width: 117px;
  height: 16px;
  background: inherit;
  background-color: rgba(255, 255, 255, 0);
  border: none;
  border-radius: 0px;
  -moz-box-shadow: none;
  -webkit-box-shadow: none;
  box-shadow: none;
  font-family: 'PingFang SC ', 'PingFang SC', sans-serif;
  font-weight: 650;
  font-style: normal;
  font-size: 12px;
  color: #7F7F7F;
}

#u8189 {
  border-width: 0px;
  position: absolute;
  left: 66px;
  top: 74px;
  width: 117px;
  height: 16px;
  display: flex;
  font-family: 'PingFang SC ', 'PingFang SC', sans-serif;
  font-weight: 650;
  font-style: normal;
  font-size: 12px;
  color: #7F7F7F;
}

#u8189 .text {
  position: absolute;
  align-self: flex-start;
  padding: 0px 0px 0px 0px;
  box-sizing: border-box;
  width: 100%;
}

#u8189_text {
  border-width: 0px;
  white-space: nowrap;
  text-transform: none;
}

#u8190_div {
  border-width: 0px;
  position: absolute;
  left: 0px;
  top: 0px;
  width: 117px;
  height: 13px;
  background: inherit;
  background-color: rgba(255, 255, 255, 0);
  border: none;
  border-radius: 0px;
  -moz-box-shadow: none;
  -webkit-box-shadow: none;
  box-shadow: none;
  font-family: 'PingFang SC ', 'PingFang SC', sans-serif;
  font-weight: 650;
  font-style: normal;
  font-size: 12px;
  color: #7F7F7F;
}

#u8190 {
  border-width: 0px;
  position: absolute;
  left: 229px;
  top: 177px;
  width: 117px;
  height: 13px;
  display: flex;
  font-family: 'PingFang SC ', 'PingFang SC', sans-serif;
  font-weight: 650;
  font-style: normal;
  font-size: 12px;
  color: #7F7F7F;
}

#u8190 .text {
  position: absolute;
  align-self: flex-start;
  padding: 0px 0px 0px 0px;
  box-sizing: border-box;
  width: 100%;
}

#u8190_text {
  border-width: 0px;
  white-space: nowrap;
  text-transform: none;
}

#u8191_img {
  border-width: 0px;
  position: absolute;
  left: 0px;
  top: 0px;
  width: 24px;
  height: 20px;
}

#u8191 {
  border-width: 0px;
  position: absolute;
  left: 22px;
  top: 109px;
  width: 24px;
  height: 20px;
  display: flex;
}

#u8191 .text {
  position: absolute;
  align-self: center;
  padding: 2px 2px 2px 2px;
  box-sizing: border-box;
  width: 100%;
}

#u8191_text {
  border-width: 0px;
  word-wrap: break-word;
  text-transform: none;
  visibility: hidden;
}

#u8192_div {
  border-width: 0px;
  position: absolute;
  left: 0px;
  top: 0px;
  width: 412px;
  height: 50px;
  background: inherit;
  background-color: rgba(255, 255, 255, 0);
  box-sizing: border-box;
  border-width: 1px;
  border-style: solid;
  border-color: rgba(215, 215, 215, 1);
  border-left: 0px;
  border-right: 0px;
  border-bottom: 0px;
  border-radius: 0px;
  border-top-left-radius: 0px;
  border-top-right-radius: 0px;
  -moz-box-shadow: none;
  -webkit-box-shadow: none;
  box-shadow: none;
}

#u8192 {
  border-width: 0px;
  position: absolute;
  left: 0px;
  top: 484px;
  width: 412px;
  height: 50px;
  display: flex;
}

#u8192 .text {
  position: absolute;
  align-self: center;
  padding: 2px 2px 2px 2px;
  box-sizing: border-box;
  width: 100%;
}

#u8192_text {
  border-width: 0px;
  word-wrap: break-word;
  text-transform: none;
  visibility: hidden;
}

#u8193_div {
  border-width: 0px;
  position: absolute;
  left: 0px;
  top: 0px;
  width: 69px;
  height: 31px;
  background: inherit;
  background-color: rgba(127, 127, 127, 1);
  border: none;
  border-radius: 8px;
  -moz-box-shadow: none;
  -webkit-box-shadow: none;
  box-shadow: none;
  font-family: 'PingFang SC ', 'PingFang SC', sans-serif;
  font-weight: 400;
  font-style: normal;
}

#u8193 {
  border-width: 0px;
  position: absolute;
  left: 337px;
  top: 494px;
  width: 69px;
  height: 31px;
  display: flex;
  font-family: 'PingFang SC ', 'PingFang SC', sans-serif;
  font-weight: 400;
  font-style: normal;
}

#u8193 .text {
  position: absolute;
  align-self: center;
  padding: 2px 2px 2px 2px;
  box-sizing: border-box;
  width: 100%;
}

#u8193_text {
  border-width: 0px;
  word-wrap: break-word;
  text-transform: none;
}

#u8194_img {
  border-width: 0px;
  position: absolute;
  left: 0px;
  top: 0px;
  width: 26px;
  height: 26px;
}

#u8194 {
  border-width: 0px;
  position: absolute;
  left: 10px;
  top: 496px;
  width: 26px;
  height: 26px;
  display: flex;
}

#u8194 .text {
  position: absolute;
  align-self: center;
  padding: 2px 2px 2px 2px;
  box-sizing: border-box;
  width: 100%;
}

#u8194_text {
  border-width: 0px;
  word-wrap: break-word;
  text-transform: none;
  visibility: hidden;
}

#u8195_img {
  border-width: 0px;
  position: absolute;
  left: 0px;
  top: 0px;
  width: 26px;
  height: 26px;
}

#u8195 {
  border-width: 0px;
  position: absolute;
  left: 44px;
  top: 497px;
  width: 26px;
  height: 26px;
  display: flex;
}

#u8195 .text {
  position: absolute;
  align-self: center;
  padding: 2px 2px 2px 2px;
  box-sizing: border-box;
  width: 100%;
}

#u8195_text {
  border-width: 0px;
  word-wrap: break-word;
  text-transform: none;
  visibility: hidden;
}

#u8196_div {
  border-width: 0px;
  position: absolute;
  left: 0px;
  top: 0px;
  width: 246px;
  height: 34px;
  background: inherit;
  background-color: rgba(255, 255, 255, 1);
  box-sizing: border-box;
  border-width: 1px;
  border-style: solid;
  border-color: rgba(215, 215, 215, 1);
  border-radius: 0px;
  -moz-box-shadow: none;
  -webkit-box-shadow: none;
  box-shadow: none;
}

#u8196 {
  border-width: 0px;
  position: absolute;
  left: 82px;
  top: 492px;
  width: 246px;
  height: 34px;
  display: flex;
}

#u8196 .text {
  position: absolute;
  align-self: center;
  padding: 2px 2px 2px 2px;
  box-sizing: border-box;
  width: 100%;
}

#u8196_text {
  border-width: 0px;
  word-wrap: break-word;
  text-transform: none;
  visibility: hidden;
}

#u8197_input {
  position: absolute;
  left: 0px;
  top: 0px;
  width: 234px;
  height: 25px;
  padding: 2px 2px 2px 2px;
  font-family: 'PingFang SC ', 'PingFang SC', sans-serif;
  font-weight: 400;
  font-style: normal;
  font-size: 14px;
  letter-spacing: normal;
  color: #000000;
  vertical-align: none;
  text-align: left;
  text-transform: none;
  background-color: transparent;
  border-color: transparent;
}

#u8197_div {
  border-width: 0px;
  position: absolute;
  left: 0px;
  top: 0px;
  width: 234px;
  height: 25px;
  background: inherit;
  background-color: rgba(255, 255, 255, 1);
  border: none;
  border-radius: 0px;
  -moz-box-shadow: none;
  -webkit-box-shadow: none;
  box-shadow: none;
  font-family: 'PingFang SC ', 'PingFang SC', sans-serif;
  font-weight: 400;
  font-style: normal;
}

#u8197 {
  border-width: 0px;
  position: absolute;
  left: 88px;
  top: 497px;
  width: 234px;
  height: 25px;
  display: flex;
  font-family: 'PingFang SC ', 'PingFang SC', sans-serif;
  font-weight: 400;
  font-style: normal;
}

#u8198 {
  border-width: 0px;
  position: absolute;
  left: 362px;
  top: 0px;
  width: 50px;
  height: 52px;
  overflow: hidden;
  background-image: url('http://18.138.254.116:9002/pm1/sc2.0/resources/images/transparent.gif');
}
</style>
