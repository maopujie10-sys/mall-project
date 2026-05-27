<template>

  <div class="editProduct">
    <fx-header fixed>
      <template #title>
        <div>{{ $t('编辑商品') }}</div>
      </template>
    </fx-header>
    <div class="edit-product-pop" :class="{'is-ar': isArLang}">
      <!--        <div class="title">{{$t('编辑商品')}}</div>-->
      <van-form>
        <div class="tip pt-2 pb-2 pl-4 pr-4">{{ $t('当前售价') }}</div>
        <van-cell-group class="input-field" inset>
          <!-- <van-field v-model="fromData.discountPrice" readonly :placeholder="$t('当前售价')"> -->
          <van-field v-model="fromData.sellingPrice" type="number" :placeholder="$t('当前售价')"
                     @input="sellingPriceInput">
            <template #button>
              <!-- <span class="profit">{{$t('利润')}} {{ (fromData.discountPrice - fromData.systemPrice).toFixed(2) }}</span> -->
              <span class="profit">{{ $t('利润') }} {{ profitNum }}</span>
            </template>
          </van-field>
        </van-cell-group>
        <div v-if="!hideShelf" class="flex pl-4 pr-4 input-item pt-3 pb-3">
          <div>{{ $t('是否上架') }}</div>
          <div class="flex">
            <van-switch
                v-model="fromData.isShelf"
                size="25"
                inactive-color="#fff"
                :inactive-value="0"
                :active-value="1"
            />
          </div>
        </div>
        <div class="flex pl-4 pr-4 input-item pt-3 pb-3">
          <div>{{ $t('是否推荐') }}</div>
          <div class="flex">
            <van-switch v-model="fromData.recTime" :inactive-value="0"
                        :active-value="1" size="25" inactive-color="#fff"/>
          </div>
        </div>
        <!--          <div class="tip pt-2 pb-2 pl-4 pr-4" v-if="fromData.isRecommend">{{$t('推荐时间')}}</div>-->
        <!--          <van-cell-group v-if="fromData.isRecommend" class="input-field" inset>-->
        <!--            <van-field @click-input="onClick(3)"  v-model="fromData.recTime" :placeholder="t('推荐时间')">-->

        <!--            </van-field>-->
        <!--          </van-cell-group>-->
        <!--          <van-popup v-model:show="isRecommendShow"-->
        <!--                     round-->
        <!--                     position="bottom"-->
        <!--          >-->
        <!--            <van-datetime-picker-->
        <!--                :confirm-button-text="$t('确定')"-->
        <!--                :cancel-button-text="$t('取消')"-->
        <!--                v-model="recommendTime"-->
        <!--                type="datetime"-->
        <!--                :title="t('选择完整时间')"-->
        <!--                @confirm="onConfirm(3)"-->
        <!--                @cancel="onCancel(3)"-->
        <!--            />-->
        <!--          </van-popup>-->
        <div class="flex pl-4 pr-4 input-item pt-3 pb-3">
          <div>{{ $t('直通车') }}</div>
          <div class="flex">
            <van-switch :loading="isChecking" v-model="fromData.isCombo" size="25"
                        inactive-color="#fff"/>
          </div>
        </div>
        <div class="tip pt-2 pb-2 pl-4 pr-4">{{ $t('百分比') }}</div>
        <van-cell-group class="input-field" inset>
          <van-field v-model="fromData.percent" type="number" :placeholder="t('百分比')"
                     :rules="[{ required: true, message: t('请填写百分比'), max: profitRange.max, min: profitRange.min }]"
                     @input="percentInput" @blur="percentBlur">
            <template #button>
              <span>%</span>
            </template>
          </van-field>
        </van-cell-group>
        <div class="tips pt-2 pb-2 pl-4 pr-4">{{ $t('将选中的商品发布到你的店铺，并填写商品利润比例，推荐比例') }}: <span>{{
            profitRange.min
          }}%-{{ profitRange.max }}%</span></div>
        <div class="tip pt-2 pb-2 pl-4 pr-4">{{ $t('折扣开始日期') }}</div>
        <van-cell-group class="input-field" inset style="position: relative;">
          <div v-if="fromData.startTime" class="time-clear" @click="fromData.startTime = ''">
            <van-icon name="cross"/>
          </div>
          <van-field @click-input="onClick(1)" v-model="fromData.startTime" :placeholder="t('折扣开始日期')">
          </van-field>
          <van-popup v-model:show="isShow"
                     round
                     position="bottom"
          >
            <van-datetime-picker
                :min-date="minDate"
                :confirm-button-text="$t('确定')"
                :cancel-button-text="$t('取消')"
                v-model="startTime"
                type="date"
                :title="t('选择完整时间')"
                @confirm="onConfirm(1)"
                @cancel="onCancel(1)"
            />
          </van-popup>
        </van-cell-group>
        <div class="tip pt-2 pb-2 pl-4 pr-4">{{ $t('折扣结束日期') }}</div>
        <van-cell-group class="input-field" inset style="position: relative;">
          <div v-if="fromData.endTime" class="time-clear" @click="fromData.endTime = ''">
            <van-icon name="cross"/>
          </div>
          <van-field @click-input="onClick(2)" v-model="fromData.endTime" :placeholder="t('折扣结束日期')">
          </van-field>
        </van-cell-group>
        <div class="tip pt-2 pb-2 pl-4 pr-4">{{ $t('折扣比例') }}</div>
        <van-cell-group class="input-field" inset>
          <van-field v-model="fromData.discount" type="number" :placeholder="t('折扣比例')">
            <template #button>
              <span>%</span>
            </template>
          </van-field>
        </van-cell-group>
        <van-popup v-model:show="isEndShow"
                   round
                   position="bottom">
          <van-datetime-picker
              :min-date="minDate"
              :cancel-button-text="$t('取消')"
              :confirm-button-text="$t('确定')"
              v-model="endTime"
              type="date"
              :title="t('选择完整时间')"
              @confirm="onConfirm(2)"
              @cancel="onCancel(2)"
          />
        </van-popup>
        <div style="margin: 16px;" class="pb-8">
          <van-button class="btn-content" block type="primary" @click="onSubmitPre"
                      native-type="submit">
            {{ $t('保存') }}
          </van-button>
          <van-button v-if="!hideDelBtn" style=" margin-top: 16px; background-color: red; border-radius: 4px; border-color: red" block
                      type="primary" @click.stop="deleteGood" native-type="submit">
            {{ $t('删除') }}
          </van-button>
        </div>
      </van-form>
    </div>
  </div>
