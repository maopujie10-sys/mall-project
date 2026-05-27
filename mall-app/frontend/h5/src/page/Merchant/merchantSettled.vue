<template>
  <div class="merchantSettled">
    <mer-chant-header id="product"></mer-chant-header>
    <div class="merchantSettled-wap">
      <div class="step-div">
        <!-- step1 -->
        <div v-if="step == 1">
          <div class="content">
            <p class="title">{{$t('第一章概述')}}</p>
            <p>
              {{$t('适用范围：本协议适用于e-shop平台商户，商户可根据需要选择经营模式企业需要通过以下方式向买家销售商品或提供服务e-shop平台。')}}
            </p>
            <p>
              {{$t('1.1) e-shop为广大买家提供最好的品质货物与服务。 为保护合法权益e-shop商户，维护e-shop的正常秩序业务，根据“e-shop 服务条款”和其他服务/合作协议，制定本协议。')}}
            </p>
            <p>
              {{$t('1.2) e-shop平台一般规则是添加基本义务或规范居民商人基本权利的行使e-shop 条款。')}}
            </p>
            <p>
              {{$t('1.3) 基于e-shop的规则行为判断与处理从合理的角度结合所提供的证据由双方根据相关事实认定平台规则严格执行。 e-shop商家是平等的规则的应用。应用程序中的应用程序是平等的是sd')}}
            </p>
            <p class="padding-tb">{{$t('第一章概述')}}</p>
            <p>
              {{$t('适用范围：本协议适用于e-shop平台商户，商户可根据需要选择经营模式企业需要通过以下方式向买家销售商品或提供服务e-shop平台。')}}
            </p>
            <p>
              {{$t('1.1) e-shop为广大买家提供最优质的商品和服务。 为保护e-shop商家的合法权益，维护e-shop业务的正常秩序，根据《e-shop服务条款》等服务/合作协议，制定本协议。')}}
            </p>
            <p>
              {{$t('1.2)e-shop平台通则是在e-shop条款中增加基本义务或规范常驻商户基本权利的行使。')}}
            </p>
            <p>
              {{$t('1.3) 规则行为的确定和处理，基于e-shop从合理的角度结合双方提供的证据确定的事实，依据相关平台规则严格执行。 e-shop商家在规则的适用上是平等的。')}}
            </p>
            <p>
              {{$t('1.4) 商户应遵守国家法律、行政法规、部门规章等规范性文件。 任何涉嫌违反国家法律、行政法规、部门规章和其他规范性文件的行为，本协议已有规定，本协议适用； 本协议未作规定，e-shop有权酌情处理相应的规则，但e-shop不免除商家因违法、违约等行为而承担的法律责任。')}}
            </p>
            <p>
              {{$t('1.5) 商家在e-shop的任何行为，也应遵守与e-shop签订的协议。')}}
            </p>
            <p>
              {{$t('1.6) e-shop有权随时更改本协议，并在平台首页或商户管理系统等渠道公布。 如商户不同意变更，应立即停止使用e-shop平台提供的相关服务，并及时通知e-shop。 e-shop有权单方面决定商户的行为及应适用的规则/协议，并据此进行处理。')}}
            </p>
          </div>
          <div class="bottom">
            <van-checkbox v-model="checked">
              {{ $t('我已经阅读并同意') }}
              <span class="color-yellow">{{ $t('入驻协议') }}</span>
            </van-checkbox>
            <van-button type="primary" :color="mainColor" class="button" @click="stepFun">{{ $t('同意') }}</van-button>
          </div>
        </div>
        <!-- step2 -->
        <div v-else-if="step == 2">
          <div class="content content2">
            <p class="title">{{ $t('商业信息') }}</p>
            <el-form :model="ruleForm" :rules="rules" ref="ruleForm" :label-position="labelPosition" label-width="200px"
              class="demo-ruleForm">
              <el-form-item :label="$t('店铺标志')" prop="sellerImg">
                <div class="uploder-wrap">
                  <van-uploader v-model="fileList1" :max-count="1" :after-read="afterRead1" accept=".png,.jpg,.jpeg" />
                  <div class="tips">{{ $t('推荐尺寸') }} 200*200px <span>{{ $t('上传需要') }}</span></div>
                </div>
                <div>
                  <cropperjs
                    :imgFile="imgFile"
                    :ratioWidth="ratioWidth"
                    :ratioHeight="ratioHeight"
                    @handleCancel="handleCancel"
                    @handleUpload="handleUpload"
                    @handleCropData="handleCropData"
                    v-if="isCutting">
                  </cropperjs>
                </div>
              </el-form-item>
              <el-form-item :label="$t('店铺名称')" prop="sellerName">
                <el-input :placeholder="$t('请输入')" v-model="ruleForm.sellerName"></el-input>
              </el-form-item>
              <el-form-item :label="$t('店铺地址')" prop="sellerAddress">
                <el-input :placeholder="$t('请输入')" v-model="ruleForm.sellerAddress"></el-input>
              </el-form-item>

              <el-form-item :label="$t('国家')" prop="nationality">
                <div @click="openNationality(2)">
                  <el-input @click="openNationality(2)" readonly :placeholder="$t('请选择国家')"
                    v-model="ruleForm.nationality"></el-input>
                </div>

              </el-form-item>
              <!-- <el-form-item :label="$t('证件类型')" prop="idname">
                <el-select v-model="ruleForm.idname" placeholder="请选择">
                  <el-option
                    v-for="item in options"
                    :key="item.value"
                    :label="item.label"
                    :value="item.value">
                  </el-option>
                </el-select>
              </el-form-item> -->
              <el-form-item :label="$t('证件/护照号码')" prop="idnumber">
                <el-input :placeholder="$t('请输入')" v-model="ruleForm.idnumber"></el-input>
              </el-form-item>
              <el-form-item :label="$t('真实姓名')" prop="name">
                <el-input :placeholder="$t('请输入真实姓名')" v-model="ruleForm.name"></el-input>
              </el-form-item>
              <el-form-item :label="$t('证件照/上传护照')">
                <div class="uploder-center">
                  <div class="uploder-two-wrap">
                    <van-uploader :after-read="afterRead2" v-model="fileList2" @delete="handleDelete(2)" :max-count="1" accept=".png,.jpg,.jpeg"  />
                    <div class="tips">{{ ruleForm.idname == '身份证'? $t('证件正面') : $t('护照')}}</div>
                  </div>
                  <!-- v-if="ruleForm.idname == '身份证'" -->
                  <div class="uploder-two-wrap">
                    <van-uploader :after-read="afterRead3" v-model="fileList3" @delete="handleDelete(3)" :max-count="1" accept=".png,.jpg,.jpeg"  />
                    <div class="tips">{{ $t('证件反面') }}</div>
                  </div>
                  <div class="uploder-two-wrap">
                    <van-uploader :after-read="afterRead4" v-model="fileList4" @delete="handleDelete(4)" :max-count="1" accept=".png,.jpg,.jpeg" />
                    <div class="tips">{{ $t('手持证件照') }}</div>
                  </div>
                </div>
                <div>
                  <div class="el-form-item__label" style="margin-bottom: -26px">{{$t('拍摄示例')}}</div>
                  <div class="correct-warp">
                    <img src="@/assets/image/Merchant/01.png" />
                    <img src="@/assets/image/Merchant/02.png" />
                    <img src="@/assets/image/Merchant/03.png" />
                  </div>
                </div>
              </el-form-item>
