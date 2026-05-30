<template>
  <div class="search-page">
    <van-search
      v-model="keyword"
      shape="round"
      :placeholder="$t('common.search') + '...'"
      @search="searchView"
      @update:model-value="inputHandle"
      autofocus
    >
      <template #right-icon>
        <van-icon v-if="keyword" name="cross" size="14" @click="clearHandle" />
      </template>
    </van-search>

    <!-- 历史搜索 -->
    <div v-if="!tipsShow && !shopShow && !listShow" class="section-pad">
      <div class="hist-header">
        <span class="hist-title">{{ $t('common.searchHistory') }}</span>
        <span v-if="searchHistory1.length" class="clear-link" @click="emptyHandle">{{ $t('common.clear') }}</span>
      </div>
      <div v-if="searchHistory1.length" class="hist-tags">
        <span v-for="(item, i) in searchHistory1" :key="i" class="hist-tag" @click="tipsHandle(item, false)">{{ item }}</span>
      </div>
      <van-empty v-else :description="$t('common.noRecord')" />
    </div>

    <!-- 搜索提示 -->
    <div v-if="tipsShow" class="section-pad">
      <div v-if="tipsData.length">
        <div v-for="(item, i) in tipsData" :key="i" class="tip-row" @click="tipsHandle(item, item.isShop)">
          <van-icon v-if="item.isShop" name="shop-o" size="16" />
          <span>{{ item.name }}</span>
        </div>
      </div>
      <van-empty v-else :description="$t('common.noData')" />
    </div>

    <!-- 商品结果 -->
    <div v-if="listShow" class="section-pad">
      <div class="goods-grid">
        <div v-for="item in listData" :key="item.id || item.goodsId" class="goods-card" @click="goDetail(item)">
          <div class="goods-img-wrap">
            <img :src="item.imgUrl1 || item.imgUrl || defaultImg" class="goods-img" />
            <div class="disc-badge" v-if="item.discountRatio >= 0.01">{{ (item.discountRatio * 100).toFixed(0) }}% OFF</div>
          </div>
          <div class="goods-info">
            <span class="goods-price">${{ formatPrice(item.discountPrice || item.sellingPrice) }}</span>
            <p class="goods-sold">{{ $t('common.sales') }}: {{ fmtInt(item.soldNum) }}</p>
            <p class="goods-name">{{ txtOmit(item.name, 30) }}</p>
          </div>
        </div>
      </div>
      <van-empty v-if="!listData.length && !listLoading" :description="$t('common.noData')" />
      <div v-if="listLoading" class="loading-tip">{{ $t('common.loading') }}</div>
    </div>

    <!-- 店铺结果 -->
    <div v-if="shopShow" class="section-pad">
      <div class="shop-desc">
        {{ $t('common.searchShopDesc') }} <b>"{{ keyword }}"</b> {{ $t('common.searchShopCount', shopData.length) }}
      </div>
      <div class="shop-list">
        <div v-for="item in shopData" :key="item.id" class="shop-row" @click="jumpShop(item)">
          <img :src="item.avatar" class="shop-av" />
          <div class="shop-mid">
            <span class="shop-nm">{{ item.name }}</span>
            <span class="shop-sub">{{ $t('common.products') }}: {{ item.sellerGoodsNum }}</span>
          </div>
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none"><path d="M9 6l6 6-6 6" stroke="#94a3b8" stroke-width="2" stroke-linecap="round"/></svg>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { Search as VanSearch, Icon as VanIcon, Empty as VanEmpty, showToast, showNotify } from 'vant'
import { searchKeyword, searchKeywordGoods, searchSeller } from '@/api/home'

const router = useRouter()
const defaultImg = 'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMjAwIiBoZWlnaHQ9IjIwMCIgdmlld0JveD0iMCAwIDIwMCAyMDAiIGZpbGw9Im5vbmUiPjxyZWN0IHdpZHRoPSIyMDAiIGhlaWdodD0iMjAwIiBmaWxsPSIjZjFmNWY5Ii8+PC9zdmc+'

