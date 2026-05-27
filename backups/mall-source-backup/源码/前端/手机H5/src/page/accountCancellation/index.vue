<template>
    <div class="account_cancellation">
        <van-nav-bar safe-area-inset-top fixed :title="$t('账号注销')" left-arrow @click-left="onClickLeft" />
        <div style="width: 100%;" class="h46"></div>
        <el-form label-position="top" label-width="80px" :model="formLabelAlign" class="acc_form">
            <el-form-item :label="$t('您的账号')">
                <el-input maxlength="50" disabled v-model.trim="formLabelAlign.account"></el-input>
            </el-form-item>
            <el-form-item :label="$t('为什么要离开?')">
                <el-input type="textarea" maxlength="1000" :autosize="{ minRows: 6, maxRows: 8 }"
                    v-model.trim="formLabelAlign.reason"></el-input>
            </el-form-item>
        </el-form>
        <div class="logout" @click="onLogout">{{ $t('注销账号') }}</div>
        <!-- 密码弹窗 -->
        <van-popup v-model="pwtStatus" position="bottom">
            <enter-Password :isPasswordShow="pwtStatus" @close="pwtStatus = false"
                @getPassword="getPassword"></enter-Password>
        </van-popup>
    </div>
</template>

<script>
import { Popup, Dialog } from "vant";
import { mapGetters } from 'vuex'
import { gerenxinxi_post, apilogoff, huoquyue_post } from '@/API/user';
import EnterPassword from "@/components/EnterPassword/index.vue";
export default {
    components: {
        EnterPassword,
        [Popup.name]: Popup,
        [Dialog.name]: Dialog,
    },
    data() {
        return {
            itemName: process.env.VUE_APP_ITEM_NAME,
            formLabelAlign: {
                account: '',
                reason: '',
                cashPassword: '',
            },
            pwtStatus: false,
        }
    },
    async created() {
        const { username } = await gerenxinxi_post({})
        this.formLabelAlign.account = username
    },
    computed: {
        ...mapGetters({
            userInfo: 'userInfo'
        })
    },
    methods: {
        onClickLeft() {
            this.$router.go(-1)
        },
        onLogout() {
            if (this.formLabelAlign.account.trim() == '') {
                this.$notify(this.$t('请输入您的账号'), 'warning')
                return
            }
            if (this.formLabelAlign.reason.trim() == '') {
                this.$notify(this.$t('请输入您的离开原因'), 'warning')
                return
            }
            let message = this.$t('警告！请谨慎操作注销账户，如果您不再使用该账号，可点击【同意注销】，注销后可能几天内无法注册。')
            if (process.env.VUE_APP_PUT_ON_SHELVES) {
                message = this.$t('警告！请谨慎操作注销账户，如果您不再使用该账号，可点击【同意注销】，注销后72小时内无法注册。')
            }
            Dialog.alert({
                title: this.$t('您确认要注销账号吗？'),
                message,
                messageAlign: 'left',
                showCancelButton: true,
                confirmButtonText: this.$t('同意注销'),
                confirmButtonColor: '#FF0000',
                cancelButtonText: this.$t('取消'),
                cancelButtonColor: '#999999',
            }).then(async () => {
                this.$toast.loading()
                const { money } = await huoquyue_post()
                if (money !== 0) {
                    this.$notify(this.$t('该账号存在可用余额, 不可注销!'), 'warning')
                    this.$toast.clear()
                    return
                }
                if (this.userInfo.safeword == 0) {
                    this.getPassword(null)
                } else {
                    this.pwtStatus = true;
                }
            });
        },
        async getPassword(value) {
            this.formLabelAlign.cashPassword = value;
            this.$toast.loading()
            if (value == '') {
                this.$notify(this.$t('请输入密码'), 'warning')
                this.$toast.clear()
                return
            }

            try {
                const res = await apilogoff(this.formLabelAlign)
                this.$toast.clear()
                this.$notify(this.$t('注销成功'), 'success')
                this.$router.replace('/login')
            } catch (error) {
                console.log(`error ::->`, error);
            }

            // if (value == '123456') {
            //     this.$toast(this.$t('注销成功'))
            //     this.$router.push('/login')
            // } else {
            //     this.$toast(this.$t('密码错误'))
            // }

        },
    }
}
</script>

<style lang="scss" scoped>
.acc_form {
    padding: 0 15px;

    :deep(.el-form-item__label) {
        padding: 0 !important;
        font-weight: 600;
        font-size: 16px;
        color: #333;
    }
}

:deep(input) {
    padding-right: 60px;
}

.logout {
    margin: 15px 15px;
    margin-top: 56px;
    background: var(--main-color);
    border-radius: 4px;
    height: 44px;
    font-style: normal;
    font-weight: 400;
    font-size: 16px;
    line-height: 44px;
    text-align: center;
    color: #FFFFFF;
}
</style>
<style lang="scss">
.van-dialog__message {
    padding-top: 20px;
    line-height: 25px;
    border: none;
}

.van-dialog__footer {
    padding: 0 15px 30px 15px;

    &::after {
        display: none;
    }

    button {
        border: none;
        border-radius: 8px;

        &:nth-child(1) {
            border: 1px solid #999999;
            margin-right: 10px;
        }

        &:nth-child(2) {
            background: #DA3231;
            color: #FFFFFF !important;
        }

        &::before {
            display: none;
        }

        &::after {
            display: none;
        }
    }
}
</style>