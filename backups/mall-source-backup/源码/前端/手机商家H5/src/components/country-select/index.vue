<template>
  <div>
    <country-dialog v-model="dialogShow" :countries="countries" @done="doneHandle"/>
    <div :class="{'empty': !countryName, 'disabled': disabled}" class="input-item" @click="dialogShow = true">{{ countryName || t('selectNation')}}</div>
  </div>
</template>

<script setup>
import { ref, defineProps, nextTick, computed, toRefs } from 'vue'
import { Toast } from 'vant'
import { useI18n } from 'vue-i18n'
import CountryDialog from './components/CountryDialog.vue'
import countriesinit from "@/views/authentication/components/countryList"

import { listCountry } from '@/service/user.api.js'

const { t } = useI18n()
const $emit = defineEmits(['update:modelValue', 'done'])

const props = defineProps({
  modelValue: {
    type: String,
    default: ''
  },
  disabled: {
    type: Boolean,
    default: false
  }
})

const { modelValue } = toRefs(props)
const countries = ref([])
const getDone = ref(false)
const dialogShow = ref(false)

const countryName = computed(() => {
  if (getDone.value) {
    const itemObj = countries.value.find(item => item.id === modelValue.value)
    if (itemObj) {
      return itemObj.countryName
    } else {
      for (const key in countriesinit) {
        if (Number(countriesinit[key].dialCode) === Number(modelValue.value)) {
          return countriesinit[key].name
        }
      }
      return ''
    }
  } else {
    return ''
  }
})

const doneHandle = (data) => {
  $emit('update:modelValue', data.id)
  $emit('done', data)
}

nextTick(async () => {
  Toast.loading({
    duration: 0,
    message: t('loading'),
    forbidClick: true
  })
  await listCountry().then(res => {
    countries.value = res.data || []
    getDone.value = true
    Toast.clear()
  }).catch(() => {
    Toast.clear()
  })
})
</script>

<style lang="scss" scoped>
.input-item {
  display: flex;
  align-items: center;
  height: 44px;
  margin-top: 9px;
  padding: 0 20px;
  align-items: center;
  border-radius: 3px;
  background-color: #fff;
  border: 1px solid #eee;
  color: #222;
  &.empty {
    color: #7b818c;
  }
  &.disabled {
    pointer-events: none;
  }
}
</style>
