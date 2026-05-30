<template>
  <div class="cart-page">
    <!-- 头部 -->
    <div class="cart-header">
      <h2>{{ $t('common.cart') }}</h2>
    </div>

    <!-- 空购物车 -->
    <div v-if="!items.length && !loading" class="empty-cart">
      <svg width="64" height="64" viewBox="0 0 24 24" fill="none">
        <circle cx="9" cy="21" r="1" stroke="var(--text-muted)" stroke-width="1.5"/>
        <circle cx="20" cy="21" r="1" stroke="var(--text-muted)" stroke-width="1.5"/>
        <path d="M1 1h4l2.68 13.39a2 2 0 0 0 2 1.61h9.72a2 2 0 0 0 2-1.61L23 6H6" stroke="var(--text-muted)" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
      </svg>
      <p>{{ $t('common.emptyCart') }}</p>
      <button class="go-shop-btn" @click="$router.push('/m')">{{ $t('common.goShopping') }}</button>
    </div>

    <!-- 购物车列表 -->
    <template v-else>
      <div v-for="(group, idx) in items" :key="group.key || idx" class="cart-group">
        <!-- 店铺标题 -->
        <div class="group-header">
          <van-checkbox v-model="group.checkedAll" @update:model-value="(v) => handleCheckGroup(v, idx)" />
          <span class="group-name">{{ group.sort || group.shopName }}</span>
        </div>

        <!-- 商品项 -->
        <div class="group-items">
          <div v-for="(item, n) in (group.child || [])" :key="item.tempId || n" class="cart-item">
            <van-checkbox v-model="item.selected" class="item-checkbox" @update:model-value="calcTotal" />
            <div class="item-content" @click="goDetail(item)">
              <div class="item-img-wrap">
                <img :src="item.coverImg || item.img" class="item-img" />
              </div>
              <div class="item-info">
                <p class="item-name">{{ textOmit(item.name || item.describe, 40) }}</p>
                <p class="item-sku" v-if="item.attributes?.attrs?.length">
                  <span v-for="(attr, ap) in item.attributes.attrs" :key="ap">{{ attr.attrName }}:{{ attr.attrValueName }}</span>
                </p>
                <div class="item-bottom">
                  <span class="item-price">${{ formatPrice(item.price) }}</span>
                  <van-stepper :disable-input="true" v-model="item.count" :max="maxBuyNum" integer @change="calcTotal" />
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 底部结算栏 -->
      <div class="cart-bottom" v-if="items.length">
        <van-checkbox v-model="checkedAll" @update:model-value="handleCheckAll" class="all-check">
          {{ $t('common.selectAll') }}
        </van-checkbox>
        <div class="bottom-right">
          <div class="total-info">
            <span class="total-label">{{ $t('common.total') }}:</span>
            <span class="total-amount">${{ formatPrice(totalAmount) }}</span>
          </div>
          <button class="checkout-btn" @click="goCheckout" :disabled="!hasSelected">
            {{ $t('common.checkout') }} ({{ selectedCount }})
          </button>
        </div>
      </div>
    </template>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { Checkbox as VanCheckbox, Stepper as VanStepper, showNotify } from 'vant'
import { useUserStore } from '@/stores/user'

const router = useRouter()
const userStore = useUserStore()

const items = ref([])
const loading = ref(false)
const checkedAll = ref(false)
const maxBuyNum = ref(99)

function _toFixed(n, d) { n = n.toString(); const i = n.indexOf('.'); const s = i !== -1 ? n.substring(0, d + i + 1) : n.substring(0); return parseFloat(s).toFixed(d) }
function formatPrice(n) { if (!n || !Number(n)) return 0; const s = _toFixed(n, 2); const p = s.slice(0, s.indexOf('.')); const r = s.slice(s.indexOf('.') + 1); return `${p.replace(/(\d)(?=(\d{3})+(?!\d))/g, '$1,')}.${r.length < 2 ? r + '0' : r}` }
function textOmit(t, m = 48) { if (!t) return ''; return t.length > m ? t.slice(0, m) + '...' : t }

// Load cart
onMounted(loadCart)

function loadCart() {
  try {
    const stored = JSON.parse(localStorage.getItem('productList') || '[]')
    items.value = Array.isArray(stored) ? stored : stored?.value || []
    calcTotal()
  } catch (e) {
    items.value = []
  }
}

const selectedCount = computed(() => {
  let count = 0
  items.value.forEach(g => {
    (g.child || []).forEach(item => {
      if (item.selected) count += (item.count || 1)
    })
  })
  return count
})

