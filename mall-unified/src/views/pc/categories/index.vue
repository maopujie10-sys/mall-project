<template>
  <div class="pc-categories"><h2>全部分类</h2>
    <div class="cat-grid">
      <div v-for="cat in categories" :key="cat.id" class="cat-card card card-hover" @click="$router.push('/pc/products?cat=' + cat.id)">
        <span style="font-size:32px">{{ cat.icon || '📦' }}</span>
        <span>{{ cat.name }}</span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { getCategories } from '@/api/products'
const categories = ref([])
onMounted(async () => { try { const r = await getCategories(); categories.value = r.data || r.list || [] } catch {} })
</script>

<style scoped>
.pc-categories { padding: 24px 0; }
h2 { margin-bottom: 24px; }
.cat-grid { display: grid; grid-template-columns: repeat(6, 1fr); gap: 12px; }
.cat-card { display: flex; flex-direction: column; align-items: center; gap: 8px; padding: 24px; cursor: pointer; }
@media (max-width: 1024px) { .cat-grid { grid-template-columns: repeat(4, 1fr); } }
</style>
