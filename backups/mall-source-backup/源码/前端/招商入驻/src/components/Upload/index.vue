<template>
  <div class="upload" :style="{width:this.option.autoCropWidth+'px',height:this.option.autoCropHeight+'px'}">
    <el-upload
        class="upload-content"
        :action="uploadUrl"
        :show-file-list="false"
        :before-upload="beforeAvatarUpload"
        :data="{ deadline: 0, file_size: 512 * 1024 }"
        ref="upload"
        accept="image/*"
        :limit="1"
    >
      <el-image v-if="imageUrl" :src="imageUrl" class="upload-content-image" lazy>
        <div slot="error" class="image-slot">
          <i class="van-icon-photograph"></i>
        </div>
      </el-image>
      <div class="upload-content-icon" v-else>
        <van-icon name="photograph" style="color: #B8BCC5"/>
        <!--        <div class="upload-content-text">{{ addText }}</div>-->
      </div>
      <!--      <i v-else class="el-icon-camera-solid upload-content-icon"></i>-->
    </el-upload>

    <el-dialog
        :title="$t('图片裁剪')"
        ref="dialog"
        :width="this.option.autoCropWidth>400?(this.option.autoCropWidth+120)+'px':'520px'"
        :visible.sync="dialogVisible"
        :close-on-click-modal="false"
    >
      <div class="cropper-w">
        <div class="cropper" :style="{ width: '100%', height: '280px' }">
          <vueCropper
              ref="cropper" :img="option.img" :output-size="option.size" :output-type="option.outputType" :info="true"
              :full="option.full" :fixed="option.fixed" :fixed-number="fixedNumber"
              :can-move="option.canMove" :can-move-box="option.canMoveBox" :fixed-box="option.fixedBox"
              :original="option.original"
              :auto-crop="option.autoCrop" :auto-crop-width="option.autoCropWidth"
              :auto-crop-height="option.autoCropHeight" :center-box="option.centerBox"
              :high="option.high"
              mode="cover"
          ></vueCropper>
        </div>
      </div>
      <div slot="footer" class="dialog-footer">
        <el-button @click="dialogVisible = false">{{ $t('取消') }}</el-button>
        <el-button type="primary" @click="handleConfirm">{{ $t('确认') }}</el-button>
      </div>
    </el-dialog>
  </div>
</template>

<script>
import {VueCropper} from 'vue-cropper'
import {Notification} from 'element-ui'
import {i18n} from "@/i18n";
import {uploadimg} from "@/API/commodity";
import {Toast} from "vant";

