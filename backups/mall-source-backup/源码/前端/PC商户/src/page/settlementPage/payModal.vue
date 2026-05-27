<template>
  <el-dialog
    class="es-dialog"
    :visible.sync="dialogVisible"
    :center="true"
    :append-to-body="true"
    width="475px"
  >
    <div slot="title" class="dialog-title">
      <span v-if="showModel === 0">{{ $t('message.home.desc3') }}</span>
      <span v-if="showModel === 1">{{ $t('message.home.setUpPayPaw') }}</span>
      <span v-if="showModel === 2">{{ $t('message.home.confirmPayPaw') }}</span>
    </div>
    <div class="pay-modal-content dialog-content">
      <h2 class="pay-modal-title" v-if="showModel !== 2">
        {{ $t('message.home.desc4') }}
      </h2>
      <h2 class="pay-modal-title" v-if="showModel === 2">
        {{ $t('message.home.desc6') }}
      </h2>
      <EsPayPassword
        ref="passwordRef"
        :type="'password'"
        :maxlength="6"
        @output="output"
      />
      <div class="pay-modal-btn">
        <el-button
          type="primary"
          :loading="payLoading"
          @click="pay"
          v-if="showModel === 0"
        >
          {{ $t('message.home.确认') }}
        </el-button>
        <el-button
          type="primary"
          :loading="payLoading"
          @click="setUpPaw"
          v-if="showModel === 1"
        >
          {{ $t('message.home.确认') }}
        </el-button>
        <div v-if="showModel === 2" class="pay-button-view">
          <el-button :loading="payLoading" @click="previous">
            {{ $t('message.home.previous') }}
          </el-button>
          <el-button
            type="primary"
            :loading="payLoading"
            @click="confirmPayPaw"
          >
            {{ $t('message.home.确认') }}
          </el-button>
        </div>
      </div>
    </div>
    <span slot="footer"></span>
  </el-dialog>
</template>

<script>
import EsPayPassword from '@/components/payPassword'
import { mapGetters, mapActions } from 'vuex'

export default {
  name: 'EsPayModal',
  components: { EsPayPassword },
  props: {
    show: {
      type: Boolean,
      default: false,
    },
    payCallback: {
      type: Function,
      default: null,
    },
    // setSafeword: {
    //     type: Function,
    //     default: null,
    // },
    payLoading: {
      type: Boolean,
      default: false,
    },
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
          this.$refs.passwordRef && this.$refs.passwordRef.clear()
        }
        this.$emit('update', newValue)
      }
      newValue && this.$nextTick(()=>this.$refs.passwordRef.focus(),200)
    },
    show(newValue, oldValue) {
      if (newValue !== oldValue) this.dialogVisible = newValue
    },
    showModel(val) {
     if( this.$refs.passwordRef)
      this.$refs.passwordRef.clear()
      this.$nextTick(()=>  this.$refs.passwordRef.focus(),200)
    },
  
  },
  computed: {
    ...mapGetters(['userInfo']),
    hasSafeWord() {
      return this.userInfo.safeword == 1
    },
  },
  mounted() {
    this.dialogVisible = this.show
  },
  methods: {
    ...mapActions(['getUserInfo']),
    ...mapActions({
        setSafewordFunc: 'order/setSafewordFunc',
    }),
    previous() {
      this.showModel = 1
      // this.$emit('changeShowModel', 1)
      this.$refs.passwordRef.clear()
    },
    setUpPaw() {
      // 设置支付密码
      // this.$emit('changeShowModel', 2)
      this.showModel = 2
      this.$refs.passwordRef.clear()
    },
    confirmPayPaw() {
      // 再次确认支付密码
      if (this.firstPaw === this.secondPaw) {
        this.setSafeword(this.firstPaw, this.secondPaw)
      }
    },
    output({ data, isfinished }) {
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
        this.payCallback(this.password, () => {
          this.password = ''
          this.$refs.passwordRef.clear()
          this.dialogVisible = false
        }, () => {
          this.password = ''
          this.$refs.passwordRef.clear()
        })
      }
      // : this.$router.push('/paySuccess')
    },
    async setSafeword(safeword, re_safeword) {
      try {
        await this.setSafewordFunc({
          safeword,
          re_safeword,
        })
        await this.getUserInfo()
        this.showModel = 0
        this.$message.success(this.$t('message.home.setSuccess'))
      } catch (error) {}
    },
  },
}
</script>

<style lang="scss">
.pay-modal-title {
  text-align: left;
  font-weight: 400;
  font-size: 16px;
  color: var(--color-black);
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

  .pay-button-view {
    display: flex;
    justify-content: space-between;
  }
}
</style>
