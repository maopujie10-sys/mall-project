<template>
    <div class="addPay pb-10">
        <fx-header>
            <template #title>添加 Al-Rafidain QiServices</template>
        </fx-header>
        <van-form @failed="onFailed">
            <van-cell-group inset>
                <p class="pt-6 pb-2 ash">Name</p>
                <van-field class="select-item" v-model="value1" disabled name="pattern" placeholder="正则校验"
                    :rules="[{ pattern, message: '请输入正确内容' }]">
                    <template #extra>
                        <van-icon name="arrow-down" color="#878A96" size="18" />
                    </template>
                </van-field>
            </van-cell-group>

            <van-cell-group inset>
                <p class="pt-6 pb-2 ash">Phone Number</p>
                <van-field class="select-item" v-model="value1" clearable name="picker" placeholder="Phone Number"
                    :rules="[{ pattern, message: '请输入正确内容' }]">
                </van-field>
            </van-cell-group>
            <van-cell-group inset>
                <p class="pt-6 pb-2 ash">银行名称</p>
                <van-field class="select-item" v-model="value1" clearable name="picker" placeholder="Phone Number"
                    :rules="[{ pattern, message: '请输入正确内容' }]">
                </van-field>
            </van-cell-group>
            <van-cell-group inset>
                <p class="pt-6 pb-2 ash">Bank Account Number</p>
                <van-field class="select-item" v-model="value1" name="picker" clearable
                    placeholder="Bank Account Number" :rules="[{ pattern, message: '请输入正确内容' }]">
                </van-field>
            </van-cell-group>
            <van-cell-group inset>
                <p class="pt-6 pb-2 ash">开户支行（选填）</p>
                <van-field class="select-item" v-model="value1" name="picker" clearable placeholder="开户支行（选填）"
                    :rules="[{ pattern, message: '请输入正确内容' }]">
                </van-field>
            </van-cell-group>
            <van-cell-group inset>
                <p class="pt-6 pb-2 ash">Note（选填）</p>
                <van-field class="select-item-textarea" v-model="value1" type="textarea" name="picker" clearable
                    placeholder="Bank Account Number" :rules="[{ pattern, message: '请输入正确内容' }]">
                </van-field>
            </van-cell-group>
        </van-form>
        <div class="tips mx-4 mt-8 px-4 pt-4 pb-4">
            <div class="flex tip-title">
                <img class="mr-2" src="@/assets/image/Record/icon4.png" />
                特别提醒
            </div>
            <div class="pl-4 ash mt-2 font-13">请确保添加您的银行卡号进行即时付款。请勿包含其他银行或
                付款方式的详细信息。您必须添加所选银行的付款/收款信息。</div>
        </div>
        <div class="font-13 mt-20 ash px-4">温馨提示：当您出售数字货币时，您选择的收款方式将向买方展示，请
            确认信息填写准确无误。</div>
        <div class="px-4 pt-6 mt-3">
            <van-button class="w-full" type="primary" @click="submit">确认</van-button>
        </div>
    </div>

</template>

<script setup>
import { onBeforeMount, ref } from 'vue';
import { useRoute, useRouter } from 'vue-router';

const route = useRoute()
const router = useRouter()
let value1 = ref('法币')
const onFailed = (errorInfo) => {
    console.log('failed', errorInfo);
};
</script>
<style lang="scss" scoped>
.addPay {
    .select-item {
        background: #F5F5F5;
        padding: 0 15px;
        align-items: center;
        height: 50px;
        border-radius: 3px;
    }

    .select-item-textarea {
        background: #F5F5F5;
        padding: 0 15px;
        align-items: center;
        height: 120px;
        border-radius: 3px;
    }

    .ash {
        color: #868D9A;
    }

    .tips {
        background: #F0F1F4;
        border-radius: 3px;

        .tip-title {
            font-weight: bold;
            align-items: center;

            img {
                width: 20px;
                height: 20px;

            }
        }
    }
}
</style>