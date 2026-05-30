<template>
  <div class="product">
    <fx-header fixed>
      <template #title>{{t('product.2')}}</template>
      <template #right>
        <!-- <img @click="isShow = true" class="nav_filtering_icon" src="@/assets/imgs/product/nav_filtering.png" /> -->
        <img @click="search" class="nav_filtering_icon" src="@/assets/imgs/product/search-icon-top.png" />
      </template>
    </fx-header>
    <div class="dropdown">
      <div class="dropdownitem one h-10.5" @click="classifyOneShow = true">
        <div class="p-2.5 bg-white flex justify-between items-center w-full h-full">
          <span class="text-xs">{{ title1 }}</span>
          <div class="triangle"></div>
        </div>
      </div>

      <div class="dropdownitem one h-10.5" @click="classifyTwoShow = true">
        <div class="p-2.5 bg-white flex justify-between items-center w-full h-full">
          <span class="text-xs">{{ title2 }}</span>
          <div class="triangle"></div>
        </div>
      </div>
    </div>

    <van-popup v-model:show="classifyOneShow" round>
      <div class="classify-pop-content">
        <div class="title">{{ t('一级分类') }}</div>
        <div class="content">
          <div v-for="item in categoryOneArry" :key="item.categoryId" class="classify-item" @click="classifyHandle(item, true)">
            {{ item.name }}
            <van-icon v-if="classifyOneActive === item.categoryId" name="success" class="yes"/>
          </div>
        </div>
      </div>
    </van-popup>
    <van-popup v-model:show="classifyTwoShow" round>
      <div class="classify-pop-content">
        <div class="title">{{ t('二级分类') }}</div>
        <div class="content">
          <div v-for="item in categoryTwoArry" :key="item.categoryId" class="classify-item" @click="classifyHandle(item, false)">
            {{ item.name }}
            <van-icon v-if="classifyTwoActive === item.categoryId" name="success" class="yes"/>
          </div>
        </div>
      </div>
    </van-popup>
    <div class="list mt-4 mb-4" :class="isArLang? 'ml-4' : 'mr-4'">

      <van-pull-refresh :loading-text="$t('加载中')" :loosing-text="$t('释放以刷新')" :pulling-text="$t('下拉以刷新')" v-model="refreshing" @refresh="onRefresh">
        <van-list v-model:loading="loading" :loading-text="$t('加载中')" :finished="finished" :finished-text="t('product.3')" @load="onLoad">
          <div class="item pb-3 pt-3 flex" v-for="(item, index) in list" :key="index">
            <div class="pl-3 pr-3 ">
              <div class="check-icon" @click="itemCheckHandle(item)" :class="[item.check ? 'check-true ' : 'check']">
                <i class="iconfont icon-duigoux"></i>
              </div>
            </div>
            <div class="flex-1 flex left">
              <div class="product-img-wrap">
                <img class="w-20 h-20" style="object-fit: contain" :src="item.imgUrl1" />
              </div>
              <div class="product-info" :class="{'is-ar': isArLang}">
                <div class="name">{{ item.name }}</div>
                <div class="Specification">
                  <span>{{ item.categoryName }}</span>
                  <!-- <span>{{t('product.4')}}: {{item.unit || '-'}}</span> -->
                  <!-- <span>Sales: {{1000}}</span> -->
                </div>
                <div class="money">${{ numberStrFormat(item.systemPrice) }}</div>
              </div>
            </div>
          </div>
        </van-list>
      </van-pull-refresh>
      <div v-if="bottomShow" class="flex fixed-wrap" :class="{'pl-3': !isArLang && !bottomDisabledType, 'pr-3': isArLang && !bottomDisabledType}">
        <div v-if="!bottomDisabledType" class="flex-1 flex " @click="allCheck">
          <div class="check-icon" :class="[isAll ? 'check-true ' : 'check']">
            <i class="iconfont icon-duigoux"></i>
          </div>
          <div :class="isArLang? 'pr-2' : 'pl-2'">
            {{t('product.5')}}: {{ selectNumber() }}
          </div>
        </div>
        <div v-if="!bottomDisabledType" class="submit-but" @click="openEdit">{{t('product.6')}}</div>
        <div v-else class="submit-but disabled" @click="openSetPage">{{ bottomDisabledType === 1 ? t('product.34') : t('product.35') }}</div>
      </div>
    </div>
    <!-- <van-action-sheet v-model:show="isShow"  :title="t('product.7')" :actions="categoryOneArry" @select="onSelect" /> -->
    <edit-profit :isEdit="isEdit" @update="updateInfo" :productArry="productArry" @close="close"></edit-profit>
  </div>
