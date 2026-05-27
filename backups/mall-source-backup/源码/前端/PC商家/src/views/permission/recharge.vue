<template>
  <div class="recharge-main">
    <el-card style="display: flex;flex: 1;width: 100%;height: 100%;">
      <div class="recharge" style="height: 120px" v-if="['Shop2U'].includes(projectTitle)">
        <div class="biaoti">{{ $t('充值方式') }}</div>
        <div class="duoxuan">
          <el-select v-model="channel" class="m-2" placeholder="Select" size="large" style="width: 100%">
            <el-option
                v-for="item in channelMap"
                :key="item.value"
                :label="item.label"
                :value="item.value"
            />
          </el-select>
        </div>
      </div>
      <div class="recharge" v-if="channel==='fund'">
        <div style="display: flex;justify-content: flex-start;">
          <div class="qrcode">
            <canvas id="canvas" style="display:none"></canvas>
            <el-image :src="imgUrl" class="image"/>
          </div>
          <div class="baocunerweima">
            <div class="qr-text">{{ $t('扫描二维码') }}</div>
            <div class="baocunerweima-buuon" style="margin-top: 20px;" @click="baocunhaibao">{{
                $t('保存二维码')
              }}
            </div>
          </div>
        </div>
        <div class="biaoti">{{ $t('币种') }}</div>
        <div class="duoxuan">
          <div v-for="(item,indx) in type_list" :key="indx" :class="type===item?'xuanzhong':'weixuan'" class="xuan1 "
               @click="tongdao_qiehuan2(item)">{{ item }}
            <img v-if="type===item" class="xuanzhong-img" src="../../assets/block_choose.png"/>
          </div>
          <div class="xuan1 weixuan"  @click="userBarkFunction">
            {{ $t('银行卡') }}
          </div>
        </div>
        <div class="biaoti">{{ $t('区块链网络') }}</div>
        <div class="duoxuan">
          <div v-for="(item,indx) in tongdao" :key="indx"
               :class="tongdao_xuanzhong.blockchain_name===item.blockchain_name?'xuanzhong':'weixuan'"
               class="xuan1 "
               @click="tongdao_qiehuan(item)">{{ item.blockchain_name }}
            <img v-if="tongdao_xuanzhong.blockchain_name===item.blockchain_name" class="xuanzhong-img"
                 src="../../assets/block_choose.png"/>
          </div>
        </div>
        <div class="biaoti">{{ $t('充值地址') }}</div>
        <div class="chongzhifuzhi">
          <div class="chongzhifuzhi2">
            <div class="dizhi">{{ tongdao_xuanzhong.address }}</div>
            <div style="flex: 1;"></div>
            <div class="fuzhi11 copy" style="color: #4AA8FF;" v-clipboard:copy="tongdao_xuanzhong.address"
                 v-clipboard:success="clipboardSuccess">{{ $t('复制') }}
            </div>
          </div>
        </div>
        <div class="biaoti">{{ $t('充值数量') }}</div>
        <div class="shuru">
          <el-form :model="form" :rules="rules" ref="rechargeForm">
            <el-form-item prop="amount">
              <el-input @input="inputNumber"
                        v-model.number="form.amount" :placeholder="$t('请输入充值数量')" clearable maxlength="30"/>
            </el-form-item>
          </el-form>
        </div>
        <div class="biaoti">{{ $t('预计到账') }}({{ $t('当前汇率') }} 1:{{ tongdao_xuanzhong.fee }})</div>
        <div class="chongzhifuzhi">
          <div class="chongzhifuzhi2">
            <div class="dizhi">{{ (form.amount * tongdao_xuanzhong.fee).toFloor(2) }}</div>
            <div style="flex: 1;"></div>
            <div class="fuzhi11" style="">{{ $t('USDT') }}</div>
          </div>
        </div>
        <div class="biaoti" style="margin-bottom: 10px;">{{ $t('上传图片（上传支付详情截图）') }}</div>
        <div class="shangchaun">
          <!--        <van-uploader v-model="fileList" multiple :max-count="1" preview-size="120px" :after-read="afterRead"/>-->
          <van-uploader v-model="fileList" :after-read="afterRead" :max-count="1" :max-size="isOverSize"
                        accept="image/png,image/jpg,image/jpeg"
                        deletable preview-size="120px" @delete="deleteImg(1)"
                        @oversize="onOversize"/>
        </div>
        <div class="tijiao">
          <el-button type="primary" @click="submitOrder" style="width: 120px">{{ $t('提交') }}</el-button>
        </div>
      </div>
      <div class="recharge" v-if="channel==='Bank'">
        <template v-if="!['FamilyShop'].includes(projectTitle)">
          <div class="biaoti">{{ $t('充值币种') }}</div>
          <div class="duoxuan">
            <el-select v-model="paraCurrency" @change="changeParaCurrency" class="m-2"
                       :placeholder="$t('请选择充值币种')"
                       size="large"
                       style="width: 100%">
              <el-option
                  v-for="item in paraCurrencyList"
                  :key="item.bank_code"
                  :label="item.bank_code"
                  :value="item.bank_code"
              />
            </el-select>
          </div>
          <div class="biaoti">{{ $t('充值金额') }}</div>
          <div class="duoxuan">
            <div class="shuru">
              <el-form :model="formParaCurrency" :rules="rulesParaCurrency" ref="formParaCurrencyForm">
                <el-form-item prop="amount">
                  <el-input @input="inputNumber"
                            v-model.number="formParaCurrency.amount" :placeholder="$t('请输入充值数量')" clearable
                            maxlength="10"/>
                </el-form-item>
              </el-form>
            </div>
          </div>
          <div class="tijiao">
            <el-button type="primary" @click="submitBankOrder" style="width: 120px">{{ $t('提交') }}</el-button>
          </div>
        </template>
        <template v-else>
          <div class="duoxuan">
            <span style="color: #F56C6C">{{ $t('银行卡充值请联系客服') }}</span>
          </div>
        </template>
      </div>
      <!-- gcash 充值 -->
      <div class="recharge" v-if="rechargeExchangeArr.includes(channel)">
        <div class="biaoti">{{ $t('充值金额') }}</div>
        <div class="duoxuan">
          <div class="shuru">
            <el-form :model="formParaCurrency" :rules="rulesParaCurrency" ref="formParaCurrencyForm">
              <el-form-item prop="amount">
                <el-input @input="inputNumber"
                          v-model.number="formParaCurrency.amount" :placeholder="$t('请输入充值数量')" clearable
                          maxlength="10"/>
              </el-form-item>
            </el-form>
          </div>
        </div>
        <div class="tijiao">
          <el-button type="primary" @click="submitGcashOrder" style="width: 120px">{{ $t('提交') }}</el-button>
        </div>
      </div>
    </el-card>
  </div>