const hasSelected = computed(() => selectedCount.value > 0)

const totalAmount = computed(() => {
  let total = 0
  items.value.forEach(g => {
    (g.child || []).forEach(item => {
      if (item.selected) total += (item.price || 0) * (item.count || 1)
    })
  })
  return total
})

function calcTotal() {
  items.value.forEach(g => {
    if (g.child && g.child.length) {
      g.checkedAll = g.child.every(item => item.selected)
    }
  })
  checkedAll.value = items.value.every(g => g.checkedAll)
  saveCart()
}

function handleCheckGroup(val, idx) {
  const group = items.value[idx]
  if (group?.child) {
    group.child.forEach(item => { item.selected = val })
  }
  calcTotal()
}

function handleCheckAll(val) {
  items.value.forEach(g => {
    g.checkedAll = val
    if (g.child) g.child.forEach(item => { item.selected = val })
  })
  calcTotal()
}

function saveCart() {
  localStorage.setItem('productList', JSON.stringify(items.value))
}

function goDetail(item) {
  router.push('/m/product/' + item.id)
}

function goCheckout() {
  if (!userStore.token) { showNotify({ type: 'warning', message: '请先登录' }); router.push('/m/login'); return }
  router.push('/m/checkout')
}
</script>

<style scoped>
.cart-page { min-height: 100vh; background: var(--bg-secondary); padding-bottom: 80px; }

.cart-header { padding: 16px; }
.cart-header h2 { font-size: 18px; font-weight: 700; color: var(--text-primary); }

/* 空购物车 */
.empty-cart { display: flex; flex-direction: column; align-items: center; gap: 16px; padding: 80px 20px; color: var(--text-muted); font-size: 14px; }
.go-shop-btn { padding: 10px 32px; border-radius: 20px; background: var(--color-primary); color: #fff; border: none; font-size: 14px; font-weight: 500; cursor: pointer; }

/* 分组 */
.cart-group { background: var(--bg-primary); border-radius: var(--border-radius); margin: 8px 14px; box-shadow: var(--shadow-sm); overflow: hidden; }
.group-header { display: flex; align-items: center; gap: 10px; padding: 12px 16px; border-bottom: 1px solid var(--border-color); }
.group-name { font-size: 14px; font-weight: 500; color: var(--text-primary); }

.cart-item { display: flex; align-items: flex-start; padding: 12px 16px 12px 12px; border-bottom: 1px solid var(--border-color); }
.cart-item:last-child { border-bottom: none; }
.item-checkbox { margin-right: 4px; padding-top: 20px; }
.item-content { flex: 1; display: flex; gap: 12px; cursor: pointer; }

.item-img-wrap { width: 80px; height: 80px; border-radius: var(--border-radius-sm); overflow: hidden; background: var(--bg-secondary); flex-shrink: 0; display: flex; align-items: center; justify-content: center; }
.item-img { max-width: 100%; max-height: 100%; object-fit: contain; }

.item-info { flex: 1; display: flex; flex-direction: column; min-width: 0; }
.item-name { font-size: 13px; color: var(--text-primary); display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; margin-bottom: 4px; }
.item-sku { font-size: 11px; color: var(--text-muted); margin-bottom: 8px; }
.item-bottom { display: flex; justify-content: space-between; align-items: center; margin-top: auto; }
.item-price { font-size: 16px; font-weight: 700; color: var(--color-primary); }

/* 底部栏 */
.cart-bottom {
  position: fixed; bottom: 0; width: 100%; max-width: 480px;
  background: var(--bg-primary); border-top: 1px solid var(--border-color);
  display: flex; align-items: center; padding: 10px 16px;
  padding-bottom: calc(10px + env(safe-area-inset-bottom, 0));
  gap: 12px; z-index: 50;
}
.all-check { flex-shrink: 0; }
.bottom-right { flex: 1; display: flex; align-items: center; justify-content: flex-end; gap: 12px; }
.total-info { display: flex; align-items: baseline; gap: 4px; }
.total-label { font-size: 13px; color: var(--text-secondary); }
.total-amount { font-size: 18px; font-weight: 700; color: var(--color-primary); }
.checkout-btn { padding: 8px 24px; border-radius: 20px; background: linear-gradient(135deg, var(--color-primary), var(--color-primary-dark)); color: #fff; border: none; font-size: 14px; font-weight: 600; cursor: pointer; }
.checkout-btn:disabled { opacity: 0.5; cursor: not-allowed; }
</style>
