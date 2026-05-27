<template>
  <div class="merchantSettled" id="merchantSettled">
    <mer-chant-header id="product" url="true"></mer-chant-header>
    <div class="merchantSettled-wap">
      <div class="step-div">
        <!-- step1 -->
        <van-popup
          v-model="show"
          :close-on-click-overlay="false"
          get-container="body"
        >
          <div class="content popup_content">
            <div class="close-btn" @click="closeAgreement">
              <img src="@/assets/image/public/x-circle.png" alt="" />
            </div>
            <div class="tc_wrap" @scroll="handleScroll" v-if="!sellerSign">
              <div
                class="tc"
                ref="capture"
                id="originHtml"
                v-if="itemname !== 'Argos'"
              >
                <p class="title">{{ $t("rzInfo", { name: itemname }) }}</p>
                <!-- <p class="title">{{$t('capture_tit')}}</p> -->
                <p class="padding-tb">{{ $t("rzTitle1") }}</p>
                <!-- <p class="padding-tb">
                                    {{$t('capture_info')}}
                                </p> -->
                <!-- <p class="padding-tb"> {{$t('capture_info1')}}</p>
                                <p class="padding-tb"> {{$t('capture_info2')}}</p> -->
                <p>
                  {{ $t("rzTitle1info") }}
                  <!-- {{$t('capture_info3')}} -->
                </p>
                <p>
                  {{ $t("rzTitle1info1") }}
                  <!-- {{$t('capture_info4')}} -->
                </p>
                <!-- <p> {{$t('capture_info5')}}</p> -->
                <p>
                  {{ $t("rzTitle1info2") }}
                  <!-- {{$t('capture_info6')}} -->
                </p>
                <!-- <p>
                                     {{$t('capture_info7')}}
                                </p> -->
                <p class="padding-tb">{{ $t("rzTitle2") }}</p>
                <!-- <p class="padding-tb"> {{$t('capture_info8')}}</p> -->
                <p>
                  {{ $t("rzTitle2info", { name: itemname }) }}
                  <!-- {{$t('capture_info9')}} -->
                </p>
                <p>
                  {{ $t("rzTitle2info1") }}
                  <!-- {{$t('capture_info10')}} -->
                </p>
                <p>
                  {{ $t("rzTitle2info2") }}
                  <!-- {{$t('capture_info11')}} -->
                </p>
                <p>
                  {{ $t("rzTitle2info3") }}
                </p>
                <p class="padding-tb">{{ $t("rzTitle3") }}</p>
                <!-- <p class="padding-tb"> {{$t('capture_info12')}}</p> -->
                <p>
                  {{ $t("rzTitle3info") }}
                  <!-- {{$t('capture_info13')}} -->
                </p>
                <p>
                  {{ $t("rzTitle3info1") }}
                  <!-- {{$t('capture_info14')}} -->
                </p>
                <p>
                  {{ $t("rzTitle3info2") }}
                  <!-- {{$t('capture_info15')}} -->
                </p>
                <!-- <p> {{$t('capture_info16')}}</p> -->
                <p class="padding-tb">{{ $t("rzTitle4") }}</p>
                <p>
                  {{ $t("rzTitle4info") }}
                </p>
                <p>
                  {{ $t("rzTitle4info1") }}
                </p>
              </div>
              <div class="tc" v-else>
                <p class="title">{{ $t("capture_tit") }}</p>
                <p class="padding-tb">
                  {{ $t("capture_info") }}
                </p>
                <p class="padding-tb">{{ $t("capture_info1") }}</p>
                <p class="padding-tb">{{ $t("capture_info2") }}</p>
                <p>
                  {{ $t("capture_info3") }}
                </p>
                <p>
                  {{ $t("capture_info4") }}
                </p>
                <p>{{ $t("capture_info5") }}</p>
                <p>
                  {{ $t("capture_info6") }}
                </p>
                <p>
                  {{ $t("capture_info7") }}
                </p>
                <p class="padding-tb">{{ $t("capture_info8") }}</p>
                <p>
                  {{ $t("capture_info9") }}
                </p>
                <p>
                  {{ $t("capture_info10") }}
                </p>
                <p>
                  {{
                    $t("capture_info11", {
                      time: itemname == "Argos" ? "72" : 24,
                    })
                  }}
                </p>
                <p class="padding-tb">{{ $t("capture_info12") }}</p>
                <p>
                  {{ $t("capture_info13") }}
                </p>
                <p>
                  {{ $t("capture_info14") }}
                </p>
                <p>
                  {{ $t("capture_info15") }}
                </p>
                <p>{{ $t("capture_info16") }}</p>
                <p> {{ $t("argos_bottom") }}</p>
              </div>
            </div>
            <div class="tc_wrap" @scroll="handleScroll" v-else>
              <div class="tc" ref="capture" id="originHtml">
                <p class="title">{{ $t("capture_tit") }}</p>
                <p class="padding-tb">
                  {{ $t("capture_info") }}
                </p>
                <p class="padding-tb">{{ $t("capture_info1") }}</p>
                <p class="padding-tb">{{ $t("capture_info2") }}</p>
                <p>
                  {{ $t("capture_info3") }}
                </p>
                <p>
                  {{ $t("capture_info4") }}
                </p>
                <p>{{ $t("capture_info5") }}</p>
                <p>
                  {{ $t("capture_info6") }}
                </p>
                <p>
                  {{ $t("capture_info7") }}
                </p>
                <p class="padding-tb">{{ $t("capture_info8") }}</p>
                <p>
                  {{ $t("capture_info9") }}
                </p>
                <p>
                  {{ $t("capture_info10") }}
                </p>
                <p v-if="itemname !== 'AntMall'">
                  {{
                    $t("capture_info11", {
                      time:
                        itemname == "Argos"
                          ? "72"
                          : itemname == "AntMall" || itemname == "GreenMall"
                          ? "48"
                          : 24,
                    })
                  }}
                </p>
                <p v-else>
                  {{
                    $t(
                      "3.乙方需48小时内处理订单，否则将被扣除店铺信誉分，需重新缴纳保证金."
                    )
                  }}
                </p>
                <p class="padding-tb">{{ $t("capture_info12") }}</p>
                <p>
                  {{ $t("capture_info13") }}
                </p>
                <p>
                  {{ $t("capture_info14") }}
                </p>
                <p>
                  {{ $t("capture_info15") }}
                </p>
                <p>{{ $t("capture_info16") }}</p>
                <p v-if="itemname == 'Argos'"> {{ $t("argos_bottom") }}</p>
                <div class="esign-content">
                  <div>
                    <p class="padding-tb">
                      {{ $t("capture_info17") }} <span>{{ itemname }}</span>
                      <img src="@/assets/image/seal.png" />
                    </p>
                    <p class="padding-tb">
                      {{ $t("capture_info19") }}{{ now_date }}
                    </p>
                  </div>

                  <div class="right">
                    <p class="padding-tb">
                      {{ $t("capture_info18")
                      }}<img :src="resultImg" class="esign-img" />
                    </p>
                    <p class="padding-tb">
                      {{ $t("capture_info19") }}{{ now_date }}
                    </p>
                  </div>
                </div>
                <!-- </div> -->
              </div>
            </div>
            <van-popup
              v-model="visible"
              class="esign-container"
              :close-on-click-overlay="false"
              get-container="#app"
            >
              <vue-esign
                class="sign-view"
                ref="esign"
                :width="800"
                :height="300"
                :isCrop="isCrop"
                :lineWidth="lineWidth"
                :lineColor="lineColor"
                :bgColor.sync="bgColor"
              />
              <div class="btn-list">
                <div class="btn-left">
                  <van-button type="warning" @click="reset">{{
                    $t("重置")
                  }}</van-button>
                  <van-button type="warning" @click="goback">{{
                    $t("返回上一步")
                  }}</van-button>
                </div>
                <van-button type="primary" @click="save">{{
                  $t("确认")
                }}</van-button>
              </div>
            </van-popup>

            <div class="pop-bnt">
              <div @click="agreement" style="pointer-events: auto">
                <van-button
                  type="primary"
                  color="var(--color-main)"
                  class="button"
                  :class="scrollDisbled && 'van-button--disabled'"
                  :readonly="scrollDisbled"
                  v-if="sellerSign"
                  >{{ $t("同意并签名") }}</van-button
                >
              </div>
              <van-button
                type="primary"
                color="var(--color-main)"
                class="button"
                :disabled="scrollDisbled"
                @click="argeementEsign"
                >{{ $t("确认") }}</van-button
              >
            </div>
          </div>
        </van-popup>
        <!-- <div v-if="step == 1">

          <div class="bottom">
            <van-checkbox v-model="checked">
              {{ $t("我已经阅读并同意") }}
              <span class="color-yellow">{{ $t("入驻协议") }}</span>
            </van-checkbox>
            <van-button
              type="primary"
              color="var(--color-main)"
              class="button"
              @click="stepFun"
              >{{ $t("同意") }}</van-button
            >
          </div>
        </div> -->
        <!-- step2 -->
        <div v-if="step == 2">
          <van-swipe
            class="my-swipe"
            :autoplay="3000"
            indicator-color="white"
            v-if="itemname == 'INT Overstock' && !isPC"
          >
            <van-swipe-item v-for="(i, index) in h5img" :key="index">
              <van-Image :src="i" @click="ImgView(h5img)"></van-Image>
            </van-swipe-item>
          </van-swipe>
          <div class="content content2">
            <div class="banner" v-if="itemname == 'Argos'">
              <img src="@/assets/image/signal.jpg" alt="" />
            </div>
            <!-- <div class="banner" v-if="itemname == 'INT Overstock'">
                            <img src="@/assets/image/Int_1.jpg" alt="">
                        </div> -->
            <div class="banner" v-if="itemname == 'INT Overstock' && isPC">
              <img :src="INTPic" alt="" />
            </div>

            <p class="title">{{ $t("商业信息") }}</p>
            <p class="info">
              {{ $t("如果您已是商家，请")
              }}<span @click="goPage()">{{ $t("点击登陆") }}</span>
            </p>
            <el-form
              :model="ruleForm"
              :rules="rules"
              ref="ruleForm"
              :label-position="labelPosition"
              :validate-on-rule-change="false"
              label-width="200px"
              class="demo-ruleForm"
            >
              <el-form-item :label="$t('店铺标志')" prop="sellerImg">
                <!--                <div v-if="isPC" class="uploder-wrap">-->
                <!--                  <Upload-->
                <!--                    class="avatar-uploader"-->
                <!--                    v-model="fileList1"-->
                <!--                    moduleName="avatar"-->
                <!--                    :width="76"-->
                <!--                    :height="76"-->
                <!--                    :fixedNumber="[1, 1]"-->
                <!--                    @success="updateMerchantInfo"-->
                <!--                  />-->
                <!--                  <div class="tips" style="margin-left: 12px">-->
                <!--                    {{ $t("推荐尺寸") }} 200*200px-->
                <!--                    <span>{{ $t("上传需要") }}</span>-->
                <!--                  </div>-->
                <!--                </div>-->
                <!--                <div v-else>-->
                <!--                  <div class="uploder-wrap">-->
                <!--                    <van-uploader-->
                <!--                      v-model="fileList1"-->
                <!--                      :max-count="1"-->
                <!--                      :after-read="avatarAfterRead"-->
                <!--                    />-->
                <!--                    <div class="tips">-->
                <!--                      {{ $t("推荐尺寸") }} 200*200px-->
                <!--                      <span>{{ $t("上传需要") }}</span>-->
                <!--                    </div>-->
                <!--                  </div>-->
                <!--                  <div>-->
                <!--                    <cropperjs-->
                <!--                      :imgFile="imgFile"-->
                <!--                      :ratioWidth="ratioWidth"-->
                <!--                      :ratioHeight="ratioHeight"-->
                <!--                      @handleCancel="handleCancel"-->
                <!--                      @handleUpload="handleUpload"-->
                <!--                      @handleCropData="handleCropData"-->
                <!--                      v-if="isCutting"-->
                <!--                    >-->
                <!--                    </cropperjs>-->
                <!--                  </div>-->
                <!--                </div>-->
                <van-uploader
                  :after-read="(file) => paperworkAfterRead(file, 0)"
                  v-model="fileList1"
                  :max-size="isOverSize"
                  @oversize="onOversize"
                  accept="image/png,image/jpg,image/jpeg"
                  :max-count="1"
                  @success="updateMerchantInfo"
                />
              </el-form-item>
              <el-form-item :label="$t('店铺名称')" prop="sellerName">
                <el-input
                  :placeholder="$t('请输入店铺名称,不包含特殊字符')"
                  v-model="ruleForm.sellerName"
                  maxlength="50"
                  @input="spaceDete()"
                  clearable
                ></el-input>
              </el-form-item>
              <el-form-item
                :label="$t('店铺地址')"
                prop="sellerAddress"
                v-if="
                  itemname !== 'FamilyShop' && itemname !== 'SM-wholesale shop'
                "
              >
                <el-input
                  :placeholder="$t('请输入店铺地址,不包含特殊字符')"
                  v-model="ruleForm.sellerAddress"
                  maxlength="200"
                  @input="spaceDete1()"
                  clearable
                ></el-input>
              </el-form-item>
              <!-- <el-form-item :label="$t('国家')" prop="nationality">
                <div @click="openNationality(2)">
                  <el-input
                    @click="openNationality(2)"
                    readonly
                    :placeholder="$t('请选择国家')"
                    v-model="ruleForm.nationality"
                  ></el-input>
                </div>
              </el-form-item> -->

              <el-form-item prop="country" :label="$t('国家')">
                <el-select
                  v-model="ruleForm.nationality"
                  :placeholder="$t('请选择国家')"
                  filterable
                  @change="changeCountry"
                  clearable
                >
                  <el-option
                    v-for="item in countryList"
                    :key="item.id"
                    :value="item.id"
                    :label="item.countryName"
                  >
                    <span>{{ item.countryName }}</span>
                  </el-option>
                </el-select>
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
                <el-input
                  :placeholder="$t('请输入身份证或者护照号')"
                  v-model="ruleForm.idnumber"
                  oninput="value=value.replace(/[\W]/g,'')"
                  maxlength="256"
                  class="input_clear"
                  clearable
                ></el-input>
              </el-form-item>
              <el-form-item :label="$t('真实姓名')" prop="name">
                <el-input
                  :placeholder="$t('请输入真实姓名,不包含特殊字符')"
                  v-model="ruleForm.name"
                  maxlength="256"
                  @input="spaceDete2()"
                  clearable
                ></el-input>
              </el-form-item>
              <el-form-item
                label="WhatsApp"
                prop="whatsappAcc"
                v-if="
                  itemname == 'FamilyShop' || itemname == 'SM-wholesale shop'
                "
              >
                <el-input
                  :placeholder="$t('请输入您的WhatsApp账号')"
                  v-model="ruleForm.whatsappAcc"
                  maxlength="16"
                  @input="inputChange"
                  clearable
                  class="phone_number_wrap argos-input"
                >
                  <div slot="prepend">
                    <div class="prepend-wrap" @click="openNationality1(1)">
                      <div class="phone_number">+{{ AppAreaCode }}</div>
                      <img src="@/assets/image/Merchant/down-icon.png" />
                    </div>
                  </div>
                </el-input>
              </el-form-item>
              <el-form-item :label="$t('证件照/上传护照')" prop="idimg_1" >
                <div class="uploder-center">
                  <div class="uploder-two-wrap">
                    <van-uploader
                      :after-read="(file) => paperworkAfterRead(file, 1)"
                      v-model="fileList2"
                      :max-size="isOverSize"
                      @oversize="onOversize"
                      accept="image/png,image/jpg,image/jpeg"
                      :max-count="1"
                    />
                    <div class="tips">
                      {{
                        ruleForm.idname === "身份证"
                          ? $t("证件正面")
                          : $t("护照")
                      }}
                    </div>
                  </div>
                  <!-- v-if="ruleForm.idname == '身份证'" -->
                  <div class="uploder-two-wrap">
                    <van-uploader
                      :after-read="(file) => paperworkAfterRead(file, 2)"
                      v-model="fileList3"
                      :max-size="isOverSize"
                      @oversize="onOversize"
                      accept="image/png,image/jpg,image/jpeg"
                      :max-count="1"
                    />
                    <div class="tips">{{ $t("证件反面") }}</div>
                  </div>
                  <div
                    class="uploder-two-wrap"
                    v-if="
                      itemname !== 'Inchoi' &&
                      itemname !== 'Hive' &&
                      itemname !== 'AntMall'
                    "
                  >
                    <van-uploader
                      :after-read="(file) => paperworkAfterRead(file, 3)"
                      v-model="fileList4"
                      :max-size="isOverSize"
                      @oversize="onOversize"
                      accept="image/png,image/jpg,image/jpeg"
                      :max-count="1"
                    />
                    <div class="tips">{{ $t("手持证件照") }}</div>
                  </div>
                </div>
              </el-form-item>
              <el-form-item :label="$t('拍摄示例')" v-if="itemname !== 'TikTok'">
                <div class="correct-warp">
                  <img src="@/assets/image/Merchant/01.png" />
                  <img src="@/assets/image/Merchant/02.png" />
                  <img
                    src="@/assets/image/Merchant/03.png"
                    v-if="
                      itemname !== 'Inchoi' &&
                      itemname !== 'Hive' &&
                      itemname !== 'AntMall'
                    "
                  />
                </div>
              </el-form-item>
              <p
                v-if="
                  itemname !== 'SM-wholesale shop' && itemname !== 'FamilyShop'
                "
              >
                {{ $t("验证您的电子邮件或电话号码") }}
              </p>
              <div
                class="tab-wrap"
                v-if="
                  itemname !== 'SM-wholesale shop' && itemname !== 'FamilyShop'
                "
              >
                <div
                  class="tab-item"
                  v-for="(item, index) in tabList"
                  :key="index"
                  @click="
                    (tabIndex = index),
                      (ruleForm.password = ''),
                      (ruleForm.re_password = ''),
                      (ruleForm.username = '')
                  "
                  :class="[tabIndex === index ? 'active' : '']"
                >
                  {{ item }}
                </div>
              </div>

              <el-form-item
                :label="$t('电子邮箱')"
                prop="username"
                v-if="
                  tabIndex === 0 &&
                  itemname !== 'SM-wholesale shop' &&
                  itemname !== 'FamilyShop'
                "
              >
                <el-input
                  :placeholder="$t('请输入正确的邮箱地址')"
                  v-model="ruleForm.username"
                >
                </el-input>
              </el-form-item>
              <el-form-item
                :label="$t('电子邮箱')"
                prop="username"
                v-if="
                  tabIndex === 0 &&
                  (itemname == 'SM-wholesale shop' || itemname == 'FamilyShop')
                "
                class="require"
              >
                <div class="sendbox">
                  <el-input
                    :placeholder="$t('请输入正确的邮箱地址')"
                    v-model="ruleForm.username"
                    clearable
                  >
                  </el-input>

                  <!-- <el-button v-if="itemname == 'ArgosShop'" type="primary" class="sendCode" size="small"  @click="getCode" :disabled='codedis'>{{send}}</el-button> -->
                </div>
              </el-form-item>
              <!-- <el-form-item :label="itemname == 'ArgosShop'?$t('短信验证码'):$t('邮箱验证码')"  prop="verifcode" v-if=" itemname == 'SM-wholesale shop'">
                                <el-input :placeholder="$t('请输入验证码')" v-model="ruleForm.verifcode" :onkeyup="(ruleForm.verifcode = ruleForm.verifcode.replace(/\s+/g, ''))
                                    "></el-input>
                            </el-form-item> -->
              <el-form-item
                :label="$t('手机号')"
                prop="phone"
                v-if="
                  itemname == 'SM-wholesale shop' || itemname == 'FamilyShop'
                "
              >
                <el-input
                  :placeholder="$t('请输入手机号')"
                  class="phone_number_wrap argos-input"
                  type="text"
                  v-model="ruleForm.phone"
                  clearable
                  :onkeyup="
                    (ruleForm.phone = ruleForm.phone.replace(/\D/g, ''))
                  "
                >
                  <div slot="prepend">
                    <div class="prepend-wrap" @click="openNationality(1)">
                      <div class="phone_number">+{{ areaCode }}</div>
                      <img src="@/assets/image/Merchant/down-icon.png" />
                    </div>
                  </div>
                </el-input>
              </el-form-item>

              <el-form-item
                :label="$t('手机号')"
                prop="username"
                v-if="tabIndex === 1"
              >
                <el-input
                  :placeholder="$t('请输入手机号')"
                  class="phone_number_wrap"
                  type="text"
                  v-model="ruleForm.userPhone"
                  clearable
                  :onkeyup="
                    (ruleForm.userPhone = ruleForm.userPhone.replace(/\D/g, ''))
                  "
                >
                  <div slot="prepend">
                    <div class="prepend-wrap" @click="openNationality(1)">
                      <div class="phone_number">+{{ areaCode }}</div>
                      <img src="@/assets/image/Merchant/down-icon.png" />
                    </div>
                  </div>
                </el-input>
              </el-form-item>
              <!-- <el-form-item :label="$t('电子邮箱')" prop="username" v-if=" itemname == 'ArgosShop'">
                                 <el-input :placeholder="$t('请输入正确的邮箱地址')" v-model="ruleForm.username" :onkeyup="(ruleForm.username = ruleForm.username.replace(/\s+/g, ''))
                                    ">
                                    </el-input>
                            </el-form-item> -->
              <el-form-item :label="$t('登录密码')" prop="password">
                <div class="password">
                  <el-input
                    :placeholder="$t('请输入登录密码')"
                    :type="showPassword ? 'password' : 'text'"
                    v-model="ruleForm.password"
              
                  >
                    <template slot="suffix">
                      <div
                        style="display: flex; align-items: center; height: 100%"
                      >
                        <img
                          class="password-icon"
                          :src="showPassword ? imageMap.close : imageMap.open"
                          @click="showPassword = !showPassword"
                        />
                      </div>
                    </template>
                  </el-input>
                </div>
              </el-form-item>
              <el-form-item
                :label="$t('再次输入确认登录密码')"
                prop="re_password"
              >
                <div class="password">
                  <el-input
                    :placeholder="$t('请确认输入登录密码')"
                    :type="showPassword2 ? 'password' : 'text'"
                    v-model="ruleForm.re_password"
            
             
                  >
                    <template slot="suffix">
                      <div
                        style="display: flex; align-items: center; height: 100%"
                      >
                        <img
                          class="password-icon"
                          :src="showPassword2 ? imageMap.close : imageMap.open"
                          @click="showPassword2 = !showPassword2"
                        />
                      </div>
                    </template>
                  </el-input>
                </div>
              </el-form-item>
              <el-form-item :label="$t('邀请码')" prop="usercode" >
                <el-input
                  :placeholder="$t('请输入邀请码')"
                  v-model="ruleForm.usercode"
          
                  clearable
                ></el-input>
              </el-form-item>
            </el-form>
          </div>
          <div class="bottom">
            <div style="display: flex; justify-items: start">
              <van-checkbox v-model="checked" @click="open">
                {{ $t("我已经阅读并同意") }}
              </van-checkbox>
              <span class="color-yellow" @click="show = true">{{
                $t("入驻协议")
              }}</span>
            </div>

            <!-- <van-button type="primary" color="var(--color-main)" v-if="step == 1" class="button" @click="stepFun()">{{ $t('同意') }}
            </van-button> -->
            <van-button
              type="primary"
              color="var(--color-main)"
              v-if="step == 2"
              class="button-xy"
              :disabled="tjbtn"
              @click="sellerRegister"
              >{{ $t("提交申请表") }}
            </van-button>
          </div>
        </div>
        <!-- step3 -->
        <submit-success :sellerSign="sellerSign" v-else></submit-success>
      </div>
    </div>
    <mer-chant-footer></mer-chant-footer>
    <nationality-list
      v-if="renderComponent"
      :isCode="isCode"
      ref="controlChild"
      :title="$t('选择区域码')"
      @getName="getName(arguments)"
    >
    </nationality-list>
    <nationality-list
      v-if="renderWhatsApp"
      :isCode="isCodeApp"
      ref="controlChild1"
      :title="$t('选择区域码')"
      @getName="getName1(arguments)"
    >
    </nationality-list>
  </div>