</template>

<script>
import QRCode from 'qrcode'
import {Uploader} from 'vant';
import Toast from "@/utils/toast";
import {
  chongzhitijiao_post,
  getSysParaCurrency,
  huilu_huoqu_post,
  imageUpload,
  rechargeLimitConfig,
  selectPaymentChannel,
  session_token,
  thirdPartyRecharge,
  thirdPartyRechargeGcash
} from "@/api/user";
import clipboard from '@/directive/clipboard/index.js'
import {projectTitle} from "@/settings";

export default {
  directives: {
    clipboard
  },
  data() {
    return {
      projectTitle,
      formParaCurrency: {
        amount: ''
      },
      formParaCurrencyQuota: {
        min_amount: 2000,
        max_amount: 30000,
      },
      channelMap: [{label: this.$t('加密货币'), value: 'fund'}],
      channel: 'fund',
      formRecharge: {
        withdrawalMethod: 1
      },
      form: {
        amount: ''
      },
      rules: {
        amount: [
          {required: true, message: this.$t('请输入充值数量'), trigger: 'blur'},
          {validator: this.validateAmount, trigger: 'change'}
        ]
      },
      rulesParaCurrency: {
        amount: [
          {required: true, message: this.$t('请输入充值数量'), trigger: 'blur'},
          {validator: this.validateAmountParaCurrency, trigger: 'change'}
        ]
      },
      data: {},
      codes: '',
      tongdao_xuanzhong: {},
      imgUrl: '',
      tongdao: [],
      fileList: [],
      shangchuanurl: '',
      session_token: '',
      type: 'USDT',
      type_list: ['ETH', 'USDT', 'BTC'],
      feeSetInvetval: null,
      quotaReminder: {},
      quotaReminderParaCurrency: {},
      paraCurrencyList: [],
      paraCurrency: '', // 充值币种
      rechargeExchangeArr: ['GCash', 'GCash2.0', 'GCash3.0', 'Maya', 'GCash pay']
    }
  },
  components: {
    QRCode: QRCode,
    [Uploader.name]: Uploader
  },
  computed: {
    isOverSize() {
      return 10 * 1024 * 1024
    },
    rechargeExchangeRate() {
      return this.$store.getters.rechargeExchangeRate
    },
    channelList() {
      let data = [{label: this.$t('加密货币'), value: 'fund'},
        {label: this.$t('银行卡'), value: 'Bank'}]
      if (['Shop2U'].includes(projectTitle)) {
        data = [...data, {
          label: 'GCash pay', value: 'GCash pay'
        }, {
          label: 'GCash', value: 'GCash'
        }, {
          label: 'GCash2.0', value: 'GCash2.0'
        }, {
          label: 'GCash3.0', value: 'GCash3.0'
        }, {
          label: 'Maya', value: 'Maya'
        }]
      }
      return data
    }
  },
  watch: {
    channel(val) {
      if (val === 'Bank') {
        this.tongdao_qiehuan2(this.type_list.find(item => item === 'USDT'))
      } else if (this.rechargeExchangeArr.includes(val)) {
        if (['Shop2U'].includes(projectTitle)) {
          this.getSysParaCurrency(val)
        }
      }

    },
  },
  created() {
    
    this.selectPaymentChannel();
    this.feeSetInvetval && clearInterval(this.feeSetInvetval)
    this.feeSetInvetval = setInterval(() => {
      if (this.$route.path === '/wallet/Recharge' && this.channel === 'fund') {
        this.huilu_huoqu_post()
      }
    }, 2000)
    if (['Shop2U'].includes(projectTitle)) {
      this.getSysParaCurrency('Bank')
    }
  },
  methods: {
    changeParaCurrency() {
      let pc = this.paraCurrencyList.find(item => item.bank_code === this.paraCurrency)
      this.quotaReminderParaCurrency.min = this.$t('充值价值不得小于最小限额') + (pc.min_amount < 30 ? 30 : pc.min_amount)
      this.quotaReminderParaCurrency.max = this.$t('充值价值不得大于最大限额') + pc.max_amount
      this.formParaCurrency.amount = ''
    },
    getSysParaCurrency(productType) {
      getSysParaCurrency().then(res => {
        if (this.rechargeExchangeArr.includes(productType)) {
          this.formParaCurrencyQuota = res.data && res.data.find(item => item.productType === productType).range.find(item => item.bank_code === 'PHP')
        } else {
          this.paraCurrencyList = res.data && res.data.find(item => item.productType === productType).range
        }
        this.channelMap = this.channelList.filter(item => {
          const itemValue = res.data.find(resItem => resItem.productType === item.value) || {}
          return item.value === itemValue.productType
        })
        this.channelMap.unshift({label: this.$t('加密货币'), value: 'fund'})
        this.$refs.formParaCurrencyForm && this.$refs.formParaCurrencyForm.resetFields()
      })
    },
    validateAmount(rule, value, callback) {
      let count = this.form.amount * this.tongdao_xuanzhong.fee
      if (count < this.tongdao_xuanzhong.recharge_limit_min) {
        callback(new Error(this.quotaReminder.min))
      } else if (count > this.tongdao_xuanzhong.recharge_limit_max) {
        callback(new Error(this.quotaReminder.max))
      } else {
        callback()
      }
    },
    validateAmountParaCurrency(rule, value, callback) {
      let count = this.formParaCurrency.amount
      let pc = {}
      let minErr = this.quotaReminderParaCurrency.min
      let maxErr = this.quotaReminderParaCurrency.max
      if (this.rechargeExchangeArr.includes(this.channel)) {
        minErr = this.$t('充值价值不得小于最小限额') + this.formParaCurrencyQuota.min_amount
        maxErr = this.$t('充值价值不得大于最大限额') + this.formParaCurrencyQuota.max_amount
        pc = this.formParaCurrencyQuota
      } else {
        pc = this.paraCurrencyList.find(item => item.bank_code === this.paraCurrency)
      }
      // let pc = this.paraCurrencyList.find(item => item.bank_code === this.paraCurrency)
      if (count < pc.min_amount) {
        // callback(new Error(this.quotaReminderParaCurrency.min))
        callback(minErr)
      } else if (count > pc.max_amount) {
        // callback(new Error(this.quotaReminderParaCurrency.max))
        callback(maxErr)
      } else {
        callback()
      }
    },
    clipboardSuccess() {
      this.$message({
        message: this.$t('复制成功'),
        type: 'success',
        duration: 1500
      })
    },
    onOversize(file) {
      this.$notify({
        message: this.$t('上传图片大小不能超过 10MB!'),
        type: 'warning'
      });
    },
    deleteImg(index) {
      this.fileList.splice(index, 1)
    },
    submitOrder() {
      this.huilu_huoqu_post(() => {
        this.biaodan_tijiao()
      })
    },
    submitBankOrder() {
      if (this.paraCurrency === '') {
        Toast(this.$t('请选择充值币种'));
        return
      }
      if (this.formParaCurrency.amount === '') {
        Toast(this.$t('请输入充值数量'));
        return
      }
      if ((this.formParaCurrency.amount * this.rechargeExchangeRate).toFloor(2) < 10) {
        Toast(this.$t('充值价值不得小于最小限额') + 10 + 'USDT')
        return
      }
      if ((this.formParaCurrency.amount * this.rechargeExchangeRate).toFloor(2) > 100000) {
        Toast(this.$t('充值价值不得大于最大限额') + 100000 + 'USDT')
        return
      }
      session_token({}).then(res => {
        this.session_token = res.data.session_token
        thirdPartyRecharge({
          session_token: this.session_token,
          amount: this.formParaCurrency.amount,
          frenchCurrency: this.paraCurrency
        }).then(res => {
          Toast.success(this.$t('订单提交成功'));
          //打开新的页面给用户支付
          window.open(res.data)

          setTimeout(() => {
            this.$router.push({path: '/wallet/index', query: {type: 'recharge'}})
          }, 1000)
        })
      })
    },
    submitGcashOrder() {
      if (this.formParaCurrency.amount === '') {
        Toast(this.$t('请输入充值数量'));
        return
      }
      if (Number(this.formParaCurrency.amount) < this.formParaCurrencyQuota.min_amount) {
        Toast(this.$t('充值价值不得小于最小限额') + ' ' + this.formParaCurrencyQuota.min_amount)
        return
      }
      if (Number(this.formParaCurrency.amount) > this.formParaCurrencyQuota.max_amount) {
        Toast(this.$t('充值价值不得大于最大限额') + ' ' + this.formParaCurrencyQuota.max_amount)
        return
      }
      session_token({}).then(res => {
        this.session_token = res.data.session_token
        //当前域名
        const params = {
          session_token: this.session_token,
          amount: this.formParaCurrency.amount,
          pageUrl: this.channel === 'GCash' ? null : window.location.href + '/www#/wallet/index'
        }
        let rechargeType = 'PHP_recharge'
        switch (this.channel) {
          case 'GCash pay':
            rechargeType = 'PHP_recharge5'
            break
          case 'GCash':
            rechargeType = 'PHP_recharge'
            break
          case 'GCash2.0':
            rechargeType = 'PHP_recharge2'
            break
          case 'GCash3.0':
            rechargeType = 'PHP_recharge3'
            break
          case 'Maya':
            rechargeType = 'PHP_recharge4'
            break
        }
        thirdPartyRechargeGcash(params, rechargeType).then(res => {
          Toast.success(this.$t('订单提交成功'));
          //打开新的页面给用户支付
          window.open(res.data)

          setTimeout(() => {
            this.$router.push({path: '/wallet/index', query: {type: 'recharge'}})
          }, 1000)
        })
      })
    },
    biaodan_tijiao() {
      const t = this
      if (this.form.amount === '') {
        Toast(t.$t('请输入充值数量'));
        return
      }
      if (this.shangchuanurl === '') {
        Toast(t.$t('请上传图片'));
        return
      }
      if ((this.form.amount * this.tongdao_xuanzhong.fee).toFloor(2) < this.tongdao_xuanzhong.recharge_limit_min) {

        Toast(t.$t('充值价值不得小于最小限额') + this.tongdao_xuanzhong.recharge_limit_min + 'usdt')
        return
      }
      if ((this.form.amount * this.tongdao_xuanzhong.fee).toFloor(2) > this.tongdao_xuanzhong.recharge_limit_max) {
        Toast(t.$t('充值价值不得大于最大限额') + this.tongdao_xuanzhong.recharge_limit_max + 'usdt')
        return
      }
      session_token({}).then(res => {
        this.session_token = res.data.session_token
        this.chongzhitijiao()
      })
    },
    rechargeLimitConfig() {
      rechargeLimitConfig({}).then(configRes => {
        const rechargeAmountMin = configRes.data?.rechargeAmountMin || 10
        const rechargeAmountMax = configRes.data?.rechargeAmountMax || 0
        this.tongdao_xuanzhong.recharge_limit_min = rechargeAmountMin
        this.quotaReminder.min = this.$t('充值价值不得小于最小限额') + this.tongdao_xuanzhong.recharge_limit_min + 'USDT'
        this.tongdao_xuanzhong.recharge_limit_max = rechargeAmountMax
        this.quotaReminder.max = this.$t('充值价值不得大于最大限额') + this.tongdao_xuanzhong.recharge_limit_max + 'USDT'
      })
    },
    chongzhitijiao() {
      const data = {
        'session_token': this.session_token,
        'amount': this.form.amount,
        'from': '123',
        'blockchain_name': this.tongdao_xuanzhong.blockchain_name,
        'img': this.shangchuanurl,
        'coin': this.tongdao_xuanzhong.coin,
        'channel_address': this.tongdao_xuanzhong.address,
        'tx': '123',
      };
      chongzhitijiao_post(data).then(res => {
        this.$notify({
          message: this.$t('提交成功'),
          type: 'success'
        });
        this.form.amount = ''
        this.fileList = []
        this.shangchuanurl = ''
        //清空表单校验
        this.$refs.rechargeForm.clearValidate()
        setTimeout(() => {
          this.$router.push({path: '/wallet/index', query: {type: 'recharge'}})
        }, 1000)
      }).catch(err => {
        console.log(err.msg)
      })
    },
    tongdao_qiehuan(e) {
      this.tongdao_xuanzhong = e
      this.useqrcode1()
    },
    tongdao_qiehuan2(e) {
      // this.tongdao_xuanzhong = e
      if (this.channel === "Bank" && ['FamilyShop'].includes(projectTitle)) {
        //localStorage缓存里加上showCustomer=true
        this.$store.commit('app/SET_SHOW_CUSTOMER', true)
        return
      }
      if (this.channel === 'fund') {
        this.type = e
        this.tongdao = []
        this.selectPaymentChannel()
      }
    },
    userBarkFunction() {
      console.log('');
      this.$store.commit('app/SET_SHOW_CUSTOMER', true)
      Toast(this.$t('银行卡充值请联系客服'))
    },
    selectPaymentChannel() {
      console.log(123)
      selectPaymentChannel({}).then(e => {
        console.log('rr', e)
        let res22 = e.data
        // this.code = this.$route.query.usercode
        this.type_list = []
        for (var i = 0; i < res22.length; i++) {
          if (res22[i]['coin'] === this.type) {
            this.tongdao.push(res22[i])
            console.log(this.tongdao)
          }
          this.type_list.push(res22[i].coin)
        }
        this.type_list = [...new Set(this.type_list)]
        // if (['FamilyShop'].includes(projectTitle)) {
        //   this.type_list.push(this.$t('银行卡'))
        // }
        this.tongdao_xuanzhong = this.tongdao[0]
        this.useqrcode1()
        this.huilu_huoqu_post()
        this.rechargeLimitConfig()
      })
    },
    //amount只能输入数字
    inputNumber(val) {
      val = val.replace(/[^0-9.]/g, '')
      if (val !== '') {
        let parts = val.toString().split('.');
        let inputValue = ''
        if (parts.length === 2) {
          const decimalPart = parts[1].slice(0, 10); // 截取小数部分的前10位
          inputValue = `${parts[0]}.${decimalPart}`;
        } else {
          inputValue = parts[0]
        }
        if (this.channel === 'fund') {
          this.form.amount = inputValue
        } else {
          this.formParaCurrency.amount = inputValue
        }
      }
    },
    huilu_huoqu_post(cb) {
      huilu_huoqu_post({symbol: this.tongdao_xuanzhong.coin}).then(res => {
        console.log(res)
        this.tongdao_xuanzhong.fee = res.data.price
        cb && cb()
      })
    },
    afterRead(file) {
      console.log(file)
      const that = this
      let formData = new FormData();//通过formdata上传
      formData.append('file', file.file);
      formData.append('moduleName', '123');
      that.fileList[0].status = 'uploading';
      that.fileList[0].message = that.$t('上传中...');
      imageUpload(formData).then(res => {
        this.shangchuanurl = res.data
        that.fileList[0].status = 'done';
      }).catch(function (err) {
        console.log(err)
        this.fileList = []
        that.fileList[0].status = 'failed';
        that.fileList[0].message = that.$t('上传失败');
      })
    },
    // copyData(ea) {
    //   //如果需要回调：
    //   this.$copyText(ea).then(e => {
    //     alert(this.$t('复制成功'))
    //     console.log(e)
    //   }, function (e) {
    //     alert(this.$t('复制失败'))
    //     console.log(e)
    //   })
    // },
    // copyData2(ea) {
    //   //如果需要回调：
    //   this.$copyText(ea).then(e => {
    //     // alert('复制成功')
    //     console.log(e)
    //   }, function (e) {
    //     // alert('复制失败')
    //     console.log(e)
    //   })
    // },
    useqrcode1() {//生成二维码
      let canvas = document.getElementById('canvas')
      let url = this.tongdao_xuanzhong?.address || ''
      if (!url) {
        return
      }
      QRCode.toCanvas(canvas, url, function (error) {
        if (error) {
          console.error(error)
        } else {
          console.log('success!');
        }
      })
      this.saveImg()//保存图片
    },
    baocunhaibao() {
      let myCanvas = document.getElementsByTagName('canvas');
      this.imgUrl = myCanvas[0].toDataURL('image/png')
      this.getUrlBase64(this.imgUrl).then(base64 => {
        let link = document.createElement('a')
        link.href = base64
        link.download = 'qrCode.png'
        link.click()
      })
    },
    getUrlBase64(url) {
      return new Promise(resolve => {
        let canvas = document.createElement('canvas')
        let ctx = canvas.getContext('2d')
        let img = new Image()
        img.crossOrigin = 'Anonymous' //允许跨域
        img.src = url
        img.onload = function () {
          canvas.height = 300
          canvas.width = 300
          ctx.drawImage(img, 0, 0, 300, 300)
          let dataURL = canvas.toDataURL('image/png')
          canvas = null
          resolve(dataURL)
        }
      })
    },
    //保存图片
    saveImg() {
      let myCanvas = document.getElementsByTagName('canvas');
      this.imgUrl = myCanvas[0].toDataURL('image/png')
    },
    onClickLeft() {
      history.go(-1)
    },
    onClick1() {
      this.$router.push({path: '/rechargeRecord'})
    }
  }
}
</script>

