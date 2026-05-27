<template>
    <div class="CommodityDetails">
        <van-nav-bar safe-area-inset-top fixed :title="$t('详情')" left-arrow @click-left="onClickLeft">
            <div slot="title" class="tab-wrap">
                <!-- <div class="tab-item" @click="toTop(index)" :class="[tab_index === index ? 'active' : '']"
                    v-for="(item, index) in tab_nav_list" :key="index">
                    {{ item }}
                </div> -->
                <van-tabs v-model="tab_index" @change="handleTabsChange" :line-height="langIsAr ? 0 : '3px'">
                    <van-tab :title="item" v-for="(item, index) in tab_nav_list" :key="index" />
                </van-tabs>
            </div>
        </van-nav-bar>
        <div style="width: 100%; height: 46px" id="product"></div>
        <div class="banner-product">
            <van-swipe @change="handleChangeSwiper" :autoplay="swiperWaitTime" ref="swiperRef" style="direction: ltr;">
                <van-swipe-item class="swipe-item" v-for="(item, index) in imageList" :key="index">
                    <img :src="item" @click="ImagePreview({ images: imageList, startPosition: index })" class="img" />
                </van-swipe-item>
                <template #indicator>
                    <ul class="indicators indicator">
                        <li v-for="(item, index) in imageList" :key="index" :class="{ active: checkActive(index) }">
                        </li>
                    </ul>
                </template>
            </van-swipe>
        </div>
        <div class="product-info-wrap">
            <div class="product-name">
                {{ goods_info.name }}
            </div>
            <div class="price-box">
                <div class="product-price">
                    <span class="title">{{ $t("单价") }}</span>
                    <span class="money">${{
                        priceFormat(goods_info.discountPrice)
                        ? priceFormat(goods_info.discountPrice)
                        : priceFormat(goods_info.sellingPrice)
                    }}</span>
                    <!-- <span class="text">{{$t('价格')}}&nbsp;$56.12</span> -->
                </div>
                <div class="product-sellingPrice" v-if="originalPrice">
                    <span class="title">{{ $t("原价") }}</span>
                    <span class="money">${{ priceFormat(originalPrice) }}</span>
                </div>
                <div class="product-sold">
                    {{ $t("销量") }} {{ priceFormatInt(goods_info.soldNum) }}
                </div>
            </div>
            <div class="sku_box" v-if="goods_info?.canSelectAttributes?.goodAttrs.length">
                <div class="attributes_box">
                    <div class="attributes" v-for="(item, i) of goods_info?.canSelectAttributes?.goodAttrs" :key="i">
                        <div class="p_title" v-if="item?.attrName">{{ currentSkuTitle[i] }}</div>
                        <ul v-if="item?.attrName">
                            <li :class="[sub.attrValueId == activeAttrs[i] && 'active', sub?.icon && 'img_box', sub.disabled && 'disabled']"
                                @click="handleToggle(sub, i, sub.disabled)" v-for="(sub, j) of item.attrValues" :key="j">
                                <img v-if="sub?.icon" :src="sub.iconImg" alt="">
                                <span v-else>{{ sub.attrValueName }}</span>
                            </li>
                        </ul>
                    </div>
                </div>
            </div>
            <!-- <div class="product-norm">
                
            </div> -->
            <div class="product-line-item">
                <div class="left">{{ $t("发货") }}</div>
                <div class="right">
                    {{
                        $t(
                            "商品下单后，24小时内发货。如下单存在物流管控，订单可能被延时发货，请留意订单物流信息或联系客服"
                        )
                    }}
                </div>
            </div>
            <div class="product-line-item">
                <div class="left">{{ $t("运费") }}</div>
                <div class="right" @click="isShippingShow = true">
                    {{
                        goods_info.freightAmount == 0
                        ? $t("免运费")
                        : `$${goods_info.freightAmount ? priceFormat(goods_info.freightAmount) : "0.00"}`
                    }}
                    <div class="right-icon image_reversed"></div>
                </div>
            </div>
            <div class="product-line-item">
                <div class="left">{{ $t("税费") }}</div>
                <div class="right" @click="isShippingShow = true">
                    ${{ goods_info.goodsTax ? priceFormat(goods_info.goodsTax) : "0.00" }}
                </div>
            </div>
            <div id="Evaluation"></div>
            <div class="product-line-item">
                <div class="left">{{ $t("已选数量") }}</div>
                <div class="right">
                    <van-stepper :disable-input="true" :max="maxBuyNum" integer v-model="bugNum" />
                </div>
            </div>
        </div>
        <div class="Evaluation">
            <!-- <router-link to="/allReviews"> -->
            <div class="nav-item" @click="jumpAllReviews">
                <div class="left" v-if="itemName != 'Inchoi'">{{ $t("用户评价") }}({{ evaluationNum > 99 ? '99+' : evaluationNum
                }})</div>
                <div class="left" v-else>{{ $t("用户评价") }}</div>
                <div class="right">
                    <div class="right-icon image_reversed"></div>
                </div>
            </div>
            <div class="sort">
                <span :class="[isEn && 'en_span', sort_index === -2 && 'active']" @click="sort_index = -2">{{
                    $t('有图')
                }}
                    ({{ havePicture > 99 ? '99+' : havePicture }})
                </span>
                <span :class="[isEn && 'en_span', sort_index === 1 && 'active']" @click="sort_index = 1">{{ $t('好评') }}
                    ({{ positiveComments > 99 ? '99+' : positiveComments }})
                </span>
                <span :class="[isEn && 'en_span', sort_index === 2 && 'active']" @click="sort_index = 2">{{ $t('中评') }}
                    ({{ mediumReview > 99 ? '99+' : mediumReview }})
                </span>
                <span :class="[isEn && 'en_span', sort_index === 3 && 'active']" @click="sort_index = 3">{{ $t('差评') }}
                    ({{ negativeComment > 99 ? '99+' : negativeComment }})
                </span>
            </div>
            <div class="reviews-list">
                <div v-for="(item, index) in EvaluationInfo" :key="index" class="sheet-item">
                    <div class="top">
                        <img :src="require(`@/assets/image/avatar/${item.avatar}.png`)" class="img" />
                        <div class="name-title">
                            {{ item.userName }}
                            <!-- {{
                                item.userName.indexOf('@') > -1 ?
                                item.userName.replace(/(.{2}).*(@.*)/, "$1***$2") :
                                item.userName.indexOf(')') > -1 ?
                                item.userName.replace(/(\(\+\d{2}\))(\d{2})(.*)(\d{4})/, "$1$2***$4") :
                                item.userName.replace(/(.{2}).*(.{2}@.*)/, "$1***$2")
                            }} -->
                        </div>
                        <!-- <div style="flex-grow: 1">
                            
                            <p class="date">
                                {{ item.createTimeStr ? item.createTimeStr : item.createTime }}
                            </p>
                        </div> -->
                    </div>
                    <div class="mid">
                        <van-rate class="rate-wrap" v-model="item.rating" allow-half :size="15" :color="mainColor"
                            void-icon="star" void-color="#eee" readonly />
                        <span>{{ $t('订单已完成') }}</span>
                        <!-- <p class="sku" v-if="item.attributes?.[0]?.attrName">
                            <span v-for="(sku, index) of item.attributes" :key="sku.sort">
                                <span v-if="item.attributes">{{ sku.attrName }}：{{ sku.attrValue }}</span>
                            </span>
                        </p> -->
                    </div>
                    <p class="reviews">{{ item.content || $t('用户未发表评论') }}</p>
                    <div class="comment_image">
                        <div v-for="(url, i) of item.images" :key="i">
                            <img @click="ImagePreview({ images: item.images, startPosition: i })" v-if="url" :src="url"
                                alt="">
                        </div>
                    </div>
                    <div class="btm_date">
                        <span v-if="item?.countryName && !['Inchoi', 'GreenMall'].includes(itemName)">{{ item.countryName }}
                            >> </span>
                        <span>
                            <!-- {{ item.createTimeStr ? item.createTimeStr : formatZoneDate(item.createTime) }} -->
                            {{
                                item.evaluationTime ? formatZoneDate(item.evaluationTime) : formatZoneDate(item.createTime)
                            }}
                        </span>
                    </div>
                </div>
                <van-empty v-if="EvaluationInfo.length == 0" :description="$t('暂无数据')" />
            </div>
            <!-- </router-link> -->
            <!-- <div class="user-info" v-if="EvaluationInfo.name">
        <div class="avatar">
          <img :src="EvaluationInfo.avatar" />
        </div>
        <div class="info">
          <div class="name">
            <div class="name-title">
              {{
                EvaluationInfo.userName
                  ? EvaluationInfo.userName.substring(0, 2)
                  : ""
              }}*****
            </div>
            <van-rate
              class="rate-wrap"
              readonly
              v-model="EvaluationInfo.rating"
              :size="15"
              :color="mainColor"
              void-icon="star"
              void-color="#eee"
            />
          </div>

          <div class="datetime">{{ EvaluationInfo.createTime }}</div>
        </div>
      </div> -->
            <div class="centent">
                {{ EvaluationInfo.content }}
            </div>
        </div>
        <div class="details-wrap">
            <div class="shop-wrap">
                <div class="shop-info">
                    <div class="left">
                        <div class="shop-logo">
                            <img :src="SellerInfo.avatar" />
                        </div>
                        <div class="info">
                            <div class="name">
                                {{
                                    SellerInfo.name?.length > 27
                                    ? SellerInfo.name.slice(0, 27) + "..."
                                    : SellerInfo.name
                                }}
                            </div>
                            <div class="title">
                                {{ $t("好评率") }}: {{ Math.floor(SellerInfo.highOpinion * 100) || 100 }}%
                            </div>
                        </div>
                    </div>
                    <div class="right" @click="jumpShop">
                        {{ $t("访问商店") }}
                    </div>
                </div>

                <div class="shop-bottom">
                    <div class="item">
                        <div class="text">
                            {{ goods_info.seller ? goods_info.seller.sellerGoodsNum : 100 }}
                        </div>
                        <div class="title">{{ $t("所有产品") }}</div>
                    </div>
                    <div class="item">
                        <div class="text">
                            {{ (+goods_info.seller?.fake || 0) + (+goods_info.seller?.focusNum || 0) }}
                        </div>
                        <div class="title">{{ $t("关注") }}</div>
                    </div>
                    <div class="item">
                        <div class="text">
                            {{ (+goods_info.seller?.soldNum || 0) + (+goods_info.seller?.fakeSoldNum || 0) }}
                        </div>
                        <div class="title">{{ $t("销售量") }}</div>
                    </div>
                </div>
            </div>
            <!-- 推荐商品 -->
            <div class="recommended_product" v-if="recommendedGoods?.length">
                <div class="rd_title">{{ $t('推荐商品') }}</div>
                <ul>
                    <li v-for="(item, index) of recommendedGoods" :key="index" @click="getSellerGoodsInfo(item.id)">
                        <div class="img">
                            <img :src="item.imgUrl1 || $defaultGoodsImage" alt="">
                        </div>
                        <div class="rd_right">
                            <span class="nowrap2">{{ $textOmit(item.name, 26) }}</span>
                            <span>${{ priceFormat(item?.discountPrice || item.sellingPrice) }}</span>
                        </div>
                    </li>
                </ul>
            </div>
            <div class="shop-description-title" id="details">
                {{ $t("产品描述") }}
            </div>
            <div class="shop-description-text" @click="isshow = true" v-html="goods_info.des"></div>
            <div class="details-centent" v-html="goods_info.imgDes"></div>
            <van-empty v-if="!goods_info.des && !goods_info.imgDes" :description="$t('暂无数据')" />
            <!-- 猜你喜欢 -->
            <div class="may_like" v-if="likeGoods?.length">
                <div class="ml_title">{{ $t('猜你喜欢') }}</div>
                <div class="ml_list">
                    <div v-for="(item, index) in likeGoods" class="list-item commodity" @click="getSellerGoodsInfo(item.id)"
                        :key="index">
                        <div class="commodity-img">
                            <img :src="item.imgUrl1 || $defaultGoodsImage" alt="" />
                        </div>
                        <div class="money padd-15">
                            ${{ priceFormat(item.discountPrice || item.sellingPrice) }}
                        </div>
                        <div class="text padd-15">
                            {{ $t("销量") }} {{ priceFormatInt(item.soldNum) }}
                        </div>
                        <!-- <div class="text padd-15">{{$t('浏览量')}} 8464</div> -->
                        <div class="titlename padd-15 nowrap2">{{ $textOmit(item.name) }}</div>
                    </div>
                </div>
            </div>
        </div>
        <div class="buy-bottom-fiexd">
            <div class="fiexd-left">
                <div class="item" @click="addKeepGoods">
                    <div class="icon" :class="[
                        goods_info.isKeep == 1 ? 'collect-check-icon' : 'collect-icon',
                    ]"></div>
                    <div class="text">{{ $t(collectTitle) }}</div>
                </div>
                <div class="item" @click="openCustomer()">
                    <div class="icon kefu-icon"></div>
                    <div class="text">{{ itemName == 'FamilyMart' ? $t("联系商家") : $t("客服") }}</div>
                </div>
                <!-- <div class="item" @click="cardShow = true"> -->
                <div class="item" @click="isCard = productPropertiesShow = true">
                    <div class="icon gouwuc-icon">
                        <div class="tips" v-if="$ls.get('productList')">
                            {{ $ls.get('productList').length }}
                        </div>
                    </div>
                    <div class="text">{{ $t("购物车") }}</div>
                </div>
            </div>
            <div class="fiexd-right" @click="productPropertiesShow = true; isCard = false;">
                <p>
                    ${{ priceFormat($operation(goods_info.discountPrice, bugNum, 'times')) ||
                        priceFormat($operation(goods_info.sellingPrice, bugNum, 'times')) }}
                </p>
                <p>{{ $t("立即购买") }}</p>
            </div>
        </div>
        <van-popup closeable v-model="isShippingShow" position="bottom" :style="{ height: '35%' }">
            <div class="pop-header-title">
                {{ $t("运费说明") }}
            </div>
            <div class="centent-wrap">
                <p>
                    {{ $t("1、跨境商品运费构成：运费=派送费+长途运费+送货费;") }}
                </p>
                <p>
                    {{ $t("2、如不满足包邮条件，按实际收取运费产品") }}
                </p>
                <p>
                    {{ $t("3、最终解释权归平台所有；") }}
                </p>
            </div>
        </van-popup>
        <transition name="fade">
            <!-- <img class="dingbu" v-show=" isShowTopBtn " @click=" toTop(0) " src="@/assets/image/commodity/dingbu.png" /> -->
            <van-icon v-show="isShowTopBtn" @click="toTop(0)" class="to_top" class-prefix="icon" name="huidaodingbu" />
        </transition>
        <van-popup v-model="cardShow" round position="bottom" :style="{ height: '40%' }" closeable>
            <div class="title">
                {{ $t("添加购物车") }}
            </div>
            <div class="card-wrap">
                <div class="left">
                    <div class="img">
                        <img :src="imageList[0]" />
                    </div>
                    <div class="goods_info">
                        <div class="name">
                            {{
                                goods_info.name?.length > 27
                                ? goods_info.name.slice(0, 27) + "..."
                                : goods_info.name
                            }}
                        </div>

                        <div class="money">
                            ${{ priceFormat(goods_info.discountPrice) || priceFormat(goods_info.sellingPrice) }}
                        </div>
                    </div>
                </div>
                <div class="right">
                    <van-stepper :disable-input="true" :max="maxBuyNum" integer v-model="bugNum" />
                </div>
            </div>
            <div class="card-but">
                <van-button type="primary" class="but" block @click="addCart">{{
                    $t("确定")
                }}</van-button>
            </div>
        </van-popup>
        <!-- 产品属性 -->
        <van-popup v-model="productPropertiesShow" position="bottom" closeable round class="product_properties">
            <div class="cart_title" v-if="isCard">
                {{ $t("添加购物车") }}
            </div>
            <div class="p_top">
                <div class="img">
                    <img :src="currentCoverImg || goods_info.imgUrl1 || $defaultGoodsImage"
                        @click=" ImagePreview([currentCoverImg || goods_info.imgUrl1])" alt="" />
                </div>
                <div class="t_right">
                    <span class="price">${{
                        priceFormat($operation(goods_info.discountPrice, bugNum, 'times')) ||
                        priceFormat($operation(goods_info.sellingPrice, bugNum, 'times'))
                    }}</span>

                    <div class="num_box">
                        <div>
                            <!-- <p></p> -->
                            {{ $t("已选") }}:
                            <span v-for=" item  of  currentSkuTitle " :key="item">
                                {{ item }}
                            </span>
                        </div>
                        <span>{{ $t("数量") }}: ×{{ bugNum }}</span>
                    </div>
                </div>
            </div>
            <div class="attributes_box">
                <div class="attributes" v-for="( item, i ) of  goods_info?.canSelectAttributes?.goodAttrs " :key="i">
                    <div class="p_title" v-if="item?.attrName">{{ currentSkuTitle[i] }}</div>
                    <ul v-if="item?.attrName">
                        <li :class="[sub.attrValueId == activeAttrs[i] && 'active', sub?.icon && 'img_box', sub.disabled && 'disabled']"
                            @click=" handleToggle(sub, i, sub.disabled)" v-for="( sub, j ) of  item.attrValues " :key="j">
                            <img v-if="sub?.icon" :src="sub.iconImg" alt="">
                            <span v-else>{{ sub.attrValueName }}</span>
                        </li>
                    </ul>
                </div>
                <div class="count_box">
                    <span>{{ $t("数量") }}:</span>
                    <van-stepper :disable-input="true" :max="maxBuyNum" integer v-model="bugNum" />
                </div>
            </div>

            <div class="sure">
                <van-button :disabled="btnDisabled" type="primary" class="btn" block @click="handleSubmit">{{
                    $t("确定")
                }}</van-button>
            </div>
        </van-popup>
        <Footer />
        <div class="loading_box" v-if="isLoading">
            <van-loading text-color="#0094ff" />
        </div>
    </div>
