<template>
  <div ref="scrollRef" class="home-page">
    <!-- 搜索栏 -->
    <div class="search-section">
      <router-link to="/m/search">
        <van-search shape="round" input-align="center" readonly>
          <template #right-icon>
            <div class="search-placeholder">
              <svg width="18" height="18" viewBox="0 0 20 20" fill="none">
                <circle cx="9" cy="9" r="6" stroke="#94a3b8" stroke-width="2"/>
                <path d="M14 14l4 4" stroke="#94a3b8" stroke-width="2" stroke-linecap="round"/>
              </svg>
              <span>{{ $t('common.search') }}</span>
            </div>
          </template>
        </van-search>
      </router-link>
    </div>

    <!-- Banner 轮播 -->
    <div class="section banner-section">
      <van-skeleton :row="1" :loading="loading.banner">
        <van-swipe
          v-if="banner.length"
          class="banner-swipe"
          :autoplay="3000"
          indicator-color="white"
        >
          <van-swipe-item v-for="(item, index) in banner" :key="index">
            <div class="banner-image-wrapper" @click="handleBannerJump(item)">
              <img :src="item.imgUrl" alt="" class="banner-image" />
            </div>
          </van-swipe-item>
        </van-swipe>
      </van-skeleton>
    </div>

    <!-- 分类导航 -->
    <div class="section category-section">
      <van-skeleton :row="2" :loading="loading.list">
        <div class="category-scroll">
          <div
            v-for="item in categoryList"
            :key="item.categoryId"
            class="category-item"
            @click="openClass(item)"
          >
            <div class="category-icon-wrap">
              <img
                v-lazy="item.iconImg || defaultGoodsImg"
                :src="item.iconImg || defaultGoodsImg"
                class="category-icon"
              />
            </div>
            <span class="category-name">{{ item.name }}</span>
          </div>
        </div>
      </van-skeleton>
    </div>

    <!-- 每日上新 -->
    <div class="section" v-if="dailyNewArrivalList.length > 0">
      <div class="section-header">
        <h3 class="section-title">{{ $t('common.dailyNew') }}</h3>
      </div>
      <van-skeleton :row="1" :loading="loading.newest">
        <div class="new-arrivals-scroll">
          <div
            v-for="(item, index) in dailyNewArrivalList"
            :key="index"
            class="new-arrival-item"
            @click="openProduct(item)"
          >
            <div class="new-arrival-img-wrap">
              <img
                v-lazy="item.imgUrl1 || defaultGoodsImg"
                :src="item.imgUrl1 || defaultGoodsImg"
                class="new-arrival-img"
              />
            </div>
            <span class="new-arrival-price">${{ priceFormat(item?.discountPrice || item.sellingPrice) }}</span>
          </div>
        </div>
      </van-skeleton>
    </div>

    <!-- 推荐产品 -->
    <div class="section" v-if="productList.length > 0">
      <div class="section-header">
        <h3 class="section-title">{{ $t('common.recommendProducts') }}</h3>
      </div>
      <van-skeleton :row="4" :loading="loading.product">
        <van-swipe @change="handleChangeSwiper" class="product-swipe">
          <van-swipe-item v-for="page in productPage" :key="page">
            <div class="product-grid">
              <div
                v-for="item in productList.filter((_it, n) => (page - 1) * 4 <= n && n < page * 4)"
                :key="item.id"
                class="product-card"
                @click="openProduct(item)"
              >
                <div class="product-card-img-wrap">
                  <img :src="item.imgUrl1 || defaultGoodsImg" class="product-card-img" />
                </div>
                <div class="product-card-info">
                  <span class="product-card-price">${{ priceFormat(item.discountPrice || item.sellingPrice) }}</span>
                  <p class="product-card-sold">{{ $t('common.sales') }} {{ priceFormatInt(item?.soldNum) }}</p>
                  <p class="product-card-name">{{ textOmit(item.name, 24) }}</p>
                </div>
                <div class="discount-badge" v-if="item.discountRatio >= 0.01">
                  <span>{{ (item.discountRatio * 100).toFixed(0) }}% OFF</span>
                </div>
              </div>
            </div>
          </van-swipe-item>
          <template #indicator>
            <div class="custom-indicators">
              <span
                v-for="(_, index) in productPage"
                :key="index"
                :class="['indicator-dot', { active: current === index }]"
              />
            </div>
          </template>
        </van-swipe>
      </van-skeleton>
    </div>

    <!-- 推荐店铺 -->
    <div class="section">
      <div class="section-header">
        <h3 class="section-title">{{ $t('common.recommendShops') }}</h3>
      </div>
      <van-skeleton :row="4" :loading="loading.shop">
        <div class="shop-list">
          <div v-for="item in recomendedStoreShopList" :key="item.key" class="shop-card">
            <div class="shop-card-top">
              <div class="shop-avatar-wrap">
                <img :src="item.avatar" class="shop-avatar" />
              </div>
              <div class="shop-info">
                <div class="shop-info-left">
                  <span class="shop-name">{{ item.name }}</span>
                  <p class="shop-stat">{{ $t('common.follow') }}: {{ priceFormatInt((+item?.fake || 0) + (+item?.focusNum || 0), true) }}</p>
                  <p>{{ $t('common.products') }}: {{ priceFormatInt(item.sellerGoodsNum, true) }}</p>
                </div>
                <button class="shop-visit-btn" @click="jumpShop(item)">
                  {{ $t('common.visitShop') }} &rsaquo;
                </button>
              </div>
            </div>
            <div class="shop-card-bottom">
              <span>{{ $t('common.positiveRate') }}: {{ Math.floor(item.highOpinion * 100) || 100 }}%</span>
              <span>{{ $t('common.soldOut') }}: {{ priceFormatInt(item.soldNum, 1) }}</span>
            </div>
          </div>
        </div>
      </van-skeleton>
    </div>

    <!-- 热销产品 -->
    <div class="section" v-if="recomendedStoreProductList.length > 0">
      <div class="section-header">
        <h3 class="section-title">{{ $t('common.hotProducts') }}</h3>
      </div>
      <div class="hot-products-grid">
        <div
          v-for="item in recomendedStoreProductList"
          :key="item.key"
          class="hot-product-card"
          @click="openProduct(item)"
        >
          <div class="hot-product-img-wrap">
            <img :src="item.imgUrl1 || defaultGoodsImg" class="hot-product-img" />
          </div>
          <div class="hot-product-info">
            <span class="hot-product-price">${{
              priceFormat(item.discountPrice) || priceFormat(item.sellingPrice)
            }}</span>
            <p class="hot-product-sold">{{ $t('common.sales') }}: {{ priceFormatInt(item.soldNum) }}</p>
            <p class="hot-product-name">{{ textOmit(item.name) }}</p>
          </div>
          <div class="discount-badge" v-if="item.discountRatio >= 0.01">
            <span>{{ (item.discountRatio * 100).toFixed(0) }}% OFF</span>
          </div>
        </div>
      </div>
    </div>

    <!-- 返回顶部 -->
    <transition name="fade">
      <div v-show="isShowTopBtn" class="back-to-top" @click="handleToTop">
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none">
          <path d="M12 20V4M5 11l7-7 7 7" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>
      </div>
    </transition>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, onBeforeUnmount, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import {
  Search as VanSearch,
  Swipe as VanSwipe,
  SwipeItem as VanSwipeItem,
  Skeleton as VanSkeleton
} from 'vant'
import { useUserStore } from '@/stores/user'
import {
  apiGetNewGoods,
  apiGetRecommendGoods,
  getSellerList,
  apiGetBannerList,
  apiQueryMessages
} from '@/api/home'