</template>

<script setup>
import {goodsUpdate, sellerGoodsdelete, sysParaProductInfo} from "@/service/product.api";
import {computed, onMounted, reactive, ref, watch} from 'vue';
import {useRoute, useRouter} from 'vue-router';
import {useI18n} from 'vue-i18n';
import {openPage, numberStrFormat} from '@/utils'
import {Dialog, Toast} from "vant";
import dayjs from 'dayjs'
import {arLangCheck} from '@/utils/arLangCheck'
import {useUserStore} from '@/store/user';

const mode = import.meta.env.MODE
const userStore = useUserStore()

// 隐藏上下架选择
const hideShelf = computed(() => {
  // return ['sm', 'familyShop'].includes(mode)
})

// 隐藏删除按钮
const hideDelBtn = computed(() => {
  // return ['sm', 'familyShop'].includes(mode)
})

const isArLang = arLangCheck()
const {t} = useI18n();
const route = useRoute()
const router = useRouter()
const productInfo = ref(JSON.parse(route.query.item));
const minDate = ref(new Date())
const fromData = ref({
  sellingPrice: '', // 展示
  isShelf: 0,
  recTime: 0,
  isCombo: false,
  // isRecommend: false,
  startTime: dayjs(),
  endTime: dayjs(),
  discount: "",
  percent: "",
  profit: '',
  id: ""
})
const deleteGood = () => {
  Dialog.confirm({
    title: t('product.21'),
    message: t('product.22'),
    confirmButtonText: t('sure'),
    cancelButtonText: t('cancel')
  })
      .then(() => {
        sellerGoodsdelete({sellerGoodsId: fromData.value.id}).then(() => {
          // onLoad()
          // onRefresh()
          sessionStorage.setItem('currentProductId', productInfo.value.id)
          sessionStorage.setItem('productDelete', true)
          Toast(t('product.10'))
          router.go(-1)
        })
      })
      .catch(() => {
        // on cancel
      })
}
const isShow = ref(false);
const isEndShow = ref(false);
const isRecommendShow = ref(false);
const startTime = ref("");
const endTime = ref("");
const recommendTime = ref("");

// 用户信息
const userInfo = computed(() => {
  let obj = {}
  if (!userStore.userInfo.token) {
    router.push('/login')
  } else {
    obj = {...userStore.userInfo}
  }
  return obj
})