</template>

<script setup>
import { ref,onMounted,watch, computed } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { useI18n } from 'vue-i18n';
import { sellerInfo } from '@/service/shop.api.js'
import { _getIdentify } from '@/service/user.api.js'
import { getSystemGoods,categoryList,goodsaddOrUpdate, categoryListTree } from "@/service/product.api";
import editProfit from './components/editProfit.vue';
import { openPage, numberStrFormat } from '@/utils'
import { Toast } from 'vant';
import { arLangCheck } from '@/utils/arLangCheck'

const isArLang = arLangCheck()
const { t } = useI18n();
const route = useRoute()
const router = useRouter()
let value = ref('')
let isShow = ref(false)
let pageNum = ref(1)

let isAll = ref(false)
let isEdit = ref(false)
let productArry = ref([])
const list = ref([]);
const loading = ref(false);
const refreshing = ref(false);
const finished = ref(false);
const bottomShow = ref(false)
const bottomDisabledType = ref(0)

onMounted(() => {
  sessionStorage.setItem('productReload', true)
  getShopInfo()
  getCategory()
})

const getShopInfo = async () => {
  let dataInfo = {}
  // 基础信息
  await sellerInfo().then(res => {
    dataInfo = res || {}
  })

  // 认证信息
  await _getIdentify().then(res => {
    const status = Number(res.status)
    let statusInfo = status
    if (status === 2) {
      statusInfo = 3
    } else if (status === 3) {
      statusInfo = 2
    }
    dataInfo.authStatus = statusInfo
  })

  const { avatar, name, authStatus } = dataInfo
  if (!avatar || !name) {
    bottomDisabledType.value = 1
  } else if (authStatus === 0 || authStatus === 1 || authStatus === 2) {
    bottomDisabledType.value = 2
  }

  bottomShow.value = true
}

const openSetPage = () => {
  const href = bottomDisabledType.value === 1 ? '/shop/settings' : '/name'
  openPage(href)
}

const close = () => {
  isEdit.value = false
}

const openEdit = () => {
  productArry.value = []
  list.value.map((item) => {
    if (item.check) {
      productArry.value.push(item.id)
    }
  })

  if (productArry.value.length > 200) {
    Toast(t('一次性最多上架', {maxNum: 200}))
    return
  }

  if (productArry.value.length) {
    isEdit.value = true
  } else {
    Toast(t('请选择商品'))
  }
}

const onRefresh = () => {
  pageNum.value = 1
  list.value = []
  onLoad()
}

const onLoad = () => {
  let data = {
    pageNum: pageNum.value,
    pageSize: 20
  }
  if (classifyTwoActive.value) {
    data.secondaryCategoryId = classifyTwoActive.value
  } else {
    data.categoryId = classifyOneActive.value
  }
  getSystemGoods(data).then((res) => {
    if (refreshing.value) {
      refreshing.value = false
    }
    pageNum.value++
    for (let i = 0; i < res.pageList.length; i++) {
      res.pageList[i].check = false
      list.value.push(res.pageList[i]);
    }
    // 加载状态结束
    loading.value = false;

    if (res.pageList.length == 0) {
      finished.value = true;
    }
  })
}

const categoryOneArry = ref([])

const title1 = ref(t('一级分类'))
const title2 = ref(t('二级分类'))
const classifyOneShow = ref(false)
const classifyTwoShow = ref(false)
const classifyOneActive = ref('')
const classifyTwoActive = ref('')

const getCategory = () => {
  categoryListTree().then(res => {
    const data = res || []
    data.unshift({
      name: t('全部分类'),
      categoryId: '',
      subList: []
    })
    categoryOneArry.value = data.filter(item => item.name)
  })
}

const categoryTwoArry = computed(() => {
  const oneObj = categoryOneArry.value.find(item => item.categoryId === classifyOneActive.value)
  let dataArr = [{
    name: t('全部分类'),
    categoryId: ''
  }]
  if (oneObj && oneObj.subList && oneObj.subList.length) {
    const data = oneObj.subList.filter(item => item.name)
    dataArr = [...dataArr, ...data]
  }
  return dataArr
})

const classifyHandle = (data, flag) => {
  if (flag) { // 一级分类
    title1.value = data.name
    classifyOneActive.value = data.categoryId
    classifyOneShow.value = false
    title2.value = t('二级分类')
    classifyTwoActive.value = ''
  } else {
    title2.value = data.name
    classifyTwoActive.value = data.categoryId
    classifyTwoShow.value = false
  }
  Toast.loading({
    duration: 0,
    forbidClick: true
  })
  isAll.value = false
  pageNum.value = 1
  list.value = []
  selectNumber()
  onLoad()
}

