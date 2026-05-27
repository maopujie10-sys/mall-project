<template>

  <div class="editProduct" :class="{'is-ar': isArLang}">
    <van-popup v-model:show="props.isEdit" round closeable @click-close-icon="close"
               :style="{ height: '65%', width: '95%' }">
      <div class="edit-product-pop">
        <div class="title">{{ t('添加商品') }}</div>
        <van-form>
          <div class="tip pt-2 pb-2 pl-4 pr-4">{{ t('product.25') }}</div>
          <van-cell-group class="input-field" inset>
            <van-field v-model="fromData.percent" type="number" :placeholder="t('百分比')"
                       :rules="[{ required: true, message: t('请填写百分比'), max: profitRange.max, min:profitRange.min }]">
              <template #button>
                <span>%</span>
              </template>
            </van-field>
          </van-cell-group>
          <div class="tips pt-2 pb-2 pl-4 pr-4">{{ $t('将选中的商品发布到你的店铺，并填写商品利润比例，推荐比例') }}:
            <span>{{ profitRange.min }}%-{{ profitRange.max }}%</span></div>
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
                  :cancel-button-text="$t('取消')"
                  :confirm-button-text="$t('确定')"
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
                     position="bottom"
          >
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
          <div style="margin: 16px;">
            <van-button :disabled="disable" block class="btn-content" type="primary" @click="onSubmit"
                        native-type="submit">
              {{ t('product.26') }}
            </van-button>
          </div>
        </van-form>
      </div>
    </van-popup>
    <!-- <fx-header fixed>
      <template #title>编辑商品</template>
    </fx-header> -->
    <!-- <van-popup v-model:show="show" position="bottom">
      <div>
        <van-date-picker v-model="fromData.recTime" title="选择日期"   ></van-date-picker>

      </div>
    </van-popup> -->
  </div>
</template>

<script setup>
import {goodsaddOrUpdate, sysParaProductInfo} from "@/service/product.api";
import {computed, reactive, ref} from 'vue';
import {Dialog, Toast} from 'vant'
import {useRoute, useRouter} from 'vue-router';
import {useI18n} from 'vue-i18n';
import dayjs from "dayjs";
import {openPage} from '@/utils'
import {arLangCheck} from '@/utils/arLangCheck'
import {useUserStore} from '@/store/user';

const userStore = useUserStore()

let show = ref('true')
const {t} = useI18n();

const isArLang = arLangCheck()
const disable = ref(false)

const isShow = ref(false);
const isEndShow = ref(false);
const isRecommendShow = ref(false);
const minDate = ref(new Date())
const startTime = ref("");
const endTime = ref("");
const recommendTime = ref("");
const emit = defineEmits(['back', 'update'])
// const minDate = new Date(2020, 0, 1)
const route = useRoute()
const router = useRouter()
const fromData = ref({
  startTime: "",
  endTime: "",
  discount: "",
  percent: "",
})

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
const onSubmit = (values) => {
  const mode = import.meta.env.MODE
  //['sm'].includes(mode)
  if ([].includes(mode) && (!userInfo.value.phoneverif || !userInfo.value.emailverif)) {
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
    return
  }

  const {startTime, endTime, discount} = fromData.value
  if (startTime || endTime) {
    const startTimeS = new Date(startTime.replace(/-/g, '/') + ' 00:00:00').getTime()
    const endTimeS = new Date(endTime.replace(/-/g, '/') + ' 00:00:00').getTime()
    if (!discount) {
      Toast(t('请设置折扣比例'))
      return
    }
    if (startTimeS > endTimeS) {
      Toast(t('开始时间应小于结束时间'))
      return
    }
  }
  if (Number(discount) && (!startTime || !endTime)) {
    Toast(t('请正确填写活动开启时间和结束时间'))
    return
  }

  let dataJson = {
    goodsIds: props.productArry.join(','),
    ...fromData.value
  }
  if (fromData.value.percent > profitRange.max || fromData.value.percent < profitRange.min) {
    Toast(t('百分比设置范围为') + `：${profitRange.min}% ~ ${profitRange.max}%`)
  } else {
    const reg = /^\+?[1-9][0-9]*$/
    if (!reg.test(String(Number(fromData.value.percent)))) {
      Toast(t('百分比必须为正整数'))
    } else if (Number(fromData.value.discount) && !reg.test(String(Number(fromData.value.discount)))) {
      Toast(t('折扣比例必须为正整数'))
    } else {
      disable.value = true
      dataJson.startTime = dataJson.startTime + ' 00:00:00'
      dataJson.endTime = dataJson.endTime + ' 00:00:00'
      dataJson.profit = (fromData.value.percent / 100).toFixed(2);
      dataJson.discount = (fromData.value.discount / 100).toFixed(2);
      dataJson.percent = (fromData.value.percent / 100).toFixed(2);
      Toast.loading({
        forbidClick: true,
      });
      goodsaddOrUpdate(dataJson).then(() => {
        Toast(t('上架成功'));
        update()
      }).catch((err) => {
        const limitObj = (typeof err.data) === 'string' ? JSON.parse(err.data) : err.data
        if (limitObj && limitObj._$1) {
          Toast({
            message: t(err.msg, {_$1: limitObj._$1}),
            duration: 2000
          })
        } else {
          if (err.msg.indexOf('：') > -1) {
            const arr = err.msg.split('：')
            Toast({
              message: t(arr[0], {num: err.data.noLevelGoodsNum}),
              duration: 2000
            })
          } else {
            Toast({
              message: t(err.msg),
              duration: 2000
            })
          }
        }

        disable.value = false
      })
    }
  }
};

const profitRange = reactive({
  min: 5,
  max: 20
})

// 请求利润区间
sysParaProductInfo().then(res => {
  profitRange.min = Number(res.sysParaMin)
  profitRange.max = Number(res.sysParaMax)
})

const update = () => {
  close()
  emit('update')
}

const props = defineProps({
  isEdit: Boolean,
  productArry: Array
});
const close = () => {
  emit('close')
  for (const key in fromData.value) {
    fromData.value[key] = ''
  }
  setTimeout(() => {
    disable.value = false
  }, 500)
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


</script>

<style scoped lang="scss">
.editProduct {
  background: #fff;
  color: #333;

  &.is-ar {
    :deep(.van-field__error-message),
    :deep(.van-field__control) {
      text-align: right;
    }
  }

  .title {
    text-align: center;
    line-height: 55px;
    font-size: 16px;
    font-weight: bold;
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
  border-color: var(--site-main-color);
  background-color: var(--site-main-color);
}
</style>
