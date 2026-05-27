<template>
  <div class="select-list-wrapper">
    <div
        class="select-list-item van-hairline--top color-333"
        v-for="(item, index) in list"
        :key="index"
        @click="handleClick(item.name)"
    >
      {{ t(item.name) }}
      <van-icon v-show="modelValue === item.name" name="success" class="icon" />
    </div>
  </div>
</template>

<script setup>
import { defineProps, defineEmits } from "vue";
import { useI18n } from 'vue-i18n'
const { t } = useI18n()

const $emit = defineEmits(['update:modelValue'])
defineProps({
  modelValue: {
    type: [Number, String],
    default: ''
  },
  list: {
    type: Array,
    default: () => []
  }
})

const handleClick = val => {
  $emit('update:modelValue', val)
}
</script>

<style lang="scss" scoped>
.select-list-wrapper {
  max-height: 70vh;
  overflow-y: scroll;
}
.select-list-item {
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
  height: 50px;
  font-size: 14px;
  box-sizing: border-box;

  .icon {
    position: absolute;
    top: 50%;
    right: 19px;
    transform: translateY(-50%);
    color: var(--site-main-color);
  }
}

</style>