<template>
    <div class="shop-item-content">
        <div class="info-content">
            <div class="poster"><img :src="shopData.avatar" alt="" /></div>
            <div class="info">
                <div class="name">{{ shopData.name }}</div>
                <!-- <div class="text"><span>{{ $t('已售') }}：</span> {{ shopData.soldNum || '0' }}</div> -->
                <div class="text">
                    <span>{{ $t("浏览量") }}：</span> {{ priceFormatInt(shopData.viewsNum) }}
                </div>
                <div class="text">
                    <span>{{ $t("好评率") }}：</span>
                    {{ Math.floor(shopData.highOpinion * 100) || 100 }}%
                </div>

                <!-- <div class="text"><span>{{ $t('分类') }}</span> {{ shopData.class }}</div>
        <div class="text"><span>{{ $t('商品') }}</span> {{ shopData.commodity }}</div>
        <div class="text"><span>{{ $t('关注') }}</span> {{ shopData.follow }}</div> -->
            </div>
            <div class="link" @click="openShop(shopData.id)">
                {{ $t("进入店铺") }}
                <img :src="arrow" alt="" />
            </div>
        </div>
        <div class="number-content">
            <!-- <p><span>{{ $t('好评率') }}</span>: {{ shopData.highOpinion }}</p> -->
            <p>
                <span>{{ $t("已售") }}</span>: {{ priceFormatInt(shopData.soldNum) }}
            </p>
        </div>
    </div>
</template>

<script>
import { priceFormatInt } from '@/utils/utis'
export default {
    name: "ShopItemOne",
    props: {
        shopData: {
            type: Object,
            required: true,
            default: function () {
                return {};
            },
        },
    },
    data() {
        return {
            priceFormatInt,
            arrow: require("@/assets/image/me/arrow3.png"),
        };
    },
    methods: {
        openShop(id) {
            this.$router.push({
                path: "/shop",
                query: {
                    sellerId: id,
                },
            });
        },
    },
};
</script>

<style lang="scss" scoped>
.shop-item-content {
    * {
        box-sizing: border-box;
    }

    margin-top: 10px;
    padding: 15px;
    border: 1px solid #eee;
    border-radius: 8px 0 0 8px;
    >.info-content {
        display: flex;
        align-items: center;

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
            flex: 1;
            width: 0;
            padding-left: 10px;
            padding-right: 5px;

            >.name {
                overflow: hidden;
                text-overflow: ellipsis;
                white-space: nowrap;
                font-size: 14px;
                margin-bottom: 6px;
            }

            >.text {
                font-size: 10px;
                color: #333;
                margin-bottom: 2px;

                &:last-child {
                    margin-bottom: 0;
                }
            }
        }

        >.link {
            padding: 0 6px;
            height: 20px;
            align-items: center;
            font-size: 12px;
            
            color: var(--main-color);
            background: #fcf2e2;
            border: 1px solid var(--main-color);
            border-radius: 20px;

            >img {
                width: 4px;
                height: auto;
            }
        }
    }

    >.number-content {
        width: 100%;
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding-top: 10px;
        border-top: 1px solid #eee;
        margin-top: 10px;

        >p {
            font-size: 10px;
            color: #333;
        }
    }
}</style>
