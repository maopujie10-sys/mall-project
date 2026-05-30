<template>
  <div class="order-page">
    <h2 class="page-title">{{ $t('orders') }}</h2>

    <!-- Tab 切换 -->
    <van-tabs v-model:active="activeTab" sticky color="var(--color-primary)" title-active-color="var(--color-primary)" @change="loadOrders">
      <van-tab v-for="tab in tabs" :key="tab.value" :title="tab.label" />
    </van-tabs>

    <!-- 订单列表 -->
    <div class="order-list">
      <template v-if="orders.length">
        <div v-for="order in orders" :key="order.id || order.orderId" class="order-card" @click="goDetail(order)">
          <!-- 订单顶部 -->
          <div class="order-top">
            <span class="order-sn">{{ $t('order.orderNo') }}: {{ order.orderSn || order.id }}</span>
            <span class="order-status" :class="statusClass(order.status)">{{ statusText(order.status) }}</span>
          </div>

          <!-- 商品列表 -->
          <div class="order-goods">
            <div v-for="(goods, gi) in (order.goods || order.items || [])" :key="gi" class="order-goods-item">
              <div class="goods-img-wrap">
                <img :src="goods.image || goods.imgUrl || goods.img" class="goods-img" />
              </div>
              <div class="goods-info">
                <p class="goods-name">{{ textOmit(goods.name || goods.goodsName, 40) }}</p>
                <p class="goods-sku" v-if="goods.skuName">{{ goods.skuName }}</p>
                <div class="goods-price-row">
                  <span class="goods-price">${{ formatPrice(goods.price || goods.sellingPrice) }}</span>
                  <span class="goods-qty">x{{ goods.count || goods.quantity || 1 }}</span>
                </div>
              </div>
            </div>
          </div>

          <!-- 订单底部 -->
          <div class="order-bottom">
            <span class="order-total">
              {{ $t('common.total') }}: <b>${{ formatPrice(order.totalAmount || order.total || order.amount) }}</b>
            </span>
            <div class="order-actions">
              <button v-if="order.status === '0' || order.status === 'pending'" class="action-btn primary" @click.stop="goPay(order)">{{ $t('order.pay') }}</button>
              <button v-if="order.status === '3' || order.status === 'shipped'" class="action-btn primary" @click.stop="confirmReceipt(order)">{{ $t('order.received') }}</button>
              <button v-if="order.status === '4'" class="action-btn" @click.stop="goEvaluate(order)">{{ $t('order.evaluate') }}</button>
            </div>
          </div>
        </div>
      </template>

      <!-- 空状态 -->
      <van-empty v-if="!orders.length && !loading" :description="$t('common.noOrders')" />
    </div>

    <!-- 加载更多 -->
    <div v-if="loading" class="loading-tip">{{ $t('common.loading') }}</div>
    <div v-if="finished && orders.length" class="loading-tip">{{ $t('common.noMore') }}</div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { Tab as VanTab, Tabs as VanTabs, Empty as VanEmpty, showToast, showNotify } from 'vant'
import { useUserStore } from '@/stores/user'
import { orderListMain, orderReceipt, orderCancel } from '@/api/user'

const router = useRouter()
const route = useRoute()
const userStore = useUserStore()

const activeTab = ref(0)
const orders = ref([])
const loading = ref(false)
const finished = ref(false)
const pageNum = ref(1)

const tabs = [
  { label: '全部', value: 'all' },
  { label: '待付款', value: '0' },
  { label: '待发货', value: '1' },
  { label: '待收货', value: '3' },
  { label: '已完成', value: '4' }
]

const statusMap = {
  '0': '待付款', 'pending': '待付款',
  '1': '待发货', 'shipped': '待发货',
  '3': '待收货', 'received': '待收货',
  '4': '已完成', 'completed': '已完成',
  '5': '已取消', 'cancelled': '已取消',
  '6': '退款/售后', 'refund': '退款/售后'
}

function _toFixed(n, d) { n = n.toString(); const i = n.indexOf('.'); const s = i !== -1 ? n.substring(0, d + i + 1) : n.substring(0); return parseFloat(s).toFixed(d) }
function formatPrice(n) { if (!n || !Number(n)) return 0; const s = _toFixed(n, 2); const p = s.slice(0, s.indexOf('.')); const r = s.slice(s.indexOf('.') + 1); return `${p.replace(/(\d)(?=(\d{3})+(?!\d))/g, '$1,')}.${r.length < 2 ? r + '0' : r}` }
function textOmit(t, m = 48) { if (!t) return ''; return t.length > m ? t.slice(0, m) + '...' : t }
function statusText(s) { return statusMap[s] || s || '--' }
function statusClass(s) {
  if (['0', 'pending'].includes(s)) return 'pending'
  if (['3', '4', 'shipped', 'received', 'completed'].includes(s)) return 'done'
  if (['5', 'cancelled'].includes(s)) return 'cancelled'
  return ''
}

