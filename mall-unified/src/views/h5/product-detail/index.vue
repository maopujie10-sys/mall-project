<template>
  <div class="product-detail" v-if="goodsInfo">
    <!-- 图片轮播 -->
    <div class="image-swipe">
      <van-swipe :autoplay="3000" indicator-color="white">
        <van-swipe-item v-for="(img, idx) in imageList" :key="idx">
          <img :src="img" class="swipe-img" />
        </van-swipe-item>
        <template #indicator>
          <div class="indicator-row">
            <span v-for="(_, i) in imageList" :key="i" :class="['dot', { active: currentImg === i }]" />
          </div>
        </template>
      </van-swipe>
    </div>

    <!-- 商品信息 -->
    <div class="card info-section">
      <h2 class="product-name">{{ goodsInfo.name }}</h2>
      <div class="price-row">
        <span class="price">${{ formatPrice(goodsInfo.discountPrice) || formatPrice(goodsInfo.sellingPrice) }}</span>
        <span class="original" v-if="goodsInfo.sellingPrice && goodsInfo.discountPrice && goodsInfo.discountPrice < goodsInfo.sellingPrice">
          ${{ formatPrice(goodsInfo.sellingPrice) }}
        </span>
      </div>
      <div class="meta-row">
        <span>{{ $t('common.sales') }}: {{ fmtInt(goodsInfo.soldNum) }}</span>
        <span class="rating" v-if="goodsInfo.highOpinion">{{ $t('common.positiveRate') }}: {{ Math.floor(goodsInfo.highOpinion * 100) || 100 }}%</span>
      </div>
    </div>

    <!-- SKU 规格 -->
    <div class="card sku-section" v-if="goodsInfo?.canSelectAttributes?.goodAttrs?.length">
      <div v-for="(attr, ai) in goodsInfo.canSelectAttributes.goodAttrs" :key="ai" class="attr-row">
        <span class="attr-label">{{ attr.attrName }}</span>
        <div class="attr-values">
          <span
            v-for="(val, vi) in attr.attrValues"
            :key="vi"
            :class="['attr-val', { active: activeAttrs[ai] === val.attrValueId, disabled: val.disabled }]"
            @click="!val.disabled && handleToggle(val, ai)"
          >
            <img v-if="val.icon" :src="val.iconImg" class="attr-icon" />
            <span v-else>{{ val.attrValueName }}</span>
          </span>
        </div>
      </div>
    </div>

    <!-- 配送信息 -->
    <div class="card shipping-section">
      <div class="info-row" @click="isShippingShow = true">
        <span class="info-label">{{ $t('product.shipping') }}</span>
        <span class="info-val">{{ $t('product.shippingDesc') }}</span>
      </div>
      <div class="info-row" @click="isShippingShow = true">
        <span class="info-label">{{ $t('product.freight') }}</span>
        <span class="info-val">{{ goodsInfo.freightAmount == 0 ? $t('product.freeShipping') : '$' + formatPrice(goodsInfo.freightAmount || 0) }}</span>
        <svg width="12" height="12" viewBox="0 0 24 24" fill="none"><path d="M9 6l6 6-6 6" stroke="#94a3b8" stroke-width="2" stroke-linecap="round"/></svg>
      </div>
      <div class="info-row">
        <span class="info-label">{{ $t('product.tax') }}</span>
        <span class="info-val">${{ formatPrice(goodsInfo.goodsTax || 0) }}</span>
      </div>
    </div>

    <!-- 数量 -->
    <div class="card qty-section">
      <div class="info-row">
        <span class="info-label">{{ $t('product.quantity') }}</span>
        <van-stepper :disable-input="true" :max="maxBuyNum" integer v-model="buyNum" />
      </div>
    </div>

    <!-- 店铺信息 -->
    <div class="card shop-card" v-if="sellerInfo" @click="goShop">
      <div class="shop-top">
        <img :src="sellerInfo.avatar" class="shop-avatar" />
        <div class="shop-mid">
          <span class="shop-name">{{ sellerInfo.name }}</span>
          <span class="shop-stats">{{ $t('common.products') }}: {{ sellerInfo.sellerGoodsNum }}</span>
        </div>
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none"><path d="M9 6l6 6-6 6" stroke="#94a3b8" stroke-width="2" stroke-linecap="round"/></svg>
      </div>
    </div>

    <!-- 详情 -->
    <div class="card detail-section" v-html="goodsInfo.description || goodsInfo.detailHtml"></div>

    <!-- 底部操作栏 -->
    <div class="bottom-bar">
      <div class="bar-left" @click="toggleFavorite">
        <svg width="20" height="20" viewBox="0 0 24 24" :fill="isFavorited ? '#ef4444' : 'none'" :stroke="isFavorited ? '#ef4444' : '#94a3b8'" stroke-width="2"><path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z"/></svg>
        <span>{{ $t('common.favorite') }}</span>
      </div>
      <div class="bar-right">
        <button class="btn-cart" @click="addToCart">{{ $t('common.addToCart') }}</button>
        <button class="btn-buy" @click="buyNow">{{ $t('common.buyNow') }}</button>
      </div>
    </div>

    <!-- 运费弹窗 -->
    <van-action-sheet v-model:show="isShippingShow" :title="$t('product.shippingInfo')">
      <div class="shipping-popup">
        <p>{{ $t('product.freight') }}: ${{ formatPrice(goodsInfo.freightAmount || 0) }}</p>
        <p>{{ $t('product.shippingDesc') }}</p>
      </div>
    </van-action-sheet>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { Swipe as VanSwipe, SwipeItem as VanSwipeItem, Stepper as VanStepper, ActionSheet as VanActionSheet, showToast, showNotify } from 'vant'
