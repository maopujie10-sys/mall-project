<template>
    <div class="goods-item" @click="openDetails">
        <div class="poster">
            <img :src="goodsData.imgUrl1 ||
                goodsData.imgUrl2 ||
                goodsData.imgUrl3 ||
                goodsData.imgUrl4 || $defaultGoodsImage
                " alt="" />
        </div>
        <div class="info">
            <div class="name">
                {{
                    goodsData.name?.length > 27
                    ? goodsData.name.slice(0, 27) + "..."
                    : goodsData.name
                }}
            </div>
            <div class="price">
                <p>${{ priceFormat(goodsData.sellingPrice) }}</p>
                <!-- <p v-if="Number(goodsData.discountPrice)" class="old"><span>{{ $t('原价') }}</span> {{ goodsData.discountPrice }}</p> -->
            </div>
            <p>
                <span>{{ $t("已售") }}</span> {{ goodsData.soldNum }}
            </p>
        </div>
    </div>
</template>

<script>
import { priceFormat } from "@/utils/utis";
export default {
    name: "GoodsItemTwo",
    props: {
        goodsData: {
            type: Object,
            required: true,
            default: function () {
                return {};
            },
        },
    },
    methods: {
        priceFormat(num) {
            return priceFormat(num);
        },
        openDetails() {
            this.$router.push({
                path: "/CommodityDetails",
                query: {
                    sellerGoodsId: this.goodsData.id,
                },
            });
        },
    },
};
</script>

<style lang="scss" scoped>
.goods-item {
    * {
        box-sizing: border-box;
    }

    display: flex;
    align-items: center;
    padding: 15px;
    border: 1px solid #eee;
    margin-top: 10px;
    border-radius: 8px 0 0 8px;
    >.poster {
        width: 63px;
        height: 63px;
        overflow: hidden;
        display: flex;
        align-items: center;
        justify-content: center;

        >img {
            width: 100%;
            height: auto;
        }
    }

    >.info {
        padding-left: 15px;
        flex: 1;

        >.name {
            overflow: hidden;
            text-overflow: ellipsis;
            display: -webkit-box;
            -webkit-box-orient: vertical;
            -moz-box-orient: vertical;
            box-orient: vertical;
            -webkit-line-clamp: 2;
            line-clamp: 2;
            font-size: 14px;
        }

        >.price {
            display: flex;
            align-items: center;
            margin-top: 10px;

            >p {
                font-size: 16px;
                font-weight: bold;
                font-size: 16px;
                color: var(--main-color);

                &.old {
                    font-weight: normal;
                    color: #999;
                    font-size: 12px;
                    margin-left: 20px;
                    text-decoration: line-through;
                }
            }
        }

        >p {
            color: #999;
            font-size: 11px;
            color: #999;
            margin-top: 10px;
        }
    }
}</style>