onMounted(() => {
  if (!userStore.token) { router.push('/m/login'); return }
  if (route.query.type) {
    const idx = tabs.findIndex(t => t.value === route.query.type)
    if (idx >= 0) activeTab.value = idx
  }
  loadOrders()
})

async function loadOrders() {
  loading.value = true
  finished.value = false
  pageNum.value = 1
  const tabVal = tabs[activeTab.value]?.value

  try {
    const params = { pageNum: 1, pageSize: 20 }
    if (tabVal !== 'all') params.status = tabVal
    const res = await orderListMain(params)
    orders.value = res.pageList || res.list || res.rows || res || []
    if ((orders.value || []).length < 20) finished.value = true
  } catch (e) {
    orders.value = []
    finished.value = true
  }
  loading.value = false
}

function goDetail(order) {
  router.push('/m/order/' + (order.id || order.orderId))
}

function goPay(order) {
  showToast('跳转支付...')
}

async function confirmReceipt(order) {
  try {
    await orderReceipt({ orderId: order.id || order.orderId })
    showToast('已确认收货')
    loadOrders()
  } catch (e) {}
}

function goEvaluate(order) {
  router.push('/m/order/' + (order.id || order.orderId))
}
</script>

<style scoped>
.order-page { min-height: 100vh; background: var(--bg-secondary); padding-bottom: 24px; }
.page-title { padding: 16px; font-size: 18px; font-weight: 700; color: var(--text-primary); }

.order-list { padding: 12px 14px; }

.order-card {
  background: var(--bg-primary); border-radius: var(--border-radius);
  box-shadow: var(--shadow-sm); margin-bottom: 12px;
  overflow: hidden; cursor: pointer;
  transition: box-shadow var(--transition-fast);
}
.order-card:hover { box-shadow: var(--shadow-md); }

.order-top {
  display: flex; justify-content: space-between; align-items: center;
  padding: 12px 16px; border-bottom: 1px solid var(--border-color);
}
.order-sn { font-size: 13px; color: var(--text-secondary); }
.order-status { font-size: 13px; font-weight: 500; }
.order-status.pending { color: var(--color-accent); }
.order-status.done { color: var(--color-success); }
.order-status.cancelled { color: var(--text-muted); }

.order-goods { padding: 8px 16px; }
.order-goods-item { display: flex; gap: 12px; padding: 8px 0; border-bottom: 1px solid var(--border-color); }
.order-goods-item:last-child { border-bottom: none; }

.goods-img-wrap { width: 64px; height: 64px; border-radius: var(--border-radius-sm); overflow: hidden; background: var(--bg-secondary); flex-shrink: 0; display: flex; align-items: center; justify-content: center; }
.goods-img { max-width: 100%; max-height: 100%; object-fit: contain; }

.goods-info { flex: 1; display: flex; flex-direction: column; min-width: 0; }
.goods-name { font-size: 13px; color: var(--text-primary); display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; }
.goods-sku { font-size: 11px; color: var(--text-muted); margin: 2px 0; }
.goods-price-row { display: flex; justify-content: space-between; align-items: center; margin-top: auto; }
.goods-price { font-size: 15px; font-weight: 600; color: var(--color-primary); }
.goods-qty { font-size: 12px; color: var(--text-muted); }

.order-bottom {
  display: flex; justify-content: space-between; align-items: center;
  padding: 12px 16px; border-top: 1px solid var(--border-color);
}
.order-total { font-size: 13px; color: var(--text-secondary); }
.order-total b { font-weight: 600; color: var(--text-primary); }
.order-actions { display: flex; gap: 8px; }
.action-btn {
  padding: 5px 14px; border-radius: 14px; border: 1px solid var(--border-color);
  background: transparent; font-size: 12px; color: var(--text-secondary); cursor: pointer;
  transition: all var(--transition-fast);
}
.action-btn.primary {
  border-color: var(--color-primary); color: var(--color-primary);
  background: rgba(99,102,241,0.06);
}

.loading-tip { text-align: center; padding: 16px; font-size: 13px; color: var(--text-muted); }
</style>