<!--              <el-form-item :label="$t('拍摄示例')">-->
<!--               -->
<!--              </el-form-item>-->
              <div style="margin-bottom: -30px; margin-top: 45px">
                <p>{{ $t('验证您的电子邮件或电话号码') }}</p>
                <div class="tab-wrap">
                  <!-- <div class="tab-item" v-for="(item, index) in tabList" :key="index" @click="tabIndex = index"
                       :class="[tabIndex === index ? 'active' : '']">{{ item }}</div> -->
                  <div class="tab-item" @click="tabIndex = 0"
                       :class="[tabIndex === 0 ? 'active' : '']">{{ $t('电子邮箱') }}</div>
                  <div class="tab-item" @click="tabIndex = 1"
                       :class="[tabIndex === 1 ? 'active' : '']">{{ $t('手机号') }}</div>
                </div>
              </div>

              <el-form-item :label="$t('电子邮箱')" prop="username" v-if="tabIndex === 0">
                <el-input :placeholder="$t('请输入正确的邮箱地址')" v-model="ruleForm.username"></el-input>
              </el-form-item>
              <el-form-item :label="$t('手机号')" prop="username" v-if="tabIndex === 1">
                <el-input :placeholder="$t('请输入手机号')" class="phone_number_wrap" type="text" v-model="ruleForm.username">
                  <div slot="prepend">
                    <div class="prepend-wrap" @click="openNationality(1)">
                      <div class="phone_number">+{{ areaCode }}</div>
                      <img src="@/assets/image/Merchant/down-icon.png" />
                    </div>
                    <!-- <el-dropdown @command="handleSetLang" :trigger="'click'">
                      <div class="prepend-wrap" >
                        <div class="phone_number">+668</div>
                        <img src="@/assets/image/Merchant/down-icon.png" />
                      </div>

                      <el-dropdown-menu slot="dropdown">
                        <el-dropdown-item :command="index" v-for="(item, index) in lang" :key="index">
                          <div class="lang-item">
                           +66(泰国)
                          </div>
                        </el-dropdown-item>
                      </el-dropdown-menu>
                    </el-dropdown> -->
                  </div>
                </el-input>
              </el-form-item>
              <!-- <el-form-item :label="$t('邮箱验证码')" prop="name" v-if="tabIndex === 0">
                <el-input :placeholder="$t('请输入')" class="code-input" type="text" v-model="ruleForm.name">
                  <div class="code-wrap" slot="suffix">{{ $t('发送') }}</div>
                </el-input>
              </el-form-item>
              <el-form-item :label="$t('短信验证码')" prop="name" v-if="tabIndex === 1">
                <el-input :placeholder="$t('请输入')" class="code-input" type="text" v-model="ruleForm.name">
                  <div class="code-wrap" slot="suffix">{{ $t('发送') }}</div>
                </el-input>
              </el-form-item> -->
              <el-form-item :label="$t('登录密码')" prop="password">
                <el-input :placeholder="$t('请输入')" type="password" v-model="ruleForm.password"></el-input>
              </el-form-item>
              <el-form-item :label="$t('再次输入确认登录密码')" prop="re_password">
                <el-input :placeholder="$t('请输入')" type="password" v-model="ruleForm.re_password"></el-input>
              </el-form-item>
              <el-form-item :label="$t('邀请码')" prop="usercode">
                <el-input :placeholder="$t('请输入')" v-model="ruleForm.usercode"></el-input>
              </el-form-item>
            </el-form>
          </div>
          <div class="bottom">
            <van-checkbox v-model="checked" v-if="step == 1">
              {{ $t('我已经阅读并同意') }}
              <span class="color-yellow">{{ $t('入驻协议') }}</span>
            </van-checkbox>
            <!-- <van-button type="primary" :color="mainColor" v-if="step == 1" class="button" @click="stepFun()">{{ $t('同意') }}
            </van-button> -->
            <van-button type="primary" :color="mainColor" v-if="step == 2" class="button" @click="sellerRegister">{{
                $t('提交申请表')
            }}
            </van-button>
          </div>
        </div>
        <!-- step3 -->
        <submit-success v-else></submit-success>
      </div>
    </div>
    <mer-chant-footer></mer-chant-footer>
    <nationality-list  ref='controlChild' :title="$t('选择区域码')" @getName="getName(arguments)">
    </nationality-list>
  </div>