onMounted(() => {
  init();
})

watch(() => fromData.value.percent, (val, old) => {
  // console.log(val, old)
  // console.log(fromData.value.systemPrice)
  // fromData.value.sellingPrice = (fromData.value.systemPrice * (1 + val / 100)).toFixed(2);
})

watch(() => fromData.value.isCombo, (val, old) => {
  if (val) {
    console.log('开关打开')
    checkComboStatus()
  }
})
watch(() => fromData.value.isShelf, (val, old) => {
  console.log('开关打开', val)
  if (val / 1 === 1) {
    checkIsShelfStatus()
  }
})
//
// watch(() => fromData.value.percent, (val ,old) => {
//   console.log('fromData.value.percent')
//   console.log('new', val)
//   console.log('old', old)
// })

const isChecking = ref(false) // 是否在检查直通车状态
const checkComboStatus = () => {
  isChecking.value = true
  onSubmit()
}
const isChecking2 = ref(false) // 检查是否能下架
const checkIsShelfStatus = () => {
  isChecking2.value = true
  onSubmit()
}

const profitRange = reactive({
  min: '',
  max: ''
})

const init = () => {
  fromData.value.id = productInfo.value.id
  fromData.value.discountPrice = productInfo.value.discountPrice ? numberStrFormat(productInfo.value.discountPrice / 1, 2, true) : numberStrFormat(productInfo.value.sellingPrice / 1, 2, true) // 折扣价优先显示
  fromData.value.sellingPrice = numberStrFormat(productInfo.value.sellingPrice / 1, 2, true)
  fromData.value.isShelf = productInfo.value.isShelf / 1
  fromData.value.isCombo = Boolean(productInfo.value.isCombo / 1)
  // fromData.value.recTime = productInfo.value.recTime / 1 === 0 ? '' : dayjs(productInfo.value.recTime / 1).format('YYYY-MM-DD HH:mm:ss')
  fromData.value.recTime = productInfo.value.recTime / 1
  // fromData.value.isRecommend = !productInfo.value.recTime ? false : true
  // fromData.value.startTime = productInfo.value.discountStartTime.split(' ')[0]
  fromData.value.startTime = productInfo.value.discountStartTime ? productInfo.value.discountStartTime.split(' ')[0] : productInfo.value.discountStartTime
  // fromData.value.endTime = productInfo.value.discountEndTime.split(' ')[0]
  fromData.value.endTime = productInfo.value.discountEndTime ? productInfo.value.discountEndTime.split(' ')[0] : productInfo.value.discountEndTime


  fromData.value.profit = numberStrFormat(productInfo.value.profitRatio * 100, 2, true)
  fromData.value.discount = numberStrFormat(productInfo.value.discountRatio * 100, 2, true)
  fromData.value.systemPrice = numberStrFormat(productInfo.value.systemPrice / 1, 2, true)

  // fromData.value.percent = ((((productInfo.value.sellingPrice / 1) - (productInfo.value.systemPrice / 1)) / productInfo.value.systemPrice) * 100).toFixed(2)
  // fromData.value.discount = (((productInfo.value.sellingPrice / 1 - productInfo.value.discountPrice / 1) / (productInfo.value.sellingPrice / 1)) * 100).toFixed(2) || 0;

  fromData.value.percent = numberStrFormat(productInfo.value.profitRatio / 1 * 100, 2, true)
  profitRange.min = Number(productInfo.value.sysParaMin)
  profitRange.max = Number(productInfo.value.sysParaMax)
  // 请求利润区间
  sysParaProductInfo().then(res => {
    profitRange.min = Number(res.sysParaMin)
    profitRange.max = Number(res.sysParaMax)
  })
}

const onSubmitPre = () => {
  // ['sm'].includes(mode)
  if ([].includes(mode)) {
    if (userInfo.value.phoneverif && userInfo.value.emailverif) {
      onSubmit()
    } else {
      const tips = !userInfo.value.phoneverif ? '请绑定手机号' : 'bindEmailTips'
      Dialog.confirm({
        title: t('dialogTips'),
        message: t(tips),
        cancelButtonText: t('cancel'),
        confirmButtonText: t('gotoSet'),
        confirmButtonColor: '#1552F0',
        cancelButtonColor: '#999'
      }).then(() => {
        openPage('/personalInfo')
      }).catch(() => {
        console.log('cancel')
      });
    }
  } else {
    onSubmit()
  }
}