import { useUserStore } from '@/stores/user'
import { goods_info_action_post } from '@/api/user'

const router = useRouter()
const route = useRoute()
const userStore = useUserStore()

const goodsInfo = ref(null)
const sellerInfo = ref(null)
const imageList = ref([])
const currentImg = ref(0)
const buyNum = ref(1)
const maxBuyNum = ref(99)
const isFavorited = ref(false)
const isShippingShow = ref(false)
const activeAttrs = ref([])

function _toFixed(n, d) { n = n.toString(); const i = n.indexOf('.'); const s = i !== -1 ? n.substring(0, d + i + 1) : n.substring(0); return parseFloat(s).toFixed(d) }
function formatPrice(n) { if (!n || !Number(n)) return 0; const s = _toFixed(n, 2); const p = s.slice(0, s.indexOf('.')); const r = s.slice(s.indexOf('.') + 1); return `${p.replace(/(\d)(?=(\d{3})+(?!\d))/g, '$1,')}.${r.length < 2 ? r + '0' : r}` }
function fmtInt(n) { if (!n || !Number(n)) return 0; const s = _toFixed(n, 2); return s.slice(0, s.indexOf('.')).replace(/(\d)(?=(\d{3})+(?!\d))/g, '$1,') }

// Load product
onMounted(async () => {
  const id = route.params.id || route.query.sellerGoodsId
  if (!id) return
  try {
    const res = await goods_info_action_post({ id })
    goodsInfo.value = res.data || res.result || res
    imageList.value = goodsInfo.value?.imgUrls?.length
      ? goodsInfo.value.imgUrls
      : [goodsInfo.value?.imgUrl1, goodsInfo.value?.imgUrl2].filter(Boolean)
    sellerInfo.value = goodsInfo.value?.sellerInfo || goodsInfo.value?.seller
  } catch (e) {}
})

function handleToggle(val, idx) {
  activeAttrs.value[idx] = val.attrValueId
}

function toggleFavorite() {
  if (!userStore.token) { showNotify({ type: 'warning', message: '请先登录' }); router.push('/m/login'); return }
  isFavorited.value = !isFavorited.value
  showToast(isFavorited.value ? '已收藏' : '已取消收藏')
}

function goShop() {
  if (sellerInfo.value?.id) router.push('/m/shop/' + sellerInfo.value.id)
}

function addToCart() {
  if (!userStore.token) { showNotify({ type: 'warning', message: '请先登录' }); router.push('/m/login'); return }
  showToast('已加入购物车')
}

function buyNow() {
  if (!userStore.token) { showNotify({ type: 'warning', message: '请先登录' }); router.push('/m/login'); return }
  router.push('/m/checkout')
}

