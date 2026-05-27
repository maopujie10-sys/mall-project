<template>
    <div class="rechargeRecord" style="min-height: 100vh;">
        <van-nav-bar safe-area-inset-top fixed :title="$t('充值记录')" left-arrow @click-left="onClickLeft" />
        <div style="width: 100%;" class="h46"></div>
        <div class="nr">
            <!--/*      <div style="width: 100%;height: 1px;background: #F6F6F6;margin-left: 50px;"></div>*/-->
            <van-pull-refresh style="min-height: 100vh;" v-model="refreshing" @refresh="onRefresh"
                :pulling-text="$t('下拉即可刷新')" :loosing-text="$t('释放即可刷新')" :loading-text="$t('加载中')">
                <van-list v-model="loading" :finished="finished" :loading-text="$t('加载中')"
                    :finished-text="list.length ? $t('没有更多了') : ''" @load="onLoad">
                    <!--          <div >{{ item }}</div>-->
                    <template v-if="list.length">
                        <div class="" v-for="(item, index) in list" :key="index">
                            <div class="liebiao" @click="openDeital(item.order_no, item.state == 2 && item.failure_msg)">
                                <div class="pinglie">
                                    <div class="l1">{{ $t('订单号') }}</div>
                                    <div class="r1" @click="copyData(item.order_no)">{{ item.order_no }}</div>
                                    <img @click.stop="copyData(item.order_no)" src="@/assets/image/me/fuzhi1.png"
                                        style="width: 10px;height: 10px;margin-left: 4px;" />
                                </div>
                                <div class="pinglie">
                                    <div class="l1">{{ $t('创建时间') }}</div>
                                    <div class="r1">{{ item.createTime }}</div>
                                </div>
                                <div class="pinglie">
                                    <div class="l1">{{ $t('充值数量') }}</div>
                                    <div class="r1 chulizhi">{{ item.volume > 1 ? priceFormat(item.volume) : item.volume }} {{ item.coin }}</div>
                                </div>
                                <div class="pinglie">
                                    <div class="l1">{{ $t('实际到账') }}</div>
                                    <div class="r1 chulizhi" v-if="priceFormat(item.amount)">
                                        {{ priceFormat(item.amount) }} USDT
                                    </div>
                                    <div class="r1 chulizhi" v-else>--</div>
                                </div>
                                <div class="pinglie">
                                    <div class="l1">{{ $t('状态') }}</div>
                                    <div class="r1 chulizhi" v-if="item.state == 0">{{ $t('处理中') }}</div>
                                    <div class="r1 chenggong" v-if="item.state == 1">{{ $t('成功') }}</div>
                                    <div class="r1 shibai" v-if="item.state == 2">{{ $t('失败') }}</div>
                                </div>
                                <div class="pinglie" v-if="item.state == 2">
                                    <div class="l1">{{ $t('失败原因') }}</div>
                                    <div class="r1 chulizhi">{{ item.failure_msg || '--' }}</div>
                                </div>
                            </div>
                        </div>
                        <div style="width: 100%;height: 1px;background: #F6F6F6;"></div>
                    </template>
                    <van-empty v-if="list.length == 0" :description="$t('暂无记录')" />
                </van-list>
            </van-pull-refresh>
        </div>
    </div>
