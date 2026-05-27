<template>
  <div class="merchandise">
    <SetBootSteps/>
    <el-form :label-width="columnWidth">
      <el-card>
        <!--        <FormatNumberShow :data="1.21770005" style="color:#67C23A" :decimalPlaces="6"/>-->
        <div class="info">
          <p class="title mb-29">{{ $t('基础信息') }}</p>
          <div class="info-m">
            <el-form-item :label="$t('店铺名称')">
              <el-input v-model="paramsData.basicInfo.shopName" :placeholder="$t('请输入店铺名称')"
                        :class="$store.getters.currentLanguage==='en'?'':'active'"
                        @blur="updateMerchantInfo"></el-input>
            </el-form-item>
            <el-form-item :label="$t('店铺LOGO')">
              <!-- <Upload class="avatar-uploader" v-model="paramsData.basicInfo.avatar" moduleName="avatar" :width="90"
                      :height="90" :fixedNumber="[1,1]" @success="updateMerchantInfo" :cropper="0"/> -->
              <van-uploader v-model="logoImg" :after-read="afterReadLogo"
                            :max-count="1"
                            :readonly="false" preview-size="105px"/>
            </el-form-item>
            <el-form-item :label="$t('联系人')">
              <el-input v-model="paramsData.basicInfo.shopUserName" :placeholder="$t('请输入联系人姓名')"
                        :class="$store.getters.currentLanguage==='en'?'':'active'"
                        @blur="updateMerchantInfo"></el-input>

            </el-form-item>
            <el-form-item :label="$t('店铺电话')">
              <el-input v-model="paramsData.basicInfo.shopPhone" :placeholder="$t('请输入店铺电话')"
                        :class="$store.getters.currentLanguage==='en'?'':'active'"
                        @blur="updateMerchantInfo"></el-input>
            </el-form-item>
            <el-form-item :label="$t('店铺简介')">
              <el-input maxlength="200" v-model="paramsData.basicInfo.shopIntr" :disabled="false"
                        :placeholder="$t('请输入店铺简介')"
                        class="desc" type="textarea"
                        :class="$store.getters.currentLanguage==='en'?'el-input':'el-input active'"
                        @blur="updateMerchantInfo">
              </el-input>
              <div :style="'padding-left:'+columnWidth" class="introduce">
                {{ $t("最多200字") }}
              </div>
            </el-form-item>
            <el-form-item :label="$t('进店欢迎语')">
              <el-input maxlength="200" v-model="paramsData.basicInfo.imInitMessage" :disabled="false"
                        :placeholder="$t('请输入进店欢迎语')"
                        class="desc" type="textarea"
                        :class="$store.getters.currentLanguage==='en'?'el-input':'el-input active'"
                        @blur="updateMerchantInfo">
              </el-input>
              <div :style="'padding-left:'+columnWidth" class="introduce">
                {{ $t("最多200字") }}
              </div>
            </el-form-item>
          </div>
        </div>
      </el-card>
      <el-card>
        <div class="info">
          <p class="title mb-29">{{ $t('横幅设置') }}</p>
          <div class="banner-settings">
            <div>
              <p class="mb-15 font-14 font-400 text-black mb-4">{{ $t('店铺横幅') }} 1(1920x300)</p>
              <Upload class="banner-uploader" v-model="banner1" moduleName="banner1" :width="960" :height="150"
                      :addText="$t('添加图片')"
                      @success="updateMerchantInfo"/>
            </div>
            <div>
              <p class="mb-15 font-14 font-400 text-black mb-4">{{ $t('店铺横幅') }} 2(1920x300)</p>
              <Upload class="banner-uploader" v-model="banner2" moduleName="banner1" :width="960" :height="150"
                      :addText="$t('添加图片')"
                      @success="updateMerchantInfo"/>
            </div>
            <div>
              <p class="mb-15 font-14 font-400 text-black mb-4">{{ $t('店铺横幅') }} 3(1920x300)</p>
              <Upload class="banner-uploader" v-model="banner3" moduleName="banner1" :width="960" :height="150"
                      :addText="$t('添加图片')"
                      @success="updateMerchantInfo"/>
            </div>
          </div>
        </div>
      </el-card>
      <el-card v-if="!hideContact">
        <div class="info">
          <p class="title mb-30">{{ $t('社交媒体') }}</p>
          <div class="info-m ">
            <el-form-item label="Facebook">
              <el-input v-model="paramsData.sociality.Facebook" :placeholder="$t('使用https插入链接')"
                        @blur="updateMerchantInfo($event)"></el-input>
            </el-form-item>
            <el-form-item label="Twitter">
              <el-input v-model="paramsData.sociality.Twitter" :placeholder="$t('使用https插入链接')"
                        @blur="updateMerchantInfo($event)"></el-input>
            </el-form-item>
            <el-form-item label="Google">
              <el-input v-model="paramsData.sociality.Google" :placeholder="$t('使用https插入链接')"
                        @blur="updateMerchantInfo($event)"></el-input>
            </el-form-item>
            <el-form-item label="YouTube">
              <el-input v-model="paramsData.sociality.YouTube" :placeholder="$t('使用https插入链接')"
                        @blur="updateMerchantInfo($event)"></el-input>
            </el-form-item>
            <el-form-item label="Instagram">
              <el-input v-model="paramsData.sociality.Instagram" :placeholder="$t('使用https插入链接')"
                        @blur="updateMerchantInfo($event)"></el-input>
            </el-form-item>
          </div>
        </div>
      </el-card>
      <el-card>
        <div class="info">
          <p class="title mb-30">{{ $t('个人信息') }}</p>
          <div class="info-m">
            <el-form-item :label="$t('头像')">
              <div>
                <el-image :src="avatar||require('@/assets/images/avatar.png')" alt="" class="w-64 h-64 ml-10 mr-6"
                          style="border-radius: 50%;position: relative;top: -12px;"/>
                <span class="cursor-pointer" style="margin-left: 10px; color: #0066ff;position: relative;top: -36px;"
                      @click="updateAvatar">{{ $t('修改') }}</span>
              </div>
            </el-form-item>
            <el-form-item :label="$t('姓名')">
              <div style="display: flex;">
                <div class="kyc-content">
                  <span style="margin-left: 10px">{{ kyc_get.name }}</span>
                  <div class="certification-status">
                    <div v-if="kyc_get.status <= 1">
                      <el-image :src="require('@/assets/images/waiting.png')" alt=""/>
                      <div class="waiting">{{ $t('待认证') }}</div>
                    </div>
                    <div v-else-if="kyc_get.status === 2">
                      <el-image :src="require('@/assets/images/success.png')" alt=""/>
                      <div class="success">{{ $t('认证通过') }}</div>
                    </div>
                    <div v-else>
                      <el-image :src="require('@/assets/images/fail.png')" alt=""/>
                      <div class="fail">{{ $t('认证失败') }}</div>
                    </div>
                  </div>
                </div>
                <span class="cursor-pointer"
                      style="margin-left: 10px; color: #0066ff" @click="handleCommand()">{{ $t('查看') }}</span>
              </div>
            </el-form-item>
            <el-form-item :label="$t('手机号')" v-if="!['FamilyMart'].includes(projectTitle)">
              <div style="display: flex;">
                <div class="kyc-content">
                  <span style="margin-left: 10px">{{ info_data.phone | formatPhone }}</span>
                  <div class="certification-status">
                    <div v-if="!info_data.phone">
                      <el-image :src="require('@/assets/images/fail.png')" alt=""/>
                      <div class="fail">{{ $t('未设置') }}</div>
                    </div>
                    <template v-else>
                      <div v-if="!userInfo.phoneverif&&info_data.phone !== null">
                        <el-image :src="require('@/assets/images/waiting.png')" alt=""/>
                        <div class="waiting">{{ $t('待认证') }}</div>
                      </div>
                      <div v-if="userInfo.phoneverif&&info_data.phone !== null">
                        <el-image :src="require('@/assets/images/success.png')" alt=""/>
                        <div class="success">{{ $t('已认证') }}</div>
                      </div>
                    </template>
                  </div>
                </div>
                <template>
                  <span v-if="!userInfo.phoneverif&&info_data.phone != null" class="cursor-pointer"
                        style="margin-left: 10px; color: #0066ff"
                        @click="changeInfo(4)">{{ $t('认证手机号') }}</span>
                  <span v-if="info_data.phone == null"
                        class="cursor-pointer"
                        style="margin-left: 10px; color: #0066ff" @click="changeInfo(1)">{{
                      $t('设置')
                    }}</span>
                  <span v-if="userInfo.phoneverif&&info_data.phone != null" class="cursor-pointer"
                        style="margin-left: 10px; color: #0066ff"
                        @click="changeInfo(1)">{{ $t('修改') }}</span>
                </template>
              </div>
            </el-form-item>
            <el-form-item :label="$t('邮箱')" v-if="!['FamilyMart'].includes(projectTitle)">
              <div style="display: flex;">
                <div class="kyc-content">
                  <span style="margin-left: 10px">{{ info_data.email | formatEmail }}</span>
                  <div class="certification-status">
                    <div v-if="!info_data.email">
                      <el-image :src="require('@/assets/images/fail.png')" alt=""/>
                      <div class="fail">{{ $t('未设置') }}</div>
                    </div>
                    <template v-else>
                      <div v-if="!userInfo.emailverif">
                        <el-image :src="require('@/assets/images/waiting.png')" alt=""/>
                        <div class="waiting">{{ $t('待认证') }}</div>
                      </div>
                      <div v-if="userInfo.emailverif">
                        <el-image :src="require('@/assets/images/success.png')" alt=""/>
                        <div class="success">{{ $t('已认证') }}</div>
                      </div>
                    </template>
                  </div>
                </div>
                <template>
                  <span v-if="!userInfo.emailverif&&info_data.email != null" class="cursor-pointer"
                        style="margin-left: 10px; color: #0066ff"
                        @click="changeInfo(4)">{{ $t('认证邮箱') }}</span>
                  <span v-if="info_data.email == null"
                        class="cursor-pointer"
                        style="margin-left: 10px; color: #0066ff" @click="changeInfo(2)">{{ $t('设置') }}</span>
                  <span v-if="userInfo.emailverif&&info_data.email != null" class="cursor-pointer"
                        style="margin-left: 10px; color: #0066ff"
                        @click="changeInfo(2)">{{ $t('修改') }}</span>
                </template>
              </div>
            </el-form-item>
            <el-form-item :label="$t('资金密码')" v-if="!defaultSettings.hideUpdatePayPassword">
              <span class="cursor-pointer" style="color: #0066ff;margin-left: 10px" @click="changePass('修改资金密码')">{{
                  $t('修改')
                }}</span>
            </el-form-item>
            <el-form-item :label="$t('登录密码')" v-if="!defaultSettings.hideUpdateLoginPassword">
              <span class="cursor-pointer" style="color: #0066ff;margin-left: 10px"
                    @click="changeLoginPassWord">{{ $t('修改') }}</span>
            </el-form-item>
            <el-form-item :label="$t('注销账号')" v-if="['Argos','Argos2','GreenMall'].includes(projectTitle)">
              <span class="cursor-pointer" style="color: #999999;margin-left: 10px"
                    @click="destroyAccount">{{ $t('立即注销') }}</span>
            </el-form-item>
            <el-form-item :label="$t('电子合同')" v-if="sellerSign">
              <span class="cursor-pointer" style="color: #0066ff;margin-left: 10px"
                    @click="pdfCheck">{{ $t('查看') }}</span>
            </el-form-item>
          </div>
        </div>
      </el-card>
    </el-form>
    <!--  修改资金密码/修改密码  -->
    <el-dialog :title="passTitle" :visible.sync="passVisible" width="450px">
      <div class="dia-main">
        <el-form>
          <el-form-item>
            <p class="font-12 font-400" style="color:#333;">{{ $t('新密码') }}</p>
            <!--            <el-input v-model="it2.input2" :placeholder="$t('请输入6位数数字密码')" clearable-->
            <!--                      maxlength="6" oninput="value=value.replace(/[^\d]/g,'')"/>-->
            <PasswordInput @clear="it2.input2=''"
                           oninput="this.value!=undefined&&(this.value=this.value.replace(/[^\d]/g,''))"
                           v-model="it2.input2" :placeholder="$t('请输入6位数数字密码')" maxlength="6"/>
          </el-form-item>
          <el-form-item>
            <p class="font-12 font-400" style="color:#333;">{{ $t('新密码') }}</p>
            <PasswordInput @clear="it2.input3=''"
                           oninput="this.value!=undefined&&(this.value=this.value.replace(/[^\d]/g,''))"
                           v-model="it2.input3" :placeholder="$t('请输入6位数数字密码')" maxlength="6"/>
            <!--            <el-input v-model="it2.input3" :placeholder="$t('请再次输入6位数数字密码')"-->
            <!--                      clearable maxlength="6" oninput="value=value.replace(/[^\d]/g,'')"/>-->
          </el-form-item>
        </el-form>
      </div>
      <el-button class="w-full h-44" type="primary" @click="biaodantijiao4">{{ $t('提交') }}</el-button>
    </el-dialog>
    <!--  修改资金密码/修改密码  -->
    <el-dialog :title="passTitle" :visible.sync="passVisible3" width="450px">
      <div class="dia-main">
        <el-form>
          <el-form-item>
            <p class="font-12 font-400" style="color:#333;">{{ $t('旧密码') }}</p>
            <PasswordInput @clear="it3.input1=''"
                           oninput="this.value!=undefined&&(this.value=this.value.replace(/[^\d]/g,''))"
                           v-model="it3.input1" :placeholder="$t('请输入6位数数字密码')" maxlength="6"/>
          </el-form-item>
          <el-form-item>
            <p class="font-12 font-400" style="color:#333;">{{ $t('新密码') }}</p>
            <PasswordInput v-model="it3.input2" :placeholder="$t('请输入6位数数字密码')"
                           maxlength="6"
                           @clear="it3.input2=''"
                           oninput="this.value!=undefined&&(this.value=this.value.replace(/[^\d]/g,''))"/>
          </el-form-item>
          <el-form-item>
            <p class="font-12 font-400" style="color:#333;">{{ $t('新密码') }}</p>
            <PasswordInput v-model="it3.input3" :placeholder="$t('请输入6位数数字密码')"
                           maxlength="6"
                           @clear="it3.input3=''"
                           oninput="this.value!=undefined&&(this.value=this.value.replace(/[^\d]/g,''))"/>
          </el-form-item>
        </el-form>
      </div>
      <el-button class="w-full h-44" type="primary" @click="biaodantijiao5">{{ $t('提交') }}</el-button>
    </el-dialog>
    <!--  修改登录密码  -->
    <el-dialog :title="$t('修改登录密码')" :visible.sync="passVisible2" width="450px">

      <div class="dia-main">
        <el-form>
          <el-form-item>
            <p class="font-12 font-400" style="color:#333;">{{ $t('原密码') }}</p>
            <PasswordInput v-model="it.input1"
                           @clear="it.input1=''"
                           :placeholder="$t('请输入6位数数字密码')"
                           maxlength="16"/>
          </el-form-item>
          <el-form-item>
            <p class="font-12 font-400" style="color:#333;">{{ $t('新密码') }}</p>
            <!--            <el-input :placeholder="$t('请输入新密码')" v-model="it.input2" clearable maxlength="16"></el-input>-->
            <PasswordInput v-model="it.input2" :placeholder="$t('新密码')"
                           @clear="it.input2=''"
                           maxlength="16"/>
          </el-form-item>
          <el-form-item>
            <p class="font-12 font-400" style="color:#333;">{{ $t('新密码') }}</p>
            <PasswordInput v-model="it.input3" :placeholder="$t('再次输入新密码')"
                           @clear="it.input3=''"
                           maxlength="16"/>
          </el-form-item>
        </el-form>
      </div>
      <el-button class="w-full h-44" type="primary" @click="biaodantijiao3">{{ $t('提交') }}</el-button>
    </el-dialog>
    <!--  修改手机/邮箱  -->
    <UpdateIphoneOrEmail ref="updateIphoneOrEmail" @getMerchantInfo="getMerchantInfo" @infoPost="info_post"/>
    <!--  身份认证  -->
    <el-dialog :title="$t('身份认证')" :visible.sync="userVisible" width="485px">
      <div class="dia-main">
        <el-form>
          <el-form-item>
            <div class="sf">
              <div v-if="kyc_get.status <= 1">
                <el-image :src="require('@/assets/images/waiting.png')" alt=""/>
                <div class="waiting">{{ $t('待认证') }}</div>
              </div>
              <div v-else-if="kyc_get.status === 2">
                <el-image :src="require('@/assets/images/success.png')" alt=""/>
                <div class="success">{{ $t('认证通过') }}</div>
              </div>
              <div v-else-if="kyc_get.status === 3">
                <el-image :src="require('@/assets/images/fail.png')" alt=""/>
                <div class="fail">{{ $t('认证失败') }}</div>
              </div>
            </div>
          </el-form-item>
          <el-form-item>
            <p class="mb-6 text-black">{{ $t('国籍') }}</p>
            <el-select v-model="kycForm.nationality" :popper-append-to-body="false"
                       :disabled="kyc_get.status==3||kyc_get.status==0?false:true"
                       :placeholder="$t('请选择国籍')" filterable>
              <el-option v-for="(item,index) in countryList" :key="index"
                         :label="$t(item.countryName)"
                         :value="item.id"></el-option>
            </el-select>
          </el-form-item>
          <el-form-item>
            <p class="mb-6 text-black">{{ $t('真实姓名') }}</p>
            <!--            <el-input placeholder="请填写真实姓名"/>-->
            <el-input v-model="kycForm.name" :disabled="kyc_get.status==3||kyc_get.status==0?false:true"
                      :placeholder="$t('请输入真实姓名')"
                      clearable maxlength="20"/>
          </el-form-item>
          <el-form-item>
            <p class="mb-6 text-black"><span>{{ $t('证件') }}</span>/<span>{{ $t('护照号码') }}</span></p>
            <!--            <el-input placeholder="请填写证件/护照号码"/>-->
            <el-input v-model="kycForm.idnumber" :disabled="kyc_get.status==3||kyc_get.status==0?false:true"
                      :placeholder="$t('请输入您的证件/护照号码')"
                      clearable maxlength="40"/>
          </el-form-item>
          <el-form-item v-if="kycForm.status !==2">
            <p class="mb-6 text-black"><span>{{ $t('证件照') }}</span>/<span>{{ $t('护照上传') }}</span></p>
            <div class="shangchaun">
              <div class="c1">
                <van-uploader v-model="kycForm.idimg_1" :after-read="afterRead21"
                              :deletable="kyc_get.status!=3&&kyc_get.status!=0?false:true" :max-count="1"
                              :readonly="!(kyc_get.status==3||kyc_get.status==0?true:false)" preview-size="105px"/>
                <div>{{ $t('证件正面') }}</div>
              </div>
              <div class="c1">
                <van-uploader v-model="kycForm.idimg_2" :after-read="afterRead22"
                              :deletable="kyc_get.status!=3&&kyc_get.status!=0?false:true" :max-count="1"
                              :readonly="!(kyc_get.status==3||kyc_get.status==0?true:false)" preview-size="105px"/>
                <div>{{ $t('证件反面') }}</div>
              </div>
              <div class="c1" v-if="!hideCertificationPhoto">
                <van-uploader v-model="kycForm.idimg_3" :after-read="afterRead23"
                              :deletable="kyc_get.status!=3&&kyc_get.status!=0?false:true" :max-count="1"
                              :readonly="!(kyc_get.status==3||kyc_get.status==0?true:false)" preview-size="105px">
                </van-uploader>
                <div>{{ $t('手持证件照') }}</div>
              </div>
            </div>
            <div v-if="kyc_get.status==3||kyc_get.status==0" class="t1">{{ $t('拍摄示例') }}</div>
            <div v-if="kyc_get.status==3||kyc_get.status==0" class="shangchaun">
              <div class="c1" style="margin-right: 8px">
                <img class="c1-a-img" :src="require('@/assets/image/auth/01.png')"/>
              </div>
              <div class="c1" style="margin-right: 8px">
                <img class="c1-a-img" :src="require('@/assets/image/auth/02.png')"/>
              </div>
              <div class="c1" v-if="!hideCertificationPhoto">
                <img class="c1-a-img" :src="require('@/assets/image/auth/03.png')"/>
              </div>
            </div>
          </el-form-item>
        </el-form>
      </div>
      <div v-if="kyc_get.status==3||kyc_get.status==0"
           class="flex justify-center items-center h-44 mt-30 rounded text-white font-16"
           style="background: #1552F0;cursor: pointer;" @click="renzzheng">{{
          kyc_get.status == 0 ? $t('提交申请') : $t('重新申请')
        }}
      </div>
    </el-dialog>
    <!--  头像选择  -->
    <el-dialog :title="$t('头像选择')" :visible.sync="showUpdateAvatar" width="485px">
      <div class="update-avatar">
        <div v-for="(item,index) in 20">
          <div class="update-avatar-item"
               @click="userInfo.avatar=(index+1)">
            <el-image class="avatar-image" :src="require(`@/assets/avatar/${index+1}.png`)" alt=""/>
            <el-image class="update-avatar-true" :class="{'update-avatar-true-active':userInfo.avatar==(index+1)}"
                      :src="require(`@/assets/avatar/true.png`)" alt=""/>
          </div>
        </div>
      </div>
      <div
          class="flex justify-center items-center h-44 mt-30 rounded text-white font-16"
          style="background: #1552F0;cursor: pointer;" @click="updateAvatarSubmit">{{ $t('确认') }}
      </div>
    </el-dialog>
    <ShowPdf @closePdf="closePdf" v-if="sellerSign&&showPdfView"/>
  </div>
