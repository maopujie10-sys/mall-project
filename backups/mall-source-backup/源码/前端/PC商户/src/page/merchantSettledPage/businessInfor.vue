<template>
  <div class="merchant-settled-content">
    <div class="merchant-settled-content-form">
      <h1>Business information</h1>
      <div>
        <el-form
          :model="infoModel"
          :rules="rules"
          ref="ruleForm"
          label-width="230px"
        >
          <el-form-item label="Shop logo" prop="logo">
            <el-upload
              class="avatar-uploader"
              action="https://jsonplaceholder.typicode.com/posts/"
              :show-file-list="false"
              :on-success="handleAvatarSuccess"
              :before-upload="beforeAvatarUpload"
            >
              <img v-if="infoModel.logo" :src="infoModel.logo" class="avatar" />
              <img
                v-else
                class="avatar-uploader-icon"
                :src="require('@/assets/image/camera.png')"
                alt=""
              />
            </el-upload>
          </el-form-item>
          <el-form-item label="Shop name" prop="name">
            <el-input
              v-model="infoModel.name"
              placeholder="Please enter store name"
            />
          </el-form-item>
          <el-form-item label="Shop Adress" prop="address">
            <el-input
              v-model="infoModel.address"
              placeholder="Please enter the store address"
            />
          </el-form-item>
          <el-form-item label="Invitation Code" prop="code">
            <el-input
              v-model="infoModel.code"
              placeholder="Please enter the invitation code"
            />
          </el-form-item>
          <el-form-item label="Actual name" prop="actualName">
            <el-input
              v-model="infoModel.actualName"
              placeholder="Please input your Actual name"
            />
          </el-form-item>
          <el-form-item label="Country" prop="country">
            <el-menu class="el-menu-demo" mode="horizontal">
              <el-submenu index="2">
                <template slot="title">
                  <div class="flex-start country-select">
                    <img :src="langIcon[infoModel.country]" alt="" />
                    <span>{{ currentCountryName }}</span>
                  </div>
                </template>

                <el-menu-item v-for="item in countryList" :key="item.key">
                  <div class="country-item" @click="selectCountry(item.key)">
                    <img :src="item.icon" :alt="item.key" />
                    <span>{{ item.name }}</span>
                  </div>
                </el-menu-item>
              </el-submenu>
            </el-menu>
            <!-- <el-dropdown trigger="click">
              <div class="lang-select flex-between">
                <div class="flex-start">
                  <img :src="langIcon[infoModel.country]" alt="" />
                  <span>{{ currentCountryName }}</span>
                </div>

                <i class="el-icon-caret-bottom"></i>
              </div>
              <el-dropdown-menu slot="dropdown">
                <el-dropdown-item v-for="item in countryList" :key="item.key">
                  <div class="country-item" @click="selectCountry(item.key)">
                    <img :src="item.icon" :alt="item.key" />
                    <span>{{ item.name }}</span>
                  </div>
                </el-dropdown-item>
              </el-dropdown-menu>
            </el-dropdown> -->
          </el-form-item>
          <el-form-item label="ID number" prop="id">
            <el-input
              v-model="infoModel.id"
              placeholder="Please input your ID number"
            />
          </el-form-item>
          <el-form-item label="ID photo/passport upload">
            <el-row>
              <el-col :span="4">
                <el-upload
                  class="avatar-uploader"
                  action="https://jsonplaceholder.typicode.com/posts/"
                  :show-file-list="false"
                  :on-success="handleAvatarSuccess"
                  :before-upload="beforeAvatarUpload"
                >
                  <div class="avatar-uploader-item">
                    <img
                      v-if="infoModel.photoFront"
                      :src="infoModel.photoFront"
                      class="avatar"
                    />
                    <img
                      v-else
                      class="avatar-uploader-icon"
                      :src="require('@/assets/image/camera.png')"
                      alt=""
                    />
                    <div class="avatar-uploader-tips">ID photo front</div>
                  </div>
                </el-upload>
              </el-col>
              <el-col :span="4">
                <el-upload
                  class="avatar-uploader"
                  action="https://jsonplaceholder.typicode.com/posts/"
                  :show-file-list="false"
                  :on-success="handleAvatarSuccess"
                  :before-upload="beforeAvatarUpload"
                >
                  <div class="avatar-uploader-item">
                    <img
                      v-if="infoModel.photoBack"
                      :src="infoModel.photoBack"
                      class="avatar"
                    />
                    <img
                      v-else
                      class="avatar-uploader-icon"
                      :src="require('@/assets/image/camera.png')"
                      alt=""
                    />
                    <div class="avatar-uploader-tips">ID photo back</div>
                  </div>
                </el-upload>
              </el-col>
              <el-col :span="4">
                <el-upload
                  class="avatar-uploader"
                  action="https://jsonplaceholder.typicode.com/posts/"
                  :show-file-list="false"
                  :on-success="handleAvatarSuccess"
                  :before-upload="beforeAvatarUpload"
                >
                  <div class="avatar-uploader-item">
                    <img
                      v-if="infoModel.holdingPhont"
                      :src="infoModel.holdingPhont"
                      class="avatar"
                    />
                    <img
                      v-else
                      class="avatar-uploader-icon"
                      :src="require('@/assets/image/camera.png')"
                      alt=""
                    />
                    <div class="avatar-uploader-tips">Holding ID photo</div>
                  </div>
                </el-upload>
              </el-col>
            </el-row>
          </el-form-item>
          <el-form-item label="Shooting examples">
            <el-row>
              <el-col :span="4">
                <div class="flex-start upload-img-wrap">
                  <img
                    class="upload-img"
                    :src="require('@/assets/image/01.png')"
                    alt=""
                  />
                  <img :src="require('@/assets/image/gou.png')" alt="" />
                </div>
              </el-col>
              <el-col :span="4">
                <div class="flex-start upload-img-wrap">
                  <img
                    class="upload-img"
                    :src="require('@/assets/image/02.png')"
                    alt=""
                  />
                  <img :src="require('@/assets/image/cha.png')" alt="" />
                </div>
              </el-col>
              <el-col :span="4">
                <div class="flex-start upload-img-wrap">
                  <img
                    class="upload-img"
                    :src="require('@/assets/image/03.png')"
                    alt=""
                  />
                  <img :src="require('@/assets/image/cha.png')" alt="" />
                </div>
              </el-col>
            </el-row>
          </el-form-item>
        </el-form>
      </div>
    </div>
    <div class="merchant-settled-content-agreement">
      <div class="agreement-btn">
        <el-button type="primary" @click="submit">Submit application</el-button>
      </div>
    </div>
    <el-dialog
      class="merchant-settled-content-dialog"
      :visible.sync="dialogVisible"
      :center="true"
    >
      <div slot="title" class="dialog-title">
        <span>Submitted successfully</span>
      </div>
      <div class="dialog-content">
        <img :src="require('@/assets/image/wanc.png')" alt="Success" />
        <p>
          The store check-in application has been submitted, if you need to
          modify it, please contact customer service
        </p>
        <el-button type="primary">Contact Customer Service</el-button>
      </div>
      <span slot="footer"></span>
    </el-dialog>
  </div>
