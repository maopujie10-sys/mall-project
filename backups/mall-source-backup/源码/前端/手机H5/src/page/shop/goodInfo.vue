<template>
    <div class="commodity">
        <div v-for="(item, index) in list" :key="index" class="list-item">
            <div class="list-item-content" @click="openDetails(item)">
                <div class="commodity-img">
                    <img :src="item.imgUrl1 || $defaultGoodsImage" fit="contain" />
                </div>
                <div class="goods-info">
                    <div class="money">
                        ${{
                            priceFormat(
                                item?.discountPrice ? item.discountPrice : item.sellingPrice
                            )
                        }}
                    </div>
                    <div class="text">{{ $t("卖出") }} {{ priceFormatInt(item.soldNum) }}</div>
                    <div class="page-views" v-if="itemName != 'SM-wholesaleShop'">
                        {{ $t("浏览量") }} {{ priceFormatInt(item.viewsNum) }}
                    </div>
                    <div class="title">
                        {{ $textOmit(item.name) }}
                    </div>
                </div>
                <!-- 活动折扣 -->
                <div class="discount_box" v-if="item.discountRatio >= 0.01">
                    <span>{{ (item.discountRatio * 100).toFixed(0) }}%</span>
                    <span>OFF</span>
                </div>
            </div>
        </div>
    </div>
</template>

<script>
import { isLogin, priceFormat, priceFormatInt } from "@/utils/utis";

export default {
    name: "goodInfo",
    props: {
        list: {
            type: Array,
            default: () => [],
        },
        index: {
            type: Number,
            default: 0
        }
    },
    data() {
        return {
            itemName: process.env.VUE_APP_ITEM_NAME,
        }
    },
    methods: {
        priceFormat,
        priceFormatInt,
        openDetails(item) {
            this.$router.push({
                path: "/CommodityDetails",
                query: {
                    sellerGoodsId: item.id
                },
            });
            //   if (isLogin()) {

            //   } else {
            //     this.$router.push('/login')
            //   }
        },
    },
};
</script>

<style scoped lang="scss">
.commodity {
    display: flex;
    flex-wrap: wrap;

    .list-item {
        width: 50%;
        box-sizing: border-box;
        position: relative;
        .list-item-content {
            display: flex;
            flex-direction: column;
            box-sizing: border-box;
            border: 1px solid #f2f2f2;
            border-radius: 4px;
            background-color: #ffffff;
            height: 268px;
            margin-bottom: 10px;
            justify-content: flex-start;
            align-items: center;

            .commodity-img {
                // width: 100%;
                // min-height: 0;
                height: 156px;
                // flex: 1;
                padding: 5px;
                display: flex;
                justify-content: center;
                align-items: center;

            }

            img {
                max-width: 100%;
                max-height: 100%;
            }

            .goods-info {
                width: 100%;
                height: 114px;
                overflow: hidden;
                flex-shrink: 0;
                padding: 0 12px;
                box-sizing: border-box;

                .money {
                    font-family: "Roboto";
                    font-style: normal;
                    font-weight: 500;
                    font-size: 16px;
                    line-height: 19px;
                    /* identical to box height */

                    color: var(--main-color);
                    margin-top: 8px;
                }

                .text {
                    font-family: "Roboto";
                    font-style: normal;
                    font-weight: 400;
                    font-size: 11px;
                    line-height: 13px;
                    /* identical to box height */
                    color: #999999;
                    margin-top: 4px;
                }

                .page-views {
                    font-family: "Roboto";
                    font-style: normal;
                    font-weight: 400;
                    font-size: 10px;
                    line-height: 13px;
                    /* identical to box height */
                    color: #999999;
                    margin-top: 2px;
                }

                .title {
                    margin-top: 5px;
                    overflow: hidden;
                    text-overflow: ellipsis;
                    display: -webkit-box;
                    -webkit-box-orient: vertical;
                    -moz-box-orient: vertical;
                    box-orient: vertical;
                    -webkit-line-clamp: 2;
                    line-clamp: 2;
                    /*! autoprefixer: off */
                    -webkit-box-orient: vertical;
                }
            }
        }

        &:nth-child(2n) {
            padding-left: 5px;
        }

        &:nth-child(2n + 1) {
            padding-right: 5px;
        }
    }
}
</style>