</template>

<script>
import merChantHeader from "./components/mer-chant-header";
import merChantFooter from "./components/mer-chant-footer";
import submitSuccess from "./components/submit-success.vue";
import { mapGetters, mapMutations } from "vuex";
import {
  Dropdown,
  DropdownItem,
  DropdownMenu,
  Form,
  FormItem,
  Input,
  Option,
  Select,
} from "element-ui";
import {
  Button,
  Checkbox,
  Toast,
  Uploader,
  ImagePreview,
  Swipe,
  SwipeItem,
} from "vant";
import {
  sellerRegister,
  uploadimg,
  apiListCountry,
  getSignType,
  getEmailCode,
  sellerRegister2,
} from "@/API/commodity";
import NationalityList from "@/components/NationalityList";
import vueEsign from "vue-esign";
// import cropperjs from "./components/cropperjs.vue";
// import Upload from "@/components/Upload";
import h5img1 from "@/assets/image/H5Banner-1.png";
import h5img2 from "@/assets/image/H5Banner-2.png";
import h5img3 from "@/assets/image/H5Banner-3.png";
import h5img4 from "@/assets/image/H5Banner-4.png";
import html2Canvas from "html2canvas";
import JsPDF from "jspdf";
export default {
  name: "merchantSettled",
  data() {
    return {
      input: "",
      sellerSign: false,
      lineWidth: 6,
      lineColor: "#000000",
      renderWhatsApp: true,
      bgColor: "",
      resultImg: "",


      // esignImg: "",
      tabIndex: 0,
      isCrop: false,
      visible: false,
      itemname: process.env.VUE_APP_ITEM_NAME,
      showPassword: true,
      showPassword2: true,
      imageMap: {
        open: require("@/assets/image/eye-open.png"),
        close: require("@/assets/image/eye-close.png"),
      },
      isCutting: false, // 是否裁剪
      imgFile:
        "https://bpic.588ku.com/element_water_img/18/06/12/b2887846cb19ff36a5502401ac918809.jpg",
      ratioWidth: 1, // 裁剪比例：长 自由比例设置为: 0 即可
      ratioHeight: 1, // 裁剪比例：宽 自由比例设置为: 0 即可
      showUpLoader: true,
      step: 2,
      show: false,
      checked: false,
      screenWidth: document.body.clientWidth,
      type: "Email", //Email/Moblie
      uploadCheckIndex: 1,
      scrollDisbled: true,
      areaCode: 44,
      AppAreaCode: 44,
      countryList: [],
      country: "",
      ruleForm: {
        type: 1, //1/手机；2/邮箱；
        usercode: "",
        name: "",
        idimg_1: "",
        idimg_2: "",
        idimg_3: "",
        idname: "身份证",
        idnumber: "",
        nationality: "",
        userPhone: "",
        sellerImg: "",
        username: "",
        userEmail: "",
        password: "",
        country: "",
        re_password: "",
        signPdfUrl: "",
        sellerName: "",
        sellerAddress: "",
        phone: "",
        verifcode: "",
        whatsappAcc: "",
      },
      labelPosition: "top",
      tjbtn: false,
      isCode: true,
      isCodeApp: true,
      options: [
        { label: this.$t("身份证"), value: "身份证" },
        { label: this.$t("护照"), value: "护照" },
      ],
      fileList1: [],
      fileList2: [],
      fileList3: [],
      fileList4: [],
      send: "",
      // sendtext:this.$t('获取验证码'),
      // CountryList: [
      //   {
      //     label: "中国",
      //     value: "zh-CN",
      //     icon: require("@/assets/image/language/cn.png"),
      //   },
      // ],
      lang: [
        {
          title: "简体中文",
          key: "zh-CN",
          icon: require("@/assets/image/language/cn.png"),
        },
        {
          title: "English",
          key: "en-US",
          icon: require("@/assets/image/language/usa.png"),
        },
        {
          title: "繁体中文",
          key: "CN",
          icon: require("@/assets/image/language/tw.png"),
        },
      ],
      pageDiaCode: true,
      renderComponent: true,
      blob: null,
      codedis: false,
      username: "",
      now_date: "",
      downloadUrl: [
        { name: "Argos", url: "https://argos.me" },
        { name: "Mata", url: "https://e-metashop.com" },
        { name: "Tongda", url: "https://www.tongdashops.com" },
        { name: "FamilyMart", url: "https://familymartex.com" },
        { name: "FamilyShop", url: "https://www.familyshopit.com" },
        { name: "Inchoi", url: "https://Inchoishop.com" },
        { name: "Hive", url: "https://www.hivemalls.com" },
        { name: "TikTok", url: "https://tiktokmallit.com" },
        { name: "Shop2u", url: "https://shop2u.co" },
        { name: "EShop", url: "https://ml.tiktokmall666.com" },
      ],
    };
  },
  // directives: {
  //     'filter-special-characters': {
  //       inserted(el) {
  //         el.addEventListener('input', function(event) {
  //           event.target.value = event.target.value.replace(/[^\w\u0080-\uFFFF]/, '');
  //         });
  //       }
  //     }
  //   },
  computed: {
    ...mapGetters({
      activeLang: "language",
    }),
    rules() {
      return {
        username: [
          {
            required: false,
            message: this.$t("请输入正确的邮箱地址"),
            trigger: "blur",
          },
        ],
        country: [
          {
            required: true,
            message: this.$t("请选择国家"),
            trigger: "blur",
          },
        ],
        idname: [
          {
            required: true,
            message: this.$t("请输入身份证或者护照号"),
            trigger: "blur",
          },
        ],
        idimg_1: [
          {
            required: true,
            message: this.$t("请上传身份证正面"),
            trigger: "blur",
          },
        ],
        idimg_2: [
          {
            required: true,
            message: this.$t("请上传身份证反面"),
            trigger: "blur",
          },
        ],

        re_password: [
          {
            required: true,
            message: this.$t("请确认输入登录密码"),
            trigger: "blur",
          },
        ],
        password: [
          {
            required: true,
            message: this.$t("请输入登录密码"),
            trigger: "blur",
          },
        ],
        sellerImg: [
          {
            required: true,
            message: this.$t("请上传店铺logo"),
            trigger: "blur",
          },
        ],
        phone: [
          {
            required: false,
            message: this.$t("请输入手机号"),
            trigger: "blur",
          },
        ],
        idnumber: [
          {
            required: true,
            message: this.$t("请输入身份证或者护照号"),
            trigger: "change",
          },
        ],
        name: [
          {
            required: true,
            message: this.$t("请输入真实姓名"),
            trigger: "blur",
          },
        ],
        sellerName: [
          {
            required: true,
            message: this.$t("请输入店铺名称"),
            trigger: "blur",
          },
        ],
        sellerAddress: [
          {
            required: true,
            message: this.$t("请输入店铺地址"),
            trigger: "blur",
          },
        ],
        usercode: [
          {
            required: true,
            message: this.$t("请输入邀请码"),
            trigger: "blur",
          },
        ],
        whatsappAcc: [
          {
            required: false,
            message: this.$t("请输入您的WhatsApp账号"),
            trigger: "blur",
            // transform: (value) => value && value.trim(),
          },
        ],
      };
    },
    sendtext() {
      return this.$t("获取验证码");
    },
    tabList() {
      return [this.$t("电子邮箱"), this.$t("手机号")];
    },
    languageIcon() {
      const language = this.$store.getters.language || "CN";
      const icon = {
        "zh-CN": require("@/assets/image/language/cn.png"),
        "en-US": require("@/assets/image/language/usa.png"),
        CN: require("@/assets/image/language/tw.png"),
      };
      return icon[language];
    },
    isOverSize() {
      return 4000 * 1024;
    },
    INTPic () {
       const language = this.$store.getters.language
       if(language == 'zh-CN'){
        return require("@/assets/image/zh.png")
       } else {
        return require("@/assets/image/en.png")
       }

    },
    h5img() {
      const language = this.$store.getters.language
      if(language == 'zh-CN'){
        return [h5img3,h5img4];
      } else {
        return [h5img1,h5img2];
      }
    },
    isPC() {
      let userAgentInfo = navigator.userAgent;
      let Agents = [
        "Android",
        "iPhone",
        "SymbianOS",
        "Windows Phone",
        "iPad",
        "iPod",
      ];
      let flag = true;
      for (let v = 0; v < Agents.length; v++) {
        if (userAgentInfo.indexOf(Agents[v]) > 0) {
          flag = false;
          break;
        }
      }
      return flag;
    },
  },
  components: {
    // cropperjs,
    vueEsign,
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
    [Toast.name]: Toast,
    [Swipe.name]: Swipe,
    [SwipeItem.name]: SwipeItem,
    // Upload,

  },
  created() {
    this.getCountry();
    this.getType();
    // console.log('this.isPC ->', this.isPC);
    if (this.screenWidth >= 500) {
      this.labelPosition = "left";
    } else {
      this.labelPosition = "top";
    }
    if (this.$route.query.usercode || localStorage.getItem("usercode")) {
      // localStorage.setItem("usercode", this.$route.query.usercode);
      // console.log(' ->', localStorage.getItem("usercode"));
      this.ruleForm.usercode =
        this.$route.query.usercode || localStorage.getItem("usercode");
    }
    if (this.isPC) {
      this.scrollDisbled = false;
    }
    this.getNowFormatDate();
    if (
      this.itemname == "SM-wholesale shop" ||
      this.itemname == "FamilyShop" ||
      this.itemname == "ArgosShop"
    ) {
      this.rules.username[0].required = true;
      this.rules.phone[0].required = true;
      this.rules.whatsappAcc[0].required = true;
    }
    if(this.itemname == 'TikTok'){
       this.rules.idimg_1[0].required = false;
    }
    if(this.itemname == 'FamilyShop' || this.itemname == 'Alibaba' || this.itemname == 'AntMall'){
        this.rules.usercode[0].required = false;
    }
  },
  methods: {
    ...mapMutations(["setLanguage"]),
    ImgView(img) {
      ImagePreview(img);
    },
    inputChange() {
      this.ruleForm.whatsappAcc = this.ruleForm.whatsappAcc.replace(
        /[^0-9]/g,
        ""
      );
    },
    handleUsernameInput() {
    this.ruleForm.username = this.ruleForm.username.replace(/\s/g, '');
  },
    //     handleInputEmoji(event) {
    //   // 使用正则表达式匹配 emoji
    //         const emojiRegex = /[\uD800-\uDFFF]./;
    //         // 如果输入的内容包含 emoji，则移除
    //         if (emojiRegex.test(this.ruleForm.whatsappAcc)) {
    //             this.ruleForm.whatsappAcc = this.ruleForm.whatsappAcc.replace(emojiRegex, '');
    //         }
    //     },
    async getCode() {
      if (
        !this.ruleForm.username &&
        (this.itemname == "SM-wholesale shop" || this.itemname == "FamilyShop")
      ) {
        return Toast(this.$t("请输入正确的邮箱地址"));
      } else if (!this.ruleForm.phone && this.itemname == "ArgosShop") {
        return Toast(this.$t("请输入手机号"));
      } else {
        let target =
          this.itemname == "ArgosShop"
            ? this.areaCode + " " + this.ruleForm.phone
            : this.ruleForm.username;
        const params = {
          target,
        };
        await getEmailCode(params).then((res) => {
          console.log("res ->", res);
          if (this.itemname == "ArgosShop") {
            Toast(this.$t("验证码已发送"));
          } else {
            Toast(this.$t("邮件已发送"));
          }
          let num = 61;
          let timer = setInterval(() => {
            num--;
            this.send = num + "s";
            if (num == 0) {
              clearInterval(timer);
              this.send = this.$t("获取验证码");
              this.codedis = false;
            }
          }, 1000);
          this.codedis = true;
        });
      }
    },
    async getType() {
      const res = await getSignType();
      console.log("res ->", res.sellerSign);
      this.sellerSign = res.sellerSign == "false" ? false : true;
      console.log("this.sellerSign ->", this.sellerSign);
    },
    //  inputHandler(){
    //     this.ruleForm.sellerName = this.ruleForm.sellerName.replace(/[^\w\u0080-\uFFFF]/g, '');
    // },
    reset() {
      this.$refs.esign.reset();
    },
    goback() {
      this.$refs.esign.reset();
      this.visible = false;
    },
    spaceDete() {
      this.ruleForm.sellerName = this.ruleForm.sellerName.trimLeft();
    },

    spaceDete1() {
      this.ruleForm.sellerAddress = this.ruleForm.sellerAddress.trimLeft();
    },

    spaceDete2() {
      this.ruleForm.name = this.ruleForm.name.trimLeft();
    },
    getNowFormatDate() {
      let date = new Date(),
        year = date.getFullYear(), //获取完整的年份(4位)
        month = date.getMonth() + 1, //获取当前月份(0-11,0代表1月)
        strDate = date.getDate(); // 获取当前日(1-31)
      if (month < 10) month = `0${month}`; // 如果月份是个位数，在前面补0
      if (strDate < 10) strDate = `0${strDate}`; // 如果日是个位数，在前面补0

      this.now_date = `${year}-${month}-${strDate}`;
    },
    clickTip() {
      console.log("3434 ->", 3434);
      // this.$message({
      //     message: this.$t("请仔细阅读合同"),
      //     type: "warning",
      // });
    },
    // 保存
    save() {
      // 可选配置参数 ，在未设置format或quality属性时可在生成图片时配置 例如： {format:'image/jpeg', quality: 0.5}
      this.$refs.esign.generate({ format: "image/jpeg", quality: 0.5 });
      this.$refs.esign
        .generate()
        .then((res) => {
          // console.log('res ->', res);
          this.resultImg = res;
          // this.$emit("finsih",res)
          this.visible = false;
        })
        .catch((err) => {
          // 画布没有签字时会执行这里 'Not Signned'
          // this.$message.error("您还未完成签字，请签字完成后保存");
          Toast(this.$t("请签字后再提交"));
        });
    },
    argeementEsign() {
      if (this.sellerSign) {
        if (this.resultImg) {
          this.show = false;
          this.checked = true;
          this.getImg();
        } else {
          Toast(this.$t("请签字后再提交"));
        }
      } else {
        this.show = false;
        this.checked = true;
        // this.getImg();
      }
    },
    dataURLtoBlob(dataurl) {
      let arr = dataurl.split(","),
        mime = arr[0].match(/:(.*?);/)[1],
        bstr = atob(arr[1]),
        n = bstr.length,
        u8arr = new Uint8Array(n);
      while (n--) {
        u8arr[n] = bstr.charCodeAt(n);
      }
      return new Blob([u8arr], { type: mime });
    },
    blobToFile(theBlob, fileName) {
      theBlob.lastModifiedDate = new Date();
      theBlob.name = fileName;
      return theBlob;
    },
    convertBase64ToFile(urlData, filename) {
      var arr = urlData.split("base64,");
      var type = arr[0].match(/:(.*?);/)[1];
      var fileExt = type.split("/")[1];
      var bstr = atob(arr[1]);
      var n = bstr.length;
      var u8arr = new Uint8Array(n);
      while (n--) {
        u8arr[n] = bstr.charCodeAt(n);
      }
      return new File([u8arr], filename + "." + fileExt, {
        type: type,
      });
    },
    getImg() {
      this.$refs.capture.scrollTop = 0;
      this.$refs.capture.style.fontSize = "24px";
      if (window.top) {
        this.$refs.capture.style.width = "1220px";
        this.$refs.capture.style.paddingRight = "30px";
      }
      html2Canvas(this.$refs.capture, {
        allowTaint: true,
        useCORS: true,
        scale: 1,
      }).then((canvas) => {
        //内容的宽度
        let contentWidth = canvas.width;
        //内容高度
        let contentHeight = canvas.height;
        //一页pdf显示html页面生成的canvas高度,a4纸的尺寸[595.28,841.89];
        let pageHeight = (contentWidth / 592.28) * 841.89;
        //未生成pdf的html页面高度
        let leftHeight = contentHeight;
        //页面偏移
        let position = 0;
        //a4纸的尺寸[595.28,841.89]，html页面生成的canvas在pdf中图片的宽高
        let imgWidth = 595.28;
        let imgHeight = (592.28 / contentWidth) * contentHeight;
        //canvas转图片数据
        let pageData = canvas.toDataURL("image/jpeg", 1);
        //新建JsPDF对象
        let PDF = new JsPDF("", "pt", "a4");
        //判断是否分页

        if (leftHeight < pageHeight) {
          PDF.addImage(pageData, "JPEG", 10, 1, imgWidth, imgHeight);
        } else {
          while (leftHeight > 0) {
            PDF.addImage(pageData, "JPEG", 10, position, imgWidth, imgHeight);
            leftHeight -= pageHeight;
            position -= 841.89;
            if (leftHeight > 0) {
              PDF.addPage();
            }
          }
        }
        this.tjbtn = true;
        let blob = this.convertBase64ToFile(
          PDF.output("dataurlstring"),
          "esign.pdf"
        );
        // PDF.save('esign.pdf')
        let fileOfBlob = new File([blob], "esign.pdf");
        let formData = new FormData(); //通过formdata上传
        console.log("fileOfBlob ->", fileOfBlob);
        formData.append("file", fileOfBlob);
        formData.append("moduleName", "seller");
        console.log("formData ->", formData.get("file"));
        Toast.loading({
          duration: 0,
          message: this.$t("上传中"),
          forbidClick: true,
        });
        uploadimg(formData)
          .then((res) => {
            this.ruleForm.signPdfUrl = res;
            this.tjbtn = false;
            Toast(this.$t("签名成功"));
            this.show = false;
            this.checked = true;
          })
          .catch(function () {
            Toast.clear();
            Toast(this.$t("失败"));
            this.ruleForm.signPdfUrl = "";
          });
        this.$refs.capture.style.fontSize = "14px";
        if (window.top) {
          this.$refs.capture.style.width = "90%";
          this.$refs.capture.style.paddingRight = "0px";
        }
      });
    },
    handleScroll(e) {
      const { scrollTop, clientHeight, scrollHeight } = e.target;
      console.log(scrollTop, clientHeight, scrollHeight);
      if (scrollTop + clientHeight + 2 >= scrollHeight) {
        // alert('滚动到底部啦')
        this.scrollDisbled = false;
      }
    },
    open() {
      // console.log('this.checked ->', this.checked);
      if (this.checked == true) {
        this.checked = false;
      }
      this.checked = false;
      if (this.checked == false) {
        this.show = true;
      }
    },
    agreement() {
      if (this.scrollDisbled) {
        Toast(this.$t("请仔细阅读经营合同"));
      } else {
        this.visible = true;
      }

      // this.show=false;
      // this.checked=true;
    },
    closeAgreement() {
      this.show = false;
      this.checked = false;
    },
    async getCountry() {
      // console.log('localStorage ->', localStorage.getItem('lang'));
      // const lang = localStorage.getItem('lang')
      // lang == 'CN' ? 'TW' : localStorage.getItem('lang') || 'zh-CN'
      let res = await apiListCountry();
      this.send = this.sendtext;
      // console.log(res);

      this.countryList = res.data;
    },
    onOversize(file) {
      // console.log(file);
      Toast(this.$t("文件大小不能超过 4Mb"));
    },
    // 裁剪
    handleCutting() {
      this.isCutting = true;
    },
    // 取消
    handleCancel() {
      this.isCutting = false;
      this.fileList1 = [];
    },
    // 上传
    handleUpload(data) {
      let fileOfBlob = new File([data], "logo.png"); // 重命名
      this.isCutting = false;
      Toast.loading({
        duration: 0,
        message: this.$t("上传中"),
        forbidClick: true,
      });
      let formData = new FormData(); //通过formdata上传
      formData.append("file", fileOfBlob);
      formData.append("moduleName", "selle");
      uploadimg(formData)
        .then((data) => {
          Toast.clear();
          this.ruleForm.sellerImg = data;
          console.log("data ->", data);
          this.fileList1[0].content = data;
          // this.fileList1[0].file=fileOfBlob
        })
        .catch(function () {
          Toast.clear();
          Toast(this.$t("失败"));
          this.fileList1 = [];
        });
    },
    updateMerchantInfo(data) {
      this.ruleForm.sellerImg = data;
    },
    handleCropData(data) {
      console.log("裁剪数据");
      console.log(data);
    },
    handleSetLang(index) {
      console.log(index);
      // 设置i18n.locale 组件库会按照上面的配置使用对应的文案文件
      this.$i18n.locale = this.lang[index].key;
      // // 提交mutations
      // this.setLanguage(this.lang[index].key);
    },
    changeCountry(val) {
      console.log(val);
      this.ruleForm.country = val;
    },

    //商户注册
    sellerRegister() {
      
   console.log("this.ruleForm.sellerImg ->", this.ruleForm.sellerImg);
      if (this.itemname !== 'TikTok'){
        if (!this.ruleForm.idimg_1 || !this.ruleForm.idimg_2) {
          Toast(this.$t("请上传证件照片"));
          return;
        }
      }

      if (
        this.itemname !== "Inchoi" &&
        this.itemname !== "Hive" &&
        this.itemname !== "AntMall" &&
        this.itemname !== 'TikTok'
      ) {
        if (!this.ruleForm.idimg_3) {
          Toast(this.$t("请上传证件照片"));
          return;
        }
      }
      if (!this.checked) {
        Toast(this.$t("请同意入驻协议"));
        return;
      }
      this.ruleForm.type = this.tabIndex === 0 ? 2 : 1;

      if (this.tabIndex == 1) {
        this.username = this.areaCode + " " + this.ruleForm.userPhone;
      } else {
        this.username = this.ruleForm.username;
      }
      this.$refs["ruleForm"]
        .validate((valid) => {
          if (
            valid &&
            this.itemname !== "SM-wholesale shop" &&
            this.itemname !== "FamilyShop"
          ) {
            sellerRegister({
              type: this.ruleForm.type,
              usercode: this.ruleForm.usercode || '000000',
              name: this.ruleForm.name,
              idimg_1: this.ruleForm.idimg_1,
              idimg_2: this.ruleForm.idimg_2,
              idimg_3: this.ruleForm.idimg_3,
              idname: this.ruleForm.idname,
              idnumber: this.ruleForm.idnumber,
              nationality: this.ruleForm.nationality,
              sellerImg: this.ruleForm.sellerImg,
              username: this.username,
              password: encodeURI(this.ruleForm.password),
              country: this.ruleForm.country,
              re_password: encodeURI(this.ruleForm.re_password),
              signPdfUrl: this.ruleForm.signPdfUrl,
              sellerAddress: this.ruleForm.sellerAddress,
              idimg_0: this.ruleForm.idimg_0,
              sellerName: this.ruleForm.sellerName,
            }).then((res) => {
              console.log("res ->", res);
              this.step = 3;
              this.$el
                .querySelector("#product")
                .scrollIntoView({ behavior: "smooth" });
            }).catch((err) => {
          console.log(err);
        });
          } else if (
            valid &&
            (this.itemname == "SM-wholesale shop" ||
              this.itemname == "FamilyShop")
          ) {
            let type = this.itemname == "ArgosShop" ? 1 : 2;
            sellerRegister2({
              type,
              usercode: this.ruleForm.usercode || '000000',
              name: this.ruleForm.name,
              idimg_1: this.ruleForm.idimg_1,
              idimg_2: this.ruleForm.idimg_2,
              idimg_3: this.ruleForm.idimg_3,
              idname: this.ruleForm.idname,
              idnumber: this.ruleForm.idnumber,
              sellerName: this.ruleForm.sellerName,
              nationality: this.ruleForm.nationality,
              sellerImg: this.ruleForm.sellerImg,
              username: this.ruleForm.username,
              password: encodeURI(this.ruleForm.password),
              country: this.ruleForm.country,
              re_password: encodeURI(this.ruleForm.re_password),
              signPdfUrl: this.ruleForm.signPdfUrl,
              sellerAddress: this.ruleForm.sellerAddress,
              phone: this.areaCode + " " + this.ruleForm.phone,
              // verifcode: this.ruleForm.verifcode,
              idimg_0: this.ruleForm.idimg_0,
              whatsApp: this.AppAreaCode + " " + this.ruleForm.whatsappAcc,
            }).then(() => {
              this.step = 3;
              this.$el
                .querySelector("#product")
                .scrollIntoView({ behavior: "smooth" });
            }).catch((err) => {
          console.log(err);
        });;
          } else {
            return false;
          }
        })

    },
    goPage() {
      // const obj = {
      //     'EShop': 'https://ml.tiktokmall666.com',
      //     'Argos': 'https://qjdbkef.com',
      //     'Inchoi': 'https://abhjr.com',
      //     'MetaShop': 'https://eudhu.com',
      //     'Tongda': 'https://fjawdef.com',
      //     'Hive': 'https://liebuw.com',
      //     'FamilyMart': 'https://jdhieb.com',
      //     'TikTok': 'https://aeknl.com',
      //     'Shop2u': 'https://tiktokmall666.com'
      // }
      // const url = this.downloadUrl.find(item => item.name == this.itemname).url
      if (self !== top) {
        window.parent.postMessage("jump", "*");
      } else {
        window.open(window.origin + "/ww", "_blank");
      }
      //    if (this.isPC){
      //        window.parent.postMessage('jump', '*')
      //    }else {
      //         window.open(window.origin + "/ww", "_blank")
      //     }
      //    if (/Mobi|Android|iPhone/i.test(navigator.userAgent) ) {
      //     //  if (window.parent) {
      //     //     var parentDomain = '';
      //     //     parentDomain = window.parent.location.origin;
      //     // }

      //        window.open(window.origin + "/ww", "_blank");
      //         // window.parent.postMessage('jump', '*')
      //     }else if(window?.plus){
      //         window.parent.postMessage('jump', '*')
      //     }else{
      //         window.open(window.origin + "/ww", "_blank");
      //     }
    },

    stepFun() {
      if (!this.checked) {
        Toast(this.$t("请同意入驻协议"));
        return;
      }
      this.step = 2;
      this.$el.querySelector("#product").scrollIntoView({ behavior: "smooth" });
    },
    openNationality(index) {
      const t = this;
      if (index === 1) {
        this.isCode = true;
      } else {
        this.isCode = false;
      }
      this.$refs.controlChild.open();
      t.renderComponent = false;
      // this.$forceUpdate()
      t.$nextTick().then(() => {
        t.renderComponent = true;
        t.$nextTick().then(() => {
          t.sj();
        });
      });
    },
    openNationality1(index) {
      const t = this;
      if (index === 1) {
        this.isCodeApp = true;
      } else {
        this.isCodeApp = false;
      }
      this.$refs.controlChild1.open();
      t.renderWhatsApp = false;
      // this.$forceUpdate()
      t.$nextTick().then(() => {
        t.renderWhatsApp = true;
        t.$nextTick().then(() => {
          t.sj1();
        });
      });
    },
    sj1() {
      this.$refs.controlChild1.open2();
      this.$refs.controlChild1.open();
    },
    getName1(params) {
      console.log(params);
      console.log("params ->", params);
      if (this.isCodeApp) {
        this.AppAreaCode = params[2];
      } else {
        this.ruleForm.nationality = params[0];
      }
    },
    sj() {
      this.$refs.controlChild.open2();
      this.$refs.controlChild.open();
    },
    getName(params) {
      console.log(params);
      console.log("params ->", params);
      if (this.isCode) {
        this.areaCode = params[2];
      } else {
        this.ruleForm.nationality = params[0];
      }
    },
    //文件上传
    avatarAfterRead(file) {
      this.imgFile = file.content;
      this.isCutting = true;
    },
    //文件上传
    paperworkAfterRead(file, fileIndex) {
      console.log("fileIndex ->", fileIndex);
      const that = this;
      Toast.loading({
        duration: 0,
        message: that.$t("上传中"),
        forbidClick: true,
      });
      let formData = new FormData(); //通过formdata上传
      formData.append("file", file.file);
      formData.append("moduleName", "selle");
      uploadimg(formData)
        .then((data) => {
          Toast.clear();
          that.ruleForm[`idimg_${fileIndex}`] = data;
        })
        .catch(() => {
          Toast.clear();
          Toast(that.$t("失败"));
          that[`fileList${fileIndex + 1}`] = [];
        });
      if (fileIndex == 0) {
        uploadimg(formData)
          .then((data) => {
            Toast.clear();
            Toast(that.$t("成功"));
            that.ruleForm.sellerImg = data;
          })
          .catch(() => {
            Toast.clear();
            Toast(that.$t("失败"));
            that.ruleForm.sellerImg = [];
          });
      }
    },
  },
  beforeDestroy() {
    Toast.clear();
  },
};
</script>
<style lang="scss" scoped>
.rtl {
  :deep(.van-checkbox__label) {
    margin-right: 8px !important;
  }

  .popup_content .close-btn {
    left: 20px;
    right: auto !important;
  }

  .pop-bnt .van-button:nth-child(1) {
    margin-left: 20px !important;
    margin-right: 0 !important;
  }

  .el-form-item /deep/ .el-form-item__error {
    left: auto !important;
    right: 0 !important;
  }

  .el-select-dropdown__item {
    text-align: center;
  }
}