const router = useRouter()
const route = useRoute()
const userStore = useUserStore()

// ===== Constants =====
const defaultGoodsImg = 'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMjAwIiBoZWlnaHQ9IjIwMCIgdmlld0JveD0iMCAwIDIwMCAyMDAiIGZpbGw9Im5vbmUiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+PHJlY3Qgd2lkdGg9IjIwMCIgaGVpZ2h0PSIyMDAiIGZpbGw9IiNmMWY1ZjkiLz48cGF0aCBkPSJNNzAgOTBoNjB2NjBINzB6IiBzdHJva2U9IiNjYmQ1ZTEiIHN0cm9rZS13aWR0aD0iMiIvPjxjaXJjbGUgY3g9Ijg1IiBjeT0iODAiIHI9IjEwIiBzdHJva2U9IiNjYmQ1ZTEiIHN0cm9rZS13aWR0aD0iMiIvPjwvc3ZnPg=='

// ===== State =====
const scrollRef = ref(null)
const isShowTopBtn = ref(false)
const current = ref(0)
const banner = ref([])
const dailyNewArrivalList = ref([])
const recomendedStoreShopList = ref([])
const recomendedStoreProductList = ref([])
const productList = ref([])
const categoryList = ref([])
const productPage = ref(1)
const queryMessages = ref(0)
let timeInterval = null