</template>

<script>
import zhIcon from '@/assets/image/cn.png'
import enIcon from '@/assets/image/en.png'
import twIcon from '@/assets/image/tw.png'

export default {
  name: 'EsBusinessInfo',
  data() {
    return {
      checked: false,
      dialogVisible: false,
      infoModel: {
        logo: '',
        name: '',
        address: '',
        code: '',
        actualName: '',
        id: '',
        country: 'en',
        photoFront: '',
        photoBack: '',
        holdingPhont: '',
      },
      rules: {
        logo: [
          {
            required: true,
            message: 'Please upload your logo',
            trigger: 'blur',
          },
        ],
        name: [
          {
            required: true,
            message: 'Please enter store name',
            trigger: 'blur',
          },
        ],
        address: [
          {
            required: true,
            message: 'Please enter the store address',
            trigger: 'blur',
          },
        ],
        code: [
          {
            required: true,
            message: 'Please enter the invitation code',
            trigger: 'blur',
          },
        ],
        actualName: [
          {
            required: true,
            message: 'Please input your Actual name',
            trigger: 'blur',
          },
        ],
        country: [
          {
            required: true,
            message: 'Please enter store name',
            trigger: 'blur',
          },
        ],
        id: [
          {
            required: true,
            message: 'Please input your ID number',
            trigger: 'blur',
          },
        ],
        country: [
          {
            required: true,
            message: 'Please select a country',
            trigger: 'blur',
          },
        ],
      },
      langIcon: {
        'zh-CN': zhIcon,
        en: enIcon,
        'zh-TW': twIcon,
      },
      countryList: [
        {
          key: 'zh-CN',
          icon: zhIcon,
          name: '中文简体',
        },
        {
          key: 'zh-TW',
          icon: twIcon,
          name: '中文繁體',
        },
        {
          key: 'en',
          icon: enIcon,
          name: 'English',
        },
      ],
    }
  },
  computed: {
    currentCountryName() {
      return this.countryList.find(
        (item) => item.key === this.infoModel.country,
      ).name
    },
  },
  methods: {
    handleAvatarSuccess() {},
    beforeAvatarUpload() {},
    selectCountry(key) {
      console.log(key)
      this.infoModel.country = key
    },
    submit() {
      this.dialogVisible = true
      this.$refs.ruleForm.validate((valid) => {
        if (valid) {
        }
      })
    },
  },
}
</script>

