<template>
  <div class="pc-home fade-in">
    <!-- Banner Carousel -->
    <section class="banner-section" v-loading="bannerLoading">
      <el-row :gutter="6">
        <el-col :xs="24" :md="16">
          <div class="banner-left">
            <div class="banner-swiper" @mouseenter="pauseBanner" @mouseleave="playBanner">
              <div class="banner-slide" v-for="item in mainBanners" :key="item.id" @click="goLink(item.link)">
                <img :src="item.imgUrl" alt="" />
              </div>
            </div>
          </div>
        </el-col>
        <el-col :xs="24" :md="8">
          <div class="banner-right">
            <div class="banner-right-grid" v-for="(chunk, ci) in bannerRightChunks" :key="ci">
              <div class="banner-right-item" v-for="(item, idx) in chunk" :key="idx" @click="goLink(item.link)">
                <img :src="item.imgUrl" alt="" />
              </div>
            </div>
          </div>
        </el-col>
      </el-row>
    </section>

    <!-- Category Classification -->
    <section class="category-section" v-loading="catLoading">
      <div class="section-header">
        <h2>Recommended Categories</h2>
        <span class="see-all" @click="$router.push('/pc/categories')">View All &rarr;</span>
      </div>
      <div class="category-scroll" ref="catScrollRef" @mouseenter="pauseCat" @mouseleave="playCat">
        <div
          v-for="item in categoryList"
          :key="item.categoryId"
          class="category-item"
          @click="$router.push({ path: '/pc/products', query: { id: item.categoryId } })"
        >
          <div class="cat-img-box">
            <img :src="item.iconImg" alt="" />
          </div>
          <span>{{ item.name }}</span>
        </div>
      </div>
    </section>

    <!-- Daily New Arrivals -->
    <section class="product-section" v-loading="dailyLoading">
      <div class="section-header">
        <h2>Daily New Arrivals</h2>
        <span class="see-all" @click="$router.push('/pc/products')">More &rarr;</span>
      </div>
      <div class="product-grid">
        <ProductCard v-for="item in dailyProducts" :key="item.id" :item="item" />
      </div>
    </section>

    <!-- Promo Banner -->
    <section class="promo-banner">
      <div class="promo-content">
        <p>Exclusive Deals</p>
        <p>Limited Time Offers</p>
        <h3>Up to $100,000</h3>
        <button class="btn btn-primary" @click="joinStore">Become a Seller</button>
      </div>
    </section>

    <!-- Recommended Products -->
    <section class="product-section" v-loading="recLoading">
      <div class="section-header">
        <h2>Recommended Products</h2>
      </div>
      <div class="product-grid">
        <ProductCard v-for="item in recommendProducts" :key="item.id" :item="item" />
      </div>
    </section>

    <!-- Recommended Stores -->
    <section class="store-section" v-loading="storeLoading">
      <div class="section-header">
        <h2>Recommended Stores</h2>
        <span class="see-all" @click="$router.push('/pc/stores')">More Stores &rarr;</span>
      </div>
      <div class="store-scroll" ref="storeScrollRef" @mouseenter="pauseStore" @mouseleave="playStore">
        <div
          v-for="item in merchantList"
          :key="item.id"
          class="store-card card card-hover"
          @click="$router.push({ path: '/pc/store/' + item.id, query: { storeId: item.id } })"
        >
          <img :src="item.avatar" class="store-avatar" />
          <div class="store-info">
            <h4>{{ item.name }}</h4>
            <p>{{ item.sellerGoodsNum || 0 }} products</p>
            <p>{{ formatNum(item.soldNum || 0) }} sold</p>
            <button class="btn btn-outline btn-sm">Visit Store</button>
          </div>
        </div>
      </div>
    </section>

    <!-- Hot Selling -->
    <section class="product-section" v-loading="hotLoading">
      <div class="section-header">
        <h2>Hot Selling</h2>
      </div>
      <div class="product-grid">
        <ProductCard v-for="item in hotProducts" :key="item.id" :item="item" />
      </div>
    </section>

    <!-- Features -->
    <section class="features-section">
      <div class="feature-item">
        <span class="feature-icon">&#10003;</span>
        <span>100% Authentic</span>
      </div>
      <div class="feature-item">
        <span class="feature-icon">&#8634;</span>
        <span>7-Day Returns</span>
      </div>
      <div class="feature-item">
        <span class="feature-icon">&#9733;</span>
        <span>Shipping Discounts</span>
      </div>
      <div class="feature-item">
        <span class="feature-icon">&#128274;</span>
        <span>Secure Payment</span>
      </div>
    </section>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onBeforeUnmount } from 'vue'
