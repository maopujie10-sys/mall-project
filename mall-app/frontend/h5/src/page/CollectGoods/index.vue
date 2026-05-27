<template>
    <div class="page-content">
        <van-nav-bar safe-area-inset-top fixed :title="$t('商品收藏')" left-arrow @click-left="() => $router.back()" />
        <div style="width: 100%;" class="h46"></div>
        <van-pull-refresh class="pull-content" v-model="refreshing" @refresh="onRefresh" :pulling-text="$t('下拉即可刷新')"
            :loosing-text="$t('释放即可刷新')" :loading-text="$t('加载中')">
            <van-list v-model="loading" :finished="finished" :finished-text="list.length ? $t('没有更多了') : ''"
                @load="onLoad" :loading-text="$t('加载中')">
                <div v-if="list.length" class="list-content">
                    <!-- <goods-item-two v-for="item in list" :key="item.sellerGoodsId" :goods-data="item" /> -->
                    <van-swipe-cell v-for="item in list" :key="item.sellerGoodsId">
                        <goods-item-two :goods-data="item" />
                        <template #right>
                            <div class="btn" @click.stop="delHandle(item)">{{ $t('删除') }}</div>
                        </template>
                    </van-swipe-cell>
                </div>
                <van-empty v-else :description="$t('暂无数据')" />
            </van-list>
        </van-pull-refresh>
    </div>
</template>

<script>
import { NavBar, List, PullRefresh, Empty, SwipeCell } from 'vant';
import GoodsItemTwo from '@/components/GoodsItemTwo/index.vue'
import { isLogin } from '@/utils/utis'
import {
    keepGoodsList
} from '@/API/user'
import { keepGoodsDel } from "@/API/commodity";
export default {
    name: 'CollectGoods',
    components: {
        [NavBar.name]: NavBar,
        [List.name]: List,
        [Empty.name]: Empty,
        [SwipeCell.name]: SwipeCell,
        [PullRefresh.name]: PullRefresh,
        GoodsItemTwo
    },
    data() {
        return {
            list: [],
            loading: false,
            finished: false,
            refreshing: false,
            pageNum: 1,
            pageSize: 10
        }
    },
    created() {
        if (!isLogin()) {
            this.$router.push('/')
        }
        // this.onLoad();
    },
    methods: {
        onRefresh() {
            // 清空列表数据
            this.finished = false;
            this.pageNum = 1
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
            this.getTableList()
        },
        getTableList() {
            const params = {
                pageNum: this.pageNum,
                pageSize: this.pageSize
            }

            keepGoodsList(params).then(res => {
                const { pageList } = res
                console.log(`pageList ::->`, pageList);
                this.list = this.pageNum === 1 ? pageList : [...this.list, ...pageList]
                this.pageNum++
                this.loading = false
                if (pageList.length < this.pageSize) {
                    this.finished = true
                }
                var obj = {};
                this.list = this.list.reduce((prev, cur) => {
                    obj[cur.id] ? "" : (obj[cur.id] = true && prev.push(cur));
                    return prev;
                }, []);
            }).catch(() => {
                this.loading = false
                this.finished = true
            })
        },
        delHandle(data) {
            this.refreshing = true
            keepGoodsDel({ sellerGoodsId: data.id }).then(() => {
                this.onRefresh()
            })
        }
    }
}
</script>

<style lang="scss" scoped>
.page-content {
    width: 100%;

    * {
        box-sizing: border-box;
    }

    .list-content {
        padding: 0 15px;
    }

    .pull-content {
        min-height: calc(100vh - 46px);
    }

    /deep/ .van-swipe-cell__right {
        display: flex;
        align-items: center;
        background-color: #fff;

        >.btn {
            height: 100%;
            width: 80px;
            display: flex;
            align-items: center;
            justify-content: center;
            color: #fff;
            font-size: 12px;
            // background-color: var(--main-color);
            background: var(--main-color);
        }
    }
}
</style>
