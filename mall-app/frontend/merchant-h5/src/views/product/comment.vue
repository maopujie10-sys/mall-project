<template>
  <div class="comment">
    <fx-header fixed>
      <template #title>{{ t('product.23') }}</template>
    </fx-header>
    <div class="list">
      <van-pull-refresh v-model="refreshing" :pulling-text="t('pullingText')" :loosing-text="t('loosingText')" :loading-text="t('loading')" @refresh="onRefresh">
        <van-list v-model:loading="loading" :finished="finished" :loading-text="t('loading')" :finished-text="list.length ? t('product.3') : ''" @load="getListData">
          <div v-if="list.length">
            <div class="pl-3 pr-3 pt-4 comment-info pb-5" :class="{'is-ar': isArLang}" v-for="(item, index) in list" :key="index">
              <div class="flex score">
                <div class="flex user-name">
                  <img class="user-img" :src="fullImg(item.avatar)"/>
                  <span class="text-black text-sm">{{ hideUserName(item.userName) }}</span>
                </div>
                <div>
                  <van-rate :size="20" color="#FFC93E" v-model="item.rating"/>
                </div>
              </div>
              <div class="comment-text pt-3 pb-3" style="color: #666">
                {{ item.content || t('用户未发表评论') }}
              </div>
              <div class="flex overflow-x-auto mb-3">
                <img @click="viewImg(item)" class="w-1/4 img-icon" :class="isArLang ? 'ml-1.5': 'mr-1.5'" v-for="(item, index) in handleImgs(item)" :key="'imgs' + index" :src="item" alt="">
              </div>
              <div class="item py-1 flex">
                <div class="flex-1 flex left">
                  <div v-if="item.goodsVo.imgUrl1" class="product-img-wrap w-28 h-28" @click="viewImg(item.goodsVo.imgUrl1)">
                    <van-image :src="item.goodsVo.imgUrl1" class="product-img">
                      <template v-slot:error>
                        <van-icon name="photo-fail"/>
                      </template>
                    </van-image>
                  </div>
                  <div class="product-info flex-1">
                    <div class="name">{{ item.goodsVo.name }}</div>
                    <div class="flex justify-between">
                      <div class="money">${{ numberStrFormat(item.goodsVo.systemPrice) }}</div>
                      <div class="comment-time">{{ formatZoneDate(item.commentTime) }}</div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
          <van-empty v-if="!list.length && !loading" :image="empytImg.href" :description="t('noData')" />
        </van-list>
      </van-pull-refresh>
    </div>
  </div>
</template>

<script setup>
import {ImagePreview} from 'vant';
import {ref} from 'vue';
import {useI18n} from 'vue-i18n';
import {getEvaluation} from "@/service/product.api";
import {formatZoneDate, numberStrFormat} from '@/utils'
import { arLangCheck } from '@/utils/arLangCheck'

const isArLang = arLangCheck()
const {t} = useI18n();
const list = ref([]);
const loading = ref(false);
const finished = ref(false);
let pageNum = ref(1)
const refreshing = ref(false)


const empytImg = new URL('@/assets/image/public/no_data.png', import.meta.url)

const viewImg = (item) => {
  ImagePreview([item]);
}

const onRefresh = () => {
  loading.value = false;
  pageNum.value = 1
  getListData()
}

const handleImgs = (item) => {
  const add = []
  Object.keys(item).forEach(key => {
    if (key.indexOf('imgUrl') > -1 && item[key]) {
      add.push(item[key])
    }
  })
  return add
}

const getListData = () => {
  const params = {
    pageNum: pageNum.value,
    pageSize: 20,
  }
  getEvaluation(params)
      .then((res) => {
        refreshing.value = false;

        const {pageInfo, pageList} = res
        const data = pageList || []
        data.map(item => {
          item.avatar = item.avatar || Math.floor(Math.random() * 20)
        })
        const tempArr = data.sort((a, b) => (b.createTime / 1) - (a.createTime / 1))
        list.value = pageNum.value === 1 ? tempArr : [...list.value, ...tempArr]
        pageNum.value++
        loading.value = false
        refreshing.value = false

        finished.value = pageInfo.lastPage
      })
      .catch(() => {
        finished.value = true
        loading.value = false
        refreshing.value = false
      })
}

/**
 * 头像
 */
const fullImg = (num) => {
  return num ? new URL(`/src/assets/image/userAvatar/${num}.png`, import.meta.url).href : new URL('@/assets/imgs/me/defaultAvatar.png', import.meta.url).href
}

/**
 * 数据脱敏
 */
function hideUserName(useName) {
  let str = useName.substring(2, useName.length - 1)
  let name = useName.replace(str, '***')
  return name
}

</script>

<style scoped lang="scss">
.img-icon:last-child {
  margin-right: 0;
}

.comment {
  padding-top: var(--van-nav-bar-height);
  box-sizing: border-box;
  // padding-top: 50px;
  // min-height: 100vh;
  // background: #EFF2F6;

  .comment-info {
    background: #fff;
    margin-top: 10px;
    &.is-ar {
      .score .user-img {
        margin-right: 0;
        margin-left: 10px;
      }
      .product-info {
        padding-left: 0;
        padding-right: 10px;
        .name {
          word-break: break-all;
        }
      }
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

  .score {
    justify-content: space-between;
    align-items: center;

    .user-name {
      align-items: center;
      color: #999999;
    }

    .user-img {
      width: 32px;
      height: 32px;
      border-radius: 50%;
      margin-right: 10px;
    }
  }

  .comment-text {
    font-size: 14px;
    color: #333;
    word-wrap: break-word;
  }

  .comment-time {
    font-size: 12px;
    color: #999;
  }

  .list {
    .item {
      border-radius: 4px;
      align-items: center;
      box-shadow: 0 0 10px 4px rgba(0, 0, 0, .05);
      background: #fff;

      .more-icon {
        width: 20px;
      }

      .product-img {
        width: 100%;
        height: 100%;
        object-fit: cover;
      }

      .left {
        align-items: center;
        padding: 12px;
        border-radius: 4px;

        .product-info {
          padding-left: 10px;

          .name {
            font-size: 14px;
            color: #333333;
            //width: 180px;
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
}

</style>