</template>
<script>
import { NavBar, List, PullRefresh, Icon, Picker, popup, Toast, Empty } from 'vant';
import { chongzhijilu_post } from "@/API/user";
import { priceFormat } from '@/utils/utis'
export default {
    data() {
        return {
            list: [],
            loading: false,
            finished: false,
            refreshing: false,
            page_no: 0,
            content_type: 'brokerage',
            // columns: [this.$t('全部'), this.$t('recharge'), this.$t('withdraw'), this.$t('brokerage'), this.$t('sys-increment'), this.$t('sys-decrement'), this.$t('vip-recharge'), this.$t('freeze-order'), this.$t('unfreeze-order'), this.$t('pay-order'), this.$t('bonus')],
            columns2: ['', 'recharge', 'withdraw', 'brokerage', 'sys-increment', 'sys-decrement', 'vip-recharge', 'freeze-order', 'unfreeze-order', 'pay-order', 'bonus'],
            showPicker: false,
            shaixuan_index: 0,
            priceFormat
        };
    },
    components: {
        [NavBar.name]: NavBar,
        [List.name]: List,
        [PullRefresh.name]: PullRefresh,
        [Icon.name]: Icon,
        [Picker.name]: Picker,
        [Empty.name]: Empty,
        [popup.name]: popup
    },
    created() {
        // this.libiao_post()
    },
    methods: {
        copyData(ea) {
            //如果需要回调：
            this.$copyText(ea).then(e => {
                Toast(this.$t('复制成功'))
                console.log(e)
            }, function (e) {
                Toast(this.$t('复制失败'))
                console.log(e)
            })
        },
        onConfirm(value, index) {
            this.content_type = this.columns2[index]
            this.page_no = 0
            this.finished = false;
            this.libiao_post()
            this.showPicker = false
            this.list = [];
            // Toast(`当前值：${value}, 当前索引：${index}`);
        },
        onChange(picker, value, index) {
            // Toast(`当前值：${value}, 当前索引：${index}`);
            console.log(picker, value, index)
        },
        onCancel() {
            this.showPicker = false
            // Toast('取消');
        },
        onClickRight() {
            this.showPicker = true
        },
        libiao_post() {
            this.page_no++
            chongzhijilu_post({ page_no: this.page_no }).then(res => {
                // console.log(res)
                // for (let i = 0; i < res.length; i++) {
                //   this.list.push(res[i]);
                // }
                if (res.elements.length == 0) {
                    this.finished = true;
                } else {
                    this.loading = false;
                    this.list = [...this.list, ...res.elements]
                }
                var obj = {};
                this.list = this.list.reduce((prev, cur) => {
                    obj[cur.order_no] ? "" : (obj[cur.order_no] = true && prev.push(cur));
                    return prev;
                }, []);
                console.log(`this.list ::->`, this.list);
            })
        },
        onClickLeft() {
            this.$router.push({ path: '/rechargeList', dir: 'left' })
        },
        onLoad() {
            if (this.refreshing) {
                this.list = [];
                this.refreshing = false;
            }
            this.libiao_post()
        },
        onRefresh() {
            // 清空列表数据
            this.finished = false;
            this.page_no = 0
            // 重新加载数据
            // 将 loading 设置为 true，表示处于加载状态
            this.loading = true;
            this.onLoad();
        },
        openDeital(order_no, failure_msg) {
            this.$router.push({
                path: '/rechargeRecordDetails',
                query: {
                    order_no,
                    failure_msg
                }
            })
        }
    },
};
</script>
<style lang="scss" scoped>
.rechargeRecord {
    width: 100%;
    //height: 100%;
    min-height: 100%;
    background: #F5F5F7;

    * {
        box-sizing: border-box;
    }

    .nr {
        width: 100%;
        padding: 0 15px;
        box-sizing: border-box;

        .liebiao {
            margin-top: 7px;
            padding: 0 10px;
            width: 100%;
            background: #fff;

            .pinglie {
                padding: 15px 0;
                box-sizing: border-box;
                width: 100%;
                display: flex;
                justify-content: center;
                align-items: center;
                border-bottom: 1px solid #eee;

                &:last-child {
                    border-bottom: none;
                }

                .l1 {
                    flex: 1;
                    font-style: normal;
                    font-weight: 400;
                    font-size: 14px;
                    color: #000;
                }

                .r1 {
                    font-style: normal;
                    font-weight: 400;
                    font-size: 14px;
                    line-height: 16px;
                    text-align: end;

                    color: #000;

                }

                .chulizhi {
                    color: var(--main-color) !important;
                }

                .shibai {
                    color: #FF4141;
                }

                .chenggong {
                    color: #0ECB81;
                }
            }

        }
    }
}
</style>
