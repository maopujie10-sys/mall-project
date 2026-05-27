<template>
    <div class="loan_wrap">
        <van-nav-bar safe-area-inset-top :title="$t('贷款申请')" left-arrow @click-left="$router.replace('/me')" fixed
            ref="header">
        </van-nav-bar>
        <!-- 顶部图 -->
        <div class="top">
            <div :class="['text', !isCn && 'en_text']">
                <span>{{ $t('创业贷款 解决借钱的烦恼') }}</span>
                <span>{{ $t('提供创业贷款 资金周转服务') }}</span>
            </div>
            <div class="btns">
                <span :class="isCheckAvailability == 'false' && 'disabled'" @click="handleApply">{{ $t("在线申请") }}</span>
                <span @click="handleMine">{{ $t("我的贷款") }}</span>
            </div>
        </div>
        <!-- 贷款无忧 -->
        <div class="worry_free">
            <div class="main_title title">{{ $t('贷款无忧') }}</div>
            <ul>
                <li v-for="(item, index) of worryFreeData" :key="index" :class="!isCn && 'en_li'">
                    <!-- <img :src="item.icon" alt=""> -->
                    <van-icon class-prefix="icon" :name="item.iconName" />
                    <div class="name">{{ item.name }}</div>
                    <div class="desc">{{ item.desc }}</div>
                </li>
            </ul>
        </div>
        <!-- 关于我们 -->
        <div class="about">
            <div class="main_title title">{{ $t('关于我们') }}</div>
            <div class="content">
                <p>
                    {{ $t('我们致力于贷款金融服务，基于“客户至上”的经营理念，以解决客户资金周转问题为使命，公司从成立至今，已帮 助无数留客户解决资金周转问题。') }}
                </p>
                <p>
                    {{ $t('额度:100,000至30,000,000，利息低 还款方式灵活，无任何前期费用，线上放款，不打审核电话，信息保密，') }}
                </p>
                <p>{{ $t('当天放款。') }}</p>
                <p>
                    {{ $t('不想向同学朋友开口借钱，请找我们。') }}
                </p>
            </div>
            <div :class="['ad', !isCn && 'en_ad']">
                <!-- <p v-if="!isCn"> -->
                <!-- <span>{{ $t('致力于创业者贷款服务') }}</span> -->
                <!-- </p> -->
                <p><span>{{ $t('致力于创业者贷款服务') }}</span></p>
                <p><span>{{ $t('解决您的资金困扰') }}</span></p>
            </div>
        </div>
        <!-- 合作伙伴 - 在线借贷平台 -->
        <div class="partner">
            <div class="main_title">{{ $t('合作伙伴 - 在线借贷平台') }}</div>
            <ul>
                <li v-for="(item, index) of partnerIcon" :key="index" @click="handleJump(item.path)">
                    <img :src="item.icon" alt="">
                </li>
            </ul>
        </div>
        <Footer />
    </div>
</template>

