<template>
    <div class="rechargeList">
        <van-nav-bar safe-area-inset-top fixed :title="itemName == 'Hive' ? $t('加值') : $t('充值')" :right-text="$t('记录')"
            @click-right="onClick1" left-arrow @click-left="onClickLeft" />
        <div style="width: 100%;" class="h46"></div>
        <img class="bj" src="@/assets/image/Recharge/beijing.png" />
        <div class="tishi">
            {{ $t('请如实填写实际转账金额，否则可能导致系统审核无法通过，影响充值进度。') }}
        </div>
        <router-link :to="`/recharge?type=${item.value}`" v-for="(item, index) of withdrawalMethod" :key="index">
            <div class="chongzhi-fs">
                <img class="chongzhi-logo" :src="getImagePath(item.value.toLowerCase())" />
                <div class="chongzhi-title">{{ item.value }}</div>
                <img class="chongzhi-right" src="@/assets/image/Recharge/arrow_right.png" />
            </div>
        </router-link>
        <!-- <router-link to="/recharge?type=USDT" v-if="!['FamilyShop'].includes(itemName)">
            <div class="chongzhi-fs">
                <img class="chongzhi-logo" src="@/assets/image/Recharge/usdt.png" />
                <div class="chongzhi-title">USDT</div>
                <img class="chongzhi-right" src="@/assets/image/Recharge/arrow_right.png" />
            </div>
        </router-link> -->
        <!-- <router-link to="/recharge?type=USDC" v-if="itemName === 'FamilyShop'">
            <div class="chongzhi-fs">
                <img class="chongzhi-logo" src="@/assets/image/Recharge/usdc.png" />
                <div class="chongzhi-title">USDC</div>
                <img class="chongzhi-right" src="@/assets/image/Recharge/arrow_right.png" />
            </div>
        </router-link> -->
        <!-- <router-link to="/recharge?type=BNB" v-if="itemName === 'FamilyShop'">
            <div class="chongzhi-fs">
                <img class="chongzhi-logo" src="@/assets/image/Recharge/bnb.png" />
                <div class="chongzhi-title">BNB</div>
                <img class="chongzhi-right" src="@/assets/image/Recharge/arrow_right.png" />
            </div>
        </router-link> -->
        <!-- <router-link to="/recharge?type=ETH" v-if="!['Inchoi'].includes(itemName)">
            <div class="chongzhi-fs">
                <img class="chongzhi-logo" src="@/assets/image/Recharge/eth.png" />
                <div class="chongzhi-title">ETH</div>
                <img class="chongzhi-right" src="@/assets/image/Recharge/arrow_right.png" />
            </div>
        </router-link>
        <router-link to="/recharge?type=BTC" v-if="!['Inchoi', 'FamilyShop'].includes(itemName)">
            <div class="chongzhi-fs">
                <img class="chongzhi-logo" src="@/assets/image/Recharge/btc.png" />
                <div class="chongzhi-title">BTC</div>
                <img class="chongzhi-right" src="@/assets/image/Recharge/arrow_right.png" />
            </div>
        </router-link> -->
        <router-link to="/customerServiceIndex?path=customerService">
            <div class="chongzhi-fs">
                <img class="chongzhi-logo" src="@/assets/image/Recharge/yinhangka.png" />
                <div class="chongzhi-title">{{ $t('银行卡') }}</div>
                <img class="chongzhi-right" src="@/assets/image/Recharge/arrow_right.png" />
            </div>
        </router-link>
        <!-- <router-link to="/bank-card" v-if="['Shop2u', 'EShop'].includes(itemName)">
            <div class="chongzhi-fs">
                <img class="chongzhi-logo" src="@/assets/image/Recharge/yinhangka.png" />
                <div class="chongzhi-title">{{ $t('银行卡') }}</div>
                <img class="chongzhi-right" src="@/assets/image/Recharge/arrow_right.png" />
            </div>
        </router-link> -->
        <!--  -->


        <!--  -->
        <!-- <router-link to="/bank-card?type=GCashPay" v-if="['Shop2u', 'EShop'].includes(itemName)">
            <div class="chongzhi-fs">
                <img class="chongzhi-logo" src="@/assets/image/Recharge/gcash.png" />
                <div class="chongzhi-title">GCashPay</div>
                <img class="chongzhi-right" src="@/assets/image/Recharge/arrow_right.png" />
            </div>
        </router-link>
        <router-link to="/bank-card?type=gcash" v-if="['Shop2u', 'EShop'].includes(itemName)">
            <div class="chongzhi-fs">
                <img class="chongzhi-logo" src="@/assets/image/Recharge/gcash.png" />
                <div class="chongzhi-title">Gcash</div>
                <img class="chongzhi-right" src="@/assets/image/Recharge/arrow_right.png" />
            </div>
        </router-link>
        <router-link to="/bank-card?type=gcash2" v-if="['Shop2u', 'EShop'].includes(itemName)">
            <div class="chongzhi-fs">
                <img class="chongzhi-logo" src="@/assets/image/Recharge/gcash.png" />
                <div class="chongzhi-title">Gcash2.0</div>
                <img class="chongzhi-right" src="@/assets/image/Recharge/arrow_right.png" />
            </div>
        </router-link>
        <router-link to="/bank-card?type=gcash3" v-if="['Shop2u', 'EShop'].includes(itemName)">
            <div class="chongzhi-fs">
                <img class="chongzhi-logo" src="@/assets/image/Recharge/gcash.png" />
                <div class="chongzhi-title">Gcash3.0</div>
                <img class="chongzhi-right" src="@/assets/image/Recharge/arrow_right.png" />
            </div>
        </router-link>
        <router-link to="/bank-card?type=Maya" v-if="['Shop2u', 'EShop'].includes(itemName)">
            <div class="chongzhi-fs">
                <img class="chongzhi-logo" src="@/assets/image/Recharge/maya.png" />
                <div class="chongzhi-title">Maya</div>
                <img class="chongzhi-right" src="@/assets/image/Recharge/arrow_right.png" />
            </div>
        </router-link> -->
        <div v-for="item of threePartyRecharge" :key="item.name">
            <router-link :to="`/bank-card?type=${item.name}&min=${item.min}&max=${item.max}`"
                v-if="['Shop2u', 'EShop'].includes(itemName)">
                <div class="chongzhi-fs">
                    <img class="chongzhi-logo" :src="images[item.name]" />
                    <div class="chongzhi-title">{{ item.name == 'Bank' ? $t('银行卡') : item.name }}</div>
                    <img class="chongzhi-right" src="@/assets/image/Recharge/arrow_right.png" />
                </div>
            </router-link>
        </div>

    </div>