</template>
<script>
import {
    NavBar,
    Swipe,
    SwipeItem,
    Popup,
    Stepper,
    Rate,
    Toast,
    ImagePreview,
    Dialog,
    Tab,
    Tabs,
    Loading,
    Empty,
    Icon
} from "vant";
import {
    getSellerGoods,
    getEvaluationList,
    getSellerInfo,
    keepGoods,
    keepGoodsDel,
    apiEvaluationCountType,
    apiRecommendAndLike,
} from "@/API/commodity";
import { apiGetRecommendNew } from '@/API/home'
import { isLogin, priceFormat, getStorage, formatZoneDate, priceFormatInt } from "@/utils/utis";
import Footer from '@/components/Footer'
export default {
    data() {
        return {
            formatZoneDate,
            priceFormatInt,
            itemName: process.env.VUE_APP_ITEM_NAME,
            mainColor: process.env.VUE_APP_MAIN_COLOR,
            sort_index: '',
            goods_info: {}, //商品信息
            tab_nav_list: [this.$t("商品"), this.$t("评价"), this.$t("详情")],
            tab_index: 0,
            swiperWaitTime: 5000,
            imageList: [],
            isShippingShow: false,
            isShowTopBtn: false,
            EvaluationInfo: [],
            SellerInfo: {},
            sellerGoodsId: "",
            cartNum: 0, //购物车数量
            bugNum: 1, //购买数量
            evaluationNum: 0,
            collectTitle: '',
            cardShow: false,
            isCard: false,
            attributesIndex: [],
            Token: "",
            isWatch: true,
            productPropertiesShow: false,
            activeAttrs: [],
            allSkus: [],
            currentSkuTitle: [],
            currentSkuId: "-1",
            //
            attrsIdSkuId: [],
            defaultSku: [],
            defaultAvatar: require("@/assets/image/default_avatar.png"),
            ImagePreview,
            isLoading: false,
            isEn: getStorage('lang') == 'en',
            havePicture: '0',
            mediumReview: '0',
            negativeComment: '0',
            positiveComments: '0',
            recommendedGoods: [],
            likeGoods: [],
            currentCoverImg: '',
            defaultImageList: [],
            btnDisabled: true,
            originalPrice: 0,
            maxBuyNum: localStorage.getItem('maxBuyNum') || 500,
        };
    },
    computed: {
        langIsAr() {
            return localStorage.getItem('lang') == 'ar'
        }
    },
    components: {
        Footer,
        [ImagePreview.name]: ImagePreview,
        [Empty.name]: Empty,
        [Loading.name]: Loading,
        [Tab.name]: Tab,
        [Tabs.name]: Tabs,
        [NavBar.name]: NavBar,
        [Swipe.name]: Swipe,
        [SwipeItem.name]: SwipeItem,
        [Popup.name]: Popup,
        [Stepper.name]: Stepper,
        [Rate.name]: Rate,
        [Icon.name]: Icon,
        [Toast.name]: Toast,
        [Dialog.Component.name]: Dialog.Component,
    },
    created() {
        setTimeout(() => {
            window.scrollTo(0, 0);
        }, 50)

        let lang = this.$route.query?.lang
        if (lang) {
            switch (lang) {
                case 'zh-CN':
                    lang = 'cn'
                    break;
                case 'zh-TW':
                case 'CN':
                    lang = 'tw'
                    break;
                case 'en-US':
                    lang = 'en'
                    break;
                default:
                    lang = 'en'
                    break;
            }
            sessionStorage.setItem('backPath', '/')
            if (lang !== localStorage.getItem('lang')) {
                localStorage.setItem('lang', lang)
                location.reload()
            }
        }
        this.sellerGoodsId = this.$route.query.sellerGoodsId;
        if (this.sellerGoodsId) {
            this.getSellerGoodsInfo();
            this.getEvaluationList();
        }
        //购物车数量
        if (this.$ls.get("productList")) {
            let list = this.$ls.get("productList");
            this.cartNum = list.reduce(function (prev, cur) {
                return (prev += cur.count);
            }, 0);
        }
        //监听购物车商品
        this.$ls.on("productList", (list) => {
            if (list.length > 0) {
                this.cartNum = list.reduce(function (prev, cur) {
                    return (prev += cur.count);
                }, 0);
            }
        });
        // 获取中评差评数量
        apiEvaluationCountType({ goodId: this.$route.query.sellerGoodsId }).then(res => {
            const { havePicture, mediumReview, negativeComment, positiveComments } = res
            this.havePicture = havePicture
            this.mediumReview = mediumReview
            this.negativeComment = negativeComment
            this.positiveComments = positiveComments
        })
        this.Token = localStorage.getItem("item");
    },
    mounted() {
        window.addEventListener("scroll", this.handleScroll);
    },
    methods: {
        // 获取推荐商品 type： 1、猜你喜欢  2、推荐
        async requestRecommendedProduct() {
            const params = { sellerId: this.SellerInfo?.id, pageNum: 1, }
            this.likeGoods = await apiRecommendAndLike({ ...params, pageSize: 4, type: 1 })
            this.recommendedGoods = await apiRecommendAndLike({ ...params, pageSize: 8, type: 2, })
        },
        handleTabsChange(index) {
            this.tab_index = index
            this.toTop(index)
        },
        handleToggle(info, index, dis, bool) {
            if (dis) return
            const disAttr = new Set();
            const allGood = this.goods_info?.canSelectAttributes?.goodAttrs
            const temparr = JSON.parse(JSON.stringify(this.activeAttrs))
            if (allGood.length === this.activeAttrs.length) {
                allGood.forEach((item, i) => {
                    if (i != index) {
                        item.attrValues.forEach((attr, j) => {
                            if (attr.attrValueId !== info.attrValueId) {
                                temparr[i] = attr.attrValueId
                                if (!this.getSkusAndPrice(true, temparr)) {
                                    disAttr.add(attr.attrValueId)
                                    this.$set(this.activeAttrs, index, info.attrValueId);
                                }
                            }
                        })
                    }
                })
            }

            this.allSkus.flatMap(item => item.attrs)
                .filter(attr => attr.hidden && attr.attrValueId !== info.attrValueId)
                .forEach(attr => disAttr.add(attr.attrValueId));

            allGood.forEach(item => {
                item.attrValues.forEach(attr => {
                    attr.disabled = disAttr.has(attr.attrValueId);
                });
            });
            this.$set(this.activeAttrs, index, info.attrValueId);
            this.getSkusAndPrice()
            disAttr.clear()
            this.$forceUpdate();
            !bool && this.handleToggle(info, index, dis, true)
        },
        getSkusAndPrice(find, arr) {
            let skuMap = {}
            this.allSkus.forEach((item) => {
                const attrIds = item.attrs.map(attr => attr.attrValueId).join(',')
                if (skuMap[attrIds]) return
                skuMap[attrIds] = {
                    title: item.attrs.map(attr => attr.attrName && attr.attrValueName ? `${attr.attrName}: ${attr.attrValueName}` : ''),
                    coverImg: item.coverImg,
                    discountPrice: item.discountPrice,
                    sellingPrice: item.sellingPrice,
                    skuId: item.skuId,
                    img: item?.img || this.defaultImageList,
                    hidden: item.hidden,
                    price: item.price,
                }
            })
            const attrIds = find ? arr.join(',') : this.activeAttrs.join(',')
            if (skuMap[attrIds] && !find) {
                this.currentSkuTitle = skuMap[attrIds].title
                this.goods_info.discountPrice = skuMap[attrIds].discountPrice || skuMap[attrIds].sellingPrice
                this.currentSkuId = skuMap[attrIds].skuId
                this.currentCoverImg = skuMap[attrIds].coverImg
                this.imageList = skuMap[attrIds].img
                this.btnDisabled = false
                this.originalPrice = skuMap[attrIds].discountPrice ? skuMap[attrIds].price : 0
            } else {
                if (Object.keys(skuMap).length === 0) {
                    this.btnDisabled = false
                } else {
                    this.btnDisabled = true
                }
                return skuMap[attrIds]
            }
        },
        handleSubmit() {
            this.getSkusAndPrice()
            this.isCard ? this.addCart() : this.openPay();
        },
        handleScroll() {
            this.isShowTopBtn = (document.documentElement.scrollTop || document.body.scrollTop) > 500
            if (!this.isWatch) return;
            let EvaluationOffsetTop =
                this.$el.querySelector("#Evaluation").offsetTop - 50;
            let detailsOffsetTop =
                this.$el.querySelector("#details").offsetTop - 50;
            let scrollTop =
                window.pageYOffset ||
                document.documentElement.scrollTop ||
                document.body.scrollTop;
            if (scrollTop <= EvaluationOffsetTop) {
                this.tab_index = 0;
            } else if (
                scrollTop >= EvaluationOffsetTop &&
                scrollTop <= detailsOffsetTop
            ) {
                this.tab_index = 1;
            } else if (scrollTop >= detailsOffsetTop) {
                this.tab_index = 2;
            }
        },
        priceFormat(num) {
            return priceFormat(num);
        },
        //添加购物车
        addCart() {
            if (isLogin()) {
                if (this.goods_info?.isShelf == 0) {
                    this.$notifyWarn(this.$t("该商品已下架"));
                    return
                }
                this.productPropertiesShow = this.cardShow = false;
                let productList = [];
                if (JSON.stringify(this.goods_info) == "{}") {
                    console.log("商品数据有误,无法添加");
                    return;
                }
                //添加选择数量
                this.goods_info.count = this.bugNum;
                this.goods_info.skuId = this.currentSkuId;
                this.goods_info.coverImg = this.currentCoverImg;
                this.goods_info.tempId = new Date().getTime();

                if (this.$ls.get("productList")) {
                    productList = this.$ls.get("productList") || [];
                    //验证是否已添加过
                    let ishave = true;
                    try {
                        productList.forEach((item) => {
                            if (item.id == this.goods_info.id && item.skuId == this.goods_info.skuId) {
                                item.count += this.bugNum;
                                this.cartNum += this.bugNum;
                                // Toast(this.$t("购物车添加成功"));
                                this.$notify(this.$t('购物车添加成功'), 'success')
                                // Toast(this.$t('购物车已存在此商品'))
                                ishave = false;
                                throw "跳出添加";
                            }
                        });
                    } catch (e) {
                        //购物数量添加,重置购物车
                        this.$ls.set("productList", productList);
                        this.$ls.remove("cartList");
                    }
                    //添加
                    if (ishave) {
                        if (this.goods_info.storeName == "") {
                            // return Toast(this.$t("购物车添加失败, 请返回重试"));
                            return this.$notify(this.$t('购物车添加失败, 请返回重试'))
                        }
                        productList.push(this.goods_info);
                        this.$ls.set("productList", productList);
                        this.cartNum = productList.reduce(function (prev, cur) {
                            return (prev += cur.count);
                        }, 0);
                        // Toast(this.$t("购物车添加成功"));
                        this.$notify(this.$t('购物车添加成功'), 'success')
                        this.$ls.remove("cartList");
                    }
                } else {
                    if (this.goods_info.storeName == "") {
                        return this.$notify(this.$t('购物车添加失败, 请返回重试'))
                    }
                    productList.push(this.goods_info);
                    this.$ls.set("productList", productList);
                    this.cartNum = productList.reduce(function (prev, cur) {
                        return (prev += cur.count);
                    }, 0);
                    // Toast(this.$t("购物车添加成功"));
                    this.$notify(this.$t('购物车添加成功'), 'success')
                    this.$ls.remove("cartList");
                }
                // console.log(this.$ls.get('productList'))
                // this.$ls.clear()
            } else {
                this.productPropertiesShow = this.cardShow = false;
                //   Toast(this.$t("请先登录"));
                // Dialog.confirm({
                //     title: this.$t("您还未登录"),
                //     message: this.$t("是否跳转到登录页面"),
                //     confirmButtonText: this.$t("确认"),
                //     cancelButtonText: this.$t("取消"),
                // }).then(() => {
                //     this.$router.push("/login");
                // });
                this.$notifyWarn(this.$t("请先登录"));
                this.$router.push("/login");
            }
        },
        //获取商品详情
        getSellerGoodsInfo(sellerGoodsId) {
            this.collectTitle = this.$t('收藏')
            this.$toast.loading()
            // 推荐商品/猜你喜欢
            if (sellerGoodsId) {
                this.activeAttrs = []
                this.allSkus = []
                this.goods_info = {}
                this.imageList = this.defaultImageList = []
                scrollTo({ top: 0, left: 0, behavior: 'smooth' })
            }
            let dataJson = {
                sellerGoodsId: sellerGoodsId || this.sellerGoodsId,
                skuId: this.$route.query?.skuId || null,
            };
            getSellerGoods(dataJson).then((data) => {
                this.$nextTick(() => {
                    this.goods_info = data;
                    this.getSkusAndPrice()
                })
                if (data.canSelectAttributes?.goodAttrs?.length) {
                    data.canSelectAttributes.goodAttrs.forEach((item) => {
                        this.activeAttrs.push(item.attrValues[0].attrValueId);
                        // if (item.attrValues[0].icon) {
                        //     this.imageList = item.attrValues.map(sub => sub.iconImg)
                        // }
                    });
                    this.allSkus = data.canSelectAttributes.skus;
                    const ids = data.canSelectAttributes.goodAttrs.map(item => item.attrId)
                    this.allSkus.forEach((item) => {
                        item.attrs = item.attrs.sort((star, next) => ids.indexOf(star.attrId) - ids.indexOf(next.attrId))
                    })
                }
                for (let i = 0; i < 10; i++) {
                    if (data[`imgUrl${i + 1}`]) {
                        this.defaultImageList.push(data[`imgUrl${i + 1}`]);
                    }
                }
                if (!this.imageList.length) {
                    this.imageList = this.defaultImageList
                }
                this.getSellerInfo(data.seller.id);
                if (this.goods_info.isKeep == 1) {
                    this.collectTitle = this.$t("已收藏");
                } else {
                    this.collectTitle = this.$t("收藏");
                }
                if (!data.canSelectAttributes?.goodAttrs) {
                    if (data.discountPrice) {
                        this.originalPrice = data.sellingPrice
                    }
                }
                this.$toast.clear()
            });
        },
        //获取评论
        getEvaluationList() {
            let dataJson = {
                sellerGoodsId: this.sellerGoodsId,
                pageNum: 1,
                pageSize: 1,
                evaluationType: this.sort_index
            };
            getEvaluationList(dataJson).then((res) => {
                if (res.pageList.length > 0) {
                    this.EvaluationInfo = res.pageList.slice(0, 5);
                    this.EvaluationInfo = this.EvaluationInfo.map(item => {
                        const images = [item.imgUrl1, item.imgUrl2, item.imgUrl3, item.imgUrl4, item.imgUrl5, item.imgUrl6, item.imgUrl7, item.imgUrl8, item.imgUrl9]
                        return {
                            ...item,
                            avatar: item.avatar || Math.floor(Math.random() * 20),
                            images: images.filter(url => (!!url))
                        }
                    })
                    this.evaluationNum = res.evaluationNum;
                } else {
                    this.EvaluationInfo = []
                }
            });
        },
        addKeepGoods() {
            if (!isLogin()) {
                //   Toast(this.$t("请先登录"));
                // Dialog.confirm({
                //     title: this.$t("您还未登录"),
                //     message: this.$t("是否跳转到登录页面"),
                //     confirmButtonText: this.$t("确认"),
                //     cancelButtonText: this.$t("取消"),
                // }).then(() => {
                //     this.$router.push("/login");
                // });
                this.$notifyWarn(this.$t("请先登录"));
                this.$router.push("/login");
                return;
            }

            if (this.goods_info.isKeep == 1) {
                let dataJson = {
                    sellerGoodsId: this.sellerGoodsId,
                };
                keepGoodsDel(dataJson).then(() => {
                    this.collectTitle = this.$t("收藏");
                    this.goods_info.isKeep = 0;
                    Toast(this.$t("取消成功"));
                });
            } else {
                let dataJson = {
                    sellerGoodsId: this.sellerGoodsId,
                };
                keepGoods(dataJson).then(() => {
                    this.collectTitle = this.$t("已收藏");
                    this.goods_info.isKeep = 1;
                    Toast(this.$t("收藏成功"));
                });
            }
        },
        //跳转评论页
        jumpAllReviews() {
            this.$router.push({
                path: "/allReviews",
                query: { sellerGoodsId: this.sellerGoodsId },
            });
        },
        // 商家详情
        getSellerInfo(id) {
            let dataJson = {
                sellerId: id,
            };
            getSellerInfo(dataJson).then((res) => {
                this.SellerInfo = res;
                //详情里添加商铺名称
                this.goods_info.storeName = res.name;
                this.isLoading = false
                isLogin() && this.requestRecommendedProduct()
            }).catch(err => {
                console.log(`err ::->`, err);
                this.isLoading = false
            })
        },
        checkActive(index) {
            return index === this.current; // current为监听的轮播index
        },
        //监听product轮播index
        handleChangeSwiper(index) {
            this.current = index;
        },
        onClickLeft() {
            const backPath = sessionStorage.getItem("backPath")
            if (backPath) {
                this.$router.replace('/')
                sessionStorage.removeItem("backPath")
            } else {
                this.$router.go(-1);
            }
        },
        toTop(index) {
            this.isWatch = false;
            setTimeout(() => (this.isWatch = true), 1000);
            this.tab_index = index;
            if (index === 0) {
                this.$el
                    .querySelector("#product")
                    .scrollIntoView({ block: "start", behavior: "smooth" });
            } else if (index === 1) {
                this.$el
                    .querySelector("#Evaluation")
                    .scrollIntoView({ block: "start", behavior: "smooth" });
            } else {
                this.$el
                    .querySelector("#details")
                    .scrollIntoView({ block: "start", behavior: "smooth" });
            }
        },
        //跳转商铺
        jumpShop() {
            sessionStorage.removeItem("shopState");
            this.$router.push(`/shop?sellerId=${this.SellerInfo.id}&index=0`);
        },
        //跳转下单
        openPay() {
            if (!isLogin()) {
                this.productPropertiesShow = false;
                // Dialog.confirm({
                //     title: this.$t("您还未登录"),
                //     message: this.$t("是否跳转到登录页面"),
                //     confirmButtonText: this.$t("确认"),
                //     cancelButtonText: this.$t("取消"),
                // }).then(() => {
                //     this.$router.push("/login");
                // });
                this.$notifyWarn(this.$t("请先登录"));
                this.$router.push("/login");
                return;
            }
            if (this.goods_info?.isShelf == 0) {
                this.$notifyWarn(this.$t("该商品已下架"));
                return
            }
            localStorage.setItem("sellerId", this.goods_info.sellerId);
            localStorage.setItem("storeName", this.goods_info.storeName);
            this.goods_info.tempId = new Date().getTime();
            //type:1直接购买,2购物车购买
            this.$router.push({
                path: "/orderComnfirmation",
                query: {
                    skuId: this.currentSkuId,
                    type: 1,
                    goodsInfo: JSON.stringify(this.goods_info),
                    bugNum: this.bugNum,
                    isCart: 0,
                    currentCoverImg: this.currentCoverImg
                },
            });
        },
        // 打开客服
        openCustomer() {
            localStorage.setItem("sellerId", this.goods_info.sellerId);
            localStorage.setItem("storeName", this.goods_info.storeName);
            if (isLogin()) {
                // Toast(this.$t("请先登录"));
                sessionStorage.setItem('shopName', this.SellerInfo.name)
                this.$router.push({ path: `/customerServiceIndex?goodsId=${this.goods_info.id}` });
            } else {
                //   Toast(this.$t("请先登录"));
                // Dialog.confirm({
                //     title: this.$t("您还未登录"),
                //     message: this.$t("是否跳转到登录页面"),
                //     confirmButtonText: this.$t("确认"),
                //     cancelButtonText: this.$t("取消"),
                // }).then(() => {
                //     this.$router.push("/login");
                // });
                this.$notifyWarn(this.$t("请先登录"));
                this.$router.push("/login");
            }
        },
    },
    watch: {
        bugNum(val) {
            this.cartNum = val;
        },
        sort_index() {
            this.getEvaluationList()
        },
        productPropertiesShow(val) {
            val && (this.swiperWaitTime = 5000)
        },
    },
    beforeDestroy() {
        window.removeEventListener("scroll", this.handleScroll);
    },
    destroyed() {
        //撤销监听
        this.$ls.off("productList");
    },
};
</script>
<style lang="scss" scoped>
html[dir="rtl"] {
    .CommodityDetails /deep/ .van-tab--active {
        position: relative;

        &::after {
            content: '';
            width: 50px;
            height: 3px;
            background: var(--main-color);
            position: absolute;
            bottom: 0;
            left: 50%;
            transform: translateX(-50%);
            border-radius: 2px;
        }
    }
}