</template>

<script>
import merChantHeader from "./components/mer-chant-header";
import merChantFooter from "./components/mer-chant-footer";
import submitSuccess from "./components/submit-success.vue";
import { mapGetters, mapMutations } from "vuex";
import { DropdownMenu, DropdownItem, Dropdown, Form, FormItem, Input, Select, Option, } from 'element-ui'
import { Checkbox, Button, Uploader, Toast } from "vant";
import { sellerRegister, uploadimg, getStatus } from "@/API/commodity";
import NationalityList from '@/components/NationalityList'
import { ref } from "vue";
import cropperjs from './components/cropperjs.vue'
export default {
  name: "merchantSettled",
  data() {
    return {
        mainColor: process.env.VUE_APP_MAIN_COLOR,
      isCutting: false,// 是否裁剪
      imgFile: 'https://bpic.588ku.com/element_water_img/18/06/12/b2887846cb19ff36a5502401ac918809.jpg',
      ratioWidth: 1,// 裁剪比例：长 自由比例设置为: 0 即可
      ratioHeight: 1,// 裁剪比例：宽 自由比例设置为: 0 即可
      step: 1,
      checked: false,
      screenWidth: document.body.clientWidth,
      type: 'Email',//Email/Moblie
      uploadCheckIndex: 1,
      areaCode: 1,
      ruleForm: {
        type: 1,  //1/手机；2/邮箱；
        usercode: '',
        name: '',
        idimg_1: '',
        idimg_2: '',
        idimg_3: '',
        idname: '身份证',
        idnumber: '',
        nationality: '',
        sellerImg: '',
        username: '',
        password: '',
        re_password: '',
        sellerName: '',
        sellerAddress: '',
      },
      labelPosition: 'top',
      isCode: true,
      rules: {
        idname: [
          { required: true, message: this.$t('请输入身份证或者护照号'), trigger: 'blur' },
        ],
        idimg_1: [
          { required: true, message: this.$t('请上传身份证正面'), trigger: 'blur' },
        ],
        idimg_2: [
          { required: true, message: this.$t('请上传身份证反面'), trigger: 'blur' },
        ],
        idimg_3: [
          { required: true, message: this.$t('请上传手持身份证'), trigger: 'blur' },
        ],
        re_password: [
          { required: true, message: this.$t('请确认输入登录密码'), trigger: 'blur' },
        ],
        password: [
          { required: true, message: this.$t('请输入登录密码'), trigger: 'blur' },
        ],
        sellerImg: [
          { required: true, message: this.$t('请上传店铺logo'), trigger: 'blur' },
        ],
        username: [
          { required: true, message: this.$t('请输入正确的数据'), trigger: 'blur' },
        ],
        idnumber: [
          { required: true, message: this.$t('请输入身份证或者护照号'), trigger: 'blur' },
        ],
        name: [
          { required: true, message: this.$t('请输入真实姓名'), trigger: 'blur' },
        ],
        sellerName: [
          { required: true, message:  this.$t('请输入店铺名称'), trigger: 'blur' },
        ],
        sellerAddress: [
          { required: true, message: this.$t('请输入店铺地址'), trigger: 'blur' },
        ],
        usercode: [
          { required: true, message: this.$t('请输入邀请码'), trigger: 'blur' },
        ],
      },
      options:[{label:this.$t('身份证'),value:'身份证'},{label:this.$t('护照'),value:'护照'}],
      fileList1: [],
      fileList2: [],
      fileList3: [],
      fileList4: [],
      CountryList: [
        {
          label: '中国',
          value: 'cn',
          icon: require('@/assets/image/language/cn.png')
        },
      ],
      tabList: [this.$t('电子邮箱'), this.$t('手机号')],
      tabIndex: 0,
      lang: [
        {
          title: '简体中文',
          key: 'cn',
          icon: require('@/assets/image/language/cn.png')
        },
        {
          title: 'English',
          key: 'en',
          icon: require('@/assets/image/language/usa.png')
        },
        {
          title: '繁体中文',
          key: 'tw',
          icon: require('@/assets/image/language/tw.png')
        }
      ],
      pageDiaCode: true,
    };
  },

  computed: {
    languageIcon() {
      const language = this.$store.getters.language || 'tw'
      const icon = {
        'cn': require('@/assets/image/language/cn.png'),
        'en': require('@/assets/image/language/usa.png'),
        'tw': require('@/assets/image/language/tw.png')
      }
      return icon[language]
    },
    ...mapGetters({
      activeLang: 'language'
    })
  },
  components: {
    cropperjs,
    merChantHeader,
    NationalityList,
    merChantFooter,
    submitSuccess,
    [DropdownMenu.name]: DropdownMenu,
    [DropdownItem.name]: DropdownItem,
    [Dropdown.name]: Dropdown,

    [Checkbox.name]: Checkbox,
    [Button.name]: Button,
    [Form.name]: Form,
    [FormItem.name]: FormItem,
    [Input.name]: Input,
    [Uploader.name]: Uploader,
    [Select.name]: Select,
    [Option.name]: Option,
    [Toast.name]: Toast
  },
  created() {
    if (this.screenWidth >= 500) {
      this.labelPosition = "left"
    } else {
      this.labelPosition = "top"
    }
  },
  watch: {
    tabIndex(val, old) {
      if (val === old) return;
      this.ruleForm.username = '';
      this.ruleForm.password = '';
      this.ruleForm.re_password = '';
    }
  },
  methods: {
    // 裁剪
    handleCutting(){
      this.isCutting = true;
    },
    // 取消
    handleCancel(){
      this.isCutting = false;
      this.fileList1 = [];
    },
    // 上传
    handleUpload(data){
      let fileOfBlob = new File([data], "logo.png") // 重命名
      Toast.loading({
        duration: 0,
        message: this.$t('上传中'),
        forbidClick: true,
      })
      let formData = new FormData();//通过formdata上传
      formData.append('file', fileOfBlob)
      formData.append('moduleName', 'selle')

      uploadimg(formData).then((data) => {
        this.ruleForm.sellerImg = data
        this.isCutting=false

        this.fileList1[0].content=data
        // this.fileList1[0].file=fileOfBlob
      }).finally(() => {
        Toast.clear()
      })
    },
    // 裁剪
    handleCropData(data){
      console.log('裁剪数据');
      console.log(data);
    },
    ...mapMutations(['setLanguage']),
    handleSetLang(index) {
      console.log(index)
      // 设置i18n.locale 组件库会按照上面的配置使用对应的文案文件
      this.$i18n.locale = this.lang[index].key
      // // 提交mutations
      this.setLanguage(this.lang[index].key)
    },
    handleDelete(index) {
      this[`fileList${index}`] = [];
    },
    //商户注册
    sellerRegister() {
      // if (this.ruleForm.idname == '身份证') {


      // } else {
      //   if (!this.ruleForm.idimg_1) {
      //     Toast(this.$t('请上传护照'))
      //     return
      //   }
      // }
      if (!this.checked) {
        Toast(this.$t('请同意入驻协议'))
        return
      }
      // if (this.ruleForm.name == '护照') {
      //   this.ruleForm.idimg_2 = '1111',
      //   this.ruleForm.idimg_3 = '1111'
      // }
      this.ruleForm.type = this.tabIndex === 0 ? 2 : 1
      this.$refs['ruleForm'].validate((valid) => {
        if (valid) {
          if (!this.ruleForm.idimg_1 || !this.ruleForm.idimg_2 || !this.ruleForm.idimg_3) {
            Toast(this.$t('请上传证件照片'))
          } else {
            sellerRegister(this.ruleForm).then((res) => {
              this.step = 3
              this.$el.querySelector('#product').scrollIntoView({ behavior: 'smooth' })
            })
          }
        } else {
          return false;
        }
      })
    },
    stepFun() {
      if (!this.checked) {
        Toast(this.$t('请同意入驻协议'));
        return
      }
      this.step = 2
      this.$el.querySelector('#product').scrollIntoView({ behavior: 'smooth' })
    },
    openNationality(index) {
      if (index === 1) {
        this.isCode = true
      } else {
        this.isCode = false
      }
      this.$refs.controlChild.open()
    },
    getName(params) {
      if (this.isCode) {
        this.areaCode = params[2]
      } else {
        this.ruleForm.nationality = params[0]
      }
    },
    //文件上传
    afterRead1(file) {
      this.imgFile=file.content
      this.isCutting=true
      // Toast.loading({
      //   duration: 0,
      //   message: this.$t('上传中'),
      //   forbidClick: true,
      // })
      // console.log(file)
      // let formData = new FormData();//通过formdata上传
      // formData.append('file', file.file)
      // formData.append('moduleName', 'selle')

      // uploadimg(formData).then((data) => {
      //   Toast.clear()
      //   this.ruleForm.sellerImg = data
      // })

    },
    //文件上传
    afterRead2(file) {
      Toast.loading({
        duration: 0,
        message: this.$t('上传中'),
        forbidClick: true,
      })
      let formData = new FormData();//通过formdata上传
      formData.append('file', file.file)
      formData.append('moduleName', 'selle')
      uploadimg(formData).then((data) => {
        this.ruleForm.idimg_1 = data
      }).catch((error) => {
        this.fileList2 = [];
        Toast.fail(this.$t('上传失败'));
      }).finally(() => {
        Toast.clear()
      })
    },
    //文件上传
    afterRead3(file) {
      Toast.loading({
        duration: 0,
        message: this.$t('上传中'),
        forbidClick: true,
      })
      let formData = new FormData();//通过formdata上传
      formData.append('file', file.file)
      formData.append('moduleName', 'selle')
      uploadimg(formData).then((data) => {
        this.ruleForm.idimg_2 = data
      }).catch((error) => {
        this.fileList3 = [];
        Toast.fail(this.$t('上传失败'));
      }).finally(() => {
        Toast.clear()
      })
    },
    //文件上传
    afterRead4(file) {
      Toast.loading({
        duration: 0,
        message: this.$t('上传中'),
        forbidClick: true,
      })
      let formData = new FormData();//通过formdata上传
      formData.append('file', file.file)
      formData.append('moduleName', 'selle')
      uploadimg(formData).then((data) => {
        this.ruleForm.idimg_3 = data
      }).catch((error) => {
        this.fileList4 = [];
        Toast.fail(this.$t('上传失败'));
      }).finally(() => {
        Toast.clear()
      })
    }
  },
};
</script>

