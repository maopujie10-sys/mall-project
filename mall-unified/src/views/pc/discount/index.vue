<template>
  <div class="pc-discount"><h2>🔥 折扣专区</h2><div class="product-grid">
    <div v-for="item in products" :key="item.id" class="product-card card card-hover" @click="$router.push('/pc/product/' + item.id)">
      <div class="prod-img"><img :src="item.image || item.imgUrl" /><span class="disc-tag">-{{ item.discountRatio || 0 }}%</span></div>
      <div class="prod-info"><h4>{{ item.name }}</h4><span class="prc">¥{{ item.price }}</span></div>
    </div>
  </div></div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { getProductList } from '@/api/products'
const products = ref([])
onMounted(async () => { try { const r = await getProductList({ isDisc: 1 }); products.value = ((r.data || r).list || (r.data || r).result || []) } catch {} })
</script>

<style scoped>
.pc-discount { padding: 24px 0; }
h2 { margin-bottom: 24px; }
.product-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px; }
.product-card { cursor: pointer; padding: 0; overflow: hidden; }
.prod-img { aspect-ratio: 1; background: var(--bg-tertiary); position: relative; }
.prod-img img { width: 100%; height: 100%; object-fit: cover; }
.disc-tag { position: absolute; top: 8px; left: 8px; background: var(--color-danger); color: white; font-size: 12px; padding: 2px 8px; border-radius: 4px; }
.prod-info { padding: 12px; }
.prc { font-size: 16px; font-weight: 700; color: var(--color-danger); }
</style>