.may_like {
    margin-top: 16px;
    width: 100%;


    .ml_title {
        font-size: 14px;
    }

    .ml_list {
        display: flex;
        flex-wrap: wrap;
        padding-bottom: 20px;
    }

    .list-item {
        width: 46%;
        height: 245px;
        border: 1px solid #eeeeee;
        margin-top: 20px;
        border-radius: 4px;

        .commodity-img {
            width: 130px;
            height: 130px;
            // height: 160px;
            padding: 10px;
            display: flex;
            justify-content: center;
            align-items: center;

            img {
                height: fit-content;
                width: auto;
                max-height: 100%;
                max-width: 100%;
            }
        }

        .money {

            color: var(--main-color);
            font-weight: 500;
            font-size: 16px;
            margin-top: 10px;
            padding-left: 8px;
            box-sizing: border-box;
        }

        .text {
            color: #999999;
            font-size: 12px;
            margin-top: 3px;
            padding-left: 8px;
            box-sizing: border-box;
        }

        .titlename {
            width: 100%;
            height: 37px;
            margin-top: 4px;
            padding-left: 8px;
            box-sizing: border-box;
            text-align: left !important;
        }
    }

    .list-item:nth-child(even) {
        margin-left: 6%;
    }
}

.recommended_product {
    margin-top: 16px;
    width: 100%;

    .rd_title {
        font-size: 14px;
    }

    ul {
        display: flex;
        flex-wrap: wrap;
        justify-content: space-between;
        box-sizing: border-box;

        li {
            flex: 0 0 167px;
            height: 70px;
            border: 1px solid #eee;
            margin-top: 16px;
            display: flex;
            border-radius: 2px;

            .img {
                flex: 0 0 63px;
                height: 63px;
                padding: 6px;
                box-sizing: border-box;
                display: flex;
                justify-content: center;
                align-items: center;

                img {
                    max-width: 100%;
                    max-height: 100%;
                }
            }

            .rd_right {
                flex: 1;
                padding-top: 10px;

                span {
                    &:nth-child(1) {
                        font-size: 10px;
                        min-height: 28px;
                    }

                    &:nth-child(2) {
                        margin-top: 4px;
                        font-weight: 500;
                        font-size: 14px;
                        line-height: 16px;

                        color: var(--main-color);
                    }
                }
            }
        }
    }
}