</template>

<script>
import {
  getCountryList,
  getInfo,
  getSysParaContract,
  imageUpload,
  kyc_apply_action_post,
  seller_info_action_post,
  shezhi_zijinmima_post,
  shifoushezhi_zijinmima_post,
  updateMerchantInfo,
  xiugai_denglumima_post,
  xiugai_touxiang_post,
  xiugai_zijinmima_post
} from "@/api/user";
import 'vant/lib/uploader/style'
import {Uploader} from "vant";
import Toast from "@/utils/toast";
import {_getIdentify} from "@/api/fund.api";
import {mapActions, mapGetters} from "vuex";
import PasswordInput from "@/components/PasswordInput";
import countryList from "@/utils/country";
import Upload from "@/components/Upload";
import UpdateIphoneOrEmail from "@/views/other/updateIphoneOrEmail";
import defaultSettings from "@/settings";
import ShowPdf from "@/components/Pact/showPdf.vue";
import FormatNumberShow from "@/components/FormatNumberShow/index.vue";
import request from "@/utils/request";

const setting = require("@/settings");
export default {
  name: "shopSetting",
  components: {
    FormatNumberShow,
    [Uploader.name]: Uploader, PasswordInput, Upload, UpdateIphoneOrEmail, ShowPdf
  },
  filters: {
    formatPhone(value) {
      if (value) {
        // 带国际区号的手机号脱敏
        let index = value.indexOf(' ');
        return value.substring(0, index + 1) + value.substring(index, index + 4) + '****' + value.substring(value.length - 2, value.length);
      }
    },
    formatEmail(value) {
      if (value) {
        return value.replace(/(\w{1})\w{1,}(\w{1})/, '$1****$2')
      }
    }
  },
  data() {
    return {
      defaultSettings,
      projectTitle: defaultSettings.projectTitle,
      showUpdateAvatar: false,
      activeAddress: setting.countryCode,
      hideContact: setting.hideContact,
      hideCertificationPhoto: setting.hideCertificationPhoto,
      searchCountry: '',
      countryList: [],
      banner1: '', // banner
      banner2: '', // banner
      banner3: '', // banner
      fileList1: [], // 证件照正面
      fileList2: [], // 证件照反面
      oldPasswd: '',
      newPasswd: '',
      repateNewPasswd: '',
      startValue: '86',
      editPhone: {
        phone: '',
        code: '',
        password: ''
      },
      editEmail: {
        email: '',
        code: '',
        password: ''
      },
      startOptions: [
        {
          value: '86',
          label: '+86'
        }
      ],
      value: 'Canada',
      options: [
        {
          value: 'Canada',
          label: this.$t('加拿大')
        }
      ],
      passVisible: false,
      passVisible2: false,
      passVisible3: false,
      passTitle: '',
      userVisible: false,
      editTitle: '',
      editVisible: false,
      paramsData: {
        basicInfo: {
          avatar: '',
          shopName: '',
          shopLogo: '',
          shopUserName: '',
          shopPhone: '',
          shopAddress: '',
          shopIntr: '',
          imInitMessage: '',
        },
        sociality: {
          Facebook: '',
          Instagram: '',
          Twitter: '',
          Google: '',
          YouTube: ''
        },
        user: {
          name: '',
          phone: '',
          email: '',
        }
      },
      imageUrl: '',
      dialogImageUrl: '',
      dialogVisible: false,
      disabled: false,
      //个人信息
      info_data: {},
      kyc_get: {},
      kycForm: {
        nationality: '',
        name: '',
        idnumber: '',
        idimg_1: [],
        idimg_2: [],
        idimg_3: []
      },
      countryName: this.$t("请选择国家"),
      countryCode: '',
      status: '', // 0
      shangchuanurl: '',
      shangchuanurl2: '',
      shangchuanurl3: '',
      logoImg: [],
      //绑定手机号
      //登录密码
      it: {
        input1: '',
        input2: '',
        input3: ''
      },
      it2: {
        input1: '',
        input2: '',
        input3: ''
      },
      it3: {
        input1: '',
        input2: '',
        input3: ''
      },
      showPdfView: false,
      sellerSign: false,//否启用电子合同true开启，false关闭
    };
  },
  computed: {
    ...mapGetters(["avatar", 'userInfo']),
    columnWidth() {
      let width = 120;
      switch (this.$i18n.locale) {
        case 'en':
          width = 180;
          break;
        case 'cn':
          width = 90;
          break;
        case 'tw':
          width = 90;
          break;
        case 'de':
          width = 160;
          break;
        case 'fr':
          width = 200;
          break;
        case 'ja':
          width = 160;
          break;
        case 'ko':
          width = 170;
          break;
        case 'ms':
          width = 180;
          break;
        case 'th':
          width = 160;
          break;
        case 'pt':
          width = 180;
          break;
        case 'es':
          width = 220;
          break;
        case 'ru':
          width = 220;
          break;
        case 'el':
          width = 220;
          break;
        case 'it':
          width = 180;
          break;
        case 'tr':
          width = 180;
          break;
        case 'af':
          width = 180;
          break;
        case 'ph':
          width = 220;
          break;
        case 'ar':
          width = 160;
          break;
        case 'vi':
          width = 250;
          break;
        case 'id':
          width = 250;
          break;
        case 'hi':
          width = 180;
          break;
      }
      return width + 'px';
    },
  },
  mounted() {
    this.getCountryList()
    this.seller_info_action()
    this.getSysParaContract()
    //个人信息
    this.info_post()
    this.getMerchantInfo()
    if (localStorage.getItem("show_kyc") === '1') {
      localStorage.removeItem('show_kyc')
      setTimeout(() => {
        this.handleCommand()
      }, 1000)
    }
  },
  methods: {
    request,
    ...mapActions("user", ["getInfo"]),
    getSysParaContract() {
      getSysParaContract().then(res => {
        this.sellerSign = res.data.sellerSign === "true"
      })
    },
    closePdf() {
      this.showPdfView = false
      document.body.style.overflow = 'auto'; // 出现滚动条
    },
    pdfCheck() {
      this.showPdfView = true
      document.body.style.overflow = 'hidden'; // 禁止滚动
    },
    destroyAccount() {
      this.$router.push({path: '/other/destroyAccount'})
    },
    getCountryList() {
      getCountryList().then(res => {
        this.countryList = res.data.data
        this.countryList.forEach(item => {
          item.label = item.countryName
          item.id = item.id
          item.value = item.id
        })
      }).catch(err => {
        console.log(err)
        countryList.forEach(item => {
          item.countryName = item.en
          item.id = item.id
        })
        this.countryList = countryList
      })
    },
    updateAvatar() {
      this.showUpdateAvatar = true
    },
    updateAvatarSubmit() {
      this.showUpdateAvatar = false
      xiugai_touxiang_post({idx: this.userInfo.avatar}).then(res => {
        Toast.success(this.$t('修改成功'))
        this.getInfo()
      })
    },
    biaodantijiao5() {
      const t = this
      if (t.it3.input1 === '') {
        Toast(t.$t('请输入6位数数字原密码'));
        return
      }
      if (t.it3.input2 === '') {
        Toast(t.$t('请输入6位数数字新密码'));
        return
      }
      if (t.it3.input3 === '') {
        Toast(t.$t('请再次输入6位数数字新密码'));
        return
      }
      let data = {}
      data.old_safeword = t.it3.input1
      data.safeword = t.it3.input2
      data.re_safeword = t.it3.input3
      xiugai_zijinmima_post(data).then(res => {
        Toast.success(t.$t('修改成功'));
        this.getInfo()
        this.passVisible3 = false
      })
    },
    biaodantijiao4() {
      const t = this
      if (t.it2.input2 === '') {
        Toast(t.$t('请输入6位数数字密码'));
        return
      }
      if (t.it2.input3 === '') {
        Toast(t.$t('请再次输入6位数数字密码'));
        return
      }
      let data = {
        'safeword': t.it2.input2,
        're_safeword': t.it2.input3
      }
      shezhi_zijinmima_post(data).then(res => {
        Toast.success(t.$t('修改成功'));
        location.reload();
      })
    },
    //登录密码
    biaodantijiao3() {
      const t = this
      if (t.it.input1 === '') {
        Toast(t.$t('请输入原密码'));
        return
      }
      if (t.it.input2 === '') {
        Toast(t.$t('请输入新密码'));
        return
      }
      if (t.it.input3 === '') {
        Toast(t.$t('请再次输入新密码'));
        return
      }
      let data = {
        'old_password': t.it.input1,
        'password': t.it.input2,
        're_password': t.it.input3
      }
      xiugai_denglumima_post(data).then(res => {
        Toast.success(t.$t('修改成功'));
        location.reload();
        // this.$router.push('/Setting')
      })
    },
    afterReadLogo(file) {
      const that = this;
      Toast.loading({
        duration: 0,
        forbidClick: true,
        loadingType: "spinner",
        message: ""
      });
      const formData = new FormData();// 通过formdata上传
      formData.append('file', file.file);
      formData.append('moduleName', 'avatar')
      imageUpload(formData).then(res => {
        Toast.clear();
        that.paramsData.basicInfo.avatar = res.data;
        that.updateMerchantInfo();
      }).catch(function (err) {
        console.log(err)
        Toast.clear();
        Toast(this.$t('添加失败'));
        that.logoImg = [];
      })
    },
    //身份证证明
    afterRead21(file) {
      Toast.loading({
        duration: 0,
        forbidClick: true,
        loadingType: "spinner",
        message: ""
      });
      const formData = new FormData();// 通过formdata上传
      formData.append('file', file.file);
      formData.append('moduleName', '123')
      imageUpload(formData).then(res => {

        Toast.clear();
        this.shangchuanurl = res.data
        // this.kycForm.idimg_1 = [{
        //   url:res.data
        // }]
      }).catch(function (err) {
        console.log(err)
        Toast.clear();
        Toast(this.$t('添加失败'));
        this.kycForm.idimg_1 = []
      })
    },
    afterRead22(file) {
      Toast.loading({
        duration: 0,
        forbidClick: true,
        loadingType: "spinner",
        message: ""
      });
      const formData = new FormData();// 通过formdata上传
      formData.append('file', file.file);
      formData.append('moduleName', '123')
      imageUpload(formData).then(res => {

        Toast.clear();
        this.shangchuanurl2 = res.data
        // this.kycForm.idimg_2 = [{
        //   url:res.data
        // }]
      }).catch(function (err) {
        console.log(err)
        Toast.clear();
        Toast(this.$t('添加失败'));
        this.kycForm.idimg_2 = []
      })
    },
    afterRead23(file) {
      Toast.loading({
        duration: 0,
        forbidClick: true,
        loadingType: "spinner",
        message: ""
      });
      const formData = new FormData();// 通过formdata上传
      formData.append('file', file.file);
      formData.append('moduleName', '123')
      imageUpload(formData).then(res => {

        Toast.clear();
        this.shangchuanurl3 = res.data
        // this.kycForm.idimg_3 = [{
        //   url:res.data
        // }]
      }).catch(function (err) {
        console.log(err)
        Toast.clear();
        Toast(this.$t('添加失败'));
        this.kycForm.idimg_3 = []
      })
    },
    renzzheng() {
      const t = this
      if (!t.kycForm.nationality) {
        Toast(t.$t('请选择国籍'));
        return
      }
      if (!t.kycForm.name) {
        Toast(t.$t('请输入真实姓名'));
        return
      }
      // 证件/护照号码
      if (!t.kycForm.idnumber) {
        Toast(t.$t('请输入证件/护照号码'));
        return
      }
      if (t.kycForm.idimg_2.length == 0 || t.kycForm.idimg_1.length == 0 || (!this.hideCertificationPhoto && t.kycForm.idimg_3.length == 0)) {
        Toast(t.$t('请完善证件照片上传'));
        return
      }
      // const data = {
      //   ...t.kycForm,
      //   idname: `${'身份证'}`,
      //   idimg_1: t.kycForm.idimg_1[0].url,
      //   idimg_2: t.kycForm.idimg_2[0].url,
      //   idimg_3: t.kycForm.idimg_3[0].url,
      // }
      const data = {
        ...t.kycForm,
        idname: `${'身份证'}`,
        idimg_1: this.shangchuanurl || t.kycForm.idimg_1[0].url,
        idimg_2: this.shangchuanurl2 || t.kycForm.idimg_2[0].url,
        idimg_3: !this.hideCertificationPhoto ? (this.shangchuanurl3 || t.kycForm.idimg_3[0].url) : null,
      }
      kyc_apply_action_post(data).then(res => {
        // t.kyc_get_action()
        Toast.success(this.$t('提交成功'));
        this.getInfo()
        this.getMerchantInfo()
        this.userVisible = false
      })
    },
    // 获取到当前选中国家的code值
    getName(params) {
      this.countryName = params[0];
      this.countryCode = params[1];
    },
    // 获取商户信息
    getMerchantInfo(cb) {
      const t = this
      _getIdentify({}).then(res => {
        //status 1审核中 ，2 审核通过，3审核未通过
        t.kyc_get = res.data
        this.kycForm = res.data
        if (res.status === 3) {
          this.kycForm.idimg_1 = res.data.idimg_1_path ? [{url: res.data.idimg_1_path}] : [];
          this.kycForm.idimg_2 = res.data.idimg_2_path ? [{url: res.data.idimg_2_path}] : [];
          this.kycForm.idimg_3 = res.data.idimg_3_path ? [{url: res.data.idimg_3_path}] : [];
        } else {
          this.kycForm.idimg_1 = res.data.idimg_1_path ? [{url: res.data.idimg_1}] : [];
          this.kycForm.idimg_2 = res.data.idimg_2_path ? [{url: res.data.idimg_2}] : [];
          this.kycForm.idimg_3 = res.data.idimg_3_path ? [{url: res.data.idimg_3}] : [];
        }
        if (res.data.status === 2) {
          //屏蔽敏感信息
          this.kycForm.idnumber = this.hidePassportNumber(this.kycForm.idnumber);
          //屏蔽name
          this.kycForm.name = this.kycForm.name.substring(0, 1) + '**';
        }
        cb && cb()
      })
    },
    hidePassportNumber(passportNumber) {
      if (passportNumber.length <= 4) {
        return passportNumber; // 如果护照号码长度小于等于4，则不进行隐藏
      }
      let firstTwo = passportNumber.substring(0, 2); // 获取前两位
      let lastTwo = passportNumber.substring(passportNumber.length - 2); // 获取后两位
      let hiddenPart = '';
      for (let i = 0; i < passportNumber.length - 4; i++) {
        hiddenPart += '*'; // 生成与中间数字相同长度的星号
      }
      return firstTwo + hiddenPart + lastTwo;
    },
    info_post() {
      getInfo({}).then(res => {
        this.info_data = res.data
      })
    },
    isOverSize(file) {
      const maxSize = file.type === 'image/jpeg' ? 500 * 1024 : 1000 * 1024;
      return file.size >= maxSize;
    },
    updateMerchantInfo(e) {
      if (this.paramsData.basicInfo.shopName === '') {
        Toast(this.$t('请输入店铺名称'));
        return
      }
      const from = {
        name: this.paramsData.basicInfo.shopName,
        avatar: this.paramsData.basicInfo.avatar,
        contact: this.paramsData.basicInfo.shopUserName,
        shopPhone: this.paramsData.basicInfo.shopPhone,
        shopRemark: this.paramsData.basicInfo.shopIntr,
        imInitMessage: this.paramsData.basicInfo.imInitMessage,
        banner1: this.banner1,
        banner2: this.banner2,
        banner3: this.banner3,
        facebook: this.paramsData.sociality.Facebook,
        instagram: this.paramsData.sociality.Instagram,
        twitter: this.paramsData.sociality.Twitter,
        google: this.paramsData.sociality.Google,
        youtube: this.paramsData.sociality.YouTube,
      }
      updateMerchantInfo(from).then((res) => {
        this.$notify({
          title: this.$t('成功'),
          message: this.$t('设置成功'),
          type: 'success'
        });
        this.seller_info_action()
      })
    },
    handleChange(e, file, fileList) {
      // this.fileList.push({
      //   name: fileList.name,
      //   url: fileList.urls
      // })
    },
    initData() {
      //登录密码
      this.it = {
        input1: '',
        input2: '',
        input3: ''
      }
      this.it2 = {
        input1: '',
        input2: '',
        input3: ''
      }
      this.it3 = {
        input1: '',
        input2: '',
        input3: ''
      }
    },
    changePass(str) {
      const t = this
      this.initData()
      shifoushezhi_zijinmima_post().then(res => {
        if (res.data.safeword == 0) {
          this.passTitle = this.$t('设置资金密码')
          this.passVisible = true
        } else {
          this.passTitle = this.$t('重置资金密码')
          this.passVisible3 = true
        }
      })

    },
    changeLoginPassWord() {
      this.it = {
        input1: '',
        input2: '',
        input3: ''
      }
      this.passVisible2 = true
    },
    changeInfo(str) {
      switch (str) {
        case 1:
          this.$refs.updateIphoneOrEmail.changeEditTitle(this.$t('修改手机'), str)
          break;
        case 2:
          this.$refs.updateIphoneOrEmail.changeEditTitle(this.$t('修改邮箱'), str)
          break;
        case 3:
          this.$refs.updateIphoneOrEmail.changeEditTitle(this.$t('认证手机号'), str)
          break;
        case 4:
          this.$refs.updateIphoneOrEmail.changeEditTitle(this.$t('认证邮箱'), str)
          break;
      }
      this.$refs.updateIphoneOrEmail.changeDialog()
    },
    handleCommand() {
      this.getMerchantInfo()
      this.userVisible = true
      this.userProcess = this.kyc_get.status
    },
    handlePictureCardPreview(file) {
      this.dialogImageUrl = file.url;
      this.dialogVisible = true;
    },
    handleRemove(file, fileList) {
      console.log(file, fileList);
    },
    seller_info_action() {
      seller_info_action_post({}).then((res) => {
        // this.promotional = e.data
        this.paramsData.basicInfo.shopName = res.data.name
        if (res.data.avatar !== '') {
          this.paramsData.basicInfo.avatar = res.data.avatar
          this.logoImg = [{url: res.data.avatar}];
        }
        this.paramsData.basicInfo.shopUserName = res.data.contact
        this.paramsData.basicInfo.shopPhone = res.data.shopPhone
        this.paramsData.basicInfo.shopIntr = res.data.shopRemark
        this.paramsData.basicInfo.imInitMessage = res.data.imInitMessage
        this.banner3 = res.data.banner3
        this.banner2 = res.data.banner2
        this.banner1 = res.data.banner1
        this.paramsData.sociality.Facebook = res.data.facebook
        this.paramsData.sociality.Instagram = res.data.instagram
        this.paramsData.sociality.Twitter = res.data.twitter
        this.paramsData.sociality.Google = res.data.google
        this.paramsData.sociality.YouTube = res.data.youtube
        this.$store.commit('user/CHANGE_MERCHANT_INFO', res.data)
      })
    },
  }
}
</script>