const loading = reactive({
  banner: true,
  list: true,
  product: true,
  newest: true,
  shop: true
})

// ===== Utility Functions (preserved from original) =====
function _toFixed(num, decimal) {
  num = num.toString()
  let index = num.indexOf('.')
  if (index !== -1) {
    num = num.substring(0, decimal + index + 1)
  } else {
    num = num.substring(0)
  }
  return parseFloat(num).toFixed(decimal)
}

function priceFormat(num, int) {
  if (num && Number(num)) {
    const numStr = _toFixed(num, 2)
    const numPre = numStr.slice(0, numStr.indexOf('.'))
    const numRi = numStr.slice(numStr.indexOf('.') + 1)
    const intStr = numPre.toString().replace(/(\d)(?=(\d{3})+(?!\d))/g, '$1,')
    const floatStr = numRi ? `.${numRi.length < 2 ? numRi + '0' : numRi}` : '.00'
    return int ? `${intStr}` : `${intStr}${floatStr}`
  } else {
    return 0
  }
}

function priceFormatInt(num) {
  if (num && Number(num)) {
    const numStr = _toFixed(num, 2)
    const numPre = numStr.slice(0, numStr.indexOf('.'))
    return numPre.toString().replace(/(\d)(?=(\d{3})+(?!\d))/g, '$1,')
  } else {
    return 0
  }
}

function textOmit(text, maxLen = 48) {
  if (!text) return ''
  return text.length > maxLen ? text.slice(0, maxLen) + '...' : text
}

function isLogin() {
  return !!(userStore.token || localStorage.getItem('token'))
}

// ===== Lifecycle =====
onMounted(() => {
  init()
  setTimeout(() => {
    window.addEventListener('scroll', handleScroll)
  }, 1000)
})

onBeforeUnmount(() => {
  window.removeEventListener('scroll', handleScroll)
  clearInterval(timeInterval)
})

// ===== Watchers =====
watch(() => route.path, (to, from) => {
  if (from === '/language') {
    init()
  }
})

// ===== Methods (preserved from original) =====
async function init() {
  requestBanner()
  requireRecommendNew()
  getMessageNum()
  requestHomeCategory()
  home_SellerList()
  timeInterval = setInterval(() => {
    getMessageNum()
  }, 10000)
}

async function getMessageNum() {
  try {
    const res = await apiQueryMessages({ loginType: 'user' })
    queryMessages.value = res
  } catch (e) {
    // silent
  }
}

async function requireRecommendNew() {
  // type 0:每日新品 1:推荐产品 2:热销产品
  if (localStorage.getItem('index_recomendedStoreProductList')) {
    recomendedStoreProductList.value = JSON.parse(localStorage.getItem('index_recomendedStoreProductList'))
    loading.product = false
  }
  if (localStorage.getItem('index_dailyNewArrivalList')) {
    dailyNewArrivalList.value = JSON.parse(localStorage.getItem('index_dailyNewArrivalList'))
    loading.newest = false
  }
  if (localStorage.getItem('index_productList')) {
    productList.value = JSON.parse(localStorage.getItem('index_productList'))
    productPage.value = Math.ceil(productList.value.length / 4)
    loading.product = false
  }

  try {
    const [recommendRes, dailyNewArrivalRes, recomendedStoreProductRes] = await Promise.all([
      apiGetNewGoods({ pageNum: 1, pageSize: 24, type: 1 }),
      apiGetNewGoods({ pageNum: 1, pageSize: 24, type: 0 }),
      apiGetNewGoods({ pageNum: 1, pageSize: 24, type: 2 })
    ])

    productList.value = recommendRes.result
    productPage.value = Math.ceil(productList.value.length / 4)
    loading.product = false

    dailyNewArrivalList.value = [...dailyNewArrivalRes.result, ...dailyNewArrivalRes.result]
    loading.newest = false

    recomendedStoreProductList.value = recomendedStoreProductRes.result

    localStorage.setItem('index_productList', JSON.stringify(productList.value))
    localStorage.setItem('index_dailyNewArrivalList', JSON.stringify(dailyNewArrivalList.value))
    localStorage.setItem('index_recomendedStoreProductList', JSON.stringify(recomendedStoreProductList.value))
  } catch (e) {
    loading.product = false
    loading.newest = false
  }
}