.product_properties {
    min-height: 30%;
    padding: 20px 0;
    // z-index: 10000 !important;



    .p_top {
        padding: 0 20px;
        display: flex;
        align-items: center;
        min-height: 60px;

        .img {
            flex: 0 0 50px;
            width: 50px;
            height: 50px;
            margin-right: 10px;
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 5px;
            border: 1px solid #efefef;
            border-radius: 4px;

            img {
                max-width: 100%;
                max-height: 100%;
            }
        }

        .t_right {
            height: 100%;
            display: flex;
            flex-direction: column;
            justify-content: space-between;

            // align-items: center;
            .price {
                font-size: 16px;
                font-weight: 500;
                color: var(--main-color);
            }

            .num_box {
                display: flex;
                flex-direction: column;
                font-size: 12px;
            }
        }
    }

    .attributes_box {
        max-height: 330px;
        overflow-y: auto;
        scrollbar-width: none;
        -ms-overflow-style: none;

        &::-webkit-scrollbar {
            display: none;
        }
    }

    .attributes {
        margin-top: 20px;
        padding: 0 0 0 20px;

        .p_title {
            font-size: 14px;
            margin-bottom: 10px;
        }

        ul {
            display: flex;
            flex-wrap: wrap;

            li {
                padding: 5px 16px;
                background: #f2f2f2;
                margin-right: 10px;
                margin-bottom: 10px;
                border-radius: 4px;
                // max-width: 38px;
                // max-height: 38px;
                border: 1px solid #eee;
                display: flex;
                justify-content: center;
                align-items: center;

                img {
                    max-width: 25px;
                    max-height: 25px;
                }

                &.active {
                    background: var(--main-color);
                    color: #fff !important;
                }

                &.disabled {
                    // background: #ccc;
                    color: #A3A3A3;
                    opacity: .8;
                    // opacity: .5;
                }

                &.img_box {
                    min-width: 38px;
                    min-height: 38px;
                    padding: 0;
                    background: #fff;

                    &.disabled {
                        border: 1px dashed #eee !important;
                        background: transparent !important;
                        opacity: .5;
                        // -webkit-filter: grayscale(100%);
                        // -moz-filter: grayscale(100%);
                        // -ms-filter: grayscale(100%);
                        // -o-filter: grayscale(100%);
                        // filter: grayscale(100%);
                        // filter: gray;
                    }

                    &.active {
                        border-color: var(--main-color);
                    }
                }
            }
        }
    }

    .count_box {
        margin-top: 30px;
        padding: 0 20px;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }

    .sure {
        // width: 100%;
        margin-top: 40px;
        padding: 0 20px;

        .btn {
            // background: var(--main-color);
            background: var(--main-color);
            border: none;
            border-radius: 4px;
            font-size: 14px;
        }
    }
}

