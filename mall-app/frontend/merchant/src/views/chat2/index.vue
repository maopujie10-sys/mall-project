<template>
  <div class="service-box" style="display: flex;flex-direction: column;height: 100%;background-color: #F0F4F9;">
    <!--    <div class="h-10 bg-grey w-full"></div>-->
    <div class="content" style="flex: 1;overflow-y: scroll;" ref="content">
      <div class="flex flex-col px-6 box-border" style="margin-bottom: 24px;" ref="msg">
        <div v-if="!finished" :style="{'visibility': finished ? 'hidden' : 'visiable'}"
             style="cursor: pointer"
             class="w-full py-10 text-grey text-center pt-100"
             @click="onMore">{{ $t('历史消息') }}
        </div>
        <ul class="flex flex-col pt-20">
          <!--          {{list}}-->
          <li v-for="(item,index) in list" :key="item.id" class="flex flex-col mt-20">

            <!--            {{list}}111-->
            <p v-if="item.showTime" class="font-16 text-center py-20 text-grey">
              <!--              {{ item.createtime && item.createtime.split(' ')[0] }}-->
              {{ item.createtime && item.createtime }}
            </p>
            <div :class="item.send_receive === 'send' ? 'justify-end': ''" class="flex">
              <template v-if="item.send_receive === 'receive'">
                <img class="w-44 h-44 mr-10" v-if="['FamilyShop','JustShop'].includes(projectTitle)"
                     :src="require('@/assets/images/login/logo.png')" style="border-radius: 50%;"/>
                <img class="w-44 h-44 mr-10" v-else :src="require('@/assets/avatar/live.png')"
                     style="border-radius: 50%;"/>
                <div class="bg-grey px-15 py-12 font-16 rounded-lg" style="background-color: #FFFFFF;">
                  <div v-if="item.type === 'text'" class="break-word"
                       style="max-width: 230px; font-size: 14px;text-align: left;" v-html="formattedText(item.content)">
                  </div>
                  <img v-else :src="item.content" class="w-200 h-200" @click="onPreview(item.content)"/>
                </div>
              </template>
              <div v-else style="display: flex;justify-content: flex-end">
                <div class="py-12 px-15 rounded-lg flex flex-col" style="background: #FFFFFF;">
                  <img v-if="item.type === 'img'" :src="`${item.content}`" class="w-200 h-200"
                       @click="onPreview(item.content)"/>
                  <div v-else class="break-word" style="max-width: 230px; font-size: 14px;text-align: left;"
                       v-html="formattedText(item.content)">
                  </div>
                </div>
                <img class="w-44 h-44 mr-10" :src="avatar||require('@/assets/avatar/2.png')"
                     style="display: block;border-radius: 50%;margin-left: 12px"/>
              </div>
            </div>
          </li>
        </ul>
      </div>
      <div style="width: 100%;height: 20px;"></div>
    </div>
    <div
        class="bottom flex justify-between h-49 items-center w-full fixed bottom-0 border-t-grey px-10 box-border bg-white"
        style="display: flex;width: 412px;">
      <div class="pointer">
        <van-uploader :after-read="afterRead" :capture="androidAttrs ? 'camera' : null" :max-size="10000 * 1024"
                      @oversize="onOversize">
          <img class="w-24 h-24" src="@/assets/images/service/photo.png"/>
        </van-uploader>
      </div>
      <!--      <img src="@/assets/images/service/send.png" class="w-20 h-20"  @click="send('text', value)" />-->
      <el-input v-model="value" :placeholder="$t('请输入您的消息')" class="flex-1 mx-20 h-full border-none no-resize"
                style="flex: 1;" :rows="1"
                type="textarea" v-on:keyup.enter="send('text', value)"/>
      <!--      <div>-->
      <img class="w-20 h-20 pointer" src="@/assets/images/service/send.png" @click="send('text', value)"/>
      <!--      </div>-->

    </div>
  </div>
</template>

<script>
import {_getMsg, _getUnreadMsg, _sendMsg} from '@/api/im.api'
import {ImagePreview, Uploader} from 'vant'
import Toast from "@/utils/toast";
import {imageUpload} from "@/api/user";
import {mapGetters} from "vuex";
import moment from 'moment'
import {projectTitle} from "@/settings";