const keyword = ref('')
const tipsShow = ref(false)
const tipsData = ref([])
const shopData = ref([])
const shopShow = ref(false)
const listData = ref([])
const listShow = ref(false)
const listLoading = ref(false)
const currentGoodsId = ref(null)
const searchHistory1 = ref([])

// Utils
function _toFixed(n, d) { n = n.toString(); const i = n.indexOf('.'); const s = i !== -1 ? n.substring(0, d + i + 1) : n.substring(0); return parseFloat(s).toFixed(d) }
function formatPrice(n) { if (!n || !Number(n)) return 0; const s = _toFixed(n, 2); const p = s.slice(0, s.indexOf('.')); const r = s.slice(s.indexOf('.') + 1); return `${p.replace(/(\d)(?=(\d{3})+(?!\d))/g, '$1,')}.${r.length < 2 ? r + '0' : r}` }
function fmtInt(n) { if (!n || !Number(n)) return 0; const s = _toFixed(n, 2); return s.slice(0, s.indexOf('.')).replace(/(\d)(?=(\d{3})+(?!\d))/g, '$1,') }
function txtOmit(t, m = 48) { if (!t) return ''; return t.length > m ? t.slice(0, m) + '...' : t }

let dt = null
function debounce(fn, ms) { return (...a) => { clearTimeout(dt); dt = setTimeout(() => fn(...a), ms) } }

onMounted(() => {
  searchHistory1.value = JSON.parse(localStorage.getItem('searchHistory1')) || []
  searchHistory1.value = [...new Set(searchHistory1.value)]
})

function goDetail(item) { router.push('/m/product/' + (item.id || item.goodsId)) }
function jumpShop(item) { router.push('/m/shop/' + item.id) }
function clearHandle() { tipsShow.value = false; listShow.value = false; shopShow.value = false; keyword.value = '' }
function emptyHandle() { searchHistory1.value = []; localStorage.setItem('searchHistory1', '[]') }

const inputHandle = debounce(() => { searchHandle() }, 1000)