<style lang="scss">
.update-avatar {
  display: flex;
  justify-content: flex-start;
  flex-wrap: wrap;
  margin-bottom: 20px;
  position: relative;

  .update-avatar-item {
    width: 64px;
    height: 64px;
    border: 1px solid #ebeef5;
    border-radius: 50%;
    margin-right: 20px;
    margin-bottom: 20px;
    cursor: pointer;
    position: relative;

    .update-avatar-true {
      width: 20px;
      height: 20px;
      position: absolute;
      right: 0;
      bottom: 0;
      opacity: 0;

      &.update-avatar-true-active {
        opacity: 1;
      }
    }

    .avatar-image {
      width: 100%;
      height: 100%;
      border-radius: 50%;
    }
  }

  .update-avatar-item:nth-child(5n) {
    margin-right: 0;
    border: 2px solid red;
  }

}

.c_phone-input-content {
  position: relative;

  .abs {
    position: absolute;
    z-index: 1;
    width: 112px;
    height: 34px;
    overflow: hidden;
    margin: 1px;

    .el-input__inner {
      border: none;
      padding-left: 24px;
    }
  }

  .login-input {
    margin-bottom: 24px;
    position: relative;
    // .input-icon {
    //   position: absolute;
    //   left: 4px;
    //   z-index: 10;
    //   top: 50%;
    //   transform: translateY(-50%);
    //   width: 20px;
    //   height: 20px;
    // }
  }

  .input-dropdown {
    position: absolute;
    left: 30px;
    z-index: 10;
    top: 50%;
    transform: translateY(-50%);
    width: 80px;
    height: 20px;
    display: flex;
    justify-content: center;
    align-items: center;
  }

  .input-icon {
    position: absolute;
    left: 4px;
    z-index: 10;
    top: 50%;
    transform: translateY(-50%);
    width: 20px;
    height: 20px;
  }

  .phone-input {
    > .el-input__inner {
      padding-left: 114px;
    }
  }
}
</style>
<style lang="scss" scoped>
.banner-settings {
  display: flex;
  justify-content: flex-start;
  flex-direction: column;
  max-width: 1075px;

  > div {
    width: 100%;
    margin-right: 20px;

    &:last-child {
      margin-right: 0;
    }
  }
}

