<template>
    <van-popup round :value="props.showPopup" @input="val => this.$emit('input', val)" :close-on-click-overlay="false"
        position="bottom">
        <div class="relative px-15 pt-23 px-4 pb-10">
            <div class="flex justify-end py-4 items-center">
                <img @click="onClose" class="z-20 w-8 h-8" src="./close.png" alt="" />
            </div>
            <h4 class="font-20 font-500 text-black title">确认订单</h4>
            <div class="flex flex-col justify-center">
                <p class="text-center mt-4">实际到账</p>
                <h2 class="font-bold text-base text-center mt-2 mb-2">123,456.12 USD</h2>
                <section v-for="(item, index) in infoList" :key="index">
                    <p class="mt-2">{{ item.title }}</p>
                    <ul class="mt-2 mb-4 border-b-1">
                        <li v-for="(_item, _index) in item.list" :key="_index" class="flex justify-between pt-1 pb-1">
                            <span class="ash">{{ _item.lable }}</span>
                            <span>{{ _item.value }}</span>
                        </li>
                    </ul>
                </section>
                <van-button type="primary" @click="onConfirm">确认订单</van-button>
            </div>
        </div>
    </van-popup>
</template>

<script setup>
const props = defineProps({
    showPopup: {
        type: Boolean,
        default: false
    }
})

const emits = defineEmits(['close'])

const infoList = [
    {
        title: '充值银行卡', list: [
            { lable: '银行名称', value: '美国银行' },
            { lable: '账户地址', value: '外汇账户' },
        ]
    },
    {
        title: '', list: [
            { lable: '货币', value: 'USD' },
            { lable: '金额', value: '123,456.12 USD' },
            { lable: '手续费', value: '1.0 USD' }
        ]
    }
]


const onClose = () => {
    emits('close')
}

const onConfirm = () => {
    console.log('confirm')
    onClose()
}
</script>
<style lang="scss" scoped>
.title {
    text-align: center;
    color: #1F2025;
    font-weight: bold;
    font-size: 20px;
}

.ash {
    color: #868D9A;
}

.money-title {
    font-size: 24px;
    font-weight: bold
}
</style>