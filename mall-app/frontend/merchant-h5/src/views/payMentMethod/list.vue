<template>
    <div class="list pb-20">
        <fx-header fixed>
            <template #title>收款方式</template>
        </fx-header>
        <ul class="">
            <li class="flex px-4 justify-between pt-5 pb-10">
                <div class="bank-after pl-4 ">
                    <div class="bank-name">银行卡</div>
                    <div class="py-2">James</div>
                    <div class="bank-no">4367 4214 2048 9044 633</div>
                </div>
                <div @click="editInfo">
                    <img class="edit-img" src="../../assets/image/Record/edit.png" />
                </div>
            </li>
            <li class="flex px-4 justify-between  pt-5 pb-10">
                <div class="AI-after pl-4 ">
                    <div class="bank-name">AI-Rafidain QiServices</div>
                    <div class="py-2">James</div>
                    <div class="bank-no">4367 4214 2048 9044 633</div>
                </div>
                <div @click="editInfo">
                    <img class="edit-img" src="../../assets/image/Record/edit.png" />
                </div>
            </li>
        </ul>
        <div class="px-4 pt-6 fixed-wrap">
            <van-button class="w-full" type="primary" @click="submit">添加收款方式</van-button>
        </div>
    </div>

</template>

<script setup>
import { onBeforeMount, ref } from 'vue';
import { useRoute, useRouter } from 'vue-router';

const route = useRoute()
const router = useRouter()
const submit = () => {
    router.push('selectPay')
}
const editInfo = () => {
    router.push('add')
}
</script>
<style lang="scss" scoped>
.list {
    padding-top: var(--van-nav-bar-height);
    color: #21262F;

    ul {
        position: relative;

        li {
            background: #fff;
            border-bottom: 1px solid #EAEBEE;
            position: relative;

            .edit-img {
                width: 17px;
                height: 17px;
            }

            .bank-no {
                font-size: 18px;
                font-weight: bold;
                letter-spacing: 1px;
            }

            .bank-name {
                font-size: 16px;
            }
        }

        .bank-after::after {
            width: 4px;
            height: 15px;
            background: #E7BB41;
            content: '';
            position: absolute;
            left: 15px;
            top: 25px;
        }

        .AI-after::after {
            width: 4px;
            height: 15px;
            background: #4BA6EB;
            content: '';
            position: absolute;
            left: 15px;
            top: 25px;
        }
    }

    .fixed-wrap {
        position: fixed;
        bottom: 0;
        height: 115px;
        background: #fff;
        width: 100%;
    }
}
</style>