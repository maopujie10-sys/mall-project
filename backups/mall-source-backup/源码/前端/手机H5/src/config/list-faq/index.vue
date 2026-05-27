<template>
<div class="list-faq">
    <ioe-title title="相关问题"/>
    <van-collapse v-model="activeNames">
        <van-collapse-item :title="item.title" :name="item.id" v-for="item in list" :key="item.id">
            <ul class="flex flex-col">
                <li v-for="(_item, _index) in item.content" :key="_index" class="mb-32">{{_item}}</li>
            </ul>
        </van-collapse-item>
    </van-collapse>
</div>
</template>

<script>
import IoeTitle from '@/components/ioe-title'
import { Collapse, CollapseItem } from 'vant';
export default {
    name: 'ListFaq',
    components: {
        IoeTitle,
        [Collapse.name]: Collapse,
        [CollapseItem.name]: CollapseItem
    },
    data() {
        return {
            list: [
                { id: 1, title: '1.在數字交易平台上能做什麼？', content: ['您可以在本平台上執行兩項操作 *數字貨幣永續合約交易 *挖礦交易。']},
                { id: 2, title: '2.DeFi挖礦它安全嗎？', content: ['1. 簡單易用：參與DeFi 挖礦無需管理私鑰、獲取資源、運行交易等複雜操作，一站式服務讓用戶只需要擁有鏈上錢包即可獲取豐厚的線上獎勵。', '2. 資產安全：精選行業內優秀DeFi項目，在產品運作期間對DeFi系統實時監測，降低項目風險。', '3. 更高收益：DeFi 挖礦為用戶免去了高昂的資源交易費，通過最優方式在同等盈利下為客戶提供最大回報。']},
                { id: 3, title: '3.如何加入？', content: ['加入安全的矿池空投节点，您只需要支付ETH矿工费就可以免费领取一个节点，一个ETH钱包地址只能领取一次。']}
            ],
            activeNames: [1]
        }
    }
}
</script>