<template>

 
  <div v-if="dialogVisible" class="tuodong">

   <VueDraggableResizable style="position: fixed;" v-on:dragging="onDrag" :w='480' :h='680' :x='wt' :y='hi'  :active="dialogVisible">
    <el-dialog
    class="es-dialog customer-service-dialog"
    :visible.sync="dialogVisible"
    :center="true"
    :append-to-body="false"
    :destroy-on-close="true"
    :modal-append-to-body='false'
    :modal="false"
    :show-close="false"
    :lock-scroll="true"
  >
    <div slot="title" class="dialog-title">
      <div class="left">
        <img :src="itemname=='FamilyShop' ? require(`@/assets/image/${itemname}/sevice.png`):itemname == 'TikTok' || itemname == 'Laz' ? require(`@/assets/image/${itemname}/logo.png`) : require(`@/assets/image/${itemname}/logo.svg`)" />
        <span style="text-wrap: nowrap">{{ $t("message.home.helpLine") }}</span>
      </div>
      <div class="right" @click="closeSevice">
        <img src="@/assets/image/icon00.png" />
      </div>
    </div>
    <div class="customer-service">
      <div class="customer-service-list">
        <VirtualList
          ref="messageListRef"
          class="list"
          data-key="id"
          :data-sources="chatList"
          :data-component="chatItemView"
          :estimate-size="200"
          page-mode
        />
      </div>

      <div class="customer-service-footer">
        <el-upload
          class="avatar-uploader"
          :action="UploadApi"
          :show-file-list="false"
          :http-request="sendImageContent"
          accept=".jpg,.jpeg,.png,.bmp,.pdf,.JPG,.JPEG,.PBG,.BMP,.PDF"
          :before-upload="beforeUpload"
        >
          <i class="el-icon-picture-outline"></i>
        </el-upload>
        <el-input
          v-model="message"
          type="textarea"
          :rows="1"
          :placeholder="$t('message.home.enterTips')"
          @keyup.enter.native="send"
        />
        <el-button type="priamry" @click="send" :loading="sendLoading">
          {{ $t("message.home.send") }}
        </el-button>
      </div>
    </div>

  </el-dialog>
  
</VueDraggableResizable>
  </div>

</template>

