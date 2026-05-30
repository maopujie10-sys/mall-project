<template>
  <div class="pc-search fade-in">
    <!-- Search Bar -->
    <div class="search-bar-section">
      <div class="search-input-wrapper">
        <el-input
          v-model="keyword"
          :placeholder="'Search products or stores...'"
          size="large"
          @keyup.enter="doSearch"
          clearable
        >
          <template #prefix>
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="8"/><path d="M21 21l-4.35-4.35"/></svg>
          </template>
          <template #append>
            <el-button type="primary" @click="doSearch" :loading="loading">Search</el-button>
          </template>
        </el-input>
      </div>

      <!-- Tab switcher -->
      <div class="search-tabs">
        <button :class="['tab', { active: searchType === 'goods' }]" @click="switchTab('goods')">Products</button>
        <button :class="['tab', { active: searchType === 'store' }]" @click="switchTab('store')">Stores</button>
      </div>
    </div>

    <!-- Sort bar (products only) -->
    <div v-if="searchType === 'goods' && results.length" class="sort-bar">
      <span :class="['sort-item', { active: sortType === 'complex' }]" @click="doSort('complex')">Comprehensive</span>
      <div class="sort-item" @click="doSort('isHot', sortParams.isHot === 2 ? 1 : 2)">
        <span :class="{ active: sortType === 'isHot' }">Sales</span>
        <i class="sort-arrow up" :class="{ active: sortParams.isHot === 1 }">&#9650;</i>
        <i class="sort-arrow down" :class="{ active: sortParams.isHot === 2 }">&#9660;</i>
      </div>
      <div class="sort-item" @click="doSort('isPrice', sortParams.isPrice === 2 ? 1 : 2)">
        <span :class="{ active: sortType === 'isPrice' }">Price</span>
        <i class="sort-arrow up" :class="{ active: sortParams.isPrice === 1 }">&#9650;</i>
        <i class="sort-arrow down" :class="{ active: sortParams.isPrice === 2 }">&#9660;</i>
      </div>
      <div class="sort-item" @click="doSort('isNew', sortParams.isNew === 2 ? 1 : 2)">
        <span :class="{ active: sortType === 'isNew' }">Newest</span>
        <i class="sort-arrow up" :class="{ active: sortParams.isNew === 1 }">&#9650;</i>
        <i class="sort-arrow down" :class="{ active: sortParams.isNew === 2 }">&#9660;</i>
      </div>
    </div>

    <!-- Results count -->
    <div v-if="keyword && !loading" class="results-count">
      Found <strong>{{ total }}</strong> {{ searchType === 'goods' ? 'products' : 'stores' }} for "<em>{{ keyword }}</em>"
    </div>

    <!-- Product Results -->
    <div v-if="searchType === 'goods'" v-loading="loading">
      <div v-if="results.length" class="product-grid">
        <ProductCard v-for="item in results" :key="item.id" :item="item" />
      </div>
      <el-empty v-if="!results.length && !loading && keyword" description="No products found" />

      <div v-if="total > pageSize" class="pagination-wrap">
        <el-pagination background layout="prev, pager, next" :current-page="pageNum" :page-size="pageSize" :total="total" @current-change="changePage" />
      </div>
    </div>

    <!-- Store Results -->
    <div v-if="searchType === 'store'" v-loading="loading">
      <div v-if="storeResults.length" class="store-grid">
        <div
          v-for="item in storeResults"
          :key="item.id"
          class="store-card card card-hover"
          @click="$router.push({ path: '/pc/store/' + item.id, query: { storeId: item.id } })"
        >
          <div class="store-top">
            <img :src="item.avatar" class="store-logo" />
            <div class="store-info">
              <h4>{{ item.name }}</h4>
              <p>{{ item.sellerGoodsNum || 0 }} products</p>
              <p>{{ formatNum(item.soldNum || 0) }} sold</p>
            </div>
          </div>
          <button class="btn btn-outline btn-sm">Visit Store &gt;</button>
        </div>
      </div>
      <el-empty v-if="!storeResults.length && !loading && keyword" description="No stores found" />
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, watch, onActivated } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { post } from '@/api/index'

const route = useRoute()
const router = useRouter()

// ===== State =====
const keyword = ref('')
const searchType = ref('goods')
const loading = ref(false)
const results = ref([])
const storeResults = ref([])
const pageNum = ref(1)
const pageSize = ref(20)
const total = ref(0)

const sortType = ref('complex')
const sortParams = reactive({ isPrice: 0, isNew: 0, isRec: 0, isHot: 0 })

// ===== Methods =====
function formatNum(n) {
  if (!n) return '0'
  return Number(n).toLocaleString()
}

function switchTab(type) {
  searchType.value = type
  pageNum.value = 1
  if (keyword.value) doSearch()
}

function doSort(type, order) {
  sortType.value = type
  if (type === 'complex') {
    sortParams.isPrice = 0; sortParams.isNew = 0; sortParams.isRec = 0; sortParams.isHot = 0
    pageNum.value = 1
    doSearch()
    return
  }
  Object.keys(sortParams).forEach(k => { if (k !== type) sortParams[k] = 0 })
  if (order) { sortParams[type] = order }
  else { sortParams[type] = sortParams[type] ? (sortParams[type] >= 2 ? 0 : sortParams[type] + 1) : 1 }
  pageNum.value = 1
  doSearch()
}