<style lang="scss" scoped>
.padding-tb {
  padding: 20Px 0 !important;
}

.color-yellow {
  color: var(--main-color) !important;
}

.merchantSettled {
  width: 100%;

  .merchantSettled-wap {
    background: #fff;
    display: flex;
    justify-content: center;
    align-items: center;
    width: 1200Px;
    margin: 0 auto;

    .step-div {
      width: 1197Px;
      background: #fff;

      border-radius: 4Px;
      margin-top: -86Px;

      .content {
        padding: 20Px 30Px;
        border: 1Px solid #eeeeee;

        .title {
          font-size: 24Px;
          color: #333333;
          font-weight: 700;
        }

        p {
          font-family: "PingFang HK";
          font-style: normal;
          font-size: 14Px;
          line-height: 20Px;
          color: #333333;
          padding: 6Px 0;
        }
      }

      .bottom {
        height: 140Px;
        font-size: 14Px;
        display: flex;
        flex-direction: column;
        justify-content: space-around;
        align-items: center;
        margin: 20Px 0;

        .button {
          width: 475Px;
        }
      }
    }
  }
}

/deep/ .van-field__label {
  width: 200Px !important;
}

/deep/ .van-tabs__wrap {
  width: 250Px;
}


@media screen and (max-width: 500Px) {
  .merchantSettled {
    width: 100%;

    .merchantSettled-wap {
      background: #fff;
      display: flex;
      justify-content: center;
      align-items: center;
      width: 100% !important;

      .step-div {
        width: 100%;
        background: #fff;

        border-radius: 4Px;
        margin-top: -86Px;

        .content {
          padding: 20Px 30Px;
          border: 1Px solid #eeeeee;

          .title p {
            font-family: "PingFang HK";
            font-style: normal;
            font-size: 14Px;
            line-height: 20Px;
            color: #333333;
            padding: 6Px 0;
          }
        }

        // .content2 {
        //   // padding: 20Px 10Px;
        // }

        .bottom {
          height: 100Px;
          font-size: 12Px;
          display: flex;
          flex-direction: column;
          justify-content: space-around;
          align-items: center;
          margin: 20Px 0;

          .button {
            width: 80%;
          }
        }
      }
    }
  }
}

