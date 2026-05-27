<template>
  <div class="code-box">
    <input ref="codeinput" v-model="inputdata" :maxlength="maxlength" class="code-input" pattern="[0-9]*" type="tel"
           @blur="inputBlur()" @keyup.enter="inputBlur()"/>
    <div v-if="type === 'password'" class="code-all" @click="focus">
      <div v-for="(item, index) in codeData" :key="index" :class="{
                                      'code-active': index === 0 || inputdata.length - 1 >= index,
                                      'code-password': inputdata.length - 1 >= index,
                                    }" :style="[styles]" class="code-item"></div>
    </div>
    <div v-else class="code-all" @click="focus">
      <div v-for="(item, index) in codeData" :key="index"
           :class="{ 'code-active': index === 0 || inputdata.length - 1 >= index }" :style="[styles]" class="code-item">
        {{ item }}
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'EsPayPassword',
  props: {
    type: {
      type: String,
      required: false,
      default: 'number',
    },
    maxlength: {
      type: Number,
      required: false,
      default: 6,
    },
    styles: {
      type: Object,
      required: false,
      default: () => {
        return {}
      },
    },
  },
  data() {
    return {
      inputdata: '',
      codeData: [],
    }
  },
  watch: {
    inputdata(newVal, oldVal) {
      if (/[^\d]/g.test(newVal)) {
        this.inputdata = this.inputdata.replace(/[^\d]/g, '')
      } else if (newVal.length < oldVal.length) {
        // 清空输入值
        if (newVal === '') {
          this.$data.codeData = ['', '', '', '', '', '']
        } else {
          // 依次删除按键
          this.$data.codeData[oldVal.length - 1] = ''
        }
      } else if (newVal.length - 1 === oldVal.length) {
        // 依次输入
        this.$data.codeData[newVal.length - 1] = newVal[newVal.length - 1]
      } else {
        // 验证码自动填充
        newVal.split('').map((item, index) => {
          this.$data.codeData[index] = item
        })
      }
    },
  },
  computed: {},
  mounted() {
    this.$nextTick(() => {
      setTimeout(() => {
        this.$refs.codeinput.focus()
      }, 300)
    })
    for (let i = 0, j = this.maxlength; i < j; i++) {
      this.codeData.push('')
    }
  },
  methods: {
    clear() {
      this.codeData = []
      this.inputdata = ''
      for (let i = 0, j = this.maxlength; i < j; i++) {
        this.codeData.push('')
      }
      this.$refs.codeinput.focus()
    },
    focus() {
      this.$refs.codeinput.focus()
    },
    inputBlur() {
      this.$emit('output', {
        data: this.$data.inputdata,
        isfinished: !this.$data.codeData.includes(''),
      })
    },
  },
}
</script>

<style lang="scss">
.code-box {
  width: 100%;
  position: relative;
  overflow-x: hidden;

  & > .code-input {
    position: absolute;
    width: 100%;
    left: 0;
    z-index: 0;
    opacity: 0;
    caret-color: transparent;
  }

  & > .code-all {
    padding-top: 12px;
    display: flex;
    align-content: space-between;
    justify-content: space-between;

    &.disabled {
      &::after {
        display: block;
        content: ' ';
        width: 100%;
        height: 100%;
        position: absolute;
        left: 0;
        right: 0;
        z-index: 9;
      }
    }

    & > .code-item {
      // flex: 1;
      width: 40px;
      height: 40px;
      flex-shrink: 0;
      border-radius: 10px;
      font-size: 24px;
      line-height: 40px;
      text-align: center;
      background: transparent;
      border: 1px solid #cccccc;
      outline: none;
    }

    & > .code-active {
      border: 1px solid #1552f0;

    }

    .code-item.code-password {
      position: relative;
    }

    .code-item.code-password::after {
      position: absolute;
      content: '';
      top: 50%;
      left: 50%;
      transform: translate(-50%, -50%);
      width: 12px;
      height: 12px;
      background: #000000;
      border-radius: 50%;
      border: solid 1px #cccccc;
    }
  }
}
</style>
