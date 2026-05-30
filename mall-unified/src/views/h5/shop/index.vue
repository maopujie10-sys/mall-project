<template>
  <div class="shop-page" v-if="shop">
    <!-- 店铺头部 -->
    <div class="shop-header">
      <div class="shop-header-bg"></div>
      <div class="shop-header-info">
        <img :src="shop.avatar" class="shop-avatar" />
        <div class="shop-detail">
          <h3 class="shop-name">{{ shop.name }}</h3>
          <p class="shop-stats">{{ $t('common.products') }}: {{ shop.sellerGoodsNum }} | {{ $t('common.follow') }}: {{ formatInt((+shop.fake || 0) + (+shop.focusNum || 0)) }}</p>
        </div>
        <button class="follow-btn">{{ $t('common.follow') }}</button>
      </div>
    </div>

    <!-- Tab -->
    <van-tabs v-model:active="activeTab" sticky color="var(--color-primary)">
      <van-tab :title="$t('common.products')" />
    </van-tabs>

    <!-- 商品列表 -->
    <div class="goods-grid">
      <div v-for="item in goods" :key="item.id" class="goods-card" @click="goDetail(item)">
        <div class="goods-img-wrap">
          <img :src="item.imgUrl1 || item.imgUrl || defaultImg" class="goods-img" />
          <div class="disc-badge" v-if="item.discountRatio >= 0.01">{{ (item.discountRatio * 100).toFixed(0) }}% OFF</div>
        </div>
        <div class="goods-info">
          <span class="goods-price">${{ formatPrice(item.discountPrice || item.sellingPrice) }}</span>
          <p class="goods-sold">{{ $t('common.sales') }}: {{ formatInt(item.soldNum) }}</p>
          <p class="goods-name">{{ textOmit(item.name, 30) }}</p>
        </div>
      </div>
    </div>

    <van-empty v-if="!goods.length && !loading" :description="$t('common.noData')" />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { Tab as VanTab, Tabs as VanTabs, Empty as VanEmpty } from 'vant'
import { getSellerList } from '@/api/home'

const router = useRouter()
const route = useRoute()
const defaultImg = 'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMjAwIiBoZWlnaHQ9IjIwMCIgdmlld0JveD0iMCAwIDIwMCAyMDAiIGZpbGw9Im5vbmUiPjxyZWN0IHdpZHRoPSIyMDAiIGhlaWdodD0iMjAwIiBmaWxsPSIjZjFmNWY5Ii8+PC9zdmc+'

const shop = ref(null)
const goods = ref([])
const loading = ref(false)
const activeTab = ref(0)
const sellerId = ref(route.params.sellerId || route.query.sellerId)

function _toFixed(n, d) { n = n.toString(); const i = n.indexOf('.'); const s = i !== -1 ? n.substring(0, d + i + 1) : n.substring(0); return parseFloat(s).toFixed(d) }
function formatPrice(n) { if (!n || !Number(n)) return 0; const s = _toFixed(n, 2); const p = s.slice(0, s.indexOf('.')); const r = s.slice(s.indexOf('.') + 1); return `${p.replace(/(\d)(?=(\d{3})+(?!\d))/g, '$1,')}.${r.length < 2 ? r + '0' : r}` }
function formatInt(n) { if (!n || !Number(n)) return 0; const s = _toFixed(n, 2); return s.slice(0, s.indexOf('.')).replace(/(\d)(?=(\d{3})+(?!\d))/g, '$1,') }
function textOmit(t, m = 48) { if (!t) return ''; return t.length > m ? t.slice(0, m) + '...' : t }

onMounted(async () => {
  if (!sellerId.value) return
  loading.value = true
  try {
    const res = await getSellerList({ pageNum: 1, pageSize: 10, sellerId: sellerId.value })
    const list = res.pageList || res.result || []
    if (list.length) shop.value = list[0]
    // Load goods
    goods.value = (res.sellerGoodsList || res.goodsList || []).map(g => ({ ...g, id: g.id || g.goodsId }))
  } catch (e) {}
  loading.value = false
})

function goDetail(item) { router.push('/m/product/' + item.id) }
</script>

<style scoped>
.shop-page { min-height: 100vh; background: var(--bg-secondary); padding-bottom: 24px; }
.shop-header { position: relative; overflow: hidden; }
.shop-header-bg { height: 120px; background: linear-gradient(135deg, var(--color-primary), #818cf8); }
.shop-header-info { display: flex; align-items: center; gap: 12px; padding: 16px; background: var(--bg-primary); border-radius: var(--border-radius-lg) var(--border-radius-lg) 0 0; margin-top: -20px; position: relative; }
.shop-avatar { width: 56px; height: 56px; border-radius: 50%; border: 3px solid #fff; object-fit: cover; margin-top: -28px; box-shadow: var(--shadow-md); }
.shop-detail { flex: 1; }
.shop-name { font-size: 16px; font-weight: 600; }
.shop-stats { font-size: 11px; color: var(--text-muted); margin-top: 2px; }
.follow-btn { padding: 5px 20px; border-radius: 16px; border: 1.5px solid var(--color-primary); background: transparent; color: var(--color-primary); font-size: 13px; cursor: pointer; }
.goods-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 10px; padding: 12px 14px; }
.goods-card { background: var(--bg-primary); border-radius: var(--border-radius); box-shadow: var(--shadow-sm); overflow: hidden; cursor: pointer; }
.goods-img-wrap { position: relative; aspect-ratio: 1; background: var(--bg-secondary); display: flex; align-items: center; justify-content: center; }
.goods-img { max-width: 100%; max-height: 100%; object-fit: contain; }
.disc-badge { position: absolute; top: 0; right: 0; background: linear-gradient(135deg, #ef4444, #f97316); color: #fff; padding: 3px 8px; border-radius: 0 var(--border-radius) 0 var(--border-radius); font-size: 11px; font-weight: 700; }
.goods-info { padding: 10px 12px 12px; }
.goods-price { font-size: 17px; font-weight: 700; color: var(--color-primary); }
.goods-sold { font-size: 11px; color: var(--text-muted); margin: 4px 0; }
.goods-name { font-size: 13px; color: var(--text-primary); display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; text-overflow: ellipsis; }
</style>
