<template>
    <div class="all-reviews" style="min-height: 100vh;">
        <van-nav-bar safe-area-inset-top fixed :title="$t('所有评论')" left-arrow @click-left="onClickLeft" />
        <div style="width: 100%; height: 46px"></div>
        <div class="top-total">
            <p v-if="itemName != 'Inchoi'">
                {{ $t("用户评价") }} <span>({{ evaluationNum }})</span>
            </p>
            <p v-else>
                {{ $t("用户评价") }}
            </p>
            <p>
                {{ $t('好评率') }}: {{ (Math.floor(positiveComments / evaluationNum * 100)) || 100 }}%
            </p>
        </div>
        <div class="sort">
            <span :class="[isEn && 'en_span', sort_index === -2 && 'active']" @click="sort_index = -2">{{
                $t('有图')
            }}
                ({{ havePicture }})
            </span>
            <span :class="[isEn && 'en_span', sort_index === 1 && 'active']" @click="sort_index = 1">{{ $t('好评') }}
                ({{ positiveComments }})
            </span>
            <span :class="[isEn && 'en_span', sort_index === 2 && 'active']" @click="sort_index = 2">{{ $t('中评') }}
                ({{ mediumReview }})
            </span>
            <span :class="[isEn && 'en_span', sort_index === 3 && 'active']" @click="sort_index = 3">{{ $t('差评') }}
                ({{ negativeComment }})
            </span>
        </div>
        <van-pull-refresh style="min-height: 100vh" v-model="refreshing" :pulling-text="$t('下拉即可刷新')"
            :loosing-text="$t('释放即可刷新')" :loading-text="$t('加载中')" @refresh="onRefresh">
            <van-list v-model="loading" :finished="finished" @load="onLoad" :loading-text="$t('加载中')">
                <div class="reviews-list">
                    <div v-for="(item, index) in list" :key="index" class="sheet-item">
                        <div class="top">
                            <img :src="require(`@/assets/image/avatar/${item.avatar || Math.floor(Math.random() * 20)}.png`)"
                                class="img" />
                            <div class="name-title">
                                <!-- {{ item.userName?.replace(/(.{2}).*(.{2}@.*)/, "$1***$2") }} -->
                                {{ item.userName }}
                            </div>
                        </div>
                        <div class="mid">
                            <van-rate class="rate-wrap" v-model="item.rating" allow-half :size="15" :color="mainColor"
                                void-icon="star" void-color="#eee" readonly />
                            <span>{{ $t('订单已完成') }}</span>
                            <p class="sku" v-if="item.attributes?.[0]?.attrName">
                                <span v-for="sku of item.attributes" :key="sku.sort">
                                    {{ sku.attrName }}：{{ sku.attrValue }}
                                </span>
                            </p>
                        </div>
                        <p class="reviews">{{ item.content || $t('用户未发表评论') }}</p>
                        <div class="comment_image">
                            <div v-for="(url, i) of item.images" :key="i">
                                <img @click="ImagePreview({ images: item.images, startPosition: i })" v-if="url" :src="url"
                                    alt="">
                            </div>
                        </div>
                        <div class="btm_date">
                            <span v-if="item?.countryName && !['Inchoi', 'GreenMall'].includes(itemName)">
                                {{ item.countryName }} >> </span>
                            {{
                                item.evaluationTime ? formatZoneDate(item.evaluationTime) : formatZoneDate(item.createTime)
                            }}
                        </div>
                    </div>
                    <van-empty v-if="list.length == 0" :description="$t('暂无数据')" />
                </div>
            </van-list>
        </van-pull-refresh>
    </div>
