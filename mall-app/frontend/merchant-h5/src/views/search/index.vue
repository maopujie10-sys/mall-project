<template>
  <div class="search-container" :class="{'is-ar': isArLang}">
    <van-nav-bar fixed left-arrow @click-left="() => $router.back()">
      <template #title>
<!--        <van-search v-model="keyword" shape="round" @blur="record" @update:model-value="search" :clearable="false"-->
<!--          placeholder="请输入商品" @input="inputHandle">-->
        <van-search v-model="keyword" shape="round" :clearable="false"
                    :placeholder="$t('请输入商品')" @input="inputHandle">
          <template #left-icon>
            <img class="search-icon" src="@/assets/imgs/product/search-icon.png" />
          </template>
          <template #right-icon>
            <van-icon v-if="keyword" name="cross" @click="clearHandle" size="14" color="#333333" />
          </template>
        </van-search>
      </template>
      <template #right>
        <div @click="search">{{ $t('搜索') }}</div>
      </template>
    </van-nav-bar>
    <div class="result-list pl-4 pr-4" v-if="resultList.length > 0">
      <div class="result-list-item pt-2 pb-2" @click="searchGoods(item)" v-for="(item, index) in resultList"
        :key="index">
        {{ item.name }}
      </div>
    </div>
    <div class="search-history" v-if="list.length == 0">
      <div class="title">
        <p>{{ $t('历史搜索') }}</p>
        <div class="clear" @click="emptyHandle" v-show="searchList.length > 0">
          <img src="@/assets/imgs/product/delete.png" alt="" class="delete-icon" />
          <p @click="clear">{{ $t('清空') }}</p>
        </div>
      </div>
      <div class="content" v-if="searchList.length > 0">
        <div :key="index" class="item" v-for="(item, index) in searchList" @click="tipsHandle(item)">{{ item }}
        </div>
      </div>
      <van-empty v-if="!searchList.length" :image="empytImg.href" :description="t('noData')" />
    </div>
    <div class="list ml-4 mr-4 mt-4 mb-4" v-if="list.length > 0">

      <van-pull-refresh :loading-text="$t('加载中')" :loosing-text="$t('释放以刷新')" :pulling-text="$t('下拉以刷新')" v-model="loading" @refresh="onRefresh">
        <van-list ref="checkEl" v-model:loading="loading" :finished="finished" :finished-text="$t('没有更多了')" @load="onLoad">
          <div class="item pl-3 pr-3 pb-3 pt-3 flex" @click="getdDtails(item)" v-for="(item, index) in list"
            :key="index">
            <div class="flex-1 flex left">
              <div class="product-img-wrap w-20 h-20 " style="overflow:hidden;">
                <img class="product-img" :src="item.imgUrl1" />
<!--                <div class="delete-wrap" @click.stop="deleteGood(item)">删除</div>-->
              </div>
              <div class="product-info">
                <div class="name">{{ item.name }}</div>
                <div class="Specification">
                  <span v-if="item.categoryName" style="margin-right: 20px">{{ item.categoryName }}</span>
                  <!-- <span>{{t('product.4')}}: {{ item.unit || '-' }}</span> -->
                  <span v-if="id / 1 === 1">{{ t('sales') }}: {{ item.soldNum }}</span>
                </div>
                <div class="money">${{ id / 1 === 1 ? numberStrFormat(item.sellingPrice) : numberStrFormat(item.systemPrice) }}</div>
              </div>
            </div>
            <div class="item-more-content">
              <div class="more" @click.stop="openEdit(item)">
                <img class="more-icon" src="@/assets/imgs/product/more.png" />
              </div>
              <van-icon v-if="id / 1 === 1" name="arrow" size="20px" style="top: 50%; right: 0; position: absolute; margin-top: -10px;" />
            </div>

          </div>
        </van-list>
      </van-pull-refresh>

    </div>
    <edit-profit :isEdit="isEdit" @update="updateInfo" :productArry="productArry" @close="close"></edit-profit>
  </div>
</template>

<script setup>
import {ref, onMounted, onUpdated} from 'vue';
import { useDebounceFn } from '@vueuse/core'
import editProfit from '../product/components/editProfit.vue';
import { useRoute, useRouter } from 'vue-router';
import { useI18n } from 'vue-i18n';
import { numberStrFormat } from '@/utils'
import { arLangCheck } from '@/utils/arLangCheck'
import {
  getSystemGoods,
  searchSllerKeyword,
  sellerGoodsList2
} from "@/service/product.api";
import { setStorage, getStorage } from '@/utils/index'
import { Toast, Dialog } from 'vant'
import clonedeep from 'lodash.clonedeep'

const isArLang = arLangCheck()
const { t } = useI18n();
const router = useRouter();
const route = useRoute();
const id = ref(route.query.id) // 1:搜索卖家自己的商品 2:搜索商品库商品
let keyword = ref('')
let pageNum = ref(1)
let goodsId = ref('')
let isEdit = ref(false)
let productInfo = ref({})
const list = ref([]);
const resultList = ref([]);
const refreshing = ref(false)
const loading = ref(false);
const finished = ref(false);
let searchList = ref([])
const inputHandle = () => {

}


const empytImg = new URL('@/assets/image/public/no_data.png', import.meta.url)

const checkEl = ref(null)

onUpdated(() => {
  if (checkEl.value) {
    console.log(checkEl.value);
  }

})

