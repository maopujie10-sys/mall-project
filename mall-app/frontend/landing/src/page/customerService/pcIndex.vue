<template>
  <div class="container" v-if="isShow">
    <div class="service-box">
      <div class="header">
        <div class="logo">
          <img :src="itemname == 'FamilyShop' ? require(`@/assets/image/${itemname}/sevice.png`) :itemname =='TikTok' || itemname == 'Laz'? require(`@/assets/image/${itemname}/logo.png`): require(`@/assets/image/${itemname}/logo.svg`)" alt="" />
          {{ itemname }} {{ $t("footer_helpLine") }}
        </div>

        <img
          class="icon"
          src="@/assets/image/icon00.png"
          alt=""
          @click="close"
        />
        <!-- </div> -->
      </div>
      <!--      <div class="h-10 bg-grey w-full"></div> -->
      <div class="content">
        <div class="flex flex-col px-15 box-border">
          <div
            class="w-full py-10 text-grey text-center"
            @click="onMore"
            :style="{ visibility: finished ? 'hidden' : 'visiable' }"
            style="font-size: 14px"
          >
            {{ $t("历史消息") }}
          </div>
          <ul class="flex flex-col pt-20">
            <li
              v-for="(item, index) in list"
              :key="item.id"
              class="flex flex-col mt-20"
              v-show="item.delete_status == 0"
            >
              <p
                class="font-26 text-center py-20 text-grey"
                v-if="showTime(index)"
                style="font-size: 14px"
              >
                {{
                  item.createtime 
                }}
              </p>
              <div
                class="flex"
                :class="item.send_receive === 'send' ? 'justify-end' : ''"
              >
                <template v-if="item.send_receive === 'receive'">
                  <img
                    :src="itemname == 'FamilyShop' ? require(`@/assets/image/${itemname}/sevice.png`) :itemname =='TikTok'? require(`@/assets/image/${itemname}/TikToklogo.png`): require(`@/assets/image/${itemname}/logo.svg`)"
                    class="w-44 h-44 mr-10"
                  />
                  <div
                    class="responser bg-grey px-15 py-12 font-30 rounded-lg"
                    style="font-size: 14px"
                  >
                    <p
                      class="break-word"
                      style="max-width: 230px"
                      v-if="item.type === 'text'"
                    >
                      {{ item.content }}
                    </p>
                    <img
                      v-else
                      :src="item.content"
                      class="w-200 h-200"
                      @click="onPreview(item.content)"
                    />
                  </div>
                </template>
                <div
                  class="border-solid py-12 px-15 rounded-lg flex flex-col"
                  v-else
                  style="font-size: 14px"
                >
                  <img
                    :src="`${item.content}`"
                    class="w-200 h-200"
                    v-if="item.type === 'img'"
                    @click="onPreview(item.content)"
                  />
                  <p class="break-word" v-else style="max-width: 230px">
                    {{ item.content }}
                  </p>
                </div>
                <img
                  v-if="item.send_receive === 'send'"
                  :src="userAvatar"
                  class="avatar"
                />
              </div>
            </li>
          </ul>
        </div>
      </div>
      <div
        class="bottom flex justify-between footer items-center w-full bottom-0 border-t-grey px-10 box-border bg-white"
      >
        <van-uploader :after-read="afterRead">
          <!--          <van-uploader :after-read="afterRead" :capture="androidAttrs ? 'camera' : null" >-->
          <img src="@/assets/image/service/photo.png" class="w-24 h-24" />
        </van-uploader>
        <input
          type="text"
          v-model="value"
          :placeholder="$t('请输入您的消息...')"
          class="flex-1 mx-20 h-full border-none"
          style="font-size: 14px"
        />
        <!--        <img src="@/assets/image/service/send.png" class="w-34 h-34" @click="send('text', value)"/>-->
        <div class="fasong" @click="send('text', value)">{{ $t("发送") }}</div>
      </div>
    </div>
  </div>
</template>

