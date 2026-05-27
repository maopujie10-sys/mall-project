<template>
  <!-- <el-header height="165px"> -->
    <div  :class="['header',isStore&&'no-gap']">
    <div class="header-fiexd" :style="!headerFlag?'padding:0 !important; transition: padding .5s linear 0s; background: rgba(255, 255, 255, 0.95); box-shadow: 0 0 10px rgba(0, 0, 0, 0.1); height:auto !important;':''">
       <div class="header-top flex-between app-container">
      <div class="header-logo flex-start" @click="goto('/')" :style="itemname == 'TikTok' ? 'height:78px': itemname == 'SM-wholesale shop'? 'width:220px':'' ">
        <img :src="itemname =='TikTok'?  require(`@/assets/image/${itemname}/shoplogo.png`): itemname =='TikTok-Wholesale' ? require(`@/assets/image/${itemname}/${itemname}logo.svg`):require(`@/assets/image/${itemname}/shoplogo.svg`)" :style="itemname == 'SM-wholesale shop'? 'width:220px;margin-right:auto':itemname =='TikTok'?'height:38.2px ;width:160px ':itemname =='TikTok-Wholesale'?'width:200px': 'width:160px'"/>
      </div>
      <div class="header-search" slot="reference">
        <i class="el-icon-search"></i>
        <el-autocomplete
          ref="serachRef"
          v-model="searchValue"
          :fetch-suggestions="querySearchAsync"
          :placeholder="$t('message.home.searchTips' /**搜索商店或产品 */)"
          popper-class="search-popper"
        >
          <template slot-scope="{ item }">
            <div class="search-content">
              <!-- <div
                class="search-content-item"
                v-for="dataItem in item.data.sellerList"
                :key="dataItem.id"
                :title="dataItem.name"
                @click.stop="handleSelect(dataItem, 'seller')"
              >
                <i class="el-icon-s-shop" />
                {{ dataItem.name }}
              </div> -->
              <div
                v-if="searchValue"
                class="search-content-item"
                @click.stop="goToSearchRes(false)"
              >
                <i class="el-icon-s-shop" />
                "{{ searchValue }}" {{ $t("message.home.storeSeachTips2") }}
              </div>
              <div
                class="search-content-item"
                v-for="dataItem in item.data.goodsList"
                :key="dataItem.id"
                :title="dataItem.name"
                @click.stop="handleSelect(dataItem)"
              >
                {{ dataItem.name }}
              </div>
              <div class="search-content-history">
                <div class="search-content-history-header flex-between">
                  <h1>{{ $t("message.home.historySearch" /**历史搜索 */) }}</h1>
                  <div @click.stop="clearSearchHistory">
                    <i class="el-icon-delete"></i>
                    {{ $t("message.home.empty" /**清空 */) }}
                  </div>
                </div>
                <div class="search-content-history-list">
                  <div v-if="historyData.length > 0">
                    <el-tag
                      v-for="(historyItem, historyIndex) in historyData"
                      :key="historyIndex"
                      type="info"
                      effect="plain"
                      @click.stop="updateSerachValue(historyItem)"
                      :title="historyItem"
                    >
                      {{ historyItem }}
                    </el-tag>
                  </div>
                  <div v-else class="empty">
                    {{ $t("message.home.noData" /**暂无数据 */) }}
                  </div>
                </div>
              </div>
            </div>
          </template>
        </el-autocomplete>
        <el-button type="primary" @click="() => goToSearchPage()">
          {{ $t("message.home.search" /**搜索 */) }}
        </el-button>
      </div>
      <div class="header-user">
        <div class="flex-start">
          <i class="el-icon-user"></i>
          <div class="no-login" v-if="!userInfo.username">
            <span class="text" @click="goto('/login')">
              {{ $t("message.home.login" /*登录 */) }}
            </span>
            <span>{{ $t("message.home.or") }}</span>
            <span class="text" @click="goto('/register')">
              {{ $t("message.home.register" /**注册 */) }}
            </span>
          </div>
          <div class="no-login" v-else>
            <span
              class="text user-name"
              @click="goto('/userInfo/dashboard', 0)"
            >
              {{ userInfo.username }}
            </span>
            <span>{{ $t("message.home.or") }}</span>
            <span class="text" @click="handleLogout">
              {{ $t("message.home.logout" /**退出 */) }}
            </span>
          </div>
          <div style="margin-right: 20px">
            <el-badge
              v-if="!!unPtcount"
              :value="unPtcount"
              @click.native="openService"
            >
              <i class="el-icon-headset"></i>
            </el-badge>
            <i v-else class="el-icon-headset" @click="openService"></i>
          </div>
          <el-badge
            v-if="!!unreadMessage"
            :value="message ? unreadMessage : ''"
            @click.native="openOnlineService"
          >
            <i class="el-icon-chat-line-round" style="font-size: 22px"></i>
          </el-badge>
          <i
            class="el-icon-chat-line-round"
            v-else
            @click="openOnlineService"
            style="font-size: 22px"
          ></i>
          <!-- <el-popover placement="bottom" width="200" trigger="hover">
            <i class="el-icon-download" slot="reference"></i>
            <div>
              <div id="qrCode" class="app-qr-code-wrap flex-center">
                <VueQr :size="132" :text="downAppUrl" :margin="0" />
              </div>
            </div>
          </el-popover> -->

          <EsLang />
        </div>
      </div>
    </div>
    </div>
    <div class="header-nav" v-if="headerFlag">
      <ul style="display: flex">
        <li
          v-for="(item, index) in nav"
          :key="index"
          :class="{ active: $router.currentRoute.path === item.path }"
          @click="goto(item.path)"
        >
          {{ item.name }}
        </li>
      </ul>
    </div>
    <EsOnlineServiceView v-model="showOnlieService" ref="headerService"/>
  </div>
  <!-- </el-header> -->