.introduce {
  font-size: 12px;
}

@media screen and (max-width: 1220px) {
  .banner-settings {

    > div {
      margin-right: 0;
      margin-bottom: 20px;
    }
  }
}

::v-deep {
  .el-input-group__prepend {
    background-color: #fff;
    width: 80px;
  }
}

.el-select .el-input {
  width: 130px;
}

.el-input-group__prepend {
  background-color: #FFFFFF;
  border: none;
}

.certification-status {
  right: 0;
  top: 0;
  height: 36px;
  margin-left: 12px;
  display: flex;
  justify-content: flex-end;
  align-items: center;


  > div {
    display: flex;
    justify-content: flex-end;
    align-items: center;

    > .el-image {
      width: 22px;
      height: 22px;
      margin-right: 4px;
      display: flex;
      justify-content: center;
      align-items: center;
      border-radius: 50%;
      overflow: hidden;

      ::v-deep .el-image__inner {
        width: 30px;
        height: 30px;
      }
    }

    > div {
      font-family: 'Roboto';
      font-style: normal;
      font-weight: 400;
      font-size: 14px;
      line-height: 14px;

      &.success {
        color: #00C58E;
        text-align: center;
      }

      &.waiting {
        color: #F99746;
        text-align: center;
      }

      &.fail {
        color: #FF4D4F;
        text-align: center;
      }
    }
  }
}

