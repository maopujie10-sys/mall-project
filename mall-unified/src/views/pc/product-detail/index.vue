<template>
  <div class="product-detail-page fade-in" v-loading="loading">
    <div v-if="product">
      <div class="detail-layout">
        <!-- Image Gallery -->
        <div class="gallery-section">
          <div class="main-image-box" @mouseenter="pauseGallery" @mouseleave="playGallery">
            <img :src="currentImage" alt="" class="main-image" />
          </div>
          <div class="thumb-list" v-if="imageList.length > 1">
            <div
              v-for="(img, idx) in imageList"
              :key="idx"
              :class="['thumb-item', { active: galleryIndex === idx }]"
              @click="galleryIndex = idx"
            >
              <img :src="img" alt="" />
            </div>
          </div>
        </div>

        <!-- Product Info -->
        <div class="info-section">
          <h1 class="product-title">{{ product.name }}</h1>

          <div class="price-row">
            <div class="price-block">
              <span class="price-label">Retail Price</span>
              <span class="price-value">${{ formatPrice(skuPrice || product.discountPrice || product.sellingPrice) }}</span>
            </div>
            <div v-if="product.discountPrice" class="price-block orig">
              <span class="price-label">Original Price</span>
              <span class="price-value">${{ formatPrice(product.sellingPrice) }}</span>
            </div>
          </div>

          <div class="action-row">
            <button class="action-btn" @click="toggleCollect">
              <i :class="product.isKeep === 1 ? 'star-filled' : 'star-empty'">{{ product.isKeep === 1 ? '★' : '☆' }}</i>
              {{ product.isKeep === 1 ? 'Unfavorite' : 'Favorite' }}
            </button>
          </div>

          <div class="meta-row">
            <div class="meta-item"><span>Sold</span><strong>{{ formatNum(product.soldNum || 0) }}</strong></div>
            <div class="meta-item"><span>Views</span><strong>{{ formatNum(product.viewsNum || 0) }}</strong></div>
            <div class="meta-item"><span>Shipping</span><strong>{{ Number(product.freightAmount) === 0 ? 'Free' : '$' + formatPrice(product.freightAmount || 0) }}</strong></div>
          </div>

          <!-- SKU Attributes -->
          <div v-if="product.canSelectAttributes?.goodAttrs?.length" class="sku-section">
            <div v-for="(attr, ai) in product.canSelectAttributes.goodAttrs" :key="attr.attrId" class="sku-row">
              <span class="sku-label">{{ attr.attrName }}</span>
              <div class="sku-values">
                <template v-if="attr.attrValues[0]?.icon">
                  <div
                    v-for="av in attr.attrValues"
                    :key="av.attrValueId"
                    :class="['sku-img-item', { active: goodsAttrObj[attr.attrId] === av.attrValueId, disabled: av.disabled }]"
                    @click="!av.disabled && changeAttr(attr.attrId, av.attrValueId, ai)"
                  >
                    <img :src="av.iconImg" alt="" />
                  </div>
                </template>
                <template v-else>
                  <el-select
                    :model-value="goodsAttrObj[attr.attrId]"
                    @change="(v) => changeAttr(attr.attrId, v)"
                    :placeholder="'Select ' + attr.attrName"
                    size="small"
                  >
                    <el-option
                      v-for="av in attr.attrValues"
                      :key="av.attrValueId"
                      :value="av.attrValueId"
                      :label="av.attrValueName"
                      :disabled="av.disabled"
                    />
                  </el-select>
                </template>
              </div>
            </div>
          </div>

          <!-- Quantity -->
          <div class="qty-row">
            <span class="sku-label">Quantity</span>
            <el-input-number v-model="quantity" :min="product.buyMin || 1" :max="maxNum" size="small" />
          </div>

          <!-- Total Price -->
          <div class="total-row">
            <span class="sku-label">Total</span>
            <span class="total-price">${{ totalPrice }}</span>
          </div>

          <!-- Buy / Cart buttons -->
          <div class="buy-row">
            <el-button type="primary" size="large" :disabled="isDisabled" @click="buyNow" class="buy-btn">Buy Now</el-button>
            <el-button size="large" :disabled="isDisabled" @click="addToCart" class="cart-btn">Add to Cart</el-button>
          </div>
        </div>
      </div>

      <!-- Description -->
      <div v-if="product.des" class="desc-section card">
        <h2>Product Description</h2>
        <div v-html="product.des" class="desc-content"></div>
      </div>

      <!-- Reviews -->
      <div class="comment-section card">
        <h2>Customer Reviews <span class="comment-count">({{ commentTotal }})</span></h2>
        <div class="comment-filters">
          <button v-for="(v, k) in commentFilters" :key="k" :class="['cmt-btn', { active: activeCommentFilter === k }]" @click="setCommentFilter(k, v)">
            {{ v.text }} ({{ v.num }})
          </button>
        </div>
        <div v-loading="commentLoading">
          <div v-if="comments.length" class="comment-list">
            <div v-for="item in comments" :key="item.id" class="comment-item">
              <div class="comment-user">
                <div class="user-avatar">{{ (item.userName || 'U')[0] }}</div>
                <span>{{ item.userName }}</span>
              </div>
              <el-rate :model-value="item.rating" disabled size="small" />
              <p class="comment-text">{{ item.content }}</p>
              <div v-if="getCommentImages(item).length" class="comment-images">
                <el-image v-for="url in getCommentImages(item)" :key="url" :src="url" :preview-src-list="getCommentImages(item)" class="cmt-img" />
              </div>
              <span class="comment-time">{{ item.evaluationTime || '' }}</span>
            </div>
          </div>
          <el-empty v-if="!comments.length && !commentLoading" description="No reviews yet" />
          <div v-if="commentTotal > commentPageSize" class="comment-pagination">
            <el-pagination background layout="prev,next" :current-page="commentPage" :page-size="commentPageSize" :total="commentTotal" @current-change="changeCommentPage" />
          </div>
        </div>
      </div>

      <!-- Related Products -->
      <section v-if="relatedProducts.length" class="related-section">
        <h2>You May Also Like</h2>
        <div class="related-grid">
          <div v-for="item in relatedProducts" :key="item.id" class="related-card card card-hover" @click="router.push({ path: '/pc/product/' + item.id, query: { id: item.id } })">
            <img :src="item.imgUrl1 || item.imgUrl" alt="" />
            <div class="related-info">
              <p class="r-price">${{ formatPrice(item.discountPrice || item.sellingPrice) }}</p>
              <p class="r-name">{{ item.name }}</p>
            </div>
          </div>
        </div>
      </section>
    </div>

    <el-empty v-if="!product && !loading" description="Product not found" />
  </div>
