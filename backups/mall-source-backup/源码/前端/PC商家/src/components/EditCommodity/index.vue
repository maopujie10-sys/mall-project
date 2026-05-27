<template>
  <el-dialog :title="$t(type)" :visible.sync="editVisible" width="500px" :close-on-click-modal="false">
    <div class="edit-commodity">
      <el-form ref="form" :model="updateInfo" :rules="rules">
        <el-form-item :label="$t('参考售价')" prop="sellingPrice" v-show="type===$t('编辑产品')">
          <el-input
              :placeholder="$t('填写售价')"
              v-model="updateInfo.sellingPrice"
              @input="changeSellingPrice">
          </el-input>
          <span style="color: #CCCCCC;font-size: 12px;">{{ $t("最终售价以利润比例换算为准") }}</span>
          <span style="" class="discountPrice">
            <!--              售价*（1-折扣比例）-成本价= x-->
              {{ $t('利润') }}：
            <FormatNumberShow
                :data="updateInfo.discountPrice ? (updateInfo.discountPrice - updateInfo.systemPrice) : updateInfo.profit"
                :currency="true"/>
          </span>
        </el-form-item>
        <el-form-item :label="$t('利润比例')" prop="profitRatio">
          <el-input

              v-model="updateInfo.profitRatio" :placeholder="$t('请输入利润比例')"
              @input="changeProfitRatio">
            <template slot="append">%</template>
          </el-input>
          <p class="lh">
              <span style="line-height: 14px;font-size: 14px;">
                {{ $t('将选中的商品发布到你的店铺，并填写利润比例。') }}
              </span>
          </p>
          <p class="lh">
            <span style="line-height: 14px;font-size: 14px;">{{ $t("建议利润比例：") }}</span>
            <span style="line-height: 14px;font-size: 12px;color: #F56C6C">
              {{ sysParaProductInfo.sysParaMin }}% — {{ sysParaProductInfo.sysParaMax }}%
            </span>
          </p>
        </el-form-item>
        <el-form-item :label="$t('折扣日期')">
          <el-date-picker
              style="width: 100%"
              v-model="discountTime"
              type="daterange"
              :picker-options="pickerOptions"
              :range-separator="$t('至')"
              :start-placeholder="$t('开始日期')"
              :end-placeholder="$t('结束日期')">
          </el-date-picker>
        </el-form-item>
        <el-form-item :label="$t('折扣比例')" prop="discountRatio">
          <el-input
              v-model="updateInfo.discountRatio" :placeholder="$t('填写折扣比例')"
              :disabled="disabledDiscountPrice"
              @input="changeDiscountRatio">
            <template slot="append">%</template>
          </el-input>
          <span class="discountPrice"
                v-if="updateInfo&&updateInfo.discountPrice">{{ $t('当前折扣价：') }} {{
              updateInfo.discountPrice
            }}</span>
        </el-form-item>
      </el-form>
    </div>
    <div slot="footer" class="dialog-footer">
      <el-button type="primary" @click="submitCommodity(updateInfo)">{{
          $t('确定')
        }}
      </el-button>
      <el-button @click="editVisible = false">{{ $t('取消') }}</el-button>
    </div>
  </el-dialog>
</template>

<script>
import {getSysParaProduct} from "@/api/user";
import moment from "moment";
import FormatNumberShow from "@/components/FormatNumberShow/index.vue";