.comment_image {
    display: flex;
    justify-content: flex-start;
    align-items: center;
    flex-wrap: wrap;

    // padding: 0 15px;
    div {
        width: 77px;
        height: 72px;
        display: flex;
        justify-content: center;
        align-items: center;
        border: 1px solid #EEEEEE;
        flex: 0 0 77px;
        margin-right: 8px;
        margin-top: 8px;

        img {
            max-width: 60px;
            max-height: 60px;
        }
    }
}

.CommodityDetails {
    width: 100%;
    min-height: 100%;
    font-size: 14px;
    padding-bottom: 53px;
    overflow-x: hidden;

    a {
        color: #333333;
    }

    .tab-wrap {
        display: flex;
        position: absolute;
        left: 0;
        top: 0;
        width: 90%;
        height: 46px;
        margin-left: 10%;

        :deep(.van-tabs) {
            width: 100%;

            .van-tabs__line {
                width: 80px;
                // background: var(--main-color) !important;
                background: var(--main-color) !important;
            }
        }

        .tab-item {
            flex: 1;
            display: flex;
            align-items: center;
            justify-content: center;
        }

        .active {
            // border-bottom: 2px solid var(--main-color);
            border-bottom: 2px solid var(--main-color);
        }
    }

    .banner-product {
        width: 100%;
        // margin-top: 10px;
        //   filter: drop-shadow(0px 6px 12px rgba(55, 63, 69, 0.1));
        border-radius: 4px;
        position: relative;
        min-height: calc(100vw + 10px);

        .van-swipe {
            min-height: calc(100vw + 10px);
        }

        .swipe-item {
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vw;

            .img {
                max-width: 100%;
                max-height: 100%;
                margin: 0 auto;
                // transform: translateY(-10px);
            }
        }

        //指示器
        .indicators {
            position: absolute;
            bottom: 0px;
            left: 50%;
            display: flex;
            transform: translateX(-50%);
        }

        .indicator li {
            display: inline;
            width: 12px;
            height: 2px;
            background-color: rgb(93, 91, 88);
            border-radius: 20%;
            opacity: 0.3;
            transition: opacity 0.5s,
                //@animation-duration-fast
                background-color 0.5s; //@animation-duration-fast

            &:not(:last-child) {
                margin-right: 6px;
            }

            &.active {
                background-color: var(--main-color);
                opacity: 1;
            }
        }
    }

    .product-info-wrap {
        padding: 0 10px;

        .product-name {
            font-weight: 500;
            font-size: 16x;
            padding: 15px 0;
            border-bottom: 1px solid #eeeeee;
        }

        .price-box {
            display: flex;
            justify-content: space-between;
            align-items: center;
            height: 30px;
            border-bottom: 1px solid #eeeeee;
            padding: 10px 0;
            overflow-x: auto;
            overflow-y: hidden;
            line-height: 18px;
            scrollbar-width: none;
            -ms-overflow-style: none;

            &::-webkit-scrollbar {
                display: none;
            }

            .product-sold {
                font-size: 12px;
                color: #999;
                white-space: nowrap;
            }

            .product-sellingPrice {
                display: flex;
                justify-content: space-between;
                align-items: center;
                color: #999999;
                line-height: 18px;
                white-space: nowrap;
                margin: 0 20px;

                .title {
                    font-size: 12px;
                    line-height: 18px;
                }

                .money {
                    text-decoration: line-through;
                    margin-left: 10px;
                    font-size: 10px;
                    line-height: 18px;
                }
            }

            .product-price {
                white-space: nowrap;

                .title {
                    color: #999999;
                    font-size: 14px;
                }

                .money {
                    // color: hsl(37, 100%, 49%);
                    color: var(--main-color);
                    font-size: 16px;
                    font-weight: 500;
                    margin-left: 10px;
                }

                .text {
                    margin-left: 15px;
                    color: #999999;
                    font-size: 12px;
                    text-decoration: line-through;
                }
            }
        }

        .product-norm {
            display: flex;
            color: #999999;
            font-size: 12px;
            margin-top: 10px;
            border-bottom: 1px solid #eeeeee;
            padding-bottom: 10px;
            justify-content: flex-end;
            // .left {
            //   // flex: 1;
            // }

            // .right {
            // }
        }

        .product-line-item {
            width: 100%;
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            font-size: 12px;
            border-bottom: 1px solid #eeeeee;
            padding: 15px 0;

            .left {
                // flex: 1;
                // min-width: 10px;
                margin-right: 10px;
            }

            .right {
                flex: 1;
                display: flex;
                align-items: center;
                justify-content: flex-end;
            }
        }
    }

    .Evaluation {
        padding: 0 10px;

        .sort {
            width: 100vw;
            display: flex;
            align-items: center;
            justify-content: flex-start;
            margin: 13px 0;
            overflow-x: auto;
            scrollbar-width: none;
            -ms-overflow-style: none;

            &::-webkit-scrollbar {
                display: none;
            }

            &.en_sort {
                flex-wrap: wrap;

                span {
                    flex: 0 0 30%;
                    margin-right: 0 !important;
                    margin-top: 13px;
                    margin-left: 13px;
                }
            }

            span {
                display: flex;
                justify-content: center;
                align-items: center;
                padding: 0 12px;
                height: 28px;
                border-radius: 14px;
                margin-right: 13px;
                color: #999;
                background: #eee;
                white-space: nowrap;

                &.active {
                    // background: var(--main-color);
                    background: var(--main-color);
                    color: #fff !important;
                }

                &.en_span {
                    margin-right: 0px;

                    &:nth-child(1) {
                        transform: scale(.8) translateX(-15px);
                    }

                    &:nth-child(2) {
                        transform: scale(.8) translateX(-30px);
                    }

                    &:nth-child(3) {
                        transform: scale(.8) translateX(-45px);
                    }

                    &:nth-child(4) {
                        transform: scale(.8) translateX(-62px);
                    }
                }
            }
        }

        .nav-item {
            display: flex;
            font-size: 12px;
            margin-top: 10px;
            // padding-bottom: 10px;

            .left {
                flex: 1;
                min-width: 60px;
            }

            .right {
                img {
                    height: 10px;
                }
            }
        }

        .user-info {
            display: flex;
            align-items: center;

            .avatar {
                width: 32px;
                height: 32px;

                img {
                    width: 100%;
                    height: 100%;
                }
            }

            .info {
                margin-left: 10px;

                .name {
                    font-weight: 400;
                    display: flex;
                    align-items: center;

                    .name-title {
                        width: 60px;
                    }

                    .rate-wrap {
                        margin-left: 10px;
                    }
                }

                .datetime {
                    color: #999999;
                    font-size: 10px;
                }
            }
        }

        .centent {
            line-height: 17px;
            margin-top: 10px;
        }
    }

    .right-icon {
        width: 6px;
        height: 10px;
        background: url("../../assets/image/commodity/gengduo.png") no-repeat;
        background-size: 100% 100%;
        margin-left: 5px;
    }

    .details-wrap {
        padding: 0 10px;

        .shop-wrap {
            min-height: 120px;
            background: #ffffff;
            border: 1px solid #eeeeee;
            padding: 15px;
            margin-top: 20px;

            .shop-info {
                display: flex;
                align-items: center;
                border-bottom: 1px solid #eeeeee;
                padding-bottom: 20px;

                .left {
                    flex: 1;
                    display: flex;
                    align-items: center;

                    .shop-logo {
                        img {
                            display: block;
                            width: 46px;
                            height: 46px;
                            border-radius: 50%;
                        }
                    }

                    .info {
                        margin-left: 10px;

                        .name {
                            font-size: 14px;
                            font-weight: bold;
                        }

                        .title {
                            color: #333333;
                            font-size: 10px;
                            line-height: 1.5;
                            padding-top: 5px;
                            text-align: start;

                            span {

                                color: var(--main-color);
                            }
                        }
                    }
                }

                .right {
                    background: #fcf2e2;
                    // border: 1px solid var(--main-color);
                    border: 1px solid var(--main-color);
                    border-radius: 27px;
                    min-width: 71px;
                    min-height: 17px;
                    padding: 0 5px;
                    font-size: 10px;
                    text-align: center;
                    line-height: 17px;

                    color: var(--main-color);
                }
            }

            .shop-bottom {
                display: flex;
                margin-top: 15px;

                .item {
                    flex: 1;
                    text-align: center;
                    position: relative;

                    .text {
                        color: #333333;
                        font-size: 16px;
                        font-weight: bold;
                    }

                    .title {
                        color: #333333;
                        margin-top: 4px;
                        font-size: 10px;
                        line-height: 1;
                    }
                }

                .item:not(:last-child) {
                    &::after {
                        position: absolute;
                        right: 0;
                        top: 50%;
                        height: 20px;
                        width: 1px;
                        transform: translateY(-50%);
                        background: #eeeeee;
                        content: "";
                    }
                }
            }
        }

        .details-centent {
            width: 100%;
            overflow-x: hidden;
            padding: 15px 0;

            :deep(*) {
                max-width: 100% !important;
            }
        }
    }

    .buy-bottom-fiexd {
        min-height: 53px;
        background: #ffffff;
        position: fixed;
        bottom: 0;
        left: 0;
        width: 100%;
        display: flex;
        align-items: center;
        z-index: 1888;

        .fiexd-left {
            flex: 1;
            display: flex;

            .item {
                padding: 0 5px;
                flex: 1;
                text-align: center;
                padding-top: 8px;

                .text {
                    font-size: 12px;
                    color: #333333;
                    transform: translateY(-1px) scale(0.9);
                }

                .icon {
                    width: 16px;
                    height: 16px;
                    margin: 0 auto;
                    margin-bottom: 2px;
                    position: relative;

                    .tips {
                        width: 15px;
                        height: 15px;
                        border-radius: 50%;
                        background: #ff3e3e;
                        text-align: center;
                        line-height: 15px;
                        font-size: 10px;
                        color: #fff;
                        position: absolute;
                        right: -10px;
                        top: -10px;
                    }
                }

                .collect-icon {
                    background: url("../../assets/image/commodity/Star6.png") center no-repeat;
                    background-size: 100% 100%;
                }

                .collect-check-icon {
                    background: url("../../assets/image/commodity/Star7.png") center no-repeat;
                    background-size: 100% 100%;
                }

                .kefu-icon {
                    background: url("../../assets/image/commodity/kefu.png") center no-repeat;
                    background-size: 100% 100%;
                }

                .kefu-icon {
                    background: url("../../assets/image/commodity/kefu.png") center no-repeat;
                    background-size: 100% 100%;
                }

                .gouwuc-icon {
                    background: url("../../assets/image/commodity/gouwuc.png") center no-repeat;
                    background-size: 100% 100%;
                }
            }
        }

        .fiexd-right {
            width: 150px;
            height: 100%;
            min-height: 53px;
            // background: var(--main-color);
            background: var(--main-color);
            height: 100%;
            color: #ffffff;
            text-align: center;
            padding-top: 8px;
            box-sizing: border-box;
        }
    }

    .dingbu {
        position: fixed;
        bottom: 100px;
        right: 10px;
        font-size: 30px;
    }

    .pop-header-title {
        height: 55px;
        text-align: center;
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        line-height: 55px;
        border-bottom: 1px solid #eeeeee;
        font-size: 16px;
        color: #333333;
    }

    .centent-wrap {
        padding: 65px 10px 10px 10px;

        p {
            color: #000;
            padding: 5px 0;
        }
    }

    .shop-description-title {
        color: #000000;
        padding: 10px 0;
    }

    .shop-description-text {
        color: #000000;
        font-size: 12px;
        width: 100%;
        overflow-x: hidden;
    }
}