async function searchView() {
  if (!keyword.value.trim()) { showNotify({ type: 'warning', message: '请输入搜索内容' }); return }
  showToast({ type: 'loading', message: '加载中', duration: 0 })
  listData.value = []; tipsShow.value = false; listShow.value = true; shopShow.value = false
  searchHistory1.value.unshift(keyword.value.trim()); searchHistory1.value = [...new Set(searchHistory1.value)]
  localStorage.setItem('searchHistory1', JSON.stringify(searchHistory1.value))
  const kw = String(keyword.value).trim(); let l = localStorage.getItem('lang') || 'cn'; l = l.replace(/"/g, '')
  try { const r = await searchKeyword({ keyword: kw, lang: l, discount: routeQ('discount') || 0 }); listData.value = r.pageList || []; showToast.clear() } catch { showToast.clear() }
}

async function searchHandle() {
  const kw = String(keyword.value).trim(); if (!kw) { tipsData.value = []; showToast('请输入搜索内容'); return }
  tipsShow.value = true; listShow.value = false; shopShow.value = false; tipsData.value = []
  let l = localStorage.getItem('lang') || 'cn'; l = l.replace(/"/g, '')
  try { const r = await searchSeller({ keyword: kw, lang: l, discount: routeQ('discount') || 0 }); const { goodsList } = r; listData.value = goodsList || []; tipsData.value = [{ keyword: kw, name: `"${kw}" 相关的店铺`, isShop: true }, ...(goodsList || [])]; showToast.clear() } catch { showToast.clear() }
}

function tipsHandle(data, isShop) {
  showToast({ type: 'loading', message: '加载中', duration: 0 })
  if (typeof data === 'string') { keyword.value = data; searchView(); return }
  const kw = String(keyword.value).trim()
  if (isShop) {
    shopShow.value = true; tipsShow.value = false; listShow.value = false
    searchHistory1.value.unshift(data.keyword); searchHistory1.value = [...new Set(searchHistory1.value)]; localStorage.setItem('searchHistory1', JSON.stringify(searchHistory1.value))
    searchSeller({ keyword: kw, isHot: '0', isPrice: '0', isNew: '0' }).then(r => { shopData.value = r.sellerList || []; showToast.clear() }).catch(() => showToast.clear())
  } else {
    searchHistory1.value.unshift(data.name); searchHistory1.value = [...new Set(searchHistory1.value)]; localStorage.setItem('searchHistory1', JSON.stringify(searchHistory1.value))
    listShow.value = true; tipsShow.value = false; shopShow.value = false; keyword.value = data.name; currentGoodsId.value = data.goodsId; listLoading.value = true; listData.value = []
    searchKeywordGoods({ goodsId: data.goodsId, pageNum: 1, pageSize: 20 }).then(r => { listData.value = r.pageList || []; listLoading.value = false; showToast.clear() }).catch(() => { listLoading.value = false; showToast.clear() })
  }
}

function routeQ(k) { return router.currentRoute?.value?.query?.[k] }
</script>

<style scoped>
.search-page { min-height: 100vh; background: var(--bg-secondary); padding-bottom: 24px; }
.section-pad { padding: 0 14px; }
/* 历史 */
.hist-header { display: flex; justify-content: space-between; padding: 12px 0; }
.hist-title { font-size: 14px; font-weight: 500; color: var(--text-primary); }
.clear-link { font-size: 12px; color: #ef4444; cursor: pointer; }
.hist-tags { display: flex; flex-wrap: wrap; gap: 8px; }
.hist-tag { padding: 5px 14px; background: var(--bg-tertiary); border-radius: 16px; font-size: 13px; color: var(--text-secondary); cursor: pointer; transition: all var(--transition-fast); }
.hist-tag:hover { background: var(--color-primary); color: #fff; }
/* 提示 */
.tip-row { display: flex; align-items: center; gap: 10px; padding: 12px 0; font-size: 14px; color: var(--text-primary); border-bottom: 1px solid var(--border-color); cursor: pointer; }
/* 商品 */
.goods-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 10px; }
.goods-card { background: var(--bg-primary); border-radius: var(--border-radius); box-shadow: var(--shadow-sm); overflow: hidden; cursor: pointer; transition: transform var(--transition-fast); }
.goods-card:active { transform: scale(0.98); }
.goods-img-wrap { position: relative; aspect-ratio: 1; background: var(--bg-secondary); display: flex; align-items: center; justify-content: center; }
.goods-img { max-width: 100%; max-height: 100%; object-fit: contain; }
.disc-badge { position: absolute; top: 0; right: 0; background: linear-gradient(135deg, #ef4444, #f97316); color: #fff; padding: 3px 8px; border-radius: 0 var(--border-radius) 0 var(--border-radius); font-size: 11px; font-weight: 700; }
.goods-info { padding: 10px 12px 12px; }
.goods-price { font-size: 17px; font-weight: 700; color: var(--color-primary); }
.goods-sold { font-size: 11px; color: var(--text-muted); margin: 4px 0; }
.goods-name { font-size: 13px; color: var(--text-primary); display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; text-overflow: ellipsis; }
.loading-tip { text-align: center; padding: 20px; color: var(--text-muted); font-size: 13px; }
/* 店铺 */
.shop-desc { font-size: 13px; color: var(--text-secondary); margin-bottom: 12px; }
.shop-desc b { color: var(--color-primary); font-weight: 600; }
.shop-list { display: flex; flex-direction: column; gap: 8px; }
.shop-row { display: flex; align-items: center; gap: 12px; background: var(--bg-primary); border-radius: var(--border-radius); padding: 12px; box-shadow: var(--shadow-sm); cursor: pointer; }
.shop-av { width: 44px; height: 44px; border-radius: 50%; object-fit: cover; }
.shop-mid { flex: 1; display: flex; flex-direction: column; gap: 4px; }
.shop-nm { font-size: 14px; font-weight: 500; color: var(--text-primary); }
.shop-sub { font-size: 11px; color: var(--text-muted); }
</style>
