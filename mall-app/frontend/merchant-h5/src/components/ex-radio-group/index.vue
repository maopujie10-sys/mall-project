<template>
  <div :class="{'disabled': disabled}" class="my-radio-group">
    <span class="label textColor">{{ label }}</span>
    <div class="container" :class="{'is-ar': isArLang}">
      <div
        v-for="item in list"
        :key="item.value"
        :class="{ active: item.value === modelValue, item: true }"
        @click.stop.prevent="handleRadioGroup(item.value)"
      >
        {{ item.label }}
        <i class="iconfont icon-duigoux"></i>
      </div>
    </div>
  </div>
</template>

<script setup>
import { arLangCheck } from '@/utils/arLangCheck'
const $emit = defineEmits(['selectRadio', 'update:modelValue'])

const isArLang = arLangCheck()

const selectRadio = () => {
  console.log(1)
  $emit('selectRadio', true)
}


const props = defineProps({
  label: {
    type: String,
    default: ''
  },

  /**
   * [{ label: '', value: 1 }]
   */
  list: {
    type: Array,
    default: []
  },

  modelValue: {
    type: [Number, String],
    default: '1'
  },

  disabled: {
    type: Boolean,
    default: false
  }
})


const handleRadioGroup = (val) => {
  $emit('update:modelValue', val)
}
</script>

<style lang="scss" scoped>
.my-radio-group {
  &.disabled {
    pointer-events: none;
  }

  .label {
    font-size: 12px;
  }

  .container {
    padding-top: 10px;
    padding-bottom: 22px;
    display: flex;
    flex-wrap: wrap;
    &.is-ar {
      .item {
        margin: 0 !important;
        margin-right: 15px !important;
        &:first-child {
          margin-right: 0 !important;
        }
      }
    }

    .item {
      position: relative;
      width: 105px;
      height: 44px;
      border: 1px solid #ddd;
      border-radius: 4px;
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 14px;
      color: $text-color-light;
      overflow: hidden;
      &::after {
        content: '';
        position: absolute;
        width: 40px;
        height: 40px;
        bottom: -22px;
        right: -22px;
        background-color: var(--site-main-color);
        transform: rotate(45deg);
        z-index: 1;
        opacity: 0;
      }
      > .iconfont {
        position: absolute;
        color: #fff;
        right: 0;
        bottom: -5px;
        z-index: 2;
        font-size: 12px;
        opacity: 0;
      }

      &:not(:last-child) {
        margin-right: 15px;
      }

      &.active {
        border-color: var(--site-main-color);
        color: var(--site-main-color);
        > .iconfont,
        &::after {
          opacity: 1;
        }
      }
    }
  }
}
</style>
