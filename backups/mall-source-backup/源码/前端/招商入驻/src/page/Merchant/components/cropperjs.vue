<template>
  <div>
    <div class="main-cropper">
      <!-- 剪裁框 -->
      <div class="cropper">
        <img class="img" ref="image" :src="imgFile" alt="">
      </div>
      <!-- 底部 -->
      <div class="cropper-footer">
        <div class="footer-handle">
          <div class="item" @click="handleCancel">取消</div>
          <div class="item" @click="handleZoom(0.05)">放大</div>
          <div class="item" @click="handleZoom(-0.05)">缩小</div>
          <!-- <div class="item" @click="handleRotate(-90)">逆时针旋转</div> -->
          <div class="item" @click="handleRotate(90)">旋转</div>
          <div class="item" @click="handleConfirm">确定</div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import Cropper from 'cropperjs'
import 'cropperjs/dist/cropper.css'

export default {
  name: 'VueCropper',
  props: {
    imgFile: {
      type: String,
      default: 'https://bpic.588ku.com/element_water_img/18/06/12/b2887846cb19ff36a5502401ac918809.jpg'
    },
    ratioWidth: {
      type: Number,
      default: 0
    },
    ratioHeight: {
      type: Number,
      default: 0
    },
  },
  data() {
    return {
      myCropper: null,
      afterImg: '',
      ScaleX: 1,
      ScaleY: 1,
      fixed: false,
      fixedBox: false,
      inputRotate: 0,
      isDisabled: false,
    }
  },
  computed: {},
  mounted() {
    this.init();
    // 判断是否是pc端
  },
  methods: {
    // 初始化
    init() {
      this.myCropper = new Cropper(this.$refs.image, {
        // responsive: true, // 在窗口大小变化后，重新渲染裁剪器 默认 true
        // restore: true, // 在窗口大小变化后，恢复被裁剪的区域 默认 true
        // checkCrossOrigin: true, // 检查图片是否跨域
        // modal: true, // 是否在图片和裁剪框之间显示黑色蒙版 默认 true
        // guides: true, // 是否显示裁剪框的虚线 默认 true
        // center: true, // 是否显示裁剪框中心的指示器 默认 true
        // highlight: true, // 是否显示裁剪框上面的白色蒙版(突出显示裁剪框） 默认 true
        background: false, // 是否在容器内显示网格背景 默认 true
        autoCrop: 1, // 定义裁剪区域占图片的大小(百分比) 取值为 0-1 默认 0.8
        // movable: true, // 是否可以移动图片 默认 true
        // rotatable :true, // 是否可以旋转图片 默认 true
        // scalable: true, // 是否可以缩放图片 默认 true
        // zoomable: true, // 是否可以缩放图片（以图片左上角为原点进行缩放）默认 true
        // zoomOnTouch: true, // 是否允许通过拖动来缩放图片 默认 true
        zoomOnWheel: true, // 是否允许通过鼠标滚轮缩放图片 默认 true
        // wheelZoomRatio: true, // 设置通过鼠标滚轮缩放图片时的缩放比例 默认 0.1
        cropBoxMovable: true, // 是否允许通过拖动来移动裁剪框 默认 true
        cropBoxResizable: true, // 是否允许通过拖动来调整裁剪框的大小 默认 true
        // toggleDragModeOnDblclick: true, // 是否允许双击切换图片容器拖拽模式(​​"crop"​​和​​"move"​​) 默认 true
        // minContainerWidth: 400, // 设置裁剪容器的最小宽度 默认 200
        // minContainerHeight: 400, // 设置裁剪容器的最小高度 默认 100
        // minCanvasWidth: 0, // 设置图片容器的最小宽度 默认 0
        minCropBoxWidth: 200, // 设置裁剪框的最小宽度 默认 0 这个尺寸是相对于页面的，而不是图片
        minCropBoxHeight: 200, // 设置裁剪框的最小高度 默认 0 这个尺寸是相对于页面的，而不是图片
        // preview: '.before', // 预览样式 如果需要预览 配置预览 class 即可
        viewMode: 1, // 裁剪器配置 [0:没有限制 1:限制裁剪框不超过图片容器的范围 2:限制最片容器尺寸以在裁剪容器中展示。 如果图片容器和裁剪容器的比例不同，则图片容器以cover模式填充（图片容器保持原有比例，最长边和裁剪容器大小一致，短边等比缩放，可能会有部分区域不可见) 3:限制图片容器尺寸以在裁剪器中展示。 如果图片容器和裁剪容器的比例不同，则图片容器以contain模式填充（图片容器保持原有比例，最短边和裁剪容器大小一直，长边等比缩放，可能会有留白）]
        dragMode: 'move', // 定义裁剪器的拖动模式 [crop:创建一个新的裁剪框 move:图片容器可移动 none:什么也不做] 默认 crop
        // initialAspectRatio: 1, // 定义裁剪框的初始宽高比。默认和图片容器的宽高比相同 默认 NaN 
        autoCropArea: 0.2, // 定义裁剪区域占图片的大小(百分比)。取值为 0 - 1
        aspectRatio: this.ratioWidth / this.ratioHeight // 定义裁剪框的固定宽高比。默认是自由比例 NaN
      })
    },
    // 取消
    handleCancel() {
      this.$emit('handleCancel')
    },
    // 缩放
    handleZoom(val) {
      this.myCropper.zoom(val)
    },
    // 旋转
    handleRotate(val) {
      this.myCropper.rotate(val)
    },
    // 绝对角度旋转
    handleRotateTo(val) {
      this.myCropper.rotateTo(val)
    },
    // 裁剪
    uploadImgs() {
      this.afterImg = this.myCropper.getCroppedCanvas({
        imageSmoothingQuality: 'high'
      }).toDataURL('image/jpeg');
      this.$emit('handleCropData', this.afterImg)
    },
    // 确定
    handleConfirm() {
      this.afterImg = this.myCropper.getCroppedCanvas({
        imageSmoothingQuality: 'high'
      }).toDataURL('image/jpeg');
      this.$emit('handleUpload', this.base64ToBlob(this.afterImg))
    },
    base64ToBlob(code) {
      const parts = code.split(';base64,');
      const contentType = parts[0].split(':')[1];
      const raw = window.atob(parts[1]);
      const rawLength = raw.length;
      const uInt8Array = new Uint8Array(rawLength);
      for (let i = 0; i < rawLength; ++i) {
        uInt8Array[i] = raw.charCodeAt(i);
      }
      return new Blob([uInt8Array], {
        type: contentType
      })
    },
    // 重置    
    handleReset() {
      this.myCropper.reset();
      this.ScaleX = 1;
      this.ScaleY = 1;
    },
    // 移动
    handleMove(val1, val2) {
      this.myCropper.move(val1, val2);
    },
    // X轴翻转
    handleCropperScaleX() {
      this.ScaleX = -this.ScaleX
      if (this.myCropper.getImageData().rotate === -90 || this.myCropper.getImageData().rotate === 90) {
        this.myCropper.scaleY(this.ScaleX)
      } else {
        this.myCropper.scaleX(this.ScaleX)
      }
    },
    // y轴翻转
    handleCropperScaleY() {
      this.ScaleY = -this.ScaleY
      if (this.myCropper.getImageData().rotate === -90 || this.myCropper.getImageData().rotate === 90) {
        this.myCropper.scaleX(this.ScaleY)
      } else {
        this.myCropper.scaleY(this.ScaleY)
      }
    }
  }
}
</script>
<style lang="scss">
* {
  margin: 0;
  padding: 0;
}

