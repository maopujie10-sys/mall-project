<template>
    <div class="RecordDetails pb-12">
        <fx-header>
            <template #title>充提详情</template>
        </fx-header>
        <div class="quantity mt-8">数量</div>
        <div class="money mt-8">
            <span>123,456,78.123</span> USDT
        </div>
        <div class="status flex mt-9">
            <div class="status-icon mr-2 status-bg3"></div> 充值成功
        </div>
        <div class="text mt-3">
            数字币已经充值成功。您可以在钱包账户中查看详情。
        </div>
        <ul class="px-4">
            <li class="flex mt-10 justify-between">
                <div class="ash">确认数</div>
                <div>12/12</div>
            </li>
            <li class="flex mt-10 justify-between">
                <div class="ash">充值账户</div>
                <div>钱包账户</div>
            </li>
            <li class="flex mt-10 justify-between">
                <div class="ash">转账网络</div>
                <div>USDT_TRC20</div>
            </li>
            <li class="flex mt-10 justify-between">
                <div class="ash">地址</div>
                <div class="flex">
                    <div class="address">TVPkt213sae3141412321ed21131e3141412</div><span class="copy"></span>
                </div>
            </li>
            <li class="flex mt-10 justify-between">
                <div class="ash">交易哈希</div>
                <div><span class="copy"></span></div>
            </li>
            <li class="flex mt-10 justify-between">
                <div class="ash">日期</div>
                <div>2022-03-17 15:39:04</div>
            </li>
            <li class="flex mt-10 justify-between">
                <div class="ash">备注</div>
                <div>充值金额不足</div>
            </li>
            <li class="flex mt-10 justify-between">
                <div class="ash">充值类型</div>
                <div>USD</div>
            </li>
            <li class="flex mt-10 justify-between">
                <div class="ash">银行账户</div>
                <div>6688 5544 2211 8866</div>
            </li>
            <li class="flex mt-10 justify-between">
                <div class="ash">开户行</div>
                <div>北京朝阳支行</div>
            </li>
        </ul>
    </div>

</template>

<script setup>
import { onBeforeMount, ref } from 'vue';
import { useRoute, useRouter } from 'vue-router';

const route = useRoute()
const router = useRouter()

</script>
<style lang="scss" scoped>
.RecordDetails {
    .quantity {
        color: #868D9A;
        text-align: center;
    }

    .money {
        font-size: 26px;
        text-align: center;

        span {
            font-weight: bold;
        }
    }

    .status {
        align-items: center;
        justify-content: center;
        font-size: 16px;
        color: #868D9A;

        .status-icon {
            width: 20px;
            height: 20px;
        }
    }

    .text {
        text-align: center;
        font-size: 14px;
        color: #868D9A;
    }

    .status-bg1 {
        background: url('@/assets/image/Record/icon1.png') no-repeat center;
        background-size: 100% 100%;
    }

    .status-bg2 {
        background: url('@/assets/image/Record/icon2.png') no-repeat center;
        background-size: 100% 100%;
    }

    .status-bg3 {
        background: url('@/assets/image/Record/icon3.png') no-repeat center;
        background-size: 100% 100%;
    }

    ul {
        li {
            .address {
                width: 200px;
                word-break: break-all;
                word-wrap: break-word;
            }

            .copy {
                display: block;
                width: 13px;
                height: 15px;
                background: url('@/assets/image/order/copy.png') no-repeat center;
                background-size: 100% 100%;
                margin-top: 4px;
            }
        }
    }

    .ash {
        color: #868C9A;
    }
}
</style>