import { useRouter } from 'vue-router'
import { post } from '@/api/index'
import ProductCard from '@/views/pc/products/ProductCard.vue'

const router = useRouter()

// State
const bannerLoading = ref(false); const catLoading = ref(false)
const dailyLoading = ref(false); const recLoading = ref(false)
const storeLoading = ref(false); const hotLoading = ref(false)

const mainBanners = ref([]); const leftBanners = ref([])
const categoryList = ref([]); const dailyProducts = ref([])
const recommendProducts = ref([]); const merchantList = ref([])
const hotProducts = ref([])

const catScrollRef = ref(null); const storeScrollRef = ref(null)
let catTimer = null; let storeTimer = null

// Computed
const bannerRightChunks = computed(() => {
  const chunks = []
  for (let i = 0; i < leftBanners.value.length; i += 2) {
    chunks.push(leftBanners.value.slice(i, i + 2))
  }
  return chunks.slice(0, 2)
})

// Methods
function goLink(path) { if (path) window.open(path, '_blank') }

function formatNum(n) {
  if (!n) return '0'
  const v = Number(n)
  if (v >= 1000) return (v / 1000).toFixed(1).replace(/\.0$/, '') + 'k'
  return v.toLocaleString()
}

function pauseBanner() {}; function playBanner() {}
function pauseCat() { clearInterval(catTimer) }
function playCat() {
  if (!catScrollRef.value) return
  catTimer = setInterval(() => { const el = catScrollRef.value; el.scrollLeft += 1; if (el.scrollLeft >= el.scrollWidth - el.clientWidth) el.scrollLeft = 0 }, 40)
}
function pauseStore() { clearInterval(storeTimer) }
function playStore() {
  if (!storeScrollRef.value) return
  storeTimer = setInterval(() => { const el = storeScrollRef.value; el.scrollLeft += 1; if (el.scrollLeft >= el.scrollWidth - el.clientWidth) el.scrollLeft = 0 }, 40)
}

function joinStore() {
  window.open(window.location.origin + '/promote/#/?lang=en', '_blank')
}

async function getBanners(type, imgType) {
  const res = await post('/api/banner!bannerList.action', { pageNum: 1, pageSize: 8, type: 'pc', imgType })
  return res.data?.result || []
}

async function getCategoryList() {
  const res = await post('/api/category!recommend.action', { pageSize: 50, pageNum: 1 })
  return res.code === 0 ? (res.data?.pageList || []) : []
}

async function getProducts(type) {
  const res = await post('/api/sellerGoods!recommend_new.action', { type, pageSize: 24, pageNum: 1 })
  return res.data?.result || []
}

async function getMerchants() {
  const res = await post('/api/seller!list.action', { isRec: 1, pageNum: 1, pageSize: 6 })
  return res.data?.pageList || []
}

onMounted(async () => {
  try { bannerLoading.value = true; mainBanners.value = await getBanners(null, 1); leftBanners.value = await getBanners(null, 0) } catch {} finally { bannerLoading.value = false }
  try { catLoading.value = true; categoryList.value = await getCategoryList(); playCat() } catch {} finally { catLoading.value = false }
  try { dailyLoading.value = true; dailyProducts.value = await getProducts(0) } catch {} finally { dailyLoading.value = false }
  try { recLoading.value = true; recommendProducts.value = await getProducts(1) } catch {} finally { recLoading.value = false }
  try { storeLoading.value = true; merchantList.value = await getMerchants(); playStore() } catch {} finally { storeLoading.value = false }
  try { hotLoading.value = true; hotProducts.value = await getProducts(2) } catch {} finally { hotLoading.value = false }
})

onBeforeUnmount(() => {
  clearInterval(catTimer); clearInterval(storeTimer)
})
</script>