.main-cropper {
  position: fixed;
  top: 0;
  right: 0;
  bottom: 0;
  left: 0;
  z-index: 10000;
}

.main-cropper .cropper {
  position: absolute;
  top: 0;
  right: 0;
  bottom: 54px;
  left: 0;
  overflow: hidden;
  background-image: url(data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABAAAAAQAQMAAAAlPW0iAAAAA3NCSVQICAjb4U/gAAAABlBMVEXMzMz////TjRV2AAAACXBIWXMAAArrAAAK6wGCiw1aAAAAHHRFWHRTb2Z0d2FyZQBBZG9iZSBGaXJld29ya3MgQ1M26LyyjAAAABFJREFUCJlj+M/AgBVhF/0PAH6/D/HkDxOGAAAAAElFTkSuQmCC);
}

.main-cropper .cropper .img {
  width: 90%;
  opacity: 0;
}

/**/
.main-cropper .cropper-footer {
  width: 100%;
  position: fixed;
  left: 0;
  bottom: 0;
  background-color: #FFFFFF;
}

.main-cropper .cropper-footer .footer-handle {
  padding: 10px 10px;
  display: flex;
  flex-direction: row;
  justify-content: center;
}

.main-cropper .cropper-footer .item {
  width: 60px;
  height: 34px;
  line-height: 34px;
  text-align: center;
  background: #28a745;
  color: #fff;
  cursor: pointer;
  border-radius: 4px;
  font-size: 15px;
  margin-right: 12px;

  &:last-child {
    margin-right: 0;
  }
}

.main-cropper .cropper-footer .item:first-child {
  background: #909399;
}

.main-cropper .cropper-footer .item:last-child {
  background: #409EFF;
}
</style>