async function doSearch() {
  const q = String(keyword.value).trim()
  if (!q) return
  try {
    loading.value = true
    if (searchType.value === 'goods') {
      const encoded = encodeURIComponent(q)
      const params = {
        keyword: encoded,
        pageNum: pageNum.value,
        pageSize: pageSize.value
      }
      if (sortParams.isHot) params.isHot = sortParams.isHot
      if (sortParams.isPrice) params.isPrice = sortParams.isPrice
      if (sortParams.isNew) params.isNew = sortParams.isNew
      if (sortParams.isRec) params.isRec = sortParams.isRec

      const res = await post('/api/sellerGoods!search.action', params)
      const data = res.data || res
      results.value = data.pageList || data.result || []
      total.value = data.pageInfo?.totalElements || 0
    } else {
      const res = await post('/api/sellerGoods!search-keyword.action', { keyword: encodeURIComponent(q) })
      const data = res.data || res
      storeResults.value = data.sellerList || data.result || []
    }
  } catch {}
  finally { loading.value = false }
}

function changePage(page) {
  pageNum.value = page
  window.scrollTo({ top: 0, behavior: 'smooth' })
  doSearch()
}

// ===== Lifecycle =====
onActivated(() => {
  const k = route.query.k || route.query.q || route.query.keyword
  if (k) {
    keyword.value = typeof k === 'string' ? k.replace(/"/g, '') : String(k)
    doSearch()
  }
})
</script>

<style scoped>
.pc-search { padding: 24px 0; }

.search-bar-section { max-width: 700px; margin: 0 auto 20px; }
.search-input-wrapper { }
.search-tabs { display: flex; gap: 8px; margin-top: 12px; justify-content: center; }
.tab { padding: 8px 20px; border-radius: 20px; font-size: 13px; background: var(--bg-tertiary); color: var(--text-secondary); border: none; cursor: pointer; font-weight: 500; transition: all var(--transition-fast); }
.tab.active { background: var(--color-primary); color: white; }

.sort-bar { display: flex; gap: 24px; align-items: center; padding: 4px 0 20px; font-size: 14px; color: var(--text-secondary); user-select: none; }
.sort-item { cursor: pointer; display: flex; align-items: center; gap: 3px; }
.sort-item span.active { color: var(--color-primary); font-weight: 600; }
.sort-arrow { font-size: 8px; color: #d9d9d9; }
.sort-arrow.active { color: var(--color-primary); }
.sort-arrow + .sort-arrow { margin-left: -2px; }

.results-count { font-size: 14px; color: var(--text-secondary); margin-bottom: 16px; }
.results-count em { color: var(--color-primary); font-style: normal; }
.results-count strong { color: var(--text-primary); }

.product-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(180px, 1fr)); gap: 14px; }

/* ProductCard styles */
.product-grid :deep(.product-card) { border: 1px solid var(--border-color); border-radius: var(--border-radius-sm); overflow: hidden; padding: 0; cursor: pointer; position: relative; transition: all var(--transition-fast); background: var(--bg-primary); }
.product-grid :deep(.product-card:hover) { border-color: var(--color-primary); box-shadow: var(--shadow-lg); transform: translateY(-2px); }
.product-grid :deep(.prod-img) { width: 100%; aspect-ratio: 1; overflow: hidden; display: flex; align-items: center; justify-content: center; background: var(--bg-tertiary); }
.product-grid :deep(.prod-img img) { width: 100%; height: 100%; object-fit: contain; transition: transform 0.3s; }
.product-grid :deep(.product-card:hover .prod-img img) { transform: scale(1.05); }
.product-grid :deep(.prod-tag) { position: absolute; top: 6px; left: 6px; background: var(--color-danger); color: white; font-size: 10px; padding: 2px 6px; border-radius: 4px; font-weight: 600; }
.product-grid :deep(.prod-info) { padding: 10px; }
.product-grid :deep(.prod-price) { font-size: 16px; font-weight: 600; color: var(--color-danger); margin-bottom: 4px; }
.product-grid :deep(.prod-sold) { font-size: 10px; color: var(--text-muted); margin-bottom: 6px; }
.product-grid :deep(.prod-name) { font-size: 13px; color: var(--text-secondary); overflow: hidden; text-overflow: ellipsis; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; line-height: 1.4; margin-bottom: 8px; min-height: 36px; }
.product-grid :deep(.prod-actions) { display: flex; justify-content: space-between; align-items: center; border-top: 1px solid var(--border-color); padding-top: 8px; }
.product-grid :deep(.buy-btn) { font-size: 12px; font-weight: 600; color: var(--color-primary); cursor: pointer; }
.product-grid :deep(.star-icon) { font-size: 18px; cursor: pointer; color: var(--text-muted); }
.product-grid :deep(.star-icon.filled) { color: var(--color-accent); }

.pagination-wrap { display: flex; justify-content: center; padding: 40px 0; }

/* Store grid */
.store-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 16px; }
.store-card { display: flex; justify-content: space-between; align-items: center; padding: 20px; cursor: pointer; }
.store-top { display: flex; gap: 14px; align-items: center; }
.store-logo { width: 64px; height: 64px; border-radius: 50%; object-fit: cover; }
.store-info h4 { font-size: 15px; font-weight: 600; margin-bottom: 4px; }
.store-info p { font-size: 12px; color: var(--text-muted); margin-bottom: 2px; }

@media (max-width: 768px) {
  .search-bar-section { max-width: 100%; }
  .store-grid { grid-template-columns: 1fr; }
}
</style>