<style scoped>
.pc-home { padding-top: 4px; }

.banner-section { margin-bottom: 24px; }
.banner-left { height: 380px; border-radius: var(--border-radius); overflow: hidden; }
.banner-swiper { height: 100%; display: flex; overflow-x: auto; scroll-snap-type: x mandatory; scrollbar-width: none; }
.banner-swiper::-webkit-scrollbar { display: none; }
.banner-slide { min-width: 100%; scroll-snap-align: start; cursor: pointer; }
.banner-slide img { width: 100%; height: 100%; object-fit: cover; }
.banner-right { display: flex; flex-direction: column; gap: 6px; height: 380px; }
.banner-right-grid { display: flex; gap: 6px; flex: 1; }
.banner-right-item { flex: 1; border-radius: 8px; overflow: hidden; cursor: pointer; }
.banner-right-item img { width: 100%; height: 100%; object-fit: cover; }

.section-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; }
.section-header h2 { font-size: 20px; font-weight: 700; color: var(--text-primary); }
.see-all { font-size: 13px; color: var(--color-primary); cursor: pointer; font-weight: 500; }
.see-all:hover { color: var(--color-primary-dark); }

.category-section { margin-bottom: 36px; }
.category-scroll { display: flex; gap: 12px; overflow-x: auto; scrollbar-width: none; padding: 4px 0; }
.category-scroll::-webkit-scrollbar { display: none; }
.category-item { display: flex; flex-direction: column; align-items: center; cursor: pointer; flex-shrink: 0; width: 100px; }
.cat-img-box { width: 88px; height: 64px; border: 1px solid var(--border-color); border-radius: 8px; display: flex; align-items: center; justify-content: center; margin-bottom: 6px; overflow: hidden; transition: border-color var(--transition-fast); }
.category-item:hover .cat-img-box { border-color: var(--color-primary); }
.cat-img-box img { width: 48px; height: 48px; object-fit: contain; }
.category-item span { font-size: 12px; color: var(--text-secondary); max-width: 90px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }

.product-section { margin-bottom: 36px; }
.product-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(170px, 1fr)); gap: 14px; }

.promo-banner { height: 300px; background: linear-gradient(135deg, var(--color-primary-dark), var(--color-primary)); background-size: cover; background-position: center; display: flex; align-items: center; justify-content: flex-end; margin-bottom: 36px; border-radius: var(--border-radius); overflow: hidden; }
.promo-content { width: 500px; text-align: center; padding-right: 40px; color: white; }
.promo-content p { font-size: 26px; font-weight: 300; opacity: 0.9; }
.promo-content h3 { font-size: 38px; margin: 8px 0 20px; font-weight: 700; }
.promo-content .btn { padding: 12px 36px; border-radius: 30px; background: white; color: var(--color-primary); }

.store-section { margin-bottom: 36px; }
.store-scroll { display: flex; gap: 16px; overflow-x: auto; scrollbar-width: none; padding: 4px 0; }
.store-scroll::-webkit-scrollbar { display: none; }
.store-card { display: flex; gap: 12px; padding: 16px; cursor: pointer; min-width: 280px; }
.store-avatar { width: 72px; height: 72px; border-radius: 50%; object-fit: cover; flex-shrink: 0; }
.store-info h4 { font-size: 14px; font-weight: 600; margin-bottom: 4px; }
.store-info p { font-size: 12px; color: var(--text-muted); margin-bottom: 3px; }
.store-info .btn { margin-top: 6px; }

.features-section { display: flex; justify-content: space-around; max-width: 800px; margin: 40px auto 20px; padding: 20px 0; }
.feature-item { display: flex; flex-direction: column; align-items: center; gap: 8px; }
.feature-icon { font-size: 36px; color: var(--color-primary); }
.feature-item span:last-child { font-size: 13px; font-weight: 500; color: var(--text-secondary); }

@media (max-width: 768px) {
  .banner-left { height: 200px; }
  .banner-right { display: none; }
  .product-grid { grid-template-columns: repeat(2, 1fr); }
  .features-section { flex-wrap: wrap; gap: 20px; }
  .promo-banner { justify-content: center; }
  .promo-content { padding: 0 20px; }
}
</style>