.shangchaun {
  width: 100%;
  display: flex;
  justify-content: flex-start;

  .van-uploader {
    width: 105px;
  }

  .c1 {
    margin-top: 6px;
    width: 33.33%;
    display: flex;
    flex-direction: column;
    justify-content: flex-start;
    align-items: center;
    //height: 105px;
    font-style: normal;
    font-weight: 400;
    font-size: 12px;
    line-height: 14px;
    text-align: center;
    color: #999999;

    .c1-a-img {
      margin-bottom: 15px;
      width: 105px;
    }
  }
}

.avatar-uploader {
  width: 90px;
  height: 90px;
  margin-bottom: 20px;
}


.dia-main {
  //padding: 0 20px;

  .sf {
    display: flex;
    flex-direction: column;
    align-items: center;
    font-size: 16px;
    color: #000000;

    > div {
      display: flex;
      justify-content: center;
      align-items: center;
      flex-direction: column;
    }

    img {
      width: 50px;
      height: 50px;
    }

    .success {
      color: #00C58E;
      text-align: center;
    }

    .waiting {
      color: #F99746;
      text-align: center;
    }

    .fail {
      color: #FF4D4F;
      text-align: center;
    }
  }

  ::v-deep .el-select {
    width: 100%;
  }

  .btn {
    width: 100%;
    height: 60px;
    line-height: 60px;
    text-align: center;
    background: #000;
    color: #fff;
  }
}

