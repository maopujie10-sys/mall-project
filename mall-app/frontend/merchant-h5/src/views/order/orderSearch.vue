<template>
  <div class="search-container" :class="{'is-ar': isArLang}">
    <van-nav-bar fixed left-arrow @click-left="() => $router.back()">
      <template #title>
        <van-search v-model="keyword" shape="round" @search="onSearch" :clearable="false"
                    :placeholder="$t('请输入订单号')">
          <template #left-icon>
            <img class="search-icon" src="@/assets/imgs/product/search-icon.png" />
          </template>
          <template #right-icon>
            <van-icon v-if="keyword" name="cross" @click="clearHandle" size="14" color="#333333" />
          </template>
        </van-search>
      </template>
      <template #right>
        <div @click="onSearch">{{ t('搜索') }}</div>
      </template>
    </van-nav-bar>
    <div class="list ml-4 mr-4 mt-4 mb-4" v-if="list.length > 0">
      <van-pull-refresh v-model="refreshing" :loading-text="$t('加载中')" :loosing-text="$t('释放以刷新')" :pulling-text="$t('下拉以刷新')" @refresh="onRefresh(false)">
        <van-list v-model:loading="loading" :finished="finished" :finished-text="t('没有更多了')" @load="getListData">
          <orderItem v-for="item in list" :info="item" />
        </van-list>
      </van-pull-refresh>
    </div>
    <van-empty v-if="!list.length && searchEd" :image="empytImg.href" :description="t('noData')" />
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { orderlist } from "@/service/my.api";   //  接口地址
import orderItem from "./orderItem.vue";
import { useI18n } from 'vue-i18n';
import { Toast } from 'vant'
import { arLangCheck } from '@/utils/arLangCheck'

const isArLang = arLangCheck()
const { t } = useI18n();
let keyword = ref('')
let pageNum = ref(1)
const list = ref([]);
const loading = ref(false);
const finished = ref(false);
const refreshing = ref(false);
const searchEd = ref(false);

const empytImg = new URL('@/assets/image/public/no_data.png', import.meta.url)

const clearHandle = () => {
  pageNum.value = 1
  keyword.value = ''
  finished.value = false
  loading.value = true
  pageNum.value = 1
  searchEd.value = false
  list.value = []
}

const onRefresh = (flag) => {
  if (keyword.value) {
    searchEd.value = false
    finished.value = false
    loading.value = true
    pageNum.value = 1

    if (flag) {
      Toast.loading({
          forbidClick: true,
          loadingType: 'spinner',
          duration: 0
      });
    }
    getListData()
  } else {
    Toast(t('请输入订单号'))
    loading.value = false
    refreshing.value = false
    finished.value = true
    list.value = []
  }
}

const onSearch = () => {
  onRefresh(true)
}

const getListData = () => {
  const params = {
    pageNum: pageNum.value,
    pageSize: 20,
    orderId: keyword.value
  }

  orderlist(params).then(res => {
    const { pageInfo, pageList } = res

    list.value = pageNum.value === 1 ? pageList : [...list.value, ...pageList]
    
    loading.value = false
    refreshing.value = false
    searchEd.value = true
    finished.value = pageInfo.lastPage
    pageNum.value++
    Toast.clear()
  }).catch(() => {
    Toast.clear()
  })
}

</script>

<style lang="scss" scoped>
.search-container {
  padding-top: 50px;
  &.is-ar {
    :deep(.van-field__left-icon) {
      margin-right: 0;
      margin-left: 8px;
    }
    :deep(.van-search__content) {
      padding-left: 0;
      padding-right: 12px;
    }
    :deep(.van-field__control) {
      text-align: right;
    }
  }

  :deep(.van-field__left-icon) {
    display: flex;
    align-items: center;
    width: 16px;
    margin-right: 8px;

    >img {
      width: 100%;
      height: auto;
    }
  }

  :deep(.van-nav-bar__left) {
    padding-right: 10px !important;
  }

  :deep(.van-nav-bar__title) {
    width: 73.6% !important;
    max-width: 73.6% !important;
    position: relative;
  }

  :deep(.van-search) {
    padding: 0 !important;

    .van-search__content {
      background-color: #fff;
    }
  }

  .search-btn {
    font-size: 12px;
    color: #333;
  }

  .search-history {
    padding: 0 15px;

    >.title {
      padding: 25px 0;
      display: flex;
      align-items: center;
      justify-content: space-between;
      font-size: 14px;
      color: #000;

      >.clear {
        display: flex;
        align-items: center;

        >img {
          width: 14px;
          height: auto;
          margin-right: 5px;
        }

        >p {
          font-size: 14px;
          color: #333;
        }
      }
    }

    >.content {
      overflow: hidden;

      &.no {
        display: flex;
        justify-content: center;
        font-size: 14px;
        color: #999;
      }

      >.item {
        float: left;
        padding: 4px 15px;
        background-color: #fff;
        border-radius: 5px;
        color: #999;
        font-size: 12px;
        margin-right: 14px;
        margin-bottom: 22px;
      }
    }
  }

  .search-tips-content {
    >.item {
      padding: 23px 15px;
      border-bottom: 1px solid #eee;
      display: flex;
      align-items: center;

      .van-icon {
        margin-right: 5px;
      }

      >p {
        color: #333;
        font-size: 12px;
      }
    }
  }

  .shop-list-content {
    padding: 20px 15px;

    >.tips {
      font-size: 12px;
      color: #333;

      >span {
        color: #F89900;
      }
    }
  }
}

:deep(.van-icon) {
  font-size: 18px;
  color: #1F2025;
}

.delete-icon {
  width: 15px;
}

.list {
  .item {
    background: #FFFFFF;
    border-radius: 4px;
    // align-items: center;
    margin-bottom: 20px;

    .more-icon {
      width: 20px;
    }

    .product-img {
      width: 100px;
    }

    .left {
      align-items: center;

      .product-info {
        padding-left: 10px;

        .name {
          font-size: 14px;
          color: #333333;
          width: 180px;
          height: 50px;
          font-weight: bold;
          overflow: hidden;
          display: -webkit-box;
          -webkit-box-orient: vertical;
          -webkit-line-clamp: 2;
          -ms-text-overflow: ellipsis;
          text-overflow: ellipsis;
        }

        .Specification {
          font-size: 12px;
          color: #999999;
        }

        .money {
          color: var(--site-main-color);
          font-weight: bold;
        }
      }
    }

  }

  .product-img-wrap {
    position: relative;
  }

  .delete-wrap {
    padding: 0 15px;
    background: rgba(0, 0, 0, 0.6);
    position: absolute;
    left: 0;
    top: 0;
    font-size: 12px;
    color: #fff;
  }
}

.result-list {
  position: fixed;
  top: 46px;
  left: 0;
  width: 100%;
  background: #fff;
  z-index: 2;
  font-size: 14px;

  .result-list-item {
    border-bottom: 1px solid #EFF2F6;
  }
}
</style>