</template>

<script setup>
import { ref, reactive, computed, watch, onMounted, onBeforeUnmount } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { post } from '@/api/index'

const route = useRoute()
const router = useRouter()

// ===== State =====
const loading = ref(false)
const product = ref(null)
const quantity = ref(1)
const maxNum = ref(999)
const goodsAttrObj = reactive({})
const skuPrice = ref(null)
const imgList = ref(null)
const galleryIndex = ref(0)

// Comments
const comments = ref([])
const commentLoading = ref(false)
const commentTotal = ref(0)
const commentPage = ref(1)
const commentPageSize = ref(5)
const activeCommentFilter = ref('')

const commentFilters = ref({
  havePicture: { text: 'With Images', num: 0, evaluationType: -2 },
  positiveComments: { text: 'Positive', num: 0, evaluationType: 1 },
  mediumReview: { text: 'Neutral', num: 0, evaluationType: 2 },
  negativeComment: { text: 'Negative', num: 0, evaluationType: 3 }
})

const relatedProducts = ref([])

// ===== Computed =====
const productId = computed(() => route.params.id || route.query.id)

const imageList = computed(() => {
  if (!product.value) return []
  if (imgList.value && typeof imgList.value === 'string') return [imgList.value]
  return new Array(10).fill('').map((_, i) => product.value['imgUrl' + (i + 1)]).filter(Boolean)
})