.demo-ruleForm {
  .uploder-wrap {
    display: flex;
    align-items: center;

    .tips {
      font-size: 12Px;
      color: #999999;

      span {
        color: var(--main-color);
      }
    }
  }

  .uploder-center {
    display: flex;

    .uploder-two-wrap {
      margin-right: 30Px;

      .tips {
        color: #333333;
        font-size: 12Px;
        text-align: center;
      }
    }
  }

  .correct-warp {
    display: flex;

    img {
      width: 100Px;
      margin-right: 20Px;
    }
  }

  .tab-wrap {
    display: flex;
    margin-top: 20Px;

    .tab-item {
      width: 98Px;
      height: 34Px;
      background: #EEEEEE;
      border-radius: 4Px;
      text-align: center;
      cursor: pointer;
      line-height: 34Px;
      margin-right: 20Px;
      color: #333333;
      font-size: 14Px;
    }

    .active {
      color: #fff !important;
      background: var(--main-color) !important;
    }
  }

  .code-input {
    width: 420Px;
  }

  .code-wrap {
    width: 133Px;
    height: 34Px;
    background: var(--main-color);
    border-radius: 4Px;
    margin-top: 8Px;
    text-align: center;
    line-height: 34Px;
    font-size: 14Px;
    color: #fff;
    cursor: pointer;
  }

  .el-dropdown {
    width: 100%;
  }

  .prepend-wrap {
    display: flex;
    align-items: center;
    padding: 0 20Px;

    .phone_number {
      flex: 1;
    }
  }

  .phone_number_wrap {
    /deep/ .el-input__inner {
      width: 320Px;
    }

  }
}