.title {
    text-align: center;
    line-height: 50px;
    font-size: 16px;
}

.cart_title {
    text-align: center;
    font-size: 16px;
    transform: translateY(-8px);
}

.card-wrap {
    padding: 0 15px;
    padding-top: 30px;
    display: flex;
    align-items: center;

    .left {
        display: flex;
        flex: 1;

        .img {
            width: 70px;
            height: 70px;
            display: flex;
            justify-content: center;
            align-items: center;

            img {
                height: fit-content;
                width: auto;
                max-height: 100%;
                max-width: 100%;
            }
        }

        .goods_info {
            width: 150px;
            padding-left: 5px;

            .money {

                color: var(--main-color);
                font-weight: bold;
                margin-top: 10px;
            }

            .name {
                //   height: 36.5px;
                font-size: 14px;
                overflow: hidden;
                text-overflow: ellipsis;
                display: -webkit-box;
                -webkit-box-orient: vertical;
                -moz-box-orient: vertical;
                box-orient: vertical;
                -webkit-line-clamp: 2;
                line-clamp: 2;
            }
        }
    }
}

.card-but {
    position: absolute;
    bottom: 10px;
    left: 5%;
    width: 90%;
    display: flex;
    align-items: center;
    justify-content: center;
    margin: 0 auto;

    .but {
        margin: 0 auto;
        // background: var(--main-color);
        background: var(--main-color);
        border: none;
    }
}

