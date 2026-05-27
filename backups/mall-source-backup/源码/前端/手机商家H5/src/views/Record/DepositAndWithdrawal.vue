<template>
    <div class="Record pb-12">
        <fx-header fixed>
            <template #title>充提记录</template>
        </fx-header>
        <div class="tab-fixed">
            <van-tabs v-model:active="active" @click-tab="onClickTab">
                <van-tab v-for="(item, index) in tabList" :key="index" :title="item"></van-tab>
            </van-tabs>
        </div>
        <div class="list-wrap">
            <div class="tab-wrap flex px-4 mt-5">
                <div class="tab-item mr-4" :class="[selectIndexActive === index ? 'active' : '']"
                    v-for="(item, index) in tabListTwo" :key="index">{{ item }}</div>
            </div>
            <van-pull-refresh :loading-text="$t('加载中')" :loosing-text="$t('释放以刷新')" :pulling-text="$t('下拉以刷新')" v-model="loading" @refresh="onRefresh">
                <van-list v-model:loading="loading" :finished="finished" finished-text="没有更多了" @load="onLoad">
                    <ul>
                        <li class="px-4 mt-10" v-for="(item) in list" :key="index" @click="openDetails">
                            <div class="flex  justify-between">
                                <div class="type">USD</div>
                                <div class="money">2000</div>
                            </div>
                            <div class="flex mt-1 justify-between">
                                <div class="time">2022-03-11 17:55:12</div>
                                <div class="status flex">
                                    <div class="status-icon status-icon-color2 mr-2"></div>
                                    成功
                                </div>
                            </div>
                        </li>
                    </ul>
                </van-list>
            </van-pull-refresh>
        </div>
    </div>

</template>

<script setup>
import { onBeforeMount, ref } from 'vue';
import { useRoute, useRouter } from 'vue-router';

const route = useRoute()
const router = useRouter()
let active = ref(0)
let selectIndexActive = ref(0)
const list = ref([]);
const loading = ref(false);
const finished = ref(false);
const tabList = ['充值', '提现']
const tabListTwo = ['外汇货币', '数字货币']
const onClickTab = () => {
}
const onLoad = () => {
    // 异步更新数据
    // setTimeout 仅做示例，真实场景中一般为 ajax 请求
    setTimeout(() => {
        for (let i = 0; i < 10; i++) {
            list.value.push(list.value.length + 1);
        }

        // 加载状态结束
        loading.value = false;

        // 数据全部加载完成
        if (list.value.length >= 40) {
            finished.value = true;
        }
    }, 1000);
}
const openDetails = () => {
    router.push('RecordDetails')
}
</script>
<style lang="scss" scoped>
:deep(.van-tabs__line) {
    background: #2555F8;
}

:deep(.van-tab) {
    font-size: 16px;
}

.Record {
    padding-top: var(--van-nav-bar-height);
}

.tab-fixed {
    position: fixed;
    top: var(--van-nav-bar-height);
    width: 100%;
    z-index: 2;
}

.tab-wrap {
    .tab-item {
        width: 90px;
        height: 32px;
        text-align: center;
        line-height: 31px;
        color: #868D9A;
        border-radius: 20px;
    }

    .active {
        background: #2555F8;
        color: #fff;
    }
}

ul {
    li {
        .type {
            font-size: 18px;
        }

        .money {
            font-weight: bold;
        }

        .time {
            color: #868C9A;
        }

        .status {
            color: #868C9A;
            align-items: center;
        }
    }
}

.list-wrap {
    padding-top: var(--van-nav-bar-height);
}

.status-icon {
    width: 8px;
    height: 8px;
    border-radius: 50%;
}

.status-icon-color1 {
    background: #2EBD85;
}

.status-icon-color2 {
    background: #EA0F0F;
}

.status-icon-color3 {
    background: #F5D658;
}
</style>