async function requestHomeCategory() {
  if (localStorage.getItem('index_categoryList')) {
    categoryList.value = JSON.parse(localStorage.getItem('index_categoryList'))
    loading.list = false
  }
  try {
    const res = await apiGetRecommendGoods({ pageNum: 1, pageSize: 20 })
    categoryList.value = res.pageList
    loading.list = false
    localStorage.setItem('index_categoryList', JSON.stringify(categoryList.value))
  } catch (e) {
    loading.list = false
  }
}

async function requestBanner() {
  if (localStorage.getItem('index_banner')) {
    banner.value = JSON.parse(localStorage.getItem('index_banner'))
    loading.banner = false
  }
  try {
    const res = await apiGetBannerList({
      type: 'h5',
      pageNum: 1,
      pageSize: 10
    })
    if (res.result.length === 0) {
      banner.value = [
        { imgUrl: '/assets/banner0.png' },
        { imgUrl: '/assets/banner1.jpg' },
        { imgUrl: '/assets/banner2.png' }
      ]
    } else {
      banner.value = res.result
    }
  } catch (error) {
    banner.value = [
      { imgUrl: '/assets/banner0.png' },
      { imgUrl: '/assets/banner1.jpg' },
      { imgUrl: '/assets/banner2.png' }
    ]
  }
  localStorage.setItem('index_banner', JSON.stringify(banner.value))
  const Image = document.createElement('img')
  Image.src = banner.value[0].imgUrl
  Image.onload = () => { loading.banner = false }
}

function home_SellerList() {
  if (localStorage.getItem('index_recomendedStoreShopList')) {
    recomendedStoreShopList.value = JSON.parse(localStorage.getItem('index_recomendedStoreShopList'))
    loading.shop = false
  }
  getSellerList({
    pageNum: 1,
    pageSize: 5,
    isRec: 1
  }).then((res) => {
    recomendedStoreShopList.value = res.pageList
    loading.shop = false
    localStorage.setItem('index_recomendedStoreShopList', JSON.stringify(recomendedStoreShopList.value))
  }).catch(() => {
    loading.shop = false
  })
}

function handleBannerJump(item) {
  if (window.plus) {
    window.plus.runtime.openURL(item.link)
  } else {
    window.open(item.link)
  }
}

function handleToTop() {
  scrollTo({ top: 0, left: 0, behavior: 'smooth' })
}

function handleChangeSwiper(index) {
  current.value = index
}

function jumpShop(item) {
  sessionStorage.removeItem('shopState')
  router.push(`/m/shop/${item.id}`)
}

function openProduct(item) {
  router.push('/m/product/' + item.id)
}

function openClass(item) {
  sessionStorage.removeItem('classificationState')
  router.push({
    path: '/m/categories',
    query: { categoryId: item.categoryId, className: item.name }
  })
}

function handleScroll() {
  const scrollTop = document.documentElement.scrollTop || document.body.scrollTop
  isShowTopBtn.value = scrollTop > 500
}
</script>

<style scoped>
.home-page {
  background: var(--bg-secondary);
  padding: 0 14px 32px;
  min-height: 100vh;
}

/* ===== 搜索 ===== */
.search-section {
  padding-top: 4px;
  margin-bottom: 10px;
}
.search-section :deep(.van-search) {
  padding: 0;
  background: transparent;
}
.search-section :deep(.van-search__content) {
  background: var(--bg-primary);
  border-radius: 24px;
  box-shadow: var(--shadow-sm);
}
.search-placeholder {
  display: flex;
  align-items: center;
  gap: 8px;
  color: var(--text-muted);
  font-size: 14px;
  width: 100%;
  justify-content: center;
}

/* ===== 通用 ===== */
.section {
  margin-bottom: 22px;
}

.section-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 12px;
  padding: 0 4px;
}

.section-title {
  font-size: 15px;
  font-weight: 600;
  color: var(--text-primary);
  position: relative;
  padding-left: 12px;
}

.section-title::before {
  content: '';
  position: absolute;
  left: 0;
  top: 50%;
  transform: translateY(-50%);
  width: 3px;
  height: 15px;
  background: linear-gradient(180deg, var(--color-primary), var(--color-primary-light));
  border-radius: 2px;
}