const pageLoading = ref(false)

const onSubmit = () => {
  const {startTime, endTime, discount} = fromData.value
  if (startTime || endTime) {
    const startTimeS = new Date(startTime.replace(/-/g, '/') + ' 00:00:00').getTime()
    const endTimeS = new Date(endTime.replace(/-/g, '/') + ' 00:00:00').getTime()
    if (!discount) {
      // isChecking.value = false
      // isChecking2.value = false
      // fromData.value.isCombo = false
      // fromData.value.isShelf = false
      Toast(t('请设置折扣比例'))
      return
    }
    if (startTimeS > endTimeS) {
      // isChecking.value = false
      // isChecking2.value = false
      // fromData.value.isCombo = false
      // fromData.value.isShelf = false
      Toast(t('开始时间应小于结束时间'))
      return
    }
  }
  if (Number(discount) && (!startTime || !endTime)) {
    // isChecking.value = false
    // isChecking2.value = false
    // fromData.value.isCombo = false
    // fromData.value.isShelf = false
    Toast(t('请正确填写活动开启时间和结束时间'))
    return
  }
  if (!percentBlur()) {
    if (!pageLoading.value) {
      pageLoading.value = true
      Toast.loading({
        forbidClick: true,
        loadingType: 'spinner',
        duration: 0
      });
    }
    
    let dataJson = {
      // sellingPrice: fromData.value.sellingPrice,
      isShelf: fromData.value.isShelf ? 1 : 0,
      recTime: fromData.value.recTime ? 1 : 0,
      // recTime: fromData.value.isRecommend ? dayjs(fromData.value.recTime).valueOf() : 0,
      isCombo: fromData.value.isCombo ? 1 : 0,
      sellerGoodsId: productInfo.value.id,
      startTime: fromData.value.startTime ? fromData.value.startTime + ' 00:00:00' : '',
      endTime: fromData.value.endTime ? fromData.value.endTime + ' 00:00:00' : '',
      discount: numberStrFormat(fromData.value.discount / 100, 2, true),
      percent: numberStrFormat(fromData.value.percent / 100, 2, true),
      profit: numberStrFormat(fromData.value.percent / 100, 2, true),
    }

    return goodsUpdate(dataJson).then((res) => {
      Toast.clear()
      pageLoading.value = false

      sessionStorage.setItem('currentProductId', productInfo.value.id)
      if (isChecking.value) { // 是在检查直通车状态
        isChecking.value = false
      } else if (isChecking2.value) { // 是在检查能否上架状态
        isChecking2.value = false
      } else { // 是更新整体状态
        Toast(t('product.10'));
        router.push('/product')
      }
    }).catch((err) => { // 处理直通车状态检查 和 上下架状态检查
      pageLoading.value = false

      const msg = err.msg
      isChecking.value = false
      isChecking2.value = false

      if (msg.indexOf('未购买') > -1) {
        Toast(t('您暂未购买直通车套餐，请购买再试'))
      } else if (msg.indexOf('已到期') > -1) {
        Toast(t('您的直通车已到期'))
      } else if (msg.indexOf('最多推广') > -1) {
        const msgArr = msg.split('最多推广商品数量为')
        Toast(t('最多推广商品数量为') + ': ' + msgArr[1])
      } else if (msg.indexOf('未激活') > -1) {
        Toast(t('您的直通未激活'))
      } else if (msg.indexOf('未激活') > -1) {
        Toast(t('您的直通未激活'))
      } else if (msg.indexOf('最小下架') > -1) {
        Toast(t('少于店铺设置最小下架商品数'))
      } else if (msg.indexOf('首次上架') > -1) {
        const limitObj = (typeof err.data) === 'string' ? JSON.parse(err.data) : err.data
        Toast(t(msg, {_$1: limitObj._$1}))
      } else {
        Toast(t(msg))
      }
      fromData.value.isCombo = false
    })
  }
};

const onClick = (index) => {
  switch (index) {
    case 1:
      isShow.value = true
      break;
    case 2:
      isEndShow.value = true
      break;
    case 3:
      isRecommendShow.value = true
      break;
  }
}

const onConfirm = (index) => {
  console.log(startTime.value);

  switch (index) {
    case 1:
      isShow.value = false
      fromData.value.startTime = dayjs(startTime.value).format('YYYY-MM-DD')
      break;
    case 2:
      isEndShow.value = false
      fromData.value.endTime = dayjs(endTime.value).format('YYYY-MM-DD')
      break;
    case 3:
      isRecommendShow.value = false
      fromData.value.recTime = formatter(recommendTime.value)
      break;

  }
}