export default {
  name: 'CustomerService',
  components: {
    [Uploader.name]: Uploader
  },
  data() {
    return {
      list: [],
      projectTitle,
      value: '',
      lastMsgId: '',
      interval: null,
      unread: 0,
      finished: false, // 没有历史消息
      androidAttrs: null,
      lock: true,
    }
  },
  computed: {
    ...mapGetters(["avatar",]),
  },
  created() {
    this.fetchList()
    const model = navigator.userAgent;
    // 判断是否是安卓手机，是则是true
    this.androidAttrs = model.indexOf('Android') > -1 || model.indexOf('Linux') > -1
  },
  methods: {
    formattedText(text) {
      return text.replace(/(\r\n)|(\n)/g, '<br/>')
    },
    onOversize(file) {
      console.log(file);
      Toast('文件大小不能超过10m');
    },
    onPreview(url) { // 预览
      ImagePreview([url])
    },
    afterRead(file) { // 文件上传
      let t = this
      let formData = new FormData();//通过formdata上传
      formData.append('file', file.file);
      formData.append('moduleName', '123')
      imageUpload(formData).then(res => {
        t.send('img', res.data)
      }).catch(function (err) {
        console.log(err)
        Toast.clear();
      })
    },
    fetchList(message_id = '') { // 获取消息列表
      _getMsg({message_id}).then(e => { // this.lastMsgId
        let data = e.data
        if (!this.lastMsgId) {
          this.lastMsgId = data.length && data[data.length - 1]['id']
        }
        if (data.length) {
          if (this.lock) {
            setTimeout(() => {
              this.$refs.content.scrollTop = 1000000000000
            }, 300)
          }
          this.lock = false
          if (message_id) { // 加载更多
            this.lastMsgId = data[data.length - 1]['id']
            this.list = [...data.reverse(), ...this.list]
          } else {
            this.list = [...this.list, ...data.reverse()]
            let hash = {};
            this.list = this.list.reduce(function (preVal, curVal) {
              hash[curVal.id] ? ' ' : hash[curVal.id] = true && preVal.push(curVal);
              return preVal
            }, []);
          }
          if (data.length < 10) {
            this.finished = true
          }
          let lastTime = ''
          this.list.forEach((item, index) => {
            let newTime = moment(item.createtime, "YYYY-MM-DD hh:mm")
            if (index === 0) {
              lastTime = moment(item.createtime, "YYYY-MM-DD hh:mm")
              item.showTime = true
            } else {
              if (newTime.diff(lastTime, 'minutes') > 5) {
                item.showTime = true
                lastTime = newTime
              } else {
                item.showTime = false
              }
            }
          })
        } else {
          this.list = []
        }
        if (!message_id) {
          this.clearInterval()
          this.interval = setInterval(() => {
            this.fetchList()
          }, 3000)
        }
      })
    },
    onMore() { // 加载更多
      this.fetchList(this.lastMsgId)
    },
    clearInterval() {
      if (this.interval) {
        clearInterval(this.interval)
        this.interval = null
      }
      console.log(this.interval)
    },
    fetchUnread() { // 获取未读
      _getUnreadMsg().then(data => {
        this.unread = data
        // console.log(data)
      })
    },
    onClickLeft() { // 返回
      this.$router.go(-1);
    },
    send(type = 'text', content = '') { // 发送消息, img 也当消息text
      if (!content) {
        Toast(this.$t('请输入消息内容'))
        return
      }
      _sendMsg(type, content).then(data => {
        console.log(data)
        this.value = ''
        // document.getElementById('bottom').click()
        this.fetchList()
        setTimeout(() => {
          this.$refs.content.scrollTop = 1000000000000
        }, 300)
      })
    }
  },
  beforeDestroy() {
    while (this.interval > 0) {
      window.clearInterval(this.interval)
      this.interval--
    }
  }
}
</script>

<style lang="scss" scoped>

.break-word {
  word-break: break-all;
}

.max-w-230 {
  max-width: 230px;
}

.responser {
  position: relative;

  &::after {
    content: '';
    width: 0;
    height: 0;
    border-top: 10px solid transparent;
    border-bottom: 10px solid transparent;
    border-right: 20px solid #f3f3f3;
    position: absolute;
    left: -20px;
    top: 20px;
  }
}

::v-deep {
  .no-resize {
    padding: 6px;

    textarea {
      resize: none;
      height: 40px;
      border: none;
    }
  }

  .el-textarea__inner {
    color: #2b2f3a !important;
  }
}
</style>
