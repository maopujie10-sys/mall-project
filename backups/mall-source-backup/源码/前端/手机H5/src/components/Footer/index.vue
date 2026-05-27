<template>
    <div>
        <div v-if="isShelves" class="footer">
            <div class="top">
                <img :src="logo" alt="" :style="itemData.logoHeight && { height: itemData.logoHeight + 'px' }" class="logo">
                <div class="email">
                    <span>{{ this.$t('获得您更多的优惠券') }}</span>
                    <input v-model.trim="email" :placeholder="this.$t('您的电子邮箱')" :maxlength="50" />
                    <button @click="subscription">{{ this.$t('订阅') }}</button>
                </div>
                <ul>
                    <li v-for="item in textList" :key="item.id" :class="{'en_li': isEn, 'de_li': isDe, 'fr_li': isFr, 'ms_li': isMs,'pt_li': isPt,'es_li': isEs, 'af_li': isAf,'ru_li': isRu,'tr_li': isTr,'it_li': isIt,'el_li': isEl,'ja_li': isJa, 'ph_li': isPh, 'ru_li': isVi, 'ru_li': isId}">
                    <div class="title">{{ item.title }}</div>
                    <div class="text" v-for="sub in item.subset" :key="sub.id" @click="handleJump(sub)">
                        {{ sub.text }}
                    </div>
                    </li>
                </ul>
            </div>
            <!-- 支付方式 -->
            <div class="mid">
                <div class="title">{{ this.$t('支付方式') }}</div>
                <ul>
                    <li v-for="(item, index) of paymentList" :key="index" @click="handleJump(item)">
                        <img :src="item?.icon" alt="">
                        <span>{{ item?.name }}</span>
                    </li>
                </ul>
            </div>
            <!-- Argos -->
            <div class="argos">
                <div class="title">{{ name == 'SM-wholesaleShop' ? 'SM-wholesale Shop' : name }}</div>
                <div :class="['text', isCn && 'cn_text']" v-if="name !== 'TikTokMall'">
                    {{ introduce }}
                </div>
                <div :class="['text', isCn && 'cn_text']" v-else>
                    {{ $t('TikTok Mall是全球短视频社交平台TikTok与亚洲最大的批发贸易公司Alibaba合作成立的，面向全球的电子商务平台，并在全球拥有三大自营智能仓库分别位于加拿大多伦多、美国洛杉矶及日本千叶。App内在售商品包含来自日本、韩国、中国等亚洲人气商品，目前总数已超过50,000款，并在持续快速增长中。') }}
                </div>
                <div class="bank_card" v-if="!['Inchoi', 'Tongda', 'FamilyMart','Hive', 'GreenMall', 'SM-wholesaleShop', 'INT Overstock', 'TikTok-Wholesale'].includes(name)">
                    <img v-if="name != 'Shop2u'" src="@/assets/image/footer/ka.png" alt="" />
                    <img v-else src="@/assets/image/footer/ka-Shop2u.png" alt="" />
                </div>
                <div :class="['images', name === 'Tongda' && 'amazon', name]" v-if="!['Hive', 'TikTok-Wholesale', 'GreenMall', 'INT Overstock'].includes(name)">
                    <img v-for="(item, k) of argosImages" :key="k" :src="item.logo" v-show="item?.logo" alt="" @click="handleJump(item, name === 'Shop2u')">
                </div>
            </div>
            <!-- 版权信息 -->
            <div class="copyright" v-if="name !== 'INT Overstock'">
                <span v-if="!isEn">© {{ name }} {{ this.$t('有限公司2023 版权所有') }}</span>
                <span v-if="isEn">Copyright {{ name }} {{ this.$t('有限公司2023 版权所有') }}</span>
                <template v-if="name !== 'TikTokMall'">
                    <span v-if="isCn">
                        {{ name }}
                        {{ this.$t('Limited 作为信贷经纪人 (713206) 获得金融行为监管局的授权和监管，并专门与贷方 Home Retail Group Card Services Limited 合作，以') }}
                        {{ name }}
                        {{ this.$t('Financial Services 的身份进行交易，') }}
                        {{ name }}
                        {{ this.$t('Financial Services 获得金融行为监管局的授权和监管以提供信贷(716148)。Home Retail Group Card Services Limited 注册于英国 (04007072)，地址为 Avebury: 489-499 Avebury Boulevard: Milton Keynes: United Kingdom。MK9 2NW。') }}
                    </span>
                    <span v-else>
                        {{ name }}
                        {{ this.$t('Limited 作为信贷经纪人 (713206) 获得金融行为监管局的授权和监管，并专门与贷方 Home Retail Group Card Services Limited 合作，以') }}
                        {{ name }}
                        {{ this.$t('Financial Services 的身份进行交易，') }}
                    </span>
                </template>
            </div>
            <div class="copyright" v-if="name === 'INT Overstock'">
                <span>
                    © Copyright 2023, overstock8.me®, Inc.799 Coliseum Way Midvale, UT 84047 | 1-840-800-1088
                </span>
            </div>
            <!-- dialog -->
            <van-dialog v-model="dialogShow" :title="$t('联系我们')">
                <div class="dialog_message" v-if="type == 'popover'">
                    <div v-if="itemData?.phone"><span>{{ $t('企业电话') }}:</span> <span>{{ itemData?.phone }}</span></div>
                    <div v-if="itemData?.mail"><span>{{ $t('企业邮箱') }}:</span> <span>{{ itemData?.mail }}</span></div>
                    <div v-if="itemData?.mail2"><span>{{ $t('企业邮箱') }}2:</span> <span>{{ itemData?.mail2 }}</span></div>
                    <div v-if="itemData?.telegram"><span>Telegram:</span> <span>{{ itemData?.telegram }}</span></div>
                    <div v-if="itemData?.line"><span>Line:</span> <span>{{ itemData?.line }}</span></div>
                    <div v-if="itemData?.whatsApp"><span>WhatsApp:</span> <span>{{ itemData?.whatsApp }}</span></div>
                    <div v-if="!itemData?.mail"><span>{{ $t('企业邮箱') }}:</span> <span>{{ name }}@{{ name }}.me</span></div>
                </div>
                <div class="dialog_message" v-if="type == 'phone'">
                    <span>{{ $t('企业电话') }}: {{ itemData?.phone }}</span>
                </div>
            </van-dialog>
        </div>
        <div style="height:50px" v-else></div>
    </div>
