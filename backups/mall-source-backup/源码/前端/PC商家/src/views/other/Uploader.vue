<template>
  <div class="rounded-md bg-white" style="border: 1px solid #ccc;overflow: hidden">
    <van-uploader v-model="fileList" :max-count="1">
      <div class="flex flex-col w-full h-full items-center justify-center">
        <img :src="require('@/assets/images/bxs_camera-plus.png')" alt="" class="w-36 h-36 upload-img"/>
        <p class="mt-8 font-12 font-400" style="color: #999">{{ title }}</p>
      </div>
    </van-uploader>
  </div>
</template>

<script>
import {Uploader} from 'vant';

export default {
  name: "Uploader",
  props: {
    title: {
      default: ''
    }
  },
  data() {
    return {
      fileList: []
    }
  },
  components: {
    [Uploader.name]: Uploader,
  },
  watch: {
    fileList() {
      this.$emit('uploader', this.fileList)
    }
  }
}
</script>

<style lang="scss" scoped>
::v-deep {
  .van-uploader, .van-uploader__wrapper, .van-uploader__upload, .van-uploader__input-wrapper, .van-uploader__preview, .van-uploader__preview-image {
    width: 100%;
    height: 100%;
  }

  .van-uploader__preview-delete {
    width: 21px;
    height: 21px;

    .van-icon {
      font-size: 23px;
    }
  }

  .van-uploader__preview {
    margin: 0;
  }

  .van-uploader__upload {
    margin: 0;
    background: #fff;
  }
}

</style>