</template>
<script>
import { zhifutongdao_post } from '@/API/user'
import { apigetCoinList } from '@/API/common'
import { deduplication } from '@/utils/utis'
import { Toast } from 'vant'
export default {
    data() {
        return {
            itemName: process.env.VUE_APP_ITEM_NAME,
            withdrawalMethod: [],
            threePartyRecharge: [],
            images: {
                'GCash': require('@/assets/image/Recharge/gcash.png'),
                'Maya': require('@/assets/image/Recharge/maya.png'),
                'GCash2.0': require('@/assets/image/Recharge/gcash.png'),
                'GCash3.0': require('@/assets/image/Recharge/gcash.png'),
                'GCash pay': require('@/assets/image/Recharge/gcash.png'),
                'Bank': require('@/assets/image/Recharge/yinhangka.png'),
            }
        }
    },
    created() {
        Toast.loading({
            message: this.$t('加载中...'),
            forbidClick: true,
            duration: 0
        });
        if(this.itemName == 'Shop2u') this.handleGcashQuery()
        zhifutongdao_post({}).then(res => {
            const tempArr = res.map(item => ({ label: item.coin, value: item.coin }))
            this.withdrawalMethod = deduplication(tempArr, 'value')
            Toast.clear()
        })
    },
    methods: {
        onClickLeft() {
            this.$router.push({ path: '/me', dir: 'left' })
        },
        onClick1() {
            this.$router.push({ path: '/rechargeRecord' })
        },
        getImagePath(path) {
            return require(`@/assets/image/Recharge/${path}.png`)
        },
        async handleGcashQuery() {
            const data = await apigetCoinList()
            this.threePartyRecharge = data.map(item => ({
                name: item.productType,
                min: item.range[0].min_amount,
                max: item.range[0].max_amount
            }))
        }
    }
}
</script>
<style lang="scss" scoped>
.rechargeList {
    width: 100%;
    height: 100%;

    .bj {
        width: 100%;
    }

    .tishi {
        margin-top: 13px;
        margin-left: 15px;
        margin-right: 15px;
        padding: 13px 11px;
        box-sizing: border-box;
        background: #F6F6F6;
        border-radius: 4px;
        font-style: normal;
        font-weight: 400;
        font-size: 14px;
        color: #999999;
    }

    .chongzhi-fs {
        margin-top: 15px;
        width: 100%;
        padding: 11px 15px;
        box-sizing: border-box;
        display: flex;
        justify-content: center;
        align-items: center;

        .chongzhi-logo {
            width: 28px;
            height: 28px;
            margin-right: 10px;
            border-radius: 50%;
        }

        .chongzhi-title {
            flex: 1;
            font-style: normal;
            font-weight: 400;
            font-size: 14px;
            color: #333333;
        }

        .chongzhi-right {
            width: 18px;
            height: 18px;
        }
    }
}
</style>
<style></style>