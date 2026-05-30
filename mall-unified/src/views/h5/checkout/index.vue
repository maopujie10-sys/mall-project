<template>
  <div class="checkout-page">
    <h2 class="page-title">{{ $t('common.checkout') }}</h2>

    <!-- 地址 -->
    <div class="card addr-card" @click="selectAddress">
      <div v-if="selectedAddress" class="addr-detail">
        <div class="addr-top">
          <span class="addr-name">{{ selectedAddress.name }}</span>
          <span class="addr-phone">{{ selectedAddress.phone }}</span>
        </div>
        <p class="addr-text">{{ selectedAddress.address }} {{ selectedAddress.detail }}</p>
      </div>
      <div v-else class="addr-empty">{{ $t('user.address') }} &rsaquo;</div>
    </div>

    <!-- 商品列表 -->
    <div class="card goods-card" v-if="cartItems.length">
      <div v-for="item in cartItems" :key="item.tempId || item.id" class="checkout-item">
        <div class="co-img-wrap">
          <img :src="item.coverImg || item.img || item.imgUrl" class="co-img" />
        </div>
        <div class="co-info">
          <p class="co-name">{{ textOmit(item.name || item.describe, 40) }}</p>
          <div class="co-price-row">
            <span class="co-price">${{ formatPrice(item.price) }}</span>
            <span class="co-qty">x{{ item.count || 1 }}</span>
          </div>
        </div>
      </div>
    </div>

    <!-- 总计 -->
    <div class="card summary-card">
      <div class="sum-row"><span>{{ $t('common.subtotal') }}</span><span>${{ formatPrice(totalAmount) }}</span></div>
      <div class="sum-row"><span>{{ $t('product.freight') }}</span><span>$0.00</span></div>
      <div class="sum-row total"><span>{{ $t('common.total') }}</span><b>${{ formatPrice(totalAmount) }}</b></div>
    </div>

    <!-- 提交 -->
    <button class="submit-btn" @click="submitOrder" :disabled="!selectedAddress">
      {{ $t('common.submit') }}
    </button>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { showToast, showNotify } from 'vant'
import { useUserStore } from '@/stores/user'

const router = useRouter()
const userStore = useUserStore()

const selectedAddress = ref(null)
const cartItems = ref([])

function _toFixed(n, d) { n = n.toString(); const i = n.indexOf('.'); const s = i !== -1 ? n.substring(0, d + i + 1) : n.substring(0); return parseFloat(s).toFixed(d) }
function formatPrice(n) { if (!n || !Number(n)) return 0; const s = _toFixed(n, 2); const p = s.slice(0, s.indexOf('.')); const r = s.slice(s.indexOf('.') + 1); return `${p.replace(/(\d)(?=(\d{3})+(?!\d))/g, '$1,')}.${r.length < 2 ? r + '0' : r}` }
function textOmit(t, m = 48) { if (!t) return ''; return t.length > m ? t.slice(0, m) + '...' : t }

const totalAmount = computed(() => {
  let t = 0
  cartItems.value.forEach(item => {
    if (item.selected !== false) t += (item.price || 0) * (item.count || 1)
  })
  return t
})

onMounted(() => {
  if (!userStore.token) { router.push('/m/login'); return }
  try {
    const stored = JSON.parse(localStorage.getItem('productList') || '[]')
    const all = Array.isArray(stored) ? stored : stored?.value || []
    cartItems.value = []
    all.forEach(g => {
      (g.child || []).forEach(item => {
        if (item.selected) cartItems.value.push(item)
      })
    })
    if (!cartItems.value.length) {
      showNotify({ type: 'warning', message: '购物车为空' })
      router.push('/m/cart')
    }
  } catch (e) { cartItems.value = [] }
})

function selectAddress() { router.push('/m/address') }

function submitOrder() {
  showToast('订单提交成功')
  localStorage.removeItem('productList')
  router.push('/m/order')
}
</script>

<style scoped>
.checkout-page { min-height: 100vh; background: var(--bg-secondary); padding: 16px 14px 24px; }
.page-title { font-size: 18px; font-weight: 700; color: var(--text-primary); margin-bottom: 16px; }
.card { background: var(--bg-primary); border-radius: var(--border-radius); box-shadow: var(--shadow-sm); padding: 16px; margin-bottom: 12px; }
.addr-card { cursor: pointer; }
.addr-empty { font-size: 14px; color: var(--color-primary); }
.addr-top { display: flex; gap: 12px; margin-bottom: 4px; font-size: 15px; font-weight: 500; }
.addr-phone { color: var(--text-secondary); }
.addr-text { font-size: 13px; color: var(--text-secondary); }
.checkout-item { display: flex; gap: 12px; padding: 10px 0; border-bottom: 1px solid var(--border-color); }
.checkout-item:last-child { border-bottom: none; }
.co-img-wrap { width: 64px; height: 64px; border-radius: var(--border-radius-sm); overflow: hidden; background: var(--bg-secondary); flex-shrink: 0; display: flex; align-items: center; justify-content: center; }
.co-img { max-width: 100%; max-height: 100%; object-fit: contain; }
.co-info { flex: 1; display: flex; flex-direction: column; min-width: 0; }
.co-name { font-size: 13px; color: var(--text-primary); display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; }
.co-price-row { display: flex; justify-content: space-between; align-items: center; margin-top: auto; }
.co-price { font-size: 15px; font-weight: 600; color: var(--color-primary); }
.co-qty { font-size: 12px; color: var(--text-muted); }
.sum-row { display: flex; justify-content: space-between; padding: 6px 0; font-size: 13px; color: var(--text-secondary); }
.sum-row.total { font-size: 16px; color: var(--text-primary); border-top: 1px solid var(--border-color); padding-top: 10px; margin-top: 6px; }
.sum-row.total b { color: var(--color-primary); }
.submit-btn { width: 100%; height: 46px; border-radius: var(--border-radius); border: none; background: linear-gradient(135deg, var(--color-primary), var(--color-primary-dark)); color: #fff; font-size: 16px; font-weight: 600; cursor: pointer; margin-top: 16px; }
.submit-btn:disabled { opacity: 0.5; cursor: not-allowed; }
</style>