.option-wrap {
  display: flex;
  align-items: center;
  font-size: 14Px;

  img {
    height: 30Px;
    margin-right: 5Px;
  }
}

.lang-item {
  display: flex;
  align-items: center;

  img {
    width: 20Px;
    height: 20Px;
    margin-right: 5px;
  }
}

/deep/ .el-form-item__label {
  text-align: left !important;
}

/deep/ .el-form-item {
  margin-top: 50Px;
}

/deep/ .el-select-dropdown__list {
  padding: 10Px 0 !important;
}

/deep/ .el-select .el-input .el-select__caret {
  font-size: 15Px;
  display: flex;
  align-items: center;
}

.el-select-dropdown__item.selected {
  color: var(--main-color) !important;
}

.el-select .el-input.is-focus .el-input__inner {
  padding-left: 30Px !important;
}

/deep/ .el-input__inner {
  height: 50Px !important;
  width: 420Px;
  font-size: 14Px;
  border: 1px solid #EEEEEE;

  &::placeholder {
    font-size: 14Px;
    color: #999999;
  }
}

/deep/ .van-uploader__upload-icon {
  font-size: 35Px !important;
  color: #AAAAAA !important;
}

/deep/.el-input-group__prepend {
  width: 100Px !important;
  padding: 0 !important;
  background: none !important;
  font-size: 14Px;
}

@media screen and (max-width: 500Px) {
  /deep/ .el-input__inner {
    width: 100% !important;
  }

  /deep/ .el-select {
    width: 100%;
  }

  .phone_number_wrap {
    /deep/ .el-input__inner {
      width: 100% !important;
    }

  }

  .demo-ruleForm .code-input {
    width: 100%;
  }

  .correct-warp {
    img {
      display: block;
      margin-top: 20Px;
      margin-right: 10Px !important;
    }
  }
}

/deep/ .van-checkbox__icon--checked .van-icon {
  background-color: var(--main-color) !important;
  border-color: var(--main-color) !important;
}

/deep/ .el-input.is-disabled .el-input__inner {
  background-color: #fff;
}
</style>