<style lang="scss" scoped>
.recharge-main {
  display: flex;
  justify-content: flex-start;
  align-items: self-start;
  flex-direction: column;
  min-height: calc(100vh - 94px);
  padding: 20px;
  box-sizing: border-box;

  .recharge {
    width: 550px;
    height: 100%;
    background: #ffffff;
    flex: 1;
    padding: 24px;


    .biaoti {
      float: left;
      margin-top: 20px;
      width: 100%;
      margin-bottom: 10px;
      font-style: normal;
      font-weight: 400;
      font-size: 14px;
      color: #333333;
    }

    .duoxuan {
      width: 100%;

      .xuan1 {
        float: left;
        width: 100px;
        height: 40px;
        text-align: center;
        position: relative;
        font-style: normal;
        font-weight: 400;
        font-size: 14px;
        line-height: 40px;
        border-radius: 4px;
        margin-right: 24px;
        margin-bottom: 12px;
        cursor: pointer;
      }

      .weixuan {
        color: #999999;
        border: 1px solid #999999;
      }

      .xuanzhong {
        color: #1552F0;
        border: 1px solid #1552F0;
      }

      .xuanzhong-img {
        width: 23px;
        height: 23px;
        position: absolute;
        right: 0;
        bottom: 0;
      }
    }

    .qrcode {
      width: 150px;
      height: 150px;
      border: solid 1px #cccccc;
      flex-shrink: 0;
      margin-right: 24px;
      box-sizing: border-box;

      .image {
        width: 100%;
        height: 100%;
      }
    }

    .baocunerweima {
      display: flex;
      justify-content: center;
      flex-direction: column;
      //margin-top: 30px;
      width: 100%;
      float: left;

      .qr-text {
        font-family: 'Roboto';
        font-style: normal;
        font-weight: 400;
        font-size: 14px;
        line-height: 16px;
        color: #000000;
        text-indent: 12px;
      }

      .baocunerweima-buuon {
        width: 114px;
        height: 40px;
        border: 1px solid #DDDDDD;
        border-radius: 4px;
        font-style: normal;
        font-weight: 400;
        font-size: 14px;
        line-height: 40px; //
        text-align: center;

        /* 333 */

        color: #333333;
      }
    }

    .chongzhifuzhi {
      float: left;
      box-sizing: border-box;
      width: 100%;

      .chongzhifuzhi2 {
        padding: 0 10px;
        box-sizing: border-box;
        width: 100%;
        height: 44px;
        border: 1px solid #DDDDDD;
        font-style: normal;
        font-weight: 400;
        font-size: 14px;
        line-height: 44px;
        display: flex;

        /* 333 */

        color: #333333;

        .dizhi {
          width: calc(100% - 60px);
          overflow: hidden;
          text-overflow: ellipsis;
          white-space: nowrap;
        }
      }
    }

    .shuru {
      width: 100%;
      float: left;
      box-sizing: border-box;
    }

    .tijiao {
      width: 100%;
      padding: 25px 0;
      box-sizing: border-box;
      float: left;

      .tijiao2 {
        width: 180px;
        height: 44px;
        background: #1552F0;
        border-radius: 4px;
        font-style: normal;
        font-weight: 400;
        font-size: 16px;
        line-height: 44px;
        /* identical to box height */

        text-align: center;

        color: #FFFFFF;
      }
    }
  }
}
</style>

<style>
.recharge.van-uploader__upload {
  width: 120px !important;
  height: 120px !important;
}

.recharge .copy {
  cursor: pointer;
}
</style>