<script>
import {
  _getMsg,
  _getUnreadMsg,
  _sendMsg,
  tupianshangchuan_post2,
} from "@/API/im.api";
// import { _uploadImage } from "@/API/fund.api";
import { Uploader, ImagePreview } from "vant";
import { mapGetters, mapMutations } from "vuex";
// import { tupianshangchuan_post } from "@/API/user";
export default {
  name: "CustomerService",
  components: {
    [Uploader.name]: Uploader,
  },
  props: {
    isShow: {
      type: Boolean,
      default: false,
    },
  },
  data() {
    return {
      list: [],
      value: "",
      lastMsgId: "",
      interval: null,
      unread: 0,
      finished: false, // 没有历史消息
      androidAttrs: null,
      token_url: "",
      userAvatar: "",
      count: "1",
      itemname: process.env.VUE_APP_ITEM_NAME,
      // show:this.isShow,
    };
  },
  computed: {
    ...mapGetters({
      activeLang: "language",
    }),
  },
  created() {
    this.count = localStorage.getItem("avater");
    this.userAvatar = require(`@/assets/image/avatar/${this.count || "2"}.png`);

    if (this.$route.query.token) {
      this.token_url = this.$route.query.token;
    } else {
      if (localStorage.getItem("token")) {
        this.token_url = localStorage.getItem("token");
      }
    }
    if (this.$route.query.lang) {
      if (this.$route.query.lang == "cn") {
        this.handleSetLang("zh-CN");
        // {title:'繁体中文',key: 'zh-CN'},
        // {title: 'English',key: 'en-US'}
      } else if (this.$route.query.lang == "en-us") {
        this.handleSetLang("en-US");
      } else {
        this.handleSetLang("CN");
      }
    }
    // this.fetchList();
    const model = navigator.userAgent;
    // 判断是否是安卓手机，是则是true
    this.androidAttrs =
      model.indexOf("Android") > -1 || model.indexOf("Linux") > -1;
  },
  methods: {
    close() {
      // console.log('this.$refs ->', this.$ref);
      // this.show = false
      this.$emit("show", false);
    },
    ...mapMutations(["setLanguage"]),
    handleSetLang(lang) {
      // 设置i18n.locale 组件库会按照上面的配置使用对应的文案文件
      close;
      this.$i18n.locale = lang;
      // 提交mutations
      // this.setLanguage(lang)
    },
    onPreview(url) {
      // 预览
      ImagePreview([url]);
    },
    showTime(index) {
      // 时间显示
      if (index === 0) {
        return true;
      }
      if (index === this.list.length - 1) {
        return false;
      }
      if (
        this.list[index].createtime.split(" ")[0] ===
        this.list[index + 1].createtime.split(" ")[1]
      ) {
        return false;
      }
    },
    afterRead(file) {
      // 文件上传
      // // this.$toast('请输入消息内容')
      this.$toast.loading({ duration: 0 });
      // _uploadImage(file,this.token_url,(percent) => {
      //     console.log(percent)
      // }).then(data => {
      //   // this.$toast('成功')
      //     this.$toast.clear()
      //     // this.send('img', data)
      // }).catch((e) => {
      //   // this.$toast('失败')
      //   // this.$toast(e)
      //     this.$toast.clear()
      // })
      var t = this;
      let formData = new FormData(); //通过formdata上传
      formData.append("file", file.file);
      formData.append("moduleName", "123");
      tupianshangchuan_post2(formData)
        .then((res) => {
          t.$toast.clear();
          console.log(res);
          t.send("img", res);
        })
        .catch(function (err) {
          console.log(err);
          this.$toast.clear();
        });
    },
    fetchList(message_id = "") {
      // if(!this.list.length){
      //   location.reload()
      // }
      // 获取消息列表
      _getMsg({ token: this.token_url, message_id }).then((data) => {
        // this.lastMsgId
        if (data == null) {
          data = [];
        }
        if (!this.lastMsgId) {
          this.lastMsgId = data.length && data[data.length - 1]["id"];
        }
        if (data.length) {
          if (message_id) {
            // 加载更多
            this.lastMsgId = data[data.length - 1]["id"];
            this.list = [...data.reverse(), ...this.list];
          } else {
            this.list = [...this.list, ...data.reverse()];
            let hash = {};
            this.list = this.list.reduce(function (preVal, curVal) {
              hash[curVal.id]
                ? " "
                : (hash[curVal.id] = true && preVal.push(curVal));
              return preVal;
            }, []);
          }
          if (data.length < 10) {
            this.finished = true;
          }
        } else {
          this.list = [
            {
              id: "1",
              send_receive: "receive",
              content: this.$t("你好，欢迎来到我们的平台"),
              type: "text",
            },
          ];
        }
        if (!message_id) {
          this.clearInterval();
          this.interval = setInterval(() => {
            this.fetchList();
          }, 1000);
        }
        this.list.forEach((item) => {
            data.forEach((item1) => {
                if (item.id == item1.id && item1.delete_status != item.delete_status) {
                    item.delete_status = item1.delete_status
                }
            });
        });
      });
      
    },
    onMore() {
      // 加载更多
      this.fetchList(this.lastMsgId);
    },
    clearInterval() {
      if (this.interval) {
        clearInterval(this.interval);
        this.interval = null;
      }
    },
    fetchUnread() {
      // 获取未读
      _getUnreadMsg().then((data) => {
        this.unread = data;
        // console.log(data)
      });
    },
    onClickLeft() {
      // 返回
      this.$router.go(-1);
    },
    send(type = "text", content = "") {
      // 发送消息, img 也当消息text
      console.log("fasong");
      console.log(content);
      if (!content) {
        this.$toast(this.$t("请输入消息内容"));
        return;
      }
      _sendMsg(type, content, this.token_url).then((data) => {
        console.log(data);
        this.value = "";
        // document.getElementById('bottom').click()
        this.fetchList();
      });
    },
  },
  beforeDestroy() {
    this.clearInterval();
  },
};
</script>
<style lang="scss" scoped>
.container {
  // width: 100%;
  // height: 100%;
  // background-color: rgba(114, 114, 114, 0.4);
  // position: fixed;
  //   top: 0;
  //   right: 0;
  //   bottom: 0;
  //   left: 0;
  //   overflow: auto;
  //   margin: 0;
}
.header {
  height: 44px;
  display: flex;
  padding: 0 10px;
  background: var(--color-main);
  align-items: center;
  justify-content: space-between;
  font-size: 14px;
  line-height: 44px;
  .logo {
    display: flex;
    color: #fff;
    align-items: center;
  }
  img {
    height: 34px;
    margin-right: 6px;
  }
  .icon {
    padding: 10px;
    display: inline-block;
    width: 8px;
    height: 8px;
    cursor: pointer;
  }
}
.service-box {
  width: 460px;
  height: 646px;
  position: fixed;
  background-color: #fff;
  bottom: 20px;
  box-shadow: 0px 18px 36px rgba(19, 26, 40, 0.2);
  border-radius: 4px;
  right: 20px;
  overflow: hidden;
}
.content {
  overflow-y: scroll;
  height: calc(646px - 98px);
}
.break-word {
  word-break: break-all;
}
.max-w-230 {
  //max-width: 230px;
}
.footer {
  margin-top: 8px;
  height: 44px !important;
}
.responser {
  position: relative;
  //&::after {
  //    content: '';
  //    width:0;
  //    height:0;
  //    border-top:10px solid transparent;
  //    border-bottom:10px solid transparent;
  //    border-right:20px solid #f3f3f3;
  //    position: absolute;
  //    left: -20px;
  //    top: 20px;
  //}
}
.fasong {
  width: 74px;
  height: 34px;
  font-style: normal;
  font-weight: 400;
  font-size: 14px;
  line-height: 34px;
  text-align: center;
  color: #ffffff;
  background: var(--color-main);
  border-radius: 10px;
}
.avatar {
  width: 44px;
  height: 44px;
  border-radius: 100%;
  margin-left: 6px;
}
</style>
