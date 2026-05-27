<template>
  <div class="ex-password-input" ref="passwordInputRef">
    <input
      ref="realInput"
      type="number"
      inputmode="numeric"
      class="hidden-input"
      @input="onInput"
      @blur="blur">
    <ul
      class="ex-password-input-security"
      :class="{
        'has-gap': hasGap
      }"
      @click="focus">
      <li
        class="ex-password-input-item"
        :class="{
          'is-focus': focusInputIndex === index
        }"
        v-for="(pwd, index) in passwords"
        :key="index">
        <i v-if="mask && (pwd !== ' ')" class="password-input-dot"></i>
        <template v-if="!mask">{{ pwd }}</template>
        <div
          v-if="showInputCursor"
          class="ex-password-input-cursor"></div>
      </li>
    </ul>
    <div class="ex-password-input-info" v-if="info">{{ info }}</div>
  </div>
</template>

<script>
import {
  ref,
  computed,
  onMounted,
  onUnmounted,
  nextTick
} from 'vue';

const trim = function (str) {
  if (typeof str !== 'string' || str.length === 0) {
    return str;
  }
  str += '';
  // 清除字符串两端空格，包含换行符、制表符
  return str.replace(/(^[\s\n\t]+|[\s\n\t]+$)/g, '');
}

export default {
  name: "PasswordInput",
  props: {
    modelValue: { // 密码值
      type: [String, Number],
      default: ''
    },
    hasGap: { // 是否有间隙
      type: Boolean,
      default: false
    },
    mask: { // 是否隐藏密码内容
      type: Boolean,
      default: true
    },
    length: { // 密码最大长度
      type: Number,
      default: 6
    },
    info: { // 输入框下方文字提示
      type: String,
      default: ''
    }
  },
  setup (props, ctx) {
    let passwordInputRef = ref(null);
    let realInput = ref(null);

    let passwords = computed(function () {
      let value = props.modelValue;
      if (typeof value !== 'string' && typeof value !== 'number') {
        value = '';
      } else {
        value = value + '';
      }

      // console.log('value', value);
      let resultArr = value.split('');
      let len = props.length;
      let diff = value.length - props.length;
      if (diff > 0) {
        resultArr = value.substr(0, len).split('');
      } else if (diff < 0) {
        diff = Math.abs(diff);
        while (diff > 0) {
          resultArr.push(' ');
          diff--;
        }
      }

      return resultArr;
    });

    // 计算获得焦点的虚拟输入框的索引
    let calcFocusInputIndex = function () {
      let pwdVal = passwords.value;
      let index = -1;
      let realPwdVal = trim(pwdVal.join(''));
      console.log('realPwdVal', realPwdVal, realPwdVal.length, pwdVal);
      for (let i = 0, len = pwdVal.length; i < len; i++) {
        if (pwdVal[i] === ' ' && realPwdVal.length !== props.length) {
          index = i;
          break;
        }
      }
      console.log('index', index);
      return index;
    };

    let nativeInputFocus = ref(false);
    let showInputCursor = ref(false);
    let focusInputIndex = ref(null);
    let focus = function () {
      let index = calcFocusInputIndex();
      if (index > -1) {
        realInput.value.focus();
        nativeInputFocus.value = true;
        showInputCursor.value = true;
        focusInputIndex.value = index;
      } else {
        realInput.value.focus();
        nativeInputFocus.value = true;
      }
    };
    let blur = function () {
      showInputCursor.value = false;
      focusInputIndex.value = null;
      realInput.value.blur();
      realInput.value.value = '';
      nativeInputFocus.value = false;
    };

    let numberReg = /^\d+$/;
    let onInput = function (evt) {
      let inputValue = evt.target.value;
      if (inputValue && !numberReg.test(inputValue)) { // 如果输入的不是数字则清空输入框
        evt.target.value = '';
        return;
      }
      console.log('输入的字符为：', inputValue);
      let password = passwords.value.join('');
      password = trim(password);
      password += inputValue;
      evt.target.value = '';
      ctx.emit('update:modelValue', password);
      if (password.length == props.length) {
        ctx.emit('complete', password);
      }
      // 隐藏输入框焦点
      nextTick(function () {
        let inputIndex = calcFocusInputIndex();
        if (inputIndex == -1) {
          blur();
        } else {
          focusInputIndex.value = inputIndex;
        }
      });
      console.log('更新modelValue', password);
    };

    let keydownEvent = function (evt) {
      let keyCode = evt.keyCode;
      console.log('keyCode', keyCode);
      if (!nativeInputFocus.value) {
        console.log('原生输入框未获得焦点');
        return;
      }
      if (keyCode == 8) { // 删除键
        let password = passwords.value.join('');
        password = trim(password);
        if (password.length == 0) {
          return;
        }
        password = password.substr(0, password.length - 1);
        console.log('new password', password);
        ctx.emit('update:modelValue', password);
        // 隐藏输入框焦点
        nextTick(function () {
          let inputIndex = calcFocusInputIndex();
          if (inputIndex == -1) {
            blur();
          } else {
            focusInputIndex.value = inputIndex;
            focus();
          }
        });
      }
    };

    onMounted(function () {
      document.addEventListener('keydown', keydownEvent, false);
    });

    onUnmounted(function () {
      document.removeEventListener('keydown', keydownEvent, false);
    });

    return {
      realInput,
      passwordInputRef,
      passwords,
      showInputCursor,
      focusInputIndex,
      blur,
      focus,
      onInput
    };
  }
};
</script>

<style lang="scss">
.ex-password-input{
  position: relative;
  overflow: hidden;
  .hidden-input{
    position: absolute;
    top: 5px;
    z-index: 1;
    /* 隐藏光标 start */
    color: transparent;
    text-shadow: 0 0 0 $text-color-dark;
    /* 隐藏光标 end */

    /* 隐藏ios设备光标 start */
    text-indent: -999em;
    margin-left: -40%;
    /* 隐藏ios设备光标 end */
  }
}
.ex-password-input-security{
  position: relative;
  z-index: 5;
  display: flex;
  height: 40px;
  user-select: none;
  background-color: $background-color;
}
.ex-password-input-item{
  position: relative;
  z-index: 5;
  display: flex;
  flex: 1;
  justify-content: center;
  align-items: center;
  height: 100%;
  cursor: pointer;
  font-size: 20px;
  border: 1px solid $border-color;

  &:not(:first-child)::before{
    position: absolute;
    top: 0;
    left: 0;
    bottom: 0;
    content: ' ';
    width: 1px;
  }

  &.is-focus{
    border-color: $primary-color;

    .password-input-dot{
      visibility: hidden;
    }
    .ex-password-input-cursor{
      display: block;
    }
  }
}
.password-input-dot{
  width: 12px;
  height: 12px;
  border-radius: 50%;
  background-color: $text-color-dark;
}
.ex-password-input-cursor{
  display: none;
  position: absolute;
  top: 50%;
  left: 50%;
  width: 1px;/*no*/
  height: 40%;
  transform: translate(-50%, -50%);
  cursor: pointer;
  background-color: rgba(32,32,32,3);
  animation: 1s cursor-flicker infinite;
}

.ex-password-input-security{
  &.has-gap{
    .ex-password-input-item{
      border-radius: 4px;
      &::before{
        display: none;
      }
      &:not(:first-child){
        margin-left: 15px;
      }
    }
  }
}
.ex-password-input-info {
  margin-top: 15px;
  color: #999;
  text-align: center;
}


@keyframes cursor-flicker {
  0% {
    opacity: 0;
  }
  50% {
    opacity: 1;
  }
  100% {
    opacity: 0;
  }
}
</style>