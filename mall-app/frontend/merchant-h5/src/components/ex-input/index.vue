<template>
  <div class="inputCom" :class="{'is-ar': isArLang}">
    <!-- <span class="label textColor">{{ label }}</span> -->
    <div :class="{'form-item-title': required, 'is-ar': isArLang}" class="label textColor">{{ label }}</div>
    <form class="iptbox inputBackground input-style">
      <div class="areaCode" v-if="area" @click="selectArea">
        <span class="icon iti-flag" :class="icon"></span>
        <span class="textColor">+{{ dialCode }}</span>
        <img src="../../assets/image/login/more.png" alt="" />
      </div>
      <!-- <p>{{ passwordType }} {{ props.value }}</p> -->
      <input
        autocomplete="off"
        name="username"
        class="inputBackground input-style"
        v-if="typeText == 'password'"
        :type="passwordType"
        :maxlength="maxLength"
        :placeholder="placeholderText"
        :value="modelValue"
        @input="onInput"
        :disabled="disabled"
        :readonly="readonly"
      />
      <van-field
        v-else-if="typeText === 'number'"
        type="number"
        :placeholder="placeholderText"
        :maxlength="maxLength"
        :model-value="modelValue"
        :readonly="readonly"
        :disabled="disabled"
        @input="onInput"
      />
      <input
        autocomplete="off"
        class="inputBackground input-style"
        v-else
        :type="typeText"
        :disabled="disabled"
        :placeholder="placeholderText"
        :maxlength="maxLength"
        :value="modelValue"
        :readonly="readonly"
        @input="onInput"
      />
      <div class="rightCon">
        <div class="closeBox" v-if="clearBtn && modelValue" @click="clear">
          <img src="../../assets/image/login/clear.png" alt="" />
        </div>
        <div class="eyeBox" v-if="typeText == 'password'" @click="changeType">
          <img
            v-if="passwordType == 'password'"
            src="../../assets/image/login/_close.png"
            alt=""
          />
          <img v-else src="../../assets/image/login/open.png" alt="" />
        </div>
        <slot name="rightBtn"></slot>
      </div>
    </form>
    <div v-if="tips" class="tips">{{ tips }}</div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { arLangCheck } from '@/utils/arLangCheck'
const passwordType = ref('password')
const $emit = defineEmits(['selectArea', 'update:modelValue'])

const props = defineProps({
  label: {
    type: String,
    default: ''
  },
  placeholderText: {
    type: String,
    default: ''
  },
  typeText: {
    type: String,
    default: 'text'
  },
  clearBtn: {
    type: Boolean,
    default: true
  },
  area: {
    type: Boolean,
    default: false
  },
  readonly: {
    type: Boolean,
    default: false
  },
  // value: {
  //     type: [Number, String],
  //     default: '1',
  // },
  modelValue: {
    type: [Number, String],
    default: '1'
  },
  tips: {
    type: String,
    default: ''
  },
  dialCode: {
    type: Number,
    default: 0
  },
  icon: {
    type: String,
    default: ''
  },
  disabled: {
    type: Boolean,
    default: false
  },
  // 考虑去除输入框前后空格
  trim: {
    type: Boolean,
    default: true
  },
  // 输入框最大最大支持字符数
  maxLength: {
    type: Number,
    default: 50
  },
  required: {
    type: Boolean,
    default: false
  }
})

const isArLang = arLangCheck()

const selectArea = () => {
  console.log(1)
  $emit('selectArea', true)
}

const clear = () => {
  $emit('update:modelValue', '')
}

const onInput = (e) => {
  let val = e.target.value
  if (props.trim) {
    val = String(val).trim()
  }
  $emit('update:modelValue', val)
}

const changeType = () => {
  if (passwordType.value == 'password') {
    passwordType.value = 'text'
  } else {
    passwordType.value = 'password'
  }
}
</script>

<style lang="scss" scoped>
@import '@/views/authentication/components/intl.css';
.input-style {
  background-color: #fff;
  border: 1px solid #ddd;
}

.inputCom {
  color: #333;
  padding-bottom: 22px;
  &.is-ar {
    :deep(.van-field__control) {
      text-align: right;
    }
    .areaCode,
    input {
      padding-left: 0 !important;
      padding-right: 10px !important;
    }
  }

  .iptbox {
    height: 44px;
    margin-top: 9px;
    padding: 0 11px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    border-radius: 3px;

    :deep(.van-cell) {
      padding: 0;
      height: 100%;
      background: transparent;

      &::after {
        border: none;
      }

      .van-field__body,
      .van-field__control {
        height: 100%;
        font-size: 16px;
      }

      input::-webkit-input-placeholder {
        color: #868c9a;
      }
    }
  }

  .areaCode {
    width: 70px;
    display: flex;
    align-items: center;
    padding-left: 10px;
    justify-content: space-between;
    height: 100%;

    img {
      width: 10px;
    }
  }

  input {
    flex: 1;
    height: 100%;
    border: none;
    padding-left: 10px;
    color: #222;
  }

  .rightCon {
    display: flex;
    align-items: center;
  }

  .closeBox,
  .eyeBox {
    width: 17px;
    height: 17px;

    img {
      width: 100%;
      height: 100%;
    }
  }

  .eyeBox {
    margin-left: 14px;
  }
}

.tips {
  font-size: 13px;
  color: #868d9a;
  margin-top: 9px;
}

input:-webkit-autofill {
  -webkit-box-shadow: 0 0 0 200px #f5f5f5 inset;
}

input::-webkit-input-placeholder {
  color: #868c9a;
}

.icon {
  transform: scale(1.3);
  display: inline-block;
}

.form-item-title {
  position: relative;
  padding-left: 10px;
  &.is-ar {
    padding-left: 0;
    padding-right: 10px;
    &::after {
      left: calc(100% - 4px);
    }
  }
  &::after {
    content: '*';
    display: block;
    position: absolute;
    top: 50%;
    transform: translateY(-50%);
    color: red;
    left: 0;
  }
}
</style>
