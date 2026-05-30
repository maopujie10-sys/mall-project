<template>
  <div>
    <area-code-dialog v-model="areaVisible" @done="doneHandle" />
    <div :class="{'active': inputActive, 'is-ar': isArLang, 'turn': isTurn}" class="input-item">
      <div v-if="areaCode" class="area-code" @click="areaVisible = true">
        <p>+{{ codeNum }}</p>
        <i class="iconfont icon-xiangxiajiantou"></i>
      </div>
      <van-field
        :type="openEye ? 'text' : type"
        :model-value="modelValue"
        :placeholder="placeholder"
        @input="inputChange"
        @focus="inputActive = true"
        @blur="inputActive = false"
      />
      <div v-if="clearShow" class="icon" @click="clearHandle">
        <i class="iconfont icon-guanbi2fill"></i>
      </div>
      <div v-if="showPassword" class="icon">
        <i v-if="openEye" class="iconfont icon-denglu-mimakejian" @click="openEye = false"></i>
        <i v-else class="iconfont icon-denglu-mimabukejian" @click="openEye = true"></i>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { arLangCheck } from '@/utils/arLangCheck'
import AreaCodeDialog from '@/components/area-code-dialog/index.vue'
const $emit = defineEmits(['update:modelValue', 'update:codeNum'])

const props = defineProps({
  modelValue: {
    type: [Number, String],
    default: ''
  },
  type: {
    type: String,
    default: 'text'
  },
  placeholder: {
    type: String,
    default: ''
  },
  clear: {
    type: Boolean,
    default: false
  },
  showPassword: {
    type: Boolean,
    default: false
  },
  areaCode: {
    type: Boolean,
    default: false
  },
  codeNum: {
    type: [Number, String],
    default: ''
  },
  isTurn: {
    type: Boolean,
    default: false
  }
})

const isArLang = arLangCheck()

const openEye = ref(false)
const inputActive = ref(false)
const areaVisible = ref(false)

const clearShow = computed(() => {
  return props.modelValue && props.clear
})

const clearHandle = () => {
  $emit('update:modelValue', '')
}

const inputChange = (e) => {
  const val = e.target.value
  $emit('update:modelValue', val)
}

const doneHandle = (data) => {
  localStorage.setItem('areaCode', data.dialCode)
  $emit('update:codeNum', data.dialCode)
}
</script>

<style lang="scss" scoped>
.input-item {
  width: 100%;
  height: 44px;
  border: 1px solid #ddd;
  border-radius: 4px;
  padding: 0 10px;
  display: flex;
  align-items: center;
  &.active {
    border-color: #fff;
  }
  &.turn {
    background-color: #FFFAFA;
    border-radius: 44px;
    border-color: #F2DB9C;
    padding: 0 20px;
    .van-cell {
      :deep(.van-field__control) {
        color: #333;
      }
      &::placeholder {
        color: #ccc;
      }
    }
    .icon {
      color: #ccc;
    }
  }
  &.is-ar {
    :deep(.van-field__control) {
      text-align: right !important;
    }
    > .area-code {
      padding-right: 0;
      padding-left: 10px;
      > p {
        margin-left: 8px;
        margin-right: 0;
      }
    }
  }
  > .area-code {
    height: 44px;
    display: flex;
    align-items: center;
    font-size: 14px;
    padding-right: 10px;
    > p {
      margin-right: 8px;
    }
    > .iconfont {
      font-size: 14px;
    }
  }
  .van-cell {
    padding: 0;
    background-color: transparent;
    border: none;
    font-size: 14px;
    line-height: 1;
    flex: 1;
    &::after {
      border: none;
    }
    :deep(.van-field__control) {
      color: #fff;
    }
    &::placeholder {
      color: rgba(255, 255, 255, .6);
    }
  }
  > .icon {
    width: 26px;
    height: 26px;
    display: flex;
    align-items: center;
    justify-content: center;
  }
}
</style>
