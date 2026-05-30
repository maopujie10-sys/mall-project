<template>
  <div class="checkout-page fade-in">
    <h2>确认订单</h2>
    <div class="checkout-layout">
      <div class="checkout-main">
        <div class="card section">
          <h3>收货地址</h3>
          <div v-if="addresses.length">
            <div v-for="addr in addresses" :key="addr.id" class="addr-row" :class="{ selected: selectedAddr === addr.id }" @click="selectedAddr = addr.id">
              <el-radio v-model="selectedAddr" :value="addr.id">{{ addr.contact }} {{ addr.mobile }}</el-radio>
              <span class="addr-detail">{{ addr.province }}{{ addr.city }}{{ addr.district }} {{ addr.address }}</span>
            </div>
          </div>
          <p v-else class="text-muted">请先添加收货地址</p>
        </div>
        <div class="card section">
          <h3>商品清单</h3>
          <div v-for="item in items" :key="item.id" class="goods-row">
            <img :src="item.image" class="goods-img" />
            <span class="goods-name">{{ item.name }}</span>
            <span class="goods-price">¥{{ item.price }} × {{ item.quantity || 1 }}</span>
          </div>
        </div>
      </div>
      <div class="checkout-sidebar">
        <div class="card summary-card">
          <h3>订单摘要</h3>
          <div class="summary-row"><span>商品合计</span><span>¥{{ subtotal }}</span></div>
          <div class="summary-row"><span>运费</span><span>¥{{ shipping }}</span></div>
          <div class="summary-row summary-total"><span>应付总额</span><span class="total-price">¥{{ total }}</span></div>
          <button class="btn btn-primary btn-lg submit-btn" @click="submitOrder">提交订单</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { getAddressList } from '@/api/user'
import { getCartList } from '@/api/cart'
import { createOrder } from '@/api/orders'

const router = useRouter()
const addresses = ref([])
const selectedAddr = ref(null)
const items = ref([])
const shipping = ref(0)

const subtotal = computed(() => items.value.reduce((s, i) => s + (i.price || 0) * (i.quantity || 1), 0).toFixed(2))
const total = computed(() => (parseFloat(subtotal.value) + parseFloat(shipping.value)).toFixed(2))

async function submitOrder() {
  if (!selectedAddr.value) { ElMessage.warning('请选择收货地址'); return }
  try {
    await createOrder({ addressId: selectedAddr.value, items: items.value.map(i => ({ goodsId: i.goodsId, skuId: i.skuId, quantity: i.quantity })) })
    ElMessage.success('下单成功')
    router.push('/pc/order')
  } catch (e) { ElMessage.error('下单失败') }
}

onMounted(async () => {
  try { const a = await getAddressList(); addresses.value = (a.data || a).list || [] } catch {}
  try { const c = await getCartList(); items.value = ((c.data || c).list || []).filter(i => i.checked) } catch {}
})
</script>

<style scoped>
.checkout-page { padding: 24px 0; }
.checkout-layout { display: grid; grid-template-columns: 1fr 360px; gap: 24px; }
.section { margin-bottom: 16px; padding: 24px; }
.section h3 { margin-bottom: 16px; }
.addr-row { padding: 10px 0; cursor: pointer; }
.addr-detail { font-size: 13px; color: var(--text-muted); margin-left: 24px; display: block; }
.goods-row { display: flex; align-items: center; gap: 12px; padding: 10px 0; border-bottom: 1px solid var(--border-color); }
.goods-img { width: 60px; height: 60px; border-radius: 8px; object-fit: cover; }
.goods-name { flex: 1; font-size: 14px; }
.goods-price { font-weight: 600; }
.summary-card { position: sticky; top: 80px; }
.summary-row { display: flex; justify-content: space-between; padding: 8px 0; font-size: 14px; }
.summary-total { border-top: 2px solid var(--border-color); padding-top: 12px; margin-top: 8px; font-size: 16px; font-weight: 700; }
.total-price { color: var(--color-danger); font-size: 22px; }
.submit-btn { width: 100%; margin-top: 16px; }
@media (max-width: 768px) { .checkout-layout { grid-template-columns: 1fr; } }
</style>