const onCancel = (index) => {
  switch (index) {
    case 1:
      isShow.value = false
      break;
    case 2:
      isEndShow.value = false
      break;
    case 3:
      isRecommendShow.value = false
      break;
  }
}

const formatter = (dat) => {
  //获取年月日，时间
  let year = dat.getFullYear();
  let mon = (dat.getMonth() + 1) < 10 ? "0" + (dat.getMonth() + 1) : dat.getMonth() + 1;
  let data = dat.getDate() < 10 ? "0" + (dat.getDate()) : dat.getDate();
  let hour = dat.getHours() < 10 ? "0" + (dat.getHours()) : dat.getHours();
  let min = dat.getMinutes() < 10 ? "0" + (dat.getMinutes()) : dat.getMinutes();
  let seon = dat.getSeconds() < 10 ? "0" + (dat.getSeconds()) : dat.getSeconds();

  let newDate = year + "-" + mon + "-" + data + " " + hour + ":" + min + ":" + seon;
  return newDate;
}

const profitNum = computed(() => {
  let profit = 0
  if (!isNaN(fromData.value.sellingPrice) && !isNaN(fromData.value.discount)) {
    const systemPrice = Number(fromData.value.systemPrice) // 成本价
    const discount = Number(numberStrFormat(Number(fromData.value.discount) / 100, 2, true)) // 折扣比例
    const discountPer = Number(fromData.value.sellingPrice) * (1 - discount) // 折扣价
    profit = Number((discountPer - systemPrice))
  }
  return numberStrFormat(profit, 2, true)
})

const percentInput = () => {

  const systemPrice = Number(fromData.value.systemPrice) // 成本价
  const percent = Number(numberStrFormat(Number(fromData.value.percent) / 100, 2, true))
  fromData.value.sellingPrice = Number(numberStrFormat(systemPrice + (systemPrice * percent),2 ,true))
}

const percentBlur = () => {
  const percent = Number(fromData.value.percent)
  const discount = Number(fromData.value.discount)
  let res = false
  if (!isNaN(percent)) {
    const reg = /^\+?[1-9][0-9]*$/
    if (!reg.test(String(percent))) {
      Toast(t('百分比必须为正整数'))
      return true
    }
    if (discount && !reg.test(String(discount))) {
      Toast(t('折扣比例必须为正整数'))
      return true
    }
    if (percent > profitRange.max) {
      console.log('12')
      fromData.value.percent = profitRange.max
      res = true
      percentInput()
    }
    if (percent < profitRange.min) {
      console.log('33')
      fromData.value.percent = profitRange.min
      res = true
      percentInput()
    }
  }
  if (res && profitRange.min && profitRange.max) {
    Toast(t(`百分比设置范围为`) + `：${profitRange.min}% ~ ${profitRange.max}%`)
  }
  return res
}

const sellingPriceInput = () => {
  const sellingPrice = Number(fromData.value.sellingPrice) // 售价
  const systemPrice = Number(fromData.value.systemPrice) // 成本价
  const percent = Number(numberStrFormat(((sellingPrice - systemPrice) / systemPrice) * 100, 2, true))

  fromData.value.percent = percent
}

</script>

<style scoped lang="scss">
.editProduct {
  background: #fff;
  color: #333;

  .title {
    text-align: center;
    line-height: 55px;
    font-size: 16px;
    font-weight: bold;
  }

  .edit-product-pop {
    padding-top: 46px;

    &.is-ar {
      :deep(.van-field__control) {
        text-align: right;
      }
    }
  }

  .tip {
    font-size: 14px;

  }

  .tips {
    font-size: 12px;
    line-height: 18px;
    color: #000000;

    span {
      color: #1552F0;
    }
  }

  .input-field {
    border: 1px solid #ddd;

    .profit {
      color: #0ECB81;
    }

  }

  .input-item {
    justify-content: space-between;
    align-items: center;

  }
}

.time-clear {
  width: 44px;
  height: 44px;
  background-color: #fff;
  position: absolute;
  z-index: 9;
  right: 0;
  top: 0;
  display: flex;
  align-items: center;
  justify-content: center;
}

.btn-content {
  background-color: var(--site-main-color);
  border-color: var(--site-main-color);
  border-radius: 4px;
}
</style>
