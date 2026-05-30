<template>
  <div class="loan-page">
    <h2 class="page-title">{{ $t('user.loanApply') }}</h2>

    <div class="card">
      <div class="loan-info">
        <svg width="40" height="40" viewBox="0 0 24 24" fill="none">
          <circle cx="12" cy="12" r="10" stroke="var(--color-accent)" stroke-width="2"/>
          <path d="M12 17V9M12 6h.01" stroke="var(--color-accent)" stroke-width="2" stroke-linecap="round"/>
        </svg>
        <p class="loan-desc">{{ $t('user.loanDesc') }}</p>
      </div>
    </div>

    <div class="card">
      <div class="input-label">{{ $t('user.loanAmount') }}</div>
      <div class="amount-input-wrap">
        <span class="currency">$</span>
        <input v-model="loanAmount" type="number" class="amount-input" :placeholder="$t('user.amountPlaceholder')" />
      </div>

      <div class="input-label">{{ $t('user.loanPurpose') }}</div>
      <textarea v-model="purpose" class="purpose-input" :placeholder="$t('user.loanPurpose') + '...'" rows="3" />

      <button class="submit-btn" @click="handleApply">{{ $t('common.submit') }}</button>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { showToast, showNotify } from 'vant'
import { useUserStore } from '@/stores/user'

const router = useRouter()
const userStore = useUserStore()
const loanAmount = ref('')
const purpose = ref('')

onMounted(() => {
  if (!userStore.token) { router.push('/m/login') }
})

function handleApply() {
  if (!loanAmount.value || loanAmount.value <= 0) { showNotify({ type: 'warning', message: '请输入贷款金额' }); return }
  showToast('申请已提交')
}
</script>

<style scoped>
.loan-page { min-height: 100vh; background: var(--bg-secondary); padding: 16px 14px; }
.page-title { font-size: 18px; font-weight: 700; color: var(--text-primary); margin-bottom: 16px; }
.card { background: var(--bg-primary); border-radius: var(--border-radius); box-shadow: var(--shadow-sm); padding: 20px; margin-bottom: 12px; }
.loan-info { text-align: center; padding: 16px; }
.loan-desc { font-size: 13px; color: var(--text-secondary); margin-top: 12px; line-height: 1.6; }
.input-label { font-size: 13px; color: var(--text-secondary); margin-bottom: 8px; margin-top: 16px; }
.input-label:first-child { margin-top: 0; }
.amount-input-wrap { display: flex; align-items: center; border: 2px solid var(--border-color); border-radius: var(--border-radius); padding: 0 16px; margin-bottom: 8px; transition: border-color var(--transition-fast); }
.amount-input-wrap:focus-within { border-color: var(--color-primary); }
.currency { font-size: 18px; font-weight: 600; color: var(--text-primary); }
.amount-input { flex: 1; border: none; outline: none; font-size: 18px; font-weight: 600; color: var(--text-primary); padding: 14px 0 14px 4px; background: transparent; }
.purpose-input { width: 100%; border: 2px solid var(--border-color); border-radius: var(--border-radius); padding: 12px; font-size: 14px; color: var(--text-primary); background: transparent; outline: none; resize: none; transition: border-color var(--transition-fast); font-family: inherit; }
.purpose-input:focus { border-color: var(--color-primary); }
.submit-btn { width: 100%; height: 46px; border-radius: var(--border-radius); border: none; background: linear-gradient(135deg, var(--color-primary), var(--color-primary-dark)); color: #fff; font-size: 16px; font-weight: 600; cursor: pointer; margin-top: 20px; box-shadow: 0 4px 12px rgba(99,102,241,0.3); }
</style>
