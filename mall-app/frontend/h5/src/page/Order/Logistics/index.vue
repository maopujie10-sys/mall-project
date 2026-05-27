<template>
    <div class="logistics">
        <van-nav-bar safe-area-inset-top fixed :title="$t('查看物流')" left-arrow @click-left="() => $router.back()" />
        <van-steps direction="vertical" :active="0">
            <van-step v-for="(item, index) of list" :key="index">
                <p class="log" v-html="item.log"></p>
                <p>{{ $formatZoneDate(item.updateTime) }}</p>
            </van-step>
        </van-steps>
    </div>
</template>

<script>
import { getLogisticsInformation } from '@/API/order'
import { isLogin } from '@/utils/utis'
export default {
    data() {
        return {
            list: []
        }
    },
    mounted() {
        const token = isLogin()
        const { id } = this.$route.query
        getLogisticsInformation({
            token,
            orderId: id
        }).then(res => {
            this.list = res.map(item => {
                const arr = item.log.split(id)
                return {
                    ...item,
                    log: `${this.$t('订单')}<span class="log_id">#${id}</span>${this.$t(arr[1] === '系统发货成功' ? '供应商发货成功' : arr[1])}`
                }
            }).reverse()
        })
    },
    methods: {
        formatTime(date) {
            date = new Date(date);
            let Y = date.getFullYear();
            let M = String(date.getMonth() + 1).padStart(2, '0');
            let D = String(date.getDate()).padStart(2, '0');
            let h = String(date.getHours()).padStart(2, '0');
            let m = String(date.getMinutes()).padStart(2, '0');
            let s = String(date.getSeconds()).padStart(2, '0');
            return `${M}/${D}/${Y} ${h}:${m}:${s}`
        }
    }
}
</script>

<style lang="scss" scoped>
.logistics {
    padding-top: 50px;

    // font-size: 16px;
    // min-height: 100vh;
    // background-color: #f5f5f7;
    :deep(.van-step--process) {
        p {
            
            color: var(--main-color);
        }
    }

    .log {
        
        margin-bottom: 2px;
    }

    .time {
        
        color: var(--main-color);
    }
}

:deep(.log_id) {
    color: #306ada !important;
}</style>