</template>

<script>
import { mapGetters, mapActions, mapMutations } from "vuex";
import { SearchApi } from "@/api";
import {heartBeat,maxBuy} from "@/api/home"
// maxBuy
import { ES_SEARCH_RESULT, ES_MESSAGE_LAST_ID } from "@/common";
import { notLogin } from "@/common/pageHook";
import config from "@/config/index";
import EsLang from "./lang.vue";
import { openChatPage } from "@/util";
import { cloneDeep } from "lodash";
import { loginOutApi } from '@/api/login'
// import VueQr from "vue-qr";
import { ChatUnReadCountPt,apiGetCustomerService } from "@/api/common";
import {
  getSearchHistoryLocal,
  setSearchHistoryLocal,
  clearSearchHistoryLocal,
} from "@/util/shop";
export default {
  name: "EsHeader",
  props: {
    isStore: {
      type: Boolean,
      default: false,
    }
  },
  components: {
    EsLang,
    // VueQr,
  },
  data() {
    return {
      itemname: process.env.VUE_APP_ITEM_NAME,
      searchVisible: false,
      showOnlieService: false,
      onlinePath:'',
      searchValue: "",
      oldSearchValue: "",
      oldSearchResult: null,
      // appDownloadUrl: "https://421s2pj.com/OxME.app",
      timer: null,
      id: "",
      message: true,
      lang: "",
      headerFlag:true,
      unPtcount: 0,
    };
  },
  computed: {
    ...mapGetters({
      userInfo: "userInfo",
      unreadMessage: "user/unreadMessage",
      storeSearchValue: "home/storeSearchValue",
      downAppUrl: "home/downAppUrl",
    }),
    ...mapGetters(["existToken", "isLogin", "historyData"]),
    nav() {
      const arr = [
        {
          name: this.$t("message.home.home" /**首页 */),
          path: "/index",
        },
        {
          name: this.$t("message.home.classification" /**分类 */),
          path: "/classification",
        },
        {
          name: this.$t("message.home.commodity" /**商品 */),
          path: "/commodity",
        },
        {
          name: this.$t("message.home.discounted" /**商品 */),
          path: "/discounted",
        },
        {
          name: this.$t("message.home.merchantSettled"),
          path: "/merchantSettled",
        },
        {
           name: this.$t("message.home.creditTit"),
          path:  "/credit" 
        }
      ];
      // if (this.itemname !== "Mbuy") {
      //   arr.push({
      //     name: this.$t("message.home.creditTit"),
      //     path: this.isLogin ? "/credit" : "/login",
      //   });
      // }
      return arr;
    },
  },
  created(){
    this.lang = localStorage.getItem("ES_LANG") || "en";
    window.addEventListener("scroll",()=>{
        //获取页面滚动的高度
           let scrollTop = document.documentElement.scrollTop;
           if(scrollTop >= 78){
               this.headerFlag = false;
           }else {
               this.headerFlag = true;
           }
       }) 
  },
  async activated() {
    this.getOnlinePath()
    
    
    const keyW = this.$route?.query?.["k"] || this.storeSearchValue;
    
    if(keyW){
      this.$nextTick(() => {
      this.searchValue = JSON.parse(keyW);
    });
      this.updateSearchValue(String(keyW))
    }
    
    this.getHistoryCacheData();

    console.log('this.historyData ->', this.historyData);
    this.initDownAppUrl();
    this.getUnCount();
    this.timer && clearInterval(this.timer);
    this.timer = setInterval(() => {
      if (this.isLogin) {
        this.requestUnreadMessageList({ loginType: "user" });
      }
      this.getUnCount();
    }, 1000*30);
    let res = await maxBuy({code:'mall_max_goods_number_in_order'})
    if(res.code == 0){
      localStorage.setItem('maxBuy',res.data.mall_max_goods_number_in_order)
    }
    setInterval(() => {
       this.heart()
    }, 5*60*1000);
    if (
      this.$route.query?.["customerService"] ||
      this.$route.query?.["customer-service"]
    ) {
      this.showOnlieService = true;
    }
  },
  watch: {
    isLogin: {
      handler(val) {
        if (!val) {
          this.SET_HISTORYDATA([]);
          this.message = false;
        } else {
          this.getHistoryCacheData();
          this.message = true;
        }
      },
      deep: true,
      immediate: true,
    },
    $route: function (to, from) {
      // console.log('to ->', to.path);
      if(to.path !== '/searchGoods' && to.path !== '/seacthStore'){
        this.$nextTick(() => {
          this.searchValue = "";
        });
        this.updateSearchValue("")
      }
    },
  },
  beforeDestroy() {
    this.searchValue = "";
    this.timer && clearInterval(this.timer);
  },
  methods: {
   async heart(){
     await heartBeat()
    },
    openService() {
      // console.log('this.$refs ->', this.$refs);
      if (this.onlinePath) {
         window.open(
          this.onlinePath,
          "_blank"
        );
      } else {
       this.showOnlieService = true;
      }
    },
    async getOnlinePath() {
      let res = await apiGetCustomerService({code:'customer_service_url'});
      this.onlinePath = res.data.customer_service_url
    },
    async getUnCount() {
      let res = await ChatUnReadCountPt();
      this.unPtcount = res.data;
    },
    ...mapActions({
      logout: "logout",
      requestUnreadMessageList: "user/requestUnreadMessageList",
      initDownAppUrl: "home/initDownAppUrl",
    }),

    ...mapMutations({
      updateSearchValue: "home/updateSearchValue",
      SET_HISTORYDATA: "SET_HISTORYDATA",
    }),
    handleLogout() {
      this.searchValue = "";
      this.updateSearchValue("");
      localStorage.setItem(ES_MESSAGE_LAST_ID, "");
      this.logout();
      loginOutApi()
      this.message = false;
      /**
       * 退出登录，路由都定向到首页，防止在详情页面还能进行购物等操作
       */
      if (this.$router.currentRoute.path !== "/index") {
        this.$router.replace("/index");
      }
    },
    getHistoryCacheData() {
      const historyCacheData = getSearchHistoryLocal();
      // console.log('historyCacheData ->', historyCacheData);
      historyCacheData &&
        historyCacheData.length &&
        this.SET_HISTORYDATA(historyCacheData);
    },
    goto(path, index) {
      if (index == 0) {
        this.$store.state.user.currentIndex = index;
        localStorage.setItem("currentIndex", index);
      }
      if (path == '/register'){
        sessionStorage.setItem("path", "/register")
      }
      if (path === "/merchantSettled") {
        // console.log(" config.HOST_URL->", config.HOST_URL);
        window.open(
          config.HOST_URL +
            "/promote/#/" +
            "?lang=" +
            this.lang +
            "&avatar=" +
            this.userInfo.avatar
        );
      } else {
        localStorage.setItem("scroll", 0);
        this.$router.push(path);
      }
    },
    goToSearchPage() {
      if (this.searchValue) {
        let historyData = cloneDeep(this.historyData);
        historyData.unshift(this.searchValue);
        historyData = [...new Set(historyData)];
        historyData = historyData.slice(0, 10);
        setSearchHistoryLocal(historyData);
        // this.querySearchAsync(this.searchValue)
        // console.log('this.$refs.serachRef ->', this.$refs);
        this.$refs.serachRef.activated=true;
        this.$refs.serachRef.fetchSuggestions(this.searchValue,'',1);
        // this.serachEvent(this.searchValue)
      } else { 
        this.$message({
          type: "warning",
          message: this.$t("message.home.请输入关键字搜索"),
          offset: 65,
          duration: 1500,
        });
      }
    },
    async querySearchAsync(queryString, cb,o) {
      // const Str = queryString || this.$route.query?.["k"];
       
      const trimQueryString = String(queryString).trim();
      const trimQueryEncode = String(encodeURIComponent(queryString)).trim();
      // console.log('trimQueryString ->', trimQueryString);
      if (trimQueryString && this.oldSearchValue === trimQueryString && o !== 1) {
        return cb([{ data: this.oldSearchResult, b: 2 }]);
      }
      // console.log('queryString ->', queryString);
      if (trimQueryString) {
        const params = {
          keyword: trimQueryEncode,
          // isNew: 0,
          // isHot: 0,
          // isPrice: 0,
        };
        const result = await SearchApi(params);
        this.getHistoryCacheData();
        this.oldSearchValue = trimQueryString;
        this.oldSearchResult = result.data;
        this.updateSearchValue(trimQueryString);
       
       
        if(o !==1){
            return cb([{ data: result.data, b: 2 }]);
          }else{
            if (result.data && result.data.goodsList.length) {
            this.goToSearchRes(true);
              } else {
            this.goToSearchRes(false);
            }
          }
        
      } else {
        this.oldSearchResult = null;
      }

      this.oldSearchValue = trimQueryString;
      this.updateSearchValue(trimQueryString);
      if(o !==1){
        cb([{ data: { sellerList: [], goodsList: [] }, b: 2 }]);
      }
     
    },
    handleSelect(item, key = "goods") {
      this.id = item.id;
      if (item.name !== this.searchValue) {
        this.$nextTick(() => {
          this.searchValue = item.name;
          this.updateSearchValue(item.name);

          // 关闭弹窗
          if (this.$refs.serachRef && this.$refs.serachRef.suggestions) {
            this.$refs.serachRef.suggestions = [];
          }
          this.serachEvent(key);
        });
      } else {
        // 关闭弹窗
        if (this.$refs.serachRef && this.$refs.serachRef.suggestions) {
          this.$refs.serachRef.suggestions = [];
        }
        this.serachEvent(key);
      }
    },
    goToSearchRes(flag) {
      const pageName = flag ? "SearchGoods" : "SearchStore";
      const pageUrl = flag ? "/searchGoods" : "/searchStore";
      const keyword = this.searchValue;
      if (this.$route.name !== pageName) {
        this.$router.push({
          path: pageUrl,
          query: {
            k: JSON.stringify(keyword),
          },
        });
      } else {
      this.$router.replace({ path: `${pageUrl}/?k=${encodeURIComponent(JSON.stringify(String(keyword)))}` }, () => {
       location.reload()
       }, () => {
       location.reload()
       })
      }
      // 关闭弹窗
      if (this.$refs.serachRef && this.$refs.serachRef.suggestions) {
        this.$refs.serachRef.suggestions = [];
      }
    },
    
    updateSerachValue(value) {
      this.searchValue = value;
      this.$nextTick(() => {
        this.$refs.serachRef.focus();
      });

      const historyData = cloneDeep(this.historyData);
      historyData.sort((a, b) => (a === value ? -1 : 1));
      setSearchHistoryLocal(historyData);

      if (this.$route.path === "/searchResult" && value) {
        this.$emit("searchValueChange", this.searchValue);
      }
    },
    clearSearchHistory() {
      this.$confirm(this.$t("message.home.delAllHistoryRecord"), {
        confirmButtonText: this.$t("message.home.确认"),
        cancelButtonText: this.$t("message.home.取消"),
        type: "warning",
      }).then(async () => {
        clearSearchHistoryLocal();
        this.SET_HISTORYDATA([]);
      });
    },
    openOnlineService() {
      // console.log("-------1111111111----------");
      !notLogin() && openChatPage(localStorage.getItem("ES_TOKEN"));
    },
    async serachEvent(key) {
      // this.searchValue = key
      if (!this.searchValue) {
        return;
      }
      let historyData = cloneDeep(this.historyData);
      historyData.unshift(this.searchValue);
      historyData = [...new Set(historyData)];
      historyData = historyData.slice(0, 10);
      setSearchHistoryLocal(historyData);
      const params = {
        keyword: encodeURIComponent( key ),
        // isNew: 0,
        // isHot: 0,
        // isPrice: 0,
      };
      const { data } = await SearchApi(params);
      const { sellerList, goodsList } = data;

      const isSeller = !!sellerList.length;

      if (isSeller) {
        const _id = this.$route.query?.id;
        const replaceId = this.id || sellerList[0].id;
        if (_id !== replaceId) {
          this.$router.replace({
            name: "store",
            query: { id: replaceId },
          });
        } else {
          this.$emit("searchValueChange", encodeURIComponent(key));
        }

        localStorage.setItem(
          ES_SEARCH_RESULT,
          JSON.stringify(sellerList || [])
        );
      } else {
        if (this.$route.path !== "/searchResult") {
          this.$router.push({
            name: "searchResult",
            params: { k: encodeURIComponent(key) },
          });
        } else {
          this.$emit("searchValueChange", encodeURIComponent(key));
        }
        localStorage.setItem(ES_SEARCH_RESULT, JSON.stringify(goodsList || []));
      }
    },
  },
};
</script>

