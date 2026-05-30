<template>
  <div class="invest-page">
    <h2 class="page-title">{{ $t('user.recharge') }}</h2>

    <div class="card">
      <div class="amount-section">
        <span class="amount-label">{{ $t('user.balance') }}</span>
        <span class="amount-value">${{ formatPrice(walletBalance) }}</span>
      </div>
    </div>

    <div class="card">
      <div class="input-label">{{ $t('user.rechargeAmount') }}</div>
      <div class="amount-input-wrap">
        <span class="currency">$</span>
        <input v-model="amount" type="number" class="amount-input" :placeholder="$t('user.amountPlaceholder')" />
      </div>

      <div class="quick-amounts">
        <span v-for="a in quickAmounts" :key="a" :class="['quick-amt', { active: amount == a }]" @click="amount = a">${{ a }}</span>
      </div>

      <button class="submit-btn" @click="handleRecharge">
        {{ $t('user.rechargeNow') }}
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { showToast, showNotify } from 'vant'
import { useUserStore } from '@/stores/user'
import { getWalletBalance } from '@/api/user'

const router = useRouter()
const userStore = useUserStore()

const walletBalance = ref(0)
const amount = ref('')
const quickAmounts = [50, 100, 200, 500, 1000]

function _toFixed(n, d) { n = n.toString(); const i = n.indexOf('.'); const s = i !== -1 ? n.substring(0, d + i + 1) : n.substring(0); return parseFloat(s).toFixed(d) }
function formatPrice(n) { if (!n || !Number(n)) return 0; const s = _toFixed(n, 2); const p = s.slice(0, s.indexOf('.')); const r = s.slice(s.indexOf('.') + 1); return `${p.replace(/(\d)(?=(\d{3})+(?!\d))/g, '$1,')}.${r.length < 2 ? r + '0' : r}` }

onMounted(async () => {
  if (!userStore.token) { router.push('/m/login'); return }
  try {
    const res = await getWalletBalance()
    walletBalance.value = res.money || res.balance || res.data?.balance || 0
  } catch (e) {}
})

function handleRecharge() {
  if (!amount.value || amount.value <= 0) { showNotify({ type: 'warning', message: '请输入充值金额' }); return }
  showToast('跳转支付...')
}
</script>

<style scoped>
.invest-page { min-height: 100vh; background: var(--bg-secondary); padding: 16px 14px; }
.page-title { font-size: 18px; font-weight: 700; color: var(--text-primary); margin-bottom: 16px; }
.card { background: var(--bg-primary); border-radius: var(--border-radius); box-shadow: var(--shadow-sm); padding: 20px; margin-bottom: 12px; }
.amount-section { text-align: center; }
.amount-label { font-size: 13px; color: var(--text-muted); display: block; margin-bottom: 4px; }
.amount-value { font-size: 32px; font-weight: 700; color: var(--text-primary); }
.input-label { font-size: 13px; color: var(--text-secondary); margin-bottom: 10px; }
.amount-input-wrap { display: flex; align-items: center; border: 2px solid var(--border-color); border-radius: var(--border-radius); padding: 0 16px; margin-bottom: 16px; transition: border-color var(--transition-fast); }
.amount-input-wrap:focus-within { border-color: var(--color-primary); }
.currency { font-size: 20px; font-weight: 600; color: var(--text-primary); margin-right: 4px; }
.amount-input { flex: 1; border: none; outline: none; font-size: 20px; font-weight: 600; color: var(--text-primary); padding: 14px 0; background: transparent; }
.quick-amounts { display: flex; flex-wrap: wrap; gap: 8px; margin-bottom: 20px; }
.quick-amt { padding: 6px 18px; border-radius: 18px; border: 1.5px solid var(--border-color); font-size: 13px; color: var(--text-secondary); cursor: pointer; transition: all var(--transition-fast); }
.quick-amt.active { border-color: var(--color-primary); background: rgba(99,102,241,0.08); color: var(--color-primary); }
.submit-btn { width: 100%; height: 46px; border-radius: var(--border-radius); border: none; background: linear-gradient(135deg, var(--color-primary), var(--color-primary-dark)); color: #fff; font-size: 16px; font-weight: 600; cursor: pointer; box-shadow: 0 4px 12px rgba(99,102,241,0.3); }
</style>
