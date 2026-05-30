<template>
  <div v-if="item" class="product-card card card-hover" @click="gotoDetail">
    <div class="prod-img">
      <img :src="item.imgUrl1 || item.mainImage || item.imgUrl || ''" :alt="item.name" />
      <span v-if="item.discountRatio" class="prod-tag">{{ Math.round(item.discountRatio * 100) }}% OFF</span>
    </div>
    <div class="prod-info">
      <div class="prod-price">${{ formatPrice(price) }}</div>
      <div class="prod-sold">Sold {{ formatNum(item.soldNum || 0) }}</div>
      <p class="prod-name">{{ item.name }}</p>
      <div class="prod-actions" @click.stop>
        <span class="buy-btn" @click="props.belike ? gotoDetail() : buyNow()">Buy Now</span>
        <i :class="keep ? 'star-icon filled' : 'star-icon'" @click="toggleCollect">{{ keep ? '★' : '☆' }}</i>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { post } from '@/api/index'

const props = defineProps({
  item: { type: Object, default: () => ({}) },
  belike: { type: Boolean, default: false }
})

const router = useRouter()
const keep = ref(props.item.isKeep)

const price = computed(() => props.item.discountPrice ?? props.item.sellingPrice)

function formatPrice(n) {
  const val = Number(n)
  if (!val) return '0.00'
  return val.toFixed(2).replace(/\B(?=(\d{3})+(?!\d))/g, ',')
}

function formatNum(n) {
  if (!n) return '0'
  return Number(n).toLocaleString()
}

function gotoDetail() {
  router.push({ path: '/pc/product/' + props.item.id, query: { id: props.item.id } })
}

async function toggleCollect() {
  const token = localStorage.getItem('token')
  if (!token) { router.push('/pc/login'); return }
  try {
    if (keep.value) {
      await post('/api/keepGoods!cancel.action', { sellerGoodsId: props.item.id })
      ElMessage.warning('Canceled')
    } else {
      await post('/api/keepGoods!add.action', { sellerGoodsId: props.item.id })
      ElMessage.success('Collected')
    }
    keep.value = !keep.value
  } catch {}
}

function buyNow() {
  router.push({ path: '/pc/product/' + props.item.id, query: { id: props.item.id, buyNow: '1' } })
}
</script>

<style scoped>
.product-card { border: 1px solid var(--border-color); border-radius: var(--border-radius-sm); overflow: hidden; padding: 0; cursor: pointer; position: relative; transition: all var(--transition-fast); background: var(--bg-primary); }
.product-card:hover { border-color: var(--color-primary); box-shadow: var(--shadow-lg); transform: translateY(-2px); }
.prod-img { width: 100%; aspect-ratio: 1; overflow: hidden; display: flex; align-items: center; justify-content: center; background: var(--bg-tertiary); }
.prod-img img { width: 100%; height: 100%; object-fit: contain; transition: transform 0.3s; }
.product-card:hover .prod-img img { transform: scale(1.05); }
.prod-tag { position: absolute; top: 6px; left: 6px; background: var(--color-danger); color: white; font-size: 10px; padding: 2px 6px; border-radius: 4px; font-weight: 600; }
.prod-info { padding: 10px; }
.prod-price { font-size: 16px; font-weight: 600; color: var(--color-danger); margin-bottom: 4px; }
.prod-sold { font-size: 10px; color: var(--text-muted); margin-bottom: 6px; }
.prod-name { font-size: 13px; color: var(--text-secondary); overflow: hidden; text-overflow: ellipsis; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; line-height: 1.4; margin-bottom: 8px; min-height: 36px; }
.prod-actions { display: flex; justify-content: space-between; align-items: center; border-top: 1px solid var(--border-color); padding-top: 8px; }
.buy-btn { font-size: 12px; font-weight: 600; color: var(--color-primary); cursor: pointer; }
.buy-btn:hover { text-decoration: underline; }
.star-icon { font-size: 18px; cursor: pointer; color: var(--text-muted); }
.star-icon.filled { color: var(--color-accent); }
</style>