.posi-ab {
  position: absolute;
  right: 10px;
  top: 50%;
  transform: translateY(-50%);
}

::v-deep .el-form-item__content {
  position: relative;
}

::v-deep .avatar-uploader-icon {
  font-size: 28px;
  color: #8c939d;
  width: 100%;
  height: 148px;
  line-height: 148px;
  text-align: center;
}

::v-deep .avatar {
  width: 100%;
  height: 213px;
  display: block;
}

.merchandise {
  background-color: #f0f2f5;
  padding: 20px;
  // height: 100%;
  .main {
    .info {
      border-radius: 10px;
      padding: 20px;
      background-color: #fff;
      //border: 1px solid rgba(215, 215, 215, 1);
      margin-bottom: 20px;

      &:last-child {
        margin-bottom: 0;
      }

      .title {
        color: #000;
        font-weight: 600;
        font-size: 16px;
        //border-bottom: 1px solid rgba(215, 215, 215, 1);
      }
    }
  }
}

::v-deep {

  .el-select-dropdown {
    position: absolute !important;
    z-index: 9999 !important;
  }

  .el-form-item__label {
    color: #000;
    font-size: 14px;
    font-weight: 400;
  }

  .info {
    .desc.el-textarea {
      width: 630px;

      &.active {
        width: 690px;
      }
    }

    .el-input {
      width: 630px;

      &.active {
        width: 690px;
      }

      input {
        width: 100%;
      }
    }
  }

  .el-input {

    input {
      width: 100%;
    }
  }

  .desc.el-textarea {
    width: 600px;

    textarea {
      width: 100%;
      height: 156px;
      resize: none;
    }
  }

  .el-textarea__inner, .el-input__inner {
    padding-left: 10px;

    &:disabled {
      color: #333333;
    }
  }

  .el-form-item__content {
    margin-left: 0 !important;
  }

  .banner-uploader {
    width: 960px;
    height: 150px;
    margin-bottom: 20px;
  }

  .avatar-uploader {
    width: 90px;
    height: 90px;
  }

  .el-dialog {
    padding-bottom: 33px;
    border-radius: 10px;
  }

  .el-dialog__header {
    padding: 30px 30px 15px;
    font-size: 20px;
    font-weight: 600;
  }

  .el-dialog__body {
    padding: 0 30px;
  }

  .certification-uploader {
    .upload-img {
      width: 30px;
      height: 30px;
    }
  }

  //.change {
  //  .el-input__inner {
  //    border: none;
  //  }
  //}
}

.gray {
  color: #cccccc !important;
  cursor: pointer;
}

.project-dropdown {
  //设置高度才能显示出滚动条 !important
  height: 200px;
  overflow: auto;
  width: 390px;
  transform: translate(119px, 2px);
}

.kyc-content {
  width: 400px;
  border-radius: 4px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  height: 32px;
  border: solid 1px #cccccc;
  background-color: #f1f1f1;
  box-sizing: border-box;
  padding: 0 6px;
  margin-left: 6px;
}
</style>
