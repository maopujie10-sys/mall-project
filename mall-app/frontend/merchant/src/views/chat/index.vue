<template>
  <div class="chat-container">
    <audio ref="chatAudioDD" style="display: none;">
      <source :src="require('@/assets/dingdong.mp3')" type="audio/mpeg">
    </audio>
    <div class="chat-icon" @click="showChat=!showChat">
      <i class="el-icon-chat-dot-round"
         style="color: #FFFFFF;font-size: 24px;"
         @click="showChatView"></i>
      <div class="icon-number" v-if="totalUnreadMessages>0">{{ totalUnreadMessages }}</div>
    </div>
    <div class="chat-content" v-if="showChat">
      <div ref="chatMain" class="chat-main">
        <div class="chat-icon-close" @click="showChat=!showChat">
          <i class="el-icon-close"
             style="color: #FFFFFF;font-size: 32px;"
             @click="showChatView"></i>
        </div>
        <iframe :src="iframeSrc" class="iframe"
                frameborder="0"></iframe>
      </div>
    </div>
  </div>
</template>

<script>
import {Picker} from 'emoji-mart-vue'
import {getToken} from '@/utils/auth'
import {seller_info_action_post} from "@/api/user";
import {getOrigin} from "@/utils/utis";

export default {
  name: "index",
  created() {
    this.Token = getToken()
  },
  data() {
    return {
      showChat: false,
      msg: '',
      Token: getToken,
      windowWidth: 1000,
      windowHeight: 700,
      setBootStepState: true,
      //客户信息
      customerInfo: {
        name: null,
        partyid: null
      },
      iframeSrc: null,
      info: {}
    }
  },
  computed: {
    totalUnreadMessages() {
      return (this.$store.getters.totalUnreadMessages > 99 ? 99 : this.$store.getters.totalUnreadMessages) + ''
    },
  },
  watch: {
    totalUnreadMessages(newVal, oldVal) {
      if (newVal - 0 > oldVal - 0) {//有新消息
        this.userClick && this.$refs["chatAudioDD"].play();
      }
    },
  },
  mounted() {
    this.seller_info_action()
    if (this.$refs.chatMain) {
      this.$nextTick(() => {
        setTimeout(() => {
          this.windowWidth = this.$refs.chatMain.clientWidth - 80
          this.windowHeight = this.$refs.chatMain.clientHeight - 80
        }, 400)
      })
    }

  },
  methods: {
    showChatView() {
      this.$refs.chatMain.style.display = 'block'
    },
    seller_info_action() {
      seller_info_action_post({}).then((e) => {
        this.info = e.data
        if (this.$route.query.name && this.$route.query.partyid) {
          this.customerInfo.name = this.$route.query.name
          this.customerInfo.partyid = this.$route.query.partyid
          this.iframeSrc = getOrigin() + '/chat/#/pc/blue?token=' + this.Token + '&name=' + this.customerInfo.name + '&partyid=' + this.customerInfo.partyid + '&selfimg=' + this.info.avatar + '&type=shop&lang=' + this.$store.getters.lang
        } else {
          this.iframeSrc = getOrigin() + '/chat/#/pc/blue?token=' + this.Token + '&selfimg=' + this.info.avatar + '&type=shop&lang=' + this.$store.getters.lang
        }
      }).catch((e) => {
      })
    },
    setBootSteps(e) {
      this.setBootStepState = e
    },
    addEmoji(e) {
      this.msg += e.native
    }
  },
  components: {
    Picker,
  }
}
</script>

<style lang="scss" scoped>
.chat-container {
  position: fixed;
  z-index: 9999999;

  .chat-icon {
    position: fixed;
    right: 27px;
    bottom: 77px;
    background-color: #2C78F8;
    width: 42px;
    height: 42px;
    border-radius: 50%;
    display: flex;
    justify-content: center;
    align-items: center;
    cursor: pointer;
    z-index: 9999999;

    .icon-number {
      position: absolute;
      right: -4px;
      top: -4px;
      font-size: 12px;
      background-color: red;
      border-radius: 50%;
      width: 20px;
      height: 20px;
      text-align: center;
      line-height: 12px;
      padding: 4px;
      box-sizing: border-box;
      color: #FFFFFF;
      transform: scale(.9);
    }
  }
}

.chat-content {
  position: fixed;
  z-index: 9999998;
  left: 0;
  top: 0;
  background-color: rgba(0, 0, 0, .5);
  width: 100%;
  height: 100%;

  .chat-icon-close {
    position: absolute;
    right: 6px;
    top: 6px;
    width: 32px;
    height: 32px;
    border-radius: 50%;
    display: flex;
    justify-content: center;
    align-items: center;
    cursor: pointer;
    z-index: 9999999;
  }
}


h2 {
  margin: 0;
}

.chat-main {
  flex: 1;
  width: 1060px;
  height: 646px;
  box-shadow: 0 0 10px rgba(0, 0, 0, .2);
  left: 50%;
  top: 50%;
  position: absolute;
  transform: translate(-50%, -50%);

  ::v-deep .cardIframe > .el-card__body {
    padding: 0;
    height: 700px;
    box-shadow: none;
  }

  ::v-deep .iframe {
    width: 100%;
    height: 100%;
  }
}

.chat-item {
  padding: 15px;
  border-bottom: 1px solid #eee;

  img {
    object-fit: cover;
  }

  p {
    width: 200px;
    font-size: 14px;
    color: #999;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }
}

.emoji {
  transition: all ease .4s;

  &:hover {
    transform: scale(1.2);
  }
}

</style>