const currentImage = computed(() => imageList.value[galleryIndex.value] || '')

const totalPrice = computed(() => {
  const price = skuPrice.value || product.value?.discountPrice || product.value?.sellingPrice || 0
  return formatPrice(Number(quantity.value) * Number(price))
})

const isDisabled = computed(() => false)

// ===== Methods =====
function formatPrice(n) {
  const val = Number(n)
  if (!val) return '0.00'
  return val.toFixed(2).replace(/\B(?=(\d{3})+(?!\d))/g, ',')
}

function formatNum(n) {
  if (!n) return '0'
  return Number(n).toLocaleString()
}

function pauseGallery() {}
function playGallery() {}

async function fetchProduct() {
  const id = productId.value
  if (!id) { router.replace('/pc'); return }
  try {
    loading.value = true
    const res = await post('/api/product!info.action', { sellerGoodsId: id })
    product.value = res.data || res
    if (product.value?.canSelectAttributes?.goodAttrs?.length) {
      product.value.canSelectAttributes.goodAttrs.forEach(attr => {
        goodsAttrObj[attr.attrId] = attr.attrValues[0]?.attrValueId
      })
      updateSku()
    }
    if (!product.value?.id) {
      router.replace('/pc')
      return
    }
    // Save seller info
    if (product.value.seller?.id) {
      localStorage.setItem('sellerId', product.value.seller.id)
    }
  } catch {
    router.replace('/pc')
  } finally {
    loading.value = false
  }
}

function changeAttr(attrId, valueId, index) {
  goodsAttrObj[attrId] = valueId
  updateSku()
}

function updateSku() {
  const { canSelectAttributes } = product.value || {}
  if (!canSelectAttributes?.skus) return
  const attrIds = Object.keys(goodsAttrObj)
  const sku = canSelectAttributes.skus.find(x => {
    if (!x.attrs?.length) return false
    return x.attrs.every(a => goodsAttrObj[a.attrId] === a.attrValueId)
  })
  if (sku && sku.skuId !== -1) {
    skuPrice.value = sku.discountPrice || sku.sellingPrice
    imgList.value = sku.img || ''
  }
}

async function fetchComments(params = {}) {
  if (!product.value) return
  try {
    commentLoading.value = true
    const res = await post('/api/evaluation!list.action', {
      sellerGoodsId: product.value.id,
      pageNum: commentPage.value,
      pageSize: commentPageSize.value,
      ...params
    })
    const data = res.data || res
    comments.value = data.pageList || data.result || []
    commentTotal.value = data.pageInfo?.totalElements || 0
  } catch {}
  finally { commentLoading.value = false }
}

async function fetchCommentCategory() {
  try {
    const res = await post('/api/evaluation!category.action', { goodId: product.value.id })
    if (res.code === '0' && res.data) {
      Object.keys(commentFilters.value).forEach(k => {
        if (res.data[k] !== undefined) commentFilters.value[k].num = res.data[k]
      })
    }
  } catch {}
}

function setCommentFilter(key, val) {
  activeCommentFilter.value = key
  commentPage.value = 1
  fetchComments({ evaluationType: val.evaluationType })
}

function changeCommentPage(page) {
  commentPage.value = page
  if (activeCommentFilter.value) {
    const f = commentFilters.value[activeCommentFilter.value]
    fetchComments({ evaluationType: f.evaluationType })
  } else {
    fetchComments()
  }
}

function getCommentImages(item) {
  if (!item) return []
  return Object.keys(item).filter(k => k.includes('imgUrl') && item[k]).map(k => item[k])
}

async function fetchRelated() {
  if (!product.value) return
  try {
    const res = await post('/api/sellerGoods!recommend_new.action', { type: 1, pageSize: 6, pageNum: 1 })
    relatedProducts.value = (res.data?.result || []).filter(x => x.id !== product.value.id).slice(0, 6)
  } catch {}
}

