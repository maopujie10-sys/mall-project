<template>
    <div class="enter-password">
        <van-popup closeable :close-on-click-overlay="true" @close="close" v-model="isPasswordShow" position="bottom"
            class="pass_pop">
            <div class="pop-header-title">
                {{ $t('输入交易密码') }}
            </div>
            <div class="passsword-wrap">
                <p>{{ $t('输入您的交易密码') }}</p>
                <van-password-input :value="user_password" :focused="showKeyboard" :maxlength="6" :error-info="errorInfo"
                    @focus="getKeyboard" />
                <van-number-keyboard v-model="user_password" :show="showKeyboard" @blur="showKeyboard = true" />
                <button @click="submitPaw()" :disabled="user_password.length < 6" class="submit-but">
                    {{ $t('确定') }}
                </button>
            </div>
        </van-popup>
    </div>
</template>
<script type="text/javascript">
// eslint-disable-next-line
/* eslint-disable */
import { Overlay, PasswordInput, NumberKeyboard, Popup } from 'vant';
export default {
    name: 'EnterPassword',
    props: {
        isPasswordShow: {
            type: Boolean,
            default: false,
        }
    },
    data() {
        return {
            user_password: '',
            showKeyboard: true,
            errorInfo: '',
            pop_height: '35%'
        }
    },
    // mounted() {
    //     this.showKeyboard ? this.pop_height = '480px' : this.pop_height = '35%';
    // },
    components: {
        [Overlay.name]: Overlay,
        [PasswordInput.name]: PasswordInput,
        [NumberKeyboard.name]: NumberKeyboard,
        [Popup.name]: Popup,
    },
    methods: {
        //获取数字键盘
        getKeyboard() {
            this.showKeyboard = true
        },
        close() {
            this.errorInfo = '';
            this.user_password = ''
            this.$emit('close')

        },
        submitPaw() {
            if (this.user_password.length < 6) {
                return;
            } else {
                // if (this.user_password !== '123456') {
                //   this.errorInfo = this.$t('交易密码错误');
                // } else {
                this.errorInfo = '';
                this.$emit('getPassword', this.user_password)
                this.close()
                // }
            }
        }
    },
    watch: {
        // showKeyboard(val) {
        //     if (val) {
        //         this.pop_height = '73%';
        //     } else {
        //         this.pop_height = '35%';
        //     }
        // },
    }
}

</script>
<style lang="scss" scoped>
.enter-password {
    .pass_pop {
        height: 500px !important;
    }

    .pop-header-title {
        height: 55px;
        text-align: center;
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        line-height: 55px;
        border-bottom: 1px solid #EEEEEE;
        font-size: 16px;
        color: #333333;
    }

    .passsword-wrap {
        padding: 65px 10px 10px 10px;

        p {
            padding: 10px 0 20px 0;
            font-size: 16px;
        }
    }

    .submit-but {
        width: 100%;
        height: 45px;
        border: none;
        font-size: 16px;
        background: var(--main-color);
        color: #fff;
        border-radius: 4px;
        margin-top: 20px;

        &:disabled {
            background: #EEEEEE;
            color: #888CA1;
        }
    }

}

/deep/ .van-password-input__info {
    color: #E10015 !important;
}

/deep/ .van-password-input {
    margin: 0 !important;
}

/deep/ [class*=van-hairline]::after {
    border: 1px solid #dddddd !important;
}

/deep/ .van-password-input__item--focus {
    border: 1px solid var(--main-color) !important;
}
:deep(.van-key__wrapper) {
    &:nth-child(10) {
        svg {
            display: none;
        }
    }
}
</style>
