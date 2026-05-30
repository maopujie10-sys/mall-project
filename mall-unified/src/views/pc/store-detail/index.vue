<template>
  <div class="pc-store-detail fade-in" v-if="shop">
    <div class="shop-header card"><img :src="shop.logo || shop.avatar" class="shop-logo" /><h2>{{ shop.name || shop.shopName }}</h2><p>商品 {{ shop.goodsCount || 0 }} · 粉丝 {{ shop.followers || 0 }}</p></div>
    <div class="product-grid">
      <div v-for="item in goods" :key="item.id" class="product-card card card-hover" @click="$router.push('/pc/product/' + item.id)">
        <div class="prod-img"><img :src="item.image || item.imgUrl" /></div>
        <div class="prod-info"><h4>{{ item.name }}</h4><span class="prc">¥{{ item.price }}</span></div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { getSellerDetail, getSellerGoods } from '@/api/products'

const route = useRoute()
const shop = ref(null)
const goods = ref([])
onMounted(async () => {
  try {
    const [s, g] = await Promise.allSettled([getSellerDetail(route.params.sellerId), getSellerGoods(route.params.sellerId)])
    if (s.status === 'fulfilled') shop.value = s.value.data || s.value
    if (g.status === 'fulfilled') goods.value = ((g.value.data || g.value).list || (g.value.data || g.value).rows || [])
  } catch {}
})
</script>

<style scoped>
.pc-store-detail { padding: 24px 0; }
.shop-header { text-align: center; padding: 40px; margin-bottom: 24px; }
.shop-logo { width: 80px; height: 80px; border-radius: 20px; object-fit: cover; margin-bottom: 12px; }
.product-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px; }
.product-card { cursor: pointer; padding: 0; overflow: hidden; }
.prod-img { aspect-ratio: 1; background: var(--bg-tertiary); }
.prod-img img { width: 100%; height: 100%; object-fit: cover; }
.prod-info { padding: 12px; }
.prod-info h4 { font-size: 14px; margin-bottom: 4px; }
.prc { font-size: 16px; font-weight: 700; color: var(--color-danger); }
</style>
