<template>
  <div>
    <fx-header :fixed="true">
      <template #title>
        {{ pageTitle }}
      </template>
    </fx-header>
    <div style="height: 46px;" />

    <van-pull-refresh v-model="refreshing" :pulling-text="t('pullingText')" :loosing-text="t('loosingText')" :loading-text="t('loading')" @refresh="onRefresh">
      <van-list v-model:loading="loading" :finished="finished" :loading-text="t('loading')" :finished-text="t('product.3')" @load="getListData">
        <div v-if="listData.length" class="list-content">
          <goods-item v-for="item in listData" :key="item.id" :goods-data="item" />
        </div>
        <van-empty v-if="!listData.length && !loading" :image="empytImg.href" :description="t('noData')" />
      </van-list>
    </van-pull-refresh>
  </div>
</template>

<script>
import { defineComponent, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRoute } from 'vue-router'
import GoodsItem from './../components/GoodsItem.vue'
import {
  merchantGoodsList
} from '@/service/product.api.js'

export default defineComponent({
  name: 'ShopClass',
  components: {
    GoodsItem
  },
  setup() {
    const { t } = useI18n()
    const route = useRoute()
    const pageTitle = ref('')
    const { name, id, sellerId } = route.query

    const empytImg = new URL('@/assets/image/public/no_data.png', import.meta.url)
    const listData = ref([])
    const refreshing = ref(false)
    const loading = ref(true)
    const finished = ref(false)
    const page = ref({
      pageNum: 1,
      pageSize: 20
    })

    const getListData = () => {
      if (name && id && sellerId) {
        const params = {
          ...page.value,
          categoryId: id,
          sellerId
        }
        merchantGoodsList(params).then(res => {
          const pageList = res.pageList || []
          listData.value = page.value.pageNum === 1 ? pageList : [...listData.value, ...pageList]
          page.value.pageNum++
          loading.value = false
          refreshing.value = false
          
          finished.value = res.pageInfo.lastPage
        }).catch(() => {
          finished.value = true
          loading.value = false
          refreshing.value = false
        })
      } else {
        finished.value = true
        loading.value = false
        refreshing.value = false
      }
    }

    const onRefresh = () => {
      loading.value = true
      page.value.pageNum = 1
      getListData()
    }

    if (name && id && sellerId) {
      pageTitle.value = name
    }

    return {
      t,
      pageTitle,
      listData,
      refreshing,
      loading,
      finished,
      empytImg,
      getListData,
      onRefresh
    }
  }
})
</script>

<style lang="scss" scoped>
.list-content {
  padding: 15px;
}
</style>
