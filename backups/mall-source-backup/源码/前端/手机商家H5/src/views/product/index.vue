<template>
  <div class="product">
    <div @click="search">
      <van-search
        class="search-wrap"
        disabled
        v-model="value"
        :placeholder="$t('请输入搜索商品名称')"
        clearable
      >
        <template #left-icon="icon">
          <img class="search-icon" src="@/assets/imgs/product/search-icon.png" />
        </template>
    </van-search>
    </div>
    

    <div class="flex ml-4 mr-4 product-header">
      <div class="flex-1 text-center after" @click="openCommodits">
        <div class="moeny icon" v-if="hideProNum">
          <img :src="getImg('image/order/diamond.svg')" alt="">
        </div>
        <div v-else class="moeny">{{ numberStrFormat(systemGoodsNum, 0) }}</div>
        <div class="title">{{ $t('商品库') }}<van-icon name="arrow" /></div>
      </div>
      <div class="flex-1 text-center" @click="openComment">
        <div class="moeny">{{ evaluations }}</div>
        <div class="title">{{ $t('评论') }}<van-icon name="arrow" /></div>
      </div>
    </div>
    <div class="hot-title ml-4 mr-4 mt-4 mb-4">
      {{ $t('店铺产品') }}({{ numberStrFormat(sellerGoodsNum, 0) }})
    </div>
    <div class="list ml-4 mr-4 mt-4 mb-4 list-content" :class="{'is-ar': isArLang}">
      <van-pull-refresh
        v-model="refreshing"
        @refresh="onRefresh"
        :loading-text="$t('加载中')" :loosing-text="$t('释放以刷新')" :pulling-text="$t('下拉以刷新')">
        <van-list
          ref="vanList"
          v-model:loading="loading"
          :loading-text="$t('加载中')"
          :finished="finished"
          :finished-text="$t('noMore')"
          @load="onLoad">
          <div
            class="item pl-3 pr-3 pb-3 pt-3 flex"
            @click="getdDtails(item)"
            v-for="(item, index) in list"
            :class="{'goods-removed': item.isShelf / 1 === 0}"
            :key="index"
          >
            <div class="flex-1 flex left" >
              <div class="product-img-wrap w-20 h-20 ">
                <img class="product-img" :src="item.imgUrl1" />
                <div v-if="item.isShelf / 1 === 0" class="take_off">{{$t('已下架')}}</div>
<!--                <div class="delete-wrap" @click.stop="deleteGood(item)">-->
<!--                  {{ $t('删除') }}-->
<!--                </div>-->
              </div>
              <div class="product-info flex-1">
                <div class="name-content">
                  <p>{{ item.name }}</p>
                  <div class="more" @click.stop="openEdit(item)">
                    <img
                      class="more-icon"
                      src="@/assets/imgs/product/more.png"
                    />
                  </div>
                </div>
                <!-- <div class="name">{{ item.name }}</div> -->
                <div class="Specification">
                  <span>{{ item.categoryName }}</span>
                  <span style="margin-left: 20px">{{ $t('销量') }}: {{ numberStrFormat(item.soldNum, 0) }}</span>
                </div>
                <div class="money-content">
                  <p>${{ numberStrFormat(item.sellingPrice) }}</p>
                  <p v-if="item.discountPrice" class="dis">{{$t('折扣价')}} ${{ numberStrFormat(item.discountPrice) }}</p>
                </div>
              </div>
            </div>
            <!-- <div>
              <img
                class="more-icon"
                @click.stop="openEdit(item)"
                src="@/assets/imgs/product/more.png"
              />
            </div> -->
          </div>
        </van-list>
      </van-pull-refresh>
      <div class="safe-area-inset-bottom"></div>
    </div>
  </div>
</template>