/* ===== Banner ===== */
.banner-section {
  margin-bottom: 18px;
}

.banner-swipe {
  border-radius: var(--border-radius);
  overflow: hidden;
  box-shadow: var(--shadow-md);
}

.banner-image-wrapper {
  border-radius: var(--border-radius);
  overflow: hidden;
  cursor: pointer;
}

.banner-image {
  width: 100%;
  aspect-ratio: 2.5 / 1;
  object-fit: cover;
  display: block;
}

.banner-section :deep(.van-swipe__indicator) {
  background: rgba(255, 255, 255, 0.5);
}

.banner-section :deep(.van-swipe__indicator--active) {
  background: var(--color-primary);
}

/* ===== 分类导航 ===== */
.category-scroll {
  display: flex;
  gap: 10px;
  overflow-x: auto;
  padding: 4px 0 8px;
  scroll-behavior: smooth;
  -webkit-overflow-scrolling: touch;
}

.category-scroll::-webkit-scrollbar { display: none; }
.category-scroll { scrollbar-width: none; -ms-overflow-style: none; }

.category-item {
  flex-shrink: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 6px;
  width: 76px;
  cursor: pointer;
  transition: transform var(--transition-fast);
}

.category-item:active { transform: scale(0.95); }

.category-icon-wrap {
  width: 60px;
  height: 60px;
  background: var(--bg-primary);
  border-radius: var(--border-radius);
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: var(--shadow-sm);
  border: 1px solid var(--border-color);
  overflow: hidden;
  transition: box-shadow var(--transition-fast), border-color var(--transition-fast);
}

.category-icon-wrap:hover {
  box-shadow: var(--shadow-md);
  border-color: var(--color-primary-light);
}

.category-icon {
  width: 44px;
  height: 44px;
  object-fit: contain;
}

.category-name {
  font-size: 11px;
  color: var(--text-primary);
  text-align: center;
  line-height: 1.3;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  word-break: break-word;
  max-width: 76px;
}

/* ===== 每日上新 ===== */
.new-arrivals-scroll {
  display: flex;
  gap: 10px;
  overflow-x: auto;
  padding: 4px 0 8px;
  scroll-behavior: smooth;
  -webkit-overflow-scrolling: touch;
}

.new-arrivals-scroll::-webkit-scrollbar { display: none; }
.new-arrivals-scroll { scrollbar-width: none; -ms-overflow-style: none; }

.new-arrival-item {
  flex-shrink: 0;
  width: 120px;
  cursor: pointer;
  transition: transform var(--transition-fast);
}

.new-arrival-item:active { transform: scale(0.97); }

.new-arrival-img-wrap {
  width: 120px;
  height: 120px;
  background: var(--bg-primary);
  border-radius: var(--border-radius);
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
  box-shadow: var(--shadow-sm);
  border: 1px solid var(--border-color);
  margin-bottom: 8px;
}

.new-arrival-img {
  width: auto;
  height: auto;
  max-width: 90%;
  max-height: 90%;
  object-fit: contain;
}

.new-arrival-price {
  font-size: 15px;
  font-weight: 600;
  color: var(--color-primary);
  display: block;
  text-align: center;
}

/* ===== 推荐产品 ===== */
.product-swipe :deep(.van-swipe__indicator) {
  display: none;
}

.product-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 10px;
  padding: 0 2px;
}

.product-card {
  background: var(--bg-primary);
  border-radius: var(--border-radius);
  box-shadow: var(--shadow-sm);
  overflow: hidden;
  position: relative;
  cursor: pointer;
  transition: transform var(--transition-fast), box-shadow var(--transition-fast);
  display: flex;
  flex-direction: column;
}

.product-card:active {
  transform: scale(0.98);
  box-shadow: var(--shadow-md);
}

.product-card-img-wrap {
  padding: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--bg-secondary);
  aspect-ratio: 1;
}

.product-card-img {
  max-width: 100%;
  max-height: 100%;
  object-fit: contain;
}

.product-card-info {
  padding: 10px 12px 12px;
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 3px;
}

.product-card-price {
  font-size: 17px;
  font-weight: 700;
  color: var(--color-primary);
}

.product-card-sold {
  font-size: 11px;
  color: var(--text-muted);
}

.product-card-name {
  font-size: 13px;
  color: var(--text-primary);
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  text-overflow: ellipsis;
  line-height: 1.4;
  word-break: break-word;
}