export default {
  name: 'SoUpload',
  components: {
    VueCropper,
  },
  data() {
    return {
      dialogVisible: false,
      imageUrl: "",
      iconImg: require("@/assets/image/bxs_camera-plus.png"),
      option: {
        img: "", // 裁剪图片的地址
        info: false, // 裁剪框的大小信息
        outputSize: 1, // 裁剪生成图片的质量
        outputType: "jpeg", // 裁剪生成图片的格式
        canScale: false, // 图片是否允许滚轮缩放
        autoCrop: true, // 是否默认生成截图框
        autoCropWidth: 345, // 默认生成截图框宽度
        autoCropHeight: 160, // 默认生成截图框高度
        fixedBox: false, // 固定截图框大小 不允许改变
        fixed: true, // 是否开启截图框宽高固定比例
        fixedNumber: [345, 160], // 截图框的宽高比例
        full: false, // 是否输出原图比例的截图
        canMoveBox: true, // 截图框能否拖动
        original: false, // 上传图片按照原始比例渲染
        centerBox: true, // 截图框是否被限制在图片里面
        infoTrue: false, // true 为展示真实输出图片宽高 false 展示看到的截图框宽高
      },
    };
  },
  props: {
    value: {
      type: [String, Array, Object],
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
    fixedNumber: {
      type: Array,
      default: () => [345, 160],
    },
  },
  watch: {
    value: {
      handler: function (val) {
        //如果是数组
        if (Array.isArray(val)) {
          if (val.length > 0) {
            this.imageUrl = val[0].url;
          } else {
            this.imageUrl = '';
          }
        } else {
          this.imageUrl = val;
        }
      },
      immediate: true,
    },
  },
  mounted() {
    this.option.autoCropHeight = this.height;
    this.option.autoCropWidth = this.width;
  },
  methods: {
    beforeAvatarUpload(file) {
      this.filename = file.name;
      this.openCropper(file);
      return false;
    },
    openCropper(file) {
      const _this = this;
      console.log(_this);
      const isJPG =
          file.type === "image/jpeg" ||
          file.type === "image/jpg" ||
          file.type === "image/png" ||
          file.type === "image/PNG" ||
          file.type === "image/JPG";
      if (!isJPG) {
        Notification.warning(this.$t("上传图片只能为jpg或png格式"))
        return;
      }
      let reader = new FileReader();
      reader.onload = (e) => {
        let data;
        if (typeof e.target.result === "object") {
          // 把Array Buffer转化为blob 如果是base64不需要
          data = window.URL.createObjectURL(new Blob([e.target.result]));
        } else {
          data = e.target.result;
        }
        _this.option.img = data;
        _this.dialogVisible = true;
      };
      // 转化为base64
      reader.readAsDataURL(file);
      // 转化为blob
      // reader.readAsArrayBuffer(file);
    },
    handleConfirm() {
      console.log(this.$refs.cropper);
      this.$refs.cropper.getCropBlob((data) => {
        // if (data.size > 2097152) {
        //   this.showMsg("图片大于2M，请进行裁剪或重新选择");
        // }
        let blob = window.URL.createObjectURL(data);
        this.downImg = blob;
        // eslint-disable-next-line no-unused-vars
        let base64;
        let img = new Image();
        img.src = blob;
        let _that = this;
        img.onload = function () {
          let that = this;
          //生成比例
          let w = that.width,
              h = that.height,
              scale = w / h;
          h = w / scale;
          //生成canvas
          let canvas = document.createElement("canvas");
          let ctx = canvas.getContext("2d");
          canvas.width = w;
          canvas.height = h;
          ctx.drawImage(that, 0, 0, w, h);
          // 生成base64
          _that.cropperPic = canvas.toDataURL("image/jpeg", 0.8);
          let files = _that.transformToFiles(_that.cropperPic, _that.filename);
          _that.temporaryCloseCropper = true;
          _that.dialogVisible = false
          Toast.loading({
            duration: 0,
            message: _that.$t('上传中'),
            forbidClick: true,
          })
          let formData = new FormData();
          formData.append("file", files, _that.filename);
          formData.append("deadline", 0); // 按照接口需求情况添加
          formData.append("file_size", 512 * 1024); // 按照接口需求情况添加
          formData.append('moduleName', this.moduleName)
          uploadimg(formData).then(res => {
            _that.imageUrl = res;
            console.log(_that.imageUrl);
            _that.$emit('input', res)
            _that.$emit('success', res)
            Toast.clear()
          }).catch(() => {
            Notification.error(this.$t('添加失败'));
          })
        };
      });
    },

    // base64转成files
    transformToFiles(dataurl, filename) {
      let arr = dataurl.split(","),
          mime = arr[0].match(/:(.*?);/)[1],
          bstr = atob(arr[1]),
          n = bstr.length,
          u8arr = new Uint8Array(n);
      while (n--) {
        u8arr[n] = bstr.charCodeAt(n);
      }
      return new File([u8arr], filename, {type: mime});
    },
  },
};
</script>

<style lang='scss' scoped>
/deep/ .el-upload {
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
    border: 1px dashed #B8BCC5;
    box-sizing: border-box;

    .upload-content-image {
      width: 100%;
      height: 100%;
      object-fit: cover;
      position: absolute;
      top: 0;
      left: 0;

      ::v-deep {
        .van-icon {
          color: red;
        }
      }
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
        //margin-bottom: 12px;
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