::v-deep {
  .preview-cover {
    position: absolute;
    bottom: 0;
    box-sizing: border-box;
    width: 100%;
    padding: 4px;
    color: #fff;
    font-size: 12px;
    text-align: center;
    background: rgba(0, 0, 0, 0.3);
  }

  .van-button--primary {
    background: #f89220;

    border: 1px solid #f89220;
  }
  .el-input{
    position: relative;
    }
}

.banner {
  width: 100%;
  margin-top: 10px;
  margin-bottom: 10px;

  img {
    max-width: 100%;
    object-fit: cover;
  }
}
::v-deep{
    .el-form-item__content{
        width: 320px;
    }
}

::v-deep {
  .argos-input {
    .el-input__inner {
      width: 244px !important;
    }
  }

  .password {
    .el-input__inner,
    .el-input {
      width: 320px;
    }
  }
}

// ::v-deep {
//     .sendbox .el-input__inner {
//         margin-right: 5Px;
//     }
// }
.require {
  .sendbox {
    position: relative;
    width: 330px;
  }

  .sendCode {
    background-color: #f89220;
    border-color: #f89220;
    min-width: 50px;
    height: 50px;
    position: absolute;
    // top: 8Px;
  }
}

.esign-content {
  display: flex;
  justify-content: space-between;
  margin-top: 20px;

  .right {
    margin-right: 200px;
  }

  span {
    position: relative;
    z-index: 999;
  }

  .padding-tb {
    padding: 5px 0 !important;
    display: flex;
    align-items: center;
    position: relative;

    img {
      position: absolute;
      right: -20px;
      top: -20px;
      width: 92px;
      min-height: 92px;
      margin-left: 10px;
    }

    // .esign-img{
    //     position: inherit;
    //     width: 84px;
    //     min-height: 84px;
    //     right: 0;
    //     top: 0;
    // }
  }
}