<script setup name="ProductIndex">
import {onMounted, computed, ref, onActivated} from 'vue'
import { merchantGoodsList, sellerGoodsdelete, sysParaProductInfo } from '@/service/product.api'
import { useRoute, useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { Toast, Dialog } from 'vant'
import { numberStrFormat } from '@/utils'
import { arLangCheck } from '@/utils/arLangCheck'
import { getImg } from '@/utils'

const isArLang = arLangCheck()
const { t } = useI18n()
const route = useRoute()
const router = useRouter()
let value = ref('')
let isEdit = ref(false)
let pageNum = ref(1)
let evaluations = ref(0)
let systemGoodsNum = ref(0)
let sellerGoodsNum = ref(0)
let productInfo = ref({})
const list = ref([])
const loading = ref(false)
const refreshing = ref(false)
const finished = ref(false)

const mode = import.meta.env.MODE

// 隐藏商品库数量
const hideProNum = computed(() => {
  return ['int'].includes(mode)
})

const deleteGood = (item) => {  // 删除商家自己的商品（假删除）
  Dialog.confirm({
    title: '提示',
    message: '确认删除吗？'
  })
      .then(() => {
        sellerGoodsdelete({ sellerGoodsId: item.id }).then(() => {
          // onLoad()
          // onRefresh()
          Toast('操作成功')
          const index = list.value.findIndex((item2) => item2.id === item.id)
          if (index) {
            list.value.splice(index, 1)
          }
        })
      })
      .catch(() => {
        // on cancel
      })
}

const firstLoading = ref(true)
// 页面打开后再次激活
onActivated(() => {
  if (!firstLoading.value) {
    if (sessionStorage.getItem('productReload')) {
      sessionStorage.removeItem('productReload')
      onLoad(true)
    }

    const currentProductId = sessionStorage.getItem('currentProductId')
    if (currentProductId) {
      const index = list.value.findIndex(item => item.id === currentProductId)
      if (sessionStorage.getItem('productDelete')) {
        list.value.splice(index, 1)
        sellerGoodsNum.value -= 1
        sessionStorage.removeItem('productDelete')
      } else {
        onLoad(true)
      }

      sessionStorage.removeItem('currentProductId')
    }
  }
})

const onLoad = (flag) => {
  if (flag) {
    pageNum.value = 1
  }

  let data = {
    pageNum: pageNum.value,
    pageSize: 20
  }

  merchantGoodsList(data).then((res) => {
    firstLoading.value = false
    if (refreshing.value) {
      refreshing.value = false
    }

    evaluations.value = res.evaluations
    systemGoodsNum.value = res.systemGoodsNum
    sellerGoodsNum.value = res.sellerGoodsNum

    if (flag) {
      list.value = res.pageList || []
    } else {
      list.value = pageNum.value === 1 ? res.pageList : [...list.value, ...res.pageList]
    }

    finished.value = list.value.length >= res.sellerGoodsNum
    pageNum.value++

    // 加载状态结束
    loading.value = false
  })
}

const onRefresh = () => {
  onLoad(true)
}
const search = () => {
  router.push('/search?id=1')
}
const openCommodits = () => {
  router.push('/productPage/list')
}
const openComment = () => {
  router.push('/productPage/comment')
}
const getdDtails = (item) => {
  router.push({
    path: '/productPage/details',
    query: { item: JSON.stringify(item) }
  })
}
const close = () => {
  isEdit.value = false
}

const sysParaMin = ref('')
const sysParaMax = ref('')
sysParaProductInfo().then(res => {
  sysParaMin.value = res.sysParaMin
  sysParaMax.value = res.sysParaMax
})

const openEdit = (item) => {
  item.sysParaMin = sysParaMin.value
  item.sysParaMax = sysParaMax.value
  router.push({ path: '/productPage/productEdit', query: { item: JSON.stringify(item) } })
  // isEdit.value = true
  productInfo.value = item
}
const updateInfo = (item, price) => {
  item.sellingPrice = price
}

onMounted(() => {
  document.addEventListener('langChange', () => {
    onRefresh()
  })
})

</script>

<style scoped lang="scss">
.take_off {
  position: absolute;
  left: 50%;
  top: 50%;
  margin-left: -35px;
  margin-top: -35px;
  transform: rotate(-45deg);
  border: 3px solid #e74343;
  color: #e74343;
  border-radius: 50%;
  font-size: 13px;
  width: 70px;
  height: 70px;
  display: flex;
  justify-content: center;
  align-items: center;
}
.product {
  padding-top: 20px;
  padding-bottom: 50px;

  .search-wrap {
    margin: 0 15px;
    border-radius: 25px;
    height: 45px;
    text-align: center;
    pointer-events: none;

    .search-icon {
      height: 24px;
    }
  }

  .product-header {
    background: #ffffff;
    border-radius: 4px;
    padding: 20px 0;
    margin-top: 20px;

    .moeny {
      font-weight: 600;
      font-size: 20px;
      height: 24px;
      display: flex;
      align-items: center;
      justify-content: center;
      &.icon {
        height: 34px;
        > img {
          height: 34px;
          width: auto;
        }
        + .title {
          margin-top: 0;
        }
      }
    }

    .title {
      margin-top: 10px;
      color: #999999;
      font-size: 12px;
    }

    .after {
      position: relative;

      &::after {
        position: absolute;
        height: 100%;
        width: 1px;
        background: #dddddd;
        content: '';
        right: 0;
        top: 0;
      }
    }
  }

  .list {
    .item {
      background: #ffffff;
      border-radius: 4px;
      // align-items: center;
      margin-bottom: 20px;

      .more-icon {
        width: 20px;
      }

      .product-img {
        flex-shrink: 0;
        width: 100%;
        height: auto;
      }

      .left {
        align-items: center;

        .product-info {
          padding-left: 10px;

          .name-content {
            width: 100%;
            display: flex;
            align-items: flex-start;
            margin-bottom: 5px;
            > p {
              flex: 1;
              font-size: 14px;
              color: #333333;
              line-height: 16px;
              font-weight: bold;
              overflow: hidden;
              display: -webkit-box;
              -webkit-box-orient: vertical;
              -webkit-line-clamp: 2;
              -ms-text-overflow: ellipsis;
              text-overflow: ellipsis;
              word-break: break-all;
            }
            > .more {
              width: 40px;
              height: 30px;
              display: flex;
              justify-content: flex-end;
              align-items: flex-start;
              padding-top: 5px;
            }
          }

          .name {
            font-size: 14px;
            color: #333333;
            width: 180px;
            line-height: 16px;
            font-weight: bold;
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
            font-weight: 400;
          }
          .money-content {
            width: 100%;
            display: flex;
            align-items: center;
            justify-content: space-between;
            color: var(--site-main-color);
            font-weight: 400;
            > .dis {
              font-size: 14px;
              color: #FF3E3E;
            }
          }
        }
      }
    }

    .product-img-wrap {
      position: relative;
      overflow: hidden;
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
}

:deep(.van-search__content) {
  background: #fff;
}

:deep(.search-wrap .van-field__control) {
  text-align: center;
}

.list-content {
  min-height: 60vh;
  &.is-ar {
    .item .left .product-info {
      padding-left: 0;
      padding-right: 10px;
    }
  }
  :deep(.van-list) {
    min-height: 60vh;
  }
}

.goods-removed {
  background-color: #f5f5f5;
}
</style>