<style lang="scss">
html[dir="rtl"]{
  .el-icon-chat-line-round{
    margin: 0 10px;
  }
  .lang-content .el-dropdown{
    margin-left: 0 !important;
  }
  .header-user .no-login span:nth-of-type(3) {
    margin: 0 0 0 26px;
  }
  .header-user .el-icon-user{
    margin-left: 11px;
    margin-right: 0;
  }
  .tuodong{
    direction: ltr;
  }
}

.header {
  width: 100%;
  height: 165px;
  padding-top: 22px;
  // margin-bottom: 24px;
  // position: fixed;
  //   top: 0px;
  //   z-index: 99999;
  //   left: 0;
  //   width: 100%;
    
  &.no-gap {
    margin-bottom: 0;
  }
  &-fiexd{
    padding-top: 22px;
    width: 100%;
    position: fixed;
    top: 0;
    z-index: 999;
    padding-bottom: 22px;
    left: 0;
    width: 100%;
    height: auto !important;
    transition: padding .5s linear 0s;
    background: #fff;
  }
  &-logo {
    img {
      height: 78px;
      // height: 44px;
      margin-right: 15px;
      padding: 4px 0;
      cursor: pointer;
    }

    h1 {
      color: var(--color-black);
      font-size: 26px;
      margin: 0;
    }
  }

  &-search {
    min-width: 367px;
    position: relative;

    .el-autocomplete {
      width: 100%;
    }

    .el-input__inner {
      height: 39px;
      width: 100%;
      padding-left: 44px;
      padding-right: 68px;
      overflow: hidden;
      text-overflow: ellipsis;
      white-space: nowrap;
    }

    .el-icon-search {
      position: absolute;
      top: 50%;
      left: 13px;
      transform: translateY(-50%);
      z-index: 2;
      font-size: 18px;
      color: var(--color-tips);
    }

    .el-button {
      position: absolute;
      right: 5px;
      top: 50%;
      transform: translateY(-50%);
      width: 63px;
      height: 32px;
      padding: 0;
      text-align: center;
    }
  }

  &-user {
    color: var(--color-grey);
    min-width: 300px;
    display: flex;
    justify-content: flex-end;

    .el-icon-user {
      margin-right: 11px;
      font-size: 22px;
      color: var(--color-icon);
    }

    .el-icon-bell,
    .el-icon-download {
      font-size: 22px;
      color: var(--color-icon);
      margin-right: 10px;
      cursor: pointer;
    }
    .el-icon-headset {
      font-size: 22px;
      color: var(--color-icon);
      cursor: pointer;
    }
    .no-login {
      font-size: 12px;
      display: flex;
      .user-name {
        max-width: 120px;
        overflow: hidden;
        text-overflow: ellipsis; //溢出用省略号显示
        white-space: nowrap;
      }
      span:nth-of-type(2) {
        margin: 0 10px;
      }

      span:nth-of-type(3) {
        margin: 0 26px 0 0;
      }

      span {
        cursor: pointer;
      }
    }

    .login {
      cursor: pointer;

      span {
        margin-right: 26px;
      }
    }

    .el-badge {
      cursor: pointer;
    }
  }

  &-nav {
    margin-top: 98px;
    border-bottom: 1px solid var(--color-border);
    padding-bottom: 13px;
    background: #fff;
    ul {
      list-style: none;
      padding: 0;
      color: var(--color-title);
      // max-width: 1200px;
      justify-content: space-between;
      margin: 0 auto;
      width: 860px;
      display: flex;

      li {
        font-size: 14px;
        font-weight: 500;
        // margin-left: 54px;
        cursor: pointer;

        &:hover {
          color: var(--color-main);
        }
      }

      .active {
        color: var(--color-main);
      }
    }
  }
}
.lang-item {
  display: flex;
  justify-content: flex-start;
  align-items: center;

  span {
    margin-left: 8px;
  }
}