export default {
  name: "index",
  components: {FormatNumberShow},
  data() {
    return {
      model: '',
      type: '编辑产品',
      discountTime: null,
      editVisible: false,
      updateInfo: {},
      sysParaProductInfo: {},
      rules: {
        sellingPrice: [
          {required: true, message: this.$t('请输入售价'),},
        ],
        profitRatio: [
          {required: true, message: this.$t('请输入利润比例'),},
          {
            message: this.$t('请输入正确的利润比例'),
            trigger: ['blur', 'change']
          },
          {
            validator: (rule, value, callback) => {
              if (value * 1 < this.sysParaProductInfo.sysParaMin * 1 || value * 1 > this.sysParaProductInfo.sysParaMax * 1) {
                callback(new Error(this.$t('利润比例不能小于') + this.sysParaProductInfo.sysParaMin + this.$t('，且不能大于') + this.sysParaProductInfo.sysParaMax))
              } else {
                callback()
              }
            },
            trigger: ['blur', 'change']
          }
        ],
        discountRatio: [
          {required: false, message: this.$t('请输入折扣比例'),},
          {
            pattern: /^([1-9][\d]{0,7}|0)(\.[\d]{1,2})?$/,
            message: this.$t('请输入正确的折扣比例'),
            trigger: ['blur', 'change']
          }
        ],
      },
      pickerOptions: {
        disabledDate: time => {
          return time.getTime() < Date.now() - 8.64e7
        },
        selectableRange: new Date().getHours() + ':' + (new Date().getMinutes() + 1) + ':00' + ' - 23:59:59'
      }
    }
  },
  computed: {
    disabledDiscountPrice() {
      return !this.discountTime
    },
  },
  watch: {
    'updateInfo.sellingPrice'(val) {
      if (val && this.updateInfo.discountRatio) {
        this.updateInfo.discountPrice = (this.$bigDecimal.multiply(val, (1 - (this.updateInfo.discountRatio || 0) / 100)) * 1).toFloor(2)
      } else {
        this.updateInfo.discountPrice = 0
      }
    },
    discountTime(val) {
      if (val && val.length > 0) {
        this.updateInfo.discountStartTime = moment(val[0]).format('YYYY-MM-DD HH:mm:ss')
        //结束时间改成23:59:59
        this.updateInfo.discountEndTime = moment(val[1]).format('YYYY-MM-DD') + ' 23:59:59'
        this.rules.discountRatio[0].required = true
      } else {
        this.updateInfo.discountStartTime = null
        this.updateInfo.discountEndTime = null
        this.updateInfo.discountRatio = null
        this.updateInfo.discountPrice = null
        this.rules.discountRatio[0].required = false
      }
    }
  },
  mounted() {
    //初始化表单校验
    setTimeout(() => {
      this.$refs["form"] && this.$refs["form"].clearValidate()
    }, 1000)
  },
  methods: {
    reset() {
      this.discountTime = null
      let obj = this.$refs["form"];
      obj && obj.resetFields();
    },
    changeEditVisible(val) {
      this.editVisible = val
      if (!val) {
        this.reset()
      } else {
        this.updateInfo.sellingPrice && this.changeSellingPrice(this.updateInfo.sellingPrice + "")
      }
    },
    changeUpdateInfo(val, type = 0) {
      if (!val) {
        this.rules.sellingPrice[0].required = false
        this.updateInfo = {}
        if (type === 0) {
          this.type = this.$t('添加产品')
        } else {
          this.type = this.$t('批量修改')
        }
      } else {
        this.rules.sellingPrice[0].required = true
        this.updateInfo = val
        this.type = this.$t('编辑产品')
        if (this.updateInfo.discountStartTime && this.updateInfo.discountEndTime) {
          this.discountTime = [this.updateInfo.discountStartTime, this.updateInfo.discountEndTime]
        } else {
          this.discountTime = null
          this.discountRatio = null
        }
      }
      this.getProfit()
      this.getSysParaProduct()
    },
    changeSellingPrice(value) {
      value = this.toDecimal(value)
      this.updateInfo.sellingPrice = value
      if (this.type === '编辑产品') {
        // 根据当前售价改变利润比例
        this.updateInfo.profitRatio = ((this.$bigDecimal.divide(this.$bigDecimal.subtract(value, this.updateInfo.systemPrice), this.updateInfo.systemPrice) * 1) * 100).toFloor(2)
        // 根据当前售价改变利润
      }
      this.getProfit()
    },
    changeProfitRatio(value) {
      value = this.toDecimal(value)
      this.updateInfo.profitRatio = value

      if (this.type === '编辑产品') {
        // 根据当前利润比例改变售价
        this.updateInfo.sellingPrice = (this.$bigDecimal.multiply(this.updateInfo.systemPrice, (1 + value / 100)) * 1).toFloor(2)
      }
      this.getProfit()
    },
    changeDiscountRatio(value) {
      //只能输入整数

      value = parseInt(value | 0)
      this.updateInfo.discountRatio = value
      if (this.type === '编辑产品') {
        // 根据当前折扣比例改变折扣价
        this.updateInfo.discountPrice = (this.$bigDecimal.multiply(this.updateInfo.sellingPrice, (1 - value / 100)) * 1).toFloor(2)
      }
    },
    getProfit() {
      this.updateInfo.profit = (this.$bigDecimal.subtract(this.updateInfo.sellingPrice, this.updateInfo.systemPrice) * 1).toFloor(2)
    },
    // 保留小数
    toDecimal(value) {
      if (value >= 10000 * 10000) {
        value = 10000 * 10000 + ''
      }
      value = value.replace(/[^\d.]/g, "");// 清除"数字"和"."以外的字符
      value = value.replace(/^\./g, "");// 验证第一个字符是数字而不是字符
      value = value.replace(/\.{2,}/g, ".");// 只保留第一个.清除多余的
      value = value.replace(".", "$#$").replace(/\./g, "").replace("$#$", ".");
      value = value.replace(/^(\\-)*(\d+)\.(\d\d).*$/, '$1$2.$3');// 只能输入2个小数
      return value
    },
    submitCommodity() {
      this.$refs.form.validate((valid) => {
        if (valid) {
          this.$emit('submitCommodity', this.updateInfo)
        }
      })
    },
    getSysParaProduct() {
      getSysParaProduct().then(res => {
        this.sysParaProductInfo = res.data
      })
    }
  }
}
</script>

<style scoped>
.lh {
  line-height: 20px;
  padding: 10px 0 0;
}

.discountPrice {
  position: absolute;
  right: 15px;
  top: 0;
}
</style>