async function toggleCollect() {
  const token = localStorage.getItem('token')
  if (!token) { router.push('/pc/login'); return }
  try {
    if (product.value.isKeep === 1) {
      await post('/api/keepGoods!cancel.action', { sellerGoodsId: product.value.id })
      ElMessage.warning('Canceled')
    } else {
      await post('/api/keepGoods!add.action', { sellerGoodsId: product.value.id })
      ElMessage.success('Collected')
    }
    await fetchProduct()
  } catch {}
}

function buyNow() {
  const token = localStorage.getItem('token')
  if (!token) { router.push('/pc/login'); return }
  if (!product.value.isShelf && product.value.isShelf !== undefined) {
    ElMessage.warning('Product unavailable')
    return
  }
  // Push to checkout
  router.push('/pc/checkout')
}

function addToCart() {
  const token = localStorage.getItem('token')
  if (!token) { router.push('/pc/login'); return }
  if (!product.value.isShelf && product.value.isShelf !== undefined) {
    ElMessage.warning('Product unavailable')
    return
  }
  ElMessage.success('Added to cart')
}

// ===== Lifecycle =====
onMounted(async () => {
  maxNum.value = Number(localStorage.getItem('maxBuy') || 999)
  await fetchProduct()
  if (product.value) {
    fetchComments()
    fetchCommentCategory()
    fetchRelated()
  }
})

onBeforeUnmount(() => {
  if (product.value?.seller) {
    localStorage.setItem('seller_cache', JSON.stringify({ id: product.value.seller.id, name: product.value.seller.name || '' }))
  }
})

// ===== Watch =====
watch(() => route.params.id, () => {
  if (route.params.id) {
    fetchProduct().then(() => {
      if (product.value) { fetchComments(); fetchCommentCategory(); fetchRelated() }
    })
  }
})
</script>

<style scoped>
.product-detail-page { padding-bottom: 40px; }

/* Layout */
.detail-layout { display: flex; gap: 32px; margin-bottom: 32px; }
.gallery-section { width: 380px; flex-shrink: 0; }
.info-section { flex: 1; min-width: 0; }

/* Gallery */
.main-image-box { width: 380px; height: 380px; border: 1px solid var(--border-color); border-radius: var(--border-radius); display: flex; align-items: center; justify-content: center; overflow: hidden; margin-bottom: 12px; background: var(--bg-tertiary); }
.main-image { max-width: 100%; max-height: 100%; object-fit: contain; }
.thumb-list { display: flex; gap: 8px; }
.thumb-item { width: 72px; height: 72px; border: 1.5px solid var(--border-color); border-radius: 6px; overflow: hidden; cursor: pointer; padding: 4px; }
.thumb-item.active { border-color: var(--color-primary); }
.thumb-item img { width: 100%; height: 100%; object-fit: cover; }

/* Info */
.product-title { font-size: 22px; font-weight: 600; line-height: 1.4; margin-bottom: 16px; color: var(--text-primary); }
.price-row { display: flex; gap: 24px; padding: 16px 0; border-top: 1px solid var(--border-color); border-bottom: 1px solid var(--border-color); margin-bottom: 12px; }
.price-block { }
.price-block.orig { text-decoration: line-through; }
.price-label { font-size: 12px; color: var(--text-muted); display: block; margin-bottom: 2px; }
.price-value { font-size: 20px; font-weight: 700; color: var(--color-danger); }
.price-block.orig .price-value { font-size: 14px; color: var(--text-muted); }
.action-row { display: flex; gap: 12px; margin-bottom: 16px; }
.action-btn { background: none; font-size: 14px; color: var(--text-secondary); display: flex; align-items: center; gap: 4px; cursor: pointer; border: 1px solid var(--border-color); padding: 6px 14px; border-radius: var(--border-radius-sm); }
.action-btn:hover { border-color: var(--color-primary); color: var(--color-primary); }
.star-filled { color: var(--color-accent); }
.meta-row { display: flex; gap: 20px; margin-bottom: 20px; }
.meta-item { font-size: 13px; color: var(--text-secondary); }
.meta-item span { margin-right: 6px; }
.meta-item strong { color: var(--text-primary); }