.discount-badge {
  position: absolute;
  top: 0;
  right: 0;
  background: linear-gradient(135deg, #ef4444, #f97316);
  color: #fff;
  padding: 3px 8px;
  border-radius: 0 var(--border-radius) 0 var(--border-radius);
  font-size: 11px;
  font-weight: 700;
  line-height: 1.2;
  box-shadow: 0 2px 8px rgba(239, 68, 68, 0.3);
}

.custom-indicators {
  display: flex;
  justify-content: center;
  gap: 6px;
  padding: 12px 0 2px;
}

.indicator-dot {
  width: 20px;
  height: 3px;
  background: var(--border-color);
  border-radius: 2px;
  transition: all var(--transition-fast);
}

.indicator-dot.active {
  background: var(--color-primary);
  width: 32px;
}

/* ===== 推荐店铺 ===== */
.shop-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.shop-card {
  background: var(--bg-primary);
  border-radius: var(--border-radius);
  box-shadow: var(--shadow-sm);
  overflow: hidden;
  transition: box-shadow var(--transition-fast);
}

.shop-card:hover { box-shadow: var(--shadow-md); }

.shop-card-top {
  display: flex;
  align-items: flex-start;
  padding: 12px;
  gap: 12px;
}

.shop-avatar-wrap {
  width: 52px;
  height: 52px;
  flex-shrink: 0;
  border-radius: 50%;
  overflow: hidden;
  box-shadow: var(--shadow-sm);
}

.shop-avatar {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.shop-info {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.shop-info-left {
  display: flex;
  flex-direction: column;
  gap: 3px;
}

.shop-name {
  font-size: 15px;
  font-weight: 600;
  color: var(--text-primary);
}

.shop-stat { margin-top: 3px; }

.shop-info-left p {
  font-size: 11px;
  color: var(--text-secondary);
}

.shop-visit-btn {
  flex-shrink: 0;
  padding: 5px 14px;
  border-radius: 20px;
  font-size: 11px;
  font-weight: 500;
  background: linear-gradient(135deg, var(--color-primary), var(--color-primary-dark));
  color: #fff;
  border: none;
  cursor: pointer;
  white-space: nowrap;
  transition: opacity var(--transition-fast), transform var(--transition-fast);
}

.shop-visit-btn:hover {
  opacity: 0.9;
  transform: translateY(-1px);
}

.shop-card-bottom {
  display: flex;
  justify-content: space-between;
  padding: 10px 14px;
  border-top: 1px solid var(--border-color);
  font-size: 11px;
  color: var(--text-secondary);
}

/* ===== 热销产品 ===== */
.hot-products-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 10px;
}

.hot-product-card {
  background: var(--bg-primary);
  border-radius: var(--border-radius);
  box-shadow: var(--shadow-sm);
  overflow: hidden;
  position: relative;
  cursor: pointer;
  transition: transform var(--transition-fast), box-shadow var(--transition-fast);
}

.hot-product-card:active {
  transform: scale(0.98);
  box-shadow: var(--shadow-md);
}

.hot-product-img-wrap {
  padding: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--bg-secondary);
  aspect-ratio: 1;
}

.hot-product-img {
  max-width: 100%;
  max-height: 100%;
  object-fit: contain;
}

.hot-product-info {
  padding: 10px 12px 12px;
}

.hot-product-price {
  font-size: 17px;
  font-weight: 700;
  color: var(--color-primary);
}

.hot-product-sold {
  font-size: 11px;
  color: var(--text-muted);
  margin: 4px 0;
}

.hot-product-name {
  font-size: 13px;
  color: var(--text-primary);
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  text-overflow: ellipsis;
}

/* ===== 返回顶部 ===== */
.back-to-top {
  position: fixed;
  bottom: 80px;
  right: 16px;
  width: 38px;
  height: 38px;
  border-radius: 50%;
  background: var(--color-primary);
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: var(--shadow-lg);
  cursor: pointer;
  z-index: 50;
  transition: all var(--transition-fast);
}

.back-to-top:hover {
  transform: translateY(-2px);
  box-shadow: var(--shadow-xl);
}

.back-to-top:active { transform: scale(0.9); }

/* ===== 动画 ===== */
.fade-enter-active,
.fade-leave-active { transition: opacity 0.3s ease; }
.fade-enter-from,
.fade-leave-to { opacity: 0; }
</style>