.reviews-list {
    width: 100%;
    background: #fff;
    display: flex;
    flex-direction: column;
    justify-content: flex-start;
    align-items: center;

    .sheet-item {
        width: 100%;
        margin-bottom: 30px;
        border-top: 1px solid rgba(238, 238, 238, 1);

        .top {
            display: flex;
            justify-content: flex-start;
            align-items: center;
            padding: 10px 0 5px 0;

            .img {
                width: 30px;
                height: 30px;
                border-radius: 50%;
                border: 1px solid rgba(238, 238, 238, 1);
                // margin: 0 4%;
            }

            .name {
                font-size: 14px;
                font-weight: 600;
                display: flex;
                align-items: center;
                width: 100%;
                justify-content: space-between;


            }

            .name-title {
                margin-left: 10px;
                // width: 100px;
                display: -webkit-box;
                -webkit-box-orient: vertical;
                -moz-box-orient: vertical;
                box-orient: vertical;
                -webkit-line-clamp: 2;
                line-clamp: 2;
                overflow: hidden;
                text-overflow: ellipsis;
            }

            .date {
                font-size: 10px;
                margin-top: 5px;
            }
        }

        .mid {

            // padding: 0 15px;
            span {
                margin-left: 20px;

                color: var(--main-color);
                font-size: 12px;
            }

            .sku {
                margin-top: 5px;
                margin-bottom: 5px;

                span {
                    margin: 0;
                    color: #999999;
                    font-size: 10px;

                    &::before {
                        content: '';
                        display: inline-block;
                        width: 1px;
                        height: 7px;
                        background: #D9D9D9;
                        margin: 0 5px;
                    }

                    &:first-child {
                        &::before {
                            content: '';
                            display: none;
                        }
                    }
                }

            }
        }

        .btm_date {
            // padding: 0 15px;
            margin-top: 9px;
            font-size: 10px;
            color: #999;
        }

        .reviews {
            color: #000;
            font-size: 12px;
            display: inline-block;
            padding: 2% 1% 2% 0;
            word-break: break-word;
            white-space: pre-wrap;
        }
    }
}