</template>
<script>
import {
    ImagePreview,
    NavBar,
    List,
    PullRefresh,
    Icon,
    Picker,
    popup,
    Tab,
    Tabs,
    Field,
    CellGroup,
    Rate,
    Empty
} from "vant";
import { getEvaluationList, apiEvaluationCountType } from "@/API/commodity";
import { getStorage, formatZoneDate } from "@/utils/utis";
export default {
    data() {
        return {
            formatZoneDate,
            itemName: process.env.VUE_APP_ITEM_NAME,
            mainColor: process.env.VUE_APP_MAIN_COLOR,
            sort_index: '',
            list: [],
            page_no: 0,
            refreshing: false,
            loading: false,
            finished: false,
            evaluationNum: 0,
            defaultAvatar: require('@/assets/image/default_avatar.png'),
            havePicture: '0',
            mediumReview: '0',
            negativeComment: '0',
            positiveComments: '0',
            ImagePreview,
            isEn: getStorage('lang') == 'en',
        };
    },
    components: {
        [NavBar.name]: NavBar,
        [List.name]: List,
        [PullRefresh.name]: PullRefresh,
        [Icon.name]: Icon,
        [Picker.name]: Picker,
        [popup.name]: popup,
        [Tab.name]: Tab,
        [Tabs.name]: Tabs,
        [Field.name]: Field,
        [CellGroup.name]: CellGroup,
        [Rate.name]: Rate,
        [Empty.name]: Empty,
    },
    created() {
        this.list = [
            // {createTime:'12:00',content:132,rating:3.5,partyName:'娃哈哈哈哈哈'}
        ];
        // 获取中评差评数量
        apiEvaluationCountType({ goodId: this.$route.query.sellerGoodsId }).then(res => {
            const { havePicture, mediumReview, negativeComment, positiveComments } = res
            this.havePicture = havePicture
            this.mediumReview = mediumReview
            this.negativeComment = negativeComment
            this.positiveComments = positiveComments
        })
        this.getList();
    },
    methods: {

        handleList(item) {
            const arr = []
            Object.keys(item).forEach(key => {
                if (key.indexOf('imgUrl') !== -1 && item[key]) {
                    arr.push(item[key])
                }
            })
            return arr
        },
        getList() {
            this.page_no++;
            let dataJson = {
                sellerGoodsId: this.$route.query.sellerGoodsId,
                pageNum: this.page_no,
                pageSize: 10,
                evaluationType: this.sort_index
            };
            getEvaluationList(dataJson).then((res) => {
                this.evaluationNum = res.evaluationNum;
                for (let i = 0; i < res.pageList.length; i++) {
                    this.list.push(res.pageList[i]);
                }
                this.list = this.list.map(item => {
                    const images = [item.imgUrl1, item.imgUrl2, item.imgUrl3, item.imgUrl4, item.imgUrl5, item.imgUrl6, item.imgUrl7, item.imgUrl8, item.imgUrl9]
                    return {
                        ...item,
                        images: images.filter(url => (!!url))
                    }
                })
                this.loading = false;

                if (res.pageList.length == 0) {
                    this.finished = true;
                }
            });
        },
        onRefresh() {
            // 清空列表数据
            this.finished = false;
            this.page_no = 0;
            // 重新加载数据
            // 将 loading 设置为 true，表示处于加载状态
            this.loading = true;
            this.onLoad();
        },
        onLoad() {
            if (this.refreshing) {
                this.list = [];
                this.refreshing = false;
            }
            this.getList();
        },
        onClickLeft() {
            this.$router.go(-1);
        },
    },
    watch: {
        sort_index() {
            this.list = []
            this.page_no = 0
            this.getList()
        }
    },
};
</script>
<style lang="scss" scoped>
.imgs {
    display: flex;
    flex-wrap: wrap;
    padding: 0 4%;

    img {
        width: 77px;
        height: 70px;
        margin-right: 15px;
        margin-top: 13px;

        &:nth-child(4n) {
            margin-right: 0;
        }
    }
}

.sort {
    width: 100vw;
    display: flex;
    align-items: center;
    justify-content: flex-start;
    margin: 13px 0;
    overflow-x: auto;
    scrollbar-width: none;
    -ms-overflow-style: none;
    font-size: 14px;
    padding: 0px 16px;
    transform: translateY(-5px);

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
            background: var(--main-color);
            color: #fff;
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

.all-reviews {
    width: 100%;
    height: 100%;
    background: #fff;

    .top-total {
        font-size: 14px;
        padding: 10px 16px;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }



    .reviews-list {
        padding: 0 4%;
        width: 100%;
        background: #fff;
        display: flex;
        flex-direction: column;
        justify-content: flex-start;
        align-items: center;

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
                    font-size: 12px;
                    margin-left: 10px;
                    width: 100px;
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
                transform: translateY(-10px);

                span {
                    margin-left: 20px;

                    color: var(--main-color);
                    font-size: 12px;
                }

                .sku {
                    // margin-top: 5px;
                    // margin-bottom: 5px;

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
                padding: 0 8% 0 4%;
                box-sizing: border-box;
                // display: -webkit-box;
                // -webkit-box-orient: vertical;
                // -moz-box-orient: vertical;
                // box-orient: vertical;
                // -webkit-line-clamp: 2;
                // line-clamp: 2;
                overflow: hidden;
                text-overflow: ellipsis;
                word-break: break-word;
            }
        }
    }
}
</style>