.padding-tb {
  padding: 10px 0 !important;
}

.color-yellow {
  color: var(--color-main) !important;
  cursor: pointer;
  // line-height: 20px;
  display: flex;
  align-items: center;
}

.van-popup {
  width: 1250px;
  max-height: 90%;
  border-radius: 15px;
}

.popup_content {
  padding: 0 20px;
  max-width: 1250px;

  .van-button {
    margin: 20px auto 0;
    // width: 100%;
    height: 45px;
    line-height: 45px;
    border-radius: 10px;
    background: var(--color-main);
    color: #fff;
    display: block;
    pointer-events: auto;
  }

  .close-btn {
    position: absolute;
    top: 20px;
    right: 20px;
    width: 24px;
    height: 24px;
    cursor: pointer;

    img {
      width: 100%;
      height: 100%;
    }
  }
}

.merchantSettled {
  width: 100%;
  overflow: hidden;

  .merchantSettled-wap {
    background: #fff;
    display: flex;
    justify-content: center;
    align-items: center;
    width: 1200px;
    margin: 0 auto;
    z-index: 99;

    .step-div {
      width: 100%;
      background: #fff;

      border-radius: 4px;
      margin-top: -46px;

      .content {
        padding: 20px 30px;
        border: 1px solid #eeeeee;

        .title {
          font-size: 24px;
          color: #333333;
          font-weight: 700;
        }

        .info {
          margin-top: -5px;
          margin-bottom: 20px;
          position: relative;
          z-index: 99;

          span {
            color: var(--color-main);
            cursor: pointer;
          }
        }

        p {
          font-family: "PingFang HK";
          font-style: normal;
          font-size: 14px;
          // line-height: 20px;
          color: #333333;
          padding: 6px 0;
        }
      }

      .bottom {
        height: 140px;
        font-size: 14px;
        display: flex;
        flex-direction: column;
        justify-content: space-around;
        align-items: center;
        margin: 20px 0;

        .button {
          width: 475px;
        }
      }
    }
  }
}

