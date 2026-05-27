<template>
  <div>
    <el-input :type="showPassword ? 'text' : 'password'" :value="value" v-bind="$attrs" ref="password"
              v-on="$listeners">
      <template slot="suffix">
        <div class="suffix">
          <i class="el-icon-circle-close" v-show="value" @click="clearInput"/>
          <div class="eye-icon" @click="changeConfirmPassword">
            <img :src="showPassword ? eyeIcon.open : eyeIcon.close" alt=""/>
          </div>
        </div>
      </template>
    </el-input>
  </div>
</template>

<script>
export default {
  name: "index",
  data() {
    return {
      showPassword: false,
      eyeIcon: {
        close: require('@/assets/images/eye-close.png'),
        open: require('@/assets/images/eye-open.png'),
      },
      showClose: false
    }
  },
  props: {
    value: {
      type: [String, Number],
      default: ""
    },
    type: {
      type: String,
      default: "text"
    },
  },
  watch: {
    value(val) {
      this.$emit('input', val)
    }
  },
  methods: {
    focus() {
      setTimeout(() => {
        this.$refs.password.focus()
      }, 300)
    },
    clearInput() {
      this.$emit('clear', '')
    },
    changeConfirmPassword() {
      this.showPassword = !this.showPassword
      this.$forceUpdate()
    }
  }
}
</script>

<style lang="scss" scoped>
.suffix {
  display: flex;
  justify-content: flex-end;
  align-items: center;
  height: 100%;
}

.eye-icon {
  width: 20px;
  height: 100%;
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 10px;
  box-sizing: border-box;
}

.el-icon-circle-close {
  font-size: 14px;
  margin-right: 6px;
  cursor: pointer;

  &:hover {
    opacity: 0.8;
  }
}

.eye-icon img {
  display: block;
  width: 16px;
}


</style>