function onClickLeft() { router.go(-1) }
</script>

<style scoped>
.product-detail { min-height: 100vh; background: var(--bg-secondary); padding-bottom: 80px; }
.image-swipe { border-radius: 0 0 var(--border-radius-lg) var(--border-radius-lg); overflow: hidden; }
.swipe-img { width: 100%; aspect-ratio: 1; object-fit: cover; display: block; }
.indicator-row { display: flex; justify-content: center; gap: 6px; padding-bottom: 12px; }
.dot { width: 18px; height: 3px; background: rgba(255,255,255,0.5); border-radius: 2px; transition: all var(--transition-fast); }
.dot.active { background: var(--color-primary); width: 28px; }

.card { background: var(--bg-primary); border-radius: var(--border-radius); margin: 10px 14px; padding: 16px; box-shadow: var(--shadow-sm); }

/* Info */
.product-name { font-size: 16px; font-weight: 600; color: var(--text-primary); line-height: 1.5; margin-bottom: 12px; }
.price-row { display: flex; align-items: baseline; gap: 10px; margin-bottom: 8px; }
.price { font-size: 22px; font-weight: 700; color: var(--color-primary); }
.original { font-size: 14px; color: var(--text-muted); text-decoration: line-through; }
.meta-row { display: flex; gap: 20px; font-size: 12px; color: var(--text-muted); }

/* SKU */
.attr-row { margin-bottom: 12px; }
.attr-label { font-size: 13px; color: var(--text-secondary); margin-bottom: 8px; display: block; }
.attr-values { display: flex; flex-wrap: wrap; gap: 8px; }
.attr-val { padding: 6px 16px; border: 1.5px solid var(--border-color); border-radius: 20px; font-size: 13px; cursor: pointer; transition: all var(--transition-fast); color: var(--text-primary); }
.attr-val.active { border-color: var(--color-primary); background: rgba(99,102,241,0.08); color: var(--color-primary); }
.attr-val.disabled { opacity: 0.4; cursor: not-allowed; }
.attr-icon { width: 24px; height: 24px; object-fit: contain; border-radius: 4px; }

/* Shipping */
.info-row { display: flex; align-items: center; padding: 10px 0; border-bottom: 1px solid var(--border-color); gap: 12px; }
.info-row:last-child { border-bottom: none; }
.info-label { font-size: 13px; color: var(--text-secondary); white-space: nowrap; min-width: 60px; }
.info-val { flex: 1; font-size: 13px; color: var(--text-primary); }

/* Shop */
.shop-card { cursor: pointer; }
.shop-top { display: flex; align-items: center; gap: 12px; }
.shop-avatar { width: 44px; height: 44px; border-radius: 50%; object-fit: cover; }
.shop-mid { flex: 1; display: flex; flex-direction: column; gap: 4px; }
.shop-name { font-size: 14px; font-weight: 500; }
.shop-stats { font-size: 11px; color: var(--text-muted); }

/* 底部 */
.bottom-bar {
  position: fixed; bottom: 0; width: 100%; max-width: 480px;
  background: var(--bg-primary); border-top: 1px solid var(--border-color);
  display: flex; align-items: center; padding: 8px 16px;
  padding-bottom: calc(8px + env(safe-area-inset-bottom, 0));
  gap: 12px; z-index: 50;
}
.bar-left { display: flex; flex-direction: column; align-items: center; gap: 2px; font-size: 10px; color: var(--text-muted); cursor: pointer; }
.bar-right { flex: 1; display: flex; gap: 8px; }
.btn-cart { flex: 1; height: 40px; border-radius: 20px; border: 1.5px solid var(--color-primary); background: transparent; color: var(--color-primary); font-size: 14px; font-weight: 500; cursor: pointer; }
.btn-buy { flex: 1; height: 40px; border-radius: 20px; border: none; background: linear-gradient(135deg, var(--color-primary), var(--color-primary-dark)); color: #fff; font-size: 14px; font-weight: 600; cursor: pointer; }

.shipping-popup { padding: 20px; font-size: 13px; color: var(--text-secondary); line-height: 1.8; }
</style>