.search-popper {
  .el-autocomplete-suggestion__list {
    li {
      padding: 0;

      &:hover {
        background-color: var(--color-white) !important;
      }
    }
  }

  .search-content {
    padding: 0 13px;

    &-item {
      padding: 8px;
      border-bottom: 1px solid var(--color-border);
      font-weight: 500;
      font-size: 12px;
      overflow-x: hidden;
      text-overflow: ellipsis;
    }

    &-history {
      // padding: 16px 0;
      font-weight: 500;
      font-size: 12px;
      color: var(--color-title);

      &-header {
        padding: 6px 0;
      }

      &-list {
        display: flex;
        justify-content: flex-start;
        flex-wrap: wrap;

        > div {
          width: 100%;
          display: flex;
          flex-wrap: wrap;
        }

        .el-tag {
          min-width: 70px;
          max-width: 330px;
          height: 33px;
          text-overflow: ellipsis;
          overflow: hidden;
          white-space: nowrap;
          color: var(--color-subtitle) !important;
          border-color: #f6f6f6 !important;
          background: #f6f6f6 !important;
          text-align: center;
          border-radius: 5px;
          margin-right: 14px;
          margin-bottom: 10px;
        }

        &-list {
          display: flex;
          justify-content: flex-start;
          flex-wrap: wrap;
          width: 100%;

          > div {
            display: flex;
            flex-wrap: wrap;
            width: 100%;
          }

          .el-tag {
            // min-width: 70px;
            height: 33px;
            text-overflow: ellipsis;
            overflow: hidden;
            white-space: nowrap;
            color: var(--color-subtitle) !important;
            border-color: #f6f6f6 !important;
            background: #f6f6f6 !important;
            text-align: center;
            border-radius: 5px;
            margin-right: 14px;
            margin-bottom: 10px;
          }

          .empty {
            width: 100%;
            text-align: center;
            padding: 16px 0;
            color: var(--color-subtitle);
          }
        }
      }

      h1 {
        font-weight: 500;
        font-size: 14px;
        color: var(--color-black);
      }

      .el-icon-delete {
        margin-right: 5px;
      }
    }
  }
}

.el-autocomplete-suggestion {
  .popper__arrow {
    display: none !important;
  }
}

.app-qr-code-wrap {
  padding: 20px;
}
.v-enter-from,
  .v-leave-to {
    opacity: 0;
  }

  .v-enter-to, 
  .v-leave-from {
    opacity: 1;
  }

  .v-enter-active,
  .v-leave-active {
    transition: opacity 2s ease;
  }
</style>