.sku_box {
    border-bottom: 1px solid #eee;
    padding: 20px 0 15px 0;

    .attributes_box {
        max-height: 330px;
        overflow-y: auto;
        scrollbar-width: none;
        -ms-overflow-style: none;

        &::-webkit-scrollbar {
            display: none;
        }
    }

    .attributes {

        .p_title {
            font-size: 14px;
            margin-bottom: 10px;
        }

        ul {
            display: flex;
            // flex-wrap: wrap;
            overflow-x: auto;
            scrollbar-width: none;
            -ms-overflow-style: none;

            &::-webkit-scrollbar {
                display: none;
            }

            li {
                // width: 100px;
                // flex: 0 0 100px;
                padding: 5px 16px;
                background: #f2f2f2;
                margin-right: 10px;
                margin-bottom: 10px;
                border-radius: 4px;
                // min-width: 38px;
                // min-height: 38px;
                border: 1px solid #eee;
                display: flex;
                justify-content: center;
                align-items: center;
                white-space: nowrap;

                img {
                    max-width: 25px;
                    max-height: 25px;
                }

                &.active {
                    background: var(--main-color);
                    color: #fff !important;
                }

                &.disabled {
                    color: #A3A3A3;
                    opacity: .8;
                    // opacity: .5;
                }

                &.img_box {
                    min-width: 38px;
                    min-height: 38px;
                    padding: 0;
                    background: #fff;

                    &.disabled {
                        border: 1px dashed #eee !important;
                        background: transparent !important;
                        opacity: .5;
                        // -webkit-filter: grayscale(100%);
                        // -moz-filter: grayscale(100%);
                        // -ms-filter: grayscale(100%);
                        // -o-filter: grayscale(100%);
                        // filter: grayscale(100%);
                        // filter: gray;
                    }

                    &.active {
                        border-color: var(--main-color);
                    }
                }
            }
        }
    }
}




.fade-enter-active,
.fade-leave-active {
    transition: opacity .3s
}

.fade-enter,
.fade-leave-to {
    opacity: 0
}

:deep(.van-swipe) {
    overflow-y: auto !important;
}</style>