<script>
import { UploadApi } from "@/api";
import VirtualList from "vue-virtual-scroll-list";
import { mapActions, mapGetters } from "vuex";
import EsChatItemView from "./item.vue";
import { ES_TOKEN, ES_MESSAGE_LAST_ID } from "@/common";
import axios from "axios";
import URL from "@/config/index";
import VueDraggableResizable from 'vue-draggable-resizable'
// import { getBase64 } from "@/util";
const userIcon = require("@/assets/image/userIcon.png");
// import logoSvg from "@/assets/image/mateshop-b.svg";
export default {
  name: "EsCustomerService",
  components: { VirtualList,VueDraggableResizable },
  props: {
    show: {
      type: Boolean,
      default: false,
    },
    // xNum: {
    //   type: Number,
    //   default: 0,
    // },
    // yNum: {
    //   type: Number,
    //   default: 0,
    // },
  },
  model: {
    prop: "show",
    event: "update",
  },
  data() {
    return {
      itemname: process.env.VUE_APP_ITEM_NAME,
      dialogVisible: false,
      chatItemView: EsChatItemView,
      message: "",
      imageUrl: "",
      sendLoading: false,
      UploadApi,
      uploadParams: {
        moduleName: "online",
        token: localStorage.getItem(ES_TOKEN),
      },
      timer: null,
      x:0,
      y:0,
      wt:0,
      hi:0,
      // shopImg: logoSvg,
    };
  },
  computed: {
    ...mapGetters({
      unreadMessageList: "user/unreadMessageList",
      messageList: "user/messageList",
      userInfo: "userInfo",
      islogin: "isLogin",
    }),
    chatList() {
      return this.messageList
        .map((item) => ({
          id: item.id,
          userIcon,
          isSelf: item.send_receive === "send",
          content:item.content.replaceAll('\n', '<br/>'),
          contentType: item.type,
          date: item.createtime,
        }))
        .reverse();
    },
  },
  watch: {
    async dialogVisible(newValue, oldValue) {
      if (newValue !== oldValue) this.$emit("update", newValue);
      if (newValue ) {
        // document.body.style.overflow = "hidden";
        const lastId = localStorage.getItem(ES_MESSAGE_LAST_ID);
        await this.requestUnreadMessageList();
        await this.requestMessageList(lastId ? { message_id: lastId } : {});
        this.scrollBottom();
        this.startTimer();
      } else {
        document.body.style.overflow = "visible";
        this.endTimer();
      }
    },
    show(newValue, oldValue) {
      if (newValue !== oldValue) this.dialogVisible = newValue;
    },
  },
  mounted() {
    this.dialogVisible = this.show;
    this.wt = document.documentElement.clientWidth - 480;
    this.hi = document.documentElement.clientHeight - 680;
    // console.log("this.$store ->", this.userInfo);
  },
  destroyed() {
    this.endTimer();
  },
  methods: {
    ...mapActions({
      requestMessageList: "user/requestMessageList",
      requestUnreadMessageList: "user/requestUnreadMessageList",
      requestSendMessage: "user/requestSendMessage",
    }),
     onDrag: function (x, y) {
      if(x<2 ){
       this.x=2
      }else{
      this.x = x
      this.y = y
      }
      
    },

    closeSevice() {
      this.dialogVisible = false;
    },
    async startTimer() {
      this.endTimer();
      await this.requestMessageList();
      this.timer = setInterval(async () => {
        this.requestUnreadMessageList();
        await this.requestMessageList();
        localStorage.setItem(ES_MESSAGE_LAST_ID, this.messageList[0].id);
      }, 5000);
    },
    endTimer() {
      this.timer && clearInterval(this.timer);
    },
    scrollBottom() {
      setTimeout(() => {
        const $$wrap = document.querySelector(".customer-service-list");
        $$wrap.scrollTo(0, $$wrap.scrollHeight);
      }, 300);
    },

    async send() {
      try {
        this.sendLoading = true;
        console.log('this.message ->', this.message);
        this.message =  encodeURIComponent(this.message) ;
        this.requestSendMessage({
          type: "text",
          content: this.message,
        });
        this.message = "";
        setTimeout(() => {
          this.requestMessageList();
          this.scrollBottom();
        }, 1000);
      } finally {
        this.sendLoading = false;
      }
    },

    beforeUpload(file) {
      if (!['image/jpeg', 'image/jpg', 'image/png'].includes(file.type)) {
        return false
      }
      return true
    },

    // uploadSuccess(res, file) {
    //   this.imageUrl = URL.createObjectURL(file.raw)
    //   this.addData(this.imageUrl, 'image')
    // },
    // onSuccess(response, file) {
    //   console.log(response, file)
    //   const formData = new FormData()
    //   formData.append(file, file)

    //   try {
    //     this.sendLoading = true
    //     this.requestSendMessage({
    //       type: 'img',
    //       content: response.data,
    //       file: formData,
    //     })
    //     // this.message = ''
    //     setTimeout(() => {
    //       this.requestMessageList()
    //       this.scrollBottom()
    //     }, 1000)
    //   } finally {
    //     this.sendLoading = false
    //   }
    // },
    async sendImageContent(data) {
      var t = this;
      const formData = new FormData();
      formData.append("file", data.file);
      formData.append("moduleName", "123");
      // formData.append('type', 'img')
      // formData.append('content', await getBase64(data.file))
      // formData.append('token', localStorage.getItem(ES_TOKEN))
     
      //  const fileSuffix = data.file.name.substring(file.name.lastIndexOf('.') + 1)
            // const whiteList = ['pdf', 'doc', 'docx']
            // const isSuffix = whiteList.indexOf(fileSuffix.toLowerCase()) === -1
      // console.log('fileSuffix ->', fileSuffix);
      axios
        .post(`${URL.BASE_URL}api/uploadimg!execute.action`, formData, {
          headers: { "Content-Type": "multipart/form-data" },
        })
        .then((res) => {
          console.log(res);
          try {
            t.sendLoading = true;
            t.requestSendMessage({
              type: "img",
              content: res.data.data,
            });
            // t.message = ''
            setTimeout(() => {
              t.requestMessageList();
              t.scrollBottom();
            }, 1000);
          } finally {
            t.sendLoading = false;
          }
        });
    },
  },
  }
