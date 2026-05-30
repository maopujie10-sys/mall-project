<template>
  <div class="pc-stores"><h2>品牌店铺</h2>
    <div class="store-grid">
      <div v-for="s in sellers" :key="s.id" class="store-card card card-hover" @click="$router.push('/pc/store/' + s.id)">
        <img :src="s.logo || s.avatar" class="store-logo" />
        <h4>{{ s.name }}</h4>
        <p>{{ s.goodsCount || 0 }} 件商品</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { getSellerList } from '@/api/products'
const sellers = ref([])
onMounted(async () => { try { const r = await getSellerList(); sellers.value = (r.data || r).list || (r.data || r).pageList || [] } catch {} })
</script>

<style scoped>
.pc-stores { padding: 24px 0; }
h2 { margin-bottom: 24px; }
.store-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px; }
.store-card { display: flex; flex-direction: column; align-items: center; padding: 24px; cursor: pointer; text-align: center; }
.store-logo { width: 64px; height: 64px; border-radius: 16px; object-fit: cover; margin-bottom: 12px; }
@media (max-width: 1024px) { .store-grid { grid-template-columns: repeat(3, 1fr); } }
</style>