</template>
<script>
import { Field, Dialog } from 'vant';
import { argosImages } from './data'
import { getStorage, isLogin } from '@/utils/utis'
import { apiSubscription } from '@/API/common'
import { removeStorage } from '@/utils/utis'
export default {
    components: {
        [Field.name]: Field,
        [Dialog.Component.name]: Dialog.Component,
    },
    data() {
        return {
            removeStorage,
            isLogin,
            argosImages,
            isShelves: !process.env.VUE_APP_PUT_ON_SHELVES,
            itemData: this.$store.state.multiItem[process.env.VUE_APP_ITEM_NAME],
            email: '',
            dialogShow: false,
            type: '',
            name: process.env.VUE_APP_ITEM_NAME,
            textList: [
                {
                    title: this.$t('客户服务'),
                    subset: [
                        {
                            path: this.$store.state.multiItem[process.env.VUE_APP_ITEM_NAME].customer_service ?
                            this.$store.state.multiItem[process.env.VUE_APP_ITEM_NAME].customer_service : '/customerServiceIndex?path=customerService',
                            text: this.$t('在线客服')
                        },
                        {
                            path: 'popover',
                            // text: this.$t('联系我们')
                        },
                        // {
                        //     path: '',
                        //     text: this.$t('合作供应商')
                        // },
                        
                    ]
                },
                {
                    title: this.$t('退货和换货'),
                    subset: [
                        {
                            path: '/promote/#/privacyPolicy',
                            text: this.$t('隐私政策')
                        },
                        {
                            path: '/promote/#/returnPolicy',
                            text: this.$t('退货政策')
                        },
                        {
                            path: '/promote/#/Delivery',
                            text: this.$t('送货及取货')
                        },
                        {
                            path: '/promote/#/shippingPolicy',
                            text: this.$t('卖家政策')
                        }
                    ]
                },
                {
                    title: this.$t('用户中心'),
                    subset: [
                        {
                            path: '/register',
                            text: this.$t('用户注册')
                        },
                        {
                            path: '/order',
                            text: this.$t('订单查询')
                        },
                        {
                            path: '/collectGoods',
                            text: this.$t('商品收藏')
                        },
                        {
                            path: '/me',
                            text: this.$t('我的钱包')
                        }
                    ]
                },
                {
                    title: this.$t('关于我们'),
                    subset: [
                        {
                            path: 'https://www.about.sainsburys.co.uk/brands-that-deliver/argos',
                            text: this.$t('关于我们')
                        },
                        {
                            path: 'https://sainsburys.jobs/',
                            text: this.$t('招贤纳士')
                        },
                        {
                            path: 'https://www.about.sainsburys.co.uk/news/media-enquiries',
                            text: this.$t('新闻资讯')
                        },
                        {
                            path: 'https://www.about.sainsburys.co.uk/sustainability/plan-for-better/our-stories/2017/standing-up-to-modern-slavery',
                            text: this.$t('现代奴隶声明')
                        }
                    ]
                },
            ],
            paymentList: [
                {
                    path: 'https://www.binance.com/',
                    icon: require('@/assets/image/footer/1.png'),
                    name: 'Binance'
                },
                {
                    path: 'https://www.huobi.com/',
                    icon: require('@/assets/image/footer/2.png'),
                    name: 'Huobi'
                },
                {
                    path: 'https://www.okx.com/',
                    icon: require('@/assets/image/footer/3.png'),
                    name: 'OKX'
                },
                {
                    path: 'https://www.kraken.com/',
                    icon: require('@/assets/image/footer/4.png'),
                    name: 'Kraken'
                },
                {
                    path: 'https://www.coinbase.com/',
                    icon: require('@/assets/image/footer/5.png'),
                    name: 'coinbase'
                },
                {
                    path: 'https://metamask.io/',
                    icon: require('@/assets/image/footer/6.png'),
                    name: 'MetaMask'
                },
                {
                    path: 'https://www.kucoin.com/',
                    icon: require('@/assets/image/footer/7.png'),
                    name: 'KuCoin'
                },
                {
                    path: 'https://www.bitfinex.com/',
                    icon: require('@/assets/image/footer/8.png'),
                    name: 'Bitfinex'
                },
            ],
            argosImages,
            isCn: getStorage('lang') == 'cn',
            isEn: getStorage('lang') == 'en',
            isDe: getStorage('lang') == 'de',
            isFr: getStorage('lang') == 'fr',
            isMs: getStorage('lang') == 'ms',
            isMs: getStorage('lang') == 'ms',
            isPt: getStorage('lang') == 'pt',
            isEs: getStorage('lang') == 'es',
            isAf: getStorage('lang') == 'af',
            isRu: getStorage('lang') == 'ru',
            isTr: getStorage('lang') == 'tr',
            isIt: getStorage('lang') == 'it',
            isEl: getStorage('lang') == 'el',
            isJa: getStorage('lang') == 'ja',
            isPh: getStorage('lang') == 'ph',
            isVi: getStorage('lang') == 'vi',
            isId: getStorage('lang') == 'id',
        }
    },
    computed: {
        introduce() {
            let { name } = this
            name = name == 'SM-wholesaleShop' ? 'SM-wholesale Shop' : name
            const text = '全球站的用户来全球103个国家，使用USDT/ETH/BTC进行 结算。USDT/ETH/BTC是一种无国界的交易方式，可以在全球范 围内实现即时低成本交易，无需等待，没有国际费用。'
            if(name === 'INT Overstock') {
                const OverstockText = '全球站的用户来全球103个国家，使用USDT/USDC/ETH/BTC进行结算。USDT/USDC/ETH/BTC是一种无国界的交易方式，可以在全球范围内实现即时低成本交易，无需等待，没有国际费用。'
                return `Overstock ${this.$t(OverstockText).replace('103', '180')} `
            }
            if(name === 'GreenMall') {
                return `${name} ${this.$t(text).replace('103', '112')} `
            }
            if(name === 'Argos') {
            const argosText = '全球站的用户来全球103个国家，使用USDT/USDC/ETH/BTC进行结算。USDT/USDC/ETH/BTC是一种无国界的交易方式，可以在全球范围内实现即时低成本交易，无需等待，没有国际费用。'
                return `${name} ${this.$t(argosText)} `
            }
            return `${name} ${this.$t(text)} `
       },
        logo() {
            if(['TikTokMall', 'Shop2u', 'Laz', 'Iceland', 'INT Overstock', 'TikTok-Wholesale', 'AntMall', 'SM-wholesaleShop'].includes(process.env.VUE_APP_ITEM_NAME)) {
                return require(`@/assets/${process.env.VUE_APP_ITEM_NAME}/logo2.${this.$store.state.multiItem[process.env.VUE_APP_ITEM_NAME].suffix}`)
            } else {
                return require(`@/assets/${process.env.VUE_APP_ITEM_NAME}/logo.${this.$store.state.multiItem[process.env.VUE_APP_ITEM_NAME].suffix}`)
            }
            
        },
    },
    created() {
        if(this.name === 'INT Overstock') {
            // this.textList[3].subset[0].path = 'https://www.bedbathandbeyond.com/about'
            this.textList[3].subset[0].path = 'https://overstock8.me/gw/#/about'
            this.textList[3].subset[1] = {
                path: 'https://overstock8.me/gw/#/',
                text: this.$t('职业机会')
            }
            this.textList[3].subset[2] = {}
            this.textList[3].subset[3] = {}
        }
        if(this.name === 'Tongda') {
            this.argosImages[0] = {
                logo: require('@/assets/Tongda/amazon2.png'),
                path: 'https://www.amazon.com/'
            }
        }
        if(this.name === 'SM-wholesaleShop') {
            this.argosImages[0] = {
                logo: require('@/assets/SM-wholesaleShop/justeat.png'),
                path: 'https://www.justeattakeaway.com/'
            }
            this.argosImages[1] = {
                logo: require('@/assets/SM-wholesaleShop/bdo.png'),
                path: 'https://www.bdo.com/'
            }
            this.argosImages[2] = {}
            this.argosImages[3] = {}
            this.argosImages[5] = {
                path: 'https://www.zellepay.com/',
                logo: require('@/assets/image/footer/logo8.png')
               
            }
            this.argosImages[6] = {
                path: 'https://crypto.com/',
                logo: require('@/assets/image/footer/logo6.png')
            }
            this.argosImages[7] = {
                path: 'https://www.sc.com/en/',
                logo: require('@/assets/image/footer/logo7.png')
            }
            this.textList[3].subset[0].path = 'https://www.smsupermalls.com/about-us/'
        }
        if(this.name === 'FamilyShop') {
            this.argosImages[5] = {
                path: 'https://crypto.com/',
                logo: require('@/assets/image/footer/logo6.png')
            }
        }
        if(['FamilyMart','Hive', 'TikTok-Wholesale'].includes(this.name)) {
            this.argosImages[0] = {}
        }
        if(this.name == 'TikTok-Wholesale') {
            this.textList[3].subset[0].path = '/promote/#/TikTok-about'
        }
        if(this.name === 'GreenMall') {
            this.textList[3] = {} 
        }
        if(this.name == 'Argos') {
            this.paymentList = this.paymentList.map(item => {
                if (item.name === 'MetaMask') {
                    item = {
                        path: 'https://crypto.com/',
                        icon: require('@/assets/image/footer/11.png'),
                        name: 'Crypto'
                    }
                } else if (item.name === 'KuCoin') {
                    item = {
                        path: 'http://www.bitopro.com/',
                        icon: require('@/assets/image/footer/9.png'),
                        name: 'Bitopro'
                    }
                } else if (item.name === 'Bitfinex') {
                    item = {
                        path: 'https://max.maicoin.com/',
                        icon: require('@/assets/image/footer/10.png'),
                        name: 'Max'
                    }
                }
                return item
            })
        }
        if(['Hive', 'TikTok-Wholesale'].includes(this.name)) {
            this.paymentList = this.paymentList.map(item => {
                if(item.name === 'MetaMask') {
                    item = {
                        path: 'https://www.bitoex.com/',
                        icon: require('@/assets/image/footer/9.png'),
                        name: 'Bitoex'
                    }
                } else if (item.name === 'Bitfinex') {
                    item = {
                        path: 'https://max.maicoin.com/',
                        icon: require('@/assets/image/footer/10.png'),
                        name: 'Max'
                    }
                }
                return item
            })
            this.textList[3].subset = [{
                path: '/promote/#/Hive-about',
                text: this.$t('关于我们')
            }]
        }
        if(this.name == 'Shop2u') {
            this.textList[3].subset[0].path = 'https://www.asiaone.com/business/shop2u-platform-officially-entered-southeast-asian-market-will-create-nearly-2-million'
            this.textList[3].subset[1].text = this.$t('企业证明')
            this.textList[3].subset[1].path = '/promote/#/enterprise-prove'
            this.textList[3].subset[2].path = 'https://finance.yahoo.com/news/british-chambers-commerce-visited-shop2u-170000654.html?fr=sycsrp_catchall'
            this.textList[3].subset[3].text = 'Youtube'
            this.textList[3].subset[3].path = 'https://www.youtube.com/@shop2u'
            this.argosImages[0].logo = require('@/assets/image/footer/logo-shop2u.png')
        }
        if(this.name == 'FamilyMart') {
            this.textList[3].subset[0].path = 'https://familymart.vip/'
        }
        if (!window.plus) {
                if(this.name == 'Shop2u') {
                    this.textList[0].subset.push({
                        path: 'https://play.google.com/store/apps/details?id=com.commerce.app',
                        text: this.$t('安卓下载')
                    })
                    this.textList[0].subset.push({
                        path: 'https://apps.apple.com/my/app/shop2u/id6448880380',
                        text: this.$t('苹果下载')
                    })
                    return
                }
                if(!['Hive', 'TikTok-Wholesale'].includes(this.name)) {
                    if(this.name == 'INT Overstock') {
                            this.textList[0].subset.push({
                            path: location.origin + '/app.html',
                            text: this.$t('应用程序下载')
                        })
                    } else {
                        this.textList[0].subset.push({
                        path: location.origin + '/app.html',
                        // text: this.$t('APP下载(买家端)')
                    })
                    this.textList[0].subset.push({
                        path: location.origin + '/app.html',
                        // text: this.$t('APP下载(卖家端)')
                    })
                    }
                    
                } 
        }
        if(this.name === 'MetaShop') {
            this.textList[3].subset[0].path = '/promote/#/aboutUs'
        }
    },
    methods: {

        handleJump(item, noJump) {
            if(noJump) return
            const { path, name, text } = item
            if (!path) return

            if (path == 'phone') {
                if (!this.itemData?.phone) return
            }
            const types = ['popover', 'phone']
            if (types.includes(path)) {
                this.type = path
                this.dialogShow = true
                return
            }
            if (path.indexOf('http') != -1) {
                if(window.plus) {
                    plus.runtime.openURL(path)
                    return
                } else {
                    window.open(path)
                }
            } else if (path.indexOf('/#/') != -1) {
                let query = {title: name || text }
                if(window.plus) {
                    query.url = `${this.itemData.app_url}${path}?lang=${getStorage('lang') || 'en'}`
                } else {
                    query.url = `${window.origin}${path}?lang=${getStorage('lang') || 'en'}`
                }
                this.$router.push({
                    path: "/iframe",
                    query
                });
            } else {
                if (path == '/register') {
                    if (this.isLogin()) {
                        Dialog.confirm({
                            title: this.$t("您已登录"),
                            message: this.$t("是否跳转到注册页面"),
                            confirmButtonText: this.$t("确认"),
                            cancelButtonText: this.$t("取消"),
                        }).then(() => {
                            this.removeStorage('token')
                            this.$router.push("/register");
                        });
                    } else {
                        this.$router.push("/register");
                    }
                    return
                }
                const arr = ['/order', '/collectGoods']
                if (arr.includes(path)) {
                    if (!this.isLogin()) {
                        this.$notifyWarn(this.$t("请先登录"));
                        this.$router.push("/login");
                    } else {
                        this.$router.push(path);
                    }
                    return
                }
                if (this.$route.path != path) {
                    this.$router.push(path)
                } else {
                    scrollTo(0, 0);
                }
            }

        },
        async subscription() {
            if(!this.isValidEmail(this.email)) return this.$notify(this.$t('请输入正确的邮箱地址'))
            await apiSubscription({ email: this.email })
            this.$notify(this.$t('订阅成功'), 'success')
        },
        isValidEmail(email) {
            var emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
            return emailRegex.test(email);
        }
    }
}
</script>
<style lang="scss" scoped>
.dialog_message {
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    min-height: 100px;
    box-sizing: border-box;
    div {
        width: 250px;
        padding: 0 50px;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    span {
        // display: block;
        // flex: 0 0 50%;
        font-size: 14px;
        color: #3f3f3f;
        line-height: 20px;
        &:nth-child(1) {
            text-align: end;
            margin-right: 10px;
            flex: 0 0 30%;
        }
        &:nth-child(2) {
            text-align: start;
        }
    }
}

.footer {
    width: 100%;
    background: #212121;
    overflow: hidden;
    .top {
        padding: 28px 38px 38px 28px;


        .logo {
            // width: 118px;
            width: auto;
            height: 35px;
        }

        .email {
            margin-top: 0px;

            span {
                display: block;
                color: var(--main-footer-color);
                font-size: 12px;
            }

            input {
                margin-top: 12px;
                width: 288px;
                height: 44px;
                border-radius: 4px;
                padding-left: 10px;
                border: none;
                outline: none;
                font-size: 12px;

                &::placeholder {
                    color: #9E9E9E;
                }
            }

            button {
                margin-top: 39px;
                width: 156px;
                height: 42px;
                border: 1px solid var(--main-footer-color) !important;
                border-radius: 4px;
                font-size: 12px;
                color: var(--main-footer-color);
                background: transparent;
            }
        }

        ul {
            margin-top: 29px;
            display: flex;
            flex-wrap: wrap;
            justify-content: space-between;

            li {
                flex: 0 0 70%;
                color: #fff;
                display: flex;
                flex-direction: column;
                align-items: flex-start;
                &.tr_li,
                &.it_li,
                &.af_li,
                &.ru_li,
                &.es_li,
                &.pt_li,
                &.ms_li,
                &.fr_li,
                &.de_li,
                &.en_li {
                    flex: 0 0 55%;

                    &:nth-child(2n) {
                        align-items: flex-end;
                        flex: 0 0 45%;
                    }
                }
                &.de_li {
                    flex: 0 0 50%;
                }
                &.fr_li {
                    flex: 0 0 52%;
                }
                &.ms_li {
                    flex: 0 0 50%;
                }
                &.pt_li {
                    flex: 0 0 40%;
                }
                &.es_li {
                    flex: 0 0 40%;
                }
                &.ru_li {
                    flex: 0 0 50%;
                }
                &.af_li {
                    flex: 0 0 50%;
                }
                &.tr_li {
                    flex: 0 0 42%;
                }
                &.it_li {
                    flex: 0 0 45%;
                }
                &.el_li {
                    flex: 0 0 45%;
                    &:nth-child(2n) {
                        align-items: flex-end;
                        flex: 0 0 50%;
                    }
                }
                &.ja_li {
                    flex: 0 0 50%;
                    &:nth-child(2n) {
                        align-items: flex-end;
                        flex: 0 0 48%;
                    }
                }
                &.ph_li {
                    flex: 0 0 50%;
                    &:nth-child(2n) {
                        align-items: flex-end;
                        flex: 0 0 48%;
                    }
                }
                div {
                    width: 100%;
                    text-align: start;

                    &.title {
                        color: var(--main-footer-color);
                        font-weight: 700;
                        font-size: 16px;
                        // margin-bottom: 19px;
                        height: 45px;
                        word-wrap:break-word;
                    }

                    &.text {
                        // margin-bottom: 23px;
                        height: 40px;
                        font-size: 12px;
                        transform: translateX(4px);
                    }
                }

                &:nth-child(2n) {
                    align-items: flex-end;
                    flex: 0 0 30%;
                }

                &:nth-child(3),
                &:nth-child(4) {
                    margin-top: 23px;
                }
            }
        }
    }

    .mid {
        padding: 13px 39px 31px 27px;
        position: relative;

        &::after {
            content: '';
            display: block;
            position: absolute;
            top: 0;
            left: 27px;
            width: 95%;
            height: 1px;
            background: #3f3f3f;
        }

        &::before {
            content: '';
            display: block;
            position: absolute;
            bottom: 0;
            left: 27px;
            width: 95%;
            height: 1px;
            background: #3f3f3f;
        }

        .title {
            color: #fff;
            font-size: 12px;
            text-align: center;
        }

        ul {
            margin-top: 29px;
            display: flex;
            flex-wrap: wrap;
            justify-content: center;
            align-items: center;
            padding: 0 20px;

            li {
                flex: 0 0 25%;
                display: flex;
                flex-direction: column;
                justify-content: center;
                align-items: center;
                margin-bottom: 15px;

                img {
                    width: 32px;
                    height: 32px;
                    border-radius: 50%;
                }

                span {
                    margin-top: 6px;
                    color: #ABABAB;
                    font-size: 10px;
                }
            }
        }
    }

    .argos {
        padding: 23px 16px 36px 16px;
        position: relative;

        &::after {
            content: '';
            display: block;
            position: absolute;
            bottom: 0;
            left: 50%;
            transform: translateX(-50%);
            width: 90%;
            height: 1px;
            background: #3f3f3f;
            box-sizing: border-box;
        }

        .title {
            color: #fff;
            font-size: 12px;
            text-align: center;
        }

        .text {
            padding-left: 16px;
            // width: 318px;
            margin-top: 10px;
            font-size: 12px;
            line-height: 17px;
            color: #FFFFFF;
            // word-break:break-all;
            // text-align: justify;
        }
        .cn_text {
            word-break:break-all;
            text-align: justify;
        }
        .bank_card {
            margin-top: 29px;
            display: flex;
            justify-content: center;
            align-items: center;

            img {
                width: 237px;
                height: 152px;
            }
        }

        .images {
            margin-top: 48px;
            min-height: 30px;
            display: flex;
            flex-wrap: wrap;
            justify-content: center;
            align-items: center;
            &.SM-wholesaleShop {
                img {
                    &:nth-child(1) {
                        width: auto !important;
                        height: 16px !important;
                        transform: translateY(2px);
                    }
                    &:nth-child(2) {
                        width: 49.6px;
                        height: 10.4px;
                        transform: translateY(4px);
                    }
                    &:nth-child(3) {
                        width: 49.6px;
                        height: 10.4px;
                    }
                    &:nth-child(6) {
                        width: 60px;
                        height: auto !important;
                        margin-left: 20px;
                    }
                    &:nth-child(7) {
                        width: 100px;
                        height: auto !important;
                        
                    }
                    &:nth-child(7) {
                        margin-left: 0;
                    }
                    &:nth-child(8) {
                        width: 52px;
                        height: auto;
                        margin-bottom: 0;
                    }
                }
            }
            &.Shop2u, &.Tongda {
                img {
                    &:nth-child(1) {
                        width: auto !important;
                        height: 14px !important;
                    }
                    &:nth-child(2) {
                        width: 49.6px;
                        height: 10.4px;
                    }
                    &:nth-child(4) {
                        width: 82.4px;
                        height: 15.2px;
                    }
                    &:nth-child(5) {
                        width: 26.4px;
                        height: 22.4px;
                    }
                    &:nth-child(8) {
                        width: 52px;
                        height: auto;
                        margin-bottom: 0;
                    }
                }
            }
            
            img {
                margin-bottom: 10px;
                margin-left: 20px;
                &:nth-child(1) {
                    margin-left: 0;
                    width: 34px;
                    height: 29px;
                }
                &:nth-child(2) {
                    width: 62px;
                    height: 13px;
                }

                &:nth-child(3) {
                    width: 22px;
                    height: 18px;
                }

                &:nth-child(4) {
                    width: 103px;
                    height: 19px;
                }

                &:nth-child(5) {
                    width: 33px;
                    height: 28px;
                }
                &:nth-child(6) {
                    margin: 0;
                    width: 159px;
                }
                &:nth-child(7) {
                    margin: 0;
                    width: 80px;
                    margin-left: 30px;
                }
            }
            &.amazon {
                img {
                    &:nth-child(1) {
                        width: 48.5px;
                        height: 15px;
                        transform: translateY(4px);
                    }
                }
            }
        }
    }

    .copyright {
        padding: 15px 16px 100px 16px;

        span {
            color: #6B6B6B;
            font-size: 10px;
            line-height: 16px;
            display: block;
            // text-align: justify;
            &:nth-child(1) {
                text-align: center;
                margin-bottom: 24px;
                font-size: 12px;
            }
        }
    }

    // :deep(.van-dialog__message) {
    //     text-align: inherit !important;
    // }
}
</style>