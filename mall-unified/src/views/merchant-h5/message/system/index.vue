<template>
  <div class="page-main-content">
    <fx-header :fixed="true">
      <template #title>
        {{ $t('系统消息') }}
      </template>
    </fx-header>
    <div style="height: 46px" />

    <van-pull-refresh
      v-model="refreshing"
      :loading-text="$t('加载中')"
      :loosing-text="$t('释放以刷新')"
      :pulling-text="$t('下拉以刷新')"
      @refresh="onRefresh"
    >
      <van-list
        v-model:loading="loading"
        :finished="finished"
        :loading-text="t('loading')"
        :finished-text="t('product.3')"
        @load="getListData"
      >
        <div v-if="listData.length" class="list-content">
          <div
            v-for="item in listData"
            :key="item.id"
            class="item-list"
            @click="goToDetails(item)"
          >
            <div class="title-content">
              <div class="title">
                <div
                  v-if="item.status === 1"
                  class="tips"
                  :class="{ 'is-ar': isArLang }"
                ></div>
                <p>{{ t(msgTypeInfo[item.bizType].title) }}</p>
              </div>
              <p>{{ item.timeStr }}</p>
            </div>
            <p v-if="msgTypeInfo[item.bizType].key" class="txt">
              <template v-if="msgTypeInfo[item.bizType].key === 'creditScore'">
                <span
                  v-html="
                    t('systemMsgScore', {
                      creditScore: getValueStr(
                        item,
                        msgTypeInfo[item.bizType].key
                      )
                    })
                  "
                ></span>
              </template>
              <template v-else-if="item.bizType === 'inbox_recharge_success'">
                <span
                  v-html="
                    t('rechargeSuccessTips', {
                      orderAmount: getValueStr(item, 'orderAmount')
                    })
                  "
                ></span>
              </template>
              <template v-else-if="item.bizType === 'inbox_withdraw_success'">
                <span
                  v-html="
                    t('withdrawalSuccessTips', {
                      orderAmount: getValueStr(item, 'orderAmount')
                    })
                  "
                ></span>
              </template>
              <template v-else-if="item.bizType === 'inbox_store_audit_fail'">
                <span
                  v-html="
                    t('storeAuthenticationFailedTips', {
                      shop_name: getValueOf(item, 'shop_name'),
                      reason: getValueOf(item, 'reason')
                    })
                  "
                ></span>
              </template>
              <template
                v-else-if="item.bizType === 'inbox_store_audit_success'"
              >
                <span
                  v-html="
                    t('storeAuthenticationPassedTips', {
                      shop_name: getValueOf(item, 'shop_name')
                    })
                  "
                ></span>
              </template>
              <template v-else>
                <span>{{ t(msgTypeInfo[item.bizType].txt) }}</span>
                <span>{{
                  getValueStr(item, msgTypeInfo[item.bizType].key)
                }}</span>
                <span v-if="msgTypeInfo[item.bizType].txt1">{{
                  t(msgTypeInfo[item.bizType].txt1)
                }}</span>
              </template>
            </p>
            <p v-else class="txt">{{ t(msgTypeInfo[item.bizType].txt, item.varObj) }}</p>
          </div>
        </div>
        <van-empty v-if="!listData.length && !loading" :image="empytImg.href" />
      </van-list>
    </van-pull-refresh>
  </div>
</template>

<script setup name="MessageSystem">
import { ref, nextTick } from 'vue'
import { useI18n } from 'vue-i18n'
import { openPage, dataTime } from '@/utils'
import { msgTypeInfo } from './../config'
import { arLangCheck } from '@/utils/arLangCheck'

import { messagePagelist, messageRead } from '@/service/user.api.js'

const { t } = useI18n()

const isArLang = arLangCheck()

const empytImg = new URL('@/assets/image/public/no_data.png', import.meta.url)
const listData = ref([])
const refreshing = ref(false)
const loading = ref(true)
const finished = ref(false)
const page = ref({
  pageSize: 20,
  pageNum: 1
})

const getListData = () => {
  const params = {
    ...page.value,
    totalElements: -1,
    type: 3,
    status: 0,
    module: 1
  }
  messagePagelist(params)
    .then((res) => {
      const pageList = res.elements || []
      pageList.forEach((item) => {
        const varObj = {}
        const dataArr = item.varInfo ? JSON.parse(item.varInfo) : []
        dataArr.forEach(_item => {
          varObj[_item.code] = ['complaintReason'].includes(_item.code) ? t(_item.value) : _item.value
        })

        item.timeStr = dataTime(item.sendTime, true)
        item.varObj = varObj
      })
      listData.value =
        page.value.pageNum === 1
          ? pageList
          : [...listData.value, ...pageList]
      loading.value = false
      refreshing.value = false

      finished.value = res.totalPage === page.value.pageNum || !res.totalPage
      page.value.pageNum += 1
    })
    .catch(() => {
      finished.value = true
      loading.value = false
      refreshing.value = false
    })
}

const onRefresh = () => {
  loading.value = true
  page.value.pageNum = 1
  getListData()
}

const goToDetails = (data) => {
  openPage({
    path: '/message/details',
    query: {
      id: data.id
    }
  })
  if (data.status !== 2) {
    messageRead({ ids: data.id }).then(() => {
      data.status = 2
    })
  }
}

const getValueStr = (data, key) => {
  const dataArr = data.varInfo ? JSON.parse(data.varInfo) : []
  const item = dataArr.find((item) => item.code === key)
  return item ? item.value : '0'
}

const getValueOf = (data, key) => {
  const dataArr = data.varInfo ? JSON.parse(data.varInfo) : []
  const item = dataArr.find((item) => item.code === key)
  return item ? item.value : ''
}

nextTick(() => {
  document.addEventListener(
  'systemListRefresh',
  () => {
    onRefresh()
  },
  false
)
})
</script>

<style lang="scss" scoped>
.van-pull-refresh {
  background-color: #eff2f6;
}

.list-content {
  .item-list {
    padding: 15px;
    border-bottom: 1px solid #eee;
    background-color: #fff;
    > .title-content {
      width: 100%;
      display: flex;
      align-items: center;
      justify-content: space-between;
      > .title {
        display: flex;
        align-items: center;
        width: calc(100% - 120px);
        > .tips {
          width: 8px;
          height: 8px;
          border-radius: 50%;
          background: #ff3e3e;
          margin-right: 8px;
          &.is-ar {
            margin-right: 0;
            margin-left: 8px;
          }
        }
        > p {
          font-size: 14px;
          color: #000;
          flex: 1;
          text-overflow: ellipsis;
          overflow: hidden;
          white-space: nowrap;
        }
      }
      > p {
        font-size: 10px;
        color: #999;
      }
    }
    > .txt {
      font-size: 12px;
      margin-top: 5px;
      word-break: break-all;
      text-overflow: ellipsis;
      display: -webkit-box;
      -webkit-box-orient: vertical;
      -webkit-line-clamp: 3; /* 这里是超出几行省略 */
      overflow: hidden;
    }
  }
}
</style>
