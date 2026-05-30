<template>
  <div class="address-page">
    <h2 class="page-title">{{ $t('user.address') }}</h2>

    <div class="address-list" v-if="addresses.length">
      <div v-for="addr in addresses" :key="addr.id" class="addr-card" @click="selectAddress(addr)">
        <div class="addr-top">
          <span class="addr-name">{{ addr.name }}</span>
          <span class="addr-phone">{{ addr.phone }}</span>
          <span class="addr-tag" v-if="addr.isDefault">{{ $t('user.default') }}</span>
        </div>
        <p class="addr-text">{{ addr.country }} {{ addr.state }} {{ addr.city }} {{ addr.address }} {{ addr.detail }}</p>
        <div class="addr-actions">
          <span class="addr-action" @click.stop="editAddress(addr)">{{ $t('common.edit') }}</span>
          <span class="addr-action danger" @click.stop="deleteAddress(addr)">{{ $t('common.delete') }}</span>
        </div>
      </div>
    </div>

    <van-empty v-if="!addresses.length && !loading" :description="$t('user.noAddress')" />

    <button class="add-btn" @click="editAddress()">{{ $t('user.addAddress') }}</button>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { Empty as VanEmpty, showToast, showDialog } from 'vant'
import { getAddressList, deleteAddress as delAddr } from '@/api/user'
import { useUserStore } from '@/stores/user'

const router = useRouter()
const userStore = useUserStore()
const addresses = ref([])
const loading = ref(false)

onMounted(async () => {
  if (!userStore.token) { router.push('/m/login'); return }
  loading.value = true
  try {
    const res = await getAddressList()
    addresses.value = res.pageList || res.list || res.data || []
  } catch (e) {}
  loading.value = false
})

function selectAddress(addr) {
  router.push({ path: '/m/checkout', query: { addressId: addr.id } })
}

function editAddress(addr) {
  router.push({ path: '/m/address/edit', query: addr ? { id: addr.id } : {} })
}

async function deleteAddress(addr) {
  try {
    await showDialog({ title: '确认删除', message: '确定要删除这个地址吗？' })
    await delAddr({ addressId: addr.id })
    addresses.value = addresses.value.filter(a => a.id !== addr.id)
    showToast('已删除')
  } catch (e) {}
}
</script>

<style scoped>
.address-page { min-height: 100vh; background: var(--bg-secondary); padding: 16px 14px 24px; }
.page-title { font-size: 18px; font-weight: 700; color: var(--text-primary); margin-bottom: 16px; }
.address-list { display: flex; flex-direction: column; gap: 10px; }
.addr-card { background: var(--bg-primary); border-radius: var(--border-radius); box-shadow: var(--shadow-sm); padding: 16px; cursor: pointer; transition: box-shadow var(--transition-fast); }
.addr-card:hover { box-shadow: var(--shadow-md); }
.addr-top { display: flex; align-items: center; gap: 10px; margin-bottom: 6px; }
.addr-name { font-size: 15px; font-weight: 600; color: var(--text-primary); }
.addr-phone { font-size: 13px; color: var(--text-secondary); }
.addr-tag { padding: 2px 8px; background: rgba(99,102,241,0.08); color: var(--color-primary); border-radius: 10px; font-size: 11px; }
.addr-text { font-size: 13px; color: var(--text-secondary); line-height: 1.5; }
.addr-actions { display: flex; gap: 16px; margin-top: 10px; padding-top: 10px; border-top: 1px solid var(--border-color); }
.addr-action { font-size: 12px; color: var(--color-primary); cursor: pointer; }
.addr-action.danger { color: var(--color-danger); }
.add-btn { width: 100%; height: 46px; border-radius: var(--border-radius); border: 1.5px dashed var(--color-primary); background: transparent; color: var(--color-primary); font-size: 15px; font-weight: 500; cursor: pointer; margin-top: 16px; }
</style>
