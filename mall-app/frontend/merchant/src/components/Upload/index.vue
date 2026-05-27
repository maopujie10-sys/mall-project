<template>
  <div class="upload" :style="{width:this.width+'px',height:this.height+'px'}" v-loading="loading">
    <el-upload
        v-if="showUpload"
        class="upload-content"
        :action="uploadUrl"
        :show-file-list="false"
        :before-upload="beforeAvatarUpload"
        :data="{ deadline: 0, file_size: 512 * 1024 }"
        ref="upload"
        accept="image/png,image/jpg,image/jpeg"
        :limit="1"
    >
      <el-image v-if="imageUrl" :src="imageUrl" class="upload-content-image" lazy>
        <div slot="error" class="image-slot">
          <i class="el-icon-picture-outline"></i>
        </div>
      </el-image>
      <div class="upload-content-icon" v-else>
        <el-image :src="iconImg" class="upload-icon">
          <div slot="error" class="image-slot">
            <i class="el-icon-picture-outline"></i>
          </div>
        </el-image>
        <div class="upload-content-text">{{ addText }}</div>
      </div>
    </el-upload>
  </div>
</template>

<script>
import {imageUpload} from "@/api/user";
import {i18n} from "@/lang";
import Toast from "@/utils/toast";
import {Notification} from "element-ui";

export default {
  name: 'SoUpload',
  data() {
    return {
      dialogVisible: false,
      imageUrl: "",
      loading: false,
      iconImg: require("@/assets/images/bxs_camera-plus.png"),
      showUpload: true,
    };
  },
  props: {
    value: {
      type: [String, Object],
      default: '',
    },
    uploadUrl: {
      type: String,
      default: '',
    },
    width: {
      type: Number,
      default: 345,
    },
    height: {
      type: Number,
      default: 95,
    },
    moduleName: {
      type: String,
      default: '',
    },
    addText: {
      type: String,
      default: i18n.t('添加图片'),
    },
  },
  watch: {
    value: {
      handler: function (val) {
        this.imageUrl = val;
      },
      immediate: true,
    },
  },
  mounted() {
    this.loading = false;
  },
  methods: {
    // 文件上传之前做处理
    beforeAvatarUpload(file) {
      const that = this
      const isJPG = (file.type === 'image/jpeg' || file.type === 'image/png' || file.type === 'image/jpg');
      const isLt2M = file.size / 1024 / 1024 < 4;
      // 图片格式
      if (!isJPG) {
        Notification.error({
          title: i18n.t('上传图片只能是 JPG/JPEG/PNG 格式!'),
          message: i18n.t('当前上传图片格式为：') + file.type,
        });
        this.$refs.upload.clearFiles();
        return false;
      }
      // 图片大小
      if (!isLt2M) {
        Notification.error({
          title: i18n.t('上传图片大小不能超过 4MB!'),
          message: i18n.t('当前上传图片大小为：') + (file.size / 1024 / 1024).toFloor(2) + 'MB',
        });
        this.$refs.upload.clearFiles();
        return false;
      }
      // 图片尺寸
      let imgWidth = "";
      let imgHeight = "";
      const isSize = new Promise(function (resolve, reject) {
        const _URL = window.URL || window.webkitURL;
        const img = new Image();
        img.onload = () => {
          imgWidth = img.width;
          imgHeight = img.height;
          const ifStatus = (img.width === 1920 && img.height === 300);
          if (ifStatus) {
            resolve();
          } else {
            reject();
          }
        }
        img.src = _URL.createObjectURL(file);
      }).then(() => {
        this.uploadImg(file);    // 调用后台接口上传图片的方法
      }).catch(() => {
        Notification.warning({
          title: that.$t('图片尺寸不符合要求'),
          message: that.$t('上传文件的图片大小不合符标准,标准尺寸为1920×300。当前上传图片的尺寸为：') + imgWidth + '×' + imgHeight
        })
        this.initUpload();
        return false;
      })
    },
    uploadImg(file) {
      const that = this
      that.loading = true;
      that.filename = file.name;
      const formData = new FormData();// 通过formdata上传
      formData.append('file', file);
      formData.append("deadline", 0); // 按照接口需求情况添加
      formData.append("file_size", 1920 * 300); // 按照接口需求情况添加
      formData.append('moduleName', that.moduleName)
      imageUpload(formData).then(res => {
        Toast.clear();
        that.loading = false;
        that.$emit('input', res.data)
        that.$emit('success', res.data)
      }).catch(function (err) {
        console.log(err)
        that.loading = false;
        Toast.clear();
        Toast(that.$t('添加失败'));
        that.logoImg = [];
      })
    },
    initUpload() {
      this.showUpload = false
      setTimeout(() => {
        this.showUpload = true
      }, 100)
    },
  },
};
</script>

<style lang='scss' scoped>
.picture-crop {
  width: 100%;
  height: 100%;
  position: fixed;
  top: 0;
  left: 0;
  z-index: 10002;
  background-color: rgba(0, 0, 0, 0.5);

  .cropper-w {
    width: 100%;
    height: calc(100% - 60px);

    .cropper {
      width: 100%;
      height: 100%;
    }

    .close {
      background-color: rgba(0, 0, 0, 0.5);
      position: fixed;
      right: 0;
      top: 0;
      z-index: 10003;
      width: 40px;
      height: 40px;
      display: flex;
      justify-content: center;
      align-items: center;
      cursor: pointer;

      &::after {
        display: block;
        content: '';
        width: 20px;
        height: 2px;
        transform: rotate(45deg);
        background-color: #FFFFFF;
        position: relative;
      }

      &::before {
        display: block;
        content: '';
        width: 2px;
        height: 20px;
        transform: rotate(45deg);
        background-color: #FFFFFF;
        left: 10px;
        position: relative;
      }
    }
  }

  .picture-crop-footer {
    background-color: #FFFFFF;
    display: flex;
    justify-content: center;
    align-items: center;
    width: 100%;
    height: 60px;
  }
}

::v-deep .el-upload {
  width: 100%;
  height: 100%;
}

.upload {
  display: inline-block;

  .upload-content {
    width: 100%;
    height: 100%;
    display: flex;
    justify-content: center;
    align-items: center;
    background-color: #FFFFFF;
    position: relative;
    border: 1px solid #DDDDDD;
    border-radius: 4px;

    .upload-content-image {
      width: 100%;
      height: 100%;
      object-fit: cover;
      position: absolute;
      top: 0;
      left: 0;
    }

    .upload-content-icon {
      width: 100%;
      height: 100%;
      display: block;
      font-size: 36px;
      color: #999;
      line-height: 36px;
      display: flex;
      justify-content: center;
      align-items: center;
      flex-direction: column;

      .upload-icon {
        width: 36px;
        height: 36px;
        margin-bottom: 12px;
      }
    }

    .upload-content-text {
      font-family: 'Roboto';
      font-style: normal;
      font-weight: 400;
      font-size: 12px;
      line-height: 14px;
      text-align: center;
      letter-spacing: -0.3px;
      color: #AAAAAA;
    }
  }
}
</style>