/deep/ .van-field__label {
  width: 200px !important;
}

/deep/ .van-tabs__wrap {
  width: 250px;
}

// @media only screen
//     and (device-width: 390px)
//     and (device-height: 844px)
//     and (-webkit-device-pixel-ratio: 3) {
//       .popup_content{
//     padding: 0 0 20px !important;

//   .tc{
//     max-height: 600px;
//     overflow-y: auto;
//     padding: 0 25px;
//     }
//     .close-btn{
//       width: 24px;
//       height: 24px;
//     }
// }
//     }
.tc {
  padding: 20px 10px;
  font-size: 14px;
}

@media (min-width: 768px) and (max-width: 1250px) {
  .van-popup {
    // padding: 0 0 20px !important;
    // width: 95% !important;
  }
}

@media screen and (max-width: 768px) {
  .banner {
    width: 100%;
  }

  .require {
    position: relative;

    .sendbox {
      width: 100% !important;
      display: flex;
      flex-direction: column;
    }

    .sendCode {
      position: initial;
      margin-top: 10px;
    }
  }

  .esign-content {
    display: flex;
    justify-content: space-between;
    margin-top: 20px;

    .right {
      margin-right: 0 !important;
    }
  }

  .pop-bnt {
    width: 100% !important;

    // &>div{
    //     pointer-events: ;
    // }
    .van-button {
      margin: 0 !important;
      margin-top: 10px !important;

      &:nth-child(1) {
        margin-right: 20px !important;
        margin-bottom: 10px;
      }
    }
  }

  .popup_content {
    padding: 0 0 20px !important;
    max-height: 50%;

    .tc_wrap {
      max-height: 500px;
      overflow-y: auto;
      padding: 0 25px;
    }

    // .tc {
    //     max-height: 400px;
    //     overflow-y: auto;
    //     padding: 0 25px;
    // }

    .close-btn {
      width: 24px;
      height: 24px;
      top: 10px;
      right: 10px;
    }
  }

  .merchantSettled {
    width: 100%;

    .merchantSettled-wap {
      background: #fff;
      display: flex;
      justify-content: center;
      align-items: center;
      width: 100% !important;
      position: relative;
      z-index: 99;

      .step-div {
        width: 100%;
        background: #fff;

        border-radius: 4px;
        margin-top: -86px;

        .content {
          padding: 20px 30px;
          border: 1px solid #eeeeee;

          .title p {
            font-family: "PingFang HK";
            font-style: normal;
            font-size: 14px;
            // line-height: 20px;
            color: #333333;
            padding: 6px 0;
          }
        }

        .bottom {
          height: 100px;
          font-size: 12px;
          display: flex;
          flex-direction: column;
          justify-content: space-around;
          align-items: center;
          margin: 20px 0;

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
      font-size: 12px;
      color: #999999;

      span {
        color: var(--color-main);
      }
    }
  }

  .uploder-center {
    display: flex;

    .uploder-two-wrap {
      margin-right: 30px;

      .tips {
        color: #333333;
        font-size: 12px;
        text-align: center;
        line-height: 1;
      }
    }
  }

  .correct-warp {
    display: flex;

    img {
      width: 100px;
      margin-right: 20px;
    }
  }

  .tab-wrap {
    display: flex;
    margin-top: 20px;
    margin-bottom: 20px;

    .tab-item {
      width: 148px;
      height: 34px;
      background: #eeeeee;
      border-radius: 4px;
      text-align: center;
      cursor: pointer;
      line-height: 34px;
      margin-right: 20px;
      color: #333333;
      font-size: 14px;
    }

    .active {
      color: #fff !important;
      background: var(--color-main) !important;
    }
  }

  .code-input {
    width: 420px;
  }

  .code-wrap {
    width: 133px;
    height: 34px;
    background: var(--color-main);
    border-radius: 4px;
    margin-top: 8px;
    text-align: center;
    line-height: 34px;
    font-size: 14px;
    color: #fff;
    cursor: pointer;
  }

  .el-dropdown {
    width: 100%;
  }

  .prepend-wrap {
    display: flex;
    align-items: center;
    padding: 0 20px;

    .phone_number {
      flex: 1;
    }
  }

  .phone_number_wrap {
    /deep/ .el-input__inner {
      width: 320px;
    }
  }
}

.option-wrap {
  display: flex;
  align-items: center;
  font-size: 14px;

  img {
    height: 30px;
    margin-right: 5px;
  }
}

.lang-item {
  display: flex;
  align-items: center;

  img {
    width: 20px;
    height: 20px;
    margin-right: 5px;
  }
}

:deep(.van-checkbox__label) {
  display: flex;
}

/deep/ .el-form-item__label {
  text-align: left !important;
  line-height: inherit;
}

/deep/ .el-select-dropdown__list {
  padding: 10px 0 !important;
}

/deep/ .el-select .el-input .el-select__caret {
  font-size: 15px;
  display: flex;
  align-items: center;
}

.el-select-dropdown__item.selected {
  color: var(--color-main) !important;
}

.el-select .el-input.is-focus .el-input__inner {
  padding-left: 30px !important;
}

/deep/ .el-input__inner {
  height: 50px !important;
  width: 320px;
  font-size: 14px;
  border: 1px solid #eeeeee;

  &::placeholder {
    font-size: 14px;
    color: #999999;
  }
}

/deep/ .van-uploader__upload-icon {
  font-size: 35px !important;
  color: #aaaaaa !important;
}

/deep/ .el-input-group__prepend {
  width: 100px !important;
  padding: 0 !important;
  background: none !important;
  font-size: 14px;
}

@media screen and (max-width: 768px) {
  .pop-bnt {
    width: 100%;
    margin: 20px auto 0 !important;
    display: flex;
    flex-wrap: wrap;
  }

  /deep/ .el-input__inner,
  .el-input {
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
      margin-top: 20px;
      margin-right: 10px !important;
    }
  }

  .van-popup {
    width: 90% !important;
  }
}

/deep/ .van-checkbox__icon--checked .van-icon {
  background-color: var(--color-main) !important;
  border-color: var(--color-main) !important;
}

/deep/ .el-input.is-disabled .el-input__inner {
  background-color: #fff;
}

::-webkit-scrollbar {
  display: none;
  /* Chrome Safari */
}

.password-icon {
  width: 16px;
  cursor: pointer;
}

.pop-bnt {
  // width: 28%;
  margin: 0 auto 10px;
  display: flex;
  justify-content: center;

  .van-button {
    margin: 0 !important;

    &:nth-child(1) {
      margin-right: 20px !important;
      margin-bottom: 10px !important;
    }
  }
}

.btn-list {
  display: flex;
  justify-content: space-between;
  flex-wrap: wrap;
  padding: 10px 0;
  border-top: 1px solid #eee;

  .btn-left {
    display: flex;
    justify-content: center;
  }

  .van-button {
    margin: 5px 10px !important;
  }
}

.esign-container {
  width: 800px;
}
</style>
