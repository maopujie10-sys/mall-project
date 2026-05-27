<template>
    <div style="min-height: 100vh;">
        <van-nav-bar safe-area-inset-top fixed :title="$t('设置')" left-arrow @click-left="onClickLeft" />
        <div style="width: 100%;" class="h46"></div>

        <div class="nav-content">
            <div v-for="(item, index) in navData" :key="index" class="item" @click="openWin(item.path)">
                <div class="name">
                    <p>{{ item.name }}</p>
                </div>
                <div class="arrow">
                    <p v-if="item?.tips">{{ item?.tips }}</p>
                    <img class="image_reversed" :src="images.arrow" alt="">
                </div>
            </div>
        </div>

        <div class="tuichu" @click="tuichu">{{ $t('退出') }}</div>
        <div class="version">v{{ version }}</div>
    </div>
</template>

<script>
import { NavBar } from 'vant';
import { isLogin } from '@/utils/utis'
import { mapGetters } from 'vuex'
import { apiLogout } from '@/API/user'
export default {
    name: 'Setting',
    components: {
        [NavBar.name]: NavBar
    },
    data() {
        return {
            version: '1.0.0',
            images: {
                arrow: require('@/assets/image/me/arrow2.png')
            },
            itemName: process.env.VUE_APP_ITEM_NAME,
            isShelves: process.env.VUE_APP_PUT_ON_SHELVES,
            navData: [
                {
                    name: this.$t('登录密码'),
                    path: '/LoginPasswordReset'
                },
                {
                    name: this.$t('资金密码'),
                    tips: '',
                    path: '/FundPasswordSettings'
                },
                // {
                //   name: this.$t('手机绑定'),
                //   tips: '',
                //   path: '/BindPhone'
                // },
                // {
                //   name: this.$t('邮箱绑定'),
                //   tips: '',
                //   path: '/BindEmail'
                // },
                {
                    name: this.$t('收货地址'),
                    path: '/AddressList',
                },
                // {
                //     name: this.$t('账号注销'),
                //     path: '/account/cancellation',
                // },
            ]
        }
    },
    computed: {
        ...mapGetters({
            userInfo: 'userInfo'
        })
    },
    created() {
        // this.version = process.env.VUE_APP_VERSION
        if (!isLogin()) {
            this.$router.push('/')
        } else {
            this.navData[1].tips = this.userInfo.safeword ? '' : this.$t('未设置')
            this.navData[1].path = this.userInfo.safeword ? '/FundPasswordReset' : '/FundPasswordSettings'

            //   this.navData[2].tips = this.userInfo.phoneverif ? '' : this.$t('未绑定')
            //   this.navData[2].path = this.userInfo.phoneverif ? '/BindPhoneBound' : '/BindPhone'
            //   this.navData[3].tips = this.userInfo.emailverif ? '' : this.$t('未绑定')
            //   this.navData[3].path = this.userInfo.emailverif ? '/BindEmailBound' : '/BindEmail'
        }
        if (['Argos', 'ArgosShop', 'Inchoi', 'EShop'].includes(this.itemName) || this.isShelves) {
            this.navData.push({
                name: this.$t('账号注销'),
                path: '/account/cancellation',
            })
        }
    },
    methods: {
        onClickLeft() {

            this.$router.push({ path: '/me', dir: 'left' })
        },

        openWin(path) {
            console.log(`path ::->`, path);
            this.$router.push({
                path
            })
        },

        tuichu() {
            apiLogout({ token: localStorage.getItem('token') })
            this.$store.dispatch('logout')
            this.$router.push('/')
        }
    }
}
</script>

<style lang="scss" scoped>
.nav-content {
    transform: none !important;

    * {
        box-sizing: border-box;
    }

    >.item {
        width: 100%;
        height: 50px;
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 0 15px;
        margin-bottom: 1px;
        background-color: #fff;
        border-bottom: 1px solid #F5F5F7;

        >div {
            display: flex;
            align-items: center;

            &.name {
                flex: 1;

                >.icon {
                    height: 18px;
                    width: auto;
                    margin-right: 10px;
                }

                >p {
                    font-size: 14px;
                    color: #333;
                }
            }

            &.arrow {
                display: flex;
                align-items: center;

                >p {
                    font-size: 14px;
                    color: #999;
                    margin-right: 10px;
                }

                >img {
                    width: 4px;
                    height: auto;
                }
            }
        }
    }
}

.tuichu {
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

.version {
    font-size: 12px;
    color: #cccccc;
    display: flex;
    justify-content: center;
    position: fixed;
    bottom: 12px;
    left: 50%;
    transform: translateX(-50%);
}
</style>
