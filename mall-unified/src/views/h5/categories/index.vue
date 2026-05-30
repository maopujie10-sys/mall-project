<template>
  <div class="categories-page">
    <h2 class="page-title">{{ $t('common.categories') }}</h2>

    <!-- 分类列表 -->
    <div class="cat-grid" v-if="categories.length">
      <div v-for="item in categories" :key="item.categoryId || item.id" class="cat-card" @click="goCategory(item)">
        <div class="cat-img-wrap">
          <img :src="item.iconImg || item.image || defaultImg" class="cat-img" />
        </div>
        <span class="cat-name">{{ item.name }}</span>
      </div>
    </div>

    <van-empty v-if="!categories.length && !loading" :description="$t('common.noData')" />
    <div v-if="loading" class="loading-tip">{{ $t('common.loading') }}</div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { Empty as VanEmpty } from 'vant'
import { apiGetRecommendGoods } from '@/api/home'

const router = useRouter()
const categories = ref([])
const loading = ref(false)
const defaultImg = 'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMjAwIiBoZWlnaHQ9IjIwMCIgdmlld0JveD0iMCAwIDIwMCAyMDAiIGZpbGw9Im5vbmUiPjxyZWN0IHdpZHRoPSIyMDAiIGhlaWdodD0iMjAwIiBmaWxsPSIjZjFmNWY5Ii8+PC9zdmc+'

onMounted(async () => {
  if (localStorage.getItem('index_categoryList')) {
    categories.value = JSON.parse(localStorage.getItem('index_categoryList'))
    return
  }
  loading.value = true
  try {
    const res = await apiGetRecommendGoods({ pageNum: 1, pageSize: 20 })
    categories.value = res.pageList || []
  } catch (e) {}
  loading.value = false
})

function goCategory(item) {
  sessionStorage.removeItem('classificationState')
  router.push({ path: '/m/categories', query: { categoryId: item.categoryId, className: item.name } })
}
</script>

<style scoped>
.categories-page { min-height: 100vh; background: var(--bg-secondary); padding: 16px; }
.page-title { font-size: 18px; font-weight: 700; color: var(--text-primary); margin-bottom: 16px; }
.cat-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 10px; }
.cat-card {
  background: var(--bg-primary); border-radius: var(--border-radius);
  box-shadow: var(--shadow-sm); padding: 16px; text-align: center;
  cursor: pointer; transition: transform var(--transition-fast), box-shadow var(--transition-fast);
}
.cat-card:active { transform: scale(0.97); box-shadow: var(--shadow-md); }
.cat-img-wrap { width: 64px; height: 64px; margin: 0 auto 10px; display: flex; align-items: center; justify-content: center; }
.cat-img { max-width: 56px; max-height: 56px; object-fit: contain; }
.cat-name { font-size: 13px; color: var(--text-primary); display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; }
.loading-tip { text-align: center; padding: 40px; color: var(--text-muted); font-size: 13px; }
</style>
