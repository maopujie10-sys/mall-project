<template>
  <el-dialog :append-to-body="true" :center="true" :visible.sync="dialogVisible" class="so-dialog" width="360px">
    <div slot="title" class="dialog-title">
      <span v-if="showModel === 0">{{ $t('输入支付密码') }}</span>
      <span v-if="showModel === 1">{{ $t('设置支付密码') }}</span>
      <span v-if="showModel === 2">{{ $t('确认') }}</span>
    </div>
    <div class="pay-modal-content dialog-content">
      <h2 v-if="showModel !== 2" class="pay-modal-title">{{ $t('输入您的支付密码') }}</h2>
      <h2 v-if="showModel === 2" class="pay-modal-title">{{ $t('输入您的支付密码') }}</h2>
      <PayPassword ref="passwordRef" :maxlength="6" :type="'password'" @output="output"/>
    </div>
    <span slot="footer">
        <div class="pay-modal-btn">
          <el-button v-if="showModel === 0" :loading="payLoading" class="so-dialog-button-item"
                     type="primary"
                     @click="pay">{{ $t('确认') }}</el-button>
          <el-button v-if="showModel === 1" :loading="payLoading" class="so-dialog-button-item"
                     type="primary"
                     @click="setUpPaw">{{ $t('确认') }}
          </el-button>
          <div v-if="showModel === 2" class="pay-button-view">
            <el-button :loading="payLoading" class="so-dialog-button-item" @click="previous">{{
                $t('上一步')
              }}</el-button>
            <el-button :loading="payLoading" class="so-dialog-button-item" type="primary"
                       @click="confirmPayPaw">{{ $t('确认') }}</el-button>
          </div>
        </div>
    </span>
  </el-dialog>
</template>

<script>
import PayPassword from '@/components/payModal/payPassword'
import {mapActions, mapGetters} from 'vuex'
import {Notification} from "element-ui";

export default {
  name: 'EsPayModal',
  components: {PayPassword},
  props: {
    show: {
      type: Boolean,
      default: false,
    },
    payCallback: {
      type: Function,
      default: null,
    },
    onlySetting: {
      type: Boolean,
      default: false,
    },
    // setSafeword: {
    //     type: Function,
    //     default: null,
    // },
  },
  model: {
    prop: 'show',
    event: 'update',
  },
  data() {
    return {
      dialogVisible: false,
      password: '',
      // 0 支付界面 1 设置支付密码 2 确认支付密码
      showModel: 0,
      payLoading: false,
    }
  },
  watch: {
    dialogVisible(newValue, oldValue) {
      if (newValue !== oldValue) {
        if (newValue) {
          if (!!this.hasSafeWord) {
            this.showModel = 0
          } else {
            this.showModel = 1
          }
          this.password = ''
          this.payLoading = false
          this.$refs.passwordRef && this.$refs.passwordRef.clear()
        }
        this.$emit('update', newValue)
      }
      setTimeout(() => {
        this.$refs.passwordRef.focus()
      }, 300)
    },
    show(newValue, oldValue) {
      if (newValue !== oldValue) this.dialogVisible = newValue
    },
    showModel() {
      this.payLoading = false
      this.$refs.passwordRef && this.$refs.passwordRef.clear() && this.$refs.passwordRef.focus()
    },
  },
  computed: {
    ...mapGetters(['userInfo']),
    hasSafeWord() {
      return this.userInfo.safeword === 1
    },
  },
  mounted() {
    this.dialogVisible = this.show
    this.payLoading = false
  },
  methods: {
    ...mapActions('user', ['getInfo']),
    ...mapActions('settings', ['settingSafeword']),
    previous() {
      this.showModel = 1
    },
    setUpPaw() {
      // 设置支付密码
      this.showModel = 2
    },
    confirmPayPaw() {
      // 再次确认支付密码
      if (this.firstPaw === this.secondPaw) {
        this.settingSafewordFunc(this.firstPaw, this.secondPaw)
      } else {
        Notification.error({
          title: this.$t('提示'),
          message: this.$t('两次密码输入不一致'),
        })
      }
    },
    output({data, isfinished}) {
      if (isfinished) {
        if (this.showModel === 1) {
          this.firstPaw = data
        } else if (this.showModel === 2) {
          this.secondPaw = data
        } else if (this.showModel === 0) {
          this.password = data
        }
      }
    },
    pay() {
      //   this.payCallback && this.payCallback(this.password)
      if (this.payCallback) {
        this.payLoading = true
        this.payCallback(this.password, () => {
          this.password = ''
          this.payLoading = false
          this.$refs.passwordRef.clear()
          this.dialogVisible = false
        }, () => {
          this.password = ''
          this.payLoading = false
          this.$refs.passwordRef.clear()
        })
      }
      // : this.$router.push('/paySuccess')
    },
    async settingSafewordFunc(safeword, re_safeword) {
      try {
        await this.settingSafeword({
          safeword,
          re_safeword,
          verifcode_type: 2
        })
        await this.getInfo()
        this.$notify({
          title: this.$t('成功'),
          message: this.$t('设置成功'),
          type: 'success',
        })
        if (this.onlySetting) {
          this.dialogVisible = false
          return
        }
        this.showModel = 0
      } catch (error) {
      }
    },
  },
}
</script>

<style lang="scss">
.so-dialog {
  ::v-deep {
    .el-dialog {
      border-radius: 6px;
    }

    .el-dialog--center .el-dialog__body {
      padding: 0;
    }


  }

  .pay-modal-btn {
    display: flex;
    justify-content: space-between;
  }

  .so-dialog-button-item {
    width: 100%;
    height: 44px !important;
    flex: 1;
  }

  .pay-modal-title {
    text-align: left;
    font-weight: 400;
    font-size: 16px;
    line-height: 16px;
    color: #000000;
  }

  .pay-button-view {
    display: flex;
    justify-content: space-between;
    width: 100%;
  }

  .pay-modal-content {
    align-items: flex-start !important;

    .el-button {
      width: 100%;
      max-width: 450px;
      height: 50px;
    }

    .pay-modal-btn {
      width: 100%;
      text-align: center;
    }

  }
}
</style>
