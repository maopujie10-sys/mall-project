<template>
  <div class="page-content">
    <van-nav-bar safe-area-inset-top
      fixed
      :title="$t('退款申请')"
      left-arrow
      @click-left="() => $router.back()"
    />
    <div style="width: 100%;" class="h46"></div>

    <div class="nr">
      <div class="biaoti">{{ $t('退款理由') }}</div>
      <div class="shuru">
        <el-select v-model="formData.returnReason" :placeholder="$t('请选择')" style="width: 100%;">
          <el-option
            v-for="item in optionsData"
            :key="item.value"
            :label="item.label"
            :value="item.value"
          />
        </el-select>
      </div>

      <div class="biaoti">{{ $t('退款金额') }}</div>
      <div class="shuru">
        <el-input
          v-model="formData.money"
          disabled
        />
      </div>

      <div class="biaoti">{{ $t('退款说明') }}</div>
      <div class="shuru">
        <el-input
          type="textarea"
          :rows="3"
          maxlength="120" show-word-limit
          :placeholder="$t('请输入')"
          v-model="formData.returnDetail"
        />
      </div>

      <div class="tijiao" @click="submitHandle">{{ $t('提交') }}</div>
    </div>
  </div>
</template>

<script>
import {NavBar, Toast} from 'vant'
import {priceFormat} from '@/utils/utis'
import {
  orderReturns
} from '@/API/user'
export default {
  name: 'OrderRefund',
  components: {
    [NavBar.name]:NavBar,
    [Toast.name]:Toast
  },
  data() {
    return {
      optionsData: [
        {
          value: '1',
          label: this.$t('未收到货')
        },
        {
          value: '2',
          label: this.$t('不喜欢，不想要')
        },
        {
          value: '3',
          label: this.$t('卖家发错货')
        },
        {
          value: '4',
          label: this.$t('假冒品牌')
        },
        {
          value: '5',
          label: this.$t('少发、漏发')
        },
        {
          value: '6',
          label: this.$t('收到商品破损')
        },
        {
          value: '7',
          label: this.$t('存在质量问题')
        },
        {
          value: '8',
          label: this.$t('与商家协商一致退款')
        },
        {
          value: '9',
          label: this.$t('其他原因')
        }
      ],
      orderId: null,
      priceFormat,
      formData: {
        returnReason: '',
        money: 0,
        returnDetail: ''
      }
    }
  },
  mounted() {
    this.$nextTick(() => {
      const { id, a } = this.$route.query
      if (id && (a || a === 0)) {
        this.orderId = id
        this.formData.money = this.priceFormat(a)
      } else {
        Toast(this.$t('订单号不存在'))
        setTimeout(() => {
          this.$router.back()
        }, 1500);
      }
    })
  },
  methods: {
    submitHandle() {
      if (this.formData.returnReason === ''){
        Toast(this.$t('请选择') + this.$t('退款理由'));
        return false
      }
    //   if (this.formData.returnDetail === ''){
    //     Toast(this.$t('请输入') + this.$t('退款说明'));
    //     return false
    //   }
      
      Toast.loading({
        duration: 0,
        message: this.$t('提交中'),
        forbidClick: true
      })

      const params = {
        orderId: this.orderId,
        ...this.formData
      }

      orderReturns(params).then(() => {
        Toast(this.$t('提交成功'))
        setTimeout(() => {
          this.$router.back()
        }, 1500);
      }).catch(() => {
        Toast.clear()
      })
    }
  }
}
</script>

<style lang="scss" scoped>
.el-select-dropdown__item.selected {
  color: var(--main-color) !important;
}
.page-content {
  * {
    box-sizing: border-box;
  }
  /deep/ .el-input {
    input:focus {
      border-color: var(--main-color) !important;
    }
  }

  /deep/ .el-textarea {
    textarea:focus {
      border-color: var(--main-color) !important;
    }
  }

  .nr {
    width: 100%;
    padding: 0 15px;
    box-sizing: border-box;

    /deep/ .el-select .el-input.is-focus .el-input__inner {
      border-color: var(--main-color) !important;
    }
    .biaoti{
      margin-top: 20px;
      font-style: normal;
      font-weight: 400;
      font-size: 12px;
      line-height: 16px;
      color: #333333;
    }

    .shuru{
      width: 100%;
      margin-top: 5px;
    }

    .tijiao{
      margin-top: 40px;
      width: 100%;
      height: 44px;
      background: var(--main-color);
      border-radius: 4px;
      font-style: normal;
      font-weight: 400;
      font-size: 16px;
      line-height: 44px;
      /* identical to box height, or 100% */

      text-align: center;

      color: #FFFFFF;
    }
  }
}
</style>