<script>
import { mapMutations } from "vuex";
import Footer from '@/components/Footer'
import { getStorage } from '@/utils/utis'
import { apiCheckAvailability } from '@/API/loan'
import { Toast, Icon } from 'vant'
import { isLogin } from "@/utils/utis";
export default {
    components: { Footer, [Toast.name]: Toast, [Icon.name]: Icon },
    data() {
        return {
            itemName: process.env.VUE_APP_ITEM_NAME,
            worryFreeData: [
                {
                    name: this.$t('灵活额度'),
                    desc: this.$t('100,000至30,000,000，额度灵活， 没有限制，最长贷款期限一年。'),
                    icon: require('@/assets/image/locn/worry_free1.png'),
                    iconName: 'meiyuan9'
                },
                {
                    name: this.$t('急速放款'),
                    desc: this.$t('最快一小时通过审核，审核通过 立马下款。'),
                    icon: require('@/assets/image/locn/worry_free2.png'),
                    iconName: 'huojianjiasu'
                },
                {
                    name: this.$t('安全无忧'),
                    desc: this.$t('无抵押贷款，无需押金，不打回访电话， 这本就是一件私密的事。'),
                    icon: require('@/assets/image/locn/worry_free3.png'),
                    iconName: 'dunpai'
                }
            ],
            isCheckAvailability: 'false',
            partnerIcon: [],
            isEn: getStorage('lang') == 'en',
            isCn: getStorage('lang') == 'cn'
        }
    },
    async created() {

        if (['SM-wholesaleShop', 'FamilyShop'].includes(this.itemName)) {
            const paths = [
                'https://www.jpmorganchase.com/',
                'https://www.bankofamerica.com/',
                'https://www.wellsfargo.com/',
                'https://www.citi.com/',
                'https://www.goldmansachs.com/',
                'https://www.hsbc.com',
                'https://www.ubs.com',
                'https://www.credit-suisse.com',
                'https://www.barclays.co.uk/',
                'https://www.sc.com/en/',
                'https://10bestpersonalloans.com/go/pmax-usa-eng-d-g.html#o6',
                'https://www.mastercard.com/global/en.html'
            ]
            for (let i = 0; i < 12; i++) {
                this.partnerIcon.push({
                    icon: require(`@/assets/image/locn/partner/s${i + 1}.png`),
                    path: paths[i]
                })
            }
        } else {
            const paths = [
                'https://www.cimbclicks.com.my',
                'https://www.cimb.com.my',
                'https://www.rhbgroup.com',
                'https://www.loanstreet.sg/',
                'https://www.dbs.com.sg/',
                'https://www.graceloanadvance.com',
                'https://hk.lendela.com',
                'https://epaycash.hk',
                'https://www.hangseng.com/',
                'https://www.hsbc.com.hk',
            ]
            for (let i = 0; i < 10; i++) {
                this.partnerIcon.push({
                    icon: require(`@/assets/image/locn/partner/${i + 1}.jpg`),
                    path: paths[i]
                })
            }
        }

        const lang = this.$route.query?.lang
        const token = this.$route.query?.token
        token && localStorage.setItem('token', token)
        token && await this.$store.dispatch('getUserInfo')
        if (lang) {
            if (lang != localStorage.getItem('lang')) {
                this.$i18n.locale = lang;
                this.setLanguage(lang);
            }
        }
        if (isLogin()) {
            this.requireCheckAvailability()
        }
    },
    methods: {
        ...mapMutations(["setLanguage"]),
        async requireCheckAvailability() {
            this.isCheckAvailability = await apiCheckAvailability()
        },
        handleJump(path) {
            if (window.plus) {
                plus.runtime.openURL(path)
                return
            } else {
                window.open(path)
            }
        },
        handleApply() {
            if (!isLogin()) {
                this.$notifyWarn(this.$t("请先登录"));
                return this.$router.push('/login')
            }
            if (this.isCheckAvailability == 'true') this.$router.push('/loan/apply')
        },
        handleMine() {
            if (!isLogin()) {
                this.$notifyWarn(this.$t("请先登录"));
                return this.$router.push('/login')
            }
            this.$router.push('/loan/my')
        }
    }
}
</script>

