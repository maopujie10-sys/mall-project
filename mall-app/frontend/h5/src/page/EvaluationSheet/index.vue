<template>
    <div class="evaluation-sheet">
        <van-nav-bar safe-area-inset-top fixed :title="$t('评价')" left-arrow @click-left="onClickLeft" />
        <div style="width: 100%;" class="h46"></div>
        <div class="evaluation-sheet-list">
            <div v-for='item in list' :key="item.key" class="sheet-item">
                <div class="top">
                    <img :src="item.goodsIcon" class="img">
                    <div class="describe">
                        <div class="name">{{ item.goodsName?.length > 27 ? (item.goodsName.slice(0, 27) + '...') :
                            item.goodsName }}</div>
                        <!-- <div class="price">$1.5</div> -->
                        <van-rate class="rate-wrap" v-model="item.value" :size="15" :color="mainColor" void-icon="star"
                            void-color="#eee" />
                    </div>

                </div>

                <van-cell-group inset>
                    <van-field type="textarea" rows="3" v-model="item.sheet" placeholder="Please rate the prodict..."
                        class="sheet-input" />
                </van-cell-group>
            </div>
        </div>
        <div class="bottom-div">
            <van-button type="primary" color="rgba(233,157,56,1)" block class="button">{{ $t('提交评论') }}</van-button>
        </div>
    </div>
</template>
<script>
import { NavBar, List, PullRefresh, Icon, Picker, popup, Tab, Tabs, Field, CellGroup, Button, Rate } from 'vant';
import { evaluationAdd } from "@/API/commodity";
import {
    orderListGoods
} from '@/API/user'
export default {
    data() {
        return {
            mainColor: process.env.VUE_APP_MAIN_COLOR,
            list: []
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
        [Button.name]: Button,
        [Rate.name]: Rate
    },
    created() {
        this.getOrderListGoods()
    },
    methods: {
        onClickLeft() {
            this.$router.go(-1)
        },
        getOrderListGoods() {
            let data = {
                orderId: this.$route.query.id
            }
            orderListGoods(data).then((res) => {
                this.list = res.pageList
                for (let i = 0; i < array.length; i++) {
                    const element = list[i];
                    this.$set(element, 'value', 0)
                    this.$set(element, 'sheet', '')
                }
            })
        },
        //评价
        evaluationAdd() {

        }
    },
};
</script>
<style lang="scss" scoped>
.evaluation-sheet {
    width: 100%;
    height: 100%;
    background: #f5f5f7;

    .evaluation-sheet-list {
        height: 70%;
        overflow: scroll;
        display: flex;
        flex-direction: column;
        justify-content: flex-start;
        align-items: center;
        margin-top: 10px;

        .sheet-item {
            margin-bottom: 30px;
            background: #FFFFFF;
            margin: 0 15px;
            margin-top: 15px;
            padding: 15px 0;
            width: 92%;

            .top {
                display: flex;
                justify-content: space-around;
                align-items: center;
                padding: 10px;

                .img {
                    width: 80px;
                    height: auto;
                }

                .describe {
                    width: 70%;

                    .name {
                        font-size: 14px;
                        display: inline-block;


                        display: -webkit-box;
                        -webkit-box-orient: vertical;
                        -moz-box-orient: vertical;
                        box-orient: vertical;
                        -webkit-line-clamp: 2;
                        line-clamp: 2;
                        // overflow: hidden;
                        text-overflow: ellipsis;
                    }

                    .price {

                        color: var(--main-color);
                        font-size: 16px;
                        margin-top: 10px;
                    }
                }
            }

            .sheet-input {
                border: 1px solid rgba(238, 238, 238, 1);
                border-radius: 10px;
            }
        }
    }

    .bottom-div {
        margin-top: 15%;
        padding: 0 5%;

        .button {
            border-radius: 4px;
        }
    }
}</style>