onMounted(() => {


  if (id.value / 1 === 1) {
    if (getStorage('searchOne')) {
      searchList.value = getStorage('searchOne')
    }
  } else {
    if (getStorage('searchTwo')) {
      searchList.value = getStorage('searchTwo')
    }
  }
})
const search = useDebounceFn(() => {
  if (keyword.value.trim()) {
    pageNum.value = 1
    list.value = []
    Toast.loading({
      forbidClick: true,
      loadingType: 'spinner'
    })
    onLoad()
    record()
  } else {
    Toast({
      message: t('请输入搜索关键字'),
      duration: 2000
    })
  }
}, 500)

const record = () => {
  const keywordStr = keyword.value.trim()
  const keyStr = id.value / 1 === 1 ? 'searchOne' : 'searchTwo'

  if (keywordStr != '') {
    if (searchList.value.length == 0) {
      searchList.value.push(keywordStr)
      setStorage(keyStr, searchList.value)
    } else {
      const dataArr = clonedeep(searchList.value)
      dataArr.unshift(keywordStr)

      const storeArr = [...new Set(dataArr)]
      searchList.value = storeArr
      setStorage(keyStr, storeArr)
    }
  }
}

const emptyHandle = () => {
  if (id.value / 1 === 1) {
    setStorage('searchOne', [])
  } else {
    setStorage('searchTwo', [])
  }
}
const clearHandle = () => {
  keyword.value = ''
}
const tipsHandle = (item) => {
  keyword.value = item
  search()
}
const clear = (item) => {
  searchList.value = []
  if (id.value / 1 === 1) {
    setStorage('searchOne', '')
  } else {
    setStorage('searchTwo', '')
  }

}



const onRefresh = () => {
  refreshing.value = false;
  search()
}

const searchSellerGoods = () => {
  let data = {
    pageNum: pageNum.value,
    pageSize: 20,
    keyword: keyword.value
  }
  sellerGoodsList2(data).then((res) => { // 搜索卖家自己的商品
    console.log(res);
    Toast.clear()
    pageNum.value++
    for (let i = 0; i < res.pageList.length; i++) {
      res.pageList[i].check = false
      list.value.push(res.pageList[i]);
    }
    // 加载状态结束
    loading.value = false;

    if (res.pageList.length < 20) {
      if (pageNum.value > 1) {
        Toast(t('没有更多数据'));
      }
      finished.value = true;
    } else {
      pageNum.value++
    }
  })

}

const searchStoreGoods = () => {
  let data = {
    name: keyword.value,
    categoryId: '',
    pageNum: pageNum.value,
    pageSize: 20,
  }
  getSystemGoods(data).then((res) => {
    Toast.clear()
    console.log('商家自己的商品', res)
    for (let i = 0; i < res.pageList.length; i++) {
      list.value.push(res.pageList[i]);
    }
    // 加载状态结束
    loading.value = false;

    if (res.pageList.length < 20) {
      if (pageNum.value > 1) {
        Toast(t('没有更多数据'));
      }
      finished.value = true;
    } else {
      pageNum.value++
    }
  })
}

const currentSearchFunc = ref(null)
if (id.value / 1 === 2) {
  currentSearchFunc.value = searchStoreGoods
} else {
  currentSearchFunc.value = searchSellerGoods
}

const onLoad = () => {
  console.log(123)
  currentSearchFunc.value()
}
const searchGoods = (item) => {
  console.log('ssss', item)
  keyword.value = ''
  resultList.value = []
  goodsId.value = item.goodsId
  pageNum.value = 1
  list.value = []
  onLoad()
  // if (id.value / 1 === 1) {
  //   onLoad()
  // } else {
  //   searchSellerGoods()
  // }

}
let productArry = ref([])
const openEdit = (item) => {
  if (id.value/1 === 1) {
    router.push({ path: '/productPage/productEdit', query: { item: JSON.stringify(item) } })
  } else {
    productArry.value = []
    // list.value.map((item) => {
    //   if (item.check) {
    //     productArry.value.push(item.id)
    //   }
    // })
    productArry.value.push(item.id)
    isEdit.value = true
  }
  // isEdit.value = true
  // productInfo.value = item
}
const updateInfo = (item, price) => {
  item.sellingPrice = price
}
const close = () => {
  isEdit.value = false
}
const getdDtails = (item) => {
  if (id.value/1 === 1) {
    router.push({ path: '/productPage/details', query: { item: JSON.stringify(item) } })
  }
}
const deleteGood = (item) => {
  Dialog.confirm({
    title: '提示',
    message:
      '确认删除吗？',
  })
    .then(() => {
      // TODO: 找到接口实现
      // sellerGoodsdelete({ sellerGoodsId: item.id }).then(() => {
      //   onLoad()
      //   Toast('操作成功');
      // })
    })
    .catch(() => {
      // on cancel
    });


}
</script>

<style lang="scss" scoped>
:deep(.van-field__body) {
  padding-right: 10px;
}
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
    .search-history > .title > .clear > img {
      margin-right: 0;
      margin-left: 5px;
    }
    .product-info {
      padding-left: 0;
      padding-right: 10px;
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
        flex: 1;

        .name {
          font-size: 14px;
          color: #333333;
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

.item-more-content {
  width: 40px;
  position: relative;
  > .more {
    width: 40px;
    height: 40px;
    display: flex;
    justify-content: flex-end;
    align-items: flex-start;
    padding-top: 5px;
  }
}
</style>