const allCheck = () => {
  isAll.value = !isAll.value
  list.value.map(item=>{
    if (isAll.value) {
      item.check = true
    } else {
      item.check = false
    }
  })
}
const selectNumber = () => {
  let  number = 0
  list.value.map(item=>{
    if (item.check) {
      number = number+1
    }
  })
  return number
}
const search = () => {
  router.push('/search?id=2')
}

const updateInfo = () => {
  isAll.value = false
  getCategory()
  onRefresh()
}

const itemCheckHandle = (data) => {
  data.check = !data.check
  const arr = list.value.filter(item => item.check)
  isAll.value = list.value.length === arr.length
}
</script>

<style scoped lang="scss">
.product {
  padding-top: 70px;
  padding-bottom: 50px;
  min-height: 100vh;
  background: #EFF2F6;

  .search-wrap {
    margin: 0 15px;
    border-radius: 25px;
    height: 45px;
    text-align: center;

    .search-icon {
      height: 24px;
    }
  }

  .product-header {
    background: #FFFFFF;
    border-radius: 4px;
    padding: 20px 0;
    margin-top: 20px;

    .moeny {
      font-weight: 600;
      font-size: 20px;
    }

    .title {
      margin-top: 10px;
      color: #999999;
    }

    .after {
      position: relative;

      &::after {
        position: absolute;
        height: 100%;
        width: 1px;
        background: #DDDDDD;
        content: '';
        right: 0;
        top: 0;
      }
    }
  }

  .list {
    .item {
      border-radius: 4px;
      align-items: center;

      .more-icon {
        width: 20px;
      }

      .product-img {
        width: 100px;
      }

      .left {
        align-items: center;
        background: #fff;
        padding: 12px;
        border-radius: 4px;

        .product-info {
          padding-left: 10px;
          flex: 1;
          &.is-ar {
            padding-left: 0;
            padding-right: 10px;
          }

          .name {
            font-size: 14px;
            color: #333333;
            line-height: 16px;
            font-weight: bold;
            word-break: break-all;
            overflow: hidden;
            display: -webkit-box;
            -webkit-box-orient: vertical;
            -webkit-line-clamp: 2;
            -ms-text-overflow: ellipsis;
            text-overflow: ellipsis;
            margin-bottom: 5px;
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

  .fixed-wrap {
    height: 50px;
    position: fixed;
    bottom: 0;
    left: 0;
    width: 100%;
    background: #fff;
    align-items: center;

    .submit-but {
      min-width: 130px;
      padding: 0 15px;
      background: var(--site-main-color);
      display: flex;
      align-items: center;
      justify-content: center;
      height: 100%;
      color: #fff;
      &.disabled {
        width: 100%;
        background-color: #666;
      }
    }
  }
}

.check-icon {
  width: 20px;
  height: 20px;
  border-radius: 50%;
  border: 1px solid #ccc;
  display: flex;
  align-items: center;
  justify-content: center;
  > .iconfont {
    color: #fff;
    font-size: 12px;
    opacity: 0;
  }
  &.check-true {
    border-color: var(--site-main-color);
    background-color: var(--site-main-color);
    > .iconfont {
      opacity: 1;
    }
  }
}

.nav_filtering_icon {
  width: 18px;
  height: 18px;
}

:deep(.van-search__content) {
  background: #fff;
}

:deep(.search-wrap .van-field__control) {
  text-align: center;
}

.dropdown {
  padding: 0 15px;
  justify-content: space-between;
  display: flex;
  width: 100%;

  .dropdownitem {
    width: 48%;
    border-radius: 5px;
    overflow: hidden;
  }
}

.triangle {
  width: 0;
  height: 0;
  border: 6px solid transparent;
  border-top-color: #000;
  position: relative;
  top: 3px;
}

.classify-pop-content {
  width: 18rem;
  min-height: 3rem;
  .title {
    width: 100%;
    height: 3rem;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 16px;
    color: #333;
    font-weight: bold;
    border-bottom: 1px solid #eaeaea;
  }

  .content {
    max-height: 60vh;
    overflow-y: scroll;
    .classify-item {
      width: 100%;
      height: 3rem;
      display: flex;
      align-items: center;
      justify-content: center;
      position: relative;
      border-bottom: 1px solid #eaeaea;
      &:last-child {
        border-bottom: none;
      }
      .yes {
        color: var(--site-main-color);
        position: absolute;
        right: 30px;
        top: 50%;
        -webkit-transform: translateY(-50%);
        transform: translateY(-50%);
      }
    }
  }
}
</style>