<style lang="scss" scoped>
.loan_wrap {
    width: 100%;
    height: 100%;
    font-size: 14px;
    padding-top: 44px;

    .top {
        height: 251px;
        background: url(@/assets/image/locn/topbg.png) no-repeat center / 100% 100%;
        position: relative;

        .text {
            position: absolute;
            top: 74px;
            left: 0;
            width: 100%;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            text-align: center;

            span {
                &:nth-child(1) {
                    font-weight: 600;
                    font-size: 24px;
                    color: var(--main-color);
                }

                &:nth-child(2) {
                    font-size: 16px;
                    font-weight: 500;
                    color: #fff;
                }
            }

            &.en_text {
                top: 40px;

                span {
                    text-align: center;
                    transform: scale(.9);
                }
            }
        }

        .btns {
            width: 100%;
            position: absolute;
            bottom: 43px;
            left: 0;
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 0 32px;
            box-sizing: border-box;

            span {
                display: flex;
                justify-content: center;
                align-items: center;
                width: 139px;
                height: 37px;
                border: 1px solid var(--main-color);
                color: var(--main-color);
                font-size: 16px;
                font-weight: 500;
                border-radius: 4px;
                white-space: nowrap;
                padding: 0 10px;
                &:nth-child(1) {
                    background: var(--main-color);
                    color: #fff;

                }

                &:nth-child(2) {
                    margin-left: 37px;
                }

                &.disabled {
                    opacity: .5;
                }
            }
        }
    }

    .worry_free {
        margin-top: 24px;

        .title {
            color: #333;
        }

        ul {
            margin-top: 44px;
            padding: 0 49px 0 50px;

            li {
                width: 100%;
                min-height: 237px;
                border: 1px solid #ededed;
                margin-bottom: 17px;
                border-radius: 8px;
                display: flex;
                flex-direction: column;
                justify-content: center;
                align-items: center;

                &:last-child {
                    .icon {
                        font-size: 65px;
                    }
                }

                &.en_li {

                    .desc,
                    .name {
                        transform: translateY(-10px);
                    }
                }

                .icon {
                    font-size: 75px;
                }

                .name {
                    margin-top: 34px;
                    color: #333;
                    font-size: 16px;
                    font-weight: 600;
                }

                .desc {
                    margin-top: 20px;
                    font-size: 14px;
                    color: #777;
                    text-align: center;
                }

                &:nth-child(1) {
                    img {
                        width: 74.45px;
                        height: 74.45px;
                    }

                    .desc {
                        padding: 0 17px;
                    }
                }

                &:nth-child(2) {
                    img {
                        width: 93px;
                        height: 92px;
                    }

                    .desc {
                        padding: 0 40px;
                    }
                }

                &:nth-child(3) {
                    img {
                        width: 56px;
                        height: 63px;
                    }

                    .desc {
                        padding: 0 10px;
                    }
                }
            }
        }
    }

    .about {
        width: 100%;
        padding-bottom: 60px;
        background: #212121;
        padding-top: 36px;

        .title {
            color: #fff;
        }

        .content {
            margin-top: 25px;
            padding: 0 14px;

            p {
                font-weight: 500;
                font-size: 12px;
                line-height: 18px;
                color: #fff;
                // text-align: justify;

                &:last-child {
                    text-align: center;
                    margin-top: 10px;
                    margin-bottom: 30px;
                }
            }
        }

        .ad {
            position: relative;
            width: 100vw;
            height: 64px;
            transform: translateX(-10px);

            p {
                display: inline-flex;
                justify-content: center;
                align-items: center;
                width: 216px;
                height: 32px;
                background: url(@/assets/image/locn/c1.png) no-repeat center / 100% 100%;
                position: absolute;
                left: 30px;
                top: 0;
                color: #212121;
                white-space: nowrap;

                &:nth-child(2) {
                    background: url(@/assets/image/locn/c2.png) no-repeat center / 100% 100%;
                    top: auto;
                    left: auto;
                    right: 0;
                    bottom: 0;
                    color: var(--main-color);
                }
            }

            &.en_ad {
                span {
                    transform: scale(.77);
                }
            }
        }
    }

    .partner {
        margin-top: 34px;
        padding-bottom: 48px;

        ul {
            margin-top: 40px;
            display: flex;
            flex-wrap: wrap;
            justify-content: space-between;
            padding: 0 17px;

            li {
                width: 161px;
                height: 44px;
                margin-bottom: 24px;

                img {
                    width: 100%;
                    height: 100%;
                }
            }
        }
    }
}

.main_title {
    width: 100%;
    display: flex;
    justify-content: center;
    align-items: center;
    font-size: 20px;
    font-weight: 600;
    position: relative;
    color: #333;

    &::after {
        content: '';
        display: block;
        width: 57px;
        height: 2px;
        background: var(--main-color);
        position: absolute;
        bottom: -7px;
        left: 50%;
        transform: translateX(-50%);
    }
}
</style>