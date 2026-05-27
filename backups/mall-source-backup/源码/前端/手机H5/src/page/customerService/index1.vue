<template>
    <div class="service-box">
        <van-nav-bar safe-area-inset-top :title="$t('在线客服')" left-arrow @click-left="onClickLeft" fixed />
        <div style="width: 100%; height: 46px"></div>
        <!--      <div class="h-10 bg-grey w-full"></div> -->
        <div ref="chatView" :class="['content', isApp && 'app_content']">
            <div class="flex flex-col px-15 box-border">
                <div class="w-full py-10 text-grey text-center" @click="onMore"
                    :style="{ visibility: finished ? 'hidden' : 'visiable' }" style="font-size: 14px">
                    {{ $t("历史消息") }}
                </div>
                <ul class="flex flex-col">
                    <li v-for="item in list" :key="item.id" class="flex flex-col mt-20">
                        <p class="font-26 flex py-20 text-grey time"
                            :class="item.send_receive === 'send' ? 'justify-end' : ''" v-if="showTime(item)"
                            style="font-size: 14px">
                            {{ item.createtime }}
                        </p>
                        <div class="flex" :class="item.send_receive === 'send' ? 'justify-end' : ''">
                            <template v-if="item.send_receive === 'receive'">
                                <img :src="responserAvatar" object-fit="cover" class="w-44 h-44 mr-10"
                                    style="border-radius: 50%;" />
                                <div class="responser bg-grey px-15 py-12 font-30 rounded-lg" style="font-size: 14px">
                                    <div class="break-word" v-if="item.type === 'text'">
                                        <p style="max-width: 231px" v-html="item.content">
                                        </p>
                                    </div>

                                    <img v-else :src="item.content" class="max-w-200" @click="onPreview(item.content)" />
                                </div>
                            </template>
                            <div class="border-solid py-12 px-15 rounded-lg flex flex-col" v-else style="font-size: 14px">
                                <img :src="`${item.content}`" class="max-w-200" v-if="item.type === 'img'"
                                    @click="onPreview(item.content)" />
                                <div class="break-word" v-else>
                                    <!-- {{ item.content }} -->
                                    <p style="max-width: 232px" v-html="item.content"></p>
                                </div>
                            </div>
                            <img v-if="item.send_receive === 'send'"
                                :src="require(`@/assets/image/avatar/${userInfo?.avatar || 1}.png`)"
                                style="width: 44px; height: 44px; margin-left: 10px; border-radius: 50%;" />
                        </div>
                    </li>
                </ul>
            </div>
        </div>
        <div class="bottom flex justify-between items-center w-full fixed bottom-0 border-t-grey px-10 box-border bg-white msg_bottom"
            :style="isApp ? { marginBottom: '20px' } : {}">
            <van-uploader :after-read="afterRead">
                <!--          <van-uploader :after-read="afterRead" :capture="androidAttrs ? 'camera' : null" >-->
                <img src="@/assets/image/service/photo.png" class="w-24 h-24" />
            </van-uploader>
            <van-field class="flex-1 mx-20 h-full border-none" v-model="value" rows="1"
                :autosize="{ maxHeight: 25, minHeight: 25 }" type="textarea" maxlength="200"
                :placeholder="$t('请输入您的消息...')" />
            <!-- <input type="text" v-model="value" maxlength="200" :placeholder="$t('请输入您的消息...')"
                class="flex-1 mx-20 h-full border-none" style="font-size: 14px" /> -->
            <!--        <img src="@/assets/image/service/send.png" class="w-34 h-34" @click="send('text', value)"/>-->
            <div class="fasong" @click="send('text', value)">{{ $t('发送') }}</div>
        </div>
    </div>
</template>