</script>

<style lang="scss">
html[dir="rtl"]{
  .el-dialog{
    direction: rtl;
  }
  .customer-service-dialog .el-dialog .el-dialog__header .dialog-title .left img{
    margin-left: 10px;
    margin-right: 0;
  }
  .customer-service .avatar-uploader{
    margin-left: 10px;
    margin-right: 0;
  }
  .customer-service-footer .el-button {
    margin-right: 10px;
    margin-left: 0;
  }
}
.customer-service-dialog {
  .el-dialog {
    position: absolute;
    bottom: 20px;
    right: 20px;
    width: 460px !important;
    height: 646px;
    border-radius: 4px;
    overflow: hidden;
    .el-dialog__header {
      background-color: var(--color-main) !important;
      height: 44px !important;
      padding: 0 10px !important;
      border-bottom-left-radius: 0 !important;
      border-bottom-right-radius: 0 !important;
      .dialog-title {
        background-color: var(--color-main) !important;
        height: 100%;
        width: 100%;
        line-height: 44px;
        font-size: 14px;
        color: #fff;
        display: flex;
        justify-content: space-between;
        align-items: center;
        .left {
          display: flex;
          align-items: center;
          img {
            height: 34px;
            margin-right: 10px;
          }
        }
        .right {
          width: 8px;
          cursor: pointer;
          img {
            width: 100%;
            height: 100%;
          }
        }
      }
    }
    .el-dialog__body {
      padding: 0 !important;
      height: calc(646px - 44px);
      background-color: #f0f4f9 !important;
    }
  }
}
.customer-service {
  position: relative;
  height: 100%;
  &-list {
    position: relative;
    height: calc(646px - 44px);
    overflow: auto;
    padding: 15px;
    padding-bottom: 44px;
  }
  &-footer {
    position: absolute;
    bottom: 0;
    left: 0;
    right: 0;
    bottom: constant(safe-area-inset-bottom);
    bottom: env(safe-area-inset-bottom);
    display: flex;
    justify-content: flex-start;
    align-items: center;
    background-color: #fff;
    height: 44px;
    padding: 10px 8px;
    box-sizing: border-box;
    font-size: 14px;
    border-radius: 0 0 10px 10px;
    .image-icon {
      font-size: 50px;
      color: #fff;
      margin-left: 20px;
    }
    .el-input {
      .el-input__inner {
        border: 0;
        height: 32px;
        background-color: #f5f5f5;
        // margin: 0 15px 0 10px;
      }
    }
    .el-button {
      background: var(--color-main);
      color: var(--color-white);
      border-color: var(--color-main);
      border-radius: 4px;
      width: 65px;
      height: 30px;
      font-size: 14px;
      padding: 0;
      margin-left: 10px;
      &:hover,
      &:focus {
        color: var(--color-white);
        border-color: var(--color-main);
        background-color: var(--color-main);
      }
    }
  }
  .avatar-uploader {
    margin-right: 10px;
  }
  .el-icon-picture-outline {
    font-size: 20px !important;
    // margin-bottom: 8px;
  }
  
}
.vdr{
    position: absolute;
    z-index: 999 !important;
    pointer-events: auto !important;
  }
  .tuodong{
    position: fixed;
    top: 0;
    bottom: 100px;
    left: 0;
    right: 0;
    z-index: 2001 !important;
    width: 100%;
    height: 100%;
    pointer-events: none;
    // background: #000;
  }
</style>
