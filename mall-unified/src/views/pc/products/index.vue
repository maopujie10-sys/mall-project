<template>
  <div class="pc-products fade-in">
    <div class="products-layout">
      <!-- Left sidebar: Category filter -->
      <aside class="filter-sidebar">
        <h2 class="filter-title">Categories</h2>
        <ul class="filter-list">
          <li
            :class="['filter-item', { active: currentFilterId === '' }]"
            @click="selectCategory('')"
          >
            All Products
          </li>
          <li
            v-for="(cat, idx) in categoryTree"
            :key="cat.categoryId || idx"
            :class="['filter-item', { active: currentFilterId === cat.categoryId }]"
            @click="selectCategory(cat)"
          >
            <div class="filter-item-label">
              {{ cat.name }}
              <i v-if="cat.subList?.length" class="expand-icon" :class="{ expanded: expandedCat === cat.categoryId }">&#9660;</i>
            </div>
            <ul v-if="expandedCat === cat.categoryId && cat.subList?.length" class="sub-list">
              <li
                v-for="sub in cat.subList"
                :key="sub.categoryId"
                :class="['sub-item', { active: currentSubId === sub.categoryId }]"
                @click.stop="selectSubCategory(sub)"
              >
                {{ sub.name }}
              </li>
            </ul>
          </li>
        </ul>
      </aside>

      <!-- Main content: Sort bar + Product grid + Pagination -->
      <div class="products-main">
        <!-- Sort bar -->
        <div class="sort-bar">
          <span :class="['sort-item', { active: sortType === 'complex' }]" @click="doSort('complex')">
            Comprehensive
          </span>
          <div class="sort-item sort-dual" @click="doSort('isHot', sortParams.isHot === 2 ? 1 : 2)">
            <span :class="{ active: sortType === 'isHot' }">Sales</span>
            <div class="sort-arrows">
              <i :class="['arrow up', { active: sortParams.isHot === 1 }]">&#9650;</i>
              <i :class="['arrow down', { active: sortParams.isHot === 2 }]">&#9660;</i>
            </div>
          </div>
          <div class="sort-item sort-dual" @click="doSort('isPrice', sortParams.isPrice === 2 ? 1 : 2)">
            <span :class="{ active: sortType === 'isPrice' }">Price</span>
            <div class="sort-arrows">
              <i :class="['arrow up', { active: sortParams.isPrice === 1 }]">&#9650;</i>
              <i :class="['arrow down', { active: sortParams.isPrice === 2 }]">&#9660;</i>
            </div>
          </div>
          <div class="sort-item sort-dual" @click="doSort('isNew', sortParams.isNew === 2 ? 1 : 2)">
            <span :class="{ active: sortType === 'isNew' }">Newest</span>
            <div class="sort-arrows">
              <i :class="['arrow up', { active: sortParams.isNew === 1 }]">&#9650;</i>
              <i :class="['arrow down', { active: sortParams.isNew === 2 }]">&#9660;</i>
            </div>
          </div>
        </div>

        <!-- Product grid -->
        <div v-loading="loading" class="product-area">
          <div v-if="products.length" class="product-grid">
            <ProductCard v-for="item in products" :key="item.id" :item="item" />
          </div>
          <el-empty v-if="!products.length && !loading" description="No products found" />

          <!-- Pagination -->
          <div v-if="total > pageSize" class="pagination-wrap">
            <el-pagination
              background
              layout="prev, pager, next"
              :current-page="pageNum"
              :page-size="pageSize"
              :total="total"
              @current-change="changePage"
            />
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onActivated, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { post, get } from '@/api/index'
import ProductCard from './ProductCard.vue'

const route = useRoute()
const router = useRouter()

// ===== State =====
const loading = ref(false)
const categoryTree = ref([])
const expandedCat = ref('')
const currentFilterId = ref('')
const currentSubId = ref('')
const products = ref([])
const pageNum = ref(1)
const pageSize = ref(20)
const total = ref(0)

const sortType = ref('complex')
const sortParams = reactive({ isPrice: 0, isNew: 0, isRec: 0, isHot: 0 })
let lastFilterId = ''

// ===== Methods =====
async function getCategoryTree() {
  try {
    const res = await post('/api/category!tree.action')
    categoryTree.value = res.data || []
  } catch {}
}

function selectCategory(cat) {
  if (!cat) {
    currentFilterId.value = ''
    currentSubId.value = ''
    expandedCat.value = ''
    pageNum.value = 1
    fetchProducts()
    return
  }
  currentFilterId.value = cat.categoryId
  expandedCat.value = expandedCat.value === cat.categoryId ? '' : cat.categoryId
  currentSubId.value = ''
  pageNum.value = 1
  // Update URL
  router.replace({ path: '/pc/products', query: { id: cat.categoryId } })
  fetchProducts({ categoryId: cat.categoryId })
}

function selectSubCategory(sub) {
  currentSubId.value = sub.categoryId
  pageNum.value = 1
  fetchProducts({ categoryId: sub.categoryId })
}