<script>
import { _getMsg, _getUnreadMsg, _sendMsg } from "@/API/im.api";
import { _uploadImage } from "@/API/fund.api";
import { Uploader, ImagePreview, Field } from "vant";
import { mapGetters, mapMutations } from "vuex";
import { uploadimg } from "@/API/commodity";
export default {
    name: "CustomerService",
    components: {
        [Uploader.name]: Uploader,
        [Field.name]: Field,
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
            isFirstRequest: true,
            responserAvatar: '',
            msgLength: 0,
            isApp: window.plus ? true : false,
        };
    },
    computed: {
        ...mapGetters({
            activeLang: "language",
            userInfo: "userInfo",
        }),
    },
    mounted() {
        
        if (['Argos','ArgosShop'].includes(process.env.VUE_APP_ITEM_NAME)) {
            this.responserAvatar = require('@/assets/Argos/avatar.png')
        } else if (process.env.VUE_APP_ITEM_NAME == 'FamilyShop') {
            this.responserAvatar = require('@/assets/FamilyShop/avatar.png')
        } else {
            this.responserAvatar = require('@/assets/image/service/responser.png')
        }
        if (this.$route.query.token) {
            this.token_url = this.$route.query.token;
        } else {
            if (localStorage.getItem("token")) {
                this.token_url = localStorage.getItem("token");
            }
        }
        if (this.$route.query.lang) {
            if (this.$route.query.lang == "cn") {
                this.handleSetLang("cn");
                // {title:'繁体中文',key: 'cn'},
                // {title: 'English',key: 'en'}
            } else if (this.$route.query.lang == "tw") {
                this.handleSetLang("tw");
            } else {
                this.handleSetLang("en");
            }
        }
        this.fetchList();
        const model = navigator.userAgent;
        // 判断是否是安卓手机，是则是true
        this.androidAttrs =
            model.indexOf("Android") > -1 || model.indexOf("Linux") > -1;
    },
    methods: {
        ...mapMutations(["setLanguage"]),
        handleSetLang(lang) {
            // 设置i18n.locale 组件库会按照上面的配置使用对应的文案文件
            this.$i18n.locale = lang;
            // 提交mutations
            this.setLanguage(lang);
        },
        onPreview(url) {
            // 预览
            ImagePreview([url]);
        },
        showTime(item) {
            return !!item.createtime;
            //   // 时间显示
            //   if (index === 0) {
            //     return true;
            //   }
            //   if (index === this.list.length - 1) {
            //     return false;
            //   }
            //   if (this.list[index].createtime.split(' ')[0] === this.list[index + 1].createtime.split(' ')[1]) {
            //     return false;
            //   }
        },
        afterRead(file) {
            // 文件上传
            this.$toast.loading({ duration: 0 });
            this.$toast.loading({ duration: 0 });
            var t = this
            let formData = new FormData();//通过formdata上传
            formData.append('file', file.file);
            formData.append('moduleName', '123')
            uploadimg(formData).then(res => {
                t.$toast.clear()
                console.log(res)
                t.send('img', res)
            }).catch((err) => {
                console.log(err)
                this.$toast.clear()
            })
        },
        fetchList(message_id = "") {
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
                        this.list = this.list.reduce((preVal, curVal) => {
                            hash[curVal.id]
                                ? " "
                                : (hash[curVal.id] = true && preVal.push(curVal));
                            return preVal;
                        }, []);
                    }
                    if (data.length < 10) {
                        this.finished = true;
                    }

                    if (this.isFirstRequest) {
                        const _that = this;
                        this.$nextTick(() => {
                            const ele = this.$refs.chatView;
                            if (ele) {
                                ele.scrollTop = ele.scrollHeight;
                                _that.isFirstRequest = false;
                            }
                        });
                    }
                } else {
                    this.list = [
                        {
                            id: "1",
                            send_receive: "receive",
                            content: this.$t("你好，欢迎来到我们的平台！"),
                            type: "text",
                        },
                    ];
                }
                // this.list.unshift({
                //             id: "1",
                //             send_receive: "receive",
                //             content: this.$t("你好，欢迎来到我们的平台！"),
                //             type: "text",
                //         },)
                if (!message_id) {
                    this.clearInterval();
                    this.interval = setInterval(() => {
                        this.fetchList();
                    }, 1000);
                }
                if (this.msgLength !== this.list.length) {
                    this.scrollToBottom()
                    this.msgLength = this.list.length
                }
                this.list = this.list.map((item) => ({
                    ...item,
                    content: item.content.replaceAll('\n', '<br/>')
                }));
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
            if (!content) {
                this.$notify(this.$t("请输入消息内容"));
                return;
            }
            _sendMsg(type, content, this.token_url).then((data) => {
                this.value = "";
                // document.getElementById('bottom').click()
                this.isFirstRequest = true;
                this.fetchList();
            });
        },
        // 滚动条去底部
        scrollToBottom() {
            this.$nextTick(() => {
                try {
                    this.$refs.chatView.scrollTo({ top: this.$refs.chatView.scrollHeight, behavior: 'smooth' });
                } catch (error) {
                    scrollTo(9999999, 9999999)
                }
            })
        }
    },
    beforeDestroy() {
        this.clearInterval();
        this.fetchList = null;
    },
};
</script>
<style lang="scss" scoped>
.time {
    padding-top: 0;
    padding-bottom: 10px;
    padding-left: 54px;

    &.justify-end {
        padding-right: 54px;
    }
}

.content {
    overflow-y: scroll;
    height: calc(100vh - 110px);
    position: fixed;
    width: 100%;
}

.break-word {
    word-break: break-word;
}

// .max-w-230 {
//   //max-width: 230px;
// }
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
    // background: var(--main-color);
    background: var(--main-color);
    border-radius: 45px;
}

.max-w-200 {
    max-width: 200px;
    max-height: 200px;
}
</style>