<style lang="scss">
.merchant-settled-content {
  position: relative;
  background-color: var(--color-white);
  padding: 0 20px;
  &-form {
    border-radius: 4px;
    border: 1px solid var(--color-border);
    position: relative;
    top: -90px;
    background-color: var(--color-white);
    padding: 24px;
    h1 {
      font-weight: 700;
      font-size: 24px;
      margin-bottom: 40px;
      color: var(--color-title);
    }
    .avatar-uploader {
      &-tips {
        font-weight: 400;
        font-size: 12px;
        color: var(--color-title);
        margin-top: -15px;
      }
    }
    .avatar-uploader-icon {
      width: 91px;
      height: 94px;
    }
    .upload-img-wrap {
      flex-direction: column;
    }
    .upload-img {
      width: 100%;
      height: 100%;
      max-width: 100px;
      max-height: 65px;
      margin-bottom: 10px;
    }
    .el-form-item__label {
      text-align: left;
    }

    .el-submenu {
      width: 100%;
      border: 1px solid #dcdfe6;
      border-radius: 4px;
    }
    .el-submenu__title {
      display: flex;
      justify-content: space-between;
      align-items: center;
      height: 40px !important;
      line-height: 40px !important;
    }

    .el-menu.el-menu--horizontal {
      border: 0;
    }
    .country-select {
      width: 100%;
      cursor: pointer;
      img {
        margin-right: 8px;
      }
    }
  }

  &-agreement {
    font-weight: 500;
    font-size: 12px;
    width: 100%;
    text-align: center;
    margin: -60px 0 100px 0;
    .agreement-btn {
      margin-top: 50px;
      .el-button {
        width: 100%;
        max-width: 475px;
        height: 52px;
        font-weight: 400;
        font-size: 16px;
      }
    }
  }

  &-dialog {
    .el-dialog__header {
      padding: 0;
      border-radius: 6px;
    }
    .el-dialog__close {
      font-size: 24px;
    }
    .el-dialog__headerbtn {
      top: 14px;
      right: 14px;
    }
    .el-dialog {
      width: 80vw;
      max-width: 600px;
    }
    .dialog-title {
      height: 50px;
      line-height: 50px;
      background-color: #f5f5f5;
      font-weight: 700;
      font-size: 18px;
      color: var(--color-title);
      border-radius: 6px;
    }
    .dialog-content {
      display: flex;
      justify-content: center;
      align-items: center;
      flex-direction: column;

      img {
        margin: 80px 0 50px 0;
      }

      p {
        padding: 0 40px;
        margin-bottom: 50px;
        text-align: center;
        font-weight: 500;
        font-size: 16px;
        color: var(--color-title);
      }

      .el-button {
        width: 100%;
        max-width: 450px;
        height: 50px;
      }
    }
  }
}

.country-item {
  padding: 0 10px;
  img {
    margin-right: 5px;
  }
}
</style>