function doSort(type, order) {
  sortType.value = type
  if (type === 'complex') {
    sortParams.isPrice = 0
    sortParams.isNew = 0
    sortParams.isRec = 0
    sortParams.isHot = 0
    pageNum.value = 1
    fetchProducts()
    return
  }
  // Reset other sorts
  Object.keys(sortParams).forEach(k => {
    if (k !== type) sortParams[k] = 0
  })
  if (order) {
    sortParams[type] = order
  } else {
    sortParams[type] = sortParams[type] ? (sortParams[type] >= 2 ? 0 : sortParams[type] + 1) : 1
  }
  pageNum.value = 1
  fetchProducts({ ...sortParams })
}

async function fetchProducts(params = {}) {
  try {
    loading.value = true
    const queryParams = {
      pageNum: pageNum.value,
      pageSize: pageSize.value,
      ...sortParams
    }
    const categoryId = params.categoryId || currentFilterId.value || currentSubId.value || route.query.id
    if (categoryId) queryParams.categoryId = categoryId
    Object.assign(queryParams, params)
    delete queryParams.isHot; delete queryParams.isPrice; delete queryParams.isNew; delete queryParams.isRec
    // Only include active sort
    if (sortParams.isHot) queryParams.isHot = sortParams.isHot
    if (sortParams.isPrice) queryParams.isPrice = sortParams.isPrice
    if (sortParams.isNew) queryParams.isNew = sortParams.isNew
    if (sortParams.isRec) queryParams.isRec = sortParams.isRec

    const res = await post('/api/sellerGoods!list.action', queryParams)
    const data = res.data || res
    products.value = data.pageList || data.result || []
    total.value = data.pageInfo?.totalElements || 0
  } catch { products.value = [] }
  finally { loading.value = false }
}

function changePage(page) {
  pageNum.value = page
  window.scrollTo({ top: 0, behavior: 'smooth' })
  fetchProducts()
}

// ===== Lifecycle =====
onMounted(async () => {
  await getCategoryTree()
  const queryId = route.query.id
  if (queryId) {
    currentFilterId.value = queryId
    // Find parent if exists
    const parentCat = categoryTree.value.find(c => c.categoryId === queryId)
    if (parentCat) expandedCat.value = queryId
  }
  fetchProducts()
})
</script>

<style scoped>
.pc-products { padding: 8px 0 40px; }

.products-layout { display: flex; gap: 24px; align-items: flex-start; }

/* Filter Sidebar */
.filter-sidebar { width: 200px; flex-shrink: 0; border-right: 1px solid var(--border-color); padding-right: 16px; }
.filter-title { font-size: 16px; font-weight: 700; padding: 16px 0; border-bottom: 1px solid var(--border-color); margin-bottom: 12px; }
.filter-list { list-style: none; padding: 0; margin: 0; }
.filter-item { font-size: 13px; color: var(--text-secondary); padding: 10px 8px; cursor: pointer; border-radius: 6px; transition: all var(--transition-fast); }
.filter-item:hover { color: var(--color-primary); }
.filter-item.active { color: var(--color-primary); font-weight: 600; background: rgba(99,102,241,0.06); border-right: 2px solid var(--color-primary); }
.filter-item-label { display: flex; justify-content: space-between; align-items: center; }
.expand-icon { font-size: 8px; transition: transform 0.2s; color: var(--text-muted); }
.expand-icon.expanded { transform: rotate(180deg); }
.sub-list { list-style: none; padding: 0; margin: 4px 0 0 12px; }
.sub-item { font-size: 12px; padding: 6px 8px; cursor: pointer; border-radius: 4px; color: var(--text-secondary); }
.sub-item:hover, .sub-item.active { color: var(--color-primary); }
.sub-item.active { font-weight: 500; }

/* Main Content */
.products-main { flex: 1; min-width: 0; }
.sort-bar { display: flex; gap: 24px; align-items: center; padding: 12px 0 16px; font-size: 14px; color: var(--text-secondary); user-select: none; }
.sort-item { cursor: pointer; display: flex; align-items: center; gap: 4px; }
.sort-item.active { color: var(--color-primary); font-weight: 600; }
.sort-arrows { display: flex; flex-direction: column; line-height: 0.6; }
.sort-arrows .arrow { font-size: 8px; color: #d9d9d9; }
.sort-arrows .arrow.active { color: var(--color-primary); }

.product-area { min-height: 300px; }
.product-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(180px, 1fr)); gap: 14px; }
.pagination-wrap { display: flex; justify-content: center; padding: 40px 0; }

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
.product-grid :deep(.buy-btn:hover) { text-decoration: underline; }
.product-grid :deep(.star-icon) { font-size: 18px; cursor: pointer; color: var(--text-muted); }
.product-grid :deep(.star-icon.filled) { color: var(--color-accent); }

@media (max-width: 768px) { .filter-sidebar { display: none; } }
</style>