/* SKU */
.sku-section { margin-bottom: 16px; }
.sku-row { display: flex; align-items: flex-start; margin-bottom: 14px; }
.sku-label { min-width: 70px; font-size: 13px; color: var(--text-secondary); padding-top: 4px; }
.sku-values { display: flex; flex-wrap: wrap; gap: 8px; }
.sku-img-item { width: 48px; height: 48px; border: 1.5px solid var(--border-color); border-radius: 6px; overflow: hidden; cursor: pointer; padding: 3px; }
.sku-img-item.active { border-color: var(--color-primary); }
.sku-img-item.disabled { opacity: 0.4; cursor: not-allowed; filter: grayscale(100%); }
.sku-img-item img { width: 100%; height: 100%; object-fit: cover; }

.qty-row { display: flex; align-items: center; margin-bottom: 16px; }
.total-row { display: flex; align-items: center; margin-bottom: 20px; }
.total-price { font-size: 24px; font-weight: 700; color: var(--color-danger); }

.buy-row { display: flex; gap: 12px; }
.buy-btn { width: 45%; height: 44px; font-weight: 600; font-size: 14px; }
.cart-btn { width: 45%; height: 44px; font-weight: 600; font-size: 14px; color: var(--color-primary); border-color: var(--color-primary); }

/* Description */
.desc-section { padding: 24px; margin-bottom: 24px; }
.desc-section h2 { font-size: 20px; font-weight: 600; border-bottom: 1px solid var(--border-color); padding-bottom: 16px; margin-bottom: 20px; }
.desc-content { font-size: 14px; line-height: 1.8; color: var(--text-secondary); }
.desc-content :deep(img) { max-width: 100%; }

/* Comments */
.comment-section { padding: 24px; margin-bottom: 24px; }
.comment-section h2 { font-size: 20px; margin-bottom: 16px; }
.comment-count { font-size: 14px; color: var(--text-muted); font-weight: 400; }
.comment-filters { display: flex; gap: 8px; margin-bottom: 20px; }
.cmt-btn { padding: 4px 12px; border-radius: 14px; font-size: 12px; background: var(--bg-tertiary); color: var(--text-secondary); border: none; cursor: pointer; }
.cmt-btn.active { background: var(--color-primary); color: white; }
.comment-list { }
.comment-item { padding: 16px 0; border-bottom: 1px solid var(--border-color); }
.comment-item:last-child { border-bottom: none; }
.comment-user { display: flex; align-items: center; gap: 8px; margin-bottom: 8px; }
.user-avatar { width: 32px; height: 32px; border-radius: 50%; background: var(--color-primary-light); color: white; display: flex; align-items: center; justify-content: center; font-size: 14px; font-weight: 600; }
.comment-user span { font-size: 13px; color: var(--text-secondary); }
.comment-text { font-size: 14px; color: var(--text-primary); line-height: 1.6; margin: 8px 0; }
.comment-images { display: flex; gap: 8px; margin-bottom: 8px; }
.cmt-img { width: 80px; height: 80px; border-radius: 6px; overflow: hidden; }
.comment-time { font-size: 11px; color: var(--text-muted); }
.comment-pagination { display: flex; justify-content: center; padding-top: 20px; }

/* Related */
.related-section { margin-bottom: 24px; }
.related-section h2 { font-size: 20px; margin-bottom: 16px; }
.related-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(160px, 1fr)); gap: 14px; }
.related-card { cursor: pointer; padding: 0; overflow: hidden; }
.related-card img { width: 100%; aspect-ratio: 1; object-fit: contain; background: var(--bg-tertiary); }
.related-info { padding: 10px; }
.r-price { font-weight: 600; color: var(--color-danger); font-size: 14px; margin-bottom: 4px; }
.r-name { font-size: 12px; color: var(--text-secondary); overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }

@media (max-width: 768px) { .detail-layout { flex-direction: column; } .gallery-section { width: 100%; } .main-image-box { width: 100%; height: 300px; } }
